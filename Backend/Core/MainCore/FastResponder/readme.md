# FastResponder — Hanuman (Instant Answers)

Deterministic instant response engine. Handles math, identity, greetings, and known patterns in milliseconds with zero model loading.

## Architecture

```mermaid
graph TB
    FR[FastResponder] --> RC[ResponseCache<br/>LRU Cache]
    FR --> PAT[Pattern Table<br/>Regex Matchers]

    PAT --> |"math"| MATH[Math Evaluator]
    PAT --> |"identity"| IDENTITY[Identity Responses]
    PAT --> |"greeting"| GREET[Greeting Responses]
    PAT --> |"system"| SYS[System Status]

    FR --> |"cache hit"| RC
    FR --> |"cache miss"| PAT
```

## Pattern Categories

| Category | Examples | Response Time |
|----------|----------|---------------|
| Math | `128 * 8`, `sqrt 144`, `is 97 prime?` | <1ms |
| Identity | `who are you`, `what is vibhu oska` | <1ms |
| Greetings | `hello`, `hi`, `good morning` | <1ms |
| System | `help`, `status`, `version` | <1ms |

## Files

| File | Purpose |
|------|---------|
| `FastResponder.py` | Pattern matching engine + cache integration |
| `ResponseCache.py` | LRU cache for repeated queries |

## Integration

FastResponder is the **primary fast path**. OrchestratorCore attempts FastResponder first:

```mermaid
graph LR
    P[User Prompt] --> FR{FastResponder}
    FR --> |"match"| R1[Instant Response]
    FR --> |"no match"| OC[OrchestratorCore]
    OC --> CC[CognitionCore]
    OC --> BC[BackupCore]
```
