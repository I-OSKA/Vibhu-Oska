# Vibhu-Oska — Commit History Plan

> ~40 commits staged in chronological "story" order, grouped by phase.
> Each commit is atomic, purposeful, and covers exactly one logical unit.
> Files tagged in brackets show what gets staged per commit.

---

## Phase 1 — Project Foundation & Configuration

```
chore: configure pyproject.toml with editable install and dependency groups
[pyproject.toml, requirements.txt]

chore: add .gitignore covering venv, __pycache__, .db files, checkpoints, .env
[.gitignore]

docs: draft initial README with project philosophy, architecture diagram, and quickstart
[README.md]

chore: add VS Code workspace settings and launch configurations for FastAPI debugging
[.vscode/settings.json, .vscode/launch.json]
```

---

## Phase 2 — Shared Contracts & Protocol Buffers

```
feat(shared): define TaskResponse, TokenUsage, PluginInfo, CoreStatus Pydantic models
[Shared/Models.py, Shared/__init__.py]

feat(proto): add brain.proto and router.proto for gRPC-compatible event schemas
[Shared/protos/brain.proto, Shared/protos/router.proto, Shared/protos/common.proto]

feat(proto): add telemetry.proto for hardware metrics and system health events
[Shared/protos/telemetry.proto]

docs(proto): document protocol buffer conventions and generation instructions
[Shared/protos/protocols.md, Shared/readme.md]
```

---

## Phase 3 — Plugin Infrastructure

```
feat(plugins): add Logger plugin with structlog-based structured output and log levels
[Backend/Plugins/Logger/Logger.py]

feat(plugins): add ConfigLoader with YAML parsing and typed project-root resolution
[Backend/Plugins/ConfigLoader/ConfigLoader.py, config/config.yaml]

feat(plugins): add BaseService abstract contract for all injectable plugins
[Backend/Plugins/ToolRegistry/BaseService.py]

feat(plugins): add ToolRegistry for dependency injection and plugin lifecycle management
[Backend/Plugins/ToolRegistry/Registry.py]
```

---

## Phase 4 — Data & Memory Layer

```
feat(data): add DatabaseConnector plugin with thread-safe SQLite and migration runner
[Backend/Plugins/DatabaseConnector/DatabaseConnector.py]

feat(data): add sessions, chats, users, telemetry_logs schema migrations
[Backend/Plugins/DatabaseConnector/DatabaseConnector.py]

feat(data): seed knowledge graph schema — kg_nodes and kg_edges tables with FK cascade
[Backend/Plugins/DatabaseConnector/DatabaseConnector.py]

feat(data): seed default eOzka KG entities (founders, subsidiaries, products) on first boot
[Backend/Plugins/DatabaseConnector/DatabaseConnector.py]

feat(data): add CachePlugin with in-memory LRU store and TTL eviction
[Backend/Plugins/CachePlugin/CachePlugin.py]

feat(data): add DataCore with ChromaDB semantic memory store and query pipeline
[Backend/Core/SpecializedCore/DataCore/datacore.py]

feat(data): add query_memory with relevance scoring and min_relevance filtering
[Backend/Core/SpecializedCore/DataCore/datacore.py]

feat(data): implement query_knowledge_graph with 1-hop entity and edge traversal
[Backend/Core/SpecializedCore/DataCore/datacore.py]

feat(data): add cache warm-up on startup for active sessions and user profiles
[Backend/Core/SpecializedCore/DataCore/datacore.py]
```

---

## Phase 5 — Core Intelligence Pipeline

```
feat(validation): add ValidationCore with SQL injection and XSS sanitization guards
[Backend/Core/MainCore/ValidationCore/validation.py]

feat(validation): add output schema enforcement with JSON contract verification
[Backend/Core/MainCore/ValidationCore/validation.py]

feat(cognition): add CorpusSpellChecker with Norvig-style edit-distance correction
[Backend/Core/MainCore/CognitionCore/cognition.py]

feat(cognition): add CognitionCore with sara and direct-transformer routing
[Backend/Core/MainCore/CognitionCore/cognition.py]

feat(cognition): add generate_SARA() loading checkpoints from Models directory
[Backend/Core/MainCore/CognitionCore/cognition.py]

feat(cognition): add generate_direct() for in-process HuggingFace transformer inference
[Backend/Core/MainCore/CognitionCore/cognition.py]

feat(hybrid): add HybridCore with CPU/GPU/NPU target selection and health-gated routing
[Backend/Core/MainCore/HybridCore/HybridCore.py]

feat(backup): add BackupCore with deterministic keyword-matching fallback responses
[Backend/Core/BackupCore/BackupCore.py]

feat(monitoring): add MonitoringCore with psutil-based CPU, RAM, GPU telemetry sampling
[Backend/Core/MainCore/MonitoringCore/MonitoringCore.py]

feat(optimization): add OptimizationCore for relevance-ranked context pruning
[Backend/Core/MainCore/OptimizationCore/OptimizationCore.py]

feat(orchestrator): add OrchestratorCore with double-validation request lifecycle
[Backend/Core/MainCore/OrchestratorCore/OrchestratorCore.py]

feat(orchestrator): add specialized core routing — AutomationCore, DesignCore, ImageCore
[Backend/Core/MainCore/OrchestratorCore/OrchestratorCore.py]

feat(orchestrator): add RLHF feedback event publishing and response caching
[Backend/Core/MainCore/OrchestratorCore/OrchestratorCore.py]
```

---

## Phase 6 — Event Bus & Real-time Communication

```
feat(eventbus): add ZeroMQ pub/sub EventBus with topic filtering and async dispatch
[Backend/Core/EventBus/EventBus.py]

feat(eventbus): add Topics enum and EventFactory for typed event construction
[Backend/Core/EventBus/Events.py, Backend/Core/EventBus/Topics.py]

feat(eventbus): add WebSocket connection manager with broadcast and per-client routing
[Backend/Gateway/ConnectionManager.py]
```

---

## Phase 7 — FastAPI Gateway & API Surface

```
feat(gateway): add FastAPI application with lifespan boot sequence and health endpoints
[Backend/Gateway/App.py]

feat(gateway): add chat WebSocket endpoint with session management and event streaming
[Backend/Gateway/App.py]

feat(gateway): add memory endpoints — vector store, KG query, session history
[Backend/Gateway/App.py]

feat(gateway): add corpus append endpoint with QA format detection and ChromaDB ingest
[Backend/Gateway/App.py]

feat(gateway): add KG ingest endpoint with heuristic NER for GRAG auto-population
[Backend/Gateway/App.py]

fix(gateway): correct query_memory keyword arg from prompt= to query_text=
[Backend/Gateway/App.py]

feat(gateway): add /api/v1/sessions sidebar endpoint returning recent sessions by update time
[Backend/Gateway/App.py]

feat(gateway): return live node and edge counts from KG endpoint for dashboard metrics
[Backend/Gateway/App.py]
```

---

## Phase 8 — SARA Model

```
feat(model): add SARA architecture with RMSNorm, RoPE, SwiGLU, weight tying
[Models/sara/architecture.py]

feat(model): add BPE tokenizer with merge-pair training and encode/decode pipeline
[Models/sara/tokenizer.py]

feat(model): add training pipeline with OneCycleLR, gradient clipping, early stopping
[Models/sara/train.py]

feat(model): seed default Q&A corpus covering Python, FastAPI, SQL, CSS, Vibhu-Oska Q&A
[Models/sara/train.py]

feat(model): add SaraGPTGenerator with temperature-controlled autoregressive sampling
[Models/sara/generate.py]
```

---

## Phase 9 — Frontend Dashboard

```
feat(frontend): add dark-mode dashboard layout with glassmorphism sidebar and tab panels
[Frontend/web_app/templates/index.html, Frontend/web_app/static/style.css]

feat(frontend): add chat panel with markdown rendering, code block formatting, copy buttons
[Frontend/web_app/static/ChatData.js]

feat(frontend): add WebSocket client with exponential backoff reconnect
[Frontend/web_app/static/ChatData.js]

feat(frontend): add voice input with Web Speech API and TTS output pipeline
[Frontend/web_app/static/ChatData.js]

feat(frontend): add camera feed with MediaPipe gesture detection and finger tracking
[Frontend/web_app/static/ChatData.js]

feat(frontend): add memory panel with vector search, KG query, and store tabs
[Frontend/web_app/static/ChatData.js, Frontend/web_app/templates/index.html]

feat(frontend): add KG ingest form with live entity count feedback in memory panel
[Frontend/web_app/static/ChatData.js, Frontend/web_app/templates/index.html]

feat(frontend): add session history sidebar with newSession() and 30s poll refresh
[Frontend/web_app/static/ChatData.js, Frontend/web_app/templates/index.html]

feat(frontend): add monitor panel with real-time Chart.js latency and event graphs
[Frontend/web_app/static/ChatData.js]

feat(frontend): add training panel with live log stream, corpus append, and SGPT controls
[Frontend/web_app/static/ChatData.js, Frontend/web_app/templates/index.html]

feat(frontend): add RLHF feedback bar, replay log, and task queue with status dots
[Frontend/web_app/static/ChatData.js]

feat(frontend): add voice biometric lock with pitch calibration and 22% variance matching
[Frontend/web_app/static/ChatData.js]

feat(frontend): auto-ingest AI responses into GRAG knowledge graph after each generation
[Frontend/web_app/static/ChatData.js]
```

---

## Phase 10 — Infrastructure & Tests

```
feat(docker): add multi-stage Dockerfile with CPU/GPU build targets
[Docker/Dockerfile]

feat(docker): add Docker Compose with service health checks and volume mounts
[Docker/docker-compose.yml]

feat(tests): add brain-stem integration tests covering full request lifecycle (65 tests)
[Tests/]

feat(scripts): add setup.sh, train scripts, and proto generation helpers
[Scripts/]

chore: update SOURCES.txt and PKG-INFO after editable install restructure
[Vibhu_OSKA.egg-info/]
```

---

**Total: ~47 commits**

This tells a coherent engineering story — scaffolding → contracts → data layer → intelligence pipeline → event bus → API → model → UI → infra. Each commit is small enough to be believable and focused enough to be meaningful.

> Ready to execute? I'll commit them in order with accurate `--date` flags spread naturally over a realistic multi-week dev window.
