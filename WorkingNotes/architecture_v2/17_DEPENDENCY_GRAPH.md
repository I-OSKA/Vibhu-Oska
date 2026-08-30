# Build Order Dependency Graph

## Overview

The Vibhu-Oska AI-OS must be built in a specific order to respect dependencies. This document defines the tiered build order, critical path, and parallel execution groups.

---

## Tier 0: Foundation Layer

**No dependencies. Build first.**

```
Shared/Constants.py          ─── Global constants, paths, config keys
Shared/EventBus.py           ─── Publish-subscribe event system
Shared/EventTypes.py         ─── Event type definitions
Shared/Utils/                ─── Common utility functions
SpecializedCore/SpecialistBase.py  ─── Base class for all specialists
SpecializedCore/CapabilityRegistry.py  ─── Specialist capability discovery
SpecializedCore/RoleAdapter.py    ─── Role-based specialist selection
```

### Tier 0 Parallel Group

All Tier 0 modules can be built simultaneously:

```
Group 0A: [Constants, EventBus, EventTypes, Utils]
Group 0B: [SpecialistBase, CapabilityRegistry, RoleAdapter]
```

**Estimated effort:** Low (1-2 days)  
**Risk:** Low (no external dependencies)

---

## Tier 1: Core Infrastructure

**Depends on:** Tier 0

```
ParaCore/                   ─── Parameter management and persistence
BackupCore/                 ─── Automated backup and restore
Models/sara/       ─── SARA model wrapper
Models/ModelRegistry.py     ─── Model loading and lifecycle
Models/TokenBudget.py       ─── VRAM/token budget management
SpecializedCore/DomainRegistry.py  ─── Domain registration system
```

### Tier 1 Parallel Group

```
Group 1A: [ParaCore, BackupCore]                    ── depends on: Constants, EventBus
Group 1B: [SaraGPT, ModelRegistry, TokenBudget]  ── depends on: Constants, EventBus
Group 1C: [DomainRegistry]                          ── depends on: SpecialistBase, CapabilityRegistry
```

**Estimated effort:** Medium (3-5 days)  
**Risk:** Medium (model loading requires GPU)

---

## Tier 2: Domain Specialists & Response Pipeline

**Depends on:** Tier 1

```
SpecializedCore/Coding/           ─── Code generation specialists
SpecializedCore/Coding/Scrapers/  ─── Code pattern scrapers
SpecializedCore/RealWorld/        ─── Real-world domain specialists
SpecializedCore/RealWorld/WebBridge/  ─── Web integration layer
SpecializedCore/RealWorld/APIBridge/  ─── External API connectors
FastResponderCore/                ─── Low-latency response pipeline
FastResponderCore/Cache/          ─── Response caching layer
Models/InferenceEngine.py         ─── Batched inference scheduler
CognitionCore/                    ─── Reasoning and thought pipeline
```

### Tier 2 Parallel Group

```
Group 2A: [Coding Specialists, Scrapers]             ── depends on: DomainRegistry, SpecialistBase
Group 2B: [RealWorld Specialists, WebBridge, APIBridge] ── depends on: DomainRegistry, SpecialistBase
Group 2C: [FastResponder, Cache]                     ── depends on: EventBus, Constants
Group 2D: [InferenceEngine, CognitionCore]           ── depends on: ModelRegistry, TokenBudget
```

**Estimated effort:** High (5-8 days)  
**Risk:** High (external API dependencies, complex inference)

---

## Tier 3: Orchestration, Evolution & Monitoring

**Depends on:** Tier 2

```
OrchestratorCore/               ─── Task routing and orchestration
OrchestratorCore/TaskRouter.py  ─── Request routing logic
OrchestratorCore/PriorityQueue.py  ─── Task priority management
ValidationCore/                 ─── Input/output validation
ValidationCore/ValidatorChain.py  ─── Chain of validators
EvolutionCore/                  ─── Self-evolution and learning
EvolutionCore/LearningLoop.py   ─── Continuous improvement
MonitoringCore/                 ─── System health and metrics
MonitoringCore/MetricsCollector.py  ─── Metric aggregation
MonitoringCore/AlertEngine.py   ─── Proactive alert system
```

### Tier 3 Parallel Group

```
Group 3A: [OrchestratorCore, TaskRouter, PriorityQueue]  ── depends on: Specialists, FastResponder
Group 3B: [ValidationCore, ValidatorChain]              ── depends on: Constants, EventBus
Group 3C: [EvolutionCore, LearningLoop]                 ── depends on: Constants, EventBus
Group 3D: [MonitoringCore, MetricsCollector, AlertEngine] ── depends on: Constants, EventBus
```

**Estimated effort:** Medium (4-6 days)  
**Risk:** Medium (complex routing logic)

---

## Tier 4: Integration, Automation & Frontend

**Depends on:** Tier 3

```
DataCore/                       ─── Data storage and retrieval
DataCore/Storage/               ─── Persistent storage layer
AutomationCore/                 ─── Workflow automation
AutomationCore/Workflows/       ─── Predefined workflows
DesignCore/                     ─── UI/UX design automation
Frontend/next_app/              ─── Next.js frontend application
Frontend/web_app/               ─── Flask web application
```

### Tier 4 Parallel Group

```
Group 4A: [DataCore, Storage, AutomationCore, Workflows, DesignCore]  ── depends on: OrchestratorCore, ValidationCore
Group 4B: [Next.js App]                                           ── depends on: FastResponder, OrchestratorCore
Group 4C: [Flask Web App]                                         ── depends on: FastResponder, OrchestratorCore
```

**Estimated effort:** Medium (3-5 days)  
**Risk:** Low (integration testing required)

---

## Tier 5: Integration Testing & Optimization

**Depends on:** Tier 4

```
Integration Tests               ─── End-to-end system tests
Performance Benchmarks          ─── System performance validation
ParaCore Training               ─── Parameter training pipeline
System Hardening                ─── Security and reliability fixes
```

### Tier 5 Parallel Group

```
Group 5A: [Integration Tests, Performance Benchmarks]  ── depends on: All Tier 4
Group 5B: [ParaCore Training]                        ── depends on: ParaCore, CognitionCore
Group 5C: [System Hardening]                         ── depends on: All modules
```

**Estimated effort:** High (5-7 days)  
**Risk:** Medium (finding integration issues)

---

## Critical Path

The critical path is the longest sequence of dependent tasks that determines minimum project duration:

```
Constants.py (T0)
  └─→ ModelRegistry.py (T1)
       └─→ SaraGPT (T1)
            └─→ InferenceEngine (T2)
                 └─→ CognitionCore (T2)
                      └─→ OrchestratorCore (T3)
                           └─→ Next.js App (T4)
                                └─→ Integration Tests (T5)
```

**Critical Path Duration:** ~25-35 days (estimated)  
**Critical Path Slack:** 0 days (any delay impacts delivery)

---

## Parallel Execution Summary

```
Day 1-2:    Tier 0 (Groups 0A, 0B)                    ── 2 parallel groups
Day 3-7:    Tier 1 (Groups 1A, 1B, 1C)                ── 3 parallel groups
Day 8-15:   Tier 2 (Groups 2A, 2B, 2C, 2D)           ── 4 parallel groups
Day 16-21:  Tier 3 (Groups 3A, 3B, 3C, 3D)           ── 4 parallel groups
Day 22-26:  Tier 4 (Groups 4A, 4B, 4C)                ── 3 parallel groups
Day 27-33:  Tier 5 (Groups 5A, 5B, 5C)                ── 3 parallel groups
```

---

## Dependency Matrix

| Module | Depends On | Required For |
|--------|------------|--------------|
| Constants.py | None | Everything |
| EventBus.py | Constants | Everything |
| SpecialistBase | Constants, EventBus | All specialists |
| CapabilityRegistry | SpecialistBase | DomainRegistry |
| RoleAdapter | SpecialistBase | OrchestratorCore |
| ParaCore | Constants, EventBus | BackupCore, Training |
| BackupCore | Constants, EventBus, ParaCore | System restore |
| ModelRegistry | Constants, EventBus | SaraGPT, InferenceEngine |
| SaraGPT | ModelRegistry, TokenBudget | CognitionCore |
| InferenceEngine | ModelRegistry, TokenBudget | FastResponder |
| DomainRegistry | SpecialistBase, CapabilityRegistry | All domain specialists |
| Coding Specialists | DomainRegistry | OrchestratorCore |
| RealWorld Specialists | DomainRegistry | OrchestratorCore |
| FastResponder | EventBus, InferenceEngine | OrchestratorCore, Frontend |
| CognitionCore | SaraGPT | OrchestratorCore |
| OrchestratorCore | Specialists, FastResponder, CognitionCore | Frontend, AutomationCore |
| ValidationCore | Constants, EventBus | OrchestratorCore |
| EvolutionCore | Constants, EventBus | MonitoringCore |
| MonitoringCore | Constants, EventBus, EvolutionCore | AlertEngine |
| DataCore | OrchestratorCore, ValidationCore | AutomationCore |
| AutomationCore | OrchestratorCore, ValidationCore | Frontend |
| Frontend | FastResponder, OrchestratorCore | User interface |

---

## Risk Areas

| Risk | Impact | Mitigation |
|------|--------|------------|
| Model loading fails | Blocks Tier 2, 3 | Fallback to CPU, mock models |
| External API downtime | Blocks RealWorld specialists | Cache responses, retry logic |
| VRAM exhaustion | Blocks inference | TokenBudget limits, model swapping |
| Integration failures | Blocks Tier 5 | Continuous integration testing |
| Frontend build errors | Blocks deployment | Separate build pipeline |

---

## Build Commands

```bash
# Tier 0
python -c "from Shared.Constants import *; print('Tier 0 OK')"
python -c "from Shared.EventBus import EventBus; print('EventBus OK')"

# Tier 1
python -c "from ParaCore import ParaCore; print('ParaCore OK')"
python -c "from Models.ModelRegistry import ModelRegistry; print('ModelRegistry OK')"

# Tier 2
python -c "from SpecializedCore.Coding import CodingSpecialist; print('Coding OK')"
python -c "from FastResponderCore import FastResponder; print('FastResponder OK')"

# Tier 3
python -c "from OrchestratorCore import Orchestrator; print('Orchestrator OK')"
python -c "from MonitoringCore import Monitor; print('Monitor OK')"

# Tier 4
python -c "from DataCore import DataCore; print('DataCore OK')"
cd Frontend/next_app && npm run build

# Tier 5
python -m pytest tests/integration/ -v
```
