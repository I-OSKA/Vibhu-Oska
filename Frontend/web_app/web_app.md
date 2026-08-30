# Frontend — Vibhu-Oska User Interface

## Components

```
Frontend/
├── web_app/               ← Primary web interface
│   ├── templates/         ← Jinja2 HTML templates
│   ├── static/            ← CSS, JS, images
│   └── web_app.md
├── next_app/              ← Next.js app (Phase 4)
│   └── next_app.md
└── unity_app/             ← Unity 3D interface (Phase 5)
    └── unity_app.md
```

## Web App (Primary)

- **Framework**: FastAPI + Jinja2 + vanilla JS
- **Port**: 8100 (same as backend)
- **WebSocket**: ws://localhost:8100/ws for real-time chat
- **Streaming**: ws://localhost:8100/ws/stream for token-by-token

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| Frontend | HTML/CSS/JS |
| Real-time | WebSocket |
| Styling | Glassmorphism (dark mode) |

## Building

Web app is served directly by FastAPI — no build step needed.
