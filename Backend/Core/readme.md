# Backend Core — The Intelligence Engine

The central intelligence layer of Vibhu-Oska AI-OS. All reasoning, memory, routing, and execution logic lives here.

## Architecture

```mermaid
graph TB
    subgraph "MainCore (Trimurti + Tools)"
        OC[OrchestratorCore<br/>Brahma — Creator]
        CC[CognitionCore<br/>Vishnu — Preserver]
        EC[EvolutionCore<br/>Shiva — Transformer]
        FR[FastResponder<br/>Hanuman — Instant]
        VC[ValidationCore<br/>Yama — Guard]
        MC[MonitoringCore<br/>Saraswati — Wisdom]
        OPT[OptimizationCore<br/>Lakshmi — Abundance]
    end

    subgraph "SpecializedCore (Domain Experts)"
        DC[DataCore<br/>Memory]
        AC[AutomationCore<br/>OS Exec]
        DES[DesignCore<br/>UI Gen]
        IG[ImageGenerationCore<br/>Image Gen]
        DIST[DistributionCore<br/>Stubvi]
        COD[CodingDomain<br/>9 Specialists]
        RW[RealWorldDomain<br/>10 Specialists]
    end

    subgraph "Infrastructure"
        BC[BackupCore<br/>CPU Contingency]
        EB[EventBus<br/>ZeroMQ]
        CM[ContextManager<br/>Token Budget]
        WD[Watchdog<br/>Health Monitor]
    end

    OC --> CC
    OC --> BC
    OC --> DC
    OC --> AC
    OC --> DES
    OC --> IG
    CC --> EC
    EC --> OPT
    MC --> EB
    EB --> OC
    EB --> CC
    EB --> EC
```

## Directory Structure

| Directory | Purpose |
|---|---|
| `MainCore/` | Trimurti (OrchestratorCore, CognitionCore, EvolutionCore) + supporting tools |
| `SpecializedCore/` | Domain-specific engines (DataCore, AutomationCore, 20 specialists) |
| `BackupCore/` | CPU-based contingency intelligence |
| `EventBus/` | ZeroMQ publish/subscribe inter-core messaging |
| `ContextManager/` | Token budget enforcement for inference |
| `Watchdog/` | Background health monitoring daemon |

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant G as Gateway
    participant O as OrchestratorCore
    participant V as ValidationCore
    participant D as DataCore
    participant C as CognitionCore
    participant B as BackupCore

    U->>G: WebSocket message
    G->>O: USER_INPUT event
    O->>V: Validate input
    V-->>O: Valid
    O->>D: Query context
    D-->>O: Context chunks
    O->>C: Generate response
    alt Primary healthy
        C-->>O: TaskResponse (GPU)
    else Primary failed
        C-->>O: RuntimeError
        O->>B: Contingency handover
        B-->>O: TaskResponse (CPU)
    end
    O->>V: Validate output
    V-->>O: Valid
    O->>D: Save interaction
    O-->>G: TASK_COMPLETED event
    G-->>U: Response
```
