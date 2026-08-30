# Data — Persistent Storage

Runtime data, training corpora, and vector embeddings.

## Structure

```mermaid
graph TB
    DATA[Data/] --> DB[vibhu_oska.db<br/>SQLite + ChromaDB]
    DATA --> TR[training/<br/>Training Corpora]
    DATA --> CH[chromadb/<br/>Vector Embeddings]

    TR --> KARSH[karsh/<br/>Karsh Training Data]
    TR --> ROUTER[router/<br/>Router Training Data]

    DB --> SQ[SQLite<br/>Sessions, Chats, Telemetry]
    DB --> VE[ChromaDB<br/>Semantic Vectors]
```

## Files

| Path | Purpose |
|------|---------|
| `vibhu_oska.db` | Combined SQLite + ChromaDB database |
| `training/karsh/corpus.txt` | Karsh training Q&A pairs |
| `training/router/` | Router training data |
| `chromadb/` | ChromaDB vector store files |

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant DC as DataCore
    participant DB as SQLite
    participant V as ChromaDB

    U->>DC: Save chat
    DC->>DB: INSERT chat message
    DC->>V: Store embedding
    U->>DC: Query memory
    DC->>V: Semantic search
    V-->>DC: Similar chunks
    DC->>DB: Get session history
    DB-->>DC: Chat history
    DC-->>U: Combined context
```
