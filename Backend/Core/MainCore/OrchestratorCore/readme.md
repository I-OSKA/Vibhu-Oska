# OrchestratorCore — Brahma (The Creator)

The tactical request lifecycle manager. Absorbs HybridCore routing. Drives the 8-step processing pipeline without containing business logic.

## Responsibility

OrchestratorCore receives user input events from the ZeroMQ EventBus and drives the processing pipeline to completion. It routes requests, manages primary/backup handover, and coordinates all cores.

## The 8-Step Pipeline

```mermaid
graph LR
    A[1. ValidationCore<br/>Input guard] --> B[2. OptimizationCore<br/>Cache check]
    B --> C[3. DataCore<br/>Create session]
    C --> D[4. DataCore<br/>Context retrieval]
    D --> E[5. OptimizationCore<br/>Context pruning]
    E --> F[6. SpecializedCore<br/>Pre-routing]
    F --> G[7. OrchestratorCore<br/>Primary routing]
    G --> H[8. ValidationCore<br/>Output guard]
```

## Routing Architecture (Absorbed from HybridCore)

```mermaid
graph TB
    P[User Prompt] --> FR{FastResponder}
    FR --> |"match"| IR[Instant Response]
    FR --> |"no match"| OC[OrchestratorCore]
    OC --> SP{Specialized<br/>Router}
    SP --> |"image"| IG[ImageGenerationCore]
    SP --> |"design"| DES[DesignCore]
    SP --> |"OS"| AC[AutomationCore]
    SP --> |"default"| ROUTE{Primary<br/>Routing}
    ROUTE --> |"GPU"| CC[CognitionCore<br/>Karsh]
    ROUTE --> |"fault/timeout"| BC[BackupCore<br/>CPU]
    ROUTE --> |"capacity"| BC
```

## Specialized Core Pre-routing

Before reaching the primary routing path, the orchestrator runs a keyword classifier:

| Trigger keywords | Routed to |
|---|---|
| `generate image`, `draw`, `paint` | ImageGenerationCore |
| `design`, `layout`, `html` | DesignCore |
| `list files`, `run command`, `cpu usage` | AutomationCore |

## Contingency Protocol

| Trigger | Action |
|---------|--------|
| Primary fault | BackupCore takes over, status → DEGRADED |
| Primary timeout (60s) | BackupCore takes over, status → DEGRADED |
| Primary at capacity (2 concurrent) | BackupCore takes over, status stays HEALTHY |
| Explicit `backup-1` | Direct BackupCore handover |

## Key File

`OrchestratorCore.py` — Main orchestrator with absorbed routing logic
