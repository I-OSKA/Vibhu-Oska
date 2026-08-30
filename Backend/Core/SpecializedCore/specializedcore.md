# SpecializedCore — Domain Expert Cores

## Architecture

```
SpecializedCore/
├── CodingDomain/            ← 9 coding specialists
│   ├── PythonCore
│   ├── JavaScriptCore
│   ├── SQLCore
│   ├── GoCore
│   ├── RustCore
│   ├── CppCore
│   ├── BashShellCore
│   ├── RegexCore
│   └── CodingRouter
├── RealWorldDomain/         ← 10 real-world specialists
│   ├── FileSystemCore
│   ├── NetworkCore
│   ├── DatabaseAdminCore
│   ├── SystemAdminCore
│   ├── SecurityCore
│   ├── ExcelCore
│   ├── KnowledgeCore
│   ├── WebScrapingCore
│   ├── CloudCore
│   └── RealWorldRouter
├── AutomationCore/          ← OS executive + AppController
├── DesignCore/              ← HTML/CSS generation
├── DataCore/                ← Data processing
├── DistributionCore/        ← Public build packaging
├── ImageGenerationCore/     ← Image generation pipeline
└── VoiceCore/               ← Voice I/O (STT + TTS)
```

## Routing

Each domain has a router that dispatches to the correct specialist:

```
Prompt → CodingRouter → detects "python" → PythonCore
Prompt → RealWorldRouter → detects "file" → FileSystemCore
```

## Integration

Specialists register with OrchestratorCore and are invoked when domain-specific queries are detected.
