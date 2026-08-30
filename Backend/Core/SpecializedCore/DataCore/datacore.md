# DataCore — Persistent Storage Layer

## Architecture

```
DataCore
├── SQLite                   → Relational state (sessions, chat history, config)
├── ChromaDB                 → Semantic vector storage (memory, embeddings)
├── GraphRAG                 → Knowledge graph (entities, relationships)
└── File I/O                 → Corpus, training data, models
```

## SQLite Tables

| Table | Purpose |
|-------|---------|
| `sessions` | User session tracking |
| `chat_messages` | Conversation history |
| `config` | System configuration |
| `events` | Monitoring event log |
| `knowledge_entities` | GraphRAG entities |
| `knowledge_relations` | GraphRAG relationships |

## ChromaDB Collections

| Collection | Purpose |
|------------|---------|
| `memory` | Semantic memory store |
| `corpus` | Training corpus embeddings |
| `context` | Retrieved context vectors |

## GraphRAG

Knowledge graph traversal for context enrichment:
1. Extract entities from query
2. Find related entities in graph
3. Retrieve surrounding context
4. Merge into response context

## API

```python
data = DataCore.get_instance()
await data.create_session(session_id, user_id)
await data.save_chat_message(msg_id, session_id, role, content)
history = await data.get_session_history(session_id, limit=10)
results = await data.query_memory("query text", top_k=5)
```
