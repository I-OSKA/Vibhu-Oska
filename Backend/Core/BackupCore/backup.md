# BackupCore — Nandi (Vishwas/Faith)

## Role
Last-line-of-defense fallback. When CognitionCore/GPU fails, BackupCore handles responses via CPU-based rules.

## Architecture

```
BackupCore
├── _reason()                → Rule-based response generation
├── BilingualCore (legacy)   → Hindi/English intent mapping
├── Intent Matcher           → Pattern-based intent detection
└── Response Templates       → Pre-built response library
```

## Activation Triggers

- CognitionCore returns error
- GPU OOM (out of memory)
- Model not loaded
- Timeout exceeded
- Explicit fallback request

## Intent Categories

| Intent | Example | Response |
|--------|---------|----------|
| greeting | "hello", "namaste" | Greeting template |
| identity | "who are you" | Karsh identity response |
| status | "system status" | Hardware telemetry |
| math | "2+2" | Calculated answer |
| help | "help" | Available commands |
| os_command | "open chrome" | AutomationCore delegation |

## BilingualCore (Legacy)

The BackupCore contains a legacy BilingualCore for Hindi intent mapping. This is being superseded by LanguageCore but remains for backward compatibility.
