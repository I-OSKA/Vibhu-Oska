# OrchestratorCore — Brahma (Srishti/Creation)

## Role
Central routing hub — decides which core handles each request.

## Architecture

```
OrchestratorCore
├── _route_request()         → Main inference path
├── _route_to_specialized()  → Specialist domain routing
├── _register_cores()        → Core registry
└── Health monitoring        → Watchdog integration
```

## Routing Logic

```
Input Prompt
    ↓
FastResponder.try_respond() → instant match?
    ├── YES → return fast response
    └── NO ↓
Specialist Router → domain match?
    ├── YES → delegate to specialist core
    └── NO ↓
CognitionCore → Karsh inference
    ↓
Response
```

## Core Registry

All cores register themselves with OrchestratorCore at startup. The orchestrator maintains a mapping of capabilities to cores for efficient routing.

## Adding a Core

```python
# In your core's initialize():
await state.orchestrator.register_core("my_core", self, capabilities=["task1", "task2"])
```

## Metrics

- `requests_routed`: Total requests routed
- `specialist_hits`: Requests handled by specialists
- `cognition_fallbacks`: Requests falling through to CognitionCore
- `avg_routing_ms`: Average routing decision time
