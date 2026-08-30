# OptimizationCore — Lakshmi (Samriddhi/Prosperity)

## Role
Query caching, context compression, and efficiency optimization.

## Architecture

```
OptimizationCore
├── LRU Query Cache          → Instant responses for repeated queries
├── Context Compressor       → Fits long contexts into token budget
├── Prompt Optimizer         → Rewrites queries for better retrieval
└── Response Dedup           → Identifies duplicate responses
```

## LRU Cache

- Stores query → response mappings
- Evicts least-recently-used entries
- Hit rate tracked via EventBus metrics
- Configurable max size (default 1000 entries)

## Context Compression

When context exceeds token budget:
1. Summarize older messages
2. Keep recent messages verbatim
3. Merge semantic chunks
4. Priority-rank by relevance

## Usage

```python
optimization = OptimizationCore.get_instance()

# Check cache
cached = await optimization.check_query_cache(prompt)
if cached:
    return cached  # Instant response

# Save to cache
await optimization.save_response_cache(prompt, response)
```
