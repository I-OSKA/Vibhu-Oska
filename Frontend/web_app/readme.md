# Frontend — Web Dashboard

Single-page application dashboard for real-time interaction with Vibhu-Oska AI-OS.

## Architecture

```mermaid
graph TB
    subgraph "Frontend"
        HTML[index.html<br/>Dashboard UI]
        JS[ChatData.js<br/>WebSocket Client]
        CSS[Styles<br/>Dark Glassmorphism]
    end

    subgraph "Communication"
        WS[WebSocket /ws]
        REST[REST API /api/v1/*]
    end

    HTML --> JS
    JS --> WS
    JS --> REST
    WS --> GW[Backend Gateway]
    REST --> GW
```

## Files

| Directory | Purpose |
|---|---|
| `templates/index.html` | Main dashboard HTML (single page) |
| `static/ChatData.js` | WebSocket client, UI logic, training controls |
| `static/` | CSS, images, static assets |

## Features

- Real-time WebSocket chat
- Training panel (start/monitor Karsh training)
- System monitor (CPU, GPU, RAM, disk)
- Session management
- Dark glassmorphism UI theme

## Communication

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant WS as WebSocket
    participant GW as Gateway

    U->>FE: Type message
    FE->>WS: Send prompt
    WS->>GW: Process
    GW-->>WS: Response
    WS-->>FE: Display
    FE-->>U: Show response
```
