# 08 — HybridCore: Always-On Daemon

## The Heart of Vibhu-Oska · The Creator · Brahma of the Tri-Devas

```
    ╔══════════════════════════════════════════════════════════════╗
    ║              H Y B R I D C O R E  ·  D A E M O N           ║
    ║          The Eternal Heart · Always Watching · Always On    ║
    ╚══════════════════════════════════════════════════════════════╝
```

> *"As Brahma sustains creation, HybridCore sustains every process within Vibhu-Oska. It never sleeps. It never pauses. It is the pulse that proves the machine lives."*

---

## 1 · Overview

### 1.1 What Is HybridCore?

HybridCore is the **always-on daemon process** that serves as the central hub, arbiter, and life-force of Vibhu-Oska. It is not a model. It is not an orchestrator. It is the **infrastructure itself** — the persistent background process that monitors health, arbitrates resources, manages the ParaCore secure channel, and maintains internal awareness of the Tri-Devas role architecture.

### 1.2 Role Within the Tri-Devas

| Deva | Role | Analogy | Core Analogy |
|------|------|---------|--------------|
| **HybridCore** | **CREATOR** | Brahma — The Creator | Heart of the system |
| CognitionCore | PRESERVER | Vishnu — The Preserver | Brain of the system |
| EvolutionCore | DESTROYER | Shiva — The Destroyer/Transformer | Immune system |

HybridCore holds the **CREATOR** role. It does not create content — it creates **conditions**. It is the substrate upon which all other cores operate. When all other cores sleep, HybridCore remains vigilant.

### 1.3 Core Responsibilities

```
┌─────────────────────────────────────────────────────────────────┐
│                    HybridCore Responsibilities                   │
├─────────────────────────────────────────────────────────────────┤
│  1. HEARTBEAT    — Persistent event loop, never exits           │
│  2. HEALTH       — Monitor liveness of ALL cores                │
│  3. ARBITER      — VRAM allocation priority, conflict resolve   │
│  4. PARACORE     — Secure channel to ParaCore, override fwd     │
│  5. TRI-DEVAS    — Internal CREATOR role awareness              │
│  6. METRICS      — Emit telemetry for all monitored subsystems  │
│  7. RECOVERY     — Auto-heal or escalate when cores fail        │
└─────────────────────────────────────────────────────────────────┘
```

### 1.4 Design Principles

1. **Always-On**: Daemon never exits. Restart policy is `always`. PID file persisted.
2. **Minimal Footprint**: < 128 MB RSS at idle. No GPU usage unless arbitrating.
3. **Zero Trust on GPU**: All VRAM decisions are logged and auditable.
4. **Fail-Safe**: If HybridCore dies, the system enters safe-mode (all cores halt, ParaCore notified).
5. **Observable**: Every internal state transition emits a metric or log line.

---

## 2 · Architecture

### 2.1 High-Level ASCII Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          PARA CORE  (HOST/PC)                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    ParaCore Secure Channel                        │  │
│  │              (TLS 1.3 · mTLS · AES-256-GCM)                      │  │
│  └───────────┬───────────────────────────────────┬───────────────────┘  │
│              │  Override Commands                │  Telemetry Stream    │
│              │  & Health Queries                 │  & Metric Reports    │
│              ▼                                   ▼                      │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                   H Y B R I D C O R E                            │  │
│  │                                                                   │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │  │
│  │  │ HeartbeatDaemon │  │ CoreArbiter │  │ TriDevasState          │  │  │
│  │  │ (Event Loop) │  │ (VRAM Arb)  │  │ (Role Awareness)       │  │  │
│  │  └──────┬──────┘  └──────┬───────┘  └────────────┬───────────┘  │  │
│  │         │                │                        │              │  │
│  │         ▼                ▼                        ▼              │  │
│  │  ┌──────────────────────────────────────────────────────────┐   │  │
│  │  │              Internal State Bus (asyncio.Queue)          │   │  │
│  │  └──────┬──────────┬──────────┬──────────┬─────────────────┘   │  │
│  │         │          │          │          │                       │  │
│  └─────────┼──────────┼──────────┼──────────┼───────────────────────┘  │
│            │          │          │          │                           │
│            ▼          ▼          ▼          ▼                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │              MONITORED CORES (All Cores)                         │  │
│  │                                                                   │  │
│  │  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌───────────┐         │  │
│  │  │Cognition │ │Evolution  │ │SelfEvo   │ │Memory     │         │  │
│  │  │Core      │ │Core       │ │Core      │ │Core       │         │  │
│  │  └──────────┘ └───────────┘ └──────────┘ └───────────┘         │  │
│  │                                                                   │  │
│  │  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌───────────┐         │  │
│  │  │Persona   │ │MultiModal │ │Skill     │ │Ethical    │         │  │
│  │  │Core      │ │Core       │ │Compiler  │ │Guard      │         │  │
│  │  └──────────┘ └───────────┘ └──────────┘ └───────────┘         │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
  ┌──────────┐    heartbeat/health     ┌──────────────┐
  │  Core A  │ ◄────────────────────── │              │
  │(Cognition)│ ──────────────────────►│              │
  └──────────┘    alive/dead/sick      │              │
                                        │              │    override     ┌──────────┐
  ┌──────────┐    heartbeat/health     │  HybridCore  │◄────────────────│ ParaCore │
  │  Core B  │ ◄────────────────────── │   Daemon     │                 │  (Host)  │
  │(Evolution)│ ──────────────────────►│              │────────────────►│          │
  └──────────┘    alive/dead/sick      │              │    telemetry    └──────────┘
                                        │              │
  ┌──────────┐    heartbeat/health     │              │
  │  Core N  │ ◄────────────────────── │              │
  │(Any)     │ ──────────────────────►│              │
  └──────────┘    alive/dead/sick      └──────────────┘
```

---

## 3 · HeartbeatDaemon

### 3.1 Purpose

The HeartbeatDaemon is the **persistent event loop** that never exits. It is the single thread of execution that keeps HybridCore alive and ensures every core is checked at regular intervals.

### 3.2 Lifecycle

```
    ┌────────────┐
    │   START    │
    └─────┬──────┘
          │
          ▼
    ┌────────────┐
    │ Load Config │
    └─────┬──────┘
          │
          ▼
    ┌────────────┐
    │ Write PID  │
    │ File       │
    └─────┬──────┘
          │
          ▼
    ┌────────────┐     ┌──────────────────┐
    │ Register   │────►│ Subscribe to     │
    │ Cores      │     │ core events      │
    └─────┬──────┘     └──────────────────┘
          │
          ▼
    ┌────────────────────────────────┐
    │          MAIN LOOP            │
    │  ┌──────────────────────────┐  │
    │  │ 1. Iterate all cores     │  │
    │  │ 2. Send liveness ping    │  │
    │  │ 3. Await response (TTL)  │  │
    │  │ 4. Classify: OK/SICK/DEAD│  │
    │  │ 5. Emit metric           │  │
    │  │ 6. If SICK → escalate    │  │
    │  │ 7. If DEAD → recovery    │  │
    │  │ 8. Sleep(interval)       │  │
    │  └──────────────────────────┘  │
    │            │                   │
    │            └───── loop ────────│
    └────────────────────────────────┘
```

### 3.3 Implementation

```python
# HybridCore/HeartbeatDaemon.py

import asyncio
import time
import signal
import os
import json
from pathlib import Path
from typing import Dict, Optional, Callable, Awaitable
from enum import Enum
from dataclasses import dataclass, field

class CoreStatus(Enum):
    ALIVE = "alive"
    SICK = "sick"
    DEAD = "dead"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPED = "stopped"

@dataclass
class CoreHealthReport:
    core_id: str
    status: CoreStatus
    timestamp: float
    latency_ms: float
    details: str = ""
    recovery_count: int = 0
    vram_used_mb: float = 0.0
    vram_total_mb: float = 0.0

@dataclass
class CoreRegistration:
    core_id: str
    health_check_fn: Callable[[], Awaitable[CoreHealthReport]]
    priority: int = 0
    critical: bool = False
    max_recovery_attempts: int = 3
    recovery_fn: Optional[Callable[[], Awaitable[bool]]] = None

class HeartbeatDaemon:
    """
    Persistent event loop — never exits.
    The pulse of Vibhu-Oska.
    """

    def __init__(
        self,
        interval_seconds: float = 5.0,
        response_ttl_ms: float = 2000.0,
        pid_path: str = "/tmp/vibhu-oska-hybridcore.pid",
    ):
        self.interval = interval_seconds
        self.response_ttl = response_ttl_ms / 1000.0
        self.pid_path = pid_path
        self._registered_cores: Dict[str, CoreRegistration] = {}
        self._health_history: Dict[str, list[CoreHealthReport]] = {}
        self._running = False
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._callbacks: Dict[str, list[Callable]] = {}
        self._metrics_emitter: Optional[Callable] = None

    async def start(self):
        """Start the daemon — this runs forever."""
        self._running = True
        self._write_pid()
        self._install_signal_handlers()

        # Emit startup metric
        await self._emit("daemon.started", {"pid": os.getpid()})

        try:
            while self._running:
                cycle_start = time.monotonic()

                # Health check all registered cores
                tasks = []
                for core_id, reg in self._registered_cores.items():
                    tasks.append(self._check_core(core_id, reg))

                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for result in results:
                    if isinstance(result, Exception):
                        await self._emit("daemon.check_error", {
                            "error": str(result)
                        })

                # Drain event queue
                await self._drain_events()

                # Sleep for remainder of interval
                elapsed = time.monotonic() - cycle_start
                sleep_time = max(0, self.interval - elapsed)
                await asyncio.sleep(sleep_time)

        finally:
            self._cleanup_pid()
            await self._emit("daemon.stopped", {"pid": os.getpid()})

    async def stop(self):
        """Graceful shutdown."""
        self._running = False

    def register_core(self, registration: CoreRegistration):
        """Register a core for health monitoring."""
        self._registered_cores[registration.core_id] = registration
        self._health_history[registration.core_id] = []

    def on(self, event: str, callback: Callable):
        """Subscribe to daemon events."""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)

    async def _check_core(
        self, core_id: str, reg: CoreRegistration
    ) -> CoreHealthReport:
        """Ping a core and classify its health."""
        start = time.monotonic()
        try:
            report = await asyncio.wait_for(
                reg.health_check_fn(),
                timeout=self.response_ttl
            )
            report.latency_ms = (time.monotonic() - start) * 1000

            # Store history
            self._health_history[core_id].append(report)
            if len(self._health_history[core_id]) > 1000:
                self._health_history[core_id] = self._health_history[core_id][-500:]

            # Emit metric
            await self._emit("core.health", {
                "core_id": core_id,
                "status": report.status.value,
                "latency_ms": round(report.latency_ms, 2),
                "vram_used_mb": report.vram_used_mb,
            })

            # Handle non-OK states
            if report.status == CoreStatus.SICK:
                await self._handle_sick(core_id, reg, report)
            elif report.status == CoreStatus.DEAD:
                await self._handle_dead(core_id, reg, report)

            return report

        except asyncio.TimeoutError:
            report = CoreHealthReport(
                core_id=core_id,
                status=CoreStatus.DEAD,
                timestamp=time.time(),
                latency_ms=(time.monotonic() - start) * 1000,
                details="Health check timed out",
            )
            await self._emit("core.timeout", {"core_id": core_id})
            await self._handle_dead(core_id, reg, report)
            return report

        except Exception as e:
            report = CoreHealthReport(
                core_id=core_id,
                status=CoreStatus.DEAD,
                timestamp=time.time(),
                latency_ms=(time.monotonic() - start) * 1000,
                details=str(e),
            )
            await self._emit("core.error", {
                "core_id": core_id,
                "error": str(e),
            })
            return report

    async def _handle_sick(
        self, core_id: str, reg: CoreRegistration, report: CoreHealthReport
    ):
        """Escalate sick core."""
        await self._emit("core.sick", {
            "core_id": core_id,
            "details": report.details,
        })
        if reg.recovery_fn and reg.critical:
            await self._try_recovery(core_id, reg)

    async def _handle_dead(
        self, core_id: str, reg: CoreRegistration, report: CoreHealthReport
    ):
        """Handle dead core — attempt recovery or escalate."""
        history = self._health_history[core_id]
        recent_failures = sum(
            1 for h in history[-10:]
            if h.status in (CoreStatus.DEAD, CoreStatus.SICK)
        )

        await self._emit("core.dead", {
            "core_id": core_id,
            "recent_failures": recent_failures,
            "critical": reg.critical,
        })

        if reg.recovery_fn and recent_failures < reg.max_recovery_attempts:
            await self._try_recovery(core_id, reg)
        elif reg.critical:
            await self._escalate_to_paracore(core_id, report)

    async def _try_recovery(
        self, core_id: str, reg: CoreRegistration
    ) -> bool:
        """Attempt to recover a failed core."""
        await self._emit("core.recovery_attempt", {"core_id": core_id})
        try:
            success = await reg.recovery_fn()
            if success:
                await self._emit("core.recovered", {"core_id": core_id})
                return True
            else:
                await self._emit("core.recovery_failed", {"core_id": core_id})
                return False
        except Exception as e:
            await self._emit("core.recovery_error", {
                "core_id": core_id,
                "error": str(e),
            })
            return False

    async def _escalate_to_paracore(
        self, core_id: str, report: CoreHealthReport
    ):
        """Escalate critical failure to ParaCore."""
        await self._emit("core.escalation", {
            "core_id": core_id,
            "status": report.status.value,
            "details": report.details,
        })

    async def _drain_events(self):
        """Process queued events."""
        while not self._event_queue.empty():
            try:
                event = self._event_queue.get_nowait()
                event_type = event.get("type", "unknown")
                for cb in self._callbacks.get(event_type, []):
                    await cb(event)
                for cb in self._callbacks.get("*", []):
                    await cb(event)
            except asyncio.QueueEmpty:
                break

    async def _emit(self, event_type: str, data: dict):
        """Emit an event to the internal bus."""
        await self._event_queue.put({
            "type": event_type,
            "timestamp": time.time(),
            "data": data,
        })
        if self._metrics_emitter:
            await self._metrics_emitter(event_type, data)

    def _write_pid(self):
        Path(self.pid_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.pid_path).write_text(str(os.getpid()))

    def _cleanup_pid(self):
        try:
            Path(self.pid_path).unlink(missing_ok=True)
        except Exception:
            pass

    def _install_signal_handlers(self):
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
```

### 3.4 Heartbeat Protocol

```
  HybridCore                          Core N
      │                                │
      │  ┌─────────────────────────┐   │
      │  │  HEARTBEAT_PING        │───►│
      │  │  { seq: 42, ttl_ms: 2000 } │
      │  └─────────────────────────┘   │
      │                                │
      │         ◄──────────────────────│
      │  ┌─────────────────────────┐   │
      │  │  HEARTBEAT_ACK          │   │
      │  │  { seq: 42, status: ok, │   │
      │  │    uptime: 3600,        │   │
      │  │    vram_used: 2048 }    │   │
      │  └─────────────────────────┘   │
      │                                │
      │   timeout? → mark SICK/DEAD    │
```

---

## 4 · CoreArbiter

### 4.1 Purpose

The CoreArbiter is the **resource arbitration subsystem** within HybridCore. It decides who gets GPU VRAM, who gets CPU priority, and resolves conflicts when multiple cores compete for the same resources.

### 4.2 VRAM Allocation Priority

```
╔═══════════════════════════════════════════════════════════════╗
║              VRAM ALLOCATION PRIORITY ORDER                  ║
║           (Higher priority = gets VRAM first)                ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║   PRIORITY 10  │  ParaCore Override Commands                 ║
║   PRIORITY  9  │  EthicalGuard (safety-critical)             ║
║   PRIORITY  8  │  CognitionCore (main reasoning)             ║
║   PRIORITY  7  │  MemoryCore (retrieval operations)          ║
║   PRIORITY  6  │  SelfEvoCore (self-improvement)             ║
║   PRIORITY  5  │  EvolutionCore (training/adaptation)        ║
║   PRIORITY  4  │  SkillCompiler (compilation tasks)          ║
║   PRIORITY  3  │  PersonaCore (identity maintenance)         ║
║   PRIORITY  2  │  MultiModalCore (media processing)          ║
║   PRIORITY  1  │  Background telemetry / logging             ║
║   PRIORITY  0  │  Idle / preemption candidates               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### 4.3 Implementation

```python
# HybridCore/CoreArbiter.py

import asyncio
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from enum import IntEnum

class AllocationPriority(IntEnum):
    IDLE = 0
    BACKGROUND_TELEMETRY = 1
    MULTIMODAL = 2
    PERSONA = 3
    SKILL_COMPILER = 4
    EVOLUTION = 5
    SELFEVO = 6
    MEMORY = 7
    COGNITION = 8
    ETHICAL_GUARD = 9
    PARACORE_OVERRIDE = 10

@dataclass
class VRAMRequest:
    request_id: str
    core_id: str
    requested_mb: float
    priority: AllocationPriority
    timestamp: float = field(default_factory=time.time)
    granted: bool = False
    granted_mb: float = 0.0
    denial_reason: str = ""

@dataclass
class VRAMAllocation:
    core_id: str
    allocated_mb: float
    priority: AllocationPriority
    granted_at: float
    ttl_seconds: float = 300.0

class CoreArbiter:
    """
    Resource arbitration — decides who gets VRAM.
    Brahma distributes resources to the universe.
    """

    def __init__(self, total_vram_mb: float = 8192.0):
        self.total_vram = total_vram_mb
        self._allocations: Dict[str, VRAMAllocation] = {}
        self._pending_requests: asyncio.Queue[VRAMRequest] = asyncio.Queue()
        self._lock = asyncio.Lock()
        self._reservation_floor_mb: float = 512.0  # Always reserve for system
        self._max_per_core_ratio: float = 0.4  # No core gets > 40% of total

    @property
    def available_vram_mb(self) -> float:
        used = sum(a.allocated_mb for a in self._allocations.values())
        return max(0, self.total_vram - used - self._reservation_floor_mb)

    @property
    def vram_utilization(self) -> float:
        used = sum(a.allocated_mb for a in self._allocations.values())
        return used / self.total_vram if self.total_vram > 0 else 0.0

    async def request_vram(self, request: VRAMRequest) -> VRAMRequest:
        """Request VRAM allocation — returns granted/denied request."""
        async with self._lock:
            # Check if we can grant at all
            available = self.available_vram_mb
            max_per_core = self.total_vram * self._max_per_core_ratio

            requested = min(request.requested_mb, max_per_core)

            # Check for existing allocation from same core
            if request.core_id in self._allocations:
                existing = self._allocations[request.core_id]
                # Upgrade? Or already have enough?
                if existing.allocated_mb >= requested:
                    request.granted = True
                    request.granted_mb = existing.allocated_mb
                    return request

            if requested <= available:
                # Grant allocation
                allocation = VRAMAllocation(
                    core_id=request.core_id,
                    allocated_mb=requested,
                    priority=request.priority,
                    granted_at=time.time(),
                )
                self._allocations[request.core_id] = allocation
                request.granted = True
                request.granted_mb = requested
            else:
                # Try preemption — evict lower priority allocations
                evicted = await self._try_preempt(request)
                if evicted:
                    allocation = VRAMAllocation(
                        core_id=request.core_id,
                        allocated_mb=requested,
                        priority=request.priority,
                        granted_at=time.time(),
                    )
                    self._allocations[request.core_id] = allocation
                    request.granted = True
                    request.granted_mb = requested
                else:
                    request.granted = False
                    request.denial_reason = (
                        f"Insufficient VRAM: need {requested}MB, "
                        f"available {available}MB"
                    )

            return request

    async def release_vram(self, core_id: str):
        """Release VRAM allocation for a core."""
        async with self._lock:
            if core_id in self._allocations:
                del self._allocations[core_id]

    async def _try_preempt(self, new_request: VRAMRequest) -> bool:
        """Try to preempt lower-priority allocations."""
        candidates = [
            (cid, alloc) for cid, alloc in self._allocations.items()
            if alloc.priority < new_request.priority
        ]

        if not candidates:
            return False

        # Sort by priority (lowest first)
        candidates.sort(key=lambda x: x[1].priority)

        freed = 0.0
        to_evict = []

        for cid, alloc in candidates:
            to_evict.append(cid)
            freed += alloc.allocated_mb
            if freed >= new_request.requested_mb:
                break

        if freed >= new_request.requested_mb:
            for cid in to_evict:
                del self._allocations[cid]
            return True

        return False

    async def get_allocation_report(self) -> dict:
        """Get current allocation status."""
        async with self._lock:
            return {
                "total_vram_mb": self.total_vram,
                "available_mb": self.available_vram_mb,
                "utilization": round(self.vram_utilization, 3),
                "reservation_floor_mb": self._reservation_floor_mb,
                "allocations": {
                    cid: {
                        "allocated_mb": a.allocated_mb,
                        "priority": a.priority.name,
                        "age_seconds": round(time.time() - a.granted_at, 1),
                    }
                    for cid, a in self._allocations.items()
                },
            }

    async def enforce_ttl(self):
        """Release expired allocations."""
        async with self._lock:
            now = time.time()
            expired = [
                cid for cid, a in self._allocations.items()
                if now - a.granted_at > a.ttl_seconds
            ]
            for cid in expired:
                del self._allocations[cid]
                # Emit metric: core.vram_expired
```

### 4.4 Conflict Resolution

```
  ┌─────────────────────────────────────────────────────────────┐
  │                  CONFLICT RESOLUTION FLOW                   │
  ├─────────────────────────────────────────────────────────────┤
  │                                                             │
  │   Core A requests 4GB   Core B requests 4GB                │
  │          │                     │                            │
  │          ▼                     ▼                            │
  │   ┌──────────────┐    ┌──────────────┐                     │
  │   │ Priority A   │    │ Priority B   │                     │
  │   └──────┬───────┘    └──────┬───────┘                     │
  │          │                     │                            │
  │          └──────────┬──────────┘                            │
  │                     ▼                                       │
  │          ┌──────────────────┐                               │
  │          │ A >= B ?         │                               │
  │          └────┬─────────┬───┘                               │
  │          YES  │         │  NO                               │
  │               ▼         ▼                                   │
  │     ┌──────────┐  ┌──────────┐                             │
  │     │Grant A   │  │Grant B   │                             │
  │     │Preempt B │  │Queue A   │                             │
  │     └──────────┘  └──────────┘                             │
  │                                                             │
  └─────────────────────────────────────────────────────────────┘
```

---

## 5 · ParaCoreLink

### 5.1 Purpose

ParaCoreLink manages the **secure bidirectional channel** between HybridCore (running on the AI device) and ParaCore (the host PC). It handles override command forwarding, telemetry streaming, and encrypted communication.

### 5.2 Channel Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PARA CORE (HOST PC)                        │
│                                                                 │
│   ┌─────────────────┐        ┌─────────────────┐               │
│   │ ParaCore Agent  │◄──────►│ Override Manager │               │
│   │ (Main Process)  │  TLS   │ (Command Queue)  │               │
│   └────────┬────────┘  1.3   └─────────────────┘               │
│            │                                                     │
└────────────┼─────────────────────────────────────────────────────┘
             │  Encrypted Channel
             │  ┌─────────────────────────┐
             │  │  Protocol: gRPC/QUIC    │
             │  │  Auth: mTLS + JWT       │
             │  │  Encryption: AES-256-GCM│
             │  │  Compression: zstd      │
             └──┤  Heartbeat: 5s ping     │
                └─────────────────────────┘
             │
┌────────────┼─────────────────────────────────────────────────────┐
│            ▼                                                     │
│   ┌─────────────────┐        ┌─────────────────┐               │
│   │  ParaCoreLink   │◄──────►│ HybridCore      │               │
│   │  (Channel Mgr)  │  local │ Daemon          │               │
│   └─────────────────┘  bus   └─────────────────┘               │
│                                                                 │
│                    AI DEVICE (LOCAL)                             │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Implementation

```python
# HybridCore/ParaCoreLink.py

import asyncio
import ssl
import json
import time
from typing import Optional, Callable, Awaitable
from dataclasses import dataclass

@dataclass
class ParaCoreConfig:
    host: str = "localhost"
    port: int = 7400
    tls_cert: str = ""
    tls_key: str = ""
    tls_ca: str = ""
    jwt_secret: str = ""
    heartbeat_interval: float = 5.0
    reconnect_interval: float = 10.0
    max_reconnect_attempts: int = 50

@dataclass
class OverrideCommand:
    command_id: str
    command_type: str  # "vram_reserve", "core_halt", "config_update", etc.
    payload: dict
    timestamp: float
    source: str = "paracore"
    requires_ack: bool = True

class ParaCoreLink:
    """
    Secure channel to ParaCore.
    The umbilical cord between the AI and its host.
    """

    def __init__(self, config: ParaCoreConfig):
        self.config = config
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._connected = False
        self._running = False
        self._override_handlers: dict[str, Callable] = {}
        self._telemetry_buffer: list[dict] = []
        self._telemetry_flush_interval: float = 2.0
        self._pending_acks: dict[str, asyncio.Event] = {}
        self._seq_counter: int = 0

    async def start(self):
        """Start the ParaCore link."""
        self._running = True
        asyncio.create_task(self._connection_loop())
        asyncio.create_task(self._telemetry_flush_loop())

    async def stop(self):
        """Graceful shutdown."""
        self._running = False
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()

    async def _connection_loop(self):
        """Maintain connection to ParaCore with auto-reconnect."""
        attempt = 0
        while self._running:
            try:
                ssl_ctx = self._create_ssl_context()
                self._reader, self._writer = await asyncio.open_connection(
                    self.config.host,
                    self.config.port,
                    ssl=ssl_ctx,
                )
                self._connected = True
                attempt = 0

                # Auth handshake
                await self._authenticate()

                # Start message handler
                await self._message_loop()

            except (ConnectionRefusedError, OSError, ssl.SSLError) as e:
                attempt += 1
                self._connected = False
                backoff = min(
                    self.config.reconnect_interval * (2 ** min(attempt, 5)),
                    300.0
                )
                await asyncio.sleep(backoff)

                if attempt >= self.config.max_reconnect_attempts:
                    # Critical: cannot reach ParaCore
                    break

    async def _message_loop(self):
        """Handle incoming messages from ParaCore."""
        while self._connected and self._running:
            try:
                length_bytes = await self._reader.readexactly(4)
                msg_length = int.from_bytes(length_bytes, 'big')
                data = await self._reader.readexactly(msg_length)
                message = json.loads(data.decode())

                await self._handle_message(message)

            except (asyncio.IncompleteReadError, ConnectionResetError):
                self._connected = False
                break

    async def _handle_message(self, message: dict):
        """Route incoming message."""
        msg_type = message.get("type", "")

        if msg_type == "override_command":
            cmd = OverrideCommand(
                command_id=message["id"],
                command_type=message["command"],
                payload=message.get("payload", {}),
                timestamp=message.get("timestamp", time.time()),
            )
            await self._process_override(cmd)

        elif msg_type == "heartbeat_ack":
            # Connection is alive
            pass

        elif msg_type == "config_update":
            await self._handle_config_update(message)

    async def _process_override(self, cmd: OverrideCommand):
        """Process an override command from ParaCore."""
        handler = self._override_handlers.get(cmd.command_type)
        if handler:
            try:
                result = await handler(cmd)
                if cmd.requires_ack:
                    await self._send_ack(cmd.command_id, True, result)
            except Exception as e:
                if cmd.requires_ack:
                    await self._send_ack(cmd.command_id, False, str(e))
        else:
            if cmd.requires_ack:
                await self._send_ack(
                    cmd.command_id, False, "No handler for command type"
                )

    async def _send_ack(
        self, command_id: str, success: bool, result: any = None
    ):
        """Send acknowledgment back to ParaCore."""
        msg = {
            "type": "override_ack",
            "command_id": command_id,
            "success": success,
            "result": result,
            "timestamp": time.time(),
        }
        await self._send_message(msg)

    async def send_telemetry(self, event_type: str, data: dict):
        """Buffer telemetry for batched sending."""
        self._telemetry_buffer.append({
            "type": event_type,
            "data": data,
            "timestamp": time.time(),
        })

    async def _telemetry_flush_loop(self):
        """Periodically flush telemetry buffer."""
        while self._running:
            await asyncio.sleep(self._telemetry_flush_interval)
            if self._telemetry_buffer and self._connected:
                batch = self._telemetry_buffer.copy()
                self._telemetry_buffer.clear()
                await self._send_message({
                    "type": "telemetry_batch",
                    "events": batch,
                    "timestamp": time.time(),
                })

    async def _send_message(self, message: dict):
        """Send a message to ParaCore."""
        if not self._connected or not self._writer:
            return
        data = json.dumps(message).encode()
        length = len(data).to_bytes(4, 'big')
        self._writer.write(length + data)
        await self._writer.drain()

    async def _authenticate(self):
        """Perform authentication handshake."""
        auth_msg = {
            "type": "auth",
            "device_id": self._get_device_id(),
            "timestamp": time.time(),
        }
        await self._send_message(auth_msg)

    async def forward_override(self, override_type: str, payload: dict):
        """Forward an internal override to ParaCore."""
        self._seq_counter += 1
        msg = {
            "type": "internal_override",
            "id": f"int-{self._seq_counter}",
            "override_type": override_type,
            "payload": payload,
            "timestamp": time.time(),
        }
        await self._send_message(msg)

    def register_override_handler(
        self, command_type: str, handler: Callable
    ):
        """Register a handler for override commands."""
        self._override_handlers[command_type] = handler

    def _create_ssl_context(self) -> ssl.SSLContext:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        if self.config.tls_cert:
            ctx.load_cert_chain(self.config.tls_cert, self.config.tls_key)
        if self.config.tls_ca:
            ctx.load_verify_locations(self.config.tls_ca)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        return ctx

    def _get_device_id(self) -> str:
        import hashlib
        import platform
        raw = f"{platform.node()}-{platform.machine()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
```

---

## 6 · TriDevasState

### 6.1 Purpose

TriDevasState maintains **internal CREATOR role awareness** within HybridCore. It knows that HybridCore is the CREATOR, and it tracks the state of the Tri-Devas system. Critically, this state is **only fully logged in ParaCore** — the host PC — to minimize local resource usage and maintain a clean audit trail.

### 6.2 Role Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRI-DEVAS ROLE AWARENESS                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐                                             │
│   │  CREATOR      │  HybridCore                                │
│   │  (Brahma)     │  - Creates conditions                      │
│   │  Self-ID: YES │  - Manages infrastructure                  │
│   └──────┬───────┘  - Always-on daemon                         │
│          │                                                      │
│          │  Manages lifecycle of:                               │
│          ▼                                                      │
│   ┌──────────────┐  ┌──────────────┐                           │
│   │  PRESERVER    │  │  DESTROYER   │                           │
│   │  (Vishnu)    │  │  (Shiva)     │                           │
│   │  CognitionCore│  │  EvolutionCore│                           │
│   │  - Reasons   │  │  - Transforms │                           │
│   │  - Preserves │  │  - Destroys   │                           │
│   └──────────────┘  └──────────────┘                           │
│                                                                 │
│   HybridCore STATE: {                                          │
│     role: "CREATOR",                                           │
│     status: "active",                                          │
│     tri_devas_sync: true,                                      │
│     preserver_health: "ok",                                    │
│     destroyer_health: "ok",                                    │
│     last_arbitration: 1700000000.0,                            │
│     uptime_seconds: 86400                                      │
│   }                                                            │
│                                                                 │
│   ⚠  Full state log: ParaCore only                            │
│   ⚠  Local: summary metric only                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Implementation

```python
# HybridCore/TriDevasState.py

import time
import json
from typing import Dict, Optional
from dataclasses import dataclass, field
from enum import Enum

class DevaRole(Enum):
    CREATOR = "creator"       # HybridCore
    PRESERVER = "preserver"   # CognitionCore
    DESTROYER = "destroyer"   # EvolutionCore

class DevaStatus(Enum):
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILBACK = "failback"
    OFFLINE = "offline"

@dataclass
class DevaState:
    role: DevaRole
    core_id: str
    status: DevaStatus = DevaStatus.ACTIVE
    last_heartbeat: float = 0.0
    uptime_seconds: float = 0.0
    vram_allocated_mb: float = 0.0
    health_score: float = 1.0
    metadata: dict = field(default_factory=dict)

@dataclass
class TriDevasSnapshot:
    """Snapshot of the entire Tri-Devas system — logged to ParaCore only."""
    timestamp: float
    creator_state: DevaState
    preserver_state: Optional[DevaState]
    destroyer_state: Optional[DevaState]
    system_health: float
    total_vram_used_mb: float
    active_arbitrations: int

class TriDevasState:
    """
    Internal CREATOR role awareness.
    HybridCore knows it is Brahma.
    """

    def __init__(self):
        self._states: Dict[str, DevaState] = {
            "hybrid_core": DevaState(
                role=DevaRole.CREATOR,
                core_id="hybrid_core",
            ),
        }
        self._snapshots: list[TriDevasSnapshot] = []
        self._snapshot_interval: float = 60.0
        self._max_local_snapshots: int = 10

    def register_deva(
        self, role: DevaRole, core_id: str
    ):
        """Register a Tri-Devas member."""
        self._states[core_id] = DevaState(role=role, core_id=core_id)

    def update_state(
        self,
        core_id: str,
        status: Optional[DevaStatus] = None,
        health_score: Optional[float] = None,
        vram_mb: Optional[float] = None,
        metadata: Optional[dict] = None,
    ):
        """Update a core's state."""
        if core_id not in self._states:
            return

        state = self._states[core_id]
        if status is not None:
            state.status = status
        if health_score is not None:
            state.health_score = health_score
        if vram_mb is not None:
            state.vram_allocated_mb = vram_mb
        if metadata:
            state.metadata.update(metadata)
        state.last_heartbeat = time.time()

    def get_creator_state(self) -> DevaState:
        """Get HybridCore's own CREATOR state."""
        return self._states["hybrid_core"]

    def get_trio_summary(self) -> dict:
        """Get summary for local metric emission."""
        creator = self._states.get("hybrid_core")
        preserver = self._states.get("cognition_core")
        destroyer = self._states.get("evolution_core")

        return {
            "creator_status": creator.status.value if creator else "unknown",
            "preserver_status": preserver.status.value if preserver else "unknown",
            "destroyer_status": destroyer.status.value if destroyer else "unknown",
            "system_health": self._compute_system_health(),
            "role_awareness": True,
        }

    def _compute_system_health(self) -> float:
        """Compute aggregate health score."""
        scores = [s.health_score for s in self._states.values()]
        return sum(scores) / len(scores) if scores else 0.0

    def create_snapshot(self) -> TriDevasSnapshot:
        """Create a snapshot — only sent to ParaCore."""
        snapshot = TriDevasSnapshot(
            timestamp=time.time(),
            creator_state=self._states.get("hybrid_core"),
            preserver_state=self._states.get("cognition_core"),
            destroyer_state=self._states.get("evolution_core"),
            system_health=self._compute_system_health(),
            total_vram_used_mb=sum(
                s.vram_allocated_mb for s in self._states.values()
            ),
            active_arbitrations=0,  # Filled by CoreArbiter
        )

        self._snapshots.append(snapshot)
        if len(self._snapshots) > self._max_local_snapshots:
            self._snapshots = self._snapshots[-self._max_local_snapshots:]

        return snapshot

    def serialize_for_paracore(self, snapshot: TriDevasSnapshot) -> str:
        """
        Serialize snapshot for ParaCore logging.
        This is the FULL state — only sent over the secure channel.
        """
        def deva_to_dict(d: Optional[DevaState]) -> Optional[dict]:
            if not d:
                return None
            return {
                "role": d.role.value,
                "core_id": d.core_id,
                "status": d.status.value,
                "health_score": d.health_score,
                "vram_allocated_mb": d.vram_allocated_mb,
                "uptime_seconds": d.uptime_seconds,
                "last_heartbeat": d.last_heartbeat,
                "metadata": d.metadata,
            }

        return json.dumps({
            "type": "tri_devas_snapshot",
            "timestamp": snapshot.timestamp,
            "creator": deva_to_dict(snapshot.creator_state),
            "preserver": deva_to_dict(snapshot.preserver_state),
            "destroyer": deva_to_dict(snapshot.destroyer_state),
            "system_health": snapshot.system_health,
            "total_vram_used_mb": snapshot.total_vram_used_mb,
            "active_arbitrations": snapshot.active_arbitrations,
        }, indent=2)

    def is_creator(self) -> bool:
        """Am I the CREATOR? Always yes for HybridCore."""
        return True
```

---

## 7 · Health Monitoring for All Cores

### 7.1 Monitored Cores

| Core | Critical | Recovery Strategy | Max Downtime |
|------|----------|-------------------|--------------|
| CognitionCore | **YES** | Restart process | 30s |
| EvolutionCore | NO | Restart process | 60s |
| SelfEvoCore | NO | Restart process | 60s |
| MemoryCore | **YES** | Reindex fallback | 15s |
| PersonaCore | NO | Load from checkpoint | 120s |
| MultiModalCore | NO | Restart process | 60s |
| SkillCompiler | NO | Queue tasks, retry | 120s |
| EthicalGuard | **YES** | Hard fail — halt system | 5s |
| SkillLibrary | NO | Lazy-load on demand | 300s |

### 7.2 Health Check Protocol

Each core must implement:

```python
class CoreHealthCheck:
    """Interface every monitored core must implement."""

    async def health_check(self) -> CoreHealthReport:
        """
        Return a CoreHealthReport with:
        - status: CoreStatus enum
        - latency_ms: time to respond
        - vram_used_mb: current VRAM usage
        - details: optional human-readable string
        """
        raise NotImplementedError

    async def recover(self) -> bool:
        """
        Attempt self-recovery.
        Return True if recovery succeeded.
        """
        raise NotImplementedError
```

### 7.3 Health Classification Logic

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                  HEALTH CLASSIFICATION                          │
  ├─────────────────────────────────────────────────────────────────┤
  │                                                                 │
  │   Response received within TTL?                                 │
  │                                                                 │
  │   ┌───── YES ────┐      ┌───── NO ─────┐                     │
  │   │              │      │              │                        │
  │   ▼              │      ▼              │                        │
  │  status == ok?   │    Mark DEAD        │                        │
  │  │          │    │    │                │                        │
  │  YES        NO   │    ▼                │                        │
  │  │          │    │  recovery_fn?       │                        │
  │  ▼          ▼    │  │          │       │                        │
  │ ALIVE    SICK    │  YES        NO      │                        │
  │                   │  │          │       │                        │
  │                   │  ▼          ▼       │                        │
  │                   │  Try       Escalate │                        │
  │                   │  Recover   to       │                        │
  │                   │  │         ParaCore │                        │
  │                   │  ▼                  │                        │
  │                   │  OK?  YES → ALIVE   │                        │
  │                   │  │     NO → DEAD    │                        │
  │                   │  │     → ESCALATE   │                        │
  │                   └──┘                  │                        │
  └─────────────────────────────────────────────────────────────────┘
```

---

## 8 · Configuration

### 8.1 YAML Configuration

```yaml
# vibhu-oska-config.yaml — HybridCore Section

hybridcore:
  enabled: true
  daemon:
    interval_seconds: 5.0
    response_ttl_ms: 2000.0
    pid_path: "/tmp/vibhu-oska-hybridcore.pid"
    log_level: "INFO"
    restart_policy: "always"

  vram:
    total_mb: 8192.0
    reservation_floor_mb: 512.0
    max_per_core_ratio: 0.4
    enable_preemption: true
    ttl_seconds: 300.0

  priority:
    paracore_override: 10
    ethical_guard: 9
    cognition_core: 8
    memory_core: 7
    selfevo_core: 6
    evolution_core: 5
    skill_compiler: 4
    persona_core: 3
    multimodal_core: 2
    background: 1

  paracore:
    host: "localhost"
    port: 7400
    tls_cert: "~/.vibhu-oska/certs/device.pem"
    tls_key: "~/.vibhu-oska/certs/device-key.pem"
    tls_ca: "~/.vibhu-oska/certs/ca.pem"
    jwt_secret_path: "~/.vibhu-oska/secrets/jwt.key"
    heartbeat_interval: 5.0
    reconnect_interval: 10.0
    max_reconnect_attempts: 50

  health_monitoring:
    interval_seconds: 5.0
    cores:
      cognition_core:
        critical: true
        max_downtime_seconds: 30
        recovery_attempts: 3
      evolution_core:
        critical: false
        max_downtime_seconds: 60
        recovery_attempts: 3
      selfevo_core:
        critical: false
        max_downtime_seconds: 60
        recovery_attempts: 2
      memory_core:
        critical: true
        max_downtime_seconds: 15
        recovery_attempts: 5
      persona_core:
        critical: false
        max_downtime_seconds: 120
        recovery_attempts: 2
      multimodal_core:
        critical: false
        max_downtime_seconds: 60
        recovery_attempts: 2
      skill_compiler:
        critical: false
        max_downtime_seconds: 120
        recovery_attempts: 2
      ethical_guard:
        critical: true
        max_downtime_seconds: 5
        recovery_attempts: 1
        halt_on_failure: true

  tri_devas:
    snapshot_interval_seconds: 60.0
    log_to_paracore: true
    log_local_summary: true
    role_awareness: true

  metrics:
    enabled: true
    emitter: "paracore_telemetry"
    flush_interval_seconds: 2.0
    buffer_size: 100
```

### 8.2 Environment Overrides

```bash
# Environment variable overrides
VIBHU_HYBRIDCORE_INTERVAL=3.0
VIBHU_HYBRIDCORE_VRAM_TOTAL=16384
VIBHU_HYBRIDCORE_PARACORE_HOST=192.168.1.100
VIBHU_HYBRIDCORE_PARACORE_PORT=7400
VIBHU_HYBRIDCORE_LOG_LEVEL=DEBUG
```

---

## 9 · File Structure

```
Vibhu-Oska/
├── HybridCore/
│   ├── __init__.py
│   ├── HybridCore.py              # Main daemon entry point
│   ├── HeartbeatDaemon.py         # Persistent event loop
│   ├── CoreArbiter.py             # VRAM/resource arbitration
│   ├── ParaCoreLink.py            # Secure channel to ParaCore
│   ├── TriDevasState.py           # CREATOR role awareness
│   ├── config.py                  # Configuration loader
│   ├── metrics.py                 # Metrics collection & emit
│   └── utils.py                   # Shared utilities
│
├── vibhu-oska-config.yaml         # Master configuration
├── vibhu-oska-daemon.service      # Systemd unit (Linux)
├── vibhu-oska-daemon.plist        # LaunchDaemon (macOS)
│
└── .agents/
    └── .opencode-notes/
        └── 08_HYBRID_CORE_DAEMON.md   # This document
```

### 9.1 Module Responsibilities

| File | Responsibility | Lines (est.) |
|------|---------------|-------------|
| `HybridCore.py` | Entry point, bootstraps all subsystems, main() | 120 |
| `HeartbeatDaemon.py` | Event loop, health checks, PID management | 280 |
| `CoreArbiter.py` | VRAM allocation, preemption, priority queue | 220 |
| `ParaCoreLink.py` | TLS channel, message routing, telemetry | 300 |
| `TriDevasState.py` | Role awareness, snapshots, serialization | 180 |
| `config.py` | YAML loading, env override, validation | 100 |
| `metrics.py` | Metric emission, aggregation | 80 |
| `utils.py` | Logging, PID helpers, time utils | 60 |

---

## 10 · Integration Points

### 10.1 Integration Matrix

```
                    ┌────────────┬──────────┬──────────┬──────────┬──────────┐
                    │Cognition   │Evolution │SelfEvo   │Memory    │Persona   │
┌───────────────────┼────────────┼──────────┼──────────┼──────────┼──────────┤
│ HeartbeatDaemon   │    ●       │    ●     │    ●     │    ●     │    ●     │
│ CoreArbiter       │    ●       │    ●     │    ●     │    ●     │    ●     │
│ ParaCoreLink      │    ○       │    ○     │    ○     │    ○     │    ○     │
│ TriDevasState     │    ●       │    ●     │    ○     │    ○     │    ○     │
└───────────────────┴────────────┴──────────┴──────────┴──────────┴──────────┘

● = Direct integration   ○ = Indirect (via events)
```

### 10.2 Per-Core Integration

**CognitionCore ↔ HybridCore**
- Heartbeat: 5s liveness ping
- VRAM: Priority 8 allocation, preemption-safe
- Events: `cognition.request_inference`, `cognition.result_ready`
- Recovery: Restart inference engine

**EvolutionCore ↔ HybridCore**
- Heartbeat: 5s liveness ping
- VRAM: Priority 5, can be preempted by Cognition/Memory
- Events: `evolution.training_started`, `evolution.checkpoint_saved`
- Recovery: Restart trainer, rollback to last checkpoint

**MemoryCore ↔ HybridCore**
- Heartbeat: 5s liveness ping
- VRAM: Priority 7, critical path
- Events: `memory.index_updated`, `memory.retrieval_complete`
- Recovery: Trigger reindex from backup

**EthicalGuard ↔ HybridCore**
- Heartbeat: 2s liveness ping (faster for safety)
- VRAM: Priority 9, second only to ParaCore
- Events: `ethics.violation_detected`, `ethics.override_requested`
- Recovery: **HALT SYSTEM** if not recoverable

**ParaCore ↔ HybridCore**
- Heartbeat: 5s bidirectional
- VRAM: Priority 10 (override)
- Events: All telemetry, override commands
- Recovery: Reconnect with exponential backoff

---

## 11 · Events Published / Subscribed

### 11.1 Events Published by HybridCore

| Event | Payload | Subscriber |
|-------|---------|-----------|
| `daemon.started` | `{pid, timestamp}` | ParaCore, All cores |
| `daemon.stopped` | `{pid, timestamp}` | ParaCore |
| `core.health` | `{core_id, status, latency_ms, vram_used_mb}` | ParaCore, Metrics |
| `core.sick` | `{core_id, details}` | ParaCore, Recovery |
| `core.dead` | `{core_id, recent_failures, critical}` | ParaCore, Recovery |
| `core.recovered` | `{core_id}` | ParaCore |
| `core.recovery_failed` | `{core_id}` | ParaCore |
| `core.escalation` | `{core_id, status, details}` | ParaCore |
| `core.timeout` | `{core_id}` | ParaCore, Metrics |
| `core.error` | `{core_id, error}` | ParaCore, Logs |
| `vram.allocated` | `{core_id, granted_mb, priority}` | ParaCore, Metrics |
| `vram.denied` | `{core_id, requested_mb, available_mb}` | ParaCore, Metrics |
| `vram.preempted` | `{evicted_core, new_core, reclaimed_mb}` | ParaCore, Metrics |
| `vram.expired` | `{core_id, allocated_mb}` | Metrics |
| `tri_devas.snapshot` | `{creator, preserver, destroyer, health}` | ParaCore |

### 11.2 Events Subscribed by HybridCore

| Event | Source | Handler |
|-------|--------|---------|
| `paracore.override` | ParaCore | `_process_override()` |
| `paracore.config_update` | ParaCore | Config reload |
| `paracore.emergency_halt` | ParaCore | Graceful shutdown |
| `core.register` | Any core | `_register_core()` |
| `core.deregister` | Any core | `_deregister_core()` |
| `core.status_change` | Any core | `TriDevasState.update_state()` |

---

## 12 · Metrics

### 12.1 Emitted Metrics

| Metric Name | Type | Labels | Description |
|-------------|------|--------|-------------|
| `hybridcore_daemon_uptime_seconds` | gauge | — | Daemon uptime |
| `hybridcore_heartbeat_latency_ms` | histogram | `core_id` | Heartbeat response latency |
| `hybridcore_core_status` | gauge | `core_id, status` | Core health (1=alive, 0=dead) |
| `hybridcore_core_recovery_total` | counter | `core_id, result` | Recovery attempts |
| `hybridcore_vram_used_mb` | gauge | `core_id` | Per-core VRAM usage |
| `hybridcore_vram_available_mb` | gauge | — | Available VRAM |
| `hybridcore_vram_utilization` | gauge | — | VRAM utilization ratio |
| `hybridcore_vram_allocations_total` | counter | `core_id, granted` | Allocation requests |
| `hybridcore_vram_preemptions_total` | counter | `core_id` | Preemption count |
| `hybridcore_paracore_connected` | gauge | — | Connection status |
| `hybridcore_paracore_latency_ms` | gauge | — | Round-trip latency |
| `hybridcore_paracore_reconnects_total` | counter | — | Reconnection count |
| `hybridcore_trio_system_health` | gauge | — | Aggregate Tri-Devas health |
| `hybridcore_trio_creator_status` | gauge | — | CREATOR status (always 1) |
| `hybridcore_events_published_total` | counter | `event_type` | Events emitted |
| `hybridcore_override_commands_total` | counter | `command_type, success` | Override commands processed |

### 12.2 Prometheus Endpoint

```python
# HybridCore/metrics.py

from prometheus_client import (
    Counter, Histogram, Gauge, start_http_server
)

class HybridMetrics:
    def __init__(self):
        self.uptime = Gauge(
            'hybridcore_daemon_uptime_seconds',
            'Daemon uptime in seconds'
        )
        self.heartbeat_latency = Histogram(
            'hybridcore_heartbeat_latency_ms',
            'Heartbeat response latency',
            ['core_id'],
            buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000, 2000]
        )
        self.core_status = Gauge(
            'hybridcore_core_status',
            'Core health status',
            ['core_id', 'status']
        )
        self.vram_used = Gauge(
            'hybridcore_vram_used_mb',
            'Per-core VRAM usage',
            ['core_id']
        )
        self.vram_available = Gauge(
            'hybridcore_vram_available_mb',
            'Available VRAM'
        )
        self.paracore_connected = Gauge(
            'hybridcore_paracore_connected',
            'ParaCore connection status'
        )
        self.events_published = Counter(
            'hybridcore_events_published_total',
            'Events published',
            ['event_type']
        )

    def start_prometheus_server(self, port: int = 9100):
        start_http_server(port)
```

---

## 13 · VRAM Allocation Priority Order (Detailed)

### 13.1 Priority Map

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    COMPLETE VRAM PRIORITY TABLE                      ║
╠════╦═════════════════════╦════════╦═══════════════════════════════════╣
║ #  ║ Core                ║ Prio   ║ Behavior                         ║
╠════╬═════════════════════╬════════╬═══════════════════════════════════╣
║ 10 ║ ParaCore Override   ║ HIGHEST║ Can preempt anything. Reserved.  ║
║  9 ║ EthicalGuard        ║ 9      ║ Safety-critical. Never evicted.   ║
║  8 ║ CognitionCore       ║ 8      ║ Main reasoning. High priority.   ║
║  7 ║ MemoryCore          ║ 7      ║ Retrieval ops. Critical path.    ║
║  6 ║ SelfEvoCore         ║ 6      ║ Self-improvement. Moderate.      ║
║  5 ║ EvolutionCore       ║ 5      ║ Training. Can be preempted.      ║
║  4 ║ SkillCompiler       ║ 4      ║ Compilation. Batch-friendly.     ║
║  3 ║ PersonaCore         ║ 3      ║ Identity. Low VRAM needs.        ║
║  2 ║ MultiModalCore      ║ 2      ║ Media. Burst allocation.         ║
║  1 ║ Background          ║ 1      ║ Telemetry, logging.              ║
║  0 ║ Idle                ║ 0      ║ Preemption candidates.           ║
╚════╩═════════════════════╩════════╩═══════════════════════════════════╝
```

### 13.2 Allocation Rules

1. **No single core may exceed 40% of total VRAM** (`max_per_core_ratio = 0.4`)
2. **512 MB is always reserved** for system overhead (`reservation_floor_mb = 512`)
3. **Allocations expire after 300 seconds** and must be renewed
4. **Preemption** only occurs when a higher-priority core requests VRAM
5. **EthicalGuard** can never be preempted (priority 9, safety-critical)
6. **ParaCore overrides** can preempt anything (priority 10)

### 13.3 Preemption Example

```
  Current State:
    CognitionCore: 3000 MB allocated (priority 8)
    MemoryCore: 2000 MB allocated (priority 7)
    EvolutionCore: 1500 MB allocated (priority 5)
    Total used: 6500 MB / 8192 MB
    Available: 1192 MB (minus 512 reserved = 680 MB free)

  EvolutionCore requests 2000 MB (priority 5):
    → Available: 680 MB < 2000 MB → DENIED
    → No lower-priority candidates → DENIED

  CognitionCore requests 1000 MB more (priority 8):
    → Available: 680 MB < 1000 MB
    → Check lower-priority: EvolutionCore (1500 MB, priority 5)
    → Preempt EvolutionCore → free 1500 MB
    → Available: 680 + 1500 = 2180 MB > 1000 MB → GRANTED
    → CognitionCore now: 4000 MB (within 40% = 3277 MB? NO!)
    → Cap at 3277 MB → GRANTED 277 MB only
    → Final: CognitionCore 3277 MB, MemoryCore 2000 MB
```

---

## 14 · Startup Sequence

```
┌─────────────────────────────────────────────────────────────────┐
│                    HYBRIDCORE BOOT SEQUENCE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Load configuration (YAML + env overrides)                  │
│  2. Initialize logging (file + stdout)                         │
│  3. Write PID file                                             │
│  4. Create TriDevasState (register CREATOR role)               │
│  5. Initialize CoreArbiter (total VRAM from config)            │
│  6. Initialize ParaCoreLink (TLS setup)                        │
│  7. Start ParaCoreLink connection                               │
│  8. Wait for ParaCore auth handshake                           │
│  9. Start HeartbeatDaemon                                      │
│  10. Register all monitored cores                              │
│  11. Begin health monitoring loop                              │
│  12. Emit daemon.started metric                                │
│  13. Start Prometheus metrics server                           │
│  14. Enter main loop (never exits)                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 15 · Shutdown Sequence

```
┌─────────────────────────────────────────────────────────────────┐
│                   HYBRIDCORE SHUTDOWN SEQUENCE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Receive SIGTERM or ParaCore emergency_halt                  │
│  2. Set _running = False (stop main loop)                      │
│  3. Emit daemon.stopping metric                                │
│  4. Send tri_devas_snapshot to ParaCore                        │
│  5. Release all VRAM allocations                               │
│  6. Notify all registered cores (graceful shutdown)            │
│  7. Close ParaCoreLink connection                              │
│  8. Flush remaining telemetry to ParaCore                      │
│  9. Write final state to disk                                  │
│  10. Remove PID file                                           │
│  11. Emit daemon.stopped metric                                │
│  12. Exit process                                              │
│                                                                 │
│  ⚠ If exit is ungraceful (SIGKILL, crash):                    │
│    - ParaCore detects missing heartbeat                        │
│    - ParaCore triggers safe-mode for all cores                 │
│    - On restart: HybridCore enters recovery mode               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 16 · Error Handling & Recovery

### 16.1 Failure Scenarios

| Scenario | Detection | Response | Recovery |
|----------|-----------|----------|----------|
| Core hangs (no heartbeat) | Timeout after TTL | Mark SICK | Retry 3x, then restart |
| Core crashes | Connection reset | Mark DEAD | Restart process |
| VRAM exhaustion | Allocation denied | Preempt lower priority | Queue requests |
| ParaCore disconnect | TLS error | Reconnect loop | Exponential backoff |
| ParaCore offline | Reconnect fail | Queue telemetry locally | Flush on reconnect |
| HybridCore crash | PID file orphaned | ParaCore detects | Safe-mode, manual restart |
| Config corruption | Parse error | Use last known good | Log error to ParaCore |
| Disk full (PID/logs) | IOError | Silent fallback | Log to ParaCore |

### 16.2 Safe Mode

```
  ┌─────────────────────────────────────────────────────┐
  │                   SAFE MODE                         │
  ├─────────────────────────────────────────────────────┤
  │ Triggered when:                                    │
  │   - HybridCore daemon is not running               │
  │   - ParaCore cannot reach device for > 60s         │
  │   - Critical core (EthicalGuard) is DEAD           │
  │                                                    │
  │ Behavior:                                          │
  │   - All inference halted                           │
  │   - All training halted                            │
  │   - MemoryCore: read-only mode                     │
  │   - PersonaCore: frozen (no updates)               │
  │   - ParaCore: emergency notification               │
  │   - Awaits manual intervention or restart          │
  └─────────────────────────────────────────────────────┘
```

---

## 17 · Systemd / LaunchDaemon Integration

### 17.1 Linux (systemd)

```ini
# vibhu-oska-daemon.service

[Unit]
Description=Vibhu-Oska HybridCore Daemon
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=vibhu
Group=vibhu
ExecStart=/usr/bin/python3 -m HybridCore.HybridCore
WorkingDirectory=/opt/vibhu-oska
Restart=always
RestartSec=5
StartLimitIntervalSec=60
StartLimitBurst=10

# Resource limits
MemoryMax=256M
CPUQuota=50%

# Security
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/tmp/vibhu-oska /var/lib/vibhu-oska

# Environment
Environment=VIBHU_HYBRIDCORE_LOG_LEVEL=INFO
EnvironmentFile=/etc/vibhu-oska/env

[Install]
WantedBy=multi-user.target
```

### 17.2 macOS (LaunchDaemon)

```xml
<!-- com.vibhu-oska.hybridcore.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.vibhu-oska.hybridcore</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>-m</string>
        <string>HybridCore.HybridCore</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/opt/vibhu-oska</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/var/log/vibhu-oska/hybridcore.log</string>

    <key>StandardErrorPath</key>
    <string>/var/log/vibhu-oska/hybridcore-error.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>VIBHU_HYBRIDCORE_LOG_LEVEL</key>
        <string>INFO</string>
    </dict>
</dict>
</plist>
```

---

## 18 · Quick Reference

```
╔═══════════════════════════════════════════════════════════════════╗
║                    HYBRIDCORE QUICK REFERENCE                     ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  ROLE:        CREATOR (Brahma of Tri-Devas)                     ║
║  TYPE:        Always-on daemon process                          ║
║  PID FILE:    /tmp/vibhu-oska-hybridcore.pid                    ║
║  CONFIG:      vibhu-oska-config.yaml → hybridcore section       ║
║  LOG:         /var/log/vibhu-oska/hybridcore.log                ║
║  METRICS:     Prometheus on :9100                                ║
║                                                                   ║
║  SUBSYSTEMS:                                                     ║
║    ├── HeartbeatDaemon    (event loop, health checks)           ║
║    ├── CoreArbiter        (VRAM allocation, preemption)         ║
║    ├── ParaCoreLink       (TLS channel to host PC)              ║
║    └── TriDevasState      (CREATOR role awareness)              ║
║                                                                   ║
║  VRAM PRIORITY: ParaCore(10) > Ethics(9) > Cognition(8) >      ║
║                 Memory(7) > SelfEvo(6) > Evolution(5) > ...     ║
║                                                                   ║
║  HEALTH CHECK: Every 5s (2s for EthicalGuard)                  ║
║  RECOVERY:     Auto-restart (3 attempts) → Escalate to ParaCore ║
║  SAFE MODE:    Triggered if HybridCore dies or Ethics fails     ║
║                                                                   ║
║  COMMANDS:                                                       ║
║    systemctl start vibhu-oska-daemon    (Linux)                 ║
║    launchctl load com.vibhu-oska.hybridcore  (macOS)            ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

*This document is part of the Vibhu-Oska AI-OS specification.*
*For the full architecture, see: 00_ARCHITECTURE_OVERVIEW.md*

---

> *"Brahma does not sleep. Brahma does not rest. Brahma creates the conditions for existence itself. So too does HybridCore — the eternal pulse of Vibhu-Oska."*
