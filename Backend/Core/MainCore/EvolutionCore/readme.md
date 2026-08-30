# EvolutionCore — Shiva (The Transformer)

The self-improvement engine. Destroys old patterns and transforms the system through reinforcement learning feedback.

## Architecture

```mermaid
graph TB
    EC[EvolutionCore] --> GRPO[GRPO<br/>Group Relative Policy Optimization]
    EC --> RE[RewardEngine<br/>Reward Scoring]
    EC --> SE[SandboxExecutor<br/>Safe Execution]
    EC --> BS[BackupSpawner<br/>Model Variants]

    GRPO --> |"policy update"| MODEL[Model Weights]
    RE --> |"reward signal"| GRPO
    SE --> |"test execution"| RE
    BS --> |"spawn variant"| SE

    EC --> |"training data"| PT[Parvati<br/>Training Pipeline]
    EC --> |"optimize"| OPT[OptimizationCore<br/>Lakshmi]
```

## Components

| File | Purpose |
|------|---------|
| `EvolutionCore.py` | Main orchestrator for self-improvement cycles |
| `GRPO.py` | Group Relative Policy Optimization algorithm |
| `RewardEngine.py` | Scores response quality for RL feedback |
| `SandboxExecutor.py` | Safely executes code variants in isolation |
| `BackupSpawner.py` | Creates model weight variants for exploration |

## Evolution Cycle

```mermaid
sequenceDiagram
    participant EC as EvolutionCore
    participant RE as RewardEngine
    participant GR as GRPO
    participant SE as SandboxExecutor

    EC->>SE: Execute code variant
    SE-->>EC: Result
    EC->>RE: Score response quality
    RE-->>EC: Reward signal
    EC->>GR: Update policy
    GR-->>EC: Updated weights
    EC->>EC: Validate improvement
```
