# 10 — OptimizationCore

> **The model and process optimizer.** OptimizationCore reduces inference cost through model compression (quantization, pruning, distillation), optimizes process scheduling (batching, caching, context compression), and manages VRAM lifecycle on the RTX 4060 8GB.

## 1. Overview

```
Current State                    Target State
─────────────                    ─────────────
┌──────────────────┐             ┌──────────────────────────────────────────┐
│ OptimizationCore │             │            OptimizationCore               │
│                  │             │  ┌────────────┐  ┌──────────────────┐   │
│  • optimize()    │  ──────►   │  │ModelOptimizer│  │ ProcessOptimizer │   │
│  • cache lookup  │             │  │             │  │                  │   │
│  • context       │             │  │ • Quantize  │  │ • Scheduling     │   │
│    compression   │             │  │ • Prune     │  │ • Batching       │   │
│                  │             │  │ • Distill   │  │ • Caching        │   │
└──────────────────┘             │  └──────┬─────┘  └────────┬─────────┘   │
                                 │         │                  │             │
                                 │  ┌──────▼──────────────────▼─────────┐  │
                                 │  │          VRAMManager              │  │
                                 │  │  • Weight swapping                │  │
                                 │  │  • Offloading to disk/mmap        │  │
                                 │  │  • 4-bit quantization in-place    │  │
                                 │  │  • RTX 4060 8GB allocation map     │  │
                                 │  └───────────────────────────────────┘  │
                                 └──────────────────────────────────────────┘
```

---

## 2. ModelOptimizer — Quantization, Pruning, Distillation

### Purpose

Reduces model footprint and inference latency through three complementary compression techniques. Each technique is configurable per-model and can be applied independently or in combination.

### 2.1 Quantization

| Bit-Width | Method | Size Reduction | Quality Impact | Use Case |
|---|---|---|---|---|
| **FP16** | Native torch | 2× | None | Default for GPU inference |
| **INT8** | Dynamic quantization | 4× | Minimal | CPU inference path |
| **NF4** | QLoRA (bitsandbytes) | 4× | Minimal | Fine-tuned models (reasoning) |
| **4-bit GGUF** | GGML quantization | 8× | Moderate | Model offload / disk storage |
| **2-bit GGUF** | Aggressive quant | 16× | Significant | Extreme VRAM savings |

```python
class ModelQuantizer:
    QUANT_PROFILES = {
        "fp16":   {"bits": 16, "method": "native",   "size_factor": 1.0},
        "int8":   {"bits": 8,  "method": "dynamic",   "size_factor": 0.5},
        "nf4":    {"bits": 4,  "method": "qlora",     "size_factor": 0.25},
        "4bit":   {"bits": 4,  "method": "gguf_q4",   "size_factor": 0.25},
        "2bit":   {"bits": 2,  "method": "gguf_q2",   "size_factor": 0.125},
    }

    def quantize(self, model: nn.Module, profile: str, device: str = "cuda") -> nn.Module:
        """
        Apply quantization to a model.
        Returns quantized model (may be in-place for some methods).
        """
        cfg = self.QUANT_PROFILES[profile]
        if cfg["method"] == "qlora":
            return self._apply_nf4(model)
        elif cfg["method"] == "dynamic":
            return torch.quantization.quantize_dynamic(
                model, {torch.nn.Linear}, dtype=torch.qint8
            )
        elif cfg["method"] in ("gguf_q4", "gguf_q2"):
            return self._apply_gguf_quant(model, cfg["bits"])
        return model  # fp16 is native
```

### 2.2 Structured Pruning

```python
class ModelPruner:
    def __init__(self, config: dict):
        self.sparsity_target: float = config.get("sparsity", 0.3)  # 30% neurons removed
        self.method: str = config.get("method", "magnitude")       # "magnitude" | "l1_unstructured"
        self结构化: bool = config.get("structured", True)           # Column/row pruning vs unstructured

    def prune(self, model: nn.Module) -> nn.Module:
        """
        Remove low-magnitude weights/neurons.
        Structured pruning removes entire neurons (faster inference).
        Unstructured pruning sets individual weights to zero (sparse tensors).
        """
        if self.structured:
            return self._structured_prune(model, self.sparsity_target)
        return self._unstructured_prune(model, self.sparsity_target)
```

**Pruning targets by layer type:**

| Layer Type | Pruning Strategy | Typical Sparsity |
|---|---|---|
| `nn.Linear` (attention) | Column pruning (neurons) | 20-30% |
| `nn.Linear` (MLP) | Row pruning (neurons) | 25-40% |
| `nn.Embedding` | Row pruning (tokens) | 10-20% |
| `nn.LayerNorm` | Never pruned | 0% |
| `Conv2d` (if present) | Filter pruning | 20-30% |

### 2.3 Knowledge Distillation

```python
class ModelDistiller:
    def __init__(self, config: dict):
        self.teacher_model: str = config.get("teacher", "qwen2.5-coder-3b")
        self.student_model: str = config.get("student", "vibhu-router-150m")
        self.temperature: float = config.get("temperature", 2.0)
        self.alpha: float = config.get("alpha", 0.5)  # Balance CE vs KD loss

    async def distill(self, train_data: list[dict]) -> dict:
        """
        Transfer knowledge from teacher to student.
        Loss = alpha * CE(student, labels) + (1-alpha) * KL(student/T, teacher/T)
        """
        # Load frozen teacher
        teacher = await self._load_model(self.teacher_model, frozen=True)
        student = await self._load_model(self.student_model, frozen=False)

        for batch in train_data:
            with torch.no_grad():
                teacher_logits = teacher(batch["input_ids"])

            student_logits = student(batch["input_ids"])
            loss = self._compute_distillation_loss(
                student_logits, teacher_logits, batch["labels"]
            )
            loss.backward()
            self.optimizer.step()

        return {"status": "complete", "final_loss": loss.item()}
```

---

## 3. ProcessOptimizer — Scheduling, Batching, Caching

### Purpose

Optimizes the flow of tasks through the system pipeline. Reduces redundant work, groups similar operations, and prioritizes tasks for maximum throughput.

### 3.1 Dynamic Batching

```python
class DynamicBatcher:
    def __init__(self, config: dict):
        self.max_batch_size: int = config.get("max_batch_size", 8)
        self.max_wait_ms: float = config.get("max_wait_ms", 100.0)
        self.batch_by_similarity: bool = config.get("batch_by_similarity", True)

    async def submit(self, task: Task) -> BatchResult:
        """
        Groups similar tasks into batches for fused GPU execution.
        Similarity based on prompt embedding cosine distance.
        """
        # Wait for batch window or max_size
        batch = await self._collect_batch(task)

        if self.batch_by_similarity:
            batch = self._cluster_by_embedding(batch)

        # Execute as fused batch
        results = await self._execute_batch(batch)
        return results
```

**Batching strategy:**

```
Task Queue
     │
     ▼
┌──────────────────────────┐
│ Collect for max_wait_ms  │──── timeout? ────► Execute partial batch
│ (up to max_batch_size)   │
└──────────┬───────────────┘
           │ batch ready
           ▼
┌──────────────────────────┐
│ Cluster by embedding      │
│ similarity (cosine > 0.8)│
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Pad to uniform length     │
│ Create attention masks    │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Execute as fused batch    │
│ (single forward pass)     │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Split results, dispatch   │
│ individual responses      │
└──────────────────────────┘
```

### 3.2 Task Scheduling

```python
class TaskScheduler:
    PRIORITY_LEVELS = {
        "critical": 0,    # System alerts, health checks
        "high": 1,        # Active user chat
        "normal": 2,      # Background tasks, cache warming
        "low": 3,         # Telemetry flush, maintenance
    }

    def __init__(self, config: dict):
        self.max_concurrent: int = config.get("max_concurrent_tasks", 4)
        self.preemptive: bool = config.get("preemptive_scheduling", False)
        self.queue: PriorityQueue = PriorityQueue()
        self.active: dict[str, Task] = {}

    async def schedule(self, task: Task) -> None:
        """Priority queue with optional preemption for high-priority arrivals."""
        if len(self.active) < self.max_concurrent:
            self._dispatch(task)
        else:
            if self.preemptive and task.priority < self._lowest_active_priority():
                victim = self._find_preemptable_task()
                self._suspend(victim)
                self._dispatch(task)
            else:
                self.queue.put(task)
```

### 3.3 Multi-Tier Cache

```python
class MultiTierCache:
    def __init__(self, config: dict):
        # L1: In-memory LRU (fastest, smallest)
        self.l1 = LRUCache(maxsize=config.get("l1_maxsize", 256))
        # L2: SQLite on-disk (medium speed, persistent)
        self.l2 = SQLiteCache(db_path=config.get("l2_path", "Data/cache.db"))
        # L3: ChromaDB semantic (slowest, fuzzy match)
        self.l3 = SemanticCache(collection="response_cache")

    async def get(self, prompt: str) -> CacheResult | None:
        """Check tiers in order. Semantic match returns similarity score."""
        # L1: Exact match
        result = self.l1.get(prompt)
        if result:
            return CacheResult(tier="L1", hit=True, data=result)

        # L2: Exact match on disk
        result = await self.l2.get(prompt)
        if result:
            self.l1.set(prompt, result)  # Promote to L1
            return CacheResult(tier="L2", hit=True, data=result)

        # L3: Semantic similarity
        result = await self.l3.query(prompt, threshold=0.92)
        if result:
            self.l1.set(prompt, result.data)  # Promote to L1
            return CacheResult(tier="L3", hit=True, similarity=result.score, data=result.data)

        return CacheResult(tier="none", hit=False)

    async def set(self, prompt: str, response: str, ttl: int = 1800) -> None:
        """Write to all tiers for maximum hit probability."""
        self.l1.set(prompt, response)
        await self.l2.set(prompt, response, ttl=ttl)
        await self.l3.store(prompt, response)
```

---

## 4. VRAMManager — Weight Swapping, Offloading, 4-bit Quantization

### Purpose

Manages the limited 8GB VRAM of the RTX 4060. Decides which models stay in VRAM, which get offloaded to RAM/disk, and when to apply 4-bit quantization to free space.

### 4.1 VRAM Allocation Strategy — RTX 4060 8GB

```
┌──────────────────────────────────────────────────────────────┐
│                    RTX 4060 VRAM Map (8.0 GB)                │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  System Reserved                                      │  │
│  │  0.5 GB — CUDA context, driver overhead               │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Active Model Zone                                    │  │
│  │  5.5 GB — Currently loaded model weights              │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────┐     │  │
│  │  │ Reasoning Model (qwen2.5-coder-3b QLoRA)     │     │  │
│  │  │ NF4: ~1.8 GB                                │     │  │
│  │  │ FP16 LoRA adapters: ~0.1 GB                 │     │  │
│  │  └──────────────────────────────────────────────┘     │  │
│  │  ┌──────────────────────────────────────────────┐     │  │
│  │  │ Router Model (vibhu-router-150m)             │     │  │
│  │  │ FP16: ~0.3 GB                               │     │  │
│  │  └──────────────────────────────────────────────┘     │  │
│  │  ┌──────────────────────────────────────────────┐     │  │
│  │  │ Embedding Model (all-MiniLM-L6-v2)          │     │  │
│  │  │ FP16: ~0.09 GB                              │     │  │
│  │  └──────────────────────────────────────────────┘     │  │
│  │  ┌──────────────────────────────────────────────┐     │  │
│  │  │ Image Generation (SDXL when loaded)          │     │  │
│  │  │ FP16: ~3.4 GB                               │     │  │
│  │  │ (Evicts reasoning when active)               │     │  │
│  │  └──────────────────────────────────────────────┘     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  KV Cache / Activation Zone                           │  │
│  │  1.5 GB — Attention KV cache, intermediate activations │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Safety Margin                                        │  │
│  │  0.5 GB — OOM prevention buffer                       │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 VRAM Budget Table

| Component | FP16 | NF4 | 4-bit GGUF | Offloaded |
|---|---|---|---|---|
| qwen2.5-coder-3b | 6.0 GB | 1.9 GB | 1.5 GB | 0 GB (on disk) |
| vibhu-router-150m | 0.3 GB | 0.08 GB | 0.04 GB | 0 GB |
| all-MiniLM-L6-v2 | 0.09 GB | — | — | 0 GB |
| SDXL (diffusion) | 3.4 GB | — | — | 0 GB |
| KV Cache (context) | 0.5-1.5 GB | 0.5-1.5 GB | 0.5-1.5 GB | — |
| **Total Budget** | | | | **5.5 GB active** |

### 4.3 Weight Swapping

```python
class VRAMManager:
    def __init__(self, config: dict):
        self.total_vram_gb: float = config.get("total_vram_gb", 8.0)
        self.reserved_gb: float = config.get("reserved_gb", 0.5)
        self.active_budget_gb: float = self.total_vram_gb - self.reserved_gb
        self.offload_dir: str = config.get("offload_dir", "Data/offload")
        self.swap_lock = asyncio.Lock()
        self.model_registry: dict[str, ModelSlot] = {}

    async def swap_in(self, model_name: str, priority: int = 1) -> bool:
        """
        Load a model into VRAM. If insufficient space, evict lowest priority.
        Returns True if swap succeeded.
        """
        async with self.swap_lock:
            required = self._model_size_gb(model_name)
            available = self._available_vram()

            if required <= available:
                await self._load_to_vram(model_name)
                return True

            # Need to evict
            evict_candidates = sorted(
                [m for m in self.model_registry.values() if m.in_vram],
                key=lambda m: (-m.priority, m.last_access)
            )

            freed = 0.0
            for victim in evict_candidates:
                if freed >= required:
                    break
                await self._offload_to_disk(victim.name)
                freed += victim.size_gb

            if freed >= required:
                await self._load_to_vram(model_name)
                return True

            # Still not enough — apply 4-bit quantization to active model
            await self._downquantize_active(model_name)
            return True

    async def swap_out(self, model_name: str) -> None:
        """Offload a model to RAM/disk to free VRAM."""
        async with self.swap_lock:
            if model_name in self.model_registry:
                await self._offload_to_disk(model_name)

    def _model_size_gb(self, model_name: str) -> float:
        """Estimate VRAM required (weights + KV cache overhead)."""
        profiles = {
            "qwen2.5-coder-3b": {"nf4": 1.9, "fp16": 6.0, "4bit": 1.5},
            "vibhu-router-150m": {"fp16": 0.3, "int8": 0.15},
            "all-MiniLM-L6-v2": {"fp16": 0.09},
            "sdxl": {"fp16": 3.4, "4bit": 1.2},
        }
        return profiles.get(model_name, {}).get(
            self.model_registry[model_name].quant_profile, 1.0
        )
```

### 4.4 Offloading Strategy

| Source | Destination | When | Latency Cost |
|---|---|---|---|
| VRAM → System RAM (mmap) | `torch.load(..., map_location='cpu')` | Priority eviction | ~50ms |
| VRAM → Disk (GGUF) | Serialize to `Data/offload/` | Low-priority + disk needed | ~200ms |
| VRAM → Disk (mmap) | `torch.save()` + `mmap` load | Background pre-offload | ~100ms |
| RAM → VRAM | `model.to('cuda')` | Swap-in request | ~100-500ms |

### 4.5 In-Place 4-bit Quantization

```python
async def _downquantize_active(self, model_name: str) -> None:
    """
    Convert an FP16 model in VRAM to 4-bit NF4 in-place.
    Frees ~75% of VRAM without offloading to disk.
    """
    model = self.model_registry[model_name].model
    quantized = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )
    # In-place conversion (original weights freed)
    self.model_registry[model_name].model = replace_with_bnb_layers(
        model, quantization_config=quantized
    )
    self.model_registry[model_name].quant_profile = "nf4"
    self.model_registry[model_name].size_gb *= 0.25
```

---

## 5. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       OptimizationCore                                   │
│                                                                         │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │       ModelOptimizer        │  │       ProcessOptimizer           │  │
│  │                             │  │                                  │  │
│  │  ┌───────────────────────┐  │  │  ┌───────────────────────────┐  │  │
│  │  │ ModelQuantizer        │  │  │  │ DynamicBatcher            │  │  │
│  │  │ • FP16 / INT8 / NF4  │  │  │  │ • Embedding clustering    │  │  │
│  │  │ • GGUF 4-bit / 2-bit │  │  │  │ • Max batch size          │  │  │
│  │  └───────────────────────┘  │  │  │ • Fused forward pass      │  │  │
│  │  ┌───────────────────────┐  │  │  └───────────────────────────┘  │  │
│  │  │ ModelPruner           │  │  │  ┌───────────────────────────┐  │  │
│  │  │ • Structured (column) │  │  │  │ TaskScheduler             │  │  │
│  │  │ • Unstructured (L1)   │  │  │  │ • Priority queue          │  │  │
│  │  │ • Sparsity 20-40%     │  │  │  │ • Preemptive scheduling   │  │  │
│  │  └───────────────────────┘  │  │  │ • Max concurrent tasks    │  │  │
│  │  ┌───────────────────────┐  │  │  └───────────────────────────┘  │  │
│  │  │ ModelDistiller        │  │  │  ┌───────────────────────────┐  │  │
│  │  │ • Teacher → Student   │  │  │  │ MultiTierCache            │  │  │
│  │  │ • KD loss + CE loss   │  │  │  │ • L1: In-memory LRU       │  │  │
│  │  │ • Temperature tuning  │  │  │  │ • L2: SQLite on-disk      │  │  │
│  │  └───────────────────────┘  │  │  │ • L3: ChromaDB semantic   │  │  │
│  └──────────────┬──────────────┘  │  └──────────┬────────────────┘  │  │
│                 │                  └─────────────┼──────────────────┘  │
│                 │                                │                      │
│                 ▼                                ▼                      │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                        VRAMManager                               │  │
│  │                                                                  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │  │
│  │  │ Model Slots   │  │ Swap Queue   │  │ Allocation Map         │ │  │
│  │  │              │  │              │  │                        │ │  │
│  │  │ reasoning:   │  │ swap_in()    │  │ Reserved:  0.5 GB      │ │  │
│  │  │  NF4 @1.9GB  │  │ swap_out()   │  │ Active:    5.5 GB      │ │  │
│  │  │ router:      │  │ evict()      │  │ KV Cache:  1.5 GB      │ │  │
│  │  │  FP16 @0.3GB │  │              │  │ Safety:    0.5 GB      │ │  │
│  │  │ embed:       │  │ Priority:    │  │                        │ │  │
│  │  │  FP16 @0.09GB│  │ high > low   │  │ Total:     8.0 GB      │ │  │
│  │  │ sdxl:        │  │              │  │ (RTX 4060)             │ │  │
│  │  │  FP16 @3.4GB │  │ Cooldown:    │  │                        │ │  │
│  │  └──────────────┘  │ 60s per swap │  └────────────────────────┘ │  │
│  │                    └──────────────┘                              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    EventBus Integration                          │  │
│  │                                                                  │  │
│  │  Subscribes:                                                     │  │
│  │    task.created  → schedule() + batch()                         │  │
│  │    task.completed → save_response_cache()                       │  │
│  │    monitoring.action_executed → swap_in/swap_out                │  │
│  │                                                                  │  │
│  │  Publishes:                                                      │  │
│  │    optimization.cache_hit / cache_miss                          │  │
│  │    optimization.vram_status                                     │  │
│  │    optimization.batch_executed                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. VRAM Allocation Strategy — RTX 4060 8GB Detail

### Scenario Matrix

| Scenario | Models Loaded | VRAM Used | Strategy |
|---|---|---|---|
| **Idle / Routing** | Router + Embed | 0.4 GB | All VRAM available |
| **Chat (reasoning)** | Router + Embed + Reasoning | 2.3 GB | Standard FP16 reasoning |
| **Chat + Cache Miss Storm** | Router + Embed + Reasoning | 3.8 GB | Reasoning in NF4 if threshold hit |
| **Image Generation** | Router + Embed + SDXL | 3.8 GB | Evict reasoning → load SDXL |
| **Heavy Inference** | Router + Embed + Reasoning | 2.3 GB + KV | KV cache grows dynamically |
| **All Models Active** | Router + Embed + Reasoning + SDXL | 9.8 GB | **Impossible** — must swap |
| **Emergency (OOM risk)** | Router + Embed + Reasoning (NF4) | 1.5 GB + KV | All models 4-bit quantized |

### Swap Priority Rules

```
Priority 0 (highest, never evict):
  ├── vibhu-router-150m        (always in VRAM, tiny)
  └── all-MiniLM-L6-v2         (always in VRAM, tiny)

Priority 1 (evict last):
  └── qwen2.5-coder-3b         (primary reasoning, evict only for SDXL)

Priority 2 (evict first):
  └── sdxl                     (evicted when not generating images)

Dynamic Priority (based on last access):
  └── If model idle > 5 min → demote by 1 level
  └── If model accessed → promote by 1 level (max priority 1)
```

### OOM Prevention

```python
class OOMGuard:
    def __init__(self, config: dict):
        self.safety_margin_gb: float = config.get("safety_margin_gb", 0.5)
        self.vram_monitor_interval: float = config.get("monitor_interval_s", 2.0)

    async def monitor_loop(self, vram_manager: VRAMManager) -> None:
        """Continuously monitor VRAM usage and preemptively evict if needed."""
        while True:
            used = torch.cuda.memory_allocated() / (1024 ** 3)
            total = vram_manager.total_vram_gb
            free = total - used

            if free < self.safety_margin_gb:
                # Emergency eviction: lowest priority model
                victim = vram_manager._find_eviction_candidate()
                if victim:
                    await vram_manager.swap_out(victim.name)
                    log.warning(f"OOM Guard: evicted {victim.name} to free VRAM")

            await asyncio.sleep(self.vram_monitor_interval)
```

---

## 7. Configuration

### OptimizationCore Config (default.yaml extension)

```yaml
optimization:
  # ── Model Optimization ──
  model_optimizer:
    enabled: true
    default_quant_profile: "nf4"
    pruning:
      enabled: false              # Enable when accuracy baseline established
      target_sparsity: 0.3
      method: "magnitude"
      structured: true
    distillation:
      enabled: false              # Enable in Stage 4
      teacher: "qwen2.5-coder-3b"
      student: "vibhu-router-150m"
      temperature: 2.0
      alpha: 0.5

  # ── Process Optimization ──
  process_optimizer:
    batching:
      enabled: true
      max_batch_size: 8
      max_wait_ms: 100
      batch_by_similarity: true
      similarity_threshold: 0.8
    scheduling:
      enabled: true
      max_concurrent_tasks: 4
      preemptive_scheduling: false
      priority_levels:
        critical: 0
        high: 1
        normal: 2
        low: 3
    cache:
      enabled: true
      l1_maxsize: 256
      l2_path: "Data/cache.db"
      l3_enabled: false           # Enable when ChromaDB semantic cache ready
      l3_threshold: 0.92
      default_ttl_seconds: 1800

  # ── VRAM Management ──
  vram_manager:
    enabled: true
    total_vram_gb: 8.0
    reserved_gb: 0.5
    active_budget_gb: 5.5
    kv_cache_budget_gb: 1.5
    safety_margin_gb: 0.5
    offload_dir: "Data/offload"
    swap_cooldown_seconds: 5
    vram_monitor_interval_seconds: 2.0
    model_slots:
      vibhu-router-150m:
        priority: 0
        always_loaded: true
        quant_profile: "fp16"
        size_gb: 0.3
      all-MiniLM-L6-v2:
        priority: 0
        always_loaded: true
        quant_profile: "fp16"
        size_gb: 0.09
      qwen2.5-coder-3b:
        priority: 1
        always_loaded: false
        quant_profile: "nf4"
        size_gb: 1.9
        evict_after_idle_seconds: 300
      sdxl:
        priority: 2
        always_loaded: false
        quant_profile: "fp16"
        size_gb: 3.4
        evict_after_idle_seconds: 60
```

---

## 8. File Structure

```
Backend/Core/MainCore/OptimizationCore/
├── __init__.py
├── OptimizationCore.py              ← Existing: cache + context compression
│
├── model_optimizer/
│   ├── __init__.py
│   ├── ModelOptimizer.py            ← Orchestrates quant/prune/distill
│   ├── quantizer.py                 ← ModelQuantizer (FP16/INT8/NF4/GGUF)
│   ├── pruner.py                    ← ModelPruner (structured/unstructured)
│   ├── distiller.py                 ← ModelDistiller (KD loss)
│   └── profiles/
│       ├── fp16_profile.py
│       ├── nf4_profile.py
│       └── gguf_profile.py
│
├── process_optimizer/
│   ├── __init__.py
│   ├── ProcessOptimizer.py          ← Orchestrates schedule/batch/cache
│   ├── batcher.py                   ← DynamicBatcher
│   ├── scheduler.py                 ← TaskScheduler (priority queue)
│   └── cache/
│       ├── __init__.py
│       ├── multi_tier_cache.py      ← MultiTierCache (L1/L2/L3)
│       ├── lru_cache.py             ← L1 in-memory LRU
│       ├── sqlite_cache.py          ← L2 on-disk SQLite
│       └── semantic_cache.py        ← L3 ChromaDB semantic
│
├── vram_manager/
│   ├── __init__.py
│   ├── VRAMManager.py               ← Core VRAM lifecycle manager
│   ├── model_slot.py                ← ModelSlot dataclass
│   ├── swap_queue.py                ← Async swap queue with locking
│   ├── oom_guard.py                 ← OOM prevention monitor
│   └── offload/
│       ├── __init__.py
│       ├── ram_offload.py           ← mmap-based RAM offloading
│       └── disk_offload.py          ← GGUF serialization to disk
│
├── context/
│   ├── __init__.py
│   ├── context_compressor.py        ← Existing optimize_prompt_context()
│   └── corruption_detector.py       ← Existing _is_corrupted()
│
└── config/
    └── optimization_defaults.py     ← Default configuration constants
```

---

## 9. Integration Points

### EventBus Topics Subscribed

| Topic | Handler | Purpose |
|---|---|---|
| `task.created` | `TaskScheduler.schedule()` | Route new tasks to priority queue |
| `task.completed` | `MultiTierCache.set()` | Cache successful responses |
| `task.completed` | `DynamicBatcher.on_complete()` | Remove from active batch |
| `monitoring.action_executed` | `VRAMManager.on_action()` | React to proactive swap commands |
| `system.health` | `VRAMManager.monitor_vram()` | Track VRAM utilization |
| `user.input` | `MultiTierCache.get()` | Check cache before inference |

### EventBus Topics Published

| Topic | Source | Payload |
|---|---|---|
| `optimization.cache_hit` | MultiTierCache | `{tier, similarity, prompt_hash}` |
| `optimization.cache_miss` | MultiTierCache | `{prompt_hash}` |
| `optimization.batch_executed` | DynamicBatcher | `{batch_size, avg_latency_ms}` |
| `optimization.vram_status` | VRAMManager | `{used_gb, free_gb, models_loaded}` |
| `optimization.vram_swap` | VRAMManager | `{model, direction, freed_gb}` |
| `optimization.model_quantized` | ModelOptimizer | `{model, old_profile, new_profile}` |
| `system.alert` | VRAMManager (OOM) | `{severity: 3, title: "VRAM critical"}` |

### Core Integration Map

| Core | Direction | Integration |
|---|---|---|
| **EventBus** | Subscribe + Publish | Task scheduling, cache, VRAM status |
| **CognitionCore** | Inbound | Cache lookup before inference, model loading |
| **MonitoringCore** | Outbound | VRAM metrics, cache hit rates, batch stats |
| **BackupCore** | Inbound | Context compression for backup tasks |
| **OrchestratorCore** | Inbound | Task scheduling, batch routing |
| **EvolutionCore** | Outbound | Quantized model availability for training |
| **ImageGenerationCore** | Inbound | VRAM eviction before SDXL load |

---

## 10. Events Reference

### cache_hit Event

```json
{
  "event_id": "uuid4",
  "topic": "optimization.cache_hit",
  "source": "optimization.cache",
  "payload": {
    "tier": "L1",
    "hit": true,
    "prompt_hash": "sha256:abc123",
    "response_size_chars": 842,
    "lookup_ms": 0.3
  },
  "timestamp": 1694000000.0
}
```

### vram_swap Event

```json
{
  "event_id": "uuid4",
  "topic": "optimization.vram_swap",
  "source": "optimization.vram_manager",
  "payload": {
    "model": "qwen2.5-coder-3b",
    "direction": "out",
    "method": "disk_offload",
    "freed_gb": 1.9,
    "reason": "eviction_for_sdxl",
    "vram_after_gb": 5.1
  },
  "timestamp": 1694000000.0
}
```

### batch_executed Event

```json
{
  "event_id": "uuid4",
  "topic": "optimization.batch_executed",
  "source": "optimization.batcher",
  "payload": {
    "batch_size": 4,
    "avg_latency_ms": 120.5,
    "total_tokens": 2048,
    "tokens_per_ms": 16.99
  },
  "timestamp": 1694000000.0
}
```

---

## 11. Metrics Tracked

| Metric | Type | Description |
|---|---|---|
| `cache_hit_rate` | gauge | L1+L2+L3 hits / total lookups |
| `cache_hit_by_tier` | gauge (L1/L2/L3) | Hits per cache tier |
| `cache_entries` | gauge | Total cached entries across tiers |
| `cache_size_bytes` | gauge | Estimated cache memory usage |
| `batch_size_avg` | gauge | Average tasks per batch |
| `batch_latency_ms_avg` | gauge | Average batch execution latency |
| `vram_used_gb` | gauge | Current VRAM usage |
| `vram_free_gb` | gauge | Current free VRAM |
| `vram_swap_count` | counter | Total swap in/out operations |
| `vram_swap_latency_ms` | gauge | Average swap latency |
| `oom_evictions` | counter | Emergency OOM guard evictions |
| `models_loaded` | gauge | Number of models currently in VRAM |
| `context_compression_ratio` | gauge | Original length / compressed length |
| `tasks_scheduled` | counter | Total tasks routed through scheduler |
| `tasks_preempted` | counter | Tasks preempted by higher priority |
| `quantization_operations` | counter | Total quantization conversions |
| `pruning_operations` | counter | Total pruning operations |
| `distillation_runs` | counter | Total distillation training runs |

---

## 12. Module Boundary Rules

- **No inference** — OptimizationCore never calls CognitionCore directly
- **No model training** — Distillation queues work for EvolutionCore, does not train itself
- **VRAM-only management** — Does not touch CPU memory allocation for other cores
- **Cache is read-through** — Never blocks inference; cache miss = proceed normally
- **Swap is async** — VRAM swaps never block the main inference path
- **Configuration-driven** — All thresholds, budgets, and profiles come from config
- **Observable** — All VRAM operations emit events for MonitoringCore to track
