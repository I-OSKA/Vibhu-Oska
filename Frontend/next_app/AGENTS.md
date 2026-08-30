<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# Vibhu-Oska Frontend Agent Rules

## Project Structure
```
Frontend/next_app/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main chat interface
│   ├── globals.css         # Global styles (Tailwind)
│   └── api/                # API routes (if needed)
├── components/             # React components
│   ├── ui/                 # shadcn/ui primitives
│   ├── chat/               # Chat interface components
│   └── settings/           # Settings panel components
├── lib/                    # Utility functions
│   └── utils.ts            # cn() helper, etc.
├── public/                 # Static assets
├── CLAUDE.md               # Project context for Claude
├── AGENTS.md               # This file — agent instructions
└── ARCHITECTURE.md         # Detailed architecture docs
```

## Coding Conventions
- **TypeScript** for all components and utilities
- **Functional components** with hooks (no class components)
- **Tailwind CSS** for styling (no CSS modules)
- **shadcn/ui** for UI primitives (Button, Input, Card, etc.)
- **Async/await** for all API calls
- **Error boundaries** for error handling

## Backend Communication
- Backend runs at `http://localhost:8000`
- WebSocket at `ws://localhost:8000/ws/stream` for streaming
- REST at `http://localhost:8000/api/*` for CRUD
- Always handle connection errors gracefully

## Component Patterns
```tsx
// Good: Functional component with typed props
interface ChatMessageProps {
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
}

export function ChatMessage({ content, role, timestamp }: ChatMessageProps) {
  return (
    <div className={cn("flex", role === "user" ? "justify-end" : "justify-start")}>
      <p>{content}</p>
    </div>
  );
}
```

## Testing
- Unit tests: `npm test`
- E2E tests: `npm run test:e2e` (when implemented)
- Lint: `npm run lint`
- Type check: `npm run typecheck`
