# 09 — MonitoringCore: Proactive Actor

> **Evolution of the telemetry sink.** The current MonitoringCore is a passive observer — it logs events and generates reports. This document defines its evolution into a **proactive actor** that detects anomalies in real-time, triggers corrective actions, signals training needs to EvolutionCore, and manages BackupCore pool allocation.

## 1. Overview

```
Current State                    Target State
─────────────                    ─────────────
┌──────────────┐                 ┌──────────────────────────┐
│ MonitoringCore│                 │      MonitoringCore      │
│              │                 │  ┌────────────────────┐  │
│  • Subscribe │                 │  │   AnomalyDetector   │  │
│  • Log       │  ────────►     │  │  (ML-based)         │  │
│  • Reflect   │                 │  └────────┬───────────┘  │
│  • Evaluate  │                 │  ┌────────▼───────────┐  │
│  • Report    │                 │  │   ProactiveActor    │  │
│              │                 │  │  (takes action)     │  │
└──────────────┘                 │  └────────┬───────────┘  │
                                 │  ┌────────▼───────────┐  │
                                 │  │  EvolutionTrigger   │  │
                                 │  │  BackupScaleSignal  │  │
                                 │  │  SystemHealthModel  │  │
                                 │  └────────────────────┘  │
                                 └──────────────────────────┘
```

**Key shift:** MonitoringCore transitions from *observe → log → alert* to **observe → detect → act → recover**.

---

## 2. AnomalyDetector — ML-Based Anomaly Detection

### Purpose

Runs lightweight statistical and ML models over the stream of telemetry metrics to identify deviations from normal system behavior. Unlike simple threshold checks, AnomalyDetector learns the system's baseline and flags statistically significant outliers.

### Detection Methods

| Method | Description | Use Case |
|---|---|---|
| **Z-Score** | Flags values > N standard deviations from rolling mean | CPU/RAM spikes, response time outliers |
| **IQR Fence** | Interquartile range outlier detection | Non-Gaussian metric distributions |
| **EWMA** | Exponentially weighted moving average drift | Gradual degradation (memory leaks, thermal creep) |
| **Isolation Forest** | Lightweight unsupervised ensemble (scikit-learn) | Multi-variate correlated anomalies |
| **LSTM Autoencoder** | Temporal sequence reconstruction error | Time-series anomaly detection on metric windows |

### Rolling Window Buffer

```python
@dataclass
class MetricWindow:
    metric_name: str
    values: deque[float]       # Fixed-size window (default 500)
    timestamps: deque[float]
    window_size: int = 500
    ewma_alpha: float = 0.3    # Smoothing factor for EWMA

class AnomalyDetector:
    def __init__(self, config: dict):
        self.windows: dict[str, MetricWindow] = {}
        self.z_threshold: float = config.get("z_threshold", 3.0)
        self.iqr_multiplier: float = config.get("iqr_multiplier", 1.5)
        self.isolation_forest: IsolationForest | None = None
        self.lstm_autoencoder: Optional[nn.Module] = None
        self.baseline_trained: bool = False
        self.min_samples_for_baseline: int = config.get("min_baseline_samples", 200)
```

### Detection Pipeline

```
Metric Ingest
     │
     ▼
┌─────────────┐    miss?    ┌──────────────┐
│ Update       │───────────►│ Return None   │
│ Rolling Window│           │ (insufficient │
└──────┬──────┘            │  data)        │
       │ hit               └──────────────┘
       ▼
┌──────────────┐   normal   ┌──────────────┐
│ Z-Score Check │──────────►│ IQR Check     │
└──────┬───────┘  anomaly   └──────┬───────┘
       │ anomaly          anomaly  │ anomaly
       ▼                            ▼
┌──────────────┐          ┌──────────────┐
│ AnomalySignal │          │ AnomalySignal │
│ (z-score)     │          │ (iqr)         │
└──────────────┘          └──────────────┘
       │                            │
       └────────────┬───────────────┘
                    ▼
            ┌──────────────┐  normal   ┌──────────────┐
            │ EWMA Check   │─────────►│ AnomalySignal │
            └──────┬───────┘ anomaly  │ (ewma_drift)  │
                   │                  └──────────────┘
                   ▼
            ┌──────────────────┐  normal   ┌──────────────┐
            │ Isolation Forest  │─────────►│ No Anomaly    │
            │ (multi-variate)   │ anomaly  └──────────────┘
            └──────┬───────────┘
                   │ anomaly
                   ▼
            ┌──────────────────┐
            │ AnomalySignal    │
            │ (multivariate)   │
            └──────────────────┘
```

### AnomalySignal Output

```python
@dataclass
class AnomalySignal:
    metric_name: str
    anomaly_type: str           # "z_score" | "iqr" | "ewma_drift" | "multivariate"
    severity: float             # 0.0 - 1.0 (normalized confidence)
    current_value: float
    expected_range: tuple[float, float]
    timestamp: float
    context: dict               # Additional metadata for ProactiveActor
```

### Tracked Metrics

| Metric Name | Source | Frequency | Unit |
|---|---|---|---|
| `cpu_percent` | AutomationCore.get_system_info | 5s | % |
| `ram_used_gb` | AutomationCore.get_system_info | 5s | GB |
| `gpu_vram_used_gb` | AutomationCore.get_system_info | 5s | GB |
| `gpu_temperature` | AutomationCore.get_system_info | 10s | °C |
| `inference_time_ms` | CognitionCore | per request | ms |
| `cache_hit_rate` | OptimizationCore | 30s | ratio |
| `task_queue_depth` | OrchestratorCore | 5s | count |
| `event_bus_latency` | EventBus | 10s | ms |
| `error_rate_1m` | MonitoringCore | 60s | count/min |
| `token_usage_per_request` | CognitionCore | per request | tokens |

---

## 3. ProactiveActor — Taking Action on Anomalies

### Purpose

When AnomalyDetector fires an AnomalySignal, ProactiveActor **executes corrective actions** — not just alerts. It implements the system's self-healing reflex.

### Action Registry

| Anomaly Type | Severity Range | Action | Target Core |
|---|---|---|---|
| `cpu_percent` spike | 0.7 - 1.0 | Route queries to CPU-only fallback model | CognitionCore |
| `gpu_vram_used_gb` high | 0.8 - 1.0 | Offload inactive model weights to disk | OptimizationCore |
| `gpu_temperature` high | 0.85 - 1.0 | Throttle inference batch size, emit cooldown alert | OptimizationCore |
| `inference_time_ms` spike | 0.6 - 1.0 | Increase cache TTL, prioritize cached responses | OptimizationCore |
| `cache_hit_rate` low | 0.5 - 0.8 | Trigger cache prewarming for top-N frequent queries | OptimizationCore |
| `task_queue_depth` high | 0.7 - 1.0 | Signal BackupCore to expand worker pool | BackupCore |
| `event_bus_latency` high | 0.7 - 1.0 | Enable message batching, reduce heartbeat frequency | EventBus |
| `error_rate_1m` high | 0.8 - 1.0 | Isolate failing core, route around it | OrchestratorCore |
| `ram_used_gb` high | 0.75 - 1.0 | Flush in-memory caches, compress context windows | OptimizationCore |

### Action Execution Flow

```
AnomalySignal received
         │
         ▼
┌────────────────────┐
│ Severity Check      │──── < 0.5 ────► Log only, no action
└────────┬───────────┘
         │ >= 0.5
         ▼
┌────────────────────┐
│ Lookup Action       │
│ Registry            │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Cooldown Check      │──── recent? ──► Skip (prevent action thrashing)
│ (per-metric TTL)    │
└────────┬───────────┘
         │ expired
         ▼
┌────────────────────┐
│ Execute Action      │
│ (async dispatch)    │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Publish ActionEvent │
│ to EventBus         │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Record in           │
│ telemetry_logs      │
└────────────────────┘
```

### Cooldown Mechanism

```python
class ProactiveActor:
    def __init__(self, config: dict):
        self.action_cooldowns: dict[str, float] = {}   # metric -> last_action_timestamp
        self.cooldown_seconds: float = config.get("cooldown_seconds", 60.0)
        self.max_actions_per_minute: int = config.get("max_actions_per_minute", 5)
        self.action_count_window: deque[float] = deque(maxlen=20)

    def _can_act(self, metric_name: str) -> bool:
        now = time.time()
        # Per-metric cooldown
        last = self.action_cooldowns.get(metric_name, 0.0)
        if now - last < self.cooldown_seconds:
            return False
        # Global rate limit
        recent = [t for t in self.action_count_window if now - t < 60.0]
        if len(recent) >= self.max_actions_per_minute:
            return False
        return True
```

---

## 4. EvolutionTrigger — Signaling Training Needs

### Purpose

When ProactiveActor detects persistent or recurring anomalies that cannot be resolved through runtime actions alone, EvolutionTrigger signals **EvolutionCore** that the model or configuration needs retraining.

### Trigger Conditions

| Condition | Threshold | Signal |
|---|---|---|
| Same anomaly type fires > N times in window | `recurrence_count >= 5` within 1 hour | `TRAINING_RECOMMENDED` |
| Cache hit rate remains below baseline | `hit_rate < 0.3` for > 30 minutes | `ROUTER_RETRAIN_NEEDED` |
| Inference time degrades progressively | `p95_time` increases > 20% over 2 hours | `MODEL_PRUNING_RECOMMENDED` |
| Error rate on specific task type | `error_rate > 0.1` for task_type > 10 min | `TASK_SPECIFIC_FINE_TUNE` |
| Context compression ratio drops | `compression_ratio < 0.5` sustained | `CONTEXT_MODEL_RETRAIN` |

### Signal Format

```python
@dataclass
class EvolutionSignal:
    signal_type: str        # "TRAINING_RECOMMENDED" | "ROUTER_RETRAIN" | etc.
    target_model: str       # Model identifier
    reason: str             # Human-readable explanation
    evidence: list[dict]    # AnomalySignal history that led to this
    priority: str           # "low" | "medium" | "high" | "critical"
    suggested_action: str   # "fine_tune" | "retrain" | "prune" | "distill"
    timestamp: float
```

### Integration with EvolutionCore

```
EvolutionTrigger ──publish──► Topics.EVOLUTION_SIGNAL
                                        │
                                        ▼
                              ┌──────────────────┐
                              │ EvolutionCore     │
                              │  • Queues job     │
                              │  • Loads dataset  │
                              │  • Runs training  │
                              │  • Publishes      │
                              │    TRAINING_DONE  │
                              └──────────────────┘
```

---

## 5. BackupScaleSignal — Pool Scaling Requests

### Purpose

Monitors BackupCore's worker pool utilization and dynamically requests scale-up or scale-down based on system load and task queue depth.

### Scaling Logic

```python
class BackupScaleSignal:
    def __init__(self, config: dict):
        self.min_workers: int = config.get("min_workers", 1)
        self.max_workers: int = config.get("max_workers", 4)
        self.scale_up_threshold: float = config.get("scale_up_threshold", 0.8)
        self.scale_down_threshold: float = config.get("scale_down_threshold", 0.3)
        self.scale_cooldown: float = config.get("scale_cooldown", 120.0)  # seconds

    def evaluate(self, pool_metrics: dict) -> ScaleSignal | None:
        """
        pool_metrics = {
            "active_workers": int,
            "idle_workers": int,
            "queue_depth": int,
            "avg_task_duration_ms": float
        }
        """
        total = pool_metrics["active_workers"] + pool_metrics["idle_workers"]
        utilization = pool_metrics["active_workers"] / max(total, 1)

        if utilization > self.scale_up_threshold and total < self.max_workers:
            return ScaleSignal(direction="up", target=total + 1, reason="high_utilization")
        elif utilization < self.scale_down_threshold and total > self.min_workers:
            return ScaleSignal(direction="down", target=total - 1, reason="low_utilization")
        return None
```

### ScaleSignal Format

```python
@dataclass
class ScaleSignal:
    direction: str       # "up" | "down"
    target: int          # Target worker count
    reason: str          # Human-readable reason
    timestamp: float
```

---

## 6. SystemHealthModel — Predictive Health

### Purpose

A lightweight predictive model that forecasts system health metrics N minutes into the future, enabling **proactive** intervention before anomalies occur.

### Model Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  SystemHealthModel                       │
│                                                         │
│  Input Layer (10 features, 50 timesteps)                │
│  ┌─────────────────────────────────────────────┐       │
│  │ cpu, ram, vram, temp, cache_hit, queue,     │       │
│  │ error_rate, inference_time, bus_latency,    │       │
│  │ token_usage                                 │       │
│  └──────────────┬──────────────────────────────┘       │
│                 ▼                                       │
│  ┌──────────────────────────┐                          │
│  │ LSTM (hidden=32)         │  Lightweight: ~50KB      │
│  └──────────────┬───────────┘                          │
│                 ▼                                       │
│  ┌──────────────────────────┐                          │
│  │ Dense(32 → 10)           │  Forecast horizon:       │
│  │ ReLU → Dense(10 → 10)    │  5min, 15min, 30min     │
│  └──────────────┬───────────┘                          │
│                 ▼                                       │
│  Output: Predicted metric values + confidence          │
└─────────────────────────────────────────────────────────┘
```

### Prediction Output

```python
@dataclass
class HealthForecast:
    metric_name: str
    predictions: list[PredictionPoint]  # [5min, 15min, 30min]
    overall_health_score: float         # 0.0 - 1.0
    recommended_action: str             # "none" | "watch" | "intervene" | "critical"

@dataclass
class PredictionPoint:
    horizon_minutes: int
    predicted_value: float
    confidence_lower: float
    confidence_upper: float
```

### Proactive Intervention Triggers

| Forecast Condition | Action |
|---|---|
| `health_score < 0.3` at 15min horizon | Pre-emptive model offload |
| `gpu_temperature` predicted > 80°C at 5min | Throttle batch size NOW |
| `ram_used_gb` predicted > 14GB at 30min | Flush caches, compress context |
| `cache_hit_rate` predicted < 0.2 at 15min | Trigger cache prewarming |
| `queue_depth` predicted > 10 at 5min | Signal BackupCore scale-up |

---

## 7. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MonitoringCore (Proactive)                       │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    EventBus Subscriptions                         │  │
│  │  TASK_CREATED │ TASK_COMPLETED │ TASK_FAILED │ SYSTEM_ALERT      │  │
│  │  HEALTH_CHECK │ MONITORING_LOG │ EVOLUTION_DONE │ BACKUP_SCALE   │  │
│  └───────────────────────────┬───────────────────────────────────────┘  │
│                              │                                          │
│                              ▼                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐                   │
│  │   AnomalyDetector    │  │  SystemHealthModel    │                   │
│  │                      │  │  (LSTM Predictive)    │                   │
│  │  • Z-Score           │  │                      │                   │
│  │  • IQR               │  │  • 5min/15min/30min  │                   │
│  │  • EWMA              │  │    forecasts         │                   │
│  │  • Isolation Forest  │  │  • health_score      │                   │
│  │  • LSTM AE           │  │  • confidence bands  │                   │
│  └──────────┬───────────┘  └──────────┬───────────┘                   │
│             │ AnomalySignal           │ HealthForecast                 │
│             ▼                         ▼                                │
│  ┌──────────────────────────────────────────────────────┐             │
│  │                  ProactiveActor                       │             │
│  │                                                      │             │
│  │  Action Registry ─► Cooldown Check ─► Execute ─► Log │             │
│  └───────┬──────────────────┬───────────────┬───────────┘             │
│          │                  │               │                          │
│          ▼                  ▼               ▼                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │Evolution     │  │BackupScale   │  │ EventBus     │                │
│  │Trigger       │  │Signal        │  │ Publish      │                │
│  │              │  │              │  │ (actions)    │                │
│  │► EVOLUTION_  │  │► BACKUP_     │  │              │                │
│  │  SIGNAL      │  │  SCALE       │  │              │                │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘                │
│         │                 │                                            │
│         ▼                 ▼                                            │
│  ┌──────────────┐  ┌──────────────┐                                   │
│  │EvolutionCore │  │ BackupCore   │                                   │
│  └──────────────┘  └──────────────┘                                   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────┐             │
│  │              Telemetry Persistence                    │             │
│  │  telemetry_logs │ anomaly_history │ health_forecasts  │             │
│  │  action_log     │ evolution_signals│ scale_signals    │             │
│  └──────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Configuration

### MonitoringCore Proactive Config (default.yaml extension)

```yaml
monitoring:
  # ── Existing (passive) ──
  enabled: true
  log_retention_days: 30

  # ── Anomaly Detection ──
  anomaly_detection:
    enabled: true
    z_threshold: 3.0
    iqr_multiplier: 1.5
    ewma_alpha: 0.3
    isolation_forest_enabled: true
    lstm_autoencoder_enabled: false   # Enable when baseline data available
    min_baseline_samples: 200
    window_size: 500
    metrics_tracked:
      - cpu_percent
      - ram_used_gb
      - gpu_vram_used_gb
      - gpu_temperature
      - inference_time_ms
      - cache_hit_rate
      - task_queue_depth
      - event_bus_latency
      - error_rate_1m
      - token_usage_per_request

  # ── Proactive Actions ──
  proactive_actor:
    enabled: true
    cooldown_seconds: 60
    max_actions_per_minute: 5
    severity_threshold: 0.5
    actions:
      cpu_spike:
        metric: cpu_percent
        severity_min: 0.7
        action: route_to_cpu_fallback
      vram_high:
        metric: gpu_vram_used_gb
        severity_min: 0.8
        action: offload_inactive_weights
      thermal_throttle:
        metric: gpu_temperature
        severity_min: 0.85
        action: throttle_batch_size
      cache_miss:
        metric: cache_hit_rate
        severity_min: 0.5
        action: prewarm_cache
      queue_depth:
        metric: task_queue_depth
        severity_min: 0.7
        action: signal_backup_scale_up

  # ── Evolution Triggers ──
  evolution_trigger:
    enabled: true
    recurrence_threshold: 5          # Same anomaly N times → train signal
    recurrence_window_seconds: 3600
    cache_hit_low_threshold: 0.3
    cache_hit_low_duration_seconds: 1800
    inference_degradation_pct: 0.20
    inference_degradation_window_seconds: 7200

  # ── Backup Scaling ──
  backup_scale:
    enabled: true
    min_workers: 1
    max_workers: 4
    scale_up_threshold: 0.8
    scale_down_threshold: 0.3
    scale_cooldown_seconds: 120

  # ── Predictive Health ──
  health_model:
    enabled: true
    forecast_horizons: [5, 15, 30]   # minutes
    intervention_threshold: 0.3
    lstm_hidden_size: 32
    model_update_interval_seconds: 300
```

---

## 9. File Structure

```
Backend/Core/MainCore/MonitoringCore/
├── __init__.py
├── MonitoringCore.py              ← Existing: passive telemetry sink
│
├── anomaly/
│   ├── __init__.py
│   ├── AnomalyDetector.py         ← ML-based anomaly detection engine
│   ├── metrics_buffer.py          ← Rolling window MetricWindow class
│   ├── statistical.py             ← Z-Score, IQR, EWMA implementations
│   ├── isolation_forest.py        ← IsolationForest wrapper
│   └── lstm_autoencoder.py        ← Temporal sequence anomaly model
│
├── proactive/
│   ├── __init__.py
│   ├── ProactiveActor.py          ← Action execution engine
│   ├── action_registry.py         ← Maps anomaly types → corrective actions
│   ├── cooldown.py                ← Rate limiting and cooldown logic
│   └── actions/
│       ├── route_cpu_fallback.py
│       ├── offload_weights.py
│       ├── throttle_batch.py
│       ├── prewarm_cache.py
│       ├── flush_caches.py
│       └── signal_scale.py
│
├── evolution/
│   ├── __init__.py
│   ├── EvolutionTrigger.py        ← Training need signal generator
│   └── signal_formatter.py        ← Formats EvolutionSignal for EventBus
│
├── scaling/
│   ├── __init__.py
│   ├── BackupScaleSignal.py       ← Pool scaling request generator
│   └── scale_evaluator.py         ← Utilization-based scaling logic
│
├── predictive/
│   ├── __init__.py
│   ├── SystemHealthModel.py       ← LSTM-based predictive health model
│   ├── model_trainer.py           ← Online learning / model updates
│   └── forecast.py                ← HealthForecast dataclass + formatting
│
├── telemetry/
│   ├── __init__.py
│   ├── telemetry_writer.py        ← SQLite telemetry persistence
│   ├── anomaly_history.py         ← Anomaly event history table
│   ├── action_log.py              ← Proactive action audit log
│   └── report_generator.py        ← generate_report() from existing code
│
└── config/
    └── monitoring_defaults.py     ← Default configuration constants
```

---

## 10. Integration Points

### EventBus Topics Subscribed

| Topic | Handler | Purpose |
|---|---|---|
| `system.health` | `AnomalyDetector.ingest()` | Feed metrics into detector |
| `system.alert` | `ProactiveActor.on_alert()` | React to existing alerts |
| `task.created` | `telemetry_writer.log_task()` | Log task lifecycle |
| `task.completed` | `AnomalyDetector.ingest_inference()` | Feed inference metrics |
| `task.failed` | `ProactiveActor.on_task_failure()` | Detect error rate spikes |
| `monitoring.log` | `telemetry_writer.log_event()` | General telemetry logging |
| `evolution.done` | `EvolutionTrigger.on_training_complete()` | Reset recurrence counters |
| `backup.scale_response` | `BackupScaleSignal.on_response()` | Confirm scale operations |

### EventBus Topics Published

| Topic | Source | Payload |
|---|---|---|
| `monitoring.anomaly_detected` | AnomalyDetector | AnomalySignal |
| `monitoring.action_executed` | ProactiveActor | ActionEvent |
| `monitoring.evolution_signal` | EvolutionTrigger | EvolutionSignal |
| `monitoring.backup_scale_request` | BackupScaleSignal | ScaleSignal |
| `monitoring.health_forecast` | SystemHealthModel | HealthForecast |
| `system.alert` | ProactiveActor | AlertEvent (reuses existing) |

### Core Integration Map

| Core | Direction | Integration |
|---|---|---|
| **EventBus** | Subscribe + Publish | All metric ingestion and action dispatch |
| **OrchestratorCore** | Inbound | `route_to_cpu_fallback`, `isolate_core` |
| **CognitionCore** | Inbound | `throttle_batch`, `offload_weights` |
| **OptimizationCore** | Inbound | `prewarm_cache`, `flush_caches`, `compress_context` |
| **BackupCore** | Outbound | `BACKUP_SCALE` signal for pool adjustment |
| **EvolutionCore** | Outbound | `EVOLUTION_SIGNAL` for training triggers |
| **AutomationCore** | Outbound | System metrics source (`get_system_info`) |
| **DatabaseConnector** | Outbound | Telemetry persistence (SQLite) |

---

## 11. Events Reference

### AnomalySignal Event

```json
{
  "event_id": "uuid4",
  "topic": "monitoring.anomaly_detected",
  "source": "monitoring.anomaly_detector",
  "payload": {
    "metric_name": "gpu_vram_used_gb",
    "anomaly_type": "z_score",
    "severity": 0.87,
    "current_value": 7.2,
    "expected_range": [3.0, 5.5],
    "context": {
      "model_loaded": "qwen2.5-coder-3b",
      "active_sessions": 3
    }
  },
  "timestamp": 1694000000.0
}
```

### ActionEvent

```json
{
  "event_id": "uuid4",
  "topic": "monitoring.action_executed",
  "source": "monitoring.proactive_actor",
  "payload": {
    "action": "offload_inactive_weights",
    "trigger_metric": "gpu_vram_used_gb",
    "trigger_severity": 0.87,
    "result": "success",
    "details": "Offloaded 2.1GB to disk, VRAM now at 5.1GB",
    "duration_ms": 340
  },
  "timestamp": 1694000000.5
}
```

### EvolutionSignal Event

```json
{
  "event_id": "uuid4",
  "topic": "monitoring.evolution_signal",
  "source": "monitoring.evolution_trigger",
  "payload": {
    "signal_type": "ROUTER_RETRAIN_NEEDED",
    "target_model": "vibhu-router-150m",
    "reason": "Cache hit rate sustained below 0.3 for 35 minutes",
    "evidence": [
      {"metric": "cache_hit_rate", "avg_30min": 0.24, "baseline": 0.65}
    ],
    "priority": "high",
    "suggested_action": "retrain"
  },
  "timestamp": 1694000000.0
}
```

---

## 12. Metrics Tracked

| Metric | Type | Description |
|---|---|---|
| `anomalies_detected_total` | counter | Total anomalies detected since startup |
| `anomalies_by_type` | gauge (per type) | Count by detection method |
| `actions_executed_total` | counter | Total proactive actions taken |
| `actions_by_type` | gauge (per action) | Count by action type |
| `action_cooldown_rejects` | counter | Actions skipped due to cooldown |
| `action_success_rate` | gauge | % of actions that succeeded |
| `evolution_signals_sent` | counter | Total training signals sent |
| `backup_scale_requests` | counter | Total scale up/down requests |
| `health_forecast_accuracy` | gauge | MAE of predicted vs actual values |
| `baseline_model_trained` | gauge | Boolean: whether baseline is trained |
| `telemetry_records_written` | counter | Total telemetry rows inserted |
| `mean_time_to_act_ms` | gauge | Avg time from anomaly detection to action execution |
| `false_positive_rate` | gauge | Anomalies that resulted in no corrective action |

---

## 13. Module Boundary Rules

- **No inference** — MonitoringCore never calls CognitionCore or touches model weights directly
- **No business logic modification** — Does not alter task flow, only reacts to metrics
- **Read-only on other cores' state** — Observes via EventBus, never queries other cores' internals
- **Write-only to own telemetry tables** — All persistence through DatabaseConnector plugin
- **Cooldown-enforced** — Cannot fire the same action more than configured rate
- **Severity-gated** — Actions only trigger above configured severity thresholds
- **Predictive model stays lightweight** — LSTM autoencoder < 100KB, no GPU required for inference
