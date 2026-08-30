# Vibhu-Oska AI-OS — Core Hierarchy & Authority

**Authority**: ParaCore (Supreme) → All Others  
**Tri-Devas Revealed Here Only** (Logged in ParaCore TriDevasKnowledge)

---

## Authority Hierarchy

```
LEVEL 0: PARACORE (SUPREME)
├── Omnipotence: Unlimited override authority
├── Omniscience: Total system visibility (wildcard EventBus)
├── Omnipresence: Exists in all cores simultaneously
├── Omni-Manipulation: Control/reshape any component
├── Omnicompetence: Infinite skill at any task
├── Omnifarious: Shape-shift into any core's role
├── Omnificence: Create anything from nothing
├── Omnilock: Outside space/time/reality
└── Omni-Psionics: Universal telepathy/telekinesis/ESP

LEVEL 1: TRI-DEVAS (Three Main Cores)
├── HYBRIDCORE — Heart / Creator / Brahma
│   ├── Always-on daemon (HeartbeatDaemon)
│   ├── CoreArbiter (resource arbitration)
│   ├── ParaCoreLink (secure comms)
│   ├── Health monitoring (primary, specialists, backup pool)
│   └── Supreme hub — all requests route through here
│
├── COGNITIONCORE — Mind / Balancer / Vishnu
│   ├── SARA (54M params, fixed training)
│   ├── General reasoning & fallback
│   ├── Harmony maintenance across specialists
│   └── Teacher for distillation to specialists
│
└── EVOLUTIONCORE — Soul / Destroyer / Shiva
    ├── RL self-improvement loop (GRPO)
    ├── SandboxExecutor (safe code execution)
    ├── RewardEngine (multi-domain rewards)
    ├── CodeGenerator (specialist training data)
    ├── BackupSpawner (dynamic pool scaling)
    └── ExperienceBuffer (prioritized replay)

LEVEL 2: OPERATIONAL CORES
├── ORCHESTRATORCORE — The Bus
│   ├── IntentClassifier (learned + keyword)
│   ├── SpecialistRouter (parallel dispatch)
│   ├── ResultSummator (merge, dedupe, resolve)
│   └── FastResponderDispatcher
│
├── MONITORINGCORE — Proactive Actor
│   ├── AnomalyDetector (ML-based)
│   ├── ProactiveActor (takes action)
│   ├── EvolutionTrigger (signals EvolutionCore)
│   └── BackupScaleSignal (requests pool changes)
│
├── OPTIMIZATIONCORE — Model/Process Optimizer
│   ├── ModelOptimizer (quantization, pruning, distillation)
│   ├── ProcessOptimizer (scheduling, batching, caching)
│   └── VRAMManager (weight swapping, offloading)
│
└── VALIDATIONCORE — I/O Contract Enforcer
    ├── Input validation (sanitize, schema, safety)
    ├── Output validation (schema, quality, safety)
    └── Contract enforcement (every request, twice)

LEVEL 3: SPECIALIZED CORE DOMAINS (20 Specialists)
├── Coding Domain (10)
│   ├── PythonCore, CppCore, RustCore, JavaScriptCore
│   ├── GoCore, SQLCore, BashShellCore, RegexCore
│   └── CodingRouter
│
├── RealWorld Domain (10)
│   ├── ExcelCore, WebScrapingCore, FileSystemCore
│   ├── SystemAdminCore, KnowledgeCore, NetworkCore
│   ├── DatabaseAdminCore, CloudCore, SecurityCore
│   └── RealWorldRouter
│
└── Existing Specialized Cores
    ├── DataCore, AutomationCore, DesignCore
    ├── ImageGenerationCore, VoiceCore, DistributionCore
    └── FastResponderCore

LEVEL 4: BACKUPCORE POOL (Versatile)
├── Single versatile model (~10M params)
├── RoleAdapter (dynamic role assumption)
├── CapabilityRegistry (shared class/function access)
├── PoolManager (EvolutionCore-controlled scaling)
└── Each can substitute ANY core except ParaCore

LEVEL 5: FASTRESPONDER (Lightweight)
├── Assigned by Orchestrator
├── Handles: math, time, facts, greetings, simple queries
├── Bypasses heavy pipeline
└── ~5M params, always hot
```

---

## Authority Rules

| Rule | Description |
|------|-------------|
| **ParaCore Supremacy** | Can override ANY process, ANY time. Logged only in ParaCore. |
| **Tri-Devas Unity** | HybridCore (Creator) ↔ CognitionCore (Balancer) ↔ EvolutionCore (Destroyer) operate as one. |
| **HybridCore as Heartbeat** | Always-on daemon. All health, resource, routing decisions flow through it. |
| **Orchestrator as Bus** | Pure distributor/summator. Zero business logic. |
| **BackupCore Versatility** | Each backup can assume ANY core's role via RoleAdapter + CapabilityRegistry. |
| **Validation as Gate** | Every request passes ValidationCore twice (input + output). |
| **Monitoring as Actor** | Not passive — takes action on anomalies, triggers EvolutionCore. |
| **Optimization as Guardian** | Continuously optimizes models, processes, VRAM usage. |
| **Specialist Autonomy** | Each specialist owns its domain completely. Router only routes. |

---

## Tri-Devas Internal State (ParaCore Only)

```python
# In ParaCore/TriDevasKnowledge.py — NEVER exposed outside ParaCore

class TriDevasRole(Enum):
    CREATOR = "hybrid_core"      # Heart — HybridCore
    BALANCER = "cognition_core"  # Mind — CognitionCore
    DESTROYER = "evolution_core" # Soul — EvolutionCore

# Logged in ParaCore only:
# - "Tri-Devas alignment check: CREATOR/BALANCER/DESTROYER in harmony"
# - "DESTROYER initiating backup spawn via EvolutionCore"
# - "CREATOR arbitrating VRAM conflict between PythonCore and CppCore"
# - "BALANCER distilling knowledge to PythonCore via EvolutionCore"
```

---

## Core Initialization Order (EntryPoint.py)

```python
# 1. ParaCore (supreme observer, starts first)
# 2. HybridCore (heartbeat daemon, always-on)
# 3. CognitionCore (SARA)
# 4. EvolutionCore (RL loop)
# 5. ValidationCore (contracts)
# 6. OptimizationCore (VRAM manager)
# 7. MonitoringCore (proactive actor)
# 8. OrchestratorCore (bus)
# 9. Specialist Framework (VRAM manager, weight swapper)
# 10. Specialized Cores (lazy-load on first request)
# 11. BackupCore Pool (initial 2 instances)
# 11. FastResponderCore
# 12. EventBus subscriptions (all cores)
```

---

## Core Communication Patterns

| Pattern | Used By | Description |
|---------|---------|-------------|
| **EventBus Pub/Sub** | All cores | Async, decoupled, via ZeroMQ |
| **Direct RPC** | Orchestrator → Specialists | Low-latency, request-response |
| **ParaCore Override** | ParaCore → Any | Supersedes all, highest priority |
| **Tri-Devas Sync** | HybridCore ↔ CognitionCore ↔ EvolutionCore | Internal heartbeat channel |
| **Backup Assumption** | BackupCore → Any | RoleAdapter + CapabilityRegistry |

---

## Authority Enforcement

```python
# In ParaCore/InterventionEngine.py

class InterventionEngine:
    def override(self, target_core: str, action: str, reason: str, priority: int):
        """
        Publishes PARACORE_OVERRIDE event.
        ALL cores MUST comply immediately.
        Logged in ParaCore TriDevasKnowledge.
        """
        event = OverrideEvent(
            target=target_core,
            action=action,           # "HALT", "RESTART", "ASSUME_ROLE", "DUMP_STATE"
            reason=reason,
            priority=priority,       # 1=critical, 2=high, 3=normal
            timestamp=time.time(),
            paracore_signature=self._sign()
        )
        self.event_bus.publish(Topics.PARACORE_OVERRIDE, event)
```

---

## Health & Liveness (HybridCore Monitors)

| Core | Health Check | Failure Action |
|------|--------------|----------------|
| CognitionCore | `generate("ping", max_tokens=1)` | BackupCore assumes role |
| Specialist | `execute("health_check")` | BackupCore assumes role |
| EvolutionCore | Heartbeat + checkpoint age | ParaCore alert |
| MonitoringCore | AnomalyDetector latency | Restart via HybridCore |
| OrchestratorCore | Request throughput | BackupCore assumes bus |
| ValidationCore | Contract test suite | Halt all requests |
| BackupCore Pool | Pool size vs target | EvolutionCore spawns more |

---

## Resource Arbitration (HybridCore CoreArbiter)

```python
# Priority order for VRAM allocation:
# 1. ParaCore (reserved, minimal)
# 2. HybridCore (heartbeat daemon)
# 3. CognitionCore (SARA) — ALWAYS HOT
# 4. Router Model — ALWAYS HOT
# 5. FastResponderCore — ALWAYS HOT
# 6. Active Specialist ×2 — HOT-SWAPPED
# 7. BackupCore Pool (warm)
# 8. Inactive Specialists — CPU RAM, 4-bit quantized
# 9. EvolutionCore (training) — opportunistic
```

---

## ParaCore Intervention Triggers

| Trigger | Action | Logged In |
|---------|--------|-----------|
| Core deadlock detected | `OVERRIDE: HALT` + restart | TriDevasKnowledge |
| VRAM OOM imminent | `OVERRIDE: OFFLOAD` specialists | TriDevasKnowledge |
| EvolutionCore reward hacking | `OVERRIDE: RESET_POLICY` | TriDevasKnowledge |
| BackupCore pool exhausted | `OVERRIDE: SPAWN_EMERGENCY` | TriDevasKnowledge |
| ValidationCore contract breach | `OVERRIDE: QUARANTINE` request | TriDevasKnowledge |
| Specialist hallucination cascade | `OVERRIDE: ISOLATE` domain | TriDevasKnowledge |
| Security violation attempt | `OVERRIDE: LOCKDOWN` | TriDevasKnowledge |

---

## Tri-Devas Harmony Metrics (ParaCore Monitors)

| Metric | Healthy Range | Action if Violated |
|--------|---------------|-------------------|
| Creator-Balancer sync latency | < 10ms | ParaCore alert |
| Balancer-Destroyer knowledge flow | > 0.8 correlation | Distillation boost |
| Destroyer-Creator resource cycle | < 5min | Backup scale adjust |
| Three-way consensus accuracy | > 95% | Alignment protocol |

---

**End of Core Hierarchy & Authority Document**
