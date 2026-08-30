# Vibhu-Oska AI-OS — EvolutionCore RL Self-Improvement Loop

**Version**: 2.0  
**Core**: EvolutionCore (Destroyer / Shiva)  
**Authority**: ParaCore (Supreme) → EvolutionCore  
**Status**: Phase 0 — Documentation Complete

---

## Overview

EvolutionCore implements a **continuous Reinforcement Learning (RL) self-improvement loop** that enables the system to autonomously improve its specialist models through environment feedback. It is the "Soul/Destroyer" of the Tri-Devas — destroying suboptimal behaviors and creating better ones through trial, error, and reward.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
                        EVOLUTIONCORE                              
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  SANDBOX    │  │  REWARD     │  │  EXPERIENCE │             │
│  │  EXECUTOR   │──▶│  ENGINE     │──▶│  BUFFER     │             │
│  └─────────────┘  └─────────────┘  └──────┬──────┘             │
│                                            │                    │
│  ┌─────────────┐  ┌─────────────┐         │                    │
│  │  GRPO       │◀──│  CODE       │         │                    │
│  │  TRAINER    │   │  GENERATOR  │         │                    │
│  └──────┬──────┘   └─────────────┘         │                    │
│         │                                  │                    │
│         ▼                                  ▼                    │
│  ┌─────────────────────┐   ┌─────────────────────────────┐    │
│  │  SPECIALIST LoRA    │   │  BACKUP SPAWNER             │    │
│  │  UPDATES (Hot-swap) │   │  (Dynamic Pool Scaling)     │    │
│  └─────────────────────┘   └─────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. SandboxExecutor (`SandboxExecutor.py`)

**Purpose**: Safe code execution environment for RL feedback.

```python
class SandboxExecutor:
    """
    Wraps AutomationCore.run_command with safety guarantees:
    - Timeout enforcement (configurable, default 30s)
    - Resource limits via Windows Job Objects (CPU, memory)
    - Output capture (stdout, stderr, return code, timing)
    - Security validation:
      * No network access
      * No privileged operations
      * No filesystem access outside sandbox directory
      * No process spawning
    """
    
    async def execute(
        self, 
        code: str, 
        language: str,
        test_input: str = "",
        expected_output: str = "",
        timeout: int = 30,
        memory_mb: int = 512
    ) -> ExecutionResult:
        """
        Execute code in sandboxed environment.
        
        Returns:
            ExecutionResult(
                success: bool,
                stdout: str,
                stderr: str,
                return_code: int,
                execution_time_ms: float,
                memory_used_mb: float,
                security_violations: List[str]
            )
        """
```

**Supported Languages**: Python, JavaScript/Node, Bash, C++ (compiled), Rust (compiled), Go (compiled)

### 2. RewardEngine (`RewardEngine.py`)

**Purpose**: Multi-domain reward computation for RL training.

```python
class RewardEngine:
    """
    Composable reward functions per domain.
    Returns (reward: float, metadata: Dict[str, float])
    """
    
    # Base reward components (all domains)
    BASE_REWARDS = {
        "syntax_valid": 1.0,        # Code parses without syntax errors
        "executes": 2.0,            # Runs without runtime errors
        "correct_output": 5.0,      # Output matches expected
        "performance": (1.0, 3.0),  # Relative performance bonus
        "security_violation": -10.0 # Penalty for unsafe patterns
    }
    
    # Domain-specific reward functions
    DOMAIN_REWARDS = {
        "coding": {
            **BASE_REWARDS,
            "test_passes": 3.0,           # Unit tests pass
            "type_hints_present": 0.5,    # Has type annotations
            "docstring_present": 0.5,     # Has documentation
            "complexity_penalty": -0.1    # Per cyclomatic complexity point
        },
        "excel": {
            "formula_valid": 1.0,
            "produces_result": 2.0,
            "matches_expected": 5.0,
            "efficient_formula": 1.0      # No volatile functions
        },
        "web_scraping": {
            "selector_works": 1.0,
            "data_extracted": 2.0,
            "complete": 3.0,
            "no_block": 2.0,              # Not blocked by anti-bot
            "respects_robots": 1.0
        },
        "system_admin": {
            "command_succeeds": 1.0,
            "idempotent": 2.0,            # Safe to re-run
            "safe": 3.0,                  # No destructive operations
            "reversible": 2.0             # Can be undone
        },
        "knowledge": {
            "factually_correct": 5.0,
            "well_reasoned": 2.0,
            "cites_sources": 1.0,
            "hallucination": -5.0
        }
    }
    
    def compute_reward(
        self, 
        domain: str, 
        execution_result: ExecutionResult,
        expected: Any = None,
        metadata: Dict = None
    ) -> Tuple[float, Dict[str, float]]:
        """
        Compute total reward from execution result.
        """
```

### 3. ExperienceBuffer (`ExperienceBuffer.py`)

**Purpose**: Prioritized replay buffer for GRPO training.

```python
class ExperienceBuffer:
    """
    Prioritized Experience Replay for GRPO.
    Stores: (state, action, reward, next_state, done, metadata)
    """
    
    def __init__(
        self,
        capacity: int = 100000,
        alpha: float = 0.6,      # Priority exponent
        beta: float = 0.4,       # Importance sampling exponent
        beta_increment: float = 0.001
    ):
        self.buffer = []
        self.priorities = []
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.beta_increment = beta_increment
    
    def add(self, experience: Experience, priority: float = 1.0):
        """Add experience with priority (TD error or reward magnitude)"""
    
    def sample(self, batch_size: int) -> Tuple[List[Experience], List[float], List[int]]:
        """Sample batch with importance sampling weights"""
    
    def update_priorities(self, indices: List[int], priorities: List[float]):
        """Update priorities after gradient step"""
```

### 4. GRPOTrainer (`GRPOTrainer.py`)

**Purpose**: Group Relative Policy Optimization — no critic network needed.

```python
class GRPOTrainer:
    """
    GRPO: Group Relative Policy Optimization
    - No value function/critic needed
    - Group-relative advantages (within batch)
    - Stable training, lower variance
    - Updates LoRA adapters on specialist models (not full weights)
    """
    
    def __init__(
        self,
        model: nn.Module,           # Specialist model with LoRA
        tokenizer,
        reward_engine: RewardEngine,
        experience_buffer: ExperienceBuffer,
        lr: float = 1e-5,
        kl_coef: float = 0.1,       # KL penalty coefficient
        group_size: int = 4,        # Number of generations per prompt
        epochs_per_step: int = 1,
        max_grad_norm: float = 0.5
    ):
    
    def train_step(self, prompts: List[str]) -> Dict[str, float]:
        """
        Single GRPO training step:
        1. Generate group_size completions per prompt
        2. Execute in sandbox, compute rewards
        3. Compute group-relative advantages
        4. Update policy via PPO-style clipped objective
        5. Return metrics: loss, reward_mean, kl_div, entropy
        """
    
    def hot_swap_lora(self, specialist_name: str):
        """Hot-swap updated LoRA weights into running specialist"""
```

**GRPO Algorithm Details:**
```
For each prompt in batch:
  1. Generate G completions: y_1, ..., y_G ~ π_θ(y|x)
  2. Compute rewards: r_1, ..., r_G
  3. Compute group mean: r̄ = (1/G) Σ r_i
  4. Compute advantages: A_i = r_i - r̄
  5. Policy loss: L = -E[min(ratio * A, clip(ratio, 1-ε, 1+ε) * A)]
  6. KL penalty: β * KL(π_θ || π_ref)
  7. Total loss: L_total = L + KL_penalty
  8. Update θ ← θ - lr * ∇L_total
```

### 5. CodeGenerator (`CodeGenerator.py`)

**Purpose**: Generate training tasks for specialists using CognitionCore.

```python
class CodeGenerator:
    """
    Uses CognitionCore (SARA) to generate:
    - Prompts covering domain capabilities
    - Expected outputs with test cases
    - Progressive difficulty curriculum
    """
    
    def __init__(self, cognition_core, domain: str):
        self.cognition = cognition_core
        self.domain = domain
    
    async def generate_training_batch(
        self, 
        count: int,
        difficulty: str = "mixed"  # "easy", "medium", "hard", "mixed"
    ) -> List[TrainingTask]:
        """
        Returns list of TrainingTask:
        TrainingTask(
            prompt: str,
            expected_output: str,
            test_cases: List[TestCase],
            metadata: Dict  # difficulty, subdomain, required_capabilities
        )
        """
    
    async def generate_curriculum(self, stages: int = 5) -> List[List[TrainingTask]]:
        """Generate progressive curriculum from basic to advanced"""
```

### 6. BackupSpawner (`BackupSpawner.py`)

**Purpose**: Dynamic BackupCore pool scaling based on MonitoringCore signals.

```python
class BackupSpawner:
    """
    Manages BackupCore pool size:
    - Spawns new instances when load exceeds threshold
    - Retires idle instances after cooldown
    - Maintains minimum pool size (2)
    - Maximum pool size configurable (default 8)
    """
    
    def __init__(
        self,
        min_pool: int = 2,
        max_pool: int = 8,
        scale_up_threshold: float = 0.8,   # CPU/VRAM utilization
        scale_down_threshold: float = 0.3,
        cooldown_seconds: int = 300
    ):
    
    async def handle_scale_request(self, event: BackupScaleRequest):
        """Called by EvolutionCore on BACKUP_SCALE_REQUEST event"""
    
    async def spawn_backup(self, assumed_role: str = None) -> BackupCore:
        """Create new BackupCore instance, optionally pre-assigned"""
    
    async def retire_backup(self, backup_id: str):
        """Gracefully retire BackupCore instance"""
```

---

## RL Loop Flow (Complete)

```
┌──────────────────────────────────────────────────────────────────────────────┐
                            EVOLUTION LOOP (Continuous)                         
├──────────────────────────────────────────────────────────────────────────────┤
                                                                                 
  1. TASK GENERATION                                                            
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ CodeGenerator (via CognitionCore) creates TrainingTask batch       │  
     │ - Prompt + Expected Output + Test Cases                            │  
     │ - Curriculum: Easy → Medium → Hard                                 │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  2. SPECIALIST INFERENCE                                                         
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ Specialist generates response (code/answer)                        │  
     │ - Temperature sampling for diversity                               │  
     │ - Multiple completions per prompt (group_size=4)                   │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  3. SANDBOX EXECUTION                                                          
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ SandboxExecutor runs code in safe environment                      │  
     │ - Captures: stdout, stderr, return_code, timing, memory            │  
     │ - Security validation                                              │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  4. REWARD COMPUTATION                                                         
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ RewardEngine computes multi-component reward                       │  
     │ - Domain-specific rewards                                          │  
     │ - Penalty for security violations, hallucinations                  │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  5. EXPERIENCE STORAGE                                                         
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ ExperienceBuffer stores (state, action, reward, next_state, done)  │  
     │ - Prioritized by reward magnitude / TD error                       │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  6. GRPO TRAINING STEP                                                         
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ GRPOTrainer samples batch, computes group-relative advantages      │  
     │ - Updates LoRA adapters on specialist models                       │  
     │ - KL penalty prevents catastrophic forgetting                      │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  7. HOT-SWAP & VALIDATE                                                        
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ Updated LoRA weights hot-swapped into running specialist           │  
     │ ValidationCore verifies quality on holdout set                     │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  8. CHECKPOINT & METRICS                                                       
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ Save checkpoint, log metrics to EvolutionCore/checkpoints/         │  
     │ Publish EVOLUTION_CHECKPOINT event                                 │  
     └─────────────────────────────────────────────────────────────────────┘  
                                                                                 
  9. BACKUP SCALING (Async)                                                     
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ MonitoringCore → BACKUP_SCALE_REQUEST → BackupSpawner              │  
     │ Dynamic pool adjustment based on load                              │  
     └─────────────────────────────────────────────────────────────────────┘  
                                                                                 
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Training Data Sources

| Source | Type | Volume | Quality |
|--------|------|--------|---------|
| **Supervised** | Existing corpus + user feedback | Growing | High (human) |
| **RL (Primary)** | Sandbox execution results | Infinite | Automatic |
| **Distillation** | CognitionCore → Specialists | On-demand | High (teacher) |
| **Synthetic** | CodeGenerator (CognitionCore) | Configurable | Medium |

---

## Curriculum Management

```python
class CurriculumManager:
    """
    Progressive difficulty scheduling for RL training.
    """
    
    STAGES = [
        {"name": "basics", "difficulty": "easy", "epochs": 1000},
        {"name": "intermediate", "difficulty": "medium", "epochs": 2000},
        {"name": "advanced", "difficulty": "hard", "epochs": 3000},
        {"name": "expert", "difficulty": "expert", "epochs": 4000},
    ]
    
    def get_current_stage(self, step: int) -> Dict:
        """Return current curriculum stage based on training step"""
    
    def should_advance(self, metrics: Dict) -> bool:
        """Determine if ready for next stage based on reward plateau"""
```

---

## Integration Points

| Component | Integration |
|-----------|-------------|
| **OrchestratorCore** | Routes tasks to specialists for RL generation |
| **MonitoringCore** | Triggers EvolutionCore via `EVOLUTION_TASK_GENERATED` |
| **ValidationCore** | Validates RL-updated specialists before hot-swap |
| **BackupCore Pool** | Scaled by BackupSpawner based on EvolutionCore load |
| **ParaCore** | Can OVERRIDE EvolutionCore (reset policy, halt training) |
| **CognitionCore** | Teacher for distillation; generates training tasks |
| **AutomationCore** | Provides SandboxExecutor execution environment |

---

## Checkpoint Format

```python
# EvolutionCore/checkpoints/evolution_policy_step_{step}.pt
{
    "step": 10000,
    "policy_state_dict": {...},           # GRPO policy network
    "optimizer_state_dict": {...},
    "experience_buffer": {...},           # Serialized buffer state
    "metrics": {
        "reward_mean": 3.2,
        "reward_std": 1.1,
        "kl_div": 0.02,
        "entropy": 1.5,
        "loss": 0.45
    },
    "curriculum_stage": "intermediate",
    "specialist_lora_updates": {          # Per-specialist LoRA deltas
        "python_core": {...},
        "excel_core": {...}
    },
    "timestamp": 1691673600.0
}
```

---

## Configuration

```yaml
# Backend/Core/MainCore/EvolutionCore/config.yaml
evolution_core:
  # GRPO Hyperparameters
  grpo:
    lr: 1e-5
    kl_coef: 0.1
    group_size: 4
    epochs_per_step: 1
    max_grad_norm: 0.5
    clip_epsilon: 0.2
  
  # Experience Buffer
  buffer:
    capacity: 100000
    alpha: 0.6
    beta: 0.4
    beta_increment: 0.001
  
  # Sandbox
  sandbox:
    default_timeout: 30
    max_memory_mb: 512
    allowed_languages: ["python", "javascript", "bash", "cpp", "rust", "go"]
  
  # Reward
  reward:
    clipping: true
    clip_range: [-10, 10]
    diversity_bonus: 0.1
  
  # Curriculum
  curriculum:
    stages: ["basics", "intermediate", "advanced", "expert"]
    advance_threshold: 0.95  # Reward plateau detection
  
  # Backup Scaling
  backup_scaling:
    min_pool: 2
    max_pool: 8
    scale_up_threshold: 0.8
    scale_down_threshold: 0.3
    cooldown_seconds: 300
  
  # Training Schedule
  schedule:
    steps_per_checkpoint: 1000
    steps_per_eval: 500
    max_steps: 100000
    eval_prompts: 50
```

---

## Safety & Guardrails

| Risk | Mitigation |
|------|------------|
| **Reward hacking** | Reward clipping, diversity bonus, human validation gate |
| **Catastrophic forgetting** | KL penalty, distillation from CognitionCore, experience replay |
| **Unsafe code execution** | Sandbox: no network, no privileged ops, filesystem isolation |
| **Runaway training** | Max steps, reward plateau detection, ParaCore OVERRIDE |
| **Weight corruption** | ValidationCore verification before hot-swap, checkpoint rollback |
| **VRAM OOM during training** | Gradient checkpointing, sequential specialist training, 4-bit offload |

---

## Metrics & Monitoring

```python
# Published via EVOLUTION_CHECKPOINT event
METRICS = {
    # Training
    "step": int,
    "loss": float,
    "policy_loss": float,
    "kl_div": float,
    "entropy": float,
    "grad_norm": float,
    
    # Rewards
    "reward_mean": float,
    "reward_std": float,
    "reward_min": float,
    "reward_max": float,
    "reward_per_domain": Dict[str, float],
    
    # Specialists
    "specialists_updated": List[str],
    "lora_rank": int,
    "hot_swap_success": bool,
    
    # System
    "vram_usage_mb": int,
    "training_time_ms": float,
    "sandbox_executions": int,
    "sandbox_failures": int,
    
    # Curriculum
    "curriculum_stage": str,
    "stage_progress": float
}
```

---

## File Structure

```
Backend/Core/MainCore/EvolutionCore/
├── __init__.py
├── EvolutionCore.py              # Main coordinator
├── SandboxExecutor.py            # Safe code execution
├── RewardEngine.py               # Multi-domain rewards
├── ExperienceBuffer.py           # Prioritized replay
├── GRPOTrainer.py                # GRPO implementation
├── CodeGenerator.py              # Training task generation
├── BackupSpawner.py              # Dynamic pool scaling
├── CurriculumManager.py          # Progressive difficulty
├── TriDevasState.py              # Internal: DESTROYER role awareness
├── config.yaml                   # Configuration
└── checkpoints/
    ├── evolution_policy_step_*.pt
    └── best_policy.pt
```

---

## Dependencies

| Dependency | Purpose |
|------------|---------|
| `AutomationCore` | Sandbox execution environment |
| `CognitionCore` | Teacher model, task generation |
| `SpecialistCore` | Models being improved |
| `ValidationCore` | Quality gate for hot-swap |
| `MonitoringCore` | Trigger signals, health metrics |
| `BackupCore` | Pool scaling target |
| `ParaCore` | Supreme override authority |
| `EventBus` | All inter-core communication |

---

## Tri-Devas Internal State (ParaCore Only)

```python
# Logged in ParaCore/TriDevasKnowledge.py
# "DESTROYER initiating GRPO training step 10000"
# "DESTROYER reward mean: 3.2, kl_div: 0.02, entropy: 1.5"
# "DESTROYER hot-swapped LoRA updates to: python_core, excel_core"
# "DESTROYER spawned backup_core_3 for increased load"
# "DESTROYER curriculum advanced to: advanced"
```

---

*End of EvolutionCore RL Loop Documentation*
