# CognitionCore — Vishnu (The Preserver)

The primary LLM reasoning interface. CognitionCore is the only module permitted to perform inference — nothing outside this file calls model weights directly.

## Responsibility

Accept a prompt + context, route to Karsh (the custom LLM), return a `TaskResponse`.

## Inference Hierarchy

```
1. Karsh        (if Models/karsh/checkpoints/karsh.pt exists)
   ↓ fails
2. Exception raised → OrchestratorCore catches → BackupCore CPU rules
```

## Explicit Model Routing

Pass `model_id` to bypass auto-selection:

| model_id | Routes to |
|---|---|
| `karsh` | Karsh custom checkpoint |
| `backup-1` | Handled by OrchestratorCore → BackupCore |
| `""` (empty) | Auto-fallback chain (default) |

## Corpus Spell Checker

CognitionCore includes a Norvig-style spell checker trained on the local corpus (`Data/training/karsh/corpus.txt`). If a typo is detected in the user prompt, the system prompt is modified to instruct the model to acknowledge and correct the typo before answering.

## Module Boundary Rules

- **No DB connections** — never touches ChromaDB or SQLite directly
- **No I/O scripts** — no file reads/writes except loading model weights on startup
- **No event bus calls** — inference is synchronous from the orchestrator's perspective

## Key File

`cognition.py` — 433 lines

## Classes

| Class | Purpose |
|---|---|
| `CorpusSpellChecker` | Norvig probabilistic spell correction seeded with project corpus |
| `CognitionCore` | Main inference interface implementing `BaseService` |

## Methods

| Method | Description |
|---|---|
| `generate()` | Main entry point — auto-routes based on model_id |
| `generate_karsh()` | Runs Karsh from local checkpoints |

## DeepThought Sub-Module

CognitionCore includes a `DeepThought/` sub-module for complex reasoning:

```
CognitionCore/
├── cognition.py            ← Main inference
├── DeepThought/
│   ├── __init__.py
│   └── DeepThoughtEngine.py ← MCTS-style reflection
└── readme.md
```

### When to Use DeepThought

| Query Type | Mode | Latency |
|------------|------|---------|
| Simple factual | Standard | Fast |
| Complex reasoning | DeepThought | Slower |
| Multi-step analysis | DeepThought | Slower |
| Creative generation | Standard | Fast |

### How It Works

1. **Generate** — Create N candidate reasoning paths
2. **Evaluate** — Score each path (context use, coherence, completeness)
3. **Select** — UCB1 exploration picks best path
4. **Expand** — Refine best path with additional reasoning
5. **Respond** — Return final answer from best path

### Integration

DeepThought is invoked by CognitionCore when `mode="deep_thought"` is passed to `generate()`. It's not a separate core — it's a reasoning strategy within CognitionCore.
