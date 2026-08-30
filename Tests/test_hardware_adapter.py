"""Tests for HardwareAdapter module — auto-detect hardware and classify power tier."""

import asyncio
import pytest
from unittest.mock import patch, MagicMock

from Backend.Core.MainCore.HardwareAdapter.HardwareAdapter import (
    HardwareAdapter,
    HardwareDetector,
    AdaptationEngine,
    HardwareProfile,
    PowerTier,
    ThermalState,
    AdaptationConfig,
)


class TestHardwareDetector:
    def test_detect_all(self):
        detector = HardwareDetector()
        profile = detector.detect_all()
        assert isinstance(profile, HardwareProfile)
        assert profile.cpu_cores_logical > 0
        assert profile.cpu_cores_physical > 0
        assert isinstance(profile.platform, str)

    def test_refresh_thermal(self):
        detector = HardwareDetector()
        profile = detector.detect_all()
        refreshed = detector.refresh_thermal(profile)
        assert isinstance(refreshed, HardwareProfile)
        assert refreshed.cpu_temp_c >= 0


class TestAdaptationEngine:
    def test_compute_config_gpu_high_vram(self):
        profile = HardwareProfile()
        profile.gpu_available = True
        profile.gpu_vram_total_gb = 8.0
        profile.cpu_cores_logical = 16
        profile.battery_plugged = True
        profile.thermal_state = ThermalState.COOL
        profile.power_tier = PowerTier.DESKTOP_UNBOUND
        profile.ram_total_gb = 32

        config = AdaptationEngine.compute_config(profile)
        assert isinstance(config, AdaptationConfig)
        assert config.backend_device == "cuda"
        assert config.use_gpu is True
        assert config.context_window >= 4096

    def test_compute_config_gpu_low_vram(self):
        profile = HardwareProfile()
        profile.gpu_available = True
        profile.gpu_vram_total_gb = 4.0
        profile.cpu_cores_logical = 8
        profile.power_tier = PowerTier.LAPTOP_MOBILE
        profile.ram_total_gb = 16

        config = AdaptationEngine.compute_config(profile)
        assert config.backend_device == "cuda"
        assert config.use_gpu is True

    def test_compute_config_cpu_desktop(self):
        profile = HardwareProfile()
        profile.gpu_available = False
        profile.cpu_cores_logical = 16
        profile.power_tier = PowerTier.DESKTOP_UNBOUND
        profile.ram_total_gb = 32
        profile.thermal_state = ThermalState.COOL

        config = AdaptationEngine.compute_config(profile)
        assert config.backend_device == "cpu"
        assert config.use_gpu is False
        assert config.context_window >= 4096

    def test_compute_config_mobile(self):
        profile = HardwareProfile()
        profile.gpu_available = False
        profile.cpu_cores_logical = 8
        profile.power_tier = PowerTier.MOBILE_ULTRA_LOW
        profile.ram_total_gb = 8
        profile.battery_plugged = False
        profile.thermal_state = ThermalState.COOL

        config = AdaptationEngine.compute_config(profile)
        assert config.race_to_sleep is True
        assert config.context_window <= 2048

    def test_compute_config_thermal_hot(self):
        profile = HardwareProfile()
        profile.gpu_available = True
        profile.gpu_vram_total_gb = 8.0
        profile.cpu_cores_logical = 16
        profile.power_tier = PowerTier.DESKTOP_UNBOUND
        profile.ram_total_gb = 32
        profile.thermal_state = ThermalState.HOT

        config = AdaptationEngine.compute_config(profile)
        assert config.threads <= profile.cpu_cores_logical


class TestHardwareAdapter:
    @pytest.fixture
    def adapter(self):
        return HardwareAdapter.get_instance()

    def test_singleton(self):
        a = HardwareAdapter.get_instance()
        b = HardwareAdapter.get_instance()
        assert a is b

    @pytest.mark.asyncio
    async def test_initialize(self, adapter):
        await adapter.initialize()
        profile = adapter.get_profile()
        assert profile is not None
        assert isinstance(profile.power_tier, PowerTier)

    @pytest.mark.asyncio
    async def test_get_config(self, adapter):
        await adapter.initialize()
        config = adapter.get_config()
        assert isinstance(config, AdaptationConfig)
        assert config.backend_device in ("cpu", "cuda", "mps", "auto")
        assert config.threads > 0
        assert config.context_window > 0

    @pytest.mark.asyncio
    async def test_power_tier_classification(self, adapter):
        await adapter.initialize()
        tier = adapter.get_profile().power_tier
        assert tier in (PowerTier.MOBILE_ULTRA_LOW, PowerTier.LAPTOP_MOBILE, PowerTier.DESKTOP_UNBOUND, PowerTier.UNKNOWN)
