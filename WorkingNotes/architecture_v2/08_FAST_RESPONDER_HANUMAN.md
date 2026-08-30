# FastResponder — Hanuman (The Swift Devotee)

**Divine Name**: Hanuman (हनुमान) — The Swift Devotee  
**System Name**: FastResponder  
**Role**: Instant pattern matching, deterministic responses  
**Domain**: Greetings, math, time, identity, help

---

## Philosophy

Hanuman is the devoted servant of Rama, known for his incredible speed and unwavering devotion. FastResponder is the devoted servant of the system, known for its incredible speed in handling simple patterns.

When a user says "hello" or asks "what time is it", there's no need for full inference. FastResponder handles these instantly — like Hanuman leaping across the ocean.

---

## Responsibilities

### Instant Patterns
- **Greetings** — hello, hi, hey, good morning/afternoon/evening
- **Identity** — who are you, what is vibhu-oska
- **Status** — system status, health check
- **Telemetry** — CPU, GPU, RAM usage
- **Time/Date** — current time, date
- **OS Info** — platform, machine info
- **Help** — command reference
- **Math** — arithmetic expressions, sqrt, factorial
- **Acknowledgements** — ok, thanks, got it

---

## Workflow

```mermaid
flowchart TD
    A[Prompt] --> B{Math?}
    B -->|Yes| C[Evaluate Math]
    B -->|No| D{Greeting?}
    D -->|Yes| E[Return Greeting]
    D -->|No| F{Identity?}
    F -->|Yes| G[Return Identity]
    F -->|No| H{Time/Date?}
    H -->|Yes| I[Return Time]
    H -->|No| J{Status?}
    J -->|Yes| K[Return Status]
    J -->|No| L[Return None<br/>Fall Through]

    style C fill:#2ecc71,color:#fff
    style E fill:#3498db,color:#fff
    style G fill:#9b59b6,color:#fff
    style I fill:#f39c12,color:#fff
    style K fill:#e74c3c,color:#fff
    style L fill:#95a5a6,color:#fff
```

---

## Key Files

| File | Purpose |
|------|---------|
| `FastResponder.py` | Main instant response engine |
| `ResponseCache.py` | Caches frequent responses |

---

**Boundaries**: Hanuman serves but does not lead. He is fast but not wise. He handles the simple so that others can handle the complex.
