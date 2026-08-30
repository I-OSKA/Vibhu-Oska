# Vibhu-Oska SARA Training Pipeline

## Overview

This document describes the end-to-end training pipeline for Vibhu-Oska's SARA — a from-scratch decoder-only transformer trained entirely on local hardware with no cloud dependencies.

## Architecture

- **Model**: Custom causal transformer (RoPE, RMSNorm, SwiGLU, tied embeddings)
- **Tokenizer**: Custom BPE (SaraBPETokenizer) trained on local corpus
- **Checkpoint**: `Models/sara/checkpoints/sara.pt` (best loss)
- **Tokenizer vocab**: `Models/sara/checkpoints/tokenizer_vocab.json`
- **Corpus**: `Data/training/sara/corpus.txt` (append-safe, UTF-8)

## Phased Training Strategy

### Phase 3a: Sanity Run (`--test-run`)
```bash
python -m Models.sara.train --test-run --num-threads 12
```
- Tiny model: hidden=64, layers=2, heads=4, vocab=800, max_len=64
- 2 epochs, 1 batch each
- Validates: tokenizer → model → forward/backward → checkpoint save
- Completes in ~30s on CPU

### Phase 3b: Intermediate Model
```bash
python -m Models.sara.train --epochs 40 --batch 8 --hidden 256 --layers 6 --heads 4 --max-len 256 --vocab-size 4000 --num-threads 12
```
- Small usable model: 2.5M params
- ~26 min/epoch on CPU (8 threads), ~17 hours for 40 epochs
- Produces functional checkpoint for inference testing

### Phase 3c: Full SARA
```bash
python -m Models.sara.train --epochs 60 --batch 8 --hidden 512 --layers 12 --heads 8 --max-len 512 --vocab-size 8000 --num-threads 12
```
- Full config: 54M params
- ~26 min/epoch on CPU (12 threads), ~26 hours for 60 epochs
- Final production model for CognitionCore

## CLI Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--epochs` | 60 | Training epochs |
| `--batch` | 8 | Batch size |
| `--lr` | 3e-4 | Peak learning rate (OneCycleLR) |
| `--test-run` | false | Quick compile validation |
| `--hidden` | 512 | Hidden dimension |
| `--layers` | 12 | Transformer blocks |
| `--heads` | 8 | Attention heads |
| `--max-len` | 512 | Max sequence length |
| `--vocab-size` | 8000 | BPE target vocabulary |
| `--num-threads` | 0 | PyTorch CPU threads (0 = default) |

## Running Training

### Via CLI (direct)
```bash
cd Vibhu-Oska
python -m Models.sara.train --epochs 60 --num-threads 12
```

### Via API (dashboard)
```bash
curl -X POST http://127.0.0.1:8100/api/v1/model/train \
  -H "Content-Type: application/json" \
  -d '{"epochs":60,"batch_size":8,"learning_rate":"3e-4","hidden_dimension":512,"layers":12,"attention_heads":8,"vocab_size":8000,"device":"auto"}'
```
- Returns immediately: `{"status":"started","message":"Training has been initiated in background."}`
- Logs stream via WebSocket `/ws` → `system.model_training_log` events
- Dashboard polls `/api/v1/training/status` for status

### Background launch (Windows PowerShell)
```powershell
Start-Process -FilePath ".\.venv\Scripts\python.exe" `
  -ArgumentList "-m","Models.sara.train","--epochs","60","--num-threads","12" `
  -WorkingDirectory "." `
  -RedirectStandardOutput "logs\training.log" `
  -RedirectStandardError "logs\training.err" `
  -NoNewWindow -PassThru
```

## Checkpoint & Loading

### Checkpoint format (`sara.pt`)
```python
{
    "epoch": int,
    "model_state": dict,        # state_dict
    "config": dict,             # GPTConfig.__dict__
    "best_loss": float
}
```

### CognitionCore loading logic
```python
# In CognitionCore.load_sara()
ckpt_path = Path("Models/sara/checkpoints/sara.pt")
if ckpt_path.exists() and ckpt_path.stat().st_size > 1_000_000:
    checkpoint = torch.load(ckpt_path, map_location=device)
    # load model_state into VibhuOskaGPT(config)
else:
    # fall back to BackupCore
```

**Gate**: Only checkpoints > 1MB are loaded (filters out test-run artifacts).

## Corpus Management

- Location: `Data/training/sara/corpus.txt`
- Format: `Query: ...\nResponse: ...` blocks separated by blank lines
- **Append-safe**: `seed_default_corpus()` preserves existing file if size > 0
- **UTF-8 enforced**: `path.read_text(encoding="utf-8")` and `path.write_text(..., encoding="utf-8")`
- Add via API: `POST /api/v1/corpus/append` with `{"text": "...", "format": "qa"}`

## Expected Timelines (CPU, 12 threads)

| Phase | Params | Epochs | Time/epoch | Total |
|-------|--------|--------|------------|-------|
| 3a test-run | 182K | 2 | ~5s | ~30s |
| 3b intermediate | 2.5M | 40 | ~26 min | ~17 hrs |
| 3c full | 54M | 60 | ~26 min | ~26 hrs |

GPU (RTX 4060 8GB): ~10-15x faster with float16.

## Troubleshooting

### Port conflicts
- Gateway must run on 8100 for dashboard API/WS
- Kill stale uvicorn: `Stop-Process -Id $(Get-NetTCPConnection -LocalPort 8100).OwningProcess -Force`

### Duplicate training processes
- `python -m` spawns parent+child pair on Windows — **do not kill either**
- Check: `Get-CimInstance Win32_Process | Where CommandLine -like "*Models.sara*"`
- Only one training at a time (gate in `/api/v1/model/train`)

### OOM / memory
- Reduce `--batch` (min 1)
- Reduce `--max-len` (min 64)
- Use `--num-threads` ≤ physical cores

### Checkpoint not loading in CognitionCore
- Verify `sara.pt` > 1MB
- Check `tokenizer_vocab.json` exists alongside
- Ensure `GPTConfig` matches checkpoint config

### Tokenizer mojibake
- Fixed in train.py: explicit `encoding="utf-8"` on all file reads/writes
- Corpus must be valid UTF-8

## Monitoring

- **WebSocket**: `/ws` → `system.model_training_log` events
- **API status**: `GET /api/v1/training/status`
- **Logs**: `logs/training_3c.err` (stderr captures Python logging)

## Integration with CognitionCore

1. Training completes → `sara.pt` + `tokenizer_vocab.json` in checkpoints/
2. CognitionCore auto-detects on next request (or restart)
3. `load_sara()` loads model, tokenizer, moves to device
4. Requests route: HybridCore → CognitionCore → SARA
5. If model missing or < 1MB → falls back to BackupCore
