# Agent Assignment Map

## Overview

Each agent owns a specific domain of the Vibhu-Oska AI-OS codebase. Agents coordinate through the EventBus and status files located at `.agents/.opencode-notes/`.

---

## Agent A: Foundation & ParaCore

**Owner:** Agent A  
**Domain:** Shared infrastructure, event bus, parameter core, backup systems

### File Ownership

| Module | Path | Description |
|--------|------|-------------|
| Constants | `Shared/Constants.py` | Global constants, paths, config keys |
| EventBus | `Shared/EventBus.py` | Publish-subscribe event system |
| EventTypes | `Shared/EventTypes.py` | Event type definitions |
| ParaCore | `ParaCore/` | Parameter management and persistence |
| BackupCore | `BackupCore/` | Automated backup and restore |
| SharedUtils | `Shared/Utils/` | Common utility functions |

### Status File Format

```
Agent-A-Status.md:
  - Last Updated: <timestamp>
  - Current Task: <task description>
  - Completion: <percentage>
  - Blockers: <list>
  - Ready for Integration: <yes/no>
```

### Coordination Protocol

- Publishes events: `PARAM_CHANGED`, `BACKUP_COMPLETE`, `CONSTANTS_UPDATED`
- Subscribes to: `AGENT_REQUEST_PARAMS`, `SYSTEM_RESTORE`
- Provides: `get_param()`, `set_param()`, `emit()`, `subscribe()`
- Dependencies: None (Tier 0)

---

## Agent B: SARA & CognitionCore

**Owner:** Agent B  
**Domain:** LLM integration, model management, cognition pipeline

### File Ownership

| Module | Path | Description |
|--------|------|-------------|
| SaraGPT | `Models/sara/` | SARA model wrapper |
| CognitionCore | `CognitionCore/` | Reasoning and thought pipeline |
| ModelRegistry | `Models/ModelRegistry.py` | Model loading and lifecycle |
| TokenBudget | `Models/TokenBudget.py` | VRAM/token budget management |
| InferenceEngine | `Models/InferenceEngine.py` | Batched inference scheduler |

### Status File Format

```
Agent-B-Status.md:
  - Last Updated: <timestamp>
  - Current Task: <task description>
  - Model Status: <loaded/unloaded/error>
  - VRAM Usage: <current>/<max>
  - Completion: <percentage>
  - Blockers: <list>
```

### Coordination Protocol

- Publishes events: `MODEL_LOADED`, `INFERENCE_COMPLETE`, `VRAM_ALERT`
- Subscribes to: `REQUEST_INFERENCE`, `AGENT_REQUEST_PARAMS`, `CONSTANTS_UPDATED`
- Provides: `infer()`, `load_model()`, `unload_model()`, `get_cognition()`
- Dependencies: Tier 0 (Constants, EventBus)

---

## Agent C: Specialist Framework & Coding Domains

**Owner:** Agent C  
**Domain:** Specialist architecture, coding-specific specialists, scrapers

### File Ownership

| Module | Path | Description |
|--------|------|-------------|
| SpecialistBase | `SpecializedCore/SpecialistBase.py` | Base class for all specialists |
| CapabilityRegistry | `SpecializedCore/CapabilityRegistry.py` | Specialist capability discovery |
| RoleAdapter | `SpecializedCore/RoleAdapter.py` | Role-based specialist selection |
| CodingCore | `SpecializedCore/Coding/` | Code generation specialists |
| Scrapers | `SpecializedCore/Coding/Scrapers/` | Code pattern scrapers |
| DomainRegistry | `SpecializedCore/DomainRegistry.py` | Domain registration system |

### Status File Format

```
Agent-C-Status.md:
  - Last Updated: <timestamp>
  - Current Task: <task description>
  - Specialists Registered: <count>
  - Active Domains: <list>
  - Completion: <percentage>
  - Blockers: <list>
```

### Coordination Protocol

- Publishes events: `SPECIALIST_REGISTERED`, `DOMAIN_AVAILABLE`, `CAPABILITY_ADDED`
- Subscribes to: `REQUEST_SPECIALIST`, `CONSTANTS_UPDATED`
- Provides: `register_specialist()`, `get_specialist()`, `list_capabilities()`
- Dependencies: Tier 0 (Constants, EventBus)

---

## Agent D: RealWorld Domains & FastResponder

**Owner:** Agent D  
**Domain:** Real-world integrations, fast response system

### File Ownership

| Module | Path | Description |
|--------|------|-------------|
| RealWorldCore | `SpecializedCore/RealWorld/` | Real-world domain specialists |
| FastResponder | `FastResponderCore/` | Low-latency response pipeline |
| WebBridge | `SpecializedCore/RealWorld/WebBridge/` | Web integration layer |
| APIBridge | `SpecializedCore/RealWorld/APIBridge/` | External API connectors |
| ResponseCache | `FastResponderCore/Cache/` | Response caching layer |

### Status File Format

```
Agent-D-Status.md:
  - Last Updated: <timestamp>
  - Current Task: <task description>
  - FastResponder Status: <active/inactive>
  - Cache Hit Rate: <percentage>
  - Completion: <percentage>
  - Blockers: <list>
```

### Coordination Protocol

- Publishes events: `FAST_RESPONSE`, `DOMAIN_CONNECTED`, `API_CALL_COMPLETE`
- Subscribes to: `REQUEST_FAST_RESPONSE`, `REQUEST_SPECIALIST`, `CONSTANTS_UPDATED`
- Provides: `fast_respond()`, `connect_domain()`, `query_api()`
- Dependencies: Tier 0 (Constants, EventBus, SpecialistBase)

---

## Agent E: EvolutionCore & MonitoringCore

**Owner:** Agent E  
**Domain:** Self-improvement, health monitoring, proactive alerts

### File Ownership

| Module | Path | Description |
|--------|------|-------------|
| EvolutionCore | `EvolutionCore/` | Self-evolution and learning |
| MonitoringCore | `MonitoringCore/` | System health and metrics |
| MetricsCollector | `MonitoringCore/MetricsCollector.py` | Metric aggregation |
| AlertEngine | `MonitoringCore/AlertEngine.py` | Proactive alert system |
| LearningLoop | `EvolutionCore/LearningLoop.py` | Continuous improvement |

### Status File Format

```
Agent-E-Status.md:
  - Last Updated: <timestamp>
  - Current Task: <task description>
  - System Health: <healthy/degraded/critical>
  - Evolution Status: <active/paused>
  - Completion: <percentage>
  - Blockers: <list>
```

### Coordination Protocol

- Publishes events: `HEALTH_ALERT`, `EVOLUTION_COMPLETE`, `METRIC_THRESHOLD`
- Subscribes to: `SYSTEM_HEARTBEAT`, `CONSTANTS_UPDATED`, `AGENT_REQUEST_PARAMS`
- Provides: `get_health()`, `get_metrics()`, `trigger_evolution()`
- Dependencies: Tier 1 (Constants, EventBus)

---

## Agent F: OrchestratorCore & ValidationCore

**Owner:** Agent F  
**Domain:** Task orchestration, validation pipelines

### File Ownership

| Module | Path | Description |
|--------|------|-------------|
| OrchestratorCore | `OrchestratorCore/` | Task routing and orchestration |
| ValidationCore | `ValidationCore/` | Input/output validation |
| TaskRouter | `OrchestratorCore/TaskRouter.py` | Request routing logic |
| ValidatorChain | `ValidationCore/ValidatorChain.py` | Chain of validators |
| PriorityQueue | `OrchestratorCore/PriorityQueue.py` | Task priority management |

### Status File Format

```
Agent-F-Status.md:
  - Last Updated: <timestamp>
  - Current Task: <task description>
  - Active Tasks: <count>
  - Validation Pass Rate: <percentage>
  - Completion: <percentage>
  - Blockers: <list>
```

### Coordination Protocol

- Publishes events: `TASK_ROUTED`, `VALIDATION_PASSED`, `VALIDATION_FAILED`
- Subscribes to: `REQUEST_TASK`, `CONSTANTS_UPDATED`
- Provides: `route_task()`, `validate()`, `queue_task()`
- Dependencies: Tier 0 (Constants, EventBus, SpecialistBase)

---

## Agent G: DataCore & AutomationCore

**Owner:** Agent G  
**Domain:** Data management, automation pipelines, design

### File Ownership

| Module | Path | Description |
|--------|------|-------------|
| DataCore | `DataCore/` | Data storage and retrieval |
| AutomationCore | `AutomationCore/` | Workflow automation |
| DesignCore | `DesignCore/` | UI/UX design automation |
| AutomationCore/Workflows | `AutomationCore/Workflows/` | Predefined workflows |
| DataCore/Storage | `DataCore/Storage/` | Persistent storage layer |

### Status File Format

```
Agent-G-Status.md:
  - Last Updated: <timestamp>
  - Current Task: <task description>
  - Active Workflows: <count>
  - Storage Status: <healthy/full/error>
  - Completion: <percentage>
  - Blockers: <list>
```

### Coordination Protocol

- Publishes events: `WORKFLOW_COMPLETE`, `DATA_SAVED`, `DESIGN_GENERATED`
- Subscribes to: `REQUEST_DATA`, `REQUEST_AUTOMATION`, `CONSTANTS_UPDATED`
- Provides: `save_data()`, `run_workflow()`, `generate_design()`
- Dependencies: Tier 0 (Constants, EventBus)

---

## Agent H: Frontend Integration

**Owner:** Agent H  
**Domain:** Web interfaces, Next.js app, Flask web app

### File Ownership

| Module | Path | Description |
|--------|------|-------------|
| NextApp | `Frontend/next_app/` | Next.js frontend application |
| WebApp | `Frontend/web_app/` | Flask web application |
| UIComponents | `Frontend/components/` | Shared UI components |
| APIRoutes | `Frontend/api/` | Frontend API routes |
| StaticAssets | `Frontend/static/` | Static files and assets |

### Status File Format

```
Agent-H-Status.md:
  - Last Updated: <timestamp>
  - Current Task: <task description>
  - Build Status: <passing/failing>
  - Deploy Status: <ready/pending>
  - Completion: <percentage>
  - Blockers: <list>
```

### Coordination Protocol

- Publishes events: `UI_UPDATED`, `USER_INTERACTION`, `BUILD_COMPLETE`
- Subscribes to: `FAST_RESPONSE`, `TASK_ROUTED`, `CONSTANTS_UPDATED`
- Provides: `render_ui()`, `handle_input()`, `deploy()`
- Dependencies: Tier 4 (all backend modules)

---

## Cross-Agent Communication Matrix

```
Agent A ──→ EventBus ──→ All Agents
Agent B ──→ Agent A (params), Agent F (routing)
Agent C ──→ Agent A (constants), Agent F (routing)
Agent D ──→ Agent A (constants), Agent C (specialists), Agent F (routing)
Agent E ──→ Agent A (params), monitors all
Agent F ──→ Agent A (constants), routes to B/C/D/G
Agent G ──→ Agent A (constants), Agent F (routing)
Agent H ──→ Agent D (fast response), Agent F (routing), Agent B (inference)
```

## Status File Location

All status files are stored at:
```
.agents/.opencode-notes/Agent-{A-H}-Status.md
```

## Conflict Resolution

1. **Shared files** (Constants.py, EventBus): Agent A owns; others submit PRs
2. **Event naming**: Prefix with domain (`CODING_*`, `REALWORLD_*`, etc.)
3. **Priority conflicts**: Agent F arbitrates via OrchestratorCore
4. **Resource contention**: Agent E monitors and alerts; Agent A adjusts budgets
