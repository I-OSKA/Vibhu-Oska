# Backend — Vibhu-Oska AI-OS Server

## Structure

```
Backend/
├── Gateway/               ← FastAPI app + WebSocket + MCP server
│   ├── App.py             ← Main FastAPI application
│   └── McpServer.py       ← Model Context Protocol server
├── Core/                  ← All core modules
│   ├── MainCore/          ← Trimurti + Tridevis foundation
│   ├── SpecializedCore/   ← Domain specialist cores
│   ├── BackupCore/        ← CPU fallback (Nandi)
│   ├── ContextManager/    ← Token budget enforcement
│   ├── EventBus/          ← ZeroMQ pub/sub messaging
│   └── Watchdog/          ← Health monitoring daemon
├── Plugins/               ← Plugin system
│   ├── Logger/            ← Structured logging
│   └── ToolRegistry/      ← Service registration
└── backend.md
```

## Entry Point

```bash
python -m uvicorn Backend.Gateway.App:app --host 0.0.0.0 --port 8100 --reload
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Web UI |
| `/health` | GET | System health check |
| `/api/v1/chat` | POST | REST chat endpoint |
| `/ws` | WebSocket | Real-time bidirectional |
| `/ws/stream` | WebSocket | Token-by-token streaming |

## Core Count

16 cores total:
- MainCore: 10 (Trimurti + Tridevis + extras)
- SpecializedCore: 7 domains
- Supporting: 3 (Backup, Context, Watchdog)
