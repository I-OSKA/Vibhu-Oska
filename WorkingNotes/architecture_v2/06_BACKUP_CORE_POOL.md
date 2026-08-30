# Vibhu-Oska AI-OS — BackupCore Pool (Versatile)

**Version**: 2.0  
**Core**: BackupCore Pool  
**Authority**: EvolutionCore (Destroyer) → BackupCore Pool  
**Managed By**: EvolutionCore.BackupSpawner  
**Status**: Phase 0 — Documentation Complete

---

## Overview

The **BackupCore Pool** is a dynamic, versatile ensemble of lightweight models that can **assume the role of ANY core** in the system (except ParaCore). Unlike traditional backup systems that maintain 1:1 replicas, each BackupCore is a **single versatile model** with a **RoleAdapter** and access to a **shared CapabilityRegistry** — allowing it to dynamically adopt any core's behavior at runtime.

---

## Core Philosophy

```
Traditional Backup:    1 Primary  ↔  1 Backup (identical copy)
                       10 Specialists ↔ 10 Backups (20+ models)

Vibhu-Oska Backup:    1 Versatile BackupCore Model
                          │
                          ├── RoleAdapter (dynamic role assumption)
                          ├── CapabilityRegistry (shared all-core functions)
                          └── Single Checkpoint (~10M params)
                          
                       N Instances (2-8, dynamically scaled)
                       Each can become: HybridCore, CognitionCore, OrchestratorCore,
                                        MonitoringCore, OptimizationCore, ValidationCore,
                                        ANY Specialist, FastResponder
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
                              BACKUPCORE POOL                                   
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    CAPABILITY REGISTRY                              │   │
│  │  • Global registry of ALL core classes, methods, interfaces         │   │
│  │  • Runtime introspection: get_capabilities(core_name)               │   │
│  │  • Function signatures, type hints, docstrings                      │   │
│  │  • Versioned, hot-reloadable                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│        ┌─────────────────────────────┼─────────────────────────────┐      │
│        ▼                             ▼                             ▼      │
│  ┌───────────────┐          ┌───────────────┐            ┌───────────────┐  │
│  │  BACKUPCORE_1 │          │  BACKUPCORE_2 │     ...    │  BACKUPCORE_N │  │
│  │  (Versatile)  │          │  (Versatile)  │            │  (Versatile)  │  │
│  │               │          │               │            │               │  │
│  │ ┌───────────┐ │          │ ┌───────────┐ │            │ ┌───────────┐ │  │
│  │ │RoleAdapter│ │          │ │RoleAdapter│ │            │ │RoleAdapter│ │  │
│  │ │  .assume  │ │          │ │  .assume  │ │            │ │  .assume  │ │  │
│  │ │ ("hybrid")│ │          │ │("python") │ │            │ │("monitor")│ │  │
│  │ └───────────┘ │          │ └───────────┘ │            │ └───────────┘ │  │
│  │               │          │               │            │               │  │
│  │ Shared Model  │          │ Shared Model  │            │ Shared Model  │  │
│  │ (~10M params) │          │ (~10M params) │            │ (~10M params) │  │
│  └───────────────┘          └───────────────┘            └───────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    POOL MANAGER (EvolutionCore)                     │   │
│  │  • Dynamic scaling: min=2, max=8                                    │   │
│  │  • Health monitoring per instance                                   │   │
│  │  • Role assignment optimization                                     │   │
│  │  • Graceful retirement/replacement                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. BackupCore.py — Versatile Model

```python
class BackupCore:
    """
    Single versatile model that can assume ANY core's role.
    ~10M parameters, fp16 ~0.8GB VRAM, 4-bit ~200MB CPU RAM.
    """
    
    def __init__(self, backup_id: str, config: BackupCoreConfig):
        self.backup_id = backup_id
        self.config = config
        self.current_role: Optional[str] = None
        self.role_context: Optional[RoleContext] = None
        
        # Shared components (injected at creation)
        self.capability_registry: CapabilityRegistry = None
        self.role_adapter: RoleAdapter = None
        self.model: nn.Module = None  # Loaded on first role assumption
        self.tokenizer = None
    
    async def assume_role(self, core_name: str, context: Dict = None) -> bool:
        """
        Dynamically assume a core's role.
        
        Process:
        1. Validate core_name exists in CapabilityRegistry
        2. Load model weights if not loaded (or swap if different architecture)
        3. Configure RoleAdapter for target core
        3. Initialize core-specific state from context
        4. Announce role assumption via EventBus
        5. Return True if successful
        """
        if core_name == "paracore":
            raise PermissionError("Cannot assume ParaCore role")
        
        # Get capability manifest
        capabilities = self.capability_registry.get_capabilities(core_name)
        if not capabilities:
            raise ValueError(f"Unknown core: {core_name}")
        
        # Load/swap model weights
        await self._load_weights_for_role(core_name)
        
        # Configure role adapter
        self.role_context = self.role_adapter.adapt(
            core_name=core_name,
            capabilities=capabilities,
            context=context or {}
        )
        
        self.current_role = core_name
        
        # Announce
        await self.event_bus.publish(Topics.BACKUP_ASSUMED_ROLE, {
            "backup_id": self.backup_id,
            "assumed_role": core_name,
            "capabilities": capabilities.to_dict()
        })
        
        return True
    
    async def execute(self, request: Any) -> Any:
        """Execute request using current role's capabilities"""
        if not self.current_role:
            raise RuntimeError("No role assumed")
        
        # Delegate to role adapter which routes to appropriate methods
        return await self.role_context.execute(request)
    
    async def health_check(self) -> bool:
        """Quick inference test for current role"""
        if not self.current_role:
            return False
        return await self.role_context.health_check()
    
    async def release_role(self):
        """Release current role, return to idle"""
        self.current_role = None
        self.role_context = None
        # Offload weights to CPU (4-bit quantized)
        await self._offload_weights()
```

### 2. CapabilityRegistry.py — Shared Function Registry

```python
class CapabilityRegistry:
    """
    Global registry of ALL core capabilities.
    Populated at system startup by each core registering itself.
    """
    
    def __init__(self):
        self.core_capabilities: Dict[str, CoreCapabilities] = {}
        self.function_registry: Dict[str, Callable] = {}  # Fully qualified names
        self.class_registry: Dict[str, Type] = {}
        self.interface_schemas: Dict[str, InterfaceSchema] = {}
    
    def register_core(self, core_name: str, capabilities: CoreCapabilities):
        """Called by each core at initialization"""
        self.core_capabilities[core_name] = capabilities
        
        # Register all public methods
        for method_name, method_info in capabilities.methods.items():
            fqn = f"{core_name}.{method_name}"
            self.function_registry[fqn] = method_info.callable
        
        # Register classes
        for class_name, class_info in capabilities.classes.items():
            fqn = f"{core_name}.{class_name}"
            self.class_registry[fqn] = class_info.class_type
    
    def get_capabilities(self, core_name: str) -> Optional[CoreCapabilities]:
        """Get full capability manifest for a core"""
        return self.core_capabilities.get(core_name)
    
    def get_function(self, fqn: str) -> Optional[Callable]:
        """Get callable by fully qualified name"""
        return self.function_registry.get(fqn)
    
    def get_class(self, fqn: str) -> Optional[Type]:
        """Get class by fully qualified name"""
        return self.class_registry.get(fqn)
    
    def list_all_cores(self) -> List[str]:
        """List all registered cores"""
        return list(self.core_capabilities.keys())
    
    def get_compatible_roles(self, required_capabilities: List[str]) -> List[str]:
        """Find cores that provide all required capabilities"""
        compatible = []
        for core_name, caps in self.core_capabilities.items():
            if all(cap in caps.provided_capabilities for cap in required_capabilities):
                compatible.append(core_name)
        return compatible


@dataclass
class CoreCapabilities:
    core_name: str
    core_type: str  # "main", "specialist", "utility"
    provided_capabilities: List[str]  # e.g., ["inference", "routing", "validation"]
    methods: Dict[str, MethodInfo]    # name → MethodInfo(callable, signature, doc)
    classes: Dict[str, ClassInfo]     # name → ClassInfo(class_type, init_args)
    vram_requirement_mb: int
    model_params: int
    dependencies: List[str]           # Other cores this depends on


@dataclass
class MethodInfo:
    callable: Callable
    signature: inspect.Signature
    docstring: str
    async: bool
    required_permissions: List[str]
```

### 3. RoleAdapter.py — Dynamic Role Assumption

```python
class RoleAdapter:
    """
    Adapts the versatile BackupCore model to behave like a specific core.
    Handles: method routing, state management, interface compliance.
    """
    
    def __init__(self, capability_registry: CapabilityRegistry, model: nn.Module):
        self.registry = capability_registry
        self.base_model = model
        self.role_configs: Dict[str, RoleConfig] = {}
        self._build_role_configs()
    
    def _build_role_configs(self):
        """Pre-compute adaptation configs for all registered cores"""
        for core_name, caps in self.registry.core_capabilities.items():
            self.role_configs[core_name] = RoleConfig(
                core_name=core_name,
                method_map=self._build_method_map(caps),
                state_schema=caps.state_schema,
                initialization_sequence=caps.init_sequence,
                validation_rules=caps.validation_rules
            )
    
    def adapt(
        self, 
        core_name: str, 
        capabilities: CoreCapabilities,
        context: Dict
    ) -> RoleContext:
        """Create a role context for the target core"""
        config = self.role_configs[core_name]
        
        return RoleContext(
            core_name=core_name,
            config=config,
            base_model=self.base_model,
            registry=self.registry,
            state=context.get("state", {}),
            model_weights=context.get("weights")
        )


class RoleContext:
    """
    Runtime context for an assumed role.
    Provides the interface of the target core.
    """
    
    def __init__(self, core_name: str, config: RoleContext, ...):
        self.core_name = core_name
        self.config = config
        self.state = {}
        self.model = None  # Set when weights loaded
    
    async def execute(self, request: Any) -> Any:
        """Route request to appropriate method"""
        # Determine method from request
        method_name = self._resolve_method(request)
        
        # Get callable from registry
        fqn = f"{self.core_name}.{method_name}"
        func = self.registry.get_function(fqn)
        
        if not func:
            # Fallback: use base model for generation
            return await self._model_fallback(request)
        
        # Execute with current state
        return await func(request, self.state)
    
    async def health_check(self) -> bool:
        """Run core's health check"""
        fqn = f"{self.core_name}.health_check"
        func = self.registry.get_function(fqn)
        if func:
            return await func(self.state)
        return True  # Default healthy
    
    def _resolve_method(self, request: Any) -> str:
        """Map request to core method"""
        # Could use request.type, request.action, or infer from content
        pass
```

### 4. PoolManager.py — EvolutionCore-Managed Scaling

```python
class PoolManager:
    """
    Manages BackupCore pool size and role assignments.
    Controlled by EvolutionCore via BACKUP_SCALE_REQUEST events.
    """
    
    def __init__(
        self,
        min_pool: int = 2,
        max_pool: int = 8,
        scale_up_threshold: float = 0.8,
        scale_down_threshold: float = 0.3,
        cooldown_seconds: int = 300,
        capability_registry: CapabilityRegistry = None
    ):
        self.min_pool = min_pool
        self.max_pool = max_pool
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.cooldown = cooldown_seconds
        self.registry = capability_registry
        
        self.backups: Dict[str, BackupCore] = {}
        self.role_assignments: Dict[str, str] = {}  # backup_id → role
        self.last_scale_time = 0
        self.metrics_history: List[PoolMetrics] = []
    
    async def handle_scale_request(self, event: BackupScaleRequest):
        """Process scale request from EvolutionCore/MonitoringCore"""
        current_time = time.time()
        
        if current_time - self.last_scale_time < self.cooldown:
            return  # Respect cooldown
        
        target_count = event.target_count
        reason = event.reason
        
        if target_count > len(self.backups):
            await self._scale_up(target_count - len(self.backups), reason)
        elif target_count < len(self.backups):
            await self._scale_down(len(self.backups) - target_count, reason)
        
        self.last_scale_time = current_time
    
    async def _scale_up(self, count: int, reason: str):
        """Spawn new BackupCore instances"""
        for i in range(count):
            backup_id = f"backup_core_{len(self.backups) + 1}_{int(time.time())}"
            
            backup = BackupCore(
                backup_id=backup_id,
                config=BackupCoreConfig()
            )
            
            # Inject shared components
            backup.capability_registry = self.registry
            backup.role_adapter = RoleAdapter(self.registry, backup.model)
            backup.event_bus = self.event_bus
            
            await backup.initialize()
            
            self.backups[backup_id] = backup
            
            # Announce spawn
            await self.event_bus.publish(Topics.BACKUP_SPAWNED, {
                "backup_id": backup_id,
                "reason": reason,
                "total_pool_size": len(self.backups)
            })
    
    async def _scale_down(self, count: int, reason: str):
        """Retire idle BackupCore instances"""
        # Select least recently used, non-critical roles
        candidates = self._select_retirement_candidates(count)
        
        for backup_id in candidates:
            backup = self.backups[backup_id]
            
            # Graceful shutdown
            if backup.current_role:
                await self._reassign_role(backup.current_role, exclude=backup_id)
            
            await backup.shutdown()
            del self.backups[backup_id]
            
            await self.event_bus.publish(Topics.BACKUP_RETIRED, {
                "backup_id": backup_id,
                "reason": reason,
                "total_pool_size": len(self.backups)
            })
    
    def _select_retirement_candidates(self, count: int) -> List[str]:
        """Select backups to retire (LRU, idle preferred)"""
        scored = []
        for bid, backup in self.backups.items():
            score = 0
            if backup.current_role is None:
                score += 100  # Idle preferred
            score += backup.idle_time_seconds  # LRU
            if backup.current_role in CRITICAL_ROLES:
                score -= 1000  # Never retire critical roles
            scored.append((score, bid))
        
        scored.sort()
        return [bid for _, bid in scored[:count]]
    
    async def _reassign_role(self, role: str, exclude: str):
        """Reassign role to another backup"""
        for bid, backup in self.backups.items():
            if bid != exclude and backup.current_role is None:
                await backup.assume_role(role)
                self.role_assignments[bid] = role
                return
        
        # If no idle backup, spawn new one
        await self._scale_up(1, f"reassign_{role}")
        # New backup will be assigned in next cycle
    
    def get_pool_status(self) -> PoolStatus:
        """Current pool status for monitoring"""
        return PoolStatus(
            total=len(self.backups),
            active=sum(1 for b in self.backups.values() if b.current_role),
            idle=sum(1 for b in self.backups.values() if not b.current_role),
            roles={bid: b.current_role for bid, b in self.backups.items()},
            vram_usage_mb=sum(b.vram_usage_mb for b in self.backups.values()),
            health={bid: b.last_health_check for bid, b in self.backups.items()}
        )
```

---

## Role Assumption Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
                         ROLE ASSUMPTION SEQUENCE                                
├──────────────────────────────────────────────────────────────────────────────┤
                                                                                 
  1. TRIGGER                                                                      
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ Core failure detected (MonitoringCore)                              │  
     │ OR EvolutionCore needs more capacity                                │  
     │ OR OrchestratorCore needs specialist backup                         │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  2. BACKUP_SCALE_REQUEST EVENT                                                  
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ Published by MonitoringCore/EvolutionCore                           │  
     │ { target_count: 5, reason: "python_core_failed" }                   │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  3. POOL MANAGER SCALES UP                                                      
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ Spawns new BackupCore instance(s)                                   │  
     │ Injects CapabilityRegistry + RoleAdapter                            │  
     │ Announces BACKUP_SPAWNED                                            │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  4. ROLE ASSIGNMENT (OrchestratorCore/EvolutionCore)                          
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ Selects idle BackupCore                                             │  
     │ Calls: backup.assume_role("python_core", context={...})             │  
     │   → CapabilityRegistry.get_capabilities("python_core")              │  
     │   → RoleAdapter.adapt("python_core", capabilities, context)         │  
     │   → Loads PythonCore weights (or uses base + LoRA)                  │  
     │   → Announces BACKUP_ASSUMED_ROLE                                   │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  5. EXECUTION                                                                   
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ OrchestratorCore routes requests to backup_core_X                   │  
     │ backup_core_X.execute(request) → RoleContext.execute()              │  
     │   → Routes to CapabilityRegistry function OR base model             │  
     │   → Returns response as if from PythonCore                          │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  6. RECOVERY / RETIREMENT                                                       
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ Original core recovers → backup releases role                       │  
     │ OR backup no longer needed → PoolManager retires it                 │  
     │ Announces BACKUP_RETIRED                                            │  
     └─────────────────────────────────────────────────────────────────────┘  
                                                                                 
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Supported Roles (All Cores Except ParaCore)

| Core | Role Type | Capabilities Required | VRAM (fp16) |
|------|-----------|----------------------|-------------|
| **HybridCore** | Main | arbitration, heartbeat, paracore_link | 200 MB |
| **CognitionCore** | Main | sara_inference, reasoning | 4200 MB* |
| **EvolutionCore** | Main | rl_training, sandbox_execution | 500 MB |
| **OrchestratorCore** | Main | intent_classify, route, summate | 300 MB |
| **MonitoringCore** | Main | anomaly_detect, proactive_act | 200 MB |
| **OptimizationCore** | Main | model_optimize, vram_manage | 300 MB |
| **ValidationCore** | Main | validate_input, validate_output | 100 MB |
| **PythonCore** | Specialist | python_inference, code_gen | 1200 MB |
| **CppCore** | Specialist | cpp_inference, code_gen | 1200 MB |
| **RustCore** | Specialist | rust_inference, code_gen | 1200 MB |
| **JavaScriptCore** | Specialist | js_inference, code_gen | 1200 MB |
| **GoCore** | Specialist | go_inference, code_gen | 1000 MB |
| **SQLCore** | Specialist | sql_inference, query_opt | 800 MB |
| **BashShellCore** | Specialist | bash_inference, scripting | 600 MB |
| **RegexCore** | Specialist | regex_inference, pattern_match | 600 MB |
| **ExcelCore** | Specialist | excel_inference, formula_gen | 1000 MB |
| **WebScrapingCore** | Specialist | scrape_inference, selector_gen | 1000 MB |
| **FileSystemCore** | Specialist | fs_inference, path_ops | 800 MB |
| **SystemAdminCore** | Specialist | admin_inference, cmd_gen | 1000 MB |
| **KnowledgeCore** | Specialist | knowledge_inference, reasoning | 1200 MB |
| **NetworkCore** | Specialist | network_inference, protocol_design | 1000 MB |
| **DatabaseAdminCore** | Specialist | db_admin_inference, optimization | 1000 MB |
| **CloudCore** | Specialist | cloud_inference, iac_gen | 1000 MB |
| **SecurityCore** | Specialist | security_inference, threat_model | 1000 MB |
| **FastResponderCore** | Utility | math, time, facts, greetings | 400 MB |

\* **CognitionCore**: BackupCore uses a **distilled version** (~50M → ~10M params) for backup role. Full 54M only in primary.

---

## Weight Strategy for Role Assumption

### Option A: Full Weight Swap (Current Design)
```python
# Each role has its own weight file
weights/
├── hybrid_core.pt       # ~200 MB
├── cognition_core_distilled.pt  # ~800 MB (distilled 10M)
├── evolution_core.pt    # ~500 MB
├── orchestrator_core.pt # ~300 MB
├── python_core.pt       # ~1.2 GB
├── excel_core.pt        # ~1.0 GB
# ... etc
```

### Option B: Shared Base + LoRA Adapters (Future Enhancement)
```python
# Single base model + per-role LoRA adapters
weights/
├── backup_base.pt       # ~800 MB (10M params)
├── lora/
│   ├── hybrid_core.pt       # ~10 MB
│   ├── cognition_core.pt    # ~10 MB
│   ├── python_core.pt       # ~10 MB
│   └── ...                  # One per role
```

**Current**: Option A (simpler, faster role switch ~2-3s)  
**Future**: Option B (faster switch ~500ms, less storage)

---

## Pool Scaling Policies

### Scale-Up Triggers
| Trigger | Condition | Target Increase |
|---------|-----------|-----------------|
| **Core Failure** | Any core health_check fails | +1 (assume failed role) |
| **Queue Depth** | Specialist request queue > 10 | +2 |
| **VRAM Pressure** | Active specialists > 2, need more hot | +1 per specialist |
| **EvolutionCore Load** | RL training steps pending > 100 | +2 |
| **Scheduled** | Daily peak hours (configurable) | +2 |

### Scale-Down Triggers
| Trigger | Condition | Target Decrease |
|---------|-----------|-----------------|
| **Idle Timeout** | Backup idle > 10 minutes | -1 per idle |
| **Low Load** | All queues < 2 for 30 min | -1 per 5 min |
| **VRAM Reclaim** | Need VRAM for primary cores | -1 per 500MB needed |
| **Night Hours** | Configured low-traffic period | To min_pool |

---

## Configuration

```yaml
# Backend/Core/BackupCore/config.yaml
backup_core:
  # Model
  model:
    params: 10000000  # 10M
    vocab_size: 8000
    hidden_size: 512
    num_layers: 8
    num_heads: 8
    max_seq_len: 2048
  
  # Pool
  pool:
    min_size: 2
    max_size: 8
    scale_up_threshold: 0.8
    scale_down_threshold: 0.3
    cooldown_seconds: 300
    idle_timeout_seconds: 600
  
  # Role Assumption
  role_assumption:
    max_switch_time_seconds: 5
    weight_cache_size: 3  # Keep 3 role weights hot in CPU RAM
    use_lora_adapters: false  # Future: true
  
  # Health
  health_check:
    interval_seconds: 30
    test_prompt: "health_check"
    max_latency_ms: 1000
  
  # VRAM
  vram:
    fp16_mb: 800
    quantized_4bit_mb: 200
    offload_on_idle: true
    offload_delay_seconds: 60
```

---

## File Structure

```
Backend/Core/BackupCore/
├── __init__.py
├── BackupCore.py                 # Versatile backup model
├── CapabilityRegistry.py         # Shared function/class registry
├── RoleAdapter.py                # Dynamic role assumption
├── PoolManager.py                # EvolutionCore-managed scaling
├── config.yaml
└── checkpoints/
    ├── backup_core.pt            # Base versatile model
    ├── hybrid_core.pt            # Role-specific weights
    ├── cognition_core_distilled.pt
    ├── evolution_core.pt
    ├── orchestrator_core.pt
    ├── monitoring_core.pt
    ├── optimization_core.pt
    ├── validation_core.pt
    ├── python_core.pt
    ├── cpp_core.pt
    ├── rust_core.pt
    ├── javascript_core.pt
    ├── go_core.pt
    ├── sql_core.pt
    ├── bash_core.pt
    ├── regex_core.pt
    ├── excel_core.pt
    ├── web_scraping_core.pt
    ├── filesystem_core.pt
    ├── sysadmin_core.pt
    ├── knowledge_core.pt
    ├── network_core.pt
    ├── dbadmin_core.pt
    ├── cloud_core.pt
    ├── security_core.pt
    └── fast_responder_core.pt
```

---

## Integration Points

| Component | Interaction |
|-----------|-------------|
| **EvolutionCore** | Controls pool via BackupSpawner → BACKUP_SCALE_REQUEST |
| **MonitoringCore** | Detects failures → triggers scale-up |
| **OrchestratorCore** | Routes to backups when primary fails |
| **CapabilityRegistry** | Populated by ALL cores at startup |
| **ValidationCore** | Validates backup responses before return |
| **ParaCore** | Can OVERRIDE: SPAWN_EMERGENCY, QUARANTINE backup |
| **All Cores** | Register capabilities at startup |

---

## Events

| Event | Publisher | Subscribers |
|-------|-----------|-------------|
| `BACKUP_SCALE_REQUEST` | MonitoringCore, EvolutionCore | PoolManager |
| `BACKUP_SPAWNED` | PoolManager | EvolutionCore, MonitoringCore |
| `BACKUP_ASSUMED_ROLE` | BackupCore | OrchestratorCore, EvolutionCore |
| `BACKUP_RETIRED` | PoolManager | EvolutionCore, MonitoringCore |
| `BACKUP_HEALTH_CHECK` | BackupCore (periodic) | MonitoringCore, PoolManager |

---

## Metrics

```python
# Published via BACKUP_HEALTH_CHECK and POOL_STATUS
BACKUP_METRICS = {
    "pool_size": int,
    "active_backups": int,
    "idle_backups": int,
    "role_distribution": Dict[str, int],  # role → count
    "vram_usage_mb": int,
    "avg_role_switch_time_ms": float,
    "successful_assumptions": int,
    "failed_assumptions": int,
    "requests_served": int,
    "avg_latency_ms": float,
    "health_check_pass_rate": float
}
```

---

## Edge Cases & Handling

| Edge Case | Handling |
|-----------|----------|
| **Simultaneous core failures** | PoolManager scales up to cover all; prioritizes critical cores |
| **Weight loading failure** | Fallback to base model + CapabilityRegistry functions only |
| **Role assumption timeout** | Mark backup unhealthy, spawn replacement |
| **CapabilityRegistry missing core** | Log error, use base model fallback |
| **ParaCore override during role switch** | Atomic role switch — override waits or forces release |
| **VRAM OOM during assumption** | Offload idle backups first, then cold specialists |
| **BackupCore model corruption** | Auto-retire, spawn fresh from checkpoint |

---

*End of BackupCore Pool Documentation*
