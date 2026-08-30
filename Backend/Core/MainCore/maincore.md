# MainCore — Trimurti + Tridevis Foundation

## Architecture

MainCore is the divine intelligence layer of Vibhu-Oska AI-OS. It implements the Trimurti (Brahma-Vishnu-Shiva) and Tridevis (Saraswati-Lakshmi-Parvati) framework.

```
MainCore/
├── OrchestratorCore/    ← Brahma (Srishti/Creation) — Routing hub
├── CognitionCore/       ← Vishnu (Sthiti/Preservation) — Inference engine
├── EvolutionCore/       ← Shiva (Samhara/Destruction) — Self-improvement
├── MonitoringCore/      ← Saraswati (Gyan/Knowledge) — Telemetry
├── OptimizationCore/    ← Lakshmi (Samriddhi/Prosperity) — Caching
├── ValidationCore/      ← Yama (Justice) — Input/output guard
├── FastResponder/       ← Hanuman (Seva/Service) — Instant patterns
├── LanguageCore/        ← Multi-language umbrella (12 languages)
├── BackupCore/          ← Nandi (Vishwas/Faith) — Last-line fallback
└── ContextManager/      — Token budget enforcement
```

## Cores

| Core | Deity | Role |
|------|-------|------|
| OrchestratorCore | Brahma | Routes requests to correct specialist |
| CognitionCore | Vishnu | Karsh model inference + DeepThought mode |
| EvolutionCore | Shiva | GRPO reinforcement learning loop |
| MonitoringCore | Saraswati | Logs, metrics, telemetry |
| OptimizationCore | Lakshmi | Query cache, context compression |
| ValidationCore | Yama | Input sanitization, schema validation |
| FastResponder | Hanuman | Deterministic instant patterns |
| LanguageCore | — | Multi-language detection + templates |
| BackupCore | Nandi | CPU fallback when GPU fails |
| ContextManager | — | Token budget enforcement |

## Data Flow

```
User Input
    ↓
OrchestratorCore (Brahma)
    ├── FastResponder (Hanuman) → instant if pattern matches
    ├── CognitionCore (Vishnu) → Karsh inference
    │   └── DeepThought mode → multi-path reflection
    ├── EvolutionCore (Shiva) → training loop
    └── BackupCore (Nandi) → CPU fallback
    ↓
Response
```

## Adding New Cores

1. Create directory under `MainCore/`
2. Implement core class with `initialize()`, `execute()`, `health_check()`
3. Register in `OrchestratorCore._register_cores()`
4. Add to this readme
