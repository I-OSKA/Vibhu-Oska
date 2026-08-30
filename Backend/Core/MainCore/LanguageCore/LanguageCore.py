"""
Vibhu-Oska AI-OS — LanguageCore (Umbrella)
Central language processing hub that routes to language-specific cores.

Architecture:
  LanguageCore           → Umbrella router, language detection, singleton entry point
  Languages/             → Individual language cores (Hindi, English, Sanskrit, etc.)
  BaseLanguage.py        → Abstract base class for all language cores

Supported Languages:
  Hindi (hi), English (en), Sanskrit (sa), Marathi (mr), Bengali (bn),
  Tamil (ta), Telugu (te), Gujarati (gu), Kannada (kn), Malayalam (ml),
  Punjabi (pa), Urdu (ur)

Adding a new language:
  1. Create NewLanguageCore.py in Languages/
  2. Extend LanguageCoreBase
  3. Register in LanguageCore._register_languages()
  4. Add detection patterns and templates

All processing is local. Zero external APIs.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from .BaseLanguage import LanguageCoreBase, Script

logger = logging.getLogger("LanguageCore")


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class LanguageDetection:
    """Result of language detection with confidence and metadata."""

    def __init__(
        self,
        language_code: str,
        confidence: float,
        script: Script,
        language_name: str = "",
        native_name: str = "",
    ) -> None:
        self.language_code = language_code
        self.confidence = confidence
        self.script = script
        self.language_name = language_name
        self.native_name = native_name

    def __repr__(self) -> str:
        return (
            f"LanguageDetection(code={self.language_code!r}, "
            f"conf={self.confidence:.2f}, script={self.script.value})"
        )


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class LanguageCore:
    """
    LanguageCore — Umbrella router for all language processing in Vibhu-Oska.

    Usage:
        core = LanguageCore.get_instance()
        det = core.detect("नमस्ते, क्या हाल है?")
        print(det.language_code)  # "hi"
        greeting = core.get_greeting("hi")

    Adding new languages:
        1. Create Languages/NewLangCore.py
        2. Call core.register(NewLangCore())
    """

    _instance: Optional["LanguageCore"] = None

    def __init__(self) -> None:
        self._languages: dict[str, LanguageCoreBase] = {}
        self._register_languages()

    @classmethod
    def get_instance(cls) -> "LanguageCore":
        """Return the singleton LanguageCore instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _register_languages(self) -> None:
        """
        Register all built-in language cores.

        Import here to avoid circular imports at module level.
        """
        from .Languages.HindiCore import HindiCore
        from .Languages.EnglishCore import EnglishCore
        from .Languages.SanskritCore import SanskritCore
        from .Languages.MarathiCore import MarathiCore
        from .Languages.BengaliCore import BengaliCore
        from .Languages.TamilCore import TamilCore
        from .Languages.TeluguCore import TeluguCore
        from .Languages.GujaratiCore import GujaratiCore
        from .Languages.KannadaCore import KannadaCore
        from .Languages.MalayalamCore import MalayalamCore
        from .Languages.PunjabiCore import PunjabiCore
        from .Languages.UrduCore import UrduCore

        built_in = [
            HindiCore(),
            EnglishCore(),
            SanskritCore(),
            MarathiCore(),
            BengaliCore(),
            TamilCore(),
            TeluguCore(),
            GujaratiCore(),
            KannadaCore(),
            MalayalamCore(),
            PunjabiCore(),
            UrduCore(),
        ]

        for lang in built_in:
            self._languages[lang.code] = lang

        logger.info(
            "LanguageCore initialized with %d languages: %s",
            len(self._languages),
            ", ".join(sorted(self._languages.keys())),
        )

    # ── Public API ────────────────────────────────────────────────────────────────────────

    def register(self, language: LanguageCoreBase) -> None:
        """
        Register a new language core at runtime.

        Parameters:
            language: A LanguageCoreBase instance
        """
        self._languages[language.code] = language
        logger.info("Registered language: %s (%s)", language.name, language.code)

    def get_language(self, code: str) -> Optional[LanguageCoreBase]:
        """Get a language core by ISO 639-1 code."""
        return self._languages.get(code)

    def list_languages(self) -> list[dict[str, str]]:
        """Return list of all registered languages with metadata."""
        return [
            {
                "code": lang.code,
                "name": lang.name,
                "native_name": lang.native_name,
                "family": lang.family.value,
            }
            for lang in self._languages.values()
        ]

    def detect(self, text: str) -> LanguageDetection:
        """
        Detect the language of input text.

        Scores all registered languages and returns the best match.

        Parameters:
            text: Input string to analyze
        Returns: LanguageDetection with best match
        Edge cases: Empty text → English with 0.0 confidence
        """
        if not text or not text.strip():
            return LanguageDetection(
                language_code="en",
                confidence=0.0,
                script=Script.UNKNOWN,
            )

        # Detect script first for fast-path
        script = self._detect_script(text)

        best_code = "en"
        best_score = 0.0
        best_name = "English"
        best_native = "English"

        for code, lang in self._languages.items():
            try:
                score = lang.detect_pattern(text)
                if score > best_score:
                    best_score = score
                    best_code = code
                    best_name = lang.name
                    best_native = lang.native_name
            except Exception as e:
                logger.warning("Detection failed for %s: %s", code, e)

        return LanguageDetection(
            language_code=best_code,
            confidence=best_score,
            script=script,
            language_name=best_name,
            native_name=best_native,
        )

    def get_greeting(self, language_code: str) -> str:
        """Get a greeting in the specified language."""
        lang = self._languages.get(language_code)
        if lang:
            return lang.get_greeting()
        # Fallback to English
        return self._languages["en"].get_greeting()

    def get_farewell(self, language_code: str) -> str:
        """Get a farewell in the specified language."""
        lang = self._languages.get(language_code)
        if lang:
            return lang.get_farewell()
        return self._languages["en"].get_farewell()

    def get_error(self, language_code: str) -> str:
        """Get an error message in the specified language."""
        lang = self._languages.get(language_code)
        if lang:
            return lang.get_error()
        return self._languages["en"].get_error()

    def get_thinking(self, language_code: str) -> str:
        """Get a thinking/waiting message in the specified language."""
        lang = self._languages.get(language_code)
        if lang:
            return lang.get_thinking()
        return self._languages["en"].get_thinking()

    def is_language(self, text: str, language_code: str) -> bool:
        """Check if text is in the specified language (confidence > 0.3)."""
        det = self.detect(text)
        return det.language_code == language_code and det.confidence > 0.3

    # ── Script Detection ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _detect_script(text: str) -> Script:
        """Detect the primary script used in text."""
        if not text:
            return Script.UNKNOWN

        ranges = {
            Script.DEVANAGARI: re.compile(r'[\u0900-\u097F]'),
            Script.BENGALI: re.compile(r'[\u0980-\u09FF]'),
            Script.TAMIL: re.compile(r'[\u0B80-\u0BFF]'),
            Script.TELUGU: re.compile(r'[\u0C00-\u0C7F]'),
            Script.KANNADA: re.compile(r'[\u0C80-\u0CFF]'),
            Script.MALAYALAM: re.compile(r'[\u0D00-\u0D7F]'),
            Script.GURMUKHI: re.compile(r'[\u0A00-\u0A7F]'),
            Script.GUJARATI: re.compile(r'[\u0A80-\u0AFF]'),
            Script.ARABIC: re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]'),
            Script.CYRILLIC: re.compile(r'[\u0400-\u04FF]'),
            Script.LATIN: re.compile(r'[a-zA-Z]'),
        }

        counts: dict[Script, int] = {}
        for script, pattern in ranges.items():
            c = len(pattern.findall(text))
            if c > 0:
                counts[script] = c

        if not counts:
            return Script.UNKNOWN

        max_script = max(counts, key=counts.get)
        total = sum(counts.values())

        # If multiple scripts with significant presence, it's mixed
        if len(counts) > 1:
            second = sorted(counts.values(), reverse=True)[1]
            if second / max(total, 1) > 0.2:
                return Script.MIXED

        return max_script
