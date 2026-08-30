# Vibhu-Oska AI-OS — Training Pipeline Documentation

**Version**: 2.0  
**Status**: Phase 0 — Documentation Complete  
**Authority**: EvolutionCore (Destroyer) → Training Execution

---

## Overview

This document defines the complete end-to-end training pipeline for all models in the Vibhu-Oska system. The pipeline is designed as **15-minute executable sets** to enable parallel agent execution and incremental progress tracking.

---

## Current State Assessment

| Component | Status | Issue |
|-----------|--------|-------|
| **SARA** (CognitionCore) | ❌ Failed | NaN loss from epoch 1, 0% accuracy, corrupted checkpoint |
| **Router Model** | ⚠️ Exists | Task classification only, needs domain+subdomain intent classifier |
| **QLoRA Finetune** | ⚠️ Exists | Models/reasoning/finetune.py — for synthetic corpus generation |
| **SARA Corpus** | ⚠️ Small | 230 pairs × 3 = 684 sequences (need 5,000+ per specialist) |
| **Router Corpus** | ✅ Ready | 123K train / 13K val samples |
| **Specialist Corpora** | ❌ Missing | 20 domains × 0 pairs = 0 |
| **Documentation** | ✅ Partial | 3/20 docs complete |

---

## Phase 0: Foundation (Week 1) — 15-Min Sets

### Set 0.1: Environment & Dependencies ⏱️15min
```bash
# Fix NumPy/PyTorch compatibility (CRITICAL - was causing NaN)
pip install --upgrade numpy==1.26.4

# PyTorch with CUDA 12.1 for RTX 4060
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Training acceleration & quantization
pip install accelerate bitsandbytes peft transformers datasets sentencepiece

# AutomationCore dependencies
pip install psutil pyautogui pygetwindow Pillow
```

### Set 0.2: Directory Scaffolding ⏱️15min
```bash
# ParaCore
mkdir -p Backend/Core/ParaCore/{training,checkpoints}

# EvolutionCore
mkdir -p Backend/Core/MainCore/EvolutionCore/{checkpoints,sandbox_logs}

# SpecializedCore - Coding Domain (10)
mkdir -p Backend/Core/SpecializedCore/Coding/{PythonCore,CppCore,RustCore,JavaScriptCore,GoCore,SQLCore,BashShellCore,RegexCore,CodingRouter}/{corpus,checkpoints}

# SpecializedCore - RealWorld Domain (10)
mkdir -p Backend/Core/SpecializedCore/RealWorld/{ExcelCore,WebScrapingCore,FileSystemCore,SystemAdminCore,KnowledgeCore,NetworkCore,DatabaseAdminCore,CloudCore,SecurityCore,RealWorldRouter}/{corpus,checkpoints}

# FastResponderCore
mkdir -p Backend/Core/SpecializedCore/FastResponderCore/{corpus,checkpoints}

# BackupCore Pool
mkdir -p Backend/Core/BackupCore/checkpoints

# Documentation directories
mkdir -p .agents/.opencode-notes
mkdir -p WorkingNotes/architecture_v2
```

### Set 0.3: Base Classes & Constants ⏱️15min

**Files to create:**

1. `Shared/Constants.py` — TriDevasRole enum, CoreAuthority enum, VRAM budgets
2. `Backend/Core/SpecializedCore/__init__.py` — SpecialistBase abstract class, SPECIALIST_REGISTRY
3. `Backend/Core/BackupCore/CapabilityRegistry.py` — Shared function/class registry
4. `Backend/Core/BackupCore/RoleAdapter.py` — Dynamic role assumption logic
5. `Backend/Core/ParaCore/TriDevasKnowledge.py` — Internal Tri-Devas logging (ParaCore only)

**Shared/Constants.py:**
```python
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

class TriDevasRole(Enum):
    CREATOR = "hybrid_core"      # Heart — HybridCore
    BALANCER = "cognition_core"  # Mind — CognitionCore
    DESTROYER = "evolution_core" # Soul — EvolutionCore

class CoreAuthority(Enum):
    PARACORE = 0      # Supreme
    HYBRIDCORE = 1    # Creator/Heart
    COGNITIONCORE = 2 # Balancer/Mind
    EVOLUTIONCORE = 3 # Destroyer/Soul
    ORCHESTRATORCORE = 4
    MONITORINGCORE = 5
    OPTIMIZATIONCORE = 6
    VALIDATIONCORE = 7
    SPECIALIST = 8
    BACKUPCORE = 9
    FASTRESPONDER = 10

@dataclass
class VRAMBudget:
    # RTX 4060 8GB allocation
    sara_MB: int = 4200      # 54M params fp16
    ROUTER_MB: int = 200              # 3M params
    ACTIVE_SPECIALISTS_MB: int = 2400 # 2 × 15M params
    BACKUP_POOL_MB: int = 1600        # 2 × 10M params
    FAST_RESPONDER_MB: int = 400      # 5M params
    RESERVE_MB: int = 1200            # Gradients, activations
    TOTAL_MB: int = 8000
    
    # 4-bit quantized sizes for cold storage
    COLD_SPECIALIST_MB: int = 300     # 15M params 4-bit
    COLD_BACKUP_MB: int = 200         # 10M params 4-bit
```

### Set 0.4: EventBus Extensions ⏱️15min

**Modify:**
- `Backend/Core/EventBus/Topics.py` — Add new topics
- `Backend/Core/EventBus/Events.py` — Add new event classes

**New Topics:**
```python
# Core Lifecycle
CORE_STARTED = "core.started"
CORE_HEARTBEAT = "core.heartbeat"
CORE_SHUTDOWN = "core.shutdown"

# Request Flow
USER_INPUT = "user.input"
SPECIALIST_REQUEST = "specialist.request"
SPECIALIST_RESPONSE = "specialist.response"
ORCHESTRATOR_SUMMATION = "orchestrator.summation"

# Evolution Loop
EVOLUTION_TASK_GENERATED = "evolution.task.generated"
EVOLUTION_REWARD = "evolution.reward"
EVOLUTION_CHECKPOINT = "evolution.checkpoint"

# ParaCore (Supreme)
PARACORE_OVERRIDE = "paracore.override"
PARACORE_OBSERVATION = "paracore.observation"

# Backup Scaling
BACKUP_SCALE_REQUEST = "backup.scale.request"
BACKUP_SPAWNED = "backup.spawned"
BACKUP_RETIRED = "backup.retired"
```

---

## Phase 1: SARA Fix (Week 1-2) — 15-Min Sets

### Set 1.1: NaN Guards in train.py ⏱️15min

**Edit:** `Models/sara/train.py` (after loss computation, ~line 378)

```python
# Add NaN/Inf detection with emergency checkpoint
if torch.isnan(loss) or torch.isinf(loss):
    notify(f"[ERROR] NaN/Inf loss at epoch {epoch}, step {step}. Aborting.")
    # Save emergency checkpoint for debugging
    torch.save({
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "epoch": epoch,
        "step": step,
        "loss": float(loss) if not torch.isnan(loss) else "NaN",
        "nan_detected": True
    }, output_dir / "sara_nan_emergency.pt")
    break

# Reduce gradient clipping from 1.0 to 0.5
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
```

### Set 1.2: FP32 Master Params + Gradient Scaler ⏱️15min

**Edit:** `Models/sara/train.py` — In `train()` function

```python
# After model.to(dev) (~line 338)
use_amp = dev.type == "cuda"
scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

# In training loop, replace lines 377-384:
with torch.cuda.amp.autocast(enabled=use_amp):
    out = model(input_ids=input_ids, labels=labels)
    loss = out["loss"]

optimizer.zero_grad()
scaler.scale(loss).backward()
scaler.unscale_(optimizer)
torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
scaler.step(optimizer)
scaler.update()
scheduler.step()
```

### Set 1.3: Lower LR + Curriculum Learning Args ⏱️15min

**Edit:** `Models/sara/train.py` — Default arguments

```python
parser.add_argument("--lr", type=float, default=1e-4)  # Was 3e-4
parser.add_argument("--warmup-epochs", type=int, default=5)
parser.add_argument("--max-seq-len-schedule", type=str, default="128,256,512")
parser.add_argument("--gradient-accumulation-steps", type=int, default=4)
```

### Set 1.4: Curriculum Implementation ⏱️15min

**Edit:** In `train()` function, add epoch-based sequence length schedule:

```python
# Parse curriculum schedule
seq_schedule = [int(x) for x in args.max_seq_len_schedule.split(",")]
schedule_epochs = args.epochs // len(seq_schedule)

# At start of each epoch:
current_schedule_idx = min(epoch // schedule_epochs, len(seq_schedule) - 1)
current_max_len = seq_schedule[current_schedule_idx]

# Re-create DataLoader if sequence length changed
if current_max_len != getattr(train_loader.dataset, 'max_seq_len', None):
    train_dataset = SaraGPTDataset(corpus_path, max_seq_len=current_max_len)
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
```

### Set 1.5: Test Run Validation ⏱️15min

```bash
# Quick test (2 epochs, validate no NaN)
python -m Models.sara.train --test-run --epochs 2 --batch-size 4

# Expected: loss finite, accuracy > 0%, no NaN warnings
```

### Set 1.6: Full Training Run ⏱️15min × N

```bash
# Production run (early-stops ~epoch 15-20)
python -m Models.sara.train \
    --epochs 60 \
    --batch-size 8 \
    --lr 1e-4 \
    --warmup-epochs 5 \
    --max-seq-len-schedule "128,256,512" \
    --gradient-accumulation-steps 4

# Monitor: logs/training_sara.log for finite loss, improving accuracy
# Target: loss < 2.0, accuracy > 80%, perplexity < 10
```

---

## Phase 2: Data Scraping & Corpus Generation (Week 2-3) — 15-Min Sets

### Set 2.1: Universal Scraper Base ⏱️15min

**Create:** `Scripts/scrapers/base_scraper.py`

```python
import asyncio
import aiohttp
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any
import json
import time
from urllib.robotparser import RobotFileParser

@dataclass
class ScrapedItem:
    url: str
    title: str
    content: str
    metadata: Dict[str, Any]
    timestamp: float

class BaseScraper(ABC):
    def __init__(self, rate_limit: float = 1.0, timeout: int = 30):
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.session: aiohttp.ClientSession = None
        self.robots_cache: Dict[str, RobotFileParser] = {}
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={"User-Agent": "Vibhu-Oska-Scraper/1.0"}
        )
        return self
    
    async def __aexit__(self, *args):
        await self.session.close()
    
    async def can_fetch(self, url: str) -> bool:
        # Respect robots.txt
        from urllib.parse import urlparse
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        
        if base not in self.robots_cache:
            rp = RobotFileParser()
            rp.set_url(f"{base}/robots.txt")
            try:
                rp.read()
            except:
                pass
            self.robots_cache[base] = rp
        
        return self.robots_cache[base].can_fetch("*", url)
    
    @abstractmethod
    async def discover_urls(self) -> List[str]:
        """Return list of URLs to scrape"""
        pass
    
    @abstractmethod
    async def parse_page(self, url: str, html: str) -> List[ScrapedItem]:
        """Extract structured content from page"""
        pass
    
    async def scrape(self) -> List[ScrapedItem]:
        urls = await self.discover_urls()
        results = []
        
        for url in urls:
            if not await self.can_fetch(url):
                continue
            
            try:
                async with self.session.get(url) as resp:
                    html = await resp.text()
                    items = await self.parse_page(url, html)
                    results.extend(items)
                    await asyncio.sleep(self.rate_limit)
            except Exception as e:
                print(f"Error scraping {url}: {e}")
        
        return results
```

### Set 2.2: Coding Domain Scrapers ⏱️15min each

**Create:** `Scripts/scrapers/coding/*.py`

| Scraper | Sources | Output |
|---------|---------|--------|
| `python_scraper.py` | Python docs, stdlib, PyPI top 200, RealPython, GeeksforGeeks | `Data/training/specialized/Coding/PythonCore/corpus/raw.jsonl` |
| `cpp_scraper.py` | cppreference, C++ Core Guidelines, LLVM docs | `.../CppCore/...` |
| `rust_scraper.py` | Rust Book, std docs, crate docs (serde, tokio, clap) | `.../RustCore/...` |
| `js_ts_scraper.py` | MDN, TypeScript Handbook, Node.js, React/Vue docs | `.../JavaScriptCore/...` |
| `go_scraper.py` | Go docs, Effective Go, stdlib | `.../GoCore/...` |
| `sql_scraper.py` | PostgreSQL docs, SQLite docs, SQL tutorials | `.../SQLCore/...` |
| `bash_scraper.py` | GNU Bash manual, zsh, fish, awk/sed/grep | `.../BashShellCore/...` |
| `regex_scraper.py` | PCRE docs, RE2 docs, regex101 | `.../RegexCore/...` |

### Set 2.3: RealWorld Domain Scrapers ⏱️15min each

| Scraper | Sources |
|---------|---------|
| `excel_scraper.py` | MS Excel docs, ExcelJet, VBA, Power Query M |
| `web_scraping_scraper.py` | BeautifulSoup, lxml, Playwright, Selenium, Scrapy docs |
| `filesystem_scraper.py` | pathlib, watchdog, inotify, rsync, rclone |
| `sysadmin_scraper.py` | systemd, Docker, K8s, networking, firewall |
| `knowledge_scraper.py` | Wikipedia, science/math sites, philosophy |
| `network_scraper.py` | RFCs, HTTP/2/3, gRPC, GraphQL, DNS, TLS |
| `db_admin_scraper.py` | PG admin, MySQL, Redis, MongoDB, Cassandra |
| `cloud_scraper.py` | AWS/GCP/Azure, Terraform, Ansible, Pulumi |
| `security_scraper.py` | OWASP, JWT, OAuth2, crypto, pen testing |

### Set 2.4: Corpus Formatter ⏱️15min

**Create:** `Scripts/format_corpus.py`

```python
import json
import argparse
from pathlib import Path

def format_corpus(input_path: Path, output_path: Path, domain: str, repeat: int = 3):
    """Convert scraped JSONL → Query/Response format with 3x repetition"""
    
    pairs = []
    with open(input_path) as f:
        for line in f:
            item = json.loads(line)
            # Convert to Q&A format
            query = item.get("title", "") + "\n" + item.get("content", "")[:500]
            response = item.get("content", "")
            
            if len(response) < 50:  # Skip too short
                continue
            
            pairs.append(f"Query: {query}\nResponse: {response}")
    
    # Repeat 3x for tokenizer training
    with open(output_path, 'w') as f:
        for _ in range(repeat):
            for pair in pairs:
                f.write(pair + "\n\n")
    
    # Split train/val (90/10)
    split_idx = int(len(pairs) * 0.9)
    train_pairs = pairs[:split_idx]
    val_pairs = pairs[split_idx:]
    
    with open(output_path.with_suffix('.train.txt'), 'w') as f:
        for _ in range(repeat):
            for pair in train_pairs:
                f.write(pair + "\n\n")
    
    with open(output_path.with_suffix('.val.txt'), 'w') as f:
        for pair in val_pairs:
            f.write(pair + "\n\n")
    
    print(f"Domain: {domain} | Total: {len(pairs)} | Train: {len(train_pairs)} | Val: {len(val_pairs)}")
```

### Set 2.5: Run All Scrapers ⏱️15min × 20

```bash
# Example for PythonCore (run in parallel where possible)
python Scripts/scrapers/coding/python_scraper.py \
    --output Data/training/specialized/Coding/PythonCore/corpus/raw.jsonl

python Scripts/format_corpus.py \
    --input Data/training/specialized/Coding/PythonCore/corpus/raw.jsonl \
    --output Data/training/specialized/Coding/PythonCore/corpus/corpus.txt \
    --domain python

# Repeat for all 19 domains (Coding: 8, RealWorld: 10, FastResponder: 1)
# Can run scrapers in parallel, format sequentially
```

---

## Phase 3: Specialist Training (Week 3-7) — 15-Min Sets

### Set 3.1: Specialist Base Trainer ⏱️15min

**Create:** `Backend/Core/SpecializedCore/train_specialist.py`

```python
# Generic trainer inheriting all SARA fixes
# Args: --domain, --subdomain, --model-size (small/medium/large)
# Auto-loads corpus from domain folder
# Saves to domain/checkpoints/
# Supports: fp16, gradient scaler, curriculum, NaN guards, early stopping
```

### Set 3.2: Train Coding Specialists (Priority Order) ⏱️15min × N each

```bash
# 1. PythonCore (highest usage) — ~20 min
python -m Backend.Core.SpecializedCore.Coding.PythonCore.train \
    --epochs 30 --batch-size 16 --lr 1e-4

# 2. JavaScriptCore — ~15 min
# 3. SQLCore — ~10 min
# 4. CppCore — ~20 min
# 5. RustCore — ~20 min
# 6. GoCore — ~15 min
# 7. BashShellCore — ~10 min
# 8. RegexCore — ~10 min

# Each saves to: Backend/Core/SpecializedCore/Coding/{Domain}/checkpoints/
```

### Set 3.3: Train CodingRouter ⏱️15min

```bash
python -m Backend.Core.SpecializedCore.Coding.CodingRouter.train \
    --epochs 20 --batch-size 32
# Multi-class: 9 languages + "general"
```

### Set 3.4: Train RealWorld Specialists ⏱️15min × N each

```bash
# Priority order:
# 1. ExcelCore, 2. WebScrapingCore, 3. FileSystemCore
# 4. SystemAdminCore, 5. KnowledgeCore
# 6. NetworkCore, 7. DatabaseAdminCore, 8. CloudCore, 9. SecurityCore
```

### Set 3.5: Train RealWorldRouter ⏱️15min

```bash
python -m Backend.Core.SpecializedCore.RealWorld.RealWorldRouter.train \
    --epochs 20
```

### Set 3.6: Train FastResponderCore ⏱️15min

```bash
python -m Backend.Core.SpecializedCore.FastResponderCore.train \
    --epochs 15 --model-size tiny
# ~5M params, math/time/facts/greetings
```

---

## Phase 4: EvolutionCore RL Loop (Week 7-9) — 15-Min Sets

### Set 4.1: SandboxExecutor ⏱️15min

**Create:** `Backend/Core/MainCore/EvolutionCore/SandboxExecutor.py`

```python
# Wraps AutomationCore.run_command with:
# - Timeout enforcement (30s default)
# - Resource limits (CPU, memory via Windows Job Objects)
# - Output capture (stdout, stderr, return code)
# - Security validation (no network, no privileged ops, no filesystem outside sandbox)
```

### Set 4.2: RewardEngine ⏱️15min

**Create:** `Backend/Core/MainCore/EvolutionCore/RewardEngine.py`

```python
# Domain-specific reward functions
# Returns: (reward: float, metadata: dict)
# Composable: syntax + execution + correctness + performance + safety

REWARD_FUNCTIONS = {
    "coding": {
        "syntax_valid": 1.0,
        "executes": 2.0,
        "correct_output": 5.0,
        "performance": (1.0, 3.0),  # range based on benchmark
        "security_violation": -10.0
    },
    "excel": {
        "formula_valid": 1.0,
        "produces_result": 2.0,
        "matches_expected": 5.0
    },
    "web_scraping": {
        "selector_works": 1.0,
        "data_extracted": 2.0,
        "complete": 3.0,
        "no_block": 2.0
    }
    # ... all domains
}
```

### Set 4.3: GRPO Trainer ⏱️15min

**Create:** `Backend/Core/MainCore/EvolutionCore/GRPOTrainer.py`

```python
# Group Relative Policy Optimization (no critic network)
# Uses prioritized experience replay
# Updates specialist LoRA adapters (not full weights)
# Stable, group-relative rewards
```

### Set 4.4: CodeGenerator ⏱️15min

**Create:** `Backend/Core/MainCore/EvolutionCore/CodeGenerator.py`

```python
# Generates training tasks for specialists
# Uses CognitionCore to create: (prompt, expected_output, test_cases)
# Feeds into specialist supervised fine-tuning
```

### Set 4.5: BackupSpawner + Monitoring Integration ⏱️15min

**Create:** `BackupSpawner.py` + Modify `MonitoringCore`

```python
# MonitoringCore publishes BACKUP_SCALE events
# EvolutionCore consumes → spawns/kills BackupCore instances
# PoolManager maintains target pool size
```

### Set 4.6: EvolutionCore Training Loop ⏱️15min × N (overnight)

```bash
python -m Backend.Core.MainCore.EvolutionCore.trainer \
    --steps 10000 --batch-size 4 --algorithm grpo

# Runs continuously, logs to EvolutionCore/checkpoints/
```

---

## Phase 5: Core Refactors (Week 9-11) — 15-Min Sets

### Set 5.1: OrchestratorCore Refactor ⏱️15min × 4
- IntentClassifier (learned + keyword hybrid)
- SpecialistRouter (parallel multi-specialist dispatch)
- ResultSummator (merge, dedupe, conflict resolution)
- FastResponderDispatcher

### Set 5.2: HybridCore Daemon Promotion ⏱️15min × 3
- HeartbeatDaemon (always-on event loop)
- CoreArbiter (resource arbitration)
- ParaCoreLink (secure channel)

### Set 5.3: MonitoringCore Proactive ⏱️15min × 2
- AnomalyDetector (ML-based)
- ProactiveActor (takes action)

### Set 5.4: OptimizationCore Model/Process Optimizer ⏱️15min × 2

---

## Phase 6: BackupCore Pool (Week 11-12) — 15-Min Sets

### Set 6.1: Versatile BackupCore ⏱️15min × 3
- RoleAdapter (dynamic role assumption)
- CapabilityRegistry (shared class/function access)
- Single checkpoint (~10M params)

### Set 6.2: PoolManager ⏱️15min × 2
- Dynamic scaling via EvolutionCore signals
- Health monitoring, auto-replace

---

## Phase 7: ParaCore (Week 12-13) — 15-Min Sets

### Set 7.1: OmniscienceEngine ⏱️15min × 2
- Wildcard EventBus subscription
- Real-time state model of all cores

### Set 7.2: InterventionEngine ⏱️15min × 2
- OVERRIDE event publishing
- Priority supersession logic

### Set 7.3: ParaCore Training ⏱️15min × N (continuous)

```bash
python -m Backend.Core.ParaCore.training.train_omniscience --online
# Trains on live system event stream
```

---

## Phase 8: Documentation (Parallel) — 15-Min Sets

### Set D.1: Architecture Docs ⏱️15min × 5
Mirror to `WorkingNotes/architecture_v2/`

### Set D.2: Opencode Notes ⏱️15min × 3
All 20 docs in `.agents/.opencode-notes/`

---

## Edge Case Handling (Built into Each Set)

| Edge Case | Mitigation |
|-----------|------------|
| NaN/Inf loss | NaN guards, gradient scaler, lower LR, curriculum |
| OOM (VRAM) | 4-bit quantization, gradient checkpointing, sequential loading |
| Corpus gaps | Synthetic generation fallback, human review queue |
| Specialist failure | BackupCore assumes role via RoleAdapter |
| ParaCore override loop | Max 3 overrides/min, cooldown, escalation to human |
| RL reward hacking | Reward clipping, diversity bonus, human validation |
| Weight swap race | Mutex locks, atomic VRAM manager operations |
| EventBus flood | Rate limiting, priority queues, backpressure |

---

## Suggestions & Doubts

### Suggestions
1. **Shared Base Model**: Pre-train 50M base on combined corpus → fine-tune specialists. Saves 3-4 weeks, better quality.
2. **Corpus Generation**: Use `Models/reasoning/finetune.py` (QLoRA on Qwen) to generate synthetic Q&A for each domain, then human curate.
3. **VRAM Budget**: 8GB is tight. Use 4-bit quantization (bitsandbytes) for inactive specialists.
4. **Router Unification**: Merge CodingRouter + RealWorldRouter + IntentClassifier into single MasterRouter.

### Decisions Needed
1. **ParaCore Training**: Online (live events) vs. Offline (captured logs)?
2. **BackupCore Versatility**: Single model + RoleAdapter vs. Per-role LoRA adapters on shared base?
3. **Specialist Model Size**: Target 10M/15M/20M params per domain?
4. **Corpus Source Priority**: Manual curation vs. Synthetic vs. Scraped?
5. **Phase Order**: Fix SARA first (Phase 1) OR scaffold all cores in parallel (Phase 0)?

---

## Total Estimated: ~120 sets = ~30 hours

**Recommended Start Order:**
1. Sets 0.1-0.4 (Foundation — 1 hour)
2. Sets 1.1-1.5 (SARA Fix — 1.5 hours) — BLOCKING
3. Sets 2.1-2.5 (Scraping — 5 hours, background)
4. Sets 3.1-3.6 (Specialist Training — 10 hours, parallelizable)
5. Sets D.1-D.2 (Documentation — 2 hours, parallel)

---

*End of Training Pipeline Documentation*
