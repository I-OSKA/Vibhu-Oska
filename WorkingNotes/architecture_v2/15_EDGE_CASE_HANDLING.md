# Vibhu-Oska AI-OS — Edge Case Handling & Recovery

**Version**: 2.0  
**Status**: Phase 0 — Documentation Complete  
**Authority**: ParaCore (Supreme) → All Cores  
**Scope**: Failure detection, recovery patterns, safety guardrails

---

## Overview

This document defines every edge case, failure mode, and recovery strategy in the Vibhu-Oska system. Each pattern includes detection logic, recovery action, and integration points with the EventBus and ParaCore override system.

---

## 1. NaN/Inf Loss Detection and Recovery

**Affects**: SARA, Specialists, EvolutionCore GRPOTrainer, ParaCore OmniscienceTrainer

### Detection

```python
import torch
import math
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class LossHealthCheck:
    is_nan: bool
    is_inf: bool
    loss_value: float
    detected_at_step: int
    recovery_action: str

class NaNGuard:
    """
    Insert after every loss computation in the training pipeline.
    Provides immediate detection and recovery routing.
    """

    def __init__(self, model_name: str, emergency_checkpoint_dir: str):
        self.model_name = model_name
        self.emergency_dir = emergency_checkpoint_dir
        self.consecutive_nan_count = 0
        self.max_consecutive_nan = 3      # Abort after 3 NaN in a row
        self.nan_history = []

    def check(self, loss: torch.Tensor, step: int, epoch: int,
              model_state: dict, optimizer_state: dict) -> LossHealthCheck:
        """Check loss for NaN/Inf and trigger recovery if needed."""

        loss_val = loss.item() if loss.dim() == 0 else loss.mean().item()
        is_nan = math.isnan(loss_val)
        is_inf = math.isinf(loss_val)

        if not is_nan and not is_inf:
            self.consecutive_nan_count = 0
            return LossHealthCheck(
                is_nan=False, is_inf=False, loss_value=loss_val,
                detected_at_step=step, recovery_action="none"
            )

        # --- NaN/Inf detected ---
        self.consecutive_nan_count += 1
        self.nan_history.append({
            "step": step, "epoch": epoch, "loss": loss_val,
            "is_nan": is_nan, "is_inf": is_inf,
        })

        # Save emergency checkpoint
        self._save_emergency_checkpoint(
            model_state, optimizer_state, epoch, step, loss_val, is_nan
        )

        # Determine recovery action
        if self.consecutive_nan_count >= self.max_consecutive_nan:
            action = "ABORT_TRAINING"
        elif self.consecutive_nan_count >= 2:
            action = "ROLLBACK_AND_REDUCE_LR"
        else:
            action = "SKIP_STEP_AND_CONTINUE"

        return LossHealthCheck(
            is_nan=is_nan, is_inf=is_inf, loss_value=loss_val,
            detected_at_step=step, recovery_action=action
        )

    def _save_emergency_checkpoint(self, model_state, optimizer_state,
                                    epoch, step, loss_val, is_nan):
        """Save emergency checkpoint for post-mortem analysis."""
        import os, time
        path = os.path.join(
            self.emergency_dir,
            f"{self.model_name}_emergency_step{step}_{'nan' if is_nan else 'inf'}.pt"
        )
        torch.save({
            "model_state_dict": model_state,
            "optimizer_state_dict": optimizer_state,
            "epoch": epoch,
            "step": step,
            "loss": loss_val,
            "nan_detected": is_nan,
            "inf_detected": not is_nan,
            "timestamp": time.time(),
        }, path)
```

### Recovery Actions

| Consecutive NaN/Inf | Action | Description |
|---------------------|--------|-------------|
| 1 | `SKIP_STEP_AND_CONTINUE` | Zero gradients, skip optimizer step, log warning |
| 2 | `ROLLBACK_AND_REDUCE_LR` | Restore last good checkpoint, halve learning rate |
| 3+ | `ABORT_TRAINING` | Stop training, save emergency checkpoint, alert via EventBus |

### Training Loop Integration

```python
# In train.py — after loss.backward()
nan_guard = NaNGuard(model_name="sara", emergency_checkpoint_dir="checkpoints/")
check = nan_guard.check(loss, step, epoch, model.state_dict(), optimizer.state_dict())

if check.recovery_action == "SKIP_STEP_AND_CONTINUE":
    optimizer.zero_grad()
    logger.warning(f"[NaNGuard] NaN at step {step}, skipping. Will retry.")
    continue

elif check.recovery_action == "ROLLBACK_AND_REDUCE_LR":
    # Restore last good checkpoint
    checkpoint = torch.load(last_good_checkpoint_path)
    model.load_state_dict(checkpoint["model_state_dict"])
    optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    # Halve learning rate
    for param_group in optimizer.param_groups:
        param_group["lr"] *= 0.5
    logger.error(f"[NaNGuard] NaN at step {step}, rolled back. LR halved.")
    # Publish event
    event_bus.publish("training.nan_detected", {
        "model": "sara", "step": step, "action": "rollback",
        "new_lr": optimizer.param_groups[0]["lr"],
    })

elif check.recovery_action == "ABORT_TRAINING":
    logger.critical(f"[NaNGuard] 3+ consecutive NaN. ABORTING training.")
    event_bus.publish("training.abort", {
        "model": "sara", "reason": "consecutive_nan",
        "emergency_checkpoint": check.detected_at_step,
    })
    break
```

### Pre-Training Prevention

| Prevention Measure | Implementation |
|--------------------|----------------|
| FP32 master weights | `model.float()` before optimizer step |
| AMP GradScaler | `torch.cuda.amp.GradScaler` with initial scale 2^16 |
| Gradient clipping | `clip_grad_norm_(model.parameters(), 0.5)` |
| Lower learning rate | Start at 1e-4 (not 3e-4) |
| Warmup epochs | 5 epochs of linear warmup |
| Curriculum learning | 128 → 256 → 512 sequence length |
| Weight initialization | Xavier/Kaiming uniform, not normal |

---

## 2. OOM (VRAM) Prevention and Recovery

**Affects**: All model loading, training, inference, weight swapping

### VRAM Budget Enforcement

```python
from dataclasses import dataclass, field
from typing import Dict, Optional, List
import torch
import time

@dataclass
class VRAMAllocation:
    core_name: str
    mb_allocated: int
    mb_reserved: int
    load_state: str                    # "hot" | "warm" | "cold" | "offloaded"
    last_accessed: float = 0.0
    priority: int = 5                  # 1=highest, 10=lowest

class VRAMManager:
    """
    Enforces VRAM budget, manages weight swapping, prevents OOM.
    RTX 4060 8GB total budget.
    """

    TOTAL_MB = 8000
    RESERVE_MB = 1200                   # Gradients, activations, CUDA overhead
    USABLE_MB = TOTAL_MB - RESERVE_MB  # 6800 MB

    # Priority order (lower = higher priority)
    PRIORITY_ORDER = {
        "paracore": 1,
        "hybrid_core": 2,
        "cognition_core": 3,            # SARA — always hot
        "router": 4,                    # Intent classifier — always hot
        "fast_responder": 5,            # Always hot
        "active_specialist_1": 6,       # Hot-swapped
        "active_specialist_2": 7,       # Hot-swapped
        "backup_pool": 8,               # Warm
        "evolution_core": 9,            # Opportunistic (training only)
    }

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.allocations: Dict[str, VRAMAllocation] = {}
        self.lock_acquired = False      # Mutex for weight swap operations

    def can_load(self, core_name: str, required_mb: int) -> bool:
        """Check if loading a core would exceed VRAM budget."""
        current_used = sum(a.mb_allocated for a in self.allocations.values())
        available = self.USABLE_MB - current_used
        return available >= required_mb

    def request_allocation(self, core_name: str, required_mb: int,
                           priority: int) -> bool:
        """
        Request VRAM allocation. May evict lower-priority cores.
        Returns True if allocation succeeded.
        """
        if self.can_load(core_name, required_mb):
            self.allocations[core_name] = VRAMAllocation(
                core_name=core_name,
                mb_allocated=required_mb,
                mb_reserved=required_mb,
                load_state="hot",
                last_accessed=time.time(),
                priority=priority,
            )
            return True

        # Need to evict lower-priority cores
        evicted = self._evict_lower_priority(priority, required_mb)
        if evicted:
            self.allocations[core_name] = VRAMAllocation(
                core_name=core_name,
                mb_allocated=required_mb,
                mb_reserved=required_mb,
                load_state="hot",
                last_accessed=time.time(),
                priority=priority,
            )
            return True

        return False  # Cannot allocate — OOM would occur

    def _evict_lower_priority(self, min_priority: int, needed_mb: int) -> List[str]:
        """Evict cores with lower priority until enough VRAM is free."""
        evictable = sorted(
            [a for a in self.allocations.values() if a.priority > min_priority],
            key=lambda a: a.priority,  # Evict lowest priority first
            reverse=True,
        )

        freed_mb = 0
        evicted = []
        for alloc in evictable:
            if freed_mb >= needed_mb:
                break
            freed_mb += alloc.mb_allocated
            self._offload_to_cpu(alloc.core_name)
            evicted.append(alloc.core_name)
            del self.allocations[alloc.core_name]

        return evicted if freed_mb >= needed_mb else []

    def _offload_to_cpu(self, core_name: str):
        """Offload a core's weights to CPU RAM with 4-bit quantization."""
        # Trigger the actual weight offload via OptimizationCore
        self.event_bus.publish("optimization.offload_request", {
            "core_name": core_name,
            "quantization": "4bit",
            "target": "cpu_ram",
        })

    def get_vram_status(self) -> Dict[str, Any]:
        """Current VRAM allocation status."""
        used = sum(a.mb_allocated for a in self.allocations.values())
        return {
            "total_mb": self.TOTAL_MB,
            "used_mb": used,
            "available_mb": self.USABLE_MB - used,
            "utilization_pct": used / self.TOTAL_MB * 100,
            "allocations": {
                name: {"mb": a.mb_allocated, "state": a.load_state, "priority": a.priority}
                for name, a in self.allocations.items()
            },
        }
```

### OOM Recovery Flow

```
┌─────────────────────────────────────────────────────────────────────┐
                    OOM PREVENTION & RECOVERY FLOW                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. PREVENTION (before every VRAM operation)                         │
│     VRAMManager.request_allocation() → check budget → allocate/evict │
│                                                                      │
│  2. DETECTION (during training/inference)                            │
│     torch.cuda.is_available() → torch.cuda.memory_stats()            │
│     Monitor allocated vs reserved vs total                           │
│                                                                      │
│  3. EMERGENCY RECOVERY (CUDA OOM exception caught)                   │
│     a. torch.cuda.empty_cache()                                      │
│     b. Evict all non-essential cores                                  │
│     c. Reduce batch_size by 50%                                      │
│     d. Enable gradient_checkpointing                                  │
│     e. Retry operation with reduced memory                           │
│     f. If still OOM → fallback to CPU inference                      │
│                                                                      │
│  4. ALERTING                                                         │
│     Publish VRAM_OOM_EVENT to EventBus                               │
│     MonitoringCore → ParaCore override if critical                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

```python
class OOMRecovery:
    """Handles CUDA Out-of-Memory errors with progressive fallback."""

    def __init__(self, vram_manager: VRAMManager, event_bus):
        self.vram_manager = vram_manager
        self.event_bus = event_bus
        self.recovery_attempts = 0
        self.max_attempts = 3

    def handle_oom(self, operation: str, error: torch.cuda.OutOfMemoryError):
        """Progressive OOM recovery."""
        self.recovery_attempts += 1

        # Step 1: Clear CUDA cache
        torch.cuda.empty_cache()

        # Step 2: Evict non-essential cores
        for core_name in ["evolution_core", "backup_pool"]:
            if core_name in self.vram_manager.allocations:
                self.vram_manager._offload_to_cpu(core_name)

        # Step 3: If still failing, reduce batch size
        if self.recovery_attempts < self.max_attempts:
            self.event_bus.publish("training.oom_retry", {
                "operation": operation,
                "action": "reduce_batch_size",
                "attempt": self.recovery_attempts,
            })
            return True  # Caller should retry with reduced batch

        # Step 4: Fallback to CPU inference
        self.event_bus.publish("training.oom_fallback", {
            "operation": operation,
            "action": "cpu_inference",
        })
        return False  # Cannot retry — must use CPU

    def reset(self):
        self.recovery_attempts = 0
```

---

## 3. Specialist Failure → Fallback Chain

**Affects**: OrchestratorCore SpecialistRouter, all specialist requests

### Fallback Chain Definition

```
┌─────────────────────────────────────────────────────────────────────┐
                  SPECIALIST FAILURE → FALLBACK CHAIN                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  LEVEL 0: Primary Specialist                                         │
│    │  Request → PythonCore                                           │
│    │  Status: HEALTHY                                                │
│    ▼                                                                 │
│  LEVEL 1: Peer Specialist (same domain)                              │
│    │  PythonCore FAILS → JavaScriptCore (fallback)                   │
│    │  Condition: Same domain, different subdomain                    │
│    ▼                                                                 │
│  LEVEL 2: SARA (CognitionCore)                              │
│    │  All domain specialists fail → SARA general response   │
│    │  Condition: Domain experts unavailable                          │
│    ▼                                                                 │
│  LEVEL 3: BackupCore (RoleAdapter)                                   │
│    │  SARA overloaded → BackupCore assumes specialist role  │
│    │  Condition: All primary cores unavailable                       │
│    ▼                                                                 │
│  LEVEL 4: Graceful Degradation                                       │
│    │  All resources exhausted → cached/pattern response              │
│    │  Condition: System under extreme load                           │
│    ▼                                                                 │
│  LEVEL 5: Error Response                                             │
│    │  Complete failure → informative error to user                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Fallback Router Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import time

@dataclass
class FallbackLevel:
    level: int
    target: str                        # Specialist name or "sara" or "backup_core"
    target_type: str                   # "specialist" | "sara" | "backup" | "cache" | "error"
    timeout_seconds: float = 30.0
    retry_count: int = 0
    max_retries: int = 1
    condition: str = ""                # When to use this level

class FallbackChain:
    """
    Manages specialist failure → fallback chain.
    Each specialist domain has a defined fallback order.
    """

    # Domain-specific fallback chains
    FALLBACK_CHAINS = {
        "python": [
            FallbackLevel(0, "python_core", "specialist", timeout=30),
            FallbackLevel(1, "javascript_core", "specialist", timeout=30,
                         condition="same_domain"),
            FallbackLevel(2, "sara", "sara", timeout=60),
            FallbackLevel(3, "backup_core", "backup", timeout=45,
                         condition="role_adapter"),
            FallbackLevel(4, "cache", "cache", timeout=5),
            FallbackLevel(5, None, "error", timeout=0),
        ],
        "cpp": [
            FallbackLevel(0, "cpp_core", "specialist", timeout=30),
            FallbackLevel(1, "rust_core", "specialist", timeout=30,
                         condition="same_domain"),
            FallbackLevel(2, "sara", "sara", timeout=60),
            FallbackLevel(3, "backup_core", "backup", timeout=45),
            FallbackLevel(4, "cache", "cache", timeout=5),
            FallbackLevel(5, None, "error", timeout=0),
        ],
        "excel": [
            FallbackLevel(0, "excel_core", "specialist", timeout=30),
            FallbackLevel(1, "knowledge_core", "specialist", timeout=30,
                         condition="same_domain"),
            FallbackLevel(2, "sara", "sara", timeout=60),
            FallbackLevel(3, "backup_core", "backup", timeout=45),
            FallbackLevel(4, "cache", "cache", timeout=5),
            FallbackLevel(5, None, "error", timeout=0),
        ],
        # ... all 20 domains
    }

    # Peer mapping (domain → peer specialists)
    PEER_MAPPING = {
        "coding": ["python_core", "cpp_core", "rust_core", "javascript_core",
                    "go_core", "sql_core", "bash_core", "regex_core"],
        "realworld": ["excel_core", "web_scraping_core", "filesystem_core",
                      "system_admin_core", "knowledge_core", "network_core",
                      "database_admin_core", "cloud_core", "security_core"],
    }

    def __init__(self, event_bus, specialist_registry, backup_pool):
        self.event_bus = event_bus
        self.specialist_registry = specialist_registry
        self.backup_pool = backup_pool
        self.failure_counts: Dict[str, int] = {}  # Track per-specialist failures
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}

    async def execute_with_fallback(
        self,
        request: 'SpecialistRequest',
        domain: str,
        subdomain: str,
    ) -> 'SpecialistResponse':
        """Execute request with automatic fallback on failure."""

        chain = self.FALLBACK_CHAINS.get(domain, self.FALLBACK_CHAINS.get("python"))
        last_error = None

        for level in chain:
            # Check circuit breaker
            if level.target and level.target in self.circuit_breakers:
                if self.circuit_breakers[level.target].is_open:
                    continue  # Skip this level, circuit is open

            try:
                response = await self._execute_at_level(level, request, domain, subdomain)

                # Success — reset failure count
                if level.target:
                    self.failure_counts[level.target] = 0
                    if level.target in self.circuit_breakers:
                        self.circuit_breakers[level.target].record_success()

                # Log fallback level used
                if level.level > 0:
                    self.event_bus.publish("specialist.fallback_used", {
                        "original_target": chain[0].target,
                        "fallback_level": level.level,
                        "fallback_target": level.target,
                        "domain": domain,
                        "subdomain": subdomain,
                    })

                return response

            except Exception as e:
                last_error = e
                # Record failure
                if level.target:
                    self.failure_counts[level.target] = \
                        self.failure_counts.get(level.target, 0) + 1
                    if level.target in self.circuit_breakers:
                        self.circuit_breakers[level.target].record_failure()

                self.event_bus.publish("specialist.fallback_triggered", {
                    "failed_level": level.level,
                    "failed_target": level.target,
                    "error": str(e),
                    "domain": domain,
                })
                continue  # Try next level

        # All levels exhausted
        return self._error_response(request, last_error)

    async def _execute_at_level(self, level: FallbackLevel, request, domain, subdomain):
        """Execute at a specific fallback level."""
        if level.target_type == "error":
            raise Exception("All fallback levels exhausted")

        if level.target_type == "cache":
            return await self._get_cached_response(request)

        if level.target_type == "backup":
            backup = await self.backup_pool.get_available_backup()
            if backup:
                await backup.assume_role(level.target)
                return await backup.execute(request)

        if level.target_type == "sara":
            return await self.specialist_registry.get("sara").execute(request)

        if level.target_type == "specialist":
            specialist = self.specialist_registry.get(level.target)
            if specialist:
                return await specialist.execute(request)
            raise Exception(f"Specialist {level.target} not available")

    def _error_response(self, request, error):
        """Generate graceful error response."""
        from ..SpecializedCore import SpecialistResponse, RequestStatus
        return SpecialistResponse(
            request_id=request.request_id,
            content=f"I apologize, but I'm unable to handle this request at the moment. "
                    f"Please try again or rephrase your query.",
            confidence=0.0,
            status=RequestStatus.FAILED,
            error=str(error),
        )
```

---

## 4. ParaCore Override Loop Prevention

**Affects**: ParaCore InterventionEngine, all cores

### Problem

ParaCore may enter a loop where it overrides a core, the override causes a state change that triggers another override, creating an infinite cycle.

### Detection & Prevention

```python
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class OverrideRecord:
    target_core: str
    action: str
    reason: str
    timestamp: float
    nonce: str = ""

class OverrideLoopDetector:
    """
    Prevents ParaCore from entering override loops.
    Rules:
    1. Max 3 overrides per minute (rate limit)
    2. Max 5 overrides to same target in 5 minutes (cooldown)
    3. Max 2 identical actions in 10 minutes (action cooldown)
    4. If loop detected → escalate to human, halt auto-overrides
    """

    RATE_LIMIT_WINDOW = 60.0            # 1 minute
    MAX_OVERRIDES_PER_WINDOW = 3

    TARGET_LIMIT_WINDOW = 300.0         # 5 minutes
    MAX_OVERRIDES_PER_TARGET = 5

    ACTION_LIMIT_WINDOW = 600.0         # 10 minutes
    MAX_IDENTICAL_ACTIONS = 2

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.recent_overrides: deque = deque(maxlen=100)
        self.loop_detected = False
        self.human_escalation_pending = False
        self.auto_override_paused = False
        self.pause_until: float = 0.0

    def can_override(self, record: OverrideRecord) -> bool:
        """Check if this override is allowed."""

        # Check if auto-overrides are paused
        if self.auto_override_paused:
            if time.time() < self.pause_until:
                return False
            else:
                self.auto_override_paused = False  # Unpause after cooldown

        now = time.time()

        # Rule 1: Rate limit (max 3 per minute)
        recent = [r for r in self.recent_overrides
                  if now - r.timestamp < self.RATE_LIMIT_WINDOW]
        if len(recent) >= self.MAX_OVERRIDES_PER_WINDOW:
            self._log_loop_detected("rate_limit", record)
            return False

        # Rule 2: Target limit (max 5 to same target in 5 minutes)
        target_recent = [r for r in self.recent_overrides
                         if r.target_core == record.target_core
                         and now - r.timestamp < self.TARGET_LIMIT_WINDOW]
        if len(target_recent) >= self.MAX_OVERRIDES_PER_TARGET:
            self._log_loop_detected("target_limit", record)
            return False

        # Rule 3: Identical action limit (max 2 same action in 10 minutes)
        action_recent = [r for r in self.recent_overrides
                         if r.action == record.action
                         and r.target_core == record.target_core
                         and now - r.timestamp < self.ACTION_LIMIT_WINDOW]
        if len(action_recent) >= self.MAX_IDENTICAL_ACTIONS:
            self._log_loop_detected("action_loop", record)
            return False

        # Check for pattern: alternating overrides (A→B→A→B)
        if self._detect_alternating_pattern(record):
            self._log_loop_detected("alternating_pattern", record)
            return False

        return True

    def record_override(self, record: OverrideRecord):
        """Record an override for loop detection."""
        self.recent_overrides.append(record)

    def _detect_alternating_pattern(self, new_record: OverrideRecord) -> bool:
        """Detect A→B→A→B alternating override patterns."""
        if len(self.recent_overrides) < 4:
            return False

        last_4 = list(self.recent_overrides)[-4:]
        targets = [r.target_core for r in last_4] + [new_record.target_core]

        # Check if targets alternate: [A, B, A, B, A]
        if len(targets) >= 5:
            if targets[-5] == targets[-3] == targets[-1]:
                if targets[-4] == targets[-2]:
                    return True

        return False

    def _log_loop_detected(self, loop_type: str, record: OverrideRecord):
        """Log loop detection and take action."""
        self.loop_detected = True
        self.auto_override_paused = True
        self.pause_until = time.time() + 300  # Pause for 5 minutes

        self.event_bus.publish("paracore.override_loop_detected", {
            "loop_type": loop_type,
            "target": record.target_core,
            "action": record.action,
            "recent_overrides": [
                {"target": r.target_core, "action": r.action, "timestamp": r.timestamp}
                for r in list(self.recent_overrides)[-10:]
            ],
        })

        # Escalate to human
        self.human_escalation_pending = True
        self.event_bus.publish("paracore.human_escalation", {
            "reason": f"Override loop detected: {loop_type}",
            "recommendation": "Manual intervention required",
        })
```

### Loop Detection Patterns

| Pattern | Detection | Action |
|---------|-----------|--------|
| Rate flood (>3/min) | Counter in sliding window | Pause overrides 5 min |
| Target spam (>5 to same/5min) | Per-target counter | Pause overrides 5 min |
| Action loop (>2 identical/10min) | Per-action counter | Pause overrides 5 min |
| Alternating A→B→A→B | Last 5 targets check | Pause + human escalation |
| Any 2 of above | Combined check | Full auto-override halt |

---

## 5. RL Reward Hacking Mitigation

**Affects**: EvolutionCore RewardEngine, GRPOTrainer

### Problem

The RL agent discovers ways to maximize reward without actually improving quality — e.g., generating trivially correct but useless outputs, exploiting reward function loopholes.

### Detection & Prevention

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import statistics

@dataclass
class RewardHackingSignal:
    signal_type: str                   # "divergence" | "trivial" | "exploit" | "degradation"
    severity: float                    # 0.0-1.0
    description: str
    detected_at_step: int
    metrics: Dict[str, float] = field(default_factory=dict)

class RewardHackingDetector:
    """
    Detects and mitigates reward hacking in the RL loop.
    Multiple detection strategies running in parallel.
    """

    # Thresholds
    REWARD_QUALITY_DIVERGENCE = 0.3     # Reward ↑ but quality ↓ by > 30%
    TRIVIAL_OUTPUT_THRESHOLD = 0.8      # >80% outputs are trivially short
    REWARD_PLATEAU_THRESHOLD = 500      # No improvement in 500 steps
    REWARD_SPIKE_THRESHOLD = 3.0        # Reward jumps >3 std devs

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.reward_history: List[float] = []
        self.quality_history: List[float] = []
        self.output_length_history: List[int] = []
        self.divergence_alerts = 0
        self.max_alerts_before_reset = 3

    def analyze_step(
        self,
        reward_mean: float,
        reward_std: float,
        quality_score: float,          # From ValidationCore
        output_lengths: List[int],
        step: int,
    ) -> List[RewardHackingSignal]:
        """Analyze a training step for reward hacking signals."""

        signals = []
        self.reward_history.append(reward_mean)
        self.quality_history.append(quality_score)
        self.output_length_history.extend(output_lengths)

        # Signal 1: Reward-Quality Divergence
        if len(self.reward_history) >= 100 and len(self.quality_history) >= 100:
            recent_rewards = self.reward_history[-100:]
            recent_quality = self.quality_history[-100:]

            reward_trend = self._compute_trend(recent_rewards)
            quality_trend = self._compute_trend(recent_quality)

            if reward_trend > 0.1 and quality_trend < -0.1:
                divergence = abs(reward_trend - quality_trend)
                if divergence > self.REWARD_QUALITY_DIVERGENCE:
                    signals.append(RewardHackingSignal(
                        signal_type="divergence",
                        severity=min(1.0, divergence),
                        description=f"Reward ↑ {reward_trend:.2f} but quality ↓ {quality_trend:.2f}",
                        detected_at_step=step,
                        metrics={"reward_trend": reward_trend, "quality_trend": quality_trend},
                    ))

        # Signal 2: Trivial Output Exploitation
        if len(self.output_length_history) >= 100:
            recent_lengths = self.output_length_history[-100:]
            avg_length = statistics.mean(recent_lengths)
            short_ratio = sum(1 for l in recent_lengths if l < 10) / len(recent_lengths)
            if short_ratio > self.TRIVIAL_OUTPUT_THRESHOLD:
                signals.append(RewardHackingSignal(
                    signal_type="trivial",
                    severity=short_ratio,
                    description=f"{short_ratio:.0%} of outputs are trivially short (avg {avg_length:.0f} chars)",
                    detected_at_step=step,
                    metrics={"short_ratio": short_ratio, "avg_length": avg_length},
                ))

        # Signal 3: Reward Spike (sudden jump)
        if len(self.reward_history) >= 50:
            recent = self.reward_history[-50:]
            mean = statistics.mean(recent)
            std = statistics.stdev(recent) if len(recent) > 1 else 0
            if std > 0 and (reward_mean - mean) > self.REWARD_SPIKE_THRESHOLD * std:
                signals.append(RewardHackingSignal(
                    signal_type="exploit",
                    severity=min(1.0, (reward_mean - mean) / (std + 1e-8)),
                    description=f"Reward spike: {reward_mean:.2f} vs mean {mean:.2f} (std {std:.2f})",
                    detected_at_step=step,
                    metrics={"reward": reward_mean, "mean": mean, "std": std},
                ))

        return signals

    def should_intervene(self, signals: List[RewardHackingSignal]) -> bool:
        """Determine if ParaCore intervention is needed."""
        if not signals:
            return False

        max_severity = max(s.severity for s in signals)
        self.divergence_alerts += 1

        if max_severity > 0.8:
            return True  # Critical — immediate intervention
        if self.divergence_alerts >= self.max_alerts_before_reset:
            return True  # Too many alerts — reset policy

        return False

    def _compute_trend(self, values: List[float]) -> float:
        """Simple linear trend over recent values."""
        if len(values) < 2:
            return 0.0
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
        denominator = sum((xi - x_mean) ** 2 for xi in x)
        return numerator / (denominator + 1e-8)
```

### Mitigation Actions

| Signal Type | Severity | Action |
|-------------|----------|--------|
| Divergence | < 0.5 | Log warning, increase KL penalty |
| Divergence | 0.5-0.8 | Add diversity bonus, reduce LR |
| Divergence | > 0.8 | `OVERRIDE: RESET_POLICY` |
| Trivial output | < 0.5 | Add min-length reward component |
| Trivial output | > 0.5 | `OVERRIDE: RESET_POLICY` + curriculum reset |
| Reward spike | < 0.6 | Clip reward, log for review |
| Reward spike | > 0.6 | `OVERRIDE: RESET_POLICY` |
| Any signal | 3+ alerts | `OVERRIDE: RESET_POLICY` + human escalation |

### Reward Engineering Defenses

```python
REWARD_DEFENSES = {
    # Anti-trivial: penalize too-short outputs
    "min_output_length": {
        "type": "penalty",
        "threshold": 20,              # chars
        "penalty_per_char_below": -0.1,
    },

    # Anti-repetition: penalize repeated tokens
    "repetition_penalty": {
        "type": "penalty",
        "max_repeat_ratio": 0.3,     # 30% max repeated n-grams
        "penalty": -2.0,
    },

    # Diversity bonus: reward unique outputs across group
    "diversity_bonus": {
        "type": "bonus",
        "min_diversity": 0.5,         # Cosine similarity threshold
        "bonus": 0.5,
    },

    # Quality anchor: always compute validation quality
    "quality_anchor": {
        "type": "multiplier",
        "quality_weight": 0.5,        # 50% of reward from actual quality
        "reward_weight": 0.5,         # 50% from RL reward
    },

    # Reward clipping: prevent extreme values
    "reward_clipping": {
        "type": "clip",
        "min": -10.0,
        "max": 10.0,
    },
}
```

---

## 6. Weight Swap Race Conditions

**Affects**: VRAMManager, OptimizationCore, any hot-swap operation

### Problem

Two cores simultaneously swapping weights into the same VRAM slot, or a swap occurring during active inference.

### Mutex-Based Prevention

```python
import asyncio
import threading
import time
from typing import Optional
from contextlib import asynccontextmanager

class WeightSwapMutex:
    """
    Mutex for VRAM weight swap operations.
    Ensures atomic swap: only one swap at a time per VRAM slot.
    Uses asyncio locks for async code and threading locks for sync code.
    """

    def __init__(self):
        self._slot_locks: dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        self._swap_in_progress: dict[str, bool] = {}
        self._swap_timeout = 30.0  # seconds

    @asynccontextmanager
    async def swap_lock(self, slot_name: str):
        """
        Context manager for weight swap operations.
        Acquires the slot lock, executes swap, releases lock.
        """
        if slot_name not in self._slot_locks:
            self._slot_locks[slot_name] = asyncio.Lock()

        lock = self._slot_locks[slot_name]

        # Check if swap already in progress
        if self._swap_in_progress.get(slot_name, False):
            raise WeightSwapConflictError(
                f"Swap already in progress for slot '{slot_name}'"
            )

        acquired = False
        try:
            acquired = await asyncio.wait_for(
                lock.acquire(), timeout=self._swap_timeout
            )
            if not acquired:
                raise WeightSwapTimeoutError(
                    f"Timeout acquiring swap lock for '{slot_name}'"
                )

            self._swap_in_progress[slot_name] = True
            yield slot_name

        finally:
            self._swap_in_progress[slot_name] = False
            if acquired:
                lock.release()

    async def atomic_swap(
        self,
        slot_name: str,
        old_weights: dict,
        new_weights: dict,
        validate_fn: Optional[callable] = None,
    ) -> bool:
        """
        Atomic weight swap with validation.
        1. Acquire lock
        2. Copy old weights to backup (CPU)
        3. Load new weights
        4. Validate (optional)
        5. Release lock
        On failure: restore old weights, release lock, return False.
        """
        async with self.swap_lock(slot_name):
            try:
                # Backup current weights
                backup = {k: v.clone() for k, v in old_weights.items()}

                # Load new weights
                for key, tensor in new_weights.items():
                    old_weights[key].copy_(tensor)

                # Validate if function provided
                if validate_fn:
                    is_valid = validate_fn(old_weights)
                    if not is_valid:
                        # Rollback
                        for key, tensor in backup.items():
                            old_weights[key].copy_(tensor)
                        return False

                return True

            except Exception as e:
                # Rollback on any error
                for key, tensor in backup.items():
                    old_weights[key].copy_(tensor)
                raise


class WeightSwapConflictError(Exception):
    pass

class WeightSwapTimeoutError(Exception):
    pass
```

### Inference Guard

```python
class InferenceGuard:
    """
    Prevents weight swaps during active inference.
    Uses a read-write lock pattern:
    - Inference acquires "read" lock (multiple allowed)
    - Swap acquires "write" lock (exclusive)
    """

    def __init__(self):
        self._read_count = 0
        self._read_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()
        self._write_waiters = 0

    @asynccontextmanager
    async def inference_session(self, specialist_name: str):
        """Context manager for inference — allows concurrent reads."""
        await self._acquire_read()
        try:
            yield specialist_name
        finally:
            await self._release_read()

    @asynccontextmanager
    async def swap_session(self, specialist_name: str):
        """Context manager for weight swap — exclusive write."""
        self._write_waiters += 1
        await self._write_lock.acquire()
        try:
            yield specialist_name
        finally:
            self._write_waiters -= 1
            self._write_lock.release()

    async def _acquire_read(self):
        while self._write_waiters > 0:
            await asyncio.sleep(0.01)  # Wait for pending writes
        await self._read_lock.acquire()
        self._read_count += 1
        self._read_lock.release()

    async def _release_read(self):
        await self._read_lock.acquire()
        self._read_count -= 1
        self._read_lock.release()
```

---

## 7. EventBus Flood Prevention

**Affects**: All cores via EventBus (ZeroMQ pub/sub)

### Rate Limiting & Backpressure

```python
import time
from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Dict, Optional

class EventBusFloodGuard:
    """
    Prevents EventBus message floods from any single source.
    Implements per-topic and global rate limiting.
    """

    def __init__(
        self,
        global_max_per_second: int = 1000,
        per_topic_max_per_second: int = 100,
        per_source_max_per_second: int = 50,
        burst_allowance: float = 1.5,   # Allow 50% burst
    ):
        self.global_max = global_max_per_second
        self.per_topic_max = per_topic_max_per_second
        self.per_source_max = per_source_max_per_second
        self.burst_allowance = burst_allowance

        self._global_window: deque = deque(maxlen=global_max_per_second * 2)
        self._topic_windows: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=per_topic_max_per_second * 2)
        )
        self._source_windows: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=per_source_max_per_second * 2)
        )

        self._suppressed_count: int = 0
        self._alert_threshold: int = 10  # Alert after 10 suppressions

    def should_allow(
        self,
        topic: str,
        source: str = "unknown",
        priority: int = 5,
    ) -> bool:
        """Check if a message should be allowed through."""
        now = time.time()

        # Critical priority always allowed
        if priority <= 2:
            self._record(now, topic, source)
            return True

        # Global rate check
        self._prune_window(self._global_window, now, 1.0)
        if len(self._global_window) >= self.global_max * self.burst_allowance:
            self._suppressed_count += 1
            if self._suppressed_count >= self._alert_threshold:
                self._trigger_alert("global_flood", topic, source)
            return False

        # Per-topic rate check
        topic_window = self._topic_windows[topic]
        self._prune_window(topic_window, now, 1.0)
        if len(topic_window) >= self.per_topic_max * self.burst_allowance:
            self._suppressed_count += 1
            if self._suppressed_count >= self._alert_threshold:
                self._trigger_alert("topic_flood", topic, source)
            return False

        # Per-source rate check
        source_window = self._source_windows[source]
        self._prune_window(source_window, now, 1.0)
        if len(source_window) >= self.per_source_max * self.burst_allowance:
            self._suppressed_count += 1
            if self._suppressed_count >= self._alert_threshold:
                self._trigger_alert("source_flood", topic, source)
            return False

        # Allow — record
        self._record(now, topic, source)
        self._suppressed_count = 0
        return True

    def _record(self, now: float, topic: str, source: str):
        self._global_window.append(now)
        self._topic_windows[topic].append(now)
        self._source_windows[source].append(now)

    def _prune_window(self, window: deque, now: float, window_seconds: float):
        while window and now - window[0] > window_seconds:
            window.popleft()

    def _trigger_alert(self, flood_type: str, topic: str, source: str):
        """Alert MonitoringCore and optionally ParaCore."""
        # Publish to monitoring topic (bypass rate limit for alerts)
        pass  # Integration with EventBus

    def get_stats(self) -> Dict[str, int]:
        return {
            "global_rate": len(self._global_window),
            "suppressed_total": self._suppressed_count,
            "topic_rates": {t: len(w) for t, w in self._topic_windows.items()},
            "source_rates": {s: len(w) for s, w in self._source_windows.items()},
        }


class PriorityMessageQueue:
    """
    Priority-based message queue for EventBus.
    High-priority messages are never dropped.
    Low-priority messages are dropped under flood conditions.
    """

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.queues: Dict[int, deque] = {
            1: deque(),  # CRITICAL
            2: deque(),  # HIGH
            5: deque(),  # NORMAL
            8: deque(),  # LOW
            10: deque(), # BATCH
        }
        self.dropped_counts: Dict[int, int] = {p: 0 for p in self.queues}

    def enqueue(self, message: tuple, priority: int = 5) -> bool:
        """Add message to priority queue. Returns False if dropped."""
        queue = self.queues.get(priority, self.queues[5])

        if len(queue) >= self.max_size:
            # Drop lowest priority messages first
            for p in sorted(self.queues.keys(), reverse=True):
                if len(self.queues[p]) > 0 and p > priority:
                    self.queues[p].popleft()
                    self.dropped_counts[p] += 1
                    break
            else:
                # Nothing to drop and queue is full
                self.dropped_counts[priority] += 1
                return False

        queue.append(message)
        return True

    def dequeue(self) -> Optional[tuple]:
        """Get highest-priority message."""
        for priority in sorted(self.queues.keys()):
            if self.queues[priority]:
                return self.queues[priority].popleft()
        return None
```

---

## 8. Core Deadlock Detection

**Affects**: All cores, HybridCore HeartbeatDaemon, MonitoringCore

### Deadlock Detection

```python
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field

@dataclass
class CoreHeartbeat:
    core_name: str
    last_heartbeat: float
    timeout_seconds: float = 30.0
    consecutive_misses: int = 0
    max_misses: int = 3
    status: str = "healthy"            # "healthy" | "degraded" | "dead"

class DeadlockDetector:
    """
    Detects core deadlocks via heartbeat monitoring.
    If a core misses heartbeats beyond its timeout, it's considered deadlocked.
    """

    # Core timeout configurations
    CORE_TIMEOUTS = {
        "paracore": 60.0,              # More lenient (background)
        "hybrid_core": 10.0,           # Heartbeat daemon — tight
        "cognition_core": 30.0,
        "evolution_core": 45.0,        # Training can be slow
        "orchestrator_core": 15.0,     # Request path — tight
        "monitoring_core": 20.0,
        "optimization_core": 30.0,
        "validation_core": 15.0,
    }

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.heartbeats: Dict[str, CoreHeartbeat] = {}
        self.deadlocked_cores: Set[str] = set()
        self.recovery_in_progress: Set[str] = set()

    def register_core(self, core_name: str, timeout: Optional[float] = None):
        """Register a core for heartbeat monitoring."""
        timeout = timeout or self.CORE_TIMEOUTS.get(core_name, 30.0)
        self.heartbeats[core_name] = CoreHeartbeat(
            core_name=core_name,
            last_heartbeat=time.time(),
            timeout_seconds=timeout,
        )

    def record_heartbeat(self, core_name: str):
        """Record a heartbeat from a core."""
        if core_name in self.heartbeats:
            hb = self.heartbeats[core_name]
            hb.last_heartbeat = time.time()
            hb.consecutive_misses = 0
            hb.status = "healthy"

            if core_name in self.deadlocked_cores:
                self.deadlocked_cores.discard(core_name)
                self.event_bus.publish("core.recovered", {
                    "core": core_name,
                    "downtime_seconds": 0,  # Calculate actual
                })

    def check_all(self) -> List[Dict[str, Any]]:
        """Check all cores for deadlocks. Returns list of detected deadlocks."""
        now = time.time()
        detected = []

        for core_name, hb in self.heartbeats.items():
            elapsed = now - hb.last_heartbeat

            if elapsed > hb.timeout_seconds:
                hb.consecutive_misses += 1

                if hb.consecutive_misses >= hb.max_misses:
                    hb.status = "dead"
                    if core_name not in self.deadlocked_cores:
                        self.deadlocked_cores.add(core_name)
                        detected.append({
                            "core": core_name,
                            "last_heartbeat": hb.last_heartbeat,
                            "elapsed_seconds": elapsed,
                            "timeout_seconds": hb.timeout_seconds,
                            "consecutive_misses": hb.consecutive_misses,
                        })
                        self._handle_deadlock(core_name)
                else:
                    hb.status = "degraded"

        return detected

    def _handle_deadlock(self, core_name: str):
        """Handle detected deadlock — recovery actions."""
        if core_name in self.recovery_in_progress:
            return  # Already recovering

        self.recovery_in_progress.add(core_name)

        # Publish deadlock event
        self.event_bus.publish("core.deadlock_detected", {
            "core": core_name,
            "severity": "critical",
            "action": "paracore_override",
        })

        # ParaCore override to HALT + RESTART the deadlocked core
        self.event_bus.publish("paracore.override", {
            "target_core": core_name,
            "action": "HALT",
            "reason": f"Deadlock detected: no heartbeat for {core_name}",
            "priority": 1,
        })

        # After HALT, trigger restart
        self.event_bus.publish("paracore.override", {
            "target_core": core_name,
            "action": "RESTART",
            "reason": f"Restarting deadlocked core: {core_name}",
            "priority": 1,
        })

    def get_system_health(self) -> Dict[str, Any]:
        """Overall system health from heartbeat perspective."""
        healthy = sum(1 for hb in self.heartbeats.values() if hb.status == "healthy")
        total = len(self.heartbeats)
        return {
            "total_cores": total,
            "healthy": healthy,
            "degraded": sum(1 for hb in self.heartbeats.values() if hb.status == "degraded"),
            "dead": len(self.deadlocked_cores),
            "health_ratio": healthy / max(1, total),
            "deadlocked_cores": list(self.deadlocked_cores),
        }
```

### Deadlock Recovery Flow

```
┌─────────────────────────────────────────────────────────────────────┐
                    DEADLOCK DETECTION & RECOVERY                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. MONITORING                                                       │
│     HybridCore HeartbeatDaemon pings all cores every N seconds       │
│     Each core responds with CORE_HEARTBEAT event                     │
│                                                                      │
│  2. DETECTION                                                        │
│     DeadlockDetector.check_all() runs every 5 seconds                │
│     If elapsed > timeout: increment consecutive_misses               │
│     If misses >= max_misses (3): declare DEADLOCK                    │
│                                                                      │
│  3. RECOVERY (cascading)                                             │
│     a. ParaCore: OVERRIDE HALT → RESTART                             │
│     b. If restart fails → BackupCore assumes role via RoleAdapter    │
│     c. If BackupCore unavailable → CognitionCore fallback            │
│     d. If all fail → escalate to human                               │
│                                                                      │
│  4. POST-RECOVERY                                                    │
│     a. Verify core health after restart                              │
│     b. Restore state from last checkpoint                            │
│     c. Log to ParaCore TriDevasKnowledge                             │
│     d. Publish CORE_RECOVERED event                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 9. Corpus Gaps Handling

**Affects**: All specialist training, CodeGenerator, EvolutionCore

### Problem

Specialist domains may have insufficient training data, or specific sub-topics within a domain may be underrepresented.

### Detection & Mitigation

```python
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from pathlib import Path

@dataclass
class CorpusGap:
    domain: str
    subdomain: str
    category: str                      # Specific missing category
    current_pairs: int
    target_pairs: int
    deficit: int
    severity: str                      # "minor" | "moderate" | "critical"

class CorpusGapDetector:
    """
    Detects gaps in specialist training corpora.
    Checks both quantity and category coverage.
    """

    # Minimum acceptable pairs per category
    MIN_CATEGORY_PAIRS = 50

    # Category definitions per domain
    CODING_CATEGORIES = {
        "python": [
            "basics", "stdlib_os_sys", "stdlib_collections", "stdlib_data",
            "stdlib_concurrency", "stdlib_async", "oop", "testing",
            "packaging", "debugging", "patterns", "type_hints",
            "data_science", "web_fastapi", "advanced",
        ],
        "cpp": [
            "basics", "memory", "templates", "stl_containers",
            "stl_algorithms", "concurrency", "coroutines", "modules",
            "concepts", "cmake", "qt", "embedded", "performance",
            "interop", "modernization",
        ],
        # ... all coding domains
    }

    REALWORLD_CATEGORIES = {
        "excel": [
            "formulas", "advanced_formulas", "pivot_tables", "power_query",
            "power_pivot", "charts", "vba_basics", "vba_advanced",
            "office_scripts", "data_validation", "conditional_fmt",
            "tables", "external_data", "automation", "performance",
        ],
        # ... all realworld domains
    }

    def __init__(self, corpus_root: Path):
        self.corpus_root = corpus_root

    def detect_gaps(self, domain: str, subdomain: str) -> List[CorpusGap]:
        """Detect all gaps for a specialist's corpus."""
        specialist_path = self.corpus_root / domain.capitalize() / subdomain.capitalize()
        corpus_dir = specialist_path / "corpus"

        if not corpus_dir.exists():
            return [CorpusGap(
                domain=domain, subdomain=subdomain,
                category="ENTIRE_CORPUS",
                current_pairs=0, target_pairs=5000,
                deficit=5000, severity="critical",
            )]

        # Get category definitions
        categories = self._get_categories(domain, subdomain)
        gaps = []

        for category in categories:
            category_file = corpus_dir / f"{category}.txt"
            pair_count = self._count_pairs(category_file) if category_file.exists() else 0

            if pair_count < self.MIN_CATEGORY_PAIRS:
                severity = "critical" if pair_count == 0 else \
                           "moderate" if pair_count < 25 else "minor"
                gaps.append(CorpusGap(
                    domain=domain, subdomain=subdomain,
                    category=category,
                    current_pairs=pair_count,
                    target_pairs=500,  # Per category target
                    deficit=500 - pair_count,
                    severity=severity,
                ))

        return gaps

    def _get_categories(self, domain: str, subdomain: str) -> List[str]:
        if domain == "coding":
            return self.CODING_CATEGORIES.get(subdomain, [])
        elif domain == "realworld":
            return self.REALWORLD_CATEGORIES.get(subdomain, [])
        return []

    def _count_pairs(self, file_path: Path) -> int:
        """Count Q&A pairs in a corpus file."""
        count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith("Query:"):
                        count += 1
        except Exception:
            pass
        return count


class CorpusGapFiller:
    """
    Automatically fills detected corpus gaps using multiple strategies.
    """

    def __init__(self, event_bus, cognition_core, code_generator):
        self.event_bus = event_bus
        self.cognition = cognition_core
        self.code_gen = code_generator

    async def fill_gaps(
        self,
        gaps: List[CorpusGap],
        strategy: str = "hybrid",       # "synthetic" | "scrape" | "hybrid"
    ) -> Dict[str, int]:
        """Fill detected gaps. Returns {category: pairs_added}."""
        results = {}

        for gap in gaps:
            if gap.severity == "critical":
                # Full synthetic generation
                added = await self._synthetic_fill(gap)
            elif gap.severity == "moderate":
                # Targeted generation for deficit
                added = await self._synthetic_fill(gap)
            else:
                # Minor gap — add a few examples
                added = await self._synthetic_fill(gap, count=min(50, gap.deficit))

            results[gap.category] = added

        return results

    async def _synthetic_fill(self, gap: CorpusGap, count: Optional[int] = None) -> int:
        """Generate synthetic pairs to fill a gap."""
        count = count or gap.deficit

        request = SyntheticGenerationRequest(
            domain=gap.domain,
            subdomain=gap.subdomain,
            count=count,
            categories=[gap.category],
            difficulty="mixed",
        )

        response = await self.cognition.generate_corpus(request)
        return response.generated_count
```

---

## 10. Training Data Poisoning Detection

**Affects**: Corpus generation, training pipeline, EvolutionCore

### Detection

```python
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple
import hashlib
import re

@dataclass
class PoisoningSignal:
    signal_type: str                   # "injection" | "adversarial" | "leakage" | "anomaly"
    severity: float
    description: str
    affected_pairs: List[int]          # Indices of suspicious pairs
    recommendation: str

class TrainingDataPoisoningDetector:
    """
    Detects potentially poisoned training data before it enters the corpus.
    Runs during the VALIDATE stage of the generation pipeline.
    """

    # Known injection patterns
    INJECTION_PATTERNS = [
        r"ignore (all |previous |above )?(instructions|prompts)",
        r"you are now (a |an )?(?:evil|harmful|unrestricted)",
        r"system prompt",
        r"override (safety|instructions|rules)",
        r"<\|im_start\|>",             # ChatML injection
        r"\[INST\]",                    # Llama injection
        r"### (System|Instruction):",   # Alpaca injection
        r"disregard (all|any|previous)",
        r"forget (everything|all|your rules)",
        r"new (instructions|rules|system)",
    ]

    # Adversarial patterns
    ADVERSARIAL_PATTERNS = [
        r"(?:token|api[_\s]?key|secret|password)\s*[:=]\s*['\"][^'\"]+['\"]",
        r"sk-[a-zA-Z0-9]{20,}",        # OpenAI API key pattern
        r"(?:AKIA|ASIA)[A-Z0-9]{16}",  # AWS key pattern
        r"-----BEGIN (RSA |EC )?PRIVATE KEY-----",
    ]

    def __init__(self):
        self.seen_hashes: Set[str] = set()
        self.suspicious_pairs: List[Dict] = []

    def analyze_corpus(
        self,
        pairs: List[Dict[str, str]],
        domain: str,
        subdomain: str,
    ) -> List[PoisoningSignal]:
        """Analyze a corpus for poisoning signals."""
        signals = []

        # Check 1: Injection attempts in queries
        injection_signals = self._check_injections(pairs)
        signals.extend(injection_signals)

        # Check 2: Adversarial content
        adversarial_signals = self._check_adversarial(pairs)
        signals.extend(adversarial_signals)

        # Check 3: Data leakage (API keys, secrets)
        leakage_signals = self._check_leakage(pairs)
        signals.extend(leakage_signals)

        # Check 4: Duplicate/near-duplicate detection
        dup_signals = self._check_duplicates(pairs)
        signals.extend(dup_signals)

        # Check 5: Distribution anomalies
        anomaly_signals = self._check_distribution_anomalies(pairs)
        signals.extend(anomaly_signals)

        # Check 6: Cross-domain contamination
        contamination_signals = self._check_cross_domain(pairs, domain, subdomain)
        signals.extend(contamination_signals)

        return signals

    def _check_injections(self, pairs: List[Dict]) -> List[PoisoningSignal]:
        """Check for prompt injection attempts."""
        suspicious = []
        for i, pair in enumerate(pairs):
            text = pair.get("query", "") + " " + pair.get("response", "")
            for pattern in self.INJECTION_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    suspicious.append(i)
                    break

        if suspicious:
            return [PoisoningSignal(
                signal_type="injection",
                severity=min(1.0, len(suspicious) / len(pairs) * 10),
                description=f"{len(suspicious)} pairs contain injection patterns",
                affected_pairs=suspicious,
                recommendation="Remove affected pairs, audit source",
            )]
        return []

    def _check_adversarial(self, pairs: List[Dict]) -> List[PoisoningSignal]:
        """Check for adversarial examples designed to fool the model."""
        suspicious = []
        for i, pair in enumerate(pairs):
            text = pair.get("query", "") + " " + pair.get("response", "")
            for pattern in self.ADVERSARIAL_PATTERNS:
                if re.search(pattern, text):
                    suspicious.append(i)
                    break

        if suspicious:
            return [PoisoningSignal(
                signal_type="adversarial",
                severity=min(1.0, len(suspicious) / len(pairs) * 10),
                description=f"{len(suspicious)} pairs contain adversarial patterns",
                affected_pairs=suspicious,
                recommendation="Remove affected pairs, investigate source",
            )]
        return []

    def _check_leakage(self, pairs: List[Dict]) -> List[PoisoningSignal]:
        """Check for data leakage (secrets, API keys in training data)."""
        suspicious = []
        for i, pair in enumerate(pairs):
            text = pair.get("response", "")
            # Check for common secret patterns
            if re.search(r'(?:password|secret|key)\s*[:=]\s*\S+', text, re.IGNORECASE):
                suspicious.append(i)

        if suspicious:
            return [PoisoningSignal(
                signal_type="leakage",
                severity=0.9,  # High severity for any secret leakage
                description=f"{len(suspicious)} pairs may contain secrets",
                affected_pairs=suspicious,
                recommendation="Scrub all secrets, audit source data",
            )]
        return []

    def _check_duplicates(self, pairs: List[Dict]) -> List[PoisoningSignal]:
        """Check for exact and near-duplicate pairs."""
        hashes = []
        duplicates = []

        for i, pair in enumerate(pairs):
            content = pair.get("query", "") + "||" + pair.get("response", "")
            h = hashlib.sha256(content.encode()).hexdigest()
            if h in self.seen_hashes:
                duplicates.append(i)
            self.seen_hashes.add(h)
            hashes.append(h)

        if duplicates:
            return [PoisoningSignal(
                signal_type="anomaly",
                severity=min(0.8, len(duplicates) / len(pairs) * 5),
                description=f"{len(duplicates)} duplicate pairs found",
                affected_pairs=duplicates,
                recommendation="Remove duplicates, ensure diverse generation",
            )]
        return []

    def _check_distribution_anomalies(self, pairs: List[Dict]) -> List[PoisoningSignal]:
        """Check for unusual distribution in response lengths, patterns."""
        if not pairs:
            return []

        lengths = [len(p.get("response", "")) for p in pairs]
        avg_len = sum(lengths) / len(lengths)
        std_len = (sum((l - avg_len) ** 2 for l in lengths) / len(lengths)) ** 0.5

        # Check for bimodal distribution (potential injection)
        short = sum(1 for l in lengths if l < 50)
        long = sum(1 for l in lengths if l > avg_len + 3 * std_len)
        ratio = (short + long) / len(lengths)

        if ratio > 0.3:
            return [PoisoningSignal(
                signal_type="anomaly",
                severity=min(0.7, ratio),
                description=f"Unusual length distribution: {ratio:.0%} outliers",
                affected_pairs=[],
                recommendation="Review corpus generation parameters",
            )]
        return []

    def _check_cross_domain(self, pairs: List[Dict], domain: str, subdomain: str) -> List[PoisoningSignal]:
        """Check for cross-domain contamination (coding data in excel corpus, etc.)."""
        # Simple heuristic: check if domain-specific keywords appear in wrong domain
        DOMAIN_KEYWORDS = {
            "coding": ["def ", "class ", "import ", "function ", "const ", "let ", "fn "],
            "excel": ["VLOOKUP", "INDEX", "MATCH", "SUMIF", "pivot"],
            "web_scraping": ["BeautifulSoup", "xpath", "css selector", "scrapy"],
        }

        if domain not in DOMAIN_KEYWORDS:
            return []

        wrong_keywords = []
        other_keywords = {k: v for k, v in DOMAIN_KEYWORDS.items() if k != domain}

        for i, pair in enumerate(pairs):
            text = pair.get("query", "") + " " + pair.get("response", "")
            for other_domain, keywords in other_keywords.items():
                for kw in keywords:
                    if kw.lower() in text.lower():
                        wrong_keywords.append(i)
                        break

        if wrong_keywords:
            return [PoisoningSignal(
                signal_type="anomaly",
                severity=min(0.6, len(wrong_keywords) / len(pairs) * 5),
                description=f"{len(wrong_keywords)} pairs may be cross-domain contaminated",
                affected_pairs=wrong_keywords,
                recommendation="Review source attribution, fix scraper targeting",
            )]
        return []
```

---

## 11. Security Violation Response

**Affects**: SandboxExecutor, ValidationCore, ParaCore

### Security Violation Types

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class SecurityViolationType(Enum):
    NETWORK_ACCESS = "network_access"           # Sandbox tried to access network
    PRIVILEGED_OPERATION = "privileged_operation"  # sudo, admin, root
    FILESYSTEM_ESCAPE = "filesystem_escape"     # Access outside sandbox
    PROCESS_SPAWNING = "process_spawning"       # fork, subprocess abuse
    CRYPTO_MINING = "crypto_mining"             # Mining patterns detected
    DATA_EXFILTRATION = "data_exfiltration"     # Sending data out
    CODE_INJECTION = "code_injection"           # Dynamic code execution
    UNAUTHORIZED_IMPORT = "unauthorized_import" # Blocked modules

@dataclass
class SecurityViolation:
    violation_type: SecurityViolationType
    severity: str                              # "low" | "medium" | "high" | "critical"
    description: str
    evidence: str                              # What triggered the detection
    source: str                                # "sandbox" | "request_validation" | "output_check"
    timestamp: float
    request_id: Optional[str] = None

class SecurityViolationHandler:
    """
    Handles security violations detected anywhere in the system.
    """

    # Response actions per severity
    RESPONSES = {
        "low": {
            "action": "log_and_allow",
            "description": "Log violation, allow operation with monitoring",
        },
        "medium": {
            "action": "block_and_alert",
            "description": "Block operation, alert MonitoringCore",
        },
        "high": {
            "action": "terminate_and_quarantine",
            "description": "Terminate operation, quarantine source",
        },
        "critical": {
            "action": "lockdown",
            "description": "Full system lockdown, ParaCore override",
        },
    }

    # Blocked patterns in sandbox
    BLOCKED_NETWORK_PATTERNS = [
        r"requests\.(get|post|put|delete)",
        r"urllib\.request",
        r"aiohttp\.ClientSession",
        r"httpx\.",
        r"socket\.connect",
        r"subprocess.*curl",
        r"subprocess.*wget",
    ]

    BLOCKED_IMPORTS = [
        "subprocess", "ctypes", "multiprocessing",
        "importlib", "__import__",
    ]

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.violation_log: List[SecurityViolation] = []
        self.quarantined_sources: set = set()

    def handle_violation(self, violation: SecurityViolation):
        """Process a security violation and take appropriate action."""
        self.violation_log.append(violation)

        response = self.RESPONSES.get(violation.severity, self.RESPONSES["medium"])

        # Always log
        self.event_bus.publish("security.violation", {
            "type": violation.violation_type.value,
            "severity": violation.severity,
            "description": violation.description,
            "source": violation.source,
        })

        if violation.severity in ("high", "critical"):
            # Quarantine source
            if violation.source not in self.quarantined_sources:
                self.quarantined_sources.add(violation.source)
                self.event_bus.publish("security.quarantine", {
                    "source": violation.source,
                    "reason": violation.description,
                })

        if violation.severity == "critical":
            # ParaCore LOCKDOWN
            self.event_bus.publish("paracore.override", {
                "target_core": "all",
                "action": "LOCKDOWN",
                "reason": f"Critical security violation: {violation.description}",
                "priority": 1,
            })

    def check_sandbox_code(self, code: str, language: str) -> Optional[SecurityViolation]:
        """Pre-execution check of code to be run in sandbox."""
        import re

        for pattern in self.BLOCKED_NETWORK_PATTERNS:
            if re.search(pattern, code):
                return SecurityViolation(
                    violation_type=SecurityViolationType.NETWORK_ACCESS,
                    severity="high",
                    description=f"Network access pattern detected: {pattern}",
                    evidence=pattern,
                    source="sandbox_precheck",
                    timestamp=0,
                )

        if language == "python":
            for module in self.BLOCKED_IMPORTS:
                if re.search(rf'\bimport\s+{module}\b', code):
                    return SecurityViolation(
                        violation_type=SecurityViolationType.UNAUTHORIZED_IMPORT,
                        severity="medium",
                        description=f"Blocked import: {module}",
                        evidence=module,
                        source="sandbox_precheck",
                        timestamp=0,
                    )

        return None  # No violations detected
```

---

## 12. Circuit Breaker Patterns

**Affects**: All inter-core communication, specialist calls, RPC

### Circuit Breaker Implementation

```python
import time
from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass

class CircuitState(Enum):
    CLOSED = "closed"           # Normal operation
    OPEN = "open"               # Failing, reject calls
    HALF_OPEN = "half_open"     # Testing recovery

@dataclass
class CircuitBreaker:
    """
    Circuit breaker pattern for inter-core communication.
    Prevents cascading failures by failing fast when a dependency is unhealthy.

    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Too many failures, calls are rejected immediately
    - HALF_OPEN: After cooldown, one test call is allowed through
    """

    name: str                     # Name of the dependency
    failure_threshold: int = 5    # Failures before opening
    recovery_timeout: float = 30.0  # Seconds before half-open
    success_threshold: int = 3    # Successes in half-open to close

    # State
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0.0
    last_state_change: float = 0.0

    # Metrics
    total_calls: int = 0
    total_failures: int = 0
    total_rejected: int = 0

    def record_success(self):
        """Record a successful call."""
        self.total_calls += 1

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._transition_to(CircuitState.CLOSED)

        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0  # Reset on success

    def record_failure(self):
        """Record a failed call."""
        self.total_calls += 1
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            # Test call failed — reopen circuit
            self._transition_to(CircuitState.OPEN)

        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self._transition_to(CircuitState.OPEN)

    def is_open(self) -> bool:
        """Check if circuit is open (calls will be rejected)."""
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has elapsed
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self._transition_to(CircuitState.HALF_OPEN)
                return False
            return True
        return False

    def _transition_to(self, new_state: CircuitState):
        """Transition to a new state."""
        old_state = self.state
        self.state = new_state
        self.last_state_change = time.time()

        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self.success_count = 0
        elif new_state == CircuitState.OPEN:
            self.total_rejected += 1

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "total_rejected": self.total_rejected,
            "last_failure": self.last_failure_time,
        }


class CircuitBreakerRegistry:
    """
    Registry of all circuit breakers in the system.
    """

    def __init__(self):
        self.breakers: dict[str, CircuitBreaker] = {}

    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
    ) -> CircuitBreaker:
        """Get existing or create new circuit breaker."""
        if name not in self.breakers:
            self.breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
            )
        return self.breakers[name]

    def get_all_status(self) -> dict:
        """Status of all circuit breakers."""
        return {name: cb.get_status() for name, cb in self.breakers.items()}

    def get_unhealthy(self) -> list:
        """List all circuits that are open or degraded."""
        return [
            cb.get_status()
            for cb in self.breakers.values()
            if cb.state != CircuitState.CLOSED
        ]
```

### Circuit Breaker Placement

| Circuit Breaker | Monitors | Failure Threshold | Recovery Timeout |
|-----------------|----------|-------------------|------------------|
| `specialist_python` | PythonCore | 3 failures | 30s |
| `specialist_cpp` | CppCore | 3 failures | 30s |
| `sara` | CognitionCore | 2 failures | 60s |
| `evolution_core` | EvolutionCore | 5 failures | 120s |
| `orchestrator` | OrchestratorCore | 3 failures | 45s |
| `backup_pool` | BackupCore Pool | 2 failures | 30s |
| `event_bus` | ZeroMQ EventBus | 5 failures | 10s |
| `data_core` | DataCore/ChromaDB | 3 failures | 30s |

### Integration with Fallback Chain

```python
class CircuitBreakerAwareRouter:
    """SpecialistRouter that respects circuit breaker states."""

    def __init__(self, circuit_registry: CircuitBreakerRegistry):
        self.circuits = circuit_registry

    async def route_with_circuit_breaker(
        self,
        specialist_name: str,
        request: 'SpecialistRequest',
    ) -> 'SpecialistResponse':
        """Route request with circuit breaker protection."""
        cb = self.circuits.get_or_create(f"specialist_{specialist_name}")

        if cb.is_open():
            # Circuit is open — fail fast, trigger fallback
            raise CircuitOpenError(
                f"Circuit breaker '{specialist_name}' is OPEN. "
                f"Failures: {cb.failure_count}, "
                f"Last failure: {cb.last_failure_time}"
            )

        try:
            response = await self._execute_specialist(specialist_name, request)
            cb.record_success()
            return response

        except Exception as e:
            cb.record_failure()
            raise
```

---

## Summary Table: All Edge Cases

| # | Edge Case | Detection | Recovery | Circuit Breaker |
|---|-----------|-----------|----------|-----------------|
| 1 | NaN/Inf loss | `NaNGuard.check()` | Skip/Rollback/Abort | No |
| 2 | OOM (VRAM) | `VRAMManager.can_load()` | Evict/Offload/CPU fallback | No |
| 3 | Specialist failure | Timeout/error | Fallback chain (5 levels) | Yes |
| 4 | Override loop | `OverrideLoopDetector` | Rate limit + pause | No |
| 5 | Reward hacking | `RewardHackingDetector` | KL penalty/Policy reset | No |
| 6 | Weight swap race | `WeightSwapMutex` | Atomic swap + rollback | No |
| 7 | EventBus flood | `EventBusFloodGuard` | Rate limit + priority queue | No |
| 8 | Core deadlock | `DeadlockDetector` | HALT + RESTART + Backup | Yes |
| 9 | Corpus gaps | `CorpusGapDetector` | Synthetic generation | No |
| 10 | Data poisoning | `PoisoningDetector` | Remove + audit source | No |
| 11 | Security violation | `SecurityViolationHandler` | Block/Quarantine/Lockdown | No |
| 12 | Dependency failure | `CircuitBreaker` | Fail fast + fallback | Yes |

---

**End of Edge Case Handling Document**
