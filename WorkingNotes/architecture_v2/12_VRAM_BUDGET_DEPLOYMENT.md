# VRAM Budget & Deployment Strategy

## 1. RTX 4060 8GB VRAM Budget

The entire Vibhu-Oska AI-OS must operate within 8 GB of VRAM on an RTX 4060.
Every component is carefully budgeted and managed.

### Budget Breakdown Table

| Component            | Size (GB) | State      | Priority | Evictable |
|----------------------|-----------|------------|----------|-----------|
| SARA        | 4.2       | Always Hot | 1        | No        |
| Router               | 0.2       | Always Hot | 2        | No        |
| FastResponderCore    | 0.4       | Always Hot | 3        | No        |
| Specialist Slot A    | 1.2       | Hot-Swap   | 4        | Yes       |
| Specialist Slot B    | 1.2       | Hot-Swap   | 5        | Yes       |
| BackupCore Pool      | 1.6       | Warm       | 6        | Yes       |
| CUDA Overhead        | 0.3       | Fixed      | —        | No        |
| **Total**            | **9.1**   |            |          |           |
| **Active Budget**    | **7.7**   |            |          |           |
| **Reserve Buffer**   | **0.3**   |            |          |           |

```
8 GB RTX 4060 VRAM Layout:
┌─────────────────────────────────────────────────────────────────────┐
│  SARA  │  Router  │ FastResp │ Slot A │ Slot B │ CUDA    │
│     4.2 GB      │  0.2 GB  │  0.4 GB  │ 1.2 GB │ 1.2 GB │ 0.3 GB  │
│   [always hot]  │ [always] │ [always] │[swap]  │ [swap] │ [fixed] │
└─────────────────────────────────────────────────────────────────────┘
  Used: 7.5 GB  |  Free: 0.3 GB (reserve)  |  Total: 8.0 GB
```

## 2. Always-Hot Components

These three components are **never evicted** from VRAM. They form the
permanent backbone of the inference system.

### SARA (4.2 GB)

- The primary reasoning engine
- 4-bit quantized (GPTQ/AWQ) for VRAM efficiency
- Handles complex reasoning, planning, code generation
- Always resident to avoid cold-start latency (2-5s load time)

```python
# sara_config.yaml
sara:
  model: "meta-llama/Llama-3-8B-Instruct"
  quantization: "4bit-gptq"
  vram_target_gb: 4.2
  max_batch_size: 1
  max_context: 4096
  eviction_policy: "never"
  offload_to_cpu: false
```

### Router (0.2 GB)

- Lightweight query classifier and dispatcher
- Routes queries to FastResponder or specialists
- Maintains routing table and load balancing state

```python
# router_config.yaml
router:
  model: "custom-router-200m"
  quantization: "fp16"
  vram_target_gb: 0.2
  routing_strategy: "confidence_based"
  eviction_policy: "never"
```

### FastResponderCore (0.4 GB)

- Handles trivial queries (math, time, facts, greetings)
- Prevents specialist pipeline invocation for ~50% of queries
- Always loaded for sub-50ms response times

```python
# fast_responder_config.yaml
fast_responder:
  model: "fast-responder-5m"
  quantization: "fp16"
  vram_target_gb: 0.4
  eviction_policy: "never"
```

## 3. Hot-Swap Slots (2 Active Specialists)

Two dynamic slots hold currently-active specialist models. These are loaded
on-demand and evicted when no longer needed.

### Slot Allocation

```
┌──────────────────────────────────────────────────────┐
│                    Hot-Swap Pool                      │
├─────────────────────┬────────────────────────────────┤
│     Slot A (1.2GB)  │      Slot B (1.2GB)            │
│  ┌───────────────┐  │  ┌───────────────┐            │
│  │  Code Writer   │  │  │  Data Analyst  │            │
│  │  (4-bit, 7B)   │  │  │  (4-bit, 7B)   │            │
│  └───────────────┘  │  └───────────────┘            │
│  Priority: HIGH     │  Priority: MEDIUM              │
│  Last used: 2m ago  │  Last used: 8m ago             │
│  Ref count: 3       │  Ref count: 1                  │
└─────────────────────┴────────────────────────────────┘
```

### Specialist Pool

| Specialist         | Params | VRAM (4-bit) | Domain                    |
|--------------------|--------|--------------|---------------------------|
| CodeWriter         | 7B     | 1.2 GB       | Code generation, debugging|
| DataAnalyst        | 7B     | 1.2 GB       | Data analysis, CSV, SQL   |
| CreativeWriter     | 7B     | 1.2 GB       | Stories, poetry, content  |
| ResearchAssistant  | 7B     | 1.2 GB       | Web research, summarization|
| MathSolver         | 7B     | 1.2 GB       | Advanced math, proofs     |
| TranslationEngine  | 7B     | 1.2 GB       | Multi-language translation|
| AudioProcessor     | 3B     | 0.6 GB       | Voice, transcription      |
| ImageAnalyzer      | 3B     | 0.6 GB       | Image understanding       |

### Swap Strategy

```python
class HotSwapController:
    def __init__(self, slots: int = 2, slot_size_gb: float = 1.2):
        self.slots = [None] * slots
        self.slot_size = slot_size_gb
        self.access_history = {}  # specialist -> last_access_time
        self.ref_counts = {}      # specialist -> active references

    async def activate(self, specialist_name: str) -> ModelSlot:
        """Load a specialist into a hot-swap slot."""
        # Check if already loaded
        for i, slot in enumerate(self.slots):
            if slot and slot.name == specialist_name:
                self.access_history[specialist_name] = time.time()
                return slot

        # Find free slot or evict LRU
        target_slot = self._find_victim()
        if target_slot.model:
            await self._evict(target_slot)

        # Load new specialist
        model = await self._load_specialist(specialist_name)
        target_slot.model = model
        target_slot.name = specialist_name
        self.access_history[specialist_name] = time.time()
        self.ref_counts[specialist_name] = 1

        return target_slot

    def _find_victim(self) -> Slot:
        """Find slot to evict using LRU + ref_count heuristic."""
        free = [s for s in self.slots if s.model is None]
        if free:
            return free[0]

        # Evict lowest priority (LRU * 1/ref_count)
        def eviction_score(slot):
            last = self.access_history.get(slot.name, 0)
            refs = self.ref_counts.get(slot.name, 1)
            return (time.time() - last) * refs

        return min(self.slots, key=eviction_score)
```

### Swap Timing

| Operation               | Time    | VRAM Impact                |
|-------------------------|---------|----------------------------|
| Load specialist (4-bit) | 1.2-2.0s| +1.2 GB (immediate)        |
| Evict specialist        | 0.1-0.3s| -1.2 GB (immediate)        |
| Weight transfer (GPU)   | 0.8-1.5s| Temporary peak +0.3 GB     |
| Cold start (first use)  | 2.0-5.0s| Full load sequence         |
| Warm reload (from cache)| 0.5-1.0s| Partial load               |

## 4. Warm Storage: BackupCore Pool (1.6 GB)

The BackupCore Pool holds pre-quantized specialist weights in a partially-loaded
state. They're kept in a memory-mapped format that allows fast promotion to
hot-swap slots.

```
Warm Storage Layout (1.6 GB):
┌────────────────────────────────────────────────────┐
│  BackupCore Pool                                   │
│  ┌──────────┬──────────┬──────────┬──────────┐    │
│  │ Math     │ Research │ Translat │ Image    │    │
│  │ Solver   │ Assistant│ Engine   │ Analyzer │    │
│  │ 0.4 GB   │ 0.4 GB   │ 0.4 GB   │ 0.4 GB  │    │
│  │ [mmap]   │ [mmap]   │ [mmap]   │ [mmap]  │    │
│  └──────────┴──────────┴──────────┴──────────┘    │
│  Status: memory-mapped, partially resident          │
│  Promotion time: ~0.5s to hot-swap slot             │
└────────────────────────────────────────────────────┘
```

```python
# backup_core_pool.py
class BackupCorePool:
    def __init__(self, pool_size_gb: float = 1.6):
        self.pool_size = pool_size_gb
        self.backed_up = {}  # name -> mmap_path

    async def backup(self, specialist_name: str, weights: Tensor):
        """Write specialist weights to memory-mapped backup."""
        path = f"./backup/{specialist_name}.mmap"
        mmap_array = np.memmap(path, dtype='float16', mode='w+',
                               shape=weights.shape)
        mmap_array[:] = weights.cpu().numpy()
        self.backed_up[specialist_name] = path
        return path

    async def promote(self, specialist_name: str) -> Tensor:
        """Promote backup to hot-swap slot (fast load from mmap)."""
        path = self.backed_up.get(specialist_name)
        if not path:
            raise ValueError(f"No backup for {specialist_name}")

        # Memory-map read — OS handles paging
        mmap_array = np.memmap(path, dtype='float16', mode='r')
        return torch.from_numpy(mmap_array.copy()).cuda()
```

## 5. Cold Storage: Inactive Specialists in CPU RAM

All inactive specialist models are stored in CPU RAM using 4-bit quantization.
This keeps them available for fast loading without consuming VRAM.

```
Cold Storage Strategy:
┌─────────────────────────────────────────────────────────────┐
│                        CPU RAM (16-32 GB)                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  4-bit Quantized Specialist Weights                  │    │
│  │  ┌──────┬──────┬──────┬──────┬──────┬──────┐       │    │
│  │  │Math  │Resrc │Trans │Image │Creat │Code  │ ...    │    │
│  │  │0.6GB │0.6GB │0.6GB │0.3GB │0.6GB │0.6GB │       │    │
│  │  └──────┴──────┴──────┴──────┴──────┴──────┘       │    │
│  │  Total: ~4-8 GB CPU RAM for all inactive models      │    │
│  └─────────────────────────────────────────────────────┘    │
│  Loading from CPU → GPU: PCIe bandwidth limited             │
│  Typical load time: 2-5 seconds depending on model size     │
└─────────────────────────────────────────────────────────────┘
```

```python
# cold_storage.py
class ColdStorage:
    def __init__(self, cpu_ram_budget_gb: float = 8.0):
        self.budget = cpu_ram_budget_gb
        self.models = {}  # name -> quantized_cpu_weights

    def store(self, name: str, gpu_weights: Tensor):
        """Move model from GPU to CPU (4-bit quantized)."""
        cpu_weights = quantize_4bit(gpu_weights.cpu())
        self.models[name] = cpu_weights
        torch.cuda.empty_cache()  # Reclaim VRAM

    def load(self, name: str) -> Tensor:
        """Load model from CPU to GPU."""
        if name not in self.models:
            raise ValueError(f"No cold storage for {name}")
        gpu_weights = self.models[name].cuda()
        return gpu_weights

    def get_memory_usage(self) -> float:
        """Return CPU RAM used by cold storage in GB."""
        return sum(m.nbytes for m in self.models.values()) / 1e9
```

## 6. Weight Swapping Strategy

### Swap Priority Matrix

```
┌──────────────────────────────────────────────────────────────┐
│  Swap Priority (Higher = Faster Promotion)                    │
│                                                              │
│  Priority 1: FastResponderCore     — NEVER SWAP             │
│  Priority 2: SARA         — NEVER SWAP             │
│  Priority 3: Router                — NEVER SWAP             │
│  Priority 4: Active Specialists    — SWAP ON DEMAND         │
│  Priority 5: BackupCore Pool       — PROMOTE ON REQUEST     │
│  Priority 6: Cold Storage          — LOAD ON DEMAND         │
└──────────────────────────────────────────────────────────────┘
```

### Swap Flow

```
Query arrives
     │
     ▼
┌──────────┐    miss    ┌──────────────┐    miss    ┌──────────────┐
│ FastResp │───────────▶│ Hot-Swap     │───────────▶│ BackupCore   │
│ (always) │            │ Slot A/B     │            │ Pool (warm)  │
└──────────┘            └──────────────┘            └──────┬───────┘
                                                           │ miss
                                                           ▼
                                                   ┌──────────────┐
                                                   │ Cold Storage  │
                                                   │ (CPU RAM)     │
                                                   └──────────────┘
```

### Timing Budget

```
Total VRAM Swap Budget: 500ms max
┌─────────────────────────────────────────────────────────┐
│  Phase 1: Check FastResponder         │    5ms          │
│  Phase 2: Check Hot-Swap Slots        │   10ms          │
│  Phase 3: Promote from BackupCore     │  200ms          │
│  Phase 4: Load from Cold Storage      │  500ms (max)    │
│  Phase 5: Download if not local       │ 2000ms (max)    │
└─────────────────────────────────────────────────────────┘
```

## 7. Gradient Checkpointing for Training

When training or fine-tuning specialists, gradient checkpointing reduces VRAM
usage at the cost of ~30% more compute time.

```python
# training_config.py
from torch.utils.checkpoint import checkpoint_sequential

class TrainingConfig:
    gradient_checkpointing: bool = True
    max_batch_size: int = 2
    max_seq_length: int = 2048
    accumulation_steps: int = 4

    def get_vram_estimate(self) -> dict:
        """Estimate VRAM usage with/without checkpointing."""
        base_model_gb = 4.2
        optimizer_gb = 1.6  # AdamW states
        gradients_gb = 1.2
        activations_gb = 2.4 if not self.gradient_checkpointing else 0.8

        return {
            "without_checkpointing": {
                "model": base_model_gb,
                "optimizer": optimizer_gb,
                "gradients": gradients_gb,
                "activations": activations_gb,
                "total": base_model_gb + optimizer_gb + gradients_gb + 2.4,
                "fits_8gb": False,
            },
            "with_checkpointing": {
                "model": base_model_gb,
                "optimizer": optimizer_gb,
                "gradients": gradients_gb,
                "activations": 0.8,
                "total": base_model_gb + optimizer_gb + gradients_gb + 0.8,
                "fits_8gb": True,
            },
        }

# Usage during training
def train_specialist(model, dataloader, config):
    if config.gradient_checkpointing:
        model.gradient_checkpointing_enable()

    optimizer = AdamW(model.parameters(), lr=2e-5)

    for step, batch in enumerate(dataloader):
        # Forward with checkpointing
        outputs = checkpoint_sequential(
            model.layers,
            segments=4,
            input=batch.input_ids
        )
        loss = outputs.loss / config.accumulation_steps
        loss.backward()

        if (step + 1) % config.accumulation_steps == 0:
            optimizer.step()
            optimizer.zero_grad()
```

### VRAM Savings

| Configuration          | Activations | Total VRAM | Fits RTX 4060? |
|------------------------|-------------|------------|----------------|
| No checkpointing       | 2.4 GB      | 9.4 GB     | No             |
| With checkpointing     | 0.8 GB      | 7.8 GB     | Yes (marginal) |
| Checkpointing + offload| 0.3 GB      | 7.3 GB     | Yes            |

## 8. OOM Prevention Strategy

Out-of-Memory errors are the primary failure mode on 8GB VRAM. The system
implements multiple prevention layers.

### Layer 1: Pre-flight Check

```python
def preflight_check(required_gb: float) -> bool:
    """Check if enough VRAM is available before loading."""
    free, total = torch.cuda.mem_get_info()
    free_gb = free / 1e9
    buffer = 0.3  # 300MB safety buffer

    if free_gb - buffer < required_gb:
        log.warning(f"OOM risk: need {required_gb:.1f}GB, "
                    f"have {free_gb:.1f}GB free")
        return False
    return True
```

### Layer 2: Eviction Cascade

```python
async def emergency_evict(target_gb: float):
    """Evict models until target VRAM is freed."""
    candidates = [
        ("backup_pool", 1.6),
        ("slot_b", 1.2),
        ("slot_a", 1.2),
    ]

    freed = 0.0
    for name, size in candidates:
        if freed >= target_gb:
            break
        await evict_model(name)
        freed += size
        log.warning(f"Emergency eviction: {name} freed {size}GB")

    if freed < target_gb:
        raise OOMError(f"Cannot free enough VRAM: need {target_gb}GB")
```

### Layer 3: Dynamic Precision Downgrade

```python
def downcast_if_needed(model, target_gb: float):
    """Downcast model precision if VRAM is tight."""
    current_gb = get_model_vram(model)

    if current_gb > target_gb:
        # Try FP16 → INT8 → INT4
        for dtype in ["int8", "int4"]:
            model = quantize(model, dtype)
            if get_model_vram(model) <= target_gb:
                log.info(f"Downcast to {dtype}: {get_model_vram(model):.1f}GB")
                return model

        raise OOMError("Cannot fit model in available VRAM")
    return model
```

### Layer 4: Batch Size Throttling

```python
class BatchThrottler:
    def __init__(self, max_vram_gb: float = 7.5):
        self.max_vram = max_vram_gb

    def get_safe_batch_size(self, model, seq_length: int) -> int:
        """Determine max batch size that won't OOM."""
        for batch_size in [8, 4, 2, 1]:
            estimated = self._estimate_vram(model, seq_length, batch_size)
            if estimated < self.max_vram:
                return batch_size
        return 1  # Minimum safe batch
```

### OOM Prevention Summary

```
┌─────────────────────────────────────────────────────────────┐
│                   OOM Prevention Layers                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: Pre-flight Check                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Check free VRAM before any allocation               │    │
│  │  Reject if insufficient + 300MB buffer               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Layer 2: Eviction Cascade                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Evict: BackupPool → SlotB → SlotA                  │    │
│  │  Free VRAM incrementally until target met            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Layer 3: Dynamic Precision                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  FP16 → INT8 → INT4 progressive quantization        │    │
│  │  Reduce model size to fit available VRAM             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Layer 4: Batch Throttling                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Dynamically reduce batch size under memory pressure │    │
│  │  8 → 4 → 2 → 1 adaptive scaling                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 9. VRAM Monitoring & Reallocation

### Continuous Monitoring

```python
# vram_monitor.py
import torch
import psutil
from dataclasses import dataclass
from typing import Optional

@dataclass
class VRAMSnapshot:
    timestamp: float
    total_gb: float
    allocated_gb: float
    reserved_gb: float
    free_gb: float
    components: dict  # component_name -> gb

class VRAMMonitor:
    def __init__(self, poll_interval: float = 1.0):
        self.poll_interval = poll_interval
        self.snapshots = []
        self.alerts = []
        self.budget = {
            "sara": 4.2,
            "router": 0.2,
            "fast_responder": 0.4,
            "slot_a": 1.2,
            "slot_b": 1.2,
            "backup_pool": 1.6,
            "cuda_overhead": 0.3,
        }

    def snapshot(self) -> VRAMSnapshot:
        """Capture current VRAM state."""
        total = torch.cuda.get_device_properties(0).total_mem / 1e9
        allocated = torch.cuda.memory_allocated() / 1e9
        reserved = torch.cuda.memory_reserved() / 1e9

        return VRAMSnapshot(
            timestamp=time.time(),
            total_gb=total,
            allocated_gb=allocated,
            reserved_gb=reserved,
            free_gb=total - allocated,
            components=self._get_component_breakdown(),
        )

    def check_pressure(self) -> Optional[str]:
        """Check if VRAM pressure requires reallocation."""
        snap = self.snapshot()
        usage_ratio = snap.allocated_gb / snap.total_gb

        if usage_ratio > 0.95:
            return "CRITICAL"
        elif usage_ratio > 0.85:
            return "HIGH"
        elif usage_ratio > 0.70:
            return "MEDIUM"
        return "NORMAL"

    async def reallocate(self):
        """Dynamic VRAM reallocation based on pressure."""
        pressure = self.check_pressure()

        if pressure == "CRITICAL":
            await emergency_evict(target_gb=1.5)
        elif pressure == "HIGH":
            # Evict least-used specialist
            victim = self._find_least_used_slot()
            if victim:
                await evict_model(victim)
        elif pressure == "MEDIUM":
            # Downcast backup pool precision
            await downcast_backup_pool()
```

### Reallocation Rules

```
┌──────────────────────────────────────────────────────────────┐
│  VRAM Pressure Response Matrix                                │
├────────────┬─────────────┬──────────────────────────────────┤
│  Pressure  │  Threshold  │  Action                          │
├────────────┼─────────────┼──────────────────────────────────┤
│  NORMAL    │  < 70%      │  No action                       │
│  MEDIUM    │  70-85%     │  Downcast backup pool to INT4    │
│  HIGH      │  85-95%     │  Evict LRU specialist from slot  │
│  CRITICAL  │  > 95%      │  Emergency cascade eviction      │
│  EMERGENCY │  > 98%      │  Kill non-essential processes    │
└────────────┴─────────────┴──────────────────────────────────┘
```

### Monitoring Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│  VRAM Monitor Dashboard                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Total: 8.0 GB  │  Allocated: 7.2 GB  │  Free: 0.8 GB     │
│  Usage: [████████████████████████████████████░░░░] 90%     │
│                                                             │
│  Component Breakdown:                                       │
│  ┌─────────────────┬──────────┬──────────────────────┐     │
│  │ Component       │ VRAM     │ Bar                  │     │
│  ├─────────────────┼──────────┼──────────────────────┤     │
│  │ SARA   │ 4.2 GB   │ [████████████████] 53%│    │
│  │ Router          │ 0.2 GB   │ [██] 3%              │     │
│  │ FastResponder   │ 0.4 GB   │ [████] 5%           │     │
│  │ Slot A (Code)   │ 1.2 GB   │ [██████████] 15%    │     │
│  │ Slot B (Data)   │ 1.2 GB   │ [██████████] 15%    │     │
│  │ CUDA Overhead   │ 0.3 GB   │ [███] 4%            │     │
│  │ Buffer          │ 0.3 GB   │ [███] 4%            │     │
│  └─────────────────┴──────────┴──────────────────────┘     │
│                                                             │
│  Pressure: HIGH  │  Last eviction: 2m ago                   │
│  Next action: Downcast backup pool if pressure persists     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 10. Configuration

### `vram_budget.yaml`

```yaml
vram_budget:
  total_gb: 8.0
  reserve_buffer_gb: 0.3

  always_hot:
    sara:
      size_gb: 4.2
      quantization: "4bit-gptq"
      eviction: "never"
    router:
      size_gb: 0.2
      quantization: "fp16"
      eviction: "never"
    fast_responder:
      size_gb: 0.4
      quantization: "fp16"
      eviction: "never"

  hot_swap:
    slots: 2
    slot_size_gb: 1.2
    swap_timeout_ms: 500
    eviction_policy: "lru_with_refcount"
    preload_top_n: 2

  warm_backup:
    pool_size_gb: 1.6
    format: "mmap_int4"
    promotion_time_ms: 200

  cold_storage:
    cpu_ram_budget_gb: 8.0
    format: "4bit_quantized"
    load_time_ms: 2000

  oom_prevention:
    enabled: true
    preflight_check: true
    eviction_cascade: true
    dynamic_precision: true
    batch_throttling: true
    safety_buffer_gb: 0.3

  monitoring:
    poll_interval_seconds: 1.0
    alert_thresholds:
      medium: 0.70
      high: 0.85
      critical: 0.95
    log_snapshots: true
    dashboard_port: 9090
```

### `deployment.yaml`

```yaml
deployment:
  device: "cuda:0"
  device_name: "NVIDIA GeForce RTX 4060"
  total_vram_gb: 8.0
  driver_version: "535.0"

  memory_strategy: "aggressive"
  # aggressive: maximize utilization, accept swap latency
  # conservative: keep 1GB free, fewer specialists loaded
  # balanced: default, 300MB buffer

  quantization:
    always_hot: "fp16"
    hot_swap: "4bit-gptq"
    warm_backup: "4bit-int4"
    cold_storage: "4bit-int4"

  prefetch:
    enabled: true
    lookahead_queries: 3
    preload_probability: 0.7
```

## 11. File Structure

```
vram_budget/
├── __init__.py
├── vram_monitor.py          # Continuous VRAM monitoring
├── swap_controller.py       # Hot-swap slot management
├── eviction_manager.py      # Eviction cascade logic
├── cold_storage.py          # CPU RAM cold storage
├── backup_pool.py           # Warm backup core pool
├── oom_guard.py             # OOM prevention layers
├── quantizer.py             # Dynamic precision management
├── batch_throttler.py       # Adaptive batch sizing
├── training_config.py       # Gradient checkpointing config
├── dashboard.py             # VRAM monitoring dashboard
├── config/
│   ├── vram_budget.yaml
│   └── deployment.yaml
├── tests/
│   ├── test_eviction.py
│   ├── test_oom_guard.py
│   ├── test_swap_timing.py
│   ├── test_monitoring.py
│   └── test_stress.py
└── scripts/
    ├── benchmark_vram.py
    ├── profile_swaps.py
    └── oom_stress_test.py
```

## 12. Integration Points

```
┌─────────────────────────────────────────────────────────────────────┐
│                     VRAM Budget System                               │
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │  VRAM Monitor │───▶│  OOM Guard   │───▶│  Eviction Manager    │   │
│  │  (polls 1/s)  │    │  (pre-check) │    │  (cascade eviction)  │   │
│  └──────┬───────┘    └──────────────┘    └──────────┬───────────┘   │
│         │                                            │               │
│         ▼                                            ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐   │
│  │  Dashboard    │    │  Swap Ctrl   │◀───│  Backup Pool         │   │
│  │  (port 9090)  │    │  (hot-swap)  │    │  (warm mmap backup)  │   │
│  └──────────────┘    └──────┬───────┘    └──────────────────────┘   │
│                             │                                        │
│         ┌───────────────────┼───────────────────┐                   │
│         ▼                   ▼                   ▼                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐      │
│  │ FastResponder│  │ SARA│  │ Specialist Pipeline   │      │
│  │ (0.4GB)      │  │ (4.2GB)      │  │ (slots A/B)           │      │
│  └──────────────┘  └──────────────┘  └──────────────────────┘      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Integration Interfaces:**

| Component           | Provides                    | Consumes                    |
|---------------------|-----------------------------|-----------------------------|
| VRAM Monitor        | `snapshot()`, `pressure()`  | CUDA memory APIs            |
| OOM Guard           | `preflight_check()`         | VRAM Monitor                |
| Eviction Manager    | `evict()`, `cascade()`      | OOM Guard, Swap Controller  |
| Swap Controller     | `activate()`, `deactivate()`| Eviction Manager            |
| Backup Pool         | `backup()`, `promote()`     | Swap Controller             |
| Cold Storage        | `store()`, `load()`         | Backup Pool                 |
| Dashboard           | Real-time VRAM stats        | VRAM Monitor                |
| Training Config     | `get_vram_estimate()`       | VRAM Monitor                |

## 13. Events

```python
# Events emitted by VRAM Budget system
events = {
    # Monitoring
    "vram.snapshot.taken":           # Periodic VRAM snapshot
    "vram.pressure.changed":         # Pressure level changed
    "vram.usage.threshold":          # Usage crossed threshold

    # Eviction
    "vram.eviction.started":         # Eviction cascade begun
    "vram.eviction.completed":       # Model evicted successfully
    "vram.eviction.failed":          # Eviction error

    # Swap
    "vram.swap.initiated":           # Hot-swap started
    "vram.swap.completed":           # Hot-swap finished
    "vram.swap.timeout":             # Swap exceeded timeout
    "vram.swap.promoted":            # Model promoted from warm/cold

    # OOM
    "vram.oom.risk.detected":        # Pre-flight check failed
    "vram.oom.emergency_evict":      # Emergency eviction triggered
    "vram.oom.narrowly_avoided":     # Eviction freed just enough

    # Training
    "vram.training.checkpointing":   # Gradient checkpointing enabled
    "vram.training.batch_throttled": # Batch size reduced
    "vram.training.precision_drop":  # Dynamic precision downgrade

    # System
    "vram.system.startup":           # VRAM system initialized
    "vram.system.shutdown":          # VRAM system cleaning up
}

# Example: OOM prevention event
{
    "event": "vram.oom.risk.detected",
    "timestamp": "2026-08-10T14:32:01Z",
    "current_usage_gb": 7.8,
    "requested_gb": 1.2,
    "free_gb": 0.2,
    "action": "eviction_cascade",
    "victims": ["backup_pool_math_solver"],
    "freed_gb": 0.4,
    "result": "success",
}
```

## 14. Metrics

| Metric                       | Type      | Description                           |
|------------------------------|-----------|---------------------------------------|
| `vram_total_gb`              | Gauge     | Total VRAM on device                  |
| `vram_allocated_gb`          | Gauge     | Currently allocated VRAM              |
| `vram_free_gb`               | Gauge     | Free VRAM                             |
| `vram_usage_ratio`           | Gauge     | allocated / total                     |
| `vram_pressure_level`        | Enum      | NORMAL/MEDIUM/HIGH/CRITICAL           |
| `vram_evictions_total`       | Counter   | Total evictions performed             |
| `vram_evictions_bytes`       | Counter   | Total bytes freed by eviction         |
| `vram_swaps_total`           | Counter   | Total hot-swap operations             |
| `vram_swap_duration_ms`      | Histogram | Swap operation duration               |
| `vram_oom_prevented`         | Counter   | OOM events prevented                  |
| `vram_oom_occurred`          | Counter   | OOM events that occurred (should be 0)|
| `vram_batch_throttle_events` | Counter   | Times batch size was reduced          |
| `vram_precision_downgrades`  | Counter   | Times precision was downgraded        |
| `vram_cold_load_time_ms`     | Histogram | Cold storage load time                |
| `vram_warm_promote_time_ms`  | Histogram | Warm backup promotion time            |

```python
# Prometheus metrics export
from prometheus_client import Gauge, Counter, Histogram

VRAM_TOTAL = Gauge("vram_total_gb", "Total VRAM")
VRAM_ALLOCATED = Gauge("vram_allocated_gb", "Allocated VRAM")
VRAM_FREE = Gauge("vram_free_gb", "Free VRAM")
VRAM_PRESSURE = Gauge("vram_pressure_level", "Pressure level", ["level"])
VRAM_EVICTIONS = Counter("vram_evictions_total", "Total evictions")
VRAM_SWAP_DURATION = Histogram("vram_swap_duration_ms", "Swap duration",
                                buckets=[50, 100, 200, 500, 1000, 2000])
VRAM_OOM_PREVENTED = Counter("vram_oom_prevented", "OOM prevented")
```
