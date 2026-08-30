"""
Vibhu-Oska AI-OS — HardwareAdapter
Zero-user-interference hardware detection and auto-adaptation.

Classifies device into power tiers and dynamically configures:
  - Model size & quantization
  - Context window limits
  - Thread count & CPU affinity
  - Backend device (CPU/GPU/MPS)
  - Race-to-sleep logic for mobile

All detection is automatic. No user configuration required.
"""

from __future__ import annotations

import logging
import os
import platform
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("HardwareAdapter")


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class PowerTier(Enum):
    """Device power classification based on TDP and sustained performance."""
    MOBILE_ULTRA_LOW = "mobile_ultra_low"      # 3-8W  TDP (Smartphones, Tablets)
    LAPTOP_MOBILE = "laptop_mobile"             # 15-45W TDP (Thin/Light, Gaming)
    DESKTOP_UNBOUND = "desktop_unbound"         # 65-250W+ TDP (PC, Workstation)
    UNKNOWN = "unknown"


class BackendDevice(Enum):
    """Compute backend selection."""
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"  # Apple Metal
    AUTO = "auto"


class ThermalState(Enum):
    """Current thermal condition."""
    COOL = "cool"           # Below 60°C — full performance
    WARM = "warm"           # 60-80°C — moderate throttling
    HOT = "hot"             # 80-90°C — heavy throttling
    CRITICAL = "critical"   # Above 90°C — emergency throttle


@dataclass
class HardwareProfile:
    """Complete hardware snapshot of the running device."""
    # Platform
    platform: str = ""
    architecture: str = ""
    
    # CPU
    cpu_name: str = ""
    cpu_cores_physical: int = 0
    cpu_cores_logical: int = 0
    cpu_freq_max_mhz: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # GPU
    gpu_name: str = ""
    gpu_vram_total_gb: float = 0.0
    gpu_vram_used_gb: float = 0.0
    gpu_temp_c: float = 0.0
    gpu_available: bool = False
    
    # Memory
    ram_total_gb: float = 0.0
    ram_available_gb: float = 0.0
    ram_usage_percent: float = 0.0
    
    # Battery
    battery_plugged: bool = True
    battery_percent: float = 100.0
    
    # Thermal
    cpu_temp_c: float = 0.0
    thermal_state: ThermalState = ThermalState.COOL
    
    # Classification
    power_tier: PowerTier = PowerTier.UNKNOWN
    tdp_estimate_w: float = 0.0
    
    # Adapted config
    backend_device: BackendDevice = BackendDevice.AUTO
    max_context_window: int = 4096
    recommended_threads: int = 4
    quantization_level: str = "Q4_K_M"


@dataclass
class AdaptationConfig:
    """Configuration applied by the adapter."""
    model_target: str = "karsh"
    context_window: int = 4096
    backend_device: str = "cpu"
    threads: int = 4
    quantization: str = "Q4_K_M"
    use_gpu: bool = False
    race_to_sleep: bool = False
    max_background_threads: int = 2


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class HardwareDetector:
    """
    Detects hardware specifications without user intervention.
    Runs once at startup and periodically refreshes thermal/power state.
    """

    def __init__(self) -> None:
        self._psutil = None
        self._pynvml = None
        self._ensure_deps()

    def _ensure_deps(self) -> None:
        """Import available dependencies."""
        try:
            import psutil
            self._psutil = psutil
        except ImportError:
            logger.warning("psutil not installed — hardware detection limited")

        try:
            import pynvml
            self._pynvml = pynvml
        except ImportError:
            pass  # GPU detection will return unavailable

    def detect_all(self) -> HardwareProfile:
        """
        Full hardware detection — runs automatically at startup.
        Returns complete HardwareProfile.
        """
        profile = HardwareProfile()
        profile.platform = sys.platform
        profile.architecture = platform.machine()

        self._detect_cpu(profile)
        self._detect_gpu(profile)
        self._detect_memory(profile)
        self._detect_battery(profile)
        self._detect_thermal(profile)
        self._classify_power_tier(profile)

        return profile

    def refresh_thermal(self, profile: HardwareProfile) -> HardwareProfile:
        """
        Lightweight refresh — only updates thermal and power state.
        Called every 30 seconds in background.
        """
        self._detect_battery(profile)
        self._detect_thermal(profile)
        self._classify_power_tier(profile)
        return profile

    def _detect_cpu(self, profile: HardwareProfile) -> None:
        """Detect CPU specs."""
        if not self._psutil:
            profile.cpu_cores_logical = os.cpu_count() or 4
            profile.cpu_cores_physical = profile.cpu_cores_logical // 2
            return

        profile.cpu_cores_physical = self._psutil.cpu_count(logical=False) or 4
        profile.cpu_cores_logical = self._psutil.cpu_count(logical=True) or 8
        profile.cpu_usage_percent = self._psutil.cpu_percent(interval=0.1)

        freq = self._psutil.cpu_freq()
        if freq:
            profile.cpu_freq_max_mhz = freq.max or freq.current

        profile.cpu_name = platform.processor() or "Unknown CPU"

    def _detect_gpu(self, profile: HardwareProfile) -> None:
        """Detect NVIDIA GPU via pynvml."""
        if not self._pynvml:
            profile.gpu_available = False
            return

        try:
            self._pynvml.nvmlInit()
            handle = self._pynvml.nvmlDeviceGetHandleByIndex(0)
            info = self._pynvml.nvmlDeviceGetMemoryInfo(handle)
            name = self._pynvml.nvmlDeviceGetName(handle)

            profile.gpu_name = name if isinstance(name, str) else name.decode()
            profile.gpu_vram_total_gb = info.total / (1024 ** 3)
            profile.gpu_vram_used_gb = info.used / (1024 ** 3)
            profile.gpu_available = True

            # GPU temperature
            try:
                temp = self._pynvml.nvmlDeviceGetTemperature(handle, self._pynvml.NVML_TEMPERATURE_GPU)
                profile.gpu_temp_c = float(temp)
            except Exception:
                pass

            self._pynvml.nvmlShutdown()
        except Exception as e:
            logger.debug("GPU detection failed: %s", e)
            profile.gpu_available = False

    def _detect_memory(self, profile: HardwareProfile) -> None:
        """Detect RAM specs."""
        if not self._psutil:
            return

        mem = self._psutil.virtual_memory()
        profile.ram_total_gb = round(mem.total / (1024 ** 3), 2)
        profile.ram_available_gb = round(mem.available / (1024 ** 3), 2)
        profile.ram_usage_percent = mem.percent

    def _detect_battery(self, profile: HardwareProfile) -> None:
        """Detect battery state."""
        if not self._psutil:
            return

        battery = self._psutil.sensors_battery()
        if battery is None:
            profile.battery_plugged = True
            profile.battery_percent = 100.0
        else:
            profile.battery_plugged = battery.power_plugged
            profile.battery_percent = battery.percent

    def _detect_thermal(self, profile: HardwareProfile) -> None:
        """Detect CPU thermal state."""
        if not self._psutil:
            return

        try:
            temps = self._psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    if entries:
                        profile.cpu_temp_c = entries[0].current
                        break
        except (AttributeError, Exception):
            pass

        # Classify thermal state
        max_temp = max(profile.cpu_temp_c, profile.gpu_temp_c)
        if max_temp < 60:
            profile.thermal_state = ThermalState.COOL
        elif max_temp < 80:
            profile.thermal_state = ThermalState.WARM
        elif max_temp < 90:
            profile.thermal_state = ThermalState.HOT
        else:
            profile.thermal_state = ThermalState.CRITICAL

    def _classify_power_tier(self, profile: HardwareProfile) -> None:
        """
        Classify device into power tier.
        
        Tier Classification:
        - Mobile Ultra-Low (3-8W):  Smartphones, Tablets
        - Laptop Mobile (15-45W):   Thin & Light, Gaming Laptops
        - Desktop Unbound (65-250W+): PCs, Workstations
        """
        # Detection heuristics
        is_mobile_os = profile.platform in ("android", "ios")
        has_battery = not profile.battery_plugged or profile.battery_percent < 100
        low_tdp_cpu = profile.cpu_cores_physical <= 8 and profile.cpu_freq_max_mhz < 3500
        high_tdp_cpu = profile.cpu_cores_physical >= 8 and profile.cpu_freq_max_mhz >= 3500

        if is_mobile_os:
            profile.power_tier = PowerTier.MOBILE_ULTRA_LOW
            profile.tdp_estimate_w = 5.0
        elif has_battery and low_tdp_cpu and not profile.gpu_available:
            profile.power_tier = PowerTier.MOBILE_ULTRA_LOW
            profile.tdp_estimate_w = 8.0
        elif has_battery and profile.gpu_available:
            profile.power_tier = PowerTier.LAPTOP_MOBILE
            profile.tdp_estimate_w = 35.0
        elif has_battery:
            profile.power_tier = PowerTier.LAPTOP_MOBILE
            profile.tdp_estimate_w = 25.0
        elif high_tdp_cpu or profile.gpu_available:
            profile.power_tier = PowerTier.DESKTOP_UNBOUND
            profile.tdp_estimate_w = 150.0
        else:
            profile.power_tier = PowerTier.DESKTOP_UNBOUND
            profile.tdp_estimate_w = 100.0


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class AdaptationEngine:
    """
    Decides optimal configuration based on hardware profile.
    Zero-user-interference — all decisions automatic.
    """

    @staticmethod
    def compute_config(profile: HardwareProfile) -> AdaptationConfig:
        """
        Generate optimal AdaptationConfig from hardware profile.
        
        Decision Matrix:
        - GPU available + VRAM >= 7.5GB → CUDA backend, Q8 quantization
        - GPU available + VRAM < 7.5GB  → CUDA backend, Q4 quantization
        - Apple Silicon                  → MPS backend
        - CPU only, RAM >= 16GB          → CPU, Q4, larger context
        - CPU only, RAM < 16GB           → CPU, Q4, small context
        - Mobile/Low power               → CPU, Q4, minimal context, race-to-sleep
        """
        config = AdaptationConfig()

        # Thread allocation — always leave 2 cores free for OS
        free_cores = max(1, profile.cpu_cores_logical - 2)

        # ── Desktop/Workstation with GPU ────────────────────────────────────────
        if profile.gpu_available and profile.gpu_vram_total_gb >= 7.5:
            config.backend_device = "cuda"
            config.use_gpu = True
            config.threads = free_cores

            if profile.battery_plugged and profile.thermal_state in (ThermalState.COOL, ThermalState.WARM):
                config.quantization = "Q8_0"  # High quality when plugged + cool
                config.context_window = 8192
            else:
                config.quantization = "Q4_K_M"  # Battery/thermal conservative
                config.context_window = 4096

        # ── Laptop with lower VRAM ──────────────────────────────────────────────
        elif profile.gpu_available and profile.gpu_vram_total_gb >= 4.0:
            config.backend_device = "cuda"
            config.use_gpu = True
            config.threads = free_cores
            config.quantization = "Q4_K_M"
            config.context_window = 4096

        # ── Apple Silicon (MPS) ─────────────────────────────────────────────────
        elif profile.platform == "darwin":
            config.backend_device = "mps"
            config.use_gpu = True
            config.threads = free_cores

            if profile.ram_total_gb >= 32:
                config.context_window = 16384
                config.quantization = "Q4_K_M"
            elif profile.ram_total_gb >= 16:
                config.context_window = 8192
                config.quantization = "Q4_K_M"
            else:
                config.context_window = 4096

        # ── CPU-only Desktop ────────────────────────────────────────────────────
        elif profile.power_tier == PowerTier.DESKTOP_UNBOUND:
            config.backend_device = "cpu"
            config.use_gpu = False
            config.threads = free_cores

            if profile.ram_total_gb >= 32:
                config.context_window = 8192
                config.quantization = "Q4_K_M"
            elif profile.ram_total_gb >= 16:
                config.context_window = 4096
            else:
                config.context_window = 2048
                config.quantization = "Q3_K_S"

        # ── Laptop (CPU-only or low VRAM) ───────────────────────────────────────
        elif profile.power_tier == PowerTier.LAPTOP_MOBILE:
            config.backend_device = "cpu"
            config.use_gpu = False
            config.threads = max(1, free_cores - 1)  # Extra conservative for battery

            if profile.battery_plugged:
                config.context_window = 4096
            else:
                config.context_window = 2048
                config.quantization = "Q4_K_M"
                config.race_to_sleep = True  # Blast then sleep

        # ── Mobile / Ultra-Low Power ────────────────────────────────────────────
        elif profile.power_tier == PowerTier.MOBILE_ULTRA_LOW:
            config.backend_device = "cpu"
            config.use_gpu = False
            config.threads = max(1, profile.cpu_cores_logical // 2)
            config.context_window = 2048
            config.quantization = "Q3_K_S"  # Smallest footprint
            config.race_to_sleep = True
            config.max_background_threads = 1

        # ── Thermal throttling — reduce everything ──────────────────────────────
        if profile.thermal_state == ThermalState.HOT:
            config.threads = max(1, config.threads // 2)
            config.context_window = min(config.context_window, 2048)
            config.quantization = "Q4_K_M"

        elif profile.thermal_state == ThermalState.CRITICAL:
            config.threads = 1
            config.context_window = 1024
            config.quantization = "Q3_K_S"

        return config


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class HardwareAdapter:
    """
    HardwareAdapter — Zero-user-interference hardware detection and auto-adaptation.

    Usage:
        adapter = HardwareAdapter.get_instance()
        await adapter.initialize()  # Auto-detects hardware
        config = adapter.get_config()  # Get current optimal config

    Lifecycle:
        initialize() → detect → classify → adapt
        refresh()    → update thermal/power (called every 30s)

    This module sits at the TOP of the initialization chain.
    All other cores read from HardwareAdapter for their configuration.
    """

    _instance: Optional["HardwareAdapter"] = None

    def __init__(self) -> None:
        self._detector = HardwareDetector()
        self._profile: Optional[HardwareProfile] = None
        self._config: Optional[AdaptationConfig] = None
        self._initialized = False
        self._last_refresh = 0.0
        self._refresh_interval = 30.0  # seconds

    @classmethod
    def get_instance(cls) -> "HardwareAdapter":
        """Return singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self) -> None:
        """
        Auto-detect hardware and compute optimal config.
        Called once at startup — no user intervention needed.
        """
        if self._initialized:
            return

        logger.info("HardwareAdapter initializing — detecting hardware...")
        self._profile = self._detector.detect_all()
        self._config = AdaptationEngine.compute_config(self._profile)
        self._initialized = True
        self._last_refresh = time.time()

        logger.info(
            "HardwareAdapter ready: tier=%s, gpu=%s, backend=%s, context=%d, threads=%d, quant=%s",
            self._profile.power_tier.value,
            self._profile.gpu_name or "none",
            self._config.backend_device,
            self._config.context_window,
            self._config.threads,
            self._config.quantization,
        )

    async def refresh(self) -> None:
        """
        Lightweight thermal/power refresh.
        Called periodically (every 30s) from background monitor.
        """
        if not self._initialized or self._profile is None:
            return

        now = time.time()
        if now - self._last_refresh < self._refresh_interval:
            return

        self._detector.refresh_thermal(self._profile)
        self._config = AdaptationEngine.compute_config(self._profile)
        self._last_refresh = now

    def get_profile(self) -> HardwareProfile:
        """Return current hardware profile."""
        if self._profile is None:
            raise RuntimeError("HardwareAdapter not initialized — call initialize() first")
        return self._profile

    def get_config(self) -> AdaptationConfig:
        """Return current optimal configuration."""
        if self._config is None:
            raise RuntimeError("HardwareAdapter not initialized — call initialize() first")
        return self._config

    def get_summary(self) -> dict[str, Any]:
        """Return human-readable hardware summary."""
        if self._profile is None:
            return {"status": "not_initialized"}

        p = self._profile
        c = self._config or AdaptationConfig()

        return {
            "platform": p.platform,
            "power_tier": p.power_tier.value,
            "tdp_estimate_w": p.tdp_estimate_w,
            "cpu": {
                "cores_physical": p.cpu_cores_physical,
                "cores_logical": p.cpu_cores_logical,
                "freq_max_mhz": p.cpu_freq_max_mhz,
                "usage_percent": p.cpu_usage_percent,
            },
            "gpu": {
                "available": p.gpu_available,
                "name": p.gpu_name,
                "vram_total_gb": round(p.gpu_vram_total_gb, 2),
                "vram_used_gb": round(p.gpu_vram_used_gb, 2),
            },
            "memory": {
                "total_gb": p.ram_total_gb,
                "available_gb": p.ram_available_gb,
                "usage_percent": p.ram_usage_percent,
            },
            "battery": {
                "plugged": p.battery_plugged,
                "percent": p.battery_percent,
            },
            "thermal": {
                "cpu_temp_c": p.cpu_temp_c,
                "gpu_temp_c": p.gpu_temp_c,
                "state": p.thermal_state.value,
            },
            "adapted_config": {
                "backend": c.backend_device,
                "context_window": c.context_window,
                "threads": c.threads,
                "quantization": c.quantization,
                "race_to_sleep": c.race_to_sleep,
            },
        }
