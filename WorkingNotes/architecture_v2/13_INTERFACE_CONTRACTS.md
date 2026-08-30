# Interface Contracts — Vibhu-Oska AI-OS

> **Purpose**: Canonical reference for every inter-core communication boundary in the Vibhu-Oska system. All cores, wrappers, and agents MUST conform to these schemas. Any deviation requires a versioned contract update.

---

## Table of Contents

1. [EventBus Topics](#1-eventbus-topics)
2. [EventBus Payload Schemas](#2-eventbus-payload-schemas)
3. [RPC Schemas](#3-rpc-schemas)
4. [Config Schemas](#4-config-schemas)
5. [Checkpoint Formats](#5-checkpoint-formats)
6. [Versioning & Migration](#6-versioning--migration)

---

## 1. EventBus Topics

All topics are string constants. Cores subscribe/publish via `event_bus.py`.

### 1.1 Core Lifecycle

| Topic | Direction | Publisher | Subscriber(s) | Description |
|---|---|---|---|---|
| `CORE_STARTED` | Outbound | Any Core wrapper | Orchestrator, Logger | Fired once after `core.start()` succeeds |
| `CORE_HEARTBEAT` | Periodic | Any Core wrapper | Orchestrator, Health Monitor | Emitted every `heartbeat_interval_sec` (default 5.0) |
| `CORE_SHUTDOWN` | Outbound | Any Core wrapper | Orchestrator, Logger, Backup Manager | Fired during graceful teardown |

### 1.2 Request Flow

| Topic | Direction | Publisher | Subscriber(s) | Description |
|---|---|---|---|---|
| `USER_INPUT` | Inbound | Frontend / CLI adapter | Orchestrator | Raw user message entering the system |
| `SPECIALIST_REQUEST` | Internal | Orchestrator → Core | Target Core wrapper | Task dispatched to a specific core |
| `SPECIALIST_RESPONSE` | Internal | Core wrapper → Orchestrator | Orchestrator | Core result returned |
| `ORCHESTRATOR_SUMMATION` | Outbound | Orchestrator | Frontend / CLI adapter | Final combined response sent to user |

### 1.3 Evolution Loop

| Topic | Direction | Publisher | Subscriber(s) | Description |
|---|---|---|---|---|
| `EVOLUTION_TASK_GENERATED` | Internal | Meta-Evolution Core | Evolution Scheduler | New training/evaluation task created |
| `EVOLUTION_REWARD` | Internal | Evaluator Core | Meta-Evolution Core | Scalar reward signal for policy update |
| `EVOLUTION_CHECKPOINT` | Internal | Meta-Evolution Core | Backup Manager, Checkpoint Store | Model snapshot saved to disk |

### 1.4 ParaCore

| Topic | Direction | Publisher | Subscriber(s) | Description |
|---|---|---|---|---|
| `PARACORE_OVERRIDE` | Internal | ParaCore | Any Core wrapper | Emergency override signal (kill/pause/reroute) |
| `PARACORE_OBSERVATION` | Internal | Any Core wrapper | ParaCore | Telemetry/observation for anomaly detection |

### 1.5 Backup Scaling

| Topic | Direction | Publisher | Subscriber(s) | Description |
|---|---|---|---|---|
| `BACKUP_SCALE_REQUEST` | Internal | Orchestrator | Backup Manager | Request to spawn a backup core instance |
| `BACKUP_SPAWNED` | Internal | Backup Manager | Orchestrator, Logger | Backup core instance is live |
| `BACKUP_RETIRED` | Internal | Backup Manager | Orchestrator, Logger | Backup core instance decommissioned |

---

## 2. EventBus Payload Schemas

Every EventBus message is a Python `TypedDict` (or equivalent `dataclass`). All payloads carry a universal envelope.

### 2.1 Universal Envelope

```python
from __future__ import annotations
from typing import Any, TypedDict
from datetime import datetime
from uuid import UUID

class EventEnvelope(TypedDict):
    """Wraps every EventBus message."""
    event_id: UUID                    # Unique ID for idempotency
    topic: str                        # Topic constant (e.g. "SPECIALIST_REQUEST")
    timestamp: datetime               # UTC emission time
    source_core: str                  # Name of publishing core (e.g. "orchestrator")
    payload: dict[str, Any]           # Topic-specific payload (see below)
    correlation_id: UUID | None       # Traces a single user request across cores
    metadata: dict[str, Any]          # Arbitrary key-value pairs (version, flags, etc.)
```

### 2.2 Core Lifecycle Payloads

```python
class CoreStartedPayload(TypedDict):
    core_name: str                    # e.g. "orchestrator", "paracore"
    core_version: str                 # SemVer string "1.2.3"
    capabilities: list[str]           # What this core can do
    started_at: datetime

class CoreHeartbeatPayload(TypedDict):
    core_name: str
    uptime_sec: float                 # Seconds since CORE_STARTED
    cpu_percent: float                # 0.0–100.0
    memory_mb: float                  # Resident memory in MB
    active_tasks: int                 # Number of in-flight requests
    queue_depth: int                  # Pending requests in internal queue

class CoreShutdownPayload(TypedDict):
    core_name: str
    reason: str                       # "graceful" | "error" | "override" | "heartbeat_timeout"
    final_state: dict[str, Any]       # Serializable snapshot of core internals
    shutdown_at: datetime
```

### 2.3 Request Flow Payloads

```python
class UserInputPayload(TypedDict):
    user_id: str
    session_id: str
    message: str                      # Raw text from user
    input_type: str                   # "text" | "voice" | "image" | "file"
    timestamp: datetime
    context: dict[str, Any]           # Prior conversation turns, preferences, etc.

class SpecialistRequestPayload(TypedDict):
    request_id: UUID                  # Unique ID for this task
    target_core: str                  # Which core to invoke (e.g. "nlp", "vision")
    method: str                       # RPC method name (e.g. "analyze_sentiment")
    args: list[Any]                   # Positional arguments
    kwargs: dict[str, Any]            # Keyword arguments
    priority: int                     # 0 (lowest) – 10 (highest, real-time)
    timeout_sec: float                # Max wait before timeout
    sender_core: str                  # Who sent this request

class SpecialistResponsePayload(TypedDict):
    request_id: UUID                  # Matches the SpecialistRequest
    source_core: str                  # Which core produced this result
    success: bool
    result: Any                       # Return value (must be serializable)
    error: str | None                 # Error message if success=False
    execution_time_ms: float          # Wall-clock time
    cache_hit: bool                   # Whether result came from cache

class OrchestratorSummationPayload(TypedDict):
    user_id: str
    session_id: str
    original_request_id: UUID         # Links back to USER_INPUT
    response_text: str                # Final natural-language answer
    confidence: float                 # 0.0–1.0
    sources: list[str]                # Which cores contributed
    metadata: dict[str, Any]          # Timing, token counts, etc.
```

### 2.4 Evolution Loop Payloads

```python
class EvolutionTaskGeneratedPayload(TypedDict):
    task_id: UUID
    task_type: str                    # "train" | "evaluate" | "ablation" | "data_augment"
    target_model: str                 # Model identifier (e.g. "nlp_transformer_v3")
    objective: str                    # What to optimize (e.g. "accuracy", "latency")
    dataset_ref: str                  # Path or URI to training data
    hyperparams: dict[str, Any]       # Learning rate, epochs, batch size, etc.
    created_at: datetime

class EvolutionRewardPayload(TypedDict):
    task_id: UUID
    reward: float                     # Scalar reward (higher = better)
    metrics: dict[str, float]         # Detailed metric breakdown
    eval_dataset: str                 # Which dataset was used for evaluation
    evaluated_at: datetime
    evaluator_core: str               # Which core performed evaluation

class EvolutionCheckpointPayload(TypedDict):
    checkpoint_id: UUID
    model_name: str                   # e.g. "nlp_transformer_v3"
    version: str                      # SemVer or commit hash
    path: str                         # Filesystem path to checkpoint file
    size_bytes: int
    sha256: str                       # Integrity hash
    created_at: datetime
    metadata: dict[str, Any]          # Training loss, epoch, step, etc.
```

### 2.5 ParaCore Payloads

```python
class ParaCoreOverridePayload(TypedDict):
    override_id: UUID
    target_core: str                  # Which core to affect
    action: str                       # "pause" | "resume" | "kill" | "reroute" | "throttle"
    reason: str                       # Human-readable justification
    parameters: dict[str, Any]        # Action-specific params (e.g. throttle_rate)
    issued_by: str                    # "paracore" or human operator
    issued_at: datetime

class ParaCoreObservationPayload(TypedDict):
    source_core: str
    observation_type: str             # "latency_spike" | "error_burst" | "resource_leak" | "anomaly"
    severity: int                     # 1 (low) – 5 (critical)
    metrics: dict[str, float]         # Relevant measurements
    observed_at: datetime
    raw_data: dict[str, Any]          # Optional additional context
```

### 2.6 Backup Scaling Payloads

```python
class BackupScaleRequestPayload(TypedDict):
    request_id: UUID
    target_core: str                  # Which core needs a backup
    reason: str                       # "load" | "fault_tolerance" | "maintenance"
    replicas: int                     # How many backup instances to spawn
    resource_profile: str             # "minimal" | "standard" | "performance"
    requested_at: datetime

class BackupSpawnedPayload(TypedDict):
    backup_id: UUID
    primary_core: str
    backup_core: str                  # Name of the new backup instance
    endpoint: str                     # RPC endpoint for the backup
    spawned_at: datetime

class BackupRetiredPayload(TypedDict):
    backup_id: UUID
    backup_core: str
    reason: str                       # "load_reduced" | "fault_healed" | "manual"
    retired_at: datetime
    final_state: dict[str, Any]       # Snapshot before teardown
```

---

## 3. RPC Schemas

Direct core-to-core calls bypass the EventBus for low-latency communication. All RPC calls use `asyncio` streams with msgpack serialization.

### 3.1 RPC Envelope

```python
from __future__ import annotations
from typing import Any, TypedDict
from uuid import UUID

class RPCRequest(TypedDict):
    request_id: UUID
    method: str                       # e.g. "nlp.analyze", "vision.detect"
    args: list[Any]
    kwargs: dict[str, Any]
    caller: str                       # Calling core name
    timeout_ms: int                   # Timeout in milliseconds
    priority: int                     # 0–10

class RPCResponse(TypedDict):
    request_id: UUID                  # Matches request
    success: bool
    result: Any
    error: str | None
    error_code: str | None            # Machine-readable error code
    execution_time_ms: float
```

### 3.2 Core-Specific RPC Methods

#### NLP Core

```python
class NLPAnalyzeRequest(TypedDict):
    text: str
    tasks: list[str]                  # ["sentiment", "entities", "intent", "summary"]

class NLPAnalyzeResponse(TypedDict):
    sentiment: dict[str, float] | None      # {"positive": 0.8, "negative": 0.1, "neutral": 0.1}
    entities: list[dict[str, Any]] | None   # [{"text": "...", "type": "PERSON", "start": 0, "end": 4}]
    intent: str | None                      # e.g. "question", "command", "statement"
    summary: str | None
    language: str                           # ISO 639-1 code
    token_count: int

class NLPGenerateRequest(TypedDict):
    prompt: str
    max_tokens: int
    temperature: float                      # 0.0–2.0
    top_p: float                            # Nucleus sampling threshold
    stop_sequences: list[str]
    system_prompt: str | None

class NLPGenerateResponse(TypedDict):
    text: str
    tokens_used: int
    finish_reason: str                      # "stop" | "length" | "error"
    logprobs: list[float] | None
```

#### Vision Core

```python
class VisionDetectRequest(TypedDict):
    image_ref: str                          # File path or URI
    classes: list[str] | None               # Filter to specific classes, None = all
    confidence_threshold: float             # 0.0–1.0

class VisionDetectResponse(TypedDict):
    detections: list[dict[str, Any]]
    # Each detection: {"class": str, "confidence": float, "bbox": [x, y, w, h]}
    image_size: tuple[int, int]             # (width, height)
    inference_time_ms: float

class VisionDescribeRequest(TypedDict):
    image_ref: str
    style: str                              # "concise" | "detailed" | "technical"
    max_length: int                         # Max words in description

class VisionDescribeResponse(TypedDict):
    description: str
    objects_detected: list[str]
    scene: str                              # e.g. "indoor", "outdoor", "abstract"
```

#### Orchestrator Core

```python
class OrchestratorRouteRequest(TypedDict):
    user_input: str
    user_id: str
    session_id: str
    context: dict[str, Any]
    available_cores: list[str]

class OrchestratorRouteResponse(TypedDict):
    selected_cores: list[str]               # Ordered list of cores to invoke
    parallel_groups: list[list[str]]        # Cores that can run simultaneously
    strategy: str                           # "sequential" | "parallel" | "fan_out"
    estimated_time_ms: float
```

#### Meta-Evolution Core

```python
class MetaEvolutionPlanRequest(TypedDict):
    objective: str
    current_models: dict[str, str]          # model_name -> version
    constraints: dict[str, Any]             # compute_budget, time_budget, etc.
    historical_performance: dict[str, float]

class MetaEvolutionPlanResponse(TypedDict):
    plan_id: UUID
    steps: list[dict[str, Any]]             # Ordered list of evolution actions
    estimated_improvement: float            # Expected objective improvement
    estimated_cost: float                   # Compute cost estimate
```

#### ParaCore

```python
class ParaCoreMonitorRequest(TypedDict):
    cores: list[str]                        # Which cores to monitor
    metrics: list[str]                      # ["latency", "error_rate", "throughput"]
    window_sec: int                         # Observation window

class ParaCoreMonitorResponse(TypedDict):
    observations: dict[str, dict[str, float]]  # core_name -> metric -> value
    anomalies: list[dict[str, Any]]             # Detected anomalies
    recommendations: list[str]                  # Suggested actions

class ParaCoreOverrideRequest(TypedDict):
    target_core: str
    action: str                             # "pause" | "resume" | "kill" | "reroute"
    parameters: dict[str, Any]
    reason: str

class ParaCoreOverrideResponse(TypedDict):
    success: bool
    previous_state: str
    new_state: str
    message: str
```

---

## 4. Config Schemas

Each core has a YAML configuration file. All configs share a common base.

### 4.1 Base Config (shared by all cores)

```yaml
# Base config schema — every core must include these fields
core:
  name: string              # Unique core identifier (e.g. "nlp", "vision")
  version: string           # SemVer "1.2.3"
  type: string              # "worker" | "orchestrator" | "monitor" | "evolution"
  enabled: boolean          # Whether this core is active
  
  logging:
    level: string           # "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL"
    file: string | null     # Log file path, null = stdout only
    max_size_mb: integer    # Max log file size before rotation
    backup_count: integer   # Number of rotated log files to keep

  heartbeat:
    enabled: boolean
    interval_sec: float     # Default 5.0
    timeout_sec: float      # Missed heartbeats before considered dead

  resources:
    cpu_limit: float        # Fraction of CPU cores (e.g. 0.5 = half a core)
    memory_limit_mb: integer
    gpu_device: string | null  # e.g. "cuda:0" or null for CPU-only

  rpc:
    enabled: boolean
    host: string            # e.g. "127.0.0.1"
    port: integer           # e.g. 50051
    max_concurrent: integer # Max concurrent RPC connections
    timeout_ms: integer     # Default RPC timeout

  event_bus:
    enabled: boolean
    topics_subscribe: list[string]   # Topics this core listens to
    topics_publish: list[string]     # Topics this core emits to
    buffer_size: integer             # Inbound event buffer size
```

### 4.2 NLP Core Config

```yaml
core:
  name: "nlp"
  version: "1.0.0"
  type: "worker"
  enabled: true

  # ... base fields ...

  nlp:
    model:
      name: string              # e.g. "gpt-4-turbo" or local model path
      backend: string           # "openai" | "anthropic" | "local" | "vllm"
      api_key_env: string       # Environment variable name for API key
      max_context_tokens: integer

    generation:
      default_max_tokens: integer   # Default 2048
      default_temperature: float    # Default 0.7
      default_top_p: float          # Default 0.9
      stop_sequences: list[string]

    pipeline:
      sentiment: boolean
      entity_extraction: boolean
      intent_classification: boolean
      summarization: boolean
      translation: boolean
      supported_languages: list[string]  # ISO 639-1 codes

    cache:
      enabled: boolean
      backend: string            # "redis" | "local" | "none"
      ttl_sec: integer           # Cache entry lifetime
      max_entries: integer
```

### 4.3 Vision Core Config

```yaml
core:
  name: "vision"
  version: "1.0.0"
  type: "worker"
  enabled: true

  # ... base fields ...

  vision:
    model:
      detection: string          # e.g. "yolov8x.pt" or "faster-rcnn"
      description: string        # e.g. "blip2-opt-2.7b"
      backend: string            # "torch" | "onnx" | "tensorrt"
      device: string             # "cuda:0" | "cpu"

    detection:
      default_confidence: float  # 0.0–1.0, default 0.5
      nms_threshold: float       # Non-max suppression, default 0.4
      max_detections: integer    # Per image, default 100
      supported_classes: list[string] | null  # null = all COCO classes

    description:
      style: string              # "concise" | "detailed" | "technical"
      max_length: integer        # Max words
      language: string           # Output language

    input:
      max_image_size_mb: integer
      supported_formats: list[string]  # ["jpg", "png", "webp", "bmp"]
      resize_longest_edge: integer     # Resize if larger (px)
```

### 4.4 Orchestrator Core Config

```yaml
core:
  name: "orchestrator"
  version: "1.0.0"
  type: "orchestrator"
  enabled: true

  # ... base fields ...

  orchestrator:
    routing:
      strategy: string           # "round_robin" | "capability_match" | "ml_based"
      fallback_core: string      # Core to use if routing fails
      max_retries: integer       # Retry count on failure (default 2)

    parallel:
      enabled: boolean
      max_parallel_cores: integer  # Max cores invoked simultaneously (default 4)
      group_timeout_sec: float     # Timeout for a parallel group (default 30.0)

    summarization:
      enabled: boolean
      method: string             # "concatenate" | "llm_fusion" | "weighted"
      confidence_threshold: float  # Min confidence to include a core's result

    session:
      max_history: integer       # Max conversation turns to keep
      ttl_sec: integer           # Session expiry time
      persistence: string        # "redis" | "file" | "memory"
```

### 4.5 ParaCore Config

```yaml
core:
  name: "paracore"
  version: "1.0.0"
  type: "monitor"
  enabled: true

  # ... base fields ...

  paracore:
    monitoring:
      interval_sec: float        # How often to poll core metrics (default 1.0)
      window_sec: int            # Sliding window for anomaly detection (default 60)

    thresholds:
      latency_p99_ms: float      # Trigger if p99 exceeds this (default 5000)
      error_rate: float          # Trigger if error rate exceeds this (default 0.1)
      memory_usage: float        # Trigger if memory exceeds fraction (default 0.9)
      cpu_usage: float           # Trigger if CPU exceeds fraction (default 0.95)

    actions:
      on_anomaly: string         # "alert" | "throttle" | "restart" | "reroute"
      throttle_rate: float       # Fraction to throttle (0.0 = full stop, 0.5 = half)
      restart_cooldown_sec: int  # Min time between restarts (default 60)

    override:
      require_auth: boolean      # Require human auth for overrides (default true)
      log_all: boolean           # Log all override attempts (default true)
```

### 4.6 Meta-Evolution Core Config

```yaml
core:
  name: "meta_evolution"
  version: "1.0.0"
  type: "evolution"
  enabled: true

  # ... base fields ...

  evolution:
    models:
      - name: string             # e.g. "nlp_transformer_v3"
        type: string             # "nlp" | "vision" | "custom"
        checkpoint_dir: string   # Where to save/load checkpoints
        current_version: string

    training:
      backend: string            # "torch" | "jax" | "tensorflow"
      default_optimizer: string  # "adam" | "adamw" | "sgd"
      default_lr: float
      default_epochs: integer
      early_stopping_patience: integer

    evaluation:
      metrics: list[string]      # ["accuracy", "f1", "bleu", "rouge"]
      eval_split: float          # Fraction for eval (default 0.2)
      min_improvement: float     # Min reward improvement to keep a change

    checkpointing:
      format: string             # "torch" | "safetensors" | "onnx"
      max_checkpoints: integer   # Max saved checkpoints per model
      compression: string        # "none" | "gzip" | "lz4"
```

### 4.7 Backup Manager Config

```yaml
core:
  name: "backup_manager"
  version: "1.0.0"
  type: "worker"
  enabled: true

  # ... base fields ...

  backup:
    scaling:
      auto_scale: boolean
      min_replicas: integer      # Minimum backup instances (default 0)
      max_replicas: integer      # Maximum backup instances (default 3)
      scale_up_threshold: float  # CPU/load threshold to trigger scale-up (default 0.8)
      scale_down_threshold: float

    health_check:
      interval_sec: float
      timeout_sec: float
      failure_threshold: integer  # Consecutive failures before retirement

    storage:
      checkpoint_mirror: boolean  # Mirror checkpoints to backup storage
      state_sync: boolean         # Sync core state to backups
      sync_interval_sec: float
```

---

## 5. Checkpoint Formats

All checkpoints are saved via `torch.save()` (PyTorch) or equivalent serializers. Each model type has a specific dict structure.

### 5.1 Common Checkpoint Envelope

Every checkpoint file contains this top-level structure:

```python
from __future__ import annotations
from typing import Any, TypedDict
from datetime import datetime
from uuid import UUID

class CheckpointEnvelope(TypedDict):
    """Top-level structure for ALL checkpoint files."""
    format_version: str             # "1.0" — schema version
    model_name: str                 # e.g. "nlp_transformer_v3"
    model_type: str                 # "nlp" | "vision" | "meta_evolution" | "custom"
    version: str                    # SemVer or git commit hash
    created_at: datetime
    checkpoint_id: UUID
    metadata: dict[str, Any]        # Model-specific metadata (see below)
    state_dict: dict[str, Any]      # PyTorch state_dict (model weights)
    optimizer_state: dict[str, Any] | None  # Optimizer state_dict
    scheduler_state: dict[str, Any] | None  # LR scheduler state_dict
    training_state: TrainingState           # Current training progress
    config: dict[str, Any]          # Model configuration used during training

class TrainingState(TypedDict):
    epoch: int
    global_step: int
    total_steps: int
    best_metric: float              # Best metric value seen
    best_metric_name: str           # e.g. "accuracy" or "loss"
    patience_counter: int           # For early stopping
    rng_state: bytes                # Python random module state
    numpy_rng_state: bytes          # NumPy random state
    torch_rng_state: bytes          # PyTorch CUDA/CPU RNG state
```

### 5.2 NLP Core Checkpoint

```python
class NLPCheckpointMetadata(TypedDict):
    """Additional metadata for NLP model checkpoints."""
    vocab_size: int
    max_position_embeddings: int
    hidden_size: int
    num_layers: int
    num_heads: int
    tokenizer_name: str             # e.g. "gpt2", "cl100k_base"
    tokenizer_path: str | null      # Path to custom tokenizer file
    pad_token_id: int
    eos_token_id: int
    special_tokens: list[str]
    training_loss: float
    validation_loss: float | None
    perplexity: float | None
    tokens_trained: int             # Total tokens seen during training

# torch.save() structure for NLP:
# {
#     **CheckpointEnvelope,
#     "metadata": NLPCheckpointMetadata,
#     "tokenizer": dict[str, Any],  # Serialized tokenizer state
#     "embedding_table": torch.Tensor | None,  # If tied, null
# }
```

### 5.3 Vision Core Checkpoint

```python
class VisionCheckpointMetadata(TypedDict):
    """Additional metadata for Vision model checkpoints."""
    architecture: str               # e.g. "yolov8x", "blip2-opt-2.7b"
    num_classes: int | null         # null for description models
    class_names: list[str] | null
    input_size: tuple[int, int]     # (height, width)
    mean: list[float]               # Normalization mean
    std: list[float]                # Normalization std
    backbone: str                   # e.g. "resnet50", "vit_l_14"
    pretrained_on: str | null       # Dataset used for pretraining
    fine_tune_on: str | null        # Dataset used for fine-tuning
    map_score: float | null         # mAP for detection models
    bleu_score: float | null        # BLEU for captioning models

# torch.save() structure for Vision:
# {
#     **CheckpointEnvelope,
#     "metadata": VisionCheckpointMetadata,
#     "class_mapping": dict[int, str] | None,  # class_id -> class_name
#     "preprocessing_config": dict[str, Any],   # Resize, normalize params
# }
```

### 5.4 Meta-Evolution Core Checkpoint

```python
class MetaEvolutionCheckpointMetadata(TypedDict):
    """Additional metadata for Meta-Evolution model checkpoints."""
    policy_type: str                # "actor_critic" | " evolutionary" | "bayesian"
    action_space: list[str]         # What actions the policy can take
    state_dim: int                  # Dimensionality of observation space
    reward_history: list[float]     # Last N rewards
    improvement_rate: float         # Average improvement per step
    exploration_rate: float         # Current exploration rate (epsilon, temperature)
    total_episodes: int
    total_steps: int
    best_reward: float
    best_checkpoint_id: UUID | None

# torch.save() structure for Meta-Evolution:
# {
#     **CheckpointEnvelope,
#     "metadata": MetaEvolutionCheckpointMetadata,
#     "reward_buffer": list[dict[str, Any]],  # Buffered reward signals
#     "experience_buffer": dict[str, Any],    # Replay buffer metadata (not full buffer)
#     "model_registry": dict[str, str],       # model_name -> version it manages
# }
```

### 5.5 ParaCore Checkpoint

```python
class ParaCoreCheckpointMetadata(TypedDict):
    """Additional metadata for ParaCore monitoring state."""
    anomaly_model_version: str      # Version of anomaly detection model
    threshold_history: list[dict[str, Any]]  # History of threshold adjustments
    alert_count: int                # Total alerts issued
    override_count: int             # Total overrides issued
    active_overrides: list[dict[str, Any]]   # Currently active overrides
    learning_rate: float            # Adaptive threshold learning rate

# torch.save() structure for ParaCore:
# {
#     **CheckpointEnvelope,
#     "metadata": ParaCoreCheckpointMetadata,
#     "anomaly_detector_state": dict[str, Any],  # Anomaly detection model weights
#     "threshold_adapters": dict[str, float],     # Learned thresholds per core
#     "observation_stats": dict[str, dict[str, float]],  # Running mean/var per metric
# }
```

---

## 6. Versioning & Migration

### 6.1 Schema Versioning

Every schema includes a version field. When breaking changes are introduced:

1. Bump the `format_version` in the checkpoint envelope
2. Add a migration function in `migration.py`
3. Update this document with the new schema
4. Mark the old schema as deprecated

### 6.2 Compatibility Matrix

| Schema | Current Version | Backward Compatible | Migration Available |
|---|---|---|---|
| EventEnvelope | 1.0 | Yes | N/A |
| RPC Envelope | 1.0 | Yes | N/A |
| Base Config | 1.0 | Yes | N/A |
| NLP Checkpoint | 1.0 | Yes | N/A |
| Vision Checkpoint | 1.0 | Yes | N/A |
| Meta-Evolution Checkpoint | 1.0 | Yes | N/A |
| ParaCore Checkpoint | 1.0 | Yes | N/A |

### 6.3 Breaking Change Policy

- **Minor version bump** (e.g. 1.0 → 1.1): New optional fields added, fully backward compatible
- **Major version bump** (e.g. 1.0 → 2.0): Breaking changes; migration function required
- All breaking changes must be announced at least 2 versions in advance
- Migration functions must support N-2 versions

---

## Appendix A: Type Imports

All Python type definitions in this document use these imports:

```python
from __future__ import annotations
from typing import Any, TypedDict, Literal
from datetime import datetime
from uuid import UUID
from dataclasses import dataclass, field
```

## Appendix B: Validation

All payloads MUST be validated before publishing/sending. Use these validators:

```python
from pydantic import BaseModel, Field

# Example: validate a SpecialistRequestPayload
class SpecialistRequestValidator(BaseModel):
    request_id: UUID
    target_core: str = Field(..., min_length=1)
    method: str = Field(..., min_length=1)
    args: list[Any] = Field(default_factory=list)
    kwargs: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(..., ge=0, le=10)
    timeout_sec: float = Field(..., gt=0)
    sender_core: str = Field(..., min_length=1)
```

---

> **Document Version**: 1.0.0
> **Last Updated**: 2026-08-10
> **Maintainer**: Vibhu-Oska Core Team
