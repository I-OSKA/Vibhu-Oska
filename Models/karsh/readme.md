# Karsh — The Creative Intelligence (कर्ष)

Vibhu-Oska's own language model, built entirely from PyTorch primitives with no external inference APIs. A decoder-only transformer trained on project-specific Q&A pairs.

**Karsh (कर्ष)** = Sanskrit: to draw, attract, create; a name of **Vishnu**.
Runs inside **CognitionCore** — the reasoning engine of Vibhu-Oska AI-OS.

## Architecture

| Parameter | Value |
|---|---|
| Type | Decoder-only transformer (GPT-style) |
| Attention | Multi-Head Causal Self-Attention |
| Position encoding | RoPE (Rotary Positional Embeddings) |
| Feed-forward | SwiGLU activation (Llama-style) |
| Normalization | RMSNorm (Llama-style) |
| Default config | vocab=8000, hidden=512, 12 layers, 8 heads, max_seq=512 |
| Weight tying | `embedding.weight == lm_head.weight` |
| Tokenizer | Custom BPE (KarshBPETokenizer) |

## The Divine Framework

| Level | Hindu Concept | Vibhu-Oska | Role |
|-------|---------------|------------|------|
| Creator | Brahma | OrchestratorCore | Creates task flow, routes |
| Preserver | Vishnu | CognitionCore | Preserves knowledge, hosts Karsh |
| Transformer | Shiva | EvolutionCore | Destroys old, transforms via RL |
| Wisdom | Saraswati | MonitoringCore | Observes, records |
| Abundance | Lakshmi | OptimizationCore | Optimizes resources |
| Power | Parvati | Training Pipeline | Feeds evolution |
| **Creative Intelligence** | **Vishnu (Karsh)** | **Karsh Model** | **The generative mind** |

## Files

| File | Purpose |
|---|---|
| `architecture.py` | Full model definition: RMSNorm, RoPE, SwiGLU, GPT class |
| `tokenizer.py` | BPE tokenizer: training, encode/decode, save/load |
| `train.py` | AdamW + OneCycleLR training loop with corpus seeding |
| `generate.py` | `KarshGenerator`: load checkpoint + temperature sampling |

## Training

```bash
# Train with defaults
python -m Models.karsh.train

# Custom run
python -m Models.karsh.train --epochs 60 --batch-size 8 --lr 3e-4 --vocab-size 8000
```

**Training corpus**: `Data/training/karsh/corpus.txt`
The training script self-seeds the corpus with 200+ Q&A pairs covering Python, FastAPI, SQL, CSS, and Vibhu-Oska internals. Add domain-specific pairs to this file before training for better performance.

## Checkpoints

After training, checkpoints are saved to `checkpoints/`:
- `karsh.pt` — model weights + optimizer state + config
- `tokenizer_vocab.json` — BPE vocabulary and merge rules

## Inference

```python
from Models.karsh.generate import KarshGenerator
from pathlib import Path

gen = KarshGenerator(Path("Models/karsh/checkpoints"))
output = gen.generate("Query: What is Vibhu-Oska?\nResponse:", max_tokens=128, temperature=0.7)
print(output)
```

## Notes on Scale

The default configuration (512 hidden, 12 layers) produces a ~25M parameter model. When training data grows and VRAM allows, increase `hidden_size` to 768, `num_layers` to 16, and `vocab_size` to 16000 for significantly better quality. The architecture scales cleanly.
