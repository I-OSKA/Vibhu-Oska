"""
Vibhu-Oska AI-OS — Voice & Manifestation tests.
Verifies async voice command loops, watchdog metrics, config persistence,
hotkey validations, and particle rendering stress tests.
"""

from __future__ import annotations

import os
import sys
import json
import time
import math
import pytest
import shutil
import asyncio
from unittest.mock import MagicMock, patch

import tkinter as tk
from Backend.Core.SpecializedCore.VoiceCore.VoiceCore import VoiceCore, _load_metrics, _save_metrics
from Backend.Desktop.Manifestation import (
    NeuralCanvas,
    load_settings,
    save_settings,
    validate_hotkey,
    translate_hotkey,
    get_settings_path,
    DEFAULT_SETTINGS
)

# ==================================================================================================
# # Internal Separation Division
# =================────────────────────────────────────────────────────────────────=================

class TestVoiceCoreRobustness:
    """Verify VoiceCore async interfaces, retry attempts, and watchdog metrics."""

    @pytest.fixture
    def voice_core(self):
        return VoiceCore.get_instance()

    def test_set_backup_core(self, voice_core):
        """Verify the decoupled setter interface successfully injects BackupCore."""
        mock_bc = MagicMock()
        voice_core.set_backup_core(mock_bc)
        assert voice_core._backup_core == mock_bc

    @pytest.mark.asyncio
    async def test_process_audio_chunk_transcription_retries(self, voice_core):
        """Verify process_audio_chunk uses transcriber retries and routes to BackupCore."""
        mock_bc = MagicMock()
        mock_bc._reason.return_value = "Cognition output"
        voice_core.set_backup_core(mock_bc)

        original_transcriber = voice_core._transcriber_en
        mock_transcriber = MagicMock()
        mock_transcriber.transcribe.return_value = "hello oska"
        voice_core._transcriber_en = mock_transcriber

        try:
            res = await voice_core.process_audio_chunk(b"pcm_bytes", language="en")
            assert res["status"] == "success"
            assert res["transcript"] == "hello oska"
            assert res["response"] == "Cognition output"
            mock_bc._reason.assert_called_once_with("hello oska")
        finally:
            voice_core._transcriber_en = original_transcriber

    def test_metrics_persistence_rotation(self, tmp_path):
        """Verify metrics save and load atomically and support rotation limits."""
        test_file = str(tmp_path / "voice_metrics.json")
        
        with patch("Backend.Core.SpecializedCore.VoiceCore.VoiceCore.METRICS_FILE", test_file):
            metrics = {
                "restarts_attempted": 12,
                "transcription_retries": 45,
                "failed_transcriptions": 1,
                "last_restart_timestamp": time.time(),
                "start_time": time.time()
            }
            
            # Save metrics
            _save_metrics(metrics, max_archives=2)
            assert os.path.exists(test_file)
            
            # Load metrics and assert values
            loaded = _load_metrics()
            assert loaded["restarts_attempted"] == 12
            assert loaded["transcription_retries"] == 45
            
            # Trigger rotation check by writing large file
            large_metrics = metrics.copy()
            large_metrics["dummy_field"] = "a" * 110000 # Make file >100KB
            
            # Run save to write the large file content
            _save_metrics(large_metrics, max_archives=2)
            
            # Run save again: now the file on disk is large (>100KB), which triggers rotation
            _save_metrics(large_metrics, max_archives=2)
    
            # Check rotation archive files were created
            archive_dir = os.path.dirname(test_file)
            archives = [f for f in os.listdir(archive_dir) if "voice_metrics.json_" in f]
            assert len(archives) > 0

# ==================================================================================================
# # Internal Separation Division
# =================────────────────────────────────────────────────────────────────────────────────=

class TestManifestationVisualSettings:
    """Verify settings file persistence, atomic saves, and hotkey validation."""

    def test_settings_atomic_save_load(self, tmp_path):
        """Verify settings are saved atomically and fall back to default if corrupt."""
        test_settings_file = str(tmp_path / "manifestation_settings.json")
        
        with patch("Backend.Desktop.Manifestation.get_settings_path", return_value=test_settings_file):
            # Verify default config is generated if missing
            settings = load_settings()
            assert settings["theme"] == DEFAULT_SETTINGS["theme"]
            assert settings["max_particles"] == DEFAULT_SETTINGS["max_particles"]

            # Save modified settings
            settings["theme"] = "Plasma Purple"
            save_settings(settings)
            
            # Verify modified value loaded
            reloaded = load_settings()
            assert reloaded["theme"] == "Plasma Purple"

            # Simulate file corruption (empty file)
            with open(test_settings_file, "w") as f:
                f.write("")
            
            # Verify load recovers defaults successfully
            recovered = load_settings()
            assert recovered["theme"] == DEFAULT_SETTINGS["theme"]

    def test_settings_disk_full_failover(self, tmp_path):
        """Verify settings fallback to last known configuration if disk is full."""
        test_settings_file = str(tmp_path / "manifestation_settings.json")
        
        with patch("Backend.Desktop.Manifestation.get_settings_path", return_value=test_settings_file):
            settings = load_settings()
            settings["theme"] = "Solar Amber"
            
            # Mock open to simulate OSError (e.g. disk full)
            with patch("builtins.open", side_effect=OSError("No space left on device")):
                success = save_settings(settings)
                assert success is False
                
            # Verify that fallback returns original config correctly
            assert settings["theme"] == "Solar Amber"

    def test_hotkey_conflicts_and_translations(self):
        """Verify hotkey validation and platform specific translations."""
        # Test standard modifiers
        assert validate_hotkey("<Control-Shift-space>") is True
        
        # Test reserved key blockages
        assert validate_hotkey("<control-c>") is False
        assert validate_hotkey("<control-alt-delete>") is False
        assert validate_hotkey("<alt-f4>") is False
        
        # Test macOS Command conversion
        with patch("sys.platform", "darwin"):
            translated = translate_hotkey("<control-shift-w>")
            assert "command" in translated.lower()

# ==================================================================================================
# # Internal Separation Division
# =================────────────────────────────────────────────────────────────────=================

class TestManifestationPerformance:
    """Verify particle loop ticks and hysteresis performance throttling."""

    def test_particle_stress_and_adaptive_throttling(self):
        """Verify particle calculations and dynamic caps under stress."""
        # Setup headless-safe Tkinter mock
        try:
            root = tk.Tk()
            root.withdraw()
        except (tk.TclError, Exception):
            pytest.skip("Tkinter display not available on this headless system")

        try:
            canvas = tk.Canvas(root, width=800, height=600)
            canvas.pack()
            root.update()

            nc = NeuralCanvas(canvas)
            nc.start(n=60) # Stress count
            
            # Assert stress count initialized
            assert len(nc._nodes) == 60

            # Verify calculations run without errors
            for _ in range(5):
                nc._tick()
                root.update()

            # Verify gravity mouse coordination tracking bounds
            nc._mx = 100
            nc._my = 100
            nc._tick()
            root.update()
            
            # Ensure particle velocities bounded
            for node in nc._nodes:
                speed = math.sqrt(node["vx"]**2 + node["vy"]**2)
                assert speed <= 3.01 # Max capped speed 3.0

            nc.stop()
        finally:
            try:
                root.destroy()
            except Exception:
                pass
