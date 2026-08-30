"""
Vibhu-Oska AI-OS — System-Wide Constants
Central definitions for VRAM budgets, thresholds, ports, model sizes, and component names.
"""

from __future__ import annotations

from enum import Enum


# ══════════════════════════════════════════════════════════════════
# Hardware Constraints
# ══════════════════════════════════════════════════════════════════

TOTAL_VRAM_GB: float = 8.0
TOTAL_RAM_GB: float = 16.0
GPU_DEVICE: str = "cuda"
CPU_DEVICE: str = "cpu"


# ══════════════════════════════════════════════════════════════════
# VRAM Budget Allocation (GB)
# ══════════════════════════════════════════════════════════════════

class VRAMBudget:
    PARACORE: float = 1.5       # 3B model int4 quantized
    TRI_DEVAS: float = 1.5      # 3 x 0.5GB (OrchestratorCore, CognitionCore, EvolutionCore)
    OPERATIONAL: float = 1.0    # 4 x 0.25GB (Orchestrator, Monitoring, Optimization, Validation)
    SPECIALISTS: float = 1.0    # Shared specialist pool
    BACKUP_POOL: float = 0.5    # 3-4 generalist backups (lazy loaded)
    BUFFER: float = 0.5         # Emergency reserve
    TOTAL: float = 6.0          # Leaves 2GB headroom for OS/system


# ══════════════════════════════════════════════════════════════════
# Model Sizes
# ══════════════════════════════════════════════════════════════════

class ModelSize:
    PARACORE_PARAMS: int = 3_000_000_000      # 3B params
    TRI_DEVA_PARAMS: int = 1_000_000_000      # 1B params each
    OPERATIONAL_PARAMS: int = 500_000_000     # 500M params each
    SPECIALIST_PARAMS: int = 100_000_000      # 100M params each
    BACKUP_PARAMS: int = 500_000_000          # 500M params each
    ROUTER_PARAMS: int = 3_000_000            # 3M params (existing)
    SOVEREIGN_GPT_PARAMS: int = 25_000_000    # 25M params (current)


# ══════════════════════════════════════════════════════════════════
# Network Ports
# ══════════════════════════════════════════════════════════════════

class Ports:
    GATEWAY: int = 8100
    EVENT_BUS_PUB: int = 5555
    EVENT_BUS_SUB: int = 5556
    EVENT_BUS_TASK: int = 5557
    EVENT_BUS_RESULT: int = 5558
    WEBSOCKET: int = 8100
    MCP_SERVER: int = 8101


# ══════════════════════════════════════════════════════════════════
# Component Names
# ══════════════════════════════════════════════════════════════════

class CoreNames:
    # Trimurti (Three Supreme Cores)
    BRAHMA: str = "OrchestratorCore"     # Creator — creates task flow, routes
    VISHNU: str = "CognitionCore"        # Preserver — preserves knowledge, hosts Karsh
    SHIVA: str = "EvolutionCore"         # Transformer — destroys old, transforms via RL

    # Tridevis (Shakti of Trimurti)
    SARASWATI: str = "MonitoringCore"    # Wisdom — observes, records
    LAKSHMI: str = "OptimizationCore"    # Abundance — optimizes resources
    PARVATI: str = "TrainingPipeline"    # Power — feeds evolution

    # Coordinator
    PARACORE: str = "ParaCore"

    # Operational Cores
    COGNITION_CORE: str = "CognitionCore"
    EVOLUTION_CORE: str = "EvolutionCore"
    ORCHESTRATOR_CORE: str = "OrchestratorCore"
    MONITORING_CORE: str = "MonitoringCore"
    OPTIMIZATION_CORE: str = "OptimizationCore"
    VALIDATION_CORE: str = "ValidationCore"
    BACKUP_CORE: str = "BackupCore"
    FAST_RESPONDER: str = "FastResponder"
    DATA_CORE: str = "DataCore"
    AUTOMATION_CORE: str = "AutomationCore"
    DESIGN_CORE: str = "DesignCore"
    IMAGE_GEN_CORE: str = "ImageGenerationCore"
    VOICE_CORE: str = "VoiceCore"
    DISTRIBUTION_CORE: str = "DistributionCore"

    # Model Names
    SARA_MODEL: str = "sara"          # The model file name


# ══════════════════════════════════════════════════════════════════
# Monitoring Thresholds
# ══════════════════════════════════════════════════════════════════

class Thresholds:
    CPU_WARNING: float = 80.0
    CPU_CRITICAL: float = 95.0
    RAM_WARNING: float = 12.0      # GB
    RAM_CRITICAL: float = 14.0     # GB
    VRAM_WARNING: float = 6.0      # GB
    VRAM_CRITICAL: float = 7.0     # GB
    LATENCY_WARNING: float = 2.0   # seconds
    LATENCY_CRITICAL: float = 5.0  # seconds
    HEARTBEAT_INTERVAL: float = 30.0  # seconds
    HEALTH_CHECK_TIMEOUT: float = 10.0  # seconds


# ══════════════════════════════════════════════════════════════════
# Training Constants
# ══════════════════════════════════════════════════════════════════

class Training:
    MAX_GRAD_NORM: float = 1.0
    DEFAULT_LR: float = 3e-4
    DEFAULT_EPOCHS: int = 60
    DEFAULT_BATCH_SIZE: int = 8
    DEFAULT_MAX_LEN: int = 512
    DEFAULT_VOCAB_SIZE: int = 8000
    PATIENCE: int = 5
    VAL_SPLIT: float = 0.1
    NAN_THRESHOLD: int = 3  # Switch to fp32 after 3 NaN batches


# ══════════════════════════════════════════════════════════════════
# Specialist Domains
# ══════════════════════════════════════════════════════════════════

class CodingSpecialists:
    CODE_REVIEW: str = "CodeReview"
    REFACTORING: str = "Refactoring"
    TESTING: str = "Testing"
    DOCUMENTATION: str = "Documentation"
    DEBUGGING: str = "Debugging"
    ARCHITECTURE: str = "Architecture"
    SECURITY: str = "Security"
    PERFORMANCE: str = "Performance"
    MIGRATION: str = "Migration"
    INTEGRATION: str = "Integration"


class RealWorldSpecialists:
    WEB_RESEARCH: str = "WebResearch"
    DATA_ANALYSIS: str = "DataAnalysis"
    FILE_MANAGEMENT: str = "FileManagement"
    SYSTEM_ADMIN: str = "SystemAdmin"
    NETWORK_OPS: str = "NetworkOps"
    DATABASE_OPS: str = "DatabaseOps"
    DEV_OPS: str = "DevOps"
    CONTENT_CREATION: str = "ContentCreation"
    TRANSLATION: str = "Translation"
    PLANNING: str = "Planning"


# ══════════════════════════════════════════════════════════════════
# Fallback Chain
# ══════════════════════════════════════════════════════════════════

class FallbackChain:
    """Priority order for fallback when primary fails."""
    PARACORE = 0           # Primary intelligence
    SPECIALIST = 1         # Domain specialist
    BACKUP_POOL = 2        # Generalist backup
    TEMPLATE_ENGINE = 3    # Deterministic patterns
    GRACEFUL_DEGRADE = 4   # Simplified response


# ══════════════════════════════════════════════════════════════════
# Core States
# ══════════════════════════════════════════════════════════════════

class CoreState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    DEGRADED = "degraded"
    ERROR = "error"
    OFFLINE = "offline"
    TRAINING = "training"


# ══════════════════════════════════════════════════════════════════
# EventBus Topics
# ══════════════════════════════════════════════════════════════════

class Topics:
    USER_INPUT = "user.input"
    SYSTEM_HEALTH = "system.health"
    SYSTEM_ALERT = "system.alert"
    TRAINING_LOG = "training.log"
    TRAINING_COMPLETE = "training.complete"
    INFERENCE_REQUEST = "inference.request"
    INFERENCE_RESPONSE = "inference.response"
    SPECIALIST_REQUEST = "specialist.request"
    SPECIALIST_RESPONSE = "specialist.response"
    BACKUP_REQUEST = "backup.request"
    BACKUP_RESPONSE = "backup.response"
    VRAM_ALERT = "vram.alert"
    EVOLUTION_TRIGGER = "evolution.trigger"
    EVOLUTION_COMPLETE = "evolution.complete"


# ══════════════════════════════════════════════════════════════════
# Error Codes
# ══════════════════════════════════════════════════════════════════

class ErrorCodes:
    NaN_DETECTED = "ERR_NAN_001"
    OOM_DETECTED = "ERR_OOM_001"
    MODEL_FAILURE = "ERR_MODEL_001"
    TIMEOUT = "ERR_TIMEOUT_001"
    VALIDATION_FAILED = "ERR_VALID_001"
    SPECIALIST_UNAVAILABLE = "ERR_SPEC_001"
    BACKUP_EXHAUSTED = "ERR_BACKUP_001"
    VRAM_EXCEEDED = "ERR_VRAM_001"
