# Shared — Cross-Module Utilities

## Structure

```
Shared/
├── Constants.py           ← CoreState, Topics, CoreNames, paths
├── Models.py              ← Data models (PluginInfo, TaskResponse, etc.)
├── edge_cases/            ← Edge case handlers
│   └── NaNHandler.py      ← NaN/Inf protection
└── shared.md
```

## Key Constants

### CoreState
```python
IDLE, STARTING, RUNNING, STOPPING, ERROR, UNKNOWN
```

### Topics (EventBus)
```python
CORE_HEALTH, TRAINING_LOG, INFERENCE_REQUEST, ALERT
```

### CoreNames
```python
# Trimurti
ORCHESTRATOR_CORE = "orchestrator_core"   # Brahma
COGNITION_CORE = "cognition_core"         # Vishnu
EVOLUTION_CORE = "evolution_core"         # Shiva

# Tridevis
MONITORING_CORE = "monitoring_core"       # Saraswati
OPTIMIZATION_CORE = "optimization_core"   # Lakshmi
TRAINING_PIPELINE = "training_pipeline"   # Parvati

# Supporting
VALIDATION_CORE = "validation_core"       # Yama
FAST_RESPONDER = "fast_responder"         # Hanuman
BACKUP_CORE = "backup_core"               # Nandi
```

## Usage

```python
from Shared.Constants import CoreState, Topics
from Shared.Models import TaskResponse, PluginInfo
```
