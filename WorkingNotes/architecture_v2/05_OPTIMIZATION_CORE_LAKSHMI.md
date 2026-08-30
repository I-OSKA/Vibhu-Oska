# OptimizationCore — Lakshmi (Goddess of Abundance)

**Divine Name**: Lakshmi (लक्ष्मी) — Goddess of Abundance  
**System Name**: OptimizationCore  
**Consort Of**: Vishnu (CognitionCore)  
**Domain**: Context compression, caching, VRAM management  
**Symbol**: Lotus — purity and efficiency

---

## Philosophy

Lakshmi brings prosperity, fortune, and abundance. She ensures there is always enough — never wasteful, never lacking. OptimizationCore ensures the system runs **efficiently** — maximizing performance, minimizing waste.

She compresses context to fit token budgets. She caches responses to avoid redundant work. She manages VRAM to ensure the 8GB budget is never exceeded.

---

## Responsibilities

### What Lakshmi Optimizes
- **Context size** — compresses, prunes, prioritizes
- **Response cache** — stores and retrieves frequent responses
- **Token efficiency** — minimizes prompt size
- **VRAM budget** — manages 8GB constraint

### What Lakshmi Does NOT Do
- ❌ Does NOT route requests (that's Brahma)
- ❌ Does NOT reason or generate (that's Vishnu)
- ❌ Does NOT observe or monitor (that's Saraswati)

---

## Workflow

### Context Optimization

```mermaid
flowchart TD
    A[Context Chunks] --> B[Sort by<br/>Relevance]
    B --> C[Filter<br/>Corrupted Data]
    C --> D[Compress<br/>Whitespace]
    D --> E{Exceeds<br/>Token Budget?}
    E -->|Yes| F[Truncate<br/>Low Priority]
    E -->|No| G[Return<br/>Optimized Context]
    F --> G

    style A fill:#00b894,color:#fff
    style C fill:#00cec9,color:#fff
    style F fill:#e17055,color:#fff
```

### Cache Management

```mermaid
flowchart TD
    A[Query] --> B[Check Cache]
    B -->|Hit| C[Return Cached]
    B -->|Miss| D[Proceed to<br/>Inference]
    D --> E[Save Response<br/>to Cache]

    style A fill:#00b894,color:#fff
    style C fill:#2ecc71,color:#fff
    style E fill:#3498db,color:#fff
```

---

## Key Files

| File | Purpose |
|------|---------|
| `OptimizationCore.py` | Main optimization engine |
| `VRAMManager.py` | VRAM budget management |
| `BudgetAllocator.py` | Resource allocation across cores |

---

**Boundaries**: Lakshmi optimizes but does not create. She preserves abundance but does not reason. She is the efficiency within the system, not the intelligence.
