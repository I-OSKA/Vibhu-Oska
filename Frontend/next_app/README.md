# Vibhu-Oska AI-OS — Frontend (Next.js)

## Overview
The Vibhu-Oska frontend is a **Next.js 15 + React 19** web application that provides the operator interface to the AI-OS. It communicates with the backend via:
- **REST API** (`/api/*`) — session management, settings, health checks
- **WebSocket** (`/ws/stream`) — real-time token-by-token streaming responses
- **WebSocket** (`/ws`) — event bus subscriptions, system notifications

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Next.js Frontend                │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Chat UI │  │ Settings │  │ System Panel  │  │
│  └────┬─────┘  └────┬─────┘  └──────┬────────┘  │
│       │              │               │            │
│  ┌────▼──────────────▼───────────────▼────────┐  │
│  │              API Client Layer              │  │
│  └────┬──────────────┬───────────────┬────────┘  │
└───────┼──────────────┼───────────────┼───────────┘
        │ REST         │ WebSocket     │ WebSocket
┌───────▼──────────────▼───────────────▼───────────┐
│              FastAPI Backend (Port 8000)          │
└──────────────────────────────────────────────────┘
```

## Getting Started

### Prerequisites
- Node.js 18+
- Backend running on `http://localhost:8000`

### Development
```bash
cd Frontend/next_app
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Build
```bash
npm run build
npm start
```

## Key Features
- **Real-time streaming** — Token-by-token response display via WebSocket
- **Session management** — Create, switch, and delete chat sessions
- **System monitoring** — View core health, GPU usage, thermal state
- **Settings panel** — Adjust temperature, context window, quantization
- **Responsive design** — Works on desktop and mobile

## Tech Stack
- **Framework**: Next.js 15 (App Router)
- **UI**: React 19, Tailwind CSS 4, shadcn/ui
- **State**: React hooks (useState, useEffect)
- **Transport**: WebSocket + fetch API
- **Fonts**: Geist (Vercel)

## Backend Connection
The frontend expects the backend at `http://localhost:8000`. Configure via environment variable:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```
