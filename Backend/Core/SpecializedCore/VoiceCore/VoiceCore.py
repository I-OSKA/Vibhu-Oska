"""
Vibhu-Oska AI-OS — VoiceCore
Continuous voice command daemon: wake-word detection → STT → intent → TTS response.

Architecture:
  WakeWordDetector  → listens continuously for "Hey Vibhu" or "Oska"
  AudioTranscriber  → converts audio → text (Vosk local STT, no cloud)
  VoiceRouter       → routes transcription to BackupCore for response
  VoiceResponseEngine → speaks response via pyttsx3 (local Windows SAPI TTS)
  VoiceWebSocket    → WebSocket /ws/voice endpoint for real-time audio stream

All processing is local. Zero cloud STT, zero cloud TTS, zero external APIs.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import queue
import re
import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("VoiceCore")

# Lazy import for LanguageCore to avoid circular imports
_language_core = None

def _get_language_core():
    """Lazy import of LanguageCore to avoid circular dependencies."""
    global _language_core
    if _language_core is None:
        try:
            from Backend.Core.MainCore.LanguageCore.LanguageCore import LanguageCore
            _language_core = LanguageCore.get_instance()
        except ImportError:
            logger.warning("LanguageCore not available for language detection")
    return _language_core


# ==================================================================================================
# # Internal Separation Division
# =================────────────────────────────────────────────────────────────────────────────────


# ── Wake-word configuration ────────────────────────────────────────────────────────────────────
_WAKE_WORDS: list[str] = [
    "hey vibhu", "hey vibhu-oska", "oska", "vibhu",
    "hey oska", "vibhu oska", "ai activate", "vibhu activate",
    # Hindi wake words
    "sun vibhu", "suno vibhu", "hey vibhu ji", "vibhu bolo", "vibhu sun",
]

# ── Vosk model paths (downloaded separately — see docs/VoiceCore.md) ──────────────────────────
_VOSK_MODELS: dict[str, str] = {
    "en": str(Path(__file__).parent.parent.parent.parent.parent / "Models" / "vosk" / "vosk-model-small-en-us"),
    "hi": str(Path(__file__).parent.parent.parent.parent.parent / "Models" / "vosk" / "vosk-model-small-hi"),
}

# ── TTS voice profile (pyttsx3 Windows SAPI) ──────────────────────────────────────────────────
_TTS_CONFIG: dict[str, Any] = {
    "rate": 175,       # Words per minute (170-185 = natural, grounded pace)
    "volume": 0.95,    # 0.0 - 1.0
    "voice_pref": "David",  # Prefer "Microsoft David Desktop" or first available male voice
}

# ── Watchdog metrics persistence (atomic save + rotation) ─────────────────────────────────────
METRICS_FILE = str(Path(__file__).parent.parent.parent.parent.parent / "Data" / "voice_metrics.json")
_ROTATION_THRESHOLD_BYTES = 100 * 1024  # 100KB — beyond this, rotate to a timestamped archive


def _save_metrics(metrics: dict[str, Any], max_archives: int = 2) -> None:
    """Atomically persist watchdog metrics, rotating oversized files into timestamped archives."""
    path = Path(METRICS_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists() and path.stat().st_size > _ROTATION_THRESHOLD_BYTES:
        archive = path.with_name(f"{path.name}_{time.strftime('%Y%m%d_%H%M%S')}")
        os.replace(str(path), str(archive))
        _trim_archives(path, max_archives)

    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(path))


def _trim_archives(path: Path, max_archives: int) -> None:
    archives = sorted(
        path.parent.glob(f"{path.name}_*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for stale in archives[max_archives:]:
        try:
            stale.unlink()
        except OSError:
            pass


def _load_metrics() -> dict[str, Any]:
    """Load persisted watchdog metrics. Returns {} when missing or corrupt."""
    path = Path(METRICS_FILE)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


# ==================================================================================================
# # Internal Separation Division
# =================────────────────────────────────────────────────────────────────────────────────


class WakeWordDetector:
    """
    Continuous microphone listener that fires a callback when a wake word is detected.

    Uses sounddevice + Vosk for offline audio capture and transcription.
    Wake words are matched against partial Vosk recognition results for low latency.

    Parameters: None
    Returns: Fires on_wake_word() callback when detected
    Edge cases: If Vosk model not found, logs warning and disables voice input gracefully
    """

    def __init__(self, on_wake_word: callable, language: str = "en") -> None:
        self._on_wake_word = on_wake_word
        self._language = language
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._model = None
        self._recognizer = None

    def _load_model(self) -> bool:
        """
        Load the Vosk model for the configured language.

        Parameters: none
        Returns: True if model loaded, False if model files not found
        Edge cases: Model path must exist on disk; downloads are not performed at runtime
        """
        try:
            from vosk import Model, KaldiRecognizer
            model_path = _VOSK_MODELS.get(self._language)
            if not model_path or not os.path.exists(model_path):
                logger.warning(
                    "Vosk model not found at %s. "
                    "Download from: https://alphacephei.com/vosk/models",
                    model_path,
                )
                return False
            self._model = Model(model_path)
            self._recognizer = KaldiRecognizer(self._model, 16000)
            return True
        except ImportError:
            logger.error("vosk not installed. Run: pip install vosk")
            return False

    def start(self) -> None:
        """
        Start the wake-word listener in a background daemon thread.

        Parameters: none
        Returns: none
        Edge cases: If model not found, silently skips; thread is daemonized (exits with main process)
        """
        if self._running:
            return
        if not self._load_model():
            logger.warning("WakeWordDetector disabled — model unavailable.")
            return

        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True, name="VoiceCore-WakeWord")
        self._thread.start()
        logger.info("WakeWordDetector started. Wake words: %s", _WAKE_WORDS)

    def stop(self) -> None:
        """
        Stop the wake-word listener thread.

        Parameters: none
        Returns: none
        Edge cases: Safe to call if never started
        """
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)

    def _listen_loop(self) -> None:
        """
        Internal daemon loop: reads microphone audio frames and checks for wake words.

        Parameters: none
        Returns: none (runs indefinitely until self._running = False)
        Edge cases: sounddevice import failure silently disables loop
        """
        try:
            import sounddevice as sd
            from vosk import KaldiRecognizer

            rec = KaldiRecognizer(self._model, 16000)
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                                   channels=1) as stream:
                logger.info("Microphone stream open.")
                while self._running:
                    data, _ = stream.read(4000)
                    if rec.AcceptWaveform(bytes(data)):
                        res = json.loads(rec.Result())
                        text = res.get("text", "").lower()
                    else:
                        partial = json.loads(rec.PartialResult())
                        text = partial.get("partial", "").lower()

                    if text:
                        for wake in _WAKE_WORDS:
                            if wake in text:
                                logger.info("Wake word detected: '%s' in '%s'", wake, text)
                                self._on_wake_word(text)
                                break

        except ImportError:
            logger.error("sounddevice not installed. Run: pip install sounddevice")
        except Exception as e:
            logger.error("WakeWordDetector loop error: %s", e)


# ==================================================================================================
# # Internal Separation Division
# =================────────────────────────────────────────────────────────────────────────────────


class AudioTranscriber:
    """
    One-shot audio transcriber: takes raw 16kHz int16 PCM bytes and returns text.

    Uses Vosk for offline transcription. Supports English and Hindi.
    Returns the best final transcript; falls back to partial if final is empty.

    Parameters: None
    Returns: Transcript string via transcribe()
    Edge cases: Empty audio returns empty string; Vosk model not found returns "[no model]"
    """

    def __init__(self, language: str = "en") -> None:
        self._language = language
        self._model = None

    def _ensure_model(self) -> bool:
        """
        Load the Vosk model on first use (lazy initialization).

        Parameters: none
        Returns: True if model ready, False otherwise
        """
        if self._model is not None:
            return True
        try:
            from vosk import Model
            model_path = _VOSK_MODELS.get(self._language)
            if not model_path or not os.path.exists(model_path):
                return False
            self._model = Model(model_path)
            return True
        except (ImportError, Exception):
            return False

    def transcribe(self, audio_bytes: bytes, sample_rate: int = 16000) -> str:
        """
        Transcribe raw PCM audio bytes to text.

        Parameters:
            audio_bytes: Raw int16 PCM audio data at sample_rate Hz
            sample_rate: Sample rate of the audio (default 16000)
        Returns: Transcribed text string (lowercased)
        Edge cases: Empty audio → ""; model unavailable → "[transcription unavailable]"
        """
        if not self._ensure_model():
            return "[transcription unavailable — Vosk model not found]"
        if not audio_bytes:
            return ""

        try:
            from vosk import KaldiRecognizer
            rec = KaldiRecognizer(self._model, sample_rate)
            rec.AcceptWaveform(audio_bytes)
            result = json.loads(rec.FinalResult())
            return result.get("text", "").strip().lower()
        except Exception as e:
            logger.error("Transcription failed: %s", e)
            return ""


# ==================================================================================================
# # Internal Separation Division
# =================────────────────────────────────────────────────────────────────────────────────


class VoiceResponseEngine:
    """
    Local text-to-speech response engine using Windows SAPI via pyttsx3.

    Selects the first available male voice (preference: David) for a grounded,
    commanding vocal cadence per the Vibhu-Oska design spec.

    Phase 4: Replace with custom neural voice synthesizer built from scratch.

    Parameters: None
    Returns: Speaks text via OS audio output
    Edge cases: pyttsx3 not installed → logs error, no speech; init failure → skips gracefully
    """

    def __init__(self) -> None:
        self._engine = None
        self._lock = threading.Lock()

    def _ensure_engine(self) -> bool:
        """
        Initialize pyttsx3 engine on first use.

        Parameters: none
        Returns: True if engine ready
        Edge cases: Multiple init calls are safe (idempotent)
        """
        if self._engine is not None:
            return True
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", _TTS_CONFIG["rate"])
            engine.setProperty("volume", _TTS_CONFIG["volume"])

            # Prefer male voice
            voices = engine.getProperty("voices")
            for v in voices:
                if _TTS_CONFIG["voice_pref"].lower() in v.name.lower():
                    engine.setProperty("voice", v.id)
                    break
            else:
                # Fallback: first male-sounding voice (not Zira/female)
                for v in voices:
                    if "zira" not in v.name.lower() and "female" not in v.name.lower():
                        engine.setProperty("voice", v.id)
                        break

            self._engine = engine
            return True
        except ImportError:
            logger.error("pyttsx3 not installed. Run: pip install pyttsx3")
            return False
        except Exception as e:
            logger.error("TTS engine init failed: %s", e)
            return False

    def speak(self, text: str) -> None:
        """
        Speak text via the OS TTS engine in a dedicated thread.

        Parameters:
            text: Text to speak (markdown stripped automatically)
        Returns: none (non-blocking — fires in daemon thread)
        Edge cases: Concurrent speak calls are serialized via threading.Lock
        """
        # Strip markdown before speaking
        clean = re.sub(r'[*`#_~>|]', '', text)
        clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)  # Links → link text
        clean = clean.strip()

        if not clean:
            return

        def _speak_thread():
            with self._lock:
                if self._ensure_engine():
                    try:
                        self._engine.say(clean[:500])  # Cap at 500 chars for voice
                        self._engine.runAndWait()
                    except Exception as e:
                        logger.warning("TTS speak error: %s", e)

        t = threading.Thread(target=_speak_thread, daemon=True, name="VoiceCore-TTS")
        t.start()

    def speak_sync(self, text: str) -> None:
        """
        Speak text synchronously (blocks until done).

        Parameters:
            text: Text to speak
        Returns: none
        Edge cases: Blocking — do not call from UI thread
        """
        clean = re.sub(r'[*`#_~>|]', '', text).strip()
        if clean and self._ensure_engine():
            try:
                self._engine.say(clean[:500])
                self._engine.runAndWait()
            except Exception as e:
                logger.warning("TTS sync speak error: %s", e)


# ==================================================================================================
# # Internal Separation Division
# =================────────────────────────────────────────────────────────────────────────────────


class VoiceCore:
    """
    VoiceCore — primary orchestrator for Vibhu-Oska voice command processing.

    Lifecycle:
        initialize() → start() → handle audio frames → stop()

    Features:
        - Continuous wake-word detection ("Hey Vibhu", "Oska", + Hindi variants)
        - Local offline STT via Vosk (en + hi models)
        - Routing to BackupCore for response generation
        - Local TTS via pyttsx3 Windows SAPI
        - WebSocket audio stream handler (/ws/voice)

    Parameters: None (singleton pattern — use VoiceCore.get_instance())
    Returns: Initialized VoiceCore
    Edge cases: Missing Vosk models → voice input disabled, TTS still functional
    """

    _instance: Optional["VoiceCore"] = None

    def __init__(self) -> None:
        self._initialized = False
        self._wake_detector: Optional[WakeWordDetector] = None
        self._transcriber_en = AudioTranscriber(language="en")
        self._transcriber_hi = AudioTranscriber(language="hi")
        self._tts = VoiceResponseEngine()
        self._active_session = False
        self._backup_core: Any = None

    def set_backup_core(self, backup_core: Any) -> None:
        """
        Inject the BackupCore instance used for voice response generation.
        Decoupled setter interface — allows external wiring without circular imports.
        """
        self._backup_core = backup_core

    @classmethod
    def get_instance(cls) -> "VoiceCore":
        """
        Return the singleton VoiceCore instance, creating it if needed.

        Parameters: none
        Returns: VoiceCore singleton
        Edge cases: Thread-safe singleton (single-process server model)
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self) -> None:
        """
        Initialize VoiceCore and start the wake-word detector.

        Parameters: none
        Returns: none (idempotent)
        Edge cases: Safe to call multiple times; voice disabled gracefully if models absent
        """
        if self._initialized:
            return
        self._initialized = True
        logger.info("VoiceCore initializing...")

        # Start wake-word detector
        self._wake_detector = WakeWordDetector(
            on_wake_word=self._on_wake_word_detected,
            language="en",
        )
        self._wake_detector.start()
        logger.info("VoiceCore initialized. Wake word listening active.")

    async def shutdown(self) -> None:
        """
        Stop all voice processing threads cleanly.

        Parameters: none
        Returns: none
        Edge cases: Safe to call if never started
        """
        if self._wake_detector:
            self._wake_detector.stop()
        logger.info("VoiceCore shutdown complete.")

    def _on_wake_word_detected(self, partial_text: str) -> None:
        """
        Callback fired when a wake word is detected in the audio stream.

        Parameters:
            partial_text: The partial transcript containing the wake word
        Returns: none
        Edge cases: Concurrent wake events are ignored if a session is already active
        """
        if self._active_session:
            return  # Ignore while already processing a command
        self._active_session = True
        self._tts.speak("Yes?")
        logger.info("Wake word fired — awaiting command...")
        # Session cleanup happens after command is processed (handled by WebSocket flow)
        asyncio.get_event_loop().call_later(8.0, self._reset_session)

    def _reset_session(self) -> None:
        """Reset the active voice session flag after timeout."""
        self._active_session = False

    async def process_audio_chunk(self, audio_bytes: bytes, language: str = "en") -> dict[str, Any]:
        """
        Process a raw audio chunk received from a WebSocket voice stream.

        Transcribes the audio, routes the text through BackupCore, and speaks the response.
        Uses BilingualCore for language detection when transcript is available.

        Parameters:
            audio_bytes: Raw PCM int16 audio at 16kHz
            language: "en" or "hi" (default "en")
        Returns: dict with transcript, response, status
        Edge cases: Empty audio → {"status": "empty", "transcript": "", "response": ""}
        """
        if not audio_bytes:
            return {"status": "empty", "transcript": "", "response": ""}

        # Transcribe (with bounded retries for transient STT failures)
        transcriber = self._transcriber_hi if language == "hi" else self._transcriber_en
        transcript = ""
        for attempt in range(1, 4):
            try:
                transcript = await asyncio.to_thread(transcriber.transcribe, audio_bytes, 16000)
                if transcript:
                    break
            except Exception as e:
                logger.warning("Transcription attempt %d failed: %s", attempt, e)
                transcript = ""
        if not isinstance(transcript, str):
            transcript = str(transcript)

        if not transcript or len(transcript.strip()) < 2:
            return {"status": "silence", "transcript": "", "response": ""}

        logger.info("Voice transcript [%s]: %s", language, transcript)

        # Auto-detect language from transcript using LanguageCore
        lang_core = _get_language_core()
        detected_lang = language
        if lang_core:
            detection = lang_core.detect(transcript)
            detected_lang = detection.language_code
            logger.info("LanguageCore detected language: %s for transcript", detected_lang)

        # Route through the injected BackupCore (decoupled) — fall back to a
        # standalone instance only when none was injected.
        try:
            if self._backup_core is not None:
                response_text = await asyncio.to_thread(self._backup_core._reason, transcript)
            else:
                from Backend.Core.BackupCore.BackupCore import BackupCore
                bc = BackupCore()
                response_text = await asyncio.to_thread(bc._reason, transcript)
        except Exception as e:
            logger.error("BackupCore routing failed: %s", e)
            if lang_core:
                response_text = lang_core.get_error(detected_lang)
            else:
                response_text = "Processing error — please try again."

        # Speak the response
        self._tts.speak(response_text)
        self._active_session = False  # Release session

        return {
            "status": "success",
            "transcript": transcript,
            "response": response_text,
            "language": detected_lang,
        }

    @property
    def tts(self) -> VoiceResponseEngine:
        """Direct access to TTS engine for external callers."""
        return self._tts

