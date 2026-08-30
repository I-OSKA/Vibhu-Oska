# MonitoringCore — Saraswati (Gyan/Knowledge)

## Role
Telemetry, logging, and system knowledge. Subscribes to EventBus and persists all events.

## Architecture

```
MonitoringCore
├── EventBus subscriber      → Listens to all topics
├── SQLite event store       → Persistent event log
├── Metrics aggregator       → System health metrics
└── Alert engine             → Threshold-based alerts
```

## Events Tracked

- `core.health` — Core health status changes
- `training.progress` — Training epoch/loss updates
- `inference.request` — Request/response metrics
- `system.error` — Error events from all cores
- `alert.triggered` — Alert threshold violations

## SQLite Schema

```sql
CREATE TABLE events (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    source TEXT NOT NULL,
    payload TEXT,
    timestamp REAL NOT NULL
);
```

## Querying Events

```python
monitoring = MonitoringCore.get_instance()
recent = await monitoring.get_recent_events(topic="core.health", limit=100)
```
