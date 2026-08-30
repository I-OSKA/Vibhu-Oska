# FastResponderCore — Lightweight Handler

## 1. Overview

FastResponderCore is a ~5M parameter lightweight model optimized for handling
simple, high-frequency queries that don't require deep reasoning. It acts as
the first line of defense in the Vibhu-Oska inference pipeline, intercepting
trivial requests before they reach the heavier specialist models.

**Purpose:** Eliminate unnecessary VRAM churn by resolving ~40-60% of daily
query volume locally without invoking the SARA or specialist pool.

| Property          | Value                          |
|-------------------|--------------------------------|
| Parameters        | ~5M                            |
| VRAM footprint    | ~0.4 GB (always hot)           |
| Latency (avg)     | < 50ms                        |
| Quantization      | FP16 (always loaded)           |
| Inference backend | ONNX Runtime / TensorRT       |
| Max context       | 512 tokens                     |

## 2. VRAM Allocation

FastResponderCore is classified as **always-hot** — its weights remain loaded
in VRAM for the entire system lifetime. This guarantees sub-50ms response
times for trivial queries.

```
VRAM Map (always-hot region):
┌─────────────────────────────────────────────────────┐
│  SARA   │  Router  │  FastResponder       │
│     4.2 GB       │  0.2 GB  │  0.4 GB              │
│  [0x00000000]    │ [0x4400] │  [0x4600]            │
└─────────────────────────────────────────────────────┘
  Total always-hot: 4.8 GB of 8 GB RTX 4060
```

## 3. Pattern Matching & Quick Routing

FastResponderCore uses a two-stage approach:

### Stage 1: Regex / Rule-Based Filter

Before any neural inference, a rule engine scans the input for known patterns:

```python
PATTERNS = {
    "math":      r"[\d+\-*/^%().]+\s*=\s*\?|what is \d+[\+\-\*\/]\d+",
    "time":      r"(what time|current time|clock|date today|what day)",
    "greeting":  r"^(hi|hello|hey|good morning|good night|howdy|sup)\b",
    "fact":      r"(who is|what is|when was|where is|how many|how old)",
    "status":    r"(system status|how are you|uptime|memory|cpu|gpu|disk)",
}
```

If a regex matches, the query is routed to the appropriate handler immediately
without neural inference.

### Stage 2: Neural Classification (Fallback)

For ambiguous inputs, a tiny classifier (~1M params) scores the input against
supported query types. If confidence > 0.85, it routes directly. Otherwise,
it falls through to the specialist pipeline.

```python
def classify_query(text: str) -> tuple[str, float]:
    """Returns (category, confidence)."""
    embeddings = fast_responder.encode(text)
    logits = classifier_head(embeddings)
    probs = softmax(logits)
    category = CATEGORIES[probs.argmax()]
    confidence = probs.max().item()
    return category, confidence
```

## 4. Supported Query Types

### Math

- Arithmetic: `2 + 2`, `15 * 7`, `100 / 3`
- Expression evaluation: `(3 + 5) * 2 - 10`
- Unit conversion: `100 fahrenheit to celsius`
- Percentage: `what is 15% of 230`

```python
# math_handler.py
def handle_math(query: str) -> str:
    expr = extract_expression(query)
    try:
        result = safe_eval(expr)  # restricted eval, no imports
        return f"The answer is {result}."
    except Exception:
        return "I couldn't parse that math expression."
```

### Time & Date

- Current time: `What time is it?`
- Current date: `What's today's date?`
- Timezone conversion: `What time in Tokyo?`
- Date math: `How many days until Christmas?`

```python
# time_handler.py
from datetime import datetime, timezone

def handle_time(query: str) -> str:
    tz = extract_timezone(query) or "UTC"
    now = datetime.now(timezone.utc)
    local = now.astimezone(ZoneInfo(tz))
    return f"Current time in {tz}: {local.strftime('%H:%M:%S, %B %d, %Y')}"
```

### Facts (Hardcoded Knowledge Base)

- Country capitals, population facts
- Historical dates (major events)
- Scientific constants
- Unit definitions

```python
# facts_db.py — compact key-value store (~50MB on disk, loaded to RAM)
FACTS = {
    "capital of france": "Paris",
    "speed of light": "299,792,458 m/s",
    "water boiling point": "100°C at sea level",
    "earth population": "~8 billion (2024)",
    # ... ~50K entries
}
```

### Greetings

- Hello, hi, hey, good morning/afternoon/evening
- How are you, what's up
- Thank you, goodbye

```python
# greeting_handler.py
GREETING_RESPONSES = {
    "hello":    "Hello! How can I help you today?",
    "hey":      "Hey there! What's on your mind?",
    "goodbye":  "Goodbye! Have a great day.",
    "thanks":   "You're welcome!",
}

def handle_greeting(query: str) -> str:
    intent = classify_greeting(query)
    return GREETING_RESPONSES.get(intent, "Hi there!")
```

### System Status

- GPU temperature, VRAM usage
- CPU load, disk usage
- Active specialist models
- System uptime

```python
# status_handler.py
import psutil, torch

def handle_status(query: str) -> str:
    gpu_mem = torch.cuda.memory_allocated() / 1e9
    gpu_total = torch.cuda.get_device_properties(0).total_mem / 1e9
    cpu = psutil.cpu_percent(interval=0.1)
    disk = psutil.disk_usage('/').percent
    return (
        f"GPU: {gpu_mem:.1f}/{gpu_total:.1f} GB VRAM\n"
        f"CPU: {cpu}% used\n"
        f"Disk: {disk}% used"
    )
```

## 5. Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                      User Query                          │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Input Preproc   │  (tokenize, lowercase, normalize)
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Regex Filter    │  ← Stage 1: pattern match
              └───┬─────────┬───┘
                  │         │
            match │         │ no match
                  ▼         ▼
         ┌──────────┐  ┌─────────────────┐
         │ Handler   │  │ Neural Classifier│  ← Stage 2: ~1M params
         │ Dispatch  │  │ (confidence > 0.85?)
         └────┬─────┘  └──┬──────────┬───┘
              │            │          │
              │       yes  │          │ no
              │            ▼          ▼
              │   ┌──────────┐  ┌────────────────┐
              │   │ Handler   │  │ Forward to      │
              │   │ Execute   │  │ Specialist      │
              │   └────┬─────┘  │ Pipeline        │
              │        │        │ (Router → GPT)  │
              ▼        ▼        └────────────────┘
         ┌──────────────────┐
         │  Response Synth   │  (format output, add context)
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │   Return to User  │
         └──────────────────┘
```

## 6. Configuration

### `fast_responder.yaml`

```yaml
fast_responder:
  enabled: true
  model_path: "./models/fast_responder_5m.onnx"
  classifier_path: "./models/query_classifier_1m.onnx"
  max_context_length: 512
  confidence_threshold: 0.85
  vram_budget_mb: 400

  handlers:
    math:
      enabled: true
      safe_eval_max_depth: 10
    time:
      enabled: true
      default_timezone: "UTC"
    facts:
      enabled: true
      db_path: "./data/facts_db.json"
      max_entries: 100000
    greeting:
      enabled: true
    status:
      enabled: true

  fallback:
    enabled: true
    target: "specialist_pipeline"
    log_unhandled: true
```

## 7. File Structure

```
fast_responder/
├── __init__.py
├── core.py                  # FastResponderCore main class
├── classifier.py            # Neural query classifier
├── pattern_engine.py        # Regex pattern matcher
├── handlers/
│   ├── __init__.py
│   ├── math_handler.py
│   ├── time_handler.py
│   ├── facts_handler.py
│   ├── greeting_handler.py
│   └── status_handler.py
├── models/
│   ├── fast_responder_5m.onnx
│   └── query_classifier_1m.onnx
├── data/
│   └── facts_db.json
├── tests/
│   ├── test_math.py
│   ├── test_time.py
│   ├── test_fallback.py
│   └── test_latency.py
└── config/
    └── fast_responder.yaml
```

## 8. Integration Points

```
                    ┌─────────────────┐
                    │   VRAM Manager   │
                    │  (monitors 0.4G)│
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────────┐   ┌──────────────┐
│   Router    │───▶│ FastResponder   │──▶│  Specialist   │
│  (dispatch) │    │    (0.4 GB)     │   │  Pipeline     │
└─────────────┘    └─────────────────┘   └──────────────┘
         │                   │
         │                   ▼
         │          ┌─────────────────┐
         │          │ SARA   │  (if fallback needed)
         │          │   (4.2 GB)      │
         │          └─────────────────┘
         │
         ▼
┌─────────────────┐
│   Event Bus     │  (logs query, latency, outcome)
└─────────────────┘
```

**Key Integrations:**

| Component          | Interface              | Direction       |
|--------------------|------------------------|-----------------|
| Router             | `route_query()`        | Inbound         |
| SARA      | `forward_to_gpt()`     | Outbound        |
| VRAM Manager       | `get_vram_usage()`     | Bidirectional   |
| Event Bus          | `emit("query.*")`      | Outbound        |
| Telemetry          | `record_latency()`     | Outbound        |
| Hot-Swap Controller| `is_resident()`        | Bidirectional   |

## 9. Events

```python
# Events emitted by FastResponderCore
events = {
    "fast.query.received":       # New query arrived
    "fast.query.classified":     # Classification complete
    "fast.query.routed.math":    # Routed to math handler
    "fast.query.routed.time":    # Routed to time handler
    "fast.query.routed.facts":   # Routed to facts handler
    "fast.query.routed.greeting":# Routed to greeting handler
    "fast.query.routed.status":  # Routed to status handler
    "fast.query.fallback":       # Fell through to specialist
    "fast.query.resolved":       # Successfully answered
    "fast.query.failed":         # Handler error
    "fast.latency.warning":      # Latency > 100ms threshold
    "fast.vram_pressure":        # VRAM pressure detected
}

# Example event payload
{
    "event": "fast.query.resolved",
    "timestamp": "2026-08-10T14:32:01Z",
    "query_hash": "a3f2c1...",
    "category": "math",
    "method": "regex_match",
    "latency_ms": 12,
    "confidence": 1.0,
    "vram_used_mb": 387,
}
```

## 10. Metrics

| Metric                     | Type    | Description                              |
|----------------------------|---------|------------------------------------------|
| `fast_queries_total`       | Counter | Total queries processed                  |
| `fast_queries_resolved`    | Counter | Queries resolved without fallback        |
| `fast_queries_fallback`    | Counter | Queries forwarded to specialist pipeline |
| `fast_latency_ms`          | Gauge   | Current response latency                 |
| `fast_latency_p50`         | Gauge   | 50th percentile latency                  |
| `fast_latency_p99`         | Gauge   | 99th percentile latency                  |
| `fast_vram_usage_mb`       | Gauge   | Current VRAM consumption                 |
| `fast_classifier_confidence` | Histogram | Distribution of classification scores |
| `fast_handler_accuracy`    | Gauge   | Correct / total resolved                 |
| `fast_uptime_seconds`      | Gauge   | Seconds since last restart               |

```python
# Prometheus-style export
from prometheus_client import Counter, Gauge, Histogram

QUERIES_TOTAL = Counter("fast_queries_total", "Total queries")
QUERIES_RESOLVED = Counter("fast_queries_resolved", "Resolved locally")
QUERIES_FALLBACK = Counter("fast_queries_fallback", "Sent to specialist")
LATENCY = Histogram("fast_latency_ms", "Response latency", buckets=[5,10,25,50,100,200])
VRAM_USAGE = Gauge("fast_vram_usage_mb", "VRAM usage in MB")
```

## 11. Bypassing the Specialist Pipeline

The core value proposition: **FastResponderCore intercepts and resolves queries
before they ever reach the SARA or specialist pool.**

```
WITHOUT FastResponder (old path):
  User → Router → SARA (4.2GB) → Specialist (1.2GB) → Response
  Cost: ~200ms latency, ~0.05 VRAM churn

WITH FastResponder (new path):
  User → Router → FastResponder (0.4GB) → Response
  Cost: ~20ms latency, 0 VRAM churn
```

**Bypass mechanism:**

1. Router checks `fast_responder.is_resident()` — always True (0.4GB always hot)
2. Router calls `fast_responder.handle(query)` with 50ms timeout
3. If FastResponder returns a result with confidence > 0.85, it's returned directly
4. If timeout or low confidence, the query falls through to the specialist pipeline
5. Specialist pipeline results are cached for similar future queries

```python
# In router.py
async def route_query(query: str) -> Response:
    # Fast path — always attempted first
    if self.fast_responder.is_resident():
        try:
            result = await asyncio.wait_for(
                self.fast_responder.handle(query),
                timeout=0.050  # 50ms budget
            )
            if result.confidence >= 0.85:
                self.metrics.record("fast_resolved")
                return result
        except asyncio.TimeoutError:
            self.metrics.record("fast_timeout")

    # Slow path — specialist pipeline
    specialist = self.specialist_pool.select(query)
    result = await specialist.infer(query)
    self.metrics.record("specialist_resolved")
    return result
```

**Performance Impact:**

| Metric              | Before FastResponder | After FastResponder |
|---------------------|----------------------|---------------------|
| Avg latency         | 180ms                | 45ms                |
| VRAM churn/hour     | ~2.1 GB              | ~0.6 GB             |
| GPU utilization     | 92%                  | 68%                 |
| Specialist invocations/hr | 1200            | 480                 |
| Query throughput    | 80 qps               | 180 qps             |
