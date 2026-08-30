# Vibhu-Oska AI-OS — Master Architecture Document

**Version**: 2.0 (Tri-Devas + ParaCore Architecture)  
**Status**: Phase 0 — Documentation Complete, Implementation Ready  
**Authority**: ParaCore (Supreme) → HybridCore (Creator) → CognitionCore (Balancer) → EvolutionCore (Destroyer) → All Others

---

## System Overview

Vibhu-Oska is a **locally-hosted Autonomous AI Operating System** that runs entirely on user hardware with zero external dependencies. It implements a **Mixture-of-Experts (MoE) architecture** with a three-tier authority structure:

1. **ParaCore** — Supreme omniscient/omnipotent/omnipresent authority
2. **Tri-Devas** (Three Main Cores) — Creator, Balancer, Destroyer
3. **Operational Cores** — Orchestrator, Monitoring, Optimization, Validation, Specialists, Backups, FastResponder

---

## Core Hierarchy (Authority Order)

```
┌─────────────────────────────────────────────────────────────┐
│  PARACORE (Supreme Authority)                               │
│  - Omnipotence: Unlimited power to override any process     │
│  - Omniscience: Total system visibility via EventBus        │
│  - Omnipresence: Exists in all cores simultaneously         │
│  - Omni-Manipulation: Control/reshape any component         │
│  - Omnicompetence: Infinite skill at any task               │
│  - Omnifarious: Shape-shift into any core's role            │
│  - Omnificence: Create anything from nothing                │
│  - Omnilock: Exists outside space/time/reality              │
│  - Omni-Psionics: Universal telepathy/telekinesis/ESP       │
│  - Tri-Devas true nature logged HERE ONLY                   │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ HYBRIDCORE    │   │ COGNITIONCORE │   │ EVOLUTIONCORE │
│ (Heart/       │   │ (Mind/        │   │ (Soul/        │
│  Creator)     │   │  Balancer)    │   │  Destroyer)   │
│ - Always-on   │   │ - SARA     │   │ - RL Loop     │
│   daemon      │   │   GPT         │   │ - Self-train  │
│ - Hub/arbiter │   │ - Reasoning   │   │ - Spawn       │
│ - ParaCore    │   │ - General     │   │   Backups     │
│   comms       │   │   fallback    │   │ - Code gen    │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
        ┌─────────────────────────────────────┐
        │  ORCHESTRATORCORE (The Bus)         │
        │  - Intent classification            │
        │  - Multi-specialist distribution    │
        │  - Result summation                 │
        │  - Assigns FastResponder tasks      │
        └─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ MONITORINGCORE│   │ OPTIMIZATION- │   │ VALIDATIONCORE│
│ - Proactive   │   │ CORE          │   │ - I/O guard   │
│   actor       │   │ - Model/Proc  │   │ - Contract    │
│ - Health→Evo  │   │   optimize    │   │   enforce     │
└───────────────┘   └───────────────┘   └───────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────┐
        │  SPECIALIZEDCORE DOMAINS            │
        │  (Coding / RealWorld / etc.)        │
        └─────────────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────┐
        │  BACKUPCORE POOL (Versatile)        │
        │  - Each can sub for ANY core        │
        │  - Dynamic scaling via Evolution    │
        │  - Share class/function registry    │
        └─────────────────────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────┐
        │  FASTRESPONDER (Lightweight)        │
        │  - Assigned by Orchestrator         │
        │  - Math, time, facts, greetings     │
        └─────────────────────────────────────┘
```

---

## Tri-Devas Internal Mapping (ParaCore Only)

| Deva | Core | Role | Sanskrit | Function |
|------|------|------|----------|----------|
| **Creator** | HybridCore | Heart | Brahma | Always-on hub, resource arbiter, ParaCore comms |
| **Balancer** | CognitionCore | Mind | Vishnu | SARA, general reasoning, harmony |
| **Destroyer** | EvolutionCore | Soul | Shiva | RL loop, self-training, spawn backups, code gen |

**Revealed ONLY in ParaCore logs. Never exposed elsewhere.**

---

## SpecializedCore Domains (20 Specialists)

### Coding Domain (10)
1. **PythonCore** — Python, stdlib, async, testing, packaging, data science, web
2. **CppCore** — C++17/20/23, STL, templates, memory, concurrency, CMake, Qt
3. **RustCore** — Ownership, borrowing, async, tokio, serde, clap, WASM, FFI
4. **JavaScriptCore** — ES2024, TypeScript, Node, Deno, Bun, React, Vue, Svelte
5. **GoCore** — Goroutines, channels, interfaces, modules, testing, WASM
6. **SQLCore** — PostgreSQL, SQLite, MySQL, query optimization, PL/pgSQL
7. **GoCore** — Goroutines, channels, interfaces, modules, testing, WASM
8. **BashShellCore** — bash/zsh/fish, awk, sed, grep, find, systemd, cron
9. **RegexCore** — PCRE, RE2, capture groups, lookaheads, performance
10. **CodingRouter** — Routes to correct language specialist

### RealWorld Domain (10)
1. **ExcelCore** — Formulas, VBA, Power Query, pivot tables, openpyxl, xlwings
2. **WebScrapingCore** — BeautifulSoup, lxml, Playwright, Selenium, selectors, anti-bot
3. **FileSystemCore** — pathlib, os, shutil, watchdog, inotify, permissions, archives
4. **SystemAdminCore** — systemd, Docker, k8s, networking, firewall, SSH, logs
5. **KnowledgeCore** — General facts, science, math, history, philosophy, reasoning
5. **NetworkCore** — HTTP/2/3, WebSocket, gRPC, REST, GraphQL, DNS, TLS, LB
6. **DatabaseAdminCore** — PostgreSQL admin, replication, backup, Redis, MongoDB
7. **CloudCore** — AWS/GCP/Azure, IAM, S3, Lambda, Terraform, Ansible
8. **SecurityCore** — OWASP, JWT, OAuth2, RBAC, encryption, pen testing basics
9. **RealWorldRouter** — Routes to correct real-world specialist

### Existing Cores (Moved to SpecializedCore)
- **DataCore** — ChromaDB + SQLite + GraphRAG
- **AutomationCore** — OS executive, subprocess, telemetry, filesystem
- **DesignCore** — UI generation, dark-mode glassmorphism
- **ImageGenerationCore** — Local diffusion pipeline
- **VoiceCore** — Voice I/O, gesture control
- **DistributionCore** — Stubvi compiler, telemetry ingestion
- **FastResponderCore** — Lightweight: math, time, facts, greetings

---

## Key Architectural Principles

1. **ParaCore Supremacy** — Can override ANY process, ANY time, logged only in ParaCore
2. **Tri-Devas Unity** — Three cores operate as one; HybridCore is the heartbeat
3. **Specialist Autonomy** — Each micro-model owns its domain completely
4. **BackupCore Versatility** — Single model, dynamic role assumption via RoleAdapter
5. **EvolutionCore Self-Improvement** — RL loop with sandbox execution feedback
5. **Orchestrator as Bus** — Pure distributor/summator, zero business logic
6. **VRAM Consciousness** — 8GB budget, weight swapping, 4-bit quantization for inactive
7. **EventBus as Nervous System** — All communication via ZeroMQ pub/sub
7. **Validation as Gatekeeper** — Input AND output validation, every request

---

## VRAM Budget (RTX 4060 8GB)

| Component | Params | VRAM (fp16) | Status |
|-----------|--------|-------------|--------|
| SARA (CognitionCore) | 54M | ~4.2 GB | Primary (always hot) |
| Router Model | ~3M | ~0.2 GB | Always hot |
| Active Specialist ×2 | ~30M | ~2.4 GB | Hot-swapped |
| BackupCore Pool (2) | ~20M | ~1.6 GB | Warm |
| FastResponderCore | ~5M | ~0.4 GB | Always hot |
| **Reserve/Overhead** | — | ~1.2 GB | Gradient, activations |
| **TOTAL** | **~112M** | **~8.0 GB** | **Fits** |

**Inactive specialists**: Offloaded to CPU RAM, 4-bit quantized, cold-load ~2-3s

---

## EventBus Topics (Complete)

### Core Lifecycle
- `CORE_STARTED(core_name, capabilities)`
- `CORE_HEARTBEAT(core_name, status, metrics)`
- `CORE_SHUTDOWN(core_name, reason)`

### Request Flow
- `USER_INPUT(payload)` → Orchestrator
- `SPECIALIST_REQUEST(request_id, domain, subdomain, prompt, context, priority)`
- `SPECIALIST_RESPONSE(request_id, domain, content, confidence, metadata)`
- `ORCHESTRATOR_SUMMATION(request_id, responses[], final_response)`

### Evolution Loop
- `EVOLUTION_TASK_GENERATED(task_id, domain, prompt, test_cases)`
- `EVOLUTION_REWARD(task_id, reward, components, metadata)`
- `EVOLUTION_CHECKPOINT(step, policy_loss, value_loss, metrics)`

### ParaCore (Supreme)
- `PARACORE_OVERRIDE(target_core, action, reason, priority)` — Supersedes ALL
- `PARACORE_OBSERVATION(event_stream_snapshot)`

### Backup Scaling
- `BACKUP_SCALE_REQUEST(target_count, reason)`
- `BACKUP_SPAWNED(backup_id, assumed_role)`
- `BACKUP_RETIRED(backup_id, reason)`

---

## File Structure (New)

```
Backend/
├── Core/
│   ├── ParaCore/                    # NEW
│   │   ├── ParaCore.py
│   │   ├── OmniscienceEngine.py
│   │   ├── InterventionEngine.py
│   │   ├── TriDevasKnowledge.py
│   │   ├── AuthorityPolicy.py
│   │   ├── training/
│   │   │   └── train_omniscience.py
│   │   └── checkpoints/
│   │       └── para_core.pt
│   │
│   ├── MainCore/
│   │   ├── HybridCore/              # REFACTORED: Always-on daemon
│   │   │   ├── HybridCore.py
│   │   │   ├── HeartbeatDaemon.py
│   │   │   ├── CoreArbiter.py
│   │   │   ├── ParaCoreLink.py
│   │   │   └── TriDevasState.py
│   │   ├── CognitionCore/           # SARA (FIXED)
│   │   ├── EvolutionCore/           # NEW: RL self-improvement
│   │   │   ├── EvolutionCore.py
│   │   │   ├── SandboxExecutor.py
│   │   │   ├── RewardEngine.py
│   │   │   ├── GRPOTrainer.py
│   │   │   ├── CodeGenerator.py
│   │   │   ├── BackupSpawner.py
│   │   │   ├── ExperienceBuffer.py
│   │   │   ├── CurriculumManager.py
│   │   │   └── checkpoints/
│   │   │       └── evolution_policy.pt
│   │   ├── OrchestratorCore/        # REFACTORED: Intent/Route/Summate
│   │   ├── MonitoringCore/          # REFACTORED: Proactive actor
│   │   ├── OptimizationCore/        # REFACTORED: Model/Proc optimizer
│   │   ├── ValidationCore/          # KEPT
│   │   └── FastResponderDispatcher/ # NEW
│   │
│   ├── SpecializedCore/             # RESTRUCTURED: 20 domains
│   │   ├── __init__.py              # SpecialistBase, Registry
│   │   ├── Coding/
│   │   │   ├── __init__.py
│   │   │   ├── CodingRouter/
│   │   │   ├── PythonCore/
│   │   │   ├── CppCore/
│   │   │   ├── RustCore/
│   │   │   ├── JavaScriptCore/
│   │   │   ├── GoCore/
│   │   │   ├── SQLCore/
│   │   │   ├── BashShellCore/
│   │   │   └── RegexCore/
│   │   ├── RealWorld/
│   │   │   ├── __init__.py
│   │   │   ├── RealWorldRouter/
│   │   │   ├── ExcelCore/
│   │   │   ├── WebScrapingCore/
│   │   │   ├── FileSystemCore/
│   │   │   ├── SystemAdminCore/
│   │   │   ├── KnowledgeCore/
│   │   │   ├── NetworkCore/
│   │   │   ├── DatabaseAdminCore/
│   │   │   ├── CloudCore/
│   │   │   └── SecurityCore/
│   │   ├── DataCore/                # KEPT
│   │   ├── AutomationCore/          # KEPT (moved here)
│   │   ├── DesignCore/              # KEPT
│   │   ├── ImageGenerationCore/     # KEPT
│   │   ├── VoiceCore/               # KEPT
│   │   ├── DistributionCore/        # KEPT
│   │   └── FastResponderCore/       # NEW
│   │
│   ├── BackupCore/                  # REFACTORED: Versatile pool
│   │   ├── BackupCore.py
│   │   ├── CapabilityRegistry.py
│   │   ├── RoleAdapter.py
│   │   ├── PoolManager.py
│   │   └── checkpoints/
│   │       └── backup_core.pt
│   │
│   └── EventBus/                    # EXTENDED
│       ├── Topics.py                # NEW topics added
│       ├── Events.py                # OverrideEvent, SpecialistEvent
│       └── EventBus.py
│
├── Plugins/
│   └── ToolRegistry/                # Specialist registration
│
└── EntryPoint.py                    # UPDATED: Core init order
```

---

## Implementation Phases

| Phase | Focus | Duration | Parallel Agents |
|-------|-------|----------|-----------------|
| **0** | Documentation Package | 1 week | 1 (this doc) |
| **1** | Env Fix + SARA Fix | 1-2 weeks | Agent B |
| **2** | Specialist Framework + Scraping | 2-3 weeks | Agents C, D |
| **3** | Specialist Training (all 20) | 4-6 weeks | Agents C, D |
| **4** | EvolutionCore + Monitoring | 2-3 weeks | Agent E |
| **5** | Core Refactors (Orchestrator, Hybrid, etc.) | 2-3 weeks | Agents A, F |
| **6** | BackupCore Pool + FastResponder | 1-2 weeks | Agent A |
| **7** | ParaCore (Omniscience + Intervention) | 1-2 weeks | Agent A |
| **8** | Integration + Frontend + Stress | 2 weeks | All |

---

## Critical Path

```
Tier 0: Shared/Constants.py → EventBus Topics → SpecialistBase → CapabilityRegistry → RoleAdapter → ParaCore TriDevasKnowledge
         ↓
Tier 1: ParaCore → BackupCore Pool → Specialist Framework → SARA Fixes
         ↓
Tier 2: Coding Specialists → RealWorld Specialists → FastResponder → HybridCore Daemon → Orchestrator Refactor
         ↓
Tier 3: Routers → EvolutionCore → Monitoring Proactive → Optimization ModelOptimizer
         ↓
Tier 4: Integration → Frontend → ParaCore Training → Stress Test
```

---

## Decision Log (Key Decisions)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Base Model Strategy | Shared 50M base → fine-tune specialists | Quality + speed, avoids 20× from-scratch |
| Corpus Generation | Hybrid: seed manual + synthetic (QLoRA) | Scale + accuracy |
| Router Approach | New IntentClassifier (domain+subdomain+confidence) | Existing Router only does task classification |
| VRAM Strategy | Hybrid: Router+2 hot, rest cold-load 4-bit | 8GB constraint, 2-3s cold-load acceptable |
| ParaCore Training | Online continuous (live EventBus) | True omniscience requires live visibility |
| RL Algorithm | GRPO (Group Relative Policy Optimization) | No critic, stable, group-relative rewards |
| BackupCore Design | Single model + RoleAdapter | Simpler, truly versatile |
| Tri-Devas Exposure | ParaCore logs ONLY | Security, architectural purity |

---

## Next Steps

1. **All agents read this document first**
2. **Agents read their assigned docs in `.agents/.opencode-notes/`**
3. **Agents read `13_INTERFACE_CONTRACTS.md` and `17_DEPENDENCY_GRAPH.md`**
4. **Agents create status files: `.agents/.opencode-notes/AGENT_[LETTER]_STATUS.md`**
5. **Begin Phase 1 implementation per dependency graph**

---

**End of Master Architecture Document**
