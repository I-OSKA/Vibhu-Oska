# CognitionCore — Vishnu (Sthiti/Preservation)

## Role
Primary LLM inference engine. Runs the Karsh model for response generation.

## Architecture

```
CognitionCore
├── generate()               → Standard inference
├── deep_thought_generate()  → MCTS-style multi-path reflection
├── KarshModel               → Custom transformer (from scratch)
└── CorpusSpellChecker       → Local spell correction
```

## Karsh Model

- Custom transformer built from scratch (no external models)
- Trained on 1200+ Q&A pairs (Hindi, English, Sanskrit, coding)
- Hardware: RTX 4060 (8GB VRAM), ~25 min training
- Architecture: Decoder-only transformer with rotary embeddings

## DeepThought Mode

When activated for complex queries, CognitionCore runs a multi-path reflection loop:

1. **Expand** — Generate N candidate reasoning paths
2. **Simulate** — Evaluate each path's plausibility
3. **Backpropagate** — Update path scores based on evaluation
4. **Select** — Choose best path via UCB1 exploration
5. **Respond** — Generate final answer from best path

This is integrated INTO CognitionCore (not a separate core) because it's a reasoning strategy, not a distinct capability.

## Modes

| Mode | Use Case | Latency |
|------|----------|---------|
| Standard | Most queries | Fast |
| DeepThought | Complex reasoning | Slower, more thorough |
| Cached | Repeated queries | Instant |

## Training

```bash
python -m Models.karsh.train
```

60 epochs, ~25 minutes on RTX 4060.
