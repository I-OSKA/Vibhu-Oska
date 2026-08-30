# Vibhu-Oska AI-OS — Project Context

## What This Is
Vibhu-Oska is a **sovereign, locally-hosted AI operating system** — a complete autonomous AI layer that runs entirely on user hardware. Zero cloud dependency. Zero external APIs for core logic.

## Architecture: Trimurti + Tridevis

### Trimurti (Primary Cores)
| Core | Deity | Role |
|------|-------|------|
| **OrchestratorCore** | Brahma | Request lifecycle, routing, backup fallback |
| **CognitionCore** | Vishnu | Karsh model inference, deep thinking (MCTS) |
| **EvolutionCore** | Shiva | GRPO reinforcement learning, model evolution |

### Tridevis (Supporting Cores)
| Core | Deity | Role |
|------|-------|------|
| **MonitoringCore** | Saraswati | Telemetry, health, EventBus metrics |
| **OptimizationCore** | Lakshmi | Prompt optimization, caching, resource allocation |
| **Training Pipeline** | Parvati | Corpus management, GRPO training loop |

### Supporting Tools
| Core | Deity | Role |
|------|-------|------|
| **ValidationCore** | Yama | Input sanitization, output validation, security |
| **FastResponder** | Hanuman | Sub-50ms deterministic instant patterns |
| **BackupCore** | Nandi | CPU-only contingency when GPU cores fail |

### Specialized Cores
- **DataCore** — ChromaDB + SQLite + GRAG (Graph RAG)
- **LanguageCore** — 12-language umbrella (hi, en, sa, mr, bn, ta, te, gu, kn, ml, pa, ur)
- **VoiceCore** — Wake-word + Vosk STT + pyttsx3 TTS
- **AutomationCore** — OS-level actions (files, clipboard, keyboard)
- **HardwareAdapter** — Zero-interference hardware detection, power tier classification
- **QuantumEngine** — CPU quantum-inspired optimization with usage limits

## Tech Stack
- **Backend**: FastAPI, ZeroMQ EventBus, ChromaDB, SQLite, PyTorch
- **Frontend**: Next.js 15, React 19, Tailwind CSS 4, shadcn/ui
- **Models**: Karsh (custom GPT), Router (task/target classifier)
- **Platform**: Windows (PowerShell), CUDA GPU support

## Key Conventions
- All modules import from `Backend.Core.*` or `Backend.Plugins.*`
- Use `structlog` for logging, `psutil` for system info, `pynvml` for GPU
- Singleton pattern: `ClassName.get_instance()`
- Async-first: all core methods are `async def`
- Event-driven: ZeroMQ EventBus with topic-based subscriptions
- Zero external API dependency for core logic

## Testing
```bash
# Run all tests
.venv\Scripts\python.exe -m pytest Tests/ -v

# Run specific test
.venv\Scripts\python.exe -m pytest Tests/test_specialists_integration.py -v
```

## Hardware Profile
- GPU: NVIDIA RTX 4060 Laptop (8GB VRAM, CUDA)
- RAM: System RAM
- Platform: Windows 11
