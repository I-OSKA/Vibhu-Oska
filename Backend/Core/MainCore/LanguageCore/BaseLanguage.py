"""
Vibhu-Oska AI-OS — BaseLanguage
Abstract base class for all language cores.

Every language must implement these methods to integrate with LanguageCore.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional


class Script(Enum):
    """Detected script of input text."""
    DEVANAGARI = "devanagari"
    LATIN = "latin"
    ARABIC = "arabic"
    CYRILLIC = "cyrillic"
    CJK = "cjk"
    TAMIL = "tamil"
    TELUGU = "telugu"
    BENGALI = "bengali"
    GURMUKHI = "gurmukhi"
    GUJARATI = "gujarati"
    KANNADA = "kannada"
    MALAYALAM = "malayalam"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class LanguageFamily(Enum):
    """Language family classification."""
    INDO_ARYAN = "indo-aryan"
    DRAVIDIAN = "dravidian"
    GERMANIC = "germanic"
    ROMANCE = "romance"
    SLAVIC = "slavic"
    SINO_TIBETAN = "sino-tibetan"
    SEMITIC = "semitic"
    JAPONIC = "japonic"
    KOREANIC = "koreanic"
    TURKIC = "turkic"
    AUSTROASIATIC = "austroasiatic"
    TIBETO_BURMAN = "tibeto-burman"
    CREOLE = "creole"
    CONSTRUCTED = "constructed"
    OTHER = "other"


class DialectInfo:
    """Information about a dialect variant."""

    def __init__(
        self,
        name: str,
        native_name: str,
        region: str,
        confidence_boost: float = 0.0,
    ) -> None:
        self.name = name
        self.native_name = native_name
        self.region = region
        self.confidence_boost = confidence_boost


class LanguageCoreBase(ABC):
    """
    Abstract base class for all language cores.

    Each language core provides:
    - Script detection
    - Language-specific patterns
    - Greeting/farewell/error templates
    - Dialect support
    - Response formatting
    """

    @property
    @abstractmethod
    def code(self) -> str:
        """ISO 639-1 language code (e.g., 'hi', 'en', 'sa')."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Full language name (e.g., 'Hindi', 'English', 'Sanskrit')."""

    @property
    @abstractmethod
    def native_name(self) -> str:
        """Name in the language's own script (e.g., 'हिन्दी', 'English', 'संस्कृतम्')."""

    @property
    @abstractmethod
    def family(self) -> LanguageFamily:
        """Language family classification."""

    @property
    @abstractmethod
    def scripts(self) -> list[Script]:
        """Scripts used by this language (e.g., [DEVANAGARI] for Hindi)."""

    @property
    def dialects(self) -> list[DialectInfo]:
        """Dialect variants supported. Override in subclass if needed."""
        return []

    @abstractmethod
    def detect_pattern(self, text: str) -> float:
        """
        Return a confidence score (0.0 to 1.0) that the text is in this language.

        Parameters:
            text: Input text to analyze
        Returns: Confidence score between 0.0 and 1.0
        """

    @abstractmethod
    def get_greeting(self) -> str:
        """Return a greeting in this language."""

    @abstractmethod
    def get_farewell(self) -> str:
        """Return a farewell in this language."""

    @abstractmethod
    def get_error(self) -> str:
        """Return an error message in this language."""

    @abstractmethod
    def get_thinking(self) -> str:
        """Return a thinking/waiting message in this language."""

    def format_response(self, text: str) -> str:
        """
        Format a response for this language. Override for language-specific formatting.
        Default returns text unchanged.
        """
        return text
