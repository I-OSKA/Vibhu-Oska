# Vibhu-Oska — GitHub Issues & Pull Requests

> Create these on GitHub in order. Issues first, then open the corresponding PR referencing the issue number.
> Labels suggested: `feat`, `bug`, `infra`, `docs`, `model`, `frontend`

---

## Issue #1 — Project has no editable install or dependency contract

**Label:** `infra`
**Opened:** Apr 28, 2026

The repo currently has no `pyproject.toml` that reflects the actual import structure.
Running `from Backend.Core.X import Y` fails with `ModuleNotFoundError` on a fresh clone
because Python doesn't know the project root.

Additionally, there's no pinned `requirements.txt` — contributors end up with different
versions of `fastapi`, `torch`, `chromadb`, etc., making the dev environment non-reproducible.

**Expected behavior:**
A single `pip install -e .` from the project root should make all absolute imports work.
Dependencies should be pinned in `requirements.txt` and grouped by purpose (core, dev, ml).

---

## PR #1 — chore: configure pyproject.toml with editable install and dependency groups

**Closes:** #1
**Branch:** `chore/editable-install`
**Merged:** Apr 28, 2026

### What changed
- Added `pyproject.toml` with `[project]` metadata and `[tool.setuptools.packages.find]`
  configured to pick up `Backend`, `Frontend`, `Models`, `Shared` from the project root.
- Added `pip install -e .` as the canonical dev setup step.
- Split `requirements.txt` into logical groups with pinned versions:
  - **core** — `fastapi`, `uvicorn`, `pydantic`, `pyzmq`, `aiofiles`
  - **ml** — `torch`, `chromadb`, `numpy`
  - **dev** — `pytest`, `pytest-asyncio`, `httpx`
- Updated `.gitignore` to exclude `__pycache__`, `*.pyc`, `.db`, `checkpoints/`, `.env`, `venv/`.

### Verification
```bash
pip install -e .
python -c "from Backend.Core.MainCore.CognitionCore.cognition import CognitionCore; print('OK')"
```

---

---

## Issue #2 — No shared data contracts between Gateway, Core, and Plugins

**Label:** `feat`
**Opened:** Apr 30, 2026

Every module that returns data defines its own ad-hoc dict structure.
`CognitionCore` returns `{"text": ..., "tokens": ...}`, Gateway wraps it differently,
and the frontend has to guess field names. There's no single source of truth.

This also means we can't type-check cross-module return values or write contract tests.

**Proposed solution:**
Define Pydantic models in `Shared/Models.py` — `TaskResponse`, `TokenUsage`,
`ResponseMetadata`, `PluginInfo`, `CoreStatus` — and have every layer import from there.

---

## PR #2 — feat(shared): define Pydantic contracts and Protocol Buffer event schemas

**Closes:** #2
**Branch:** `feat/shared-contracts`
**Merged:** Apr 30, 2026

### What changed
- `Shared/Models.py`: Added `TaskResponse`, `TokenUsage`, `ResponseMetadata`,
  `Status`, `StatusCode`, `PluginInfo`, `CoreStatus`, `ExecutionTarget` as Pydantic v2 models.
- `Shared/protos/brain.proto`: gRPC-compatible schema for inference requests/responses.
- `Shared/protos/router.proto`: Event routing envelope used by the EventBus.
- `Shared/protos/common.proto`: Shared enum definitions (`Priority`, `TargetDevice`).
- `Shared/protos/telemetry.proto`: Hardware metric event schema for MonitoringCore.
- `Shared/protos/protocols.md`: Generation instructions and versioning conventions.

### Why Protocol Buffers alongside Pydantic
Pydantic handles in-process Python typing. Protobuf schemas define the wire format
for the ZeroMQ EventBus and any future gRPC endpoints. They're complementary, not duplicated.

---

---

## Issue #3 — Core modules have no shared initialization contract or lifecycle hooks

**Label:** `feat`
**Opened:** May 2, 2026

`CognitionCore`, `DataCore`, and others each implement their own startup logic with no
standard interface. The Gateway wires them up manually with custom if-statements.
Adding a new plugin means touching multiple files.

We need:
1. A `BaseService` abstract class with `initialize()`, `shutdown()`, `health_check()`, `execute()`.
2. A `ToolRegistry` that handles DI, lifecycle management, and `get_safe()` fallback.
3. Structured logging that all plugins can use without importing `logging` directly.

---

## PR #3 — feat(plugins): add Logger, ConfigLoader, BaseService, and ToolRegistry

**Closes:** #3
**Branch:** `feat/plugin-infrastructure`
**Merged:** May 2–5, 2026

### What changed
- `Backend/Plugins/Logger/Logger.py`: Structlog-based logger with JSON output in prod,
  colored console output in dev. `Logger.get("Name")` returns a bound child logger.
- `Backend/Plugins/ConfigLoader/ConfigLoader.py`: Loads `config/config.yaml`,
  resolves `project_root` relative to the package, supports `config.get("key.nested")`.
- `Backend/Plugins/ToolRegistry/BaseService.py`: Abstract base with
  `initialize()`, `shutdown()`, `health_check()`, `execute()`, and `info() -> PluginInfo`.
- `Backend/Plugins/ToolRegistry/Registry.py`: Singleton registry with `register()`,
  `get()`, `get_safe()` (returns None instead of raising), and `initialize_all()`.

### Impact
All existing cores now subclass `BaseService`. Gateway calls `registry.initialize_all()`
in the FastAPI lifespan context — no manual wiring required.

---

---

## Issue #4 — No persistent memory layer — context is lost between sessions

**Label:** `feat`
**Opened:** May 6, 2026

Every conversation starts from zero. There's no:
- Relational store for sessions, messages, users.
- Semantic store for long-term factual memory retrieval.
- Knowledge graph for entity relationships (eOzka team, projects, etc.).

The CognitionCore has no way to retrieve prior context, so responses are stateless.

**Proposed:**
- SQLite via `DatabaseConnector` for structured session/chat/user data.
- ChromaDB via `DataCore` for semantic memory with cosine similarity search.
- A SQLite-backed KG (`kg_nodes`, `kg_edges`) for graph-RAG (GRAG) entity retrieval.

---

## PR #4 — feat(data): add DataCore, DatabaseConnector, GRAG knowledge graph, and ChromaDB memory

**Closes:** #4
**Branch:** `feat/memory-layer`
**Merged:** May 6–12, 2026

### What changed
- `Backend/Plugins/DatabaseConnector/DatabaseConnector.py`:
  - Thread-safe SQLite with `asyncio.to_thread` executor.
  - Auto-runs migrations on `initialize()`.
  - Schema: `users`, `sessions`, `chats`, `telemetry_logs`, `kg_nodes`, `kg_edges`.
  - Seeds default eOzka KG entities and relationships on first boot.
- `Backend/Plugins/CachePlugin/CachePlugin.py`:
  - In-memory LRU store with TTL eviction for hot session data.
- `Backend/Core/SpecializedCore/DataCore/datacore.py`:
  - `store_memory()`: adds text to ChromaDB with metadata tagging.
  - `query_memory()`: returns top-k semantically similar documents with relevance scores.
  - `query_knowledge_graph()`: 1-hop entity + edge traversal returning formatted GRAG context.
  - `warm_cache()`: preloads recent sessions and user profiles on startup.

### Notes on GRAG
The knowledge graph query does case-insensitive substring matching against entity names,
plus word-level matching for multi-word entities (e.g. "Harsh" matches "Harsh Dev Jha").
This is intentionally heuristic — a future iteration can swap in spaCy NER.

---

---

## Issue #5 — Inference pipeline has no input validation or output schema enforcement

**Label:** `feat`
**Opened:** May 12, 2026

The `/chat` endpoint currently passes raw user input directly into the CognitionCore prompt
with no sanitization. A user could inject SQL fragments or XSS payloads that end up stored
in the DB or reflected in the UI.

Also, the output from CognitionCore is an untyped dict. There's no guarantee the response
has the fields the Gateway expects before it serializes to the client.

---

## PR #5 — feat(core): add full intelligence pipeline — ValidationCore, CognitionCore, HybridCore, BackupCore, MonitoringCore

**Closes:** #5
**Branch:** `feat/intelligence-pipeline`
**Merged:** May 12–17, 2026

### What changed
- `ValidationCore`: Input guard strips SQL injection patterns and HTML tags.
  Output guard validates `TaskResponse` schema before it leaves the pipeline.
- `CognitionCore`:
  - `CorpusSpellChecker` (Norvig edit-distance) detects typos and injects correction context.
  - Routes to `generate_SARA()` (custom model) or `generate_direct()` (HuggingFace)
    based on which checkpoints are present and the `model_id` request parameter.
- `HybridCore`: Reads `psutil` hardware state and routes to CPU/GPU/NPU target accordingly.
  Falls back to the next available target if the preferred one is unhealthy.
- `BackupCore`: Pure keyword-matching fallback when all transformer paths fail.
  Returns deterministic responses for common queries — zero dependencies, never crashes.
- `MonitoringCore`: Samples CPU %, RAM MB, GPU utilization at configurable intervals,
  publishes telemetry events to the EventBus.
- `OptimizationCore`: Prunes conversation context by relevance score before it enters
  the prompt, keeping token usage within the model's `max_seq_len`.

### Pipeline order
```
Request → ValidationCore (input) → DataCore (context retrieval)
        → CognitionCore (inference) → ValidationCore (output)
        → Gateway (serialize + store)
```

---

---

## Issue #6 — No real-time event system — modules communicate via direct function calls

**Label:** `feat`
**Opened:** May 20, 2026

Currently, `OrchestratorCore` calls `CognitionCore.generate()` synchronously and blocks
the event loop. There's no way for the frontend to receive partial results, telemetry
updates, or training progress without polling separate HTTP endpoints.

We need an async pub/sub backbone that:
- Decouples modules (OrchestratorCore publishes events, subscribers react independently).
- Lets the WebSocket Gateway broadcast typed events to connected clients in real time.

---

## PR #6 — feat(eventbus): add ZeroMQ EventBus, OrchestratorCore, and WebSocket ConnectionManager

**Closes:** #6
**Branch:** `feat/eventbus-orchestrator`
**Merged:** May 19–22, 2026

### What changed
- `Backend/Core/EventBus/EventBus.py`:
  - ZeroMQ `PUB/SUB` pattern with topic-prefixed message routing.
  - `publish(topic, payload)` is async; subscribers run in background threads.
  - `Topics` enum + `EventFactory` for typed, schema-validated event construction.
- `Backend/Core/MainCore/OrchestratorCore/OrchestratorCore.py`:
  - Implements the double-validation request lifecycle end-to-end.
  - Routes specialized requests to `AutomationCore`, `DesignCore`, `ImageGenerationCore`.
  - Publishes `RLHF_FEEDBACK` events when the user rates a response.
  - Caches repeated prompts semantically (cosine similarity threshold: 0.92).
- `Backend/Gateway/ConnectionManager.py`:
  - Manages WebSocket client set (`connect`, `disconnect`, `broadcast`).
  - Subscribes to EventBus and forwards matching events to all connected clients.
  - Per-client routing supported via `send_personal_message(client_id, data)`.

---

---

## Issue #7 — No HTTP API surface — frontend has no way to talk to the backend

**Label:** `feat`
**Opened:** May 22, 2026

There's no FastAPI application. The backend has a full intelligence stack but no
entry point that a browser (or any HTTP client) can call.

Needed:
- `POST /api/v1/chat` → WebSocket upgrade for streaming conversation
- `GET /health` → readiness check for Docker/k8s
- `POST /api/v1/memory/store` → add documents to semantic memory
- `POST /api/v1/memory/kg/ingest` → add entities to the GRAG knowledge graph
- `GET /api/v1/sessions` → list recent sessions for the sidebar
- `POST /api/v1/corpus/append` → add training data to the SARA corpus

---

## PR #7 — feat(gateway): add FastAPI gateway with full API surface and chat WebSocket

**Closes:** #7
**Branch:** `feat/gateway`
**Merged:** May 23–28, 2026

### What changed
- `Backend/Gateway/App.py`:
  - FastAPI app with lifespan hook — initializes all registry services on startup,
    shuts them down cleanly on exit.
  - `GET /health` — returns service registry status map.
  - `WS /ws/{session_id}` — chat WebSocket with session management, message persistence,
    GRAG context injection, and EventBus broadcast on each response.
  - `POST /api/v1/memory/store` — stores text in ChromaDB.
  - `POST /api/v1/memory/kg` — queries GRAG; returns entity context + live node/edge counts.
  - `POST /api/v1/memory/kg/ingest` — NER-based entity extraction and KG population.
  - `POST /api/v1/corpus/append` — detects QA format and appends to training corpus.
  - `GET /api/v1/sessions` — returns recent sessions ordered by `updated_at`.
- `Backend/EntryPoint.py`: `uvicorn` launcher with auto-reload in dev mode.

### Bug fixed in this PR
`DataCore.query_memory()` expects `query_text` as its first positional argument.
The Gateway was calling it as `query_memory(prompt=...)` — a keyword mismatch that
caused a silent `TypeError` and returned empty context on every chat request.
Fixed by aligning the call signature with the method definition.

---

---

## Issue #8 — SARA has no architecture, tokenizer, or training script

**Label:** `model`
**Opened:** May 29, 2026

The `Models/sara/` directory is a stub. There's no actual transformer,
no custom tokenizer, and no way to train or run inference locally.

The system currently falls back to HuggingFace `Qwen2.5-0.5B-Instruct` if no
checkpoint is found — which requires an internet connection and is not SARA.

**Goal:**
A fully custom transformer (no HuggingFace weights) that can be trained on the local
corpus and used for offline inference. Architecture should use modern primitives:
RMSNorm, RoPE, SwiGLU, weight-tied embedding/LM-head.

---

## PR #8 — feat(model): add SARA — architecture, BPE tokenizer, training pipeline, and generator

**Closes:** #8
**Branch:** `feat/sara`
**Merged:** May 30 – Jun 3, 2026

### What changed
- `Models/sara/architecture.py`:
  - `GPTConfig` dataclass with `vocab_size`, `hidden_size`, `num_layers`, `num_heads`, `max_seq_len`.
  - `RMSNorm` — Root Mean Square normalization (Llama-style, no mean subtraction).
  - `RotaryEmbedding` — RoPE with dynamic cache extension for sequences longer than `max_seq_len`.
  - `CausalSelfAttention` — multi-head attention with RoPE-applied Q/K and causal mask.
  - `FeedForward` — SwiGLU gate (`silu(gate_proj(x)) * up_proj(x)`) with no bias.
  - `TransformerBlock` — pre-norm residual block (norm → attn, norm → ffn).
  - `VibhuOskaGPT` — full decoder-only model with weight-tied embedding/LM-head.
- `Models/sara/tokenizer.py`:
  - `SaraBPETokenizer` — byte-pair encoding trained from scratch on the local corpus.
  - `train()`, `encode()`, `decode()`, `save()`, `load()` fully implemented.
- `Models/sara/train.py`:
  - `seed_default_corpus()` — seeds a Q&A corpus covering Python, FastAPI, SQL, CSS,
    Vibhu-Oska component descriptions, math, spelling, and definitions.
  - `CausalDataset` — pads/truncates sequences and maps pad tokens to `-100` for loss masking.
  - Training loop with `AdamW`, `OneCycleLR` (10% warmup, cosine anneal), gradient clipping at 1.0.
  - Saves best checkpoint by loss; early stops at ≥99.5% accuracy after epoch 15.
- `Models/sara/generate.py`:
  - `SaraGPTGenerator` — loads tokenizer vocab + model checkpoint, runs
    temperature-controlled autoregressive sampling with top-k/nucleus optional filtering.

### Running training
```bash
python -m Models.sara.train --epochs 40 --batch 4 --lr 2e-4
```

---

---

## Issue #9 — No frontend — the system has no user-facing interface

**Label:** `frontend`
**Opened:** Jun 3, 2026

The backend is complete but there's no way to interact with it except via `curl`.
We need a full dashboard that covers:
- Chat interface with streaming WebSocket responses and markdown rendering.
- Voice input (Web Speech API) and TTS output.
- Memory panel — semantic store, KG query, GRAG ingest form.
- Session history sidebar with `New Session` flow.
- Monitor panel with real-time latency and event throughput graphs.
- Training panel — corpus append, live log stream, SARA controls.
- Camera feed with gesture detection for OS-level commands.
- Voice biometric lock — pitch fingerprinting before executing sensitive commands.

---

## PR #9 — feat(frontend): add full AI-OS dashboard with chat, memory, monitor, training, and biometric panels

**Closes:** #9
**Branch:** `feat/frontend-dashboard`
**Merged:** Jun 4–17, 2026

### What changed
- `Frontend/web_app/templates/index.html`:
  - 6-panel layout: Chat, Memory, Monitor, Training, Settings, Config.
  - Session history sidebar with live `newSession()` and 30s polling refresh.
  - KG ingest form with live node/edge count feedback.
  - Training log `<pre>` block with auto-scroll.
- `Frontend/web_app/static/style.css`:
  - Dark-mode design system with CSS custom properties for color, spacing, blur.
  - Glassmorphism panels (`backdrop-filter: blur(16px)`).
  - Animated gradient border on the active chat input.
  - Responsive grid that collapses to single-column on narrow viewports.
- `Frontend/web_app/static/ChatData.js`:
  - WebSocket client with exponential backoff reconnect (100ms → 30s cap, jitter added).
  - Markdown renderer with code block extraction, language label, and copy button.
  - Web Speech API voice input; `SpeechSynthesisUtterance` TTS output pipeline.
  - MediaPipe Hands gesture detection via webcam — maps finger poses to OS commands.
  - `pollStatus()` — refreshes KG node/edge counts, session list, and plugin health every 30s.
  - Voice biometric lock — captures 3-sample pitch fingerprint on calibration,
    gates sensitive commands behind a 22% frequency variance check.
  - Auto-ingests every AI response into the GRAG knowledge graph after generation.
  - RLHF feedback bar (thumbs up/down) on each assistant message.
  - Execution replay log and task queue with live status dot indicators.

### Design notes
The UI was intentionally kept as vanilla JS + CSS (no framework) to keep the bundle
self-contained and bootable without `npm`. The only external dependency is Chart.js
loaded via CDN for the monitor graphs.

---

---

## Issue #10 — No containerization, no test suite, and no CI/CD pipeline

**Label:** `infra`
**Opened:** Jun 18, 2026

The project runs only on the dev machine. Anyone cloning the repo has to manually
install dependencies, configure paths, and hope nothing conflicts.

Also there are no tests — we've been testing manually via the frontend UI,
which means regressions can slip through undetected.

---

## PR #10 — feat(infra): add Docker Compose, 65-test integration suite, and CI scripts

**Closes:** #10
**Branch:** `feat/infra-docker-tests`
**Merged:** Jun 19–20, 2026

### What changed
- `Docker/Dockerfile`:
  - Multi-stage build: `builder` stage installs dependencies; `runtime` stage copies
    only the installed package and source, keeping the image lean.
  - CPU and GPU targets via build arg `DEVICE=cpu|gpu` (GPU target installs CUDA-compatible torch).
- `Docker/docker-compose.yml`:
  - `vibhu-oska` service with health check on `GET /health`.
  - Named volume for `Data/` (persists SQLite + ChromaDB between container restarts).
  - Environment file injection via `.env`.
- `Tests/`:
  - 65 integration tests across `test_datacore.py`, `test_validation.py`,
    `test_orchestrator.py`, `test_gateway.py`, `test_cognition.py`.
  - Covers happy path, boundary conditions, and adversarial inputs (SQL injection,
    empty prompts, oversized payloads, malformed JSON).
  - All tests use in-memory SQLite and a temporary ChromaDB collection — no disk state.
- `Scripts/`:
  - `setup.sh` — installs editable package, creates `.env` from `.env.example`.
  - `train_sara.sh` — wrapper for the training CLI with recommended defaults.
  - `generate_protos.sh` — runs `protoc` on all `.proto` files in `Shared/protos/`.

### Test results
```
65 passed in 21.85s
```

### Running locally with Docker
```bash
docker compose up --build
# UI available at http://localhost:8000
```
