"""
Vibhu-Oska AI-OS — SanskritCore
Sanskrit language support — the root language of Vibhu-Oska's identity.

Sanskrit is the language of the Trimurti/Tridevis framework. Karsh's name
comes from Sanskrit. This core handles Sanskrit-specific patterns.
"""

from __future__ import annotations

import random
import re
from ..BaseLanguage import DialectInfo, LanguageCoreBase, LanguageFamily, Script


class SanskritCore(LanguageCoreBase):
    """
    Sanskrit language core — supports Classical Sanskrit and Vedic Sanskrit.

    Handles:
    - Devanagari script (primary)
    - IAST transliteration (Latin)
    - Sanskrit-specific word patterns
    """

    @property
    def code(self) -> str:
        return "sa"

    @property
    def name(self) -> str:
        return "Sanskrit"

    @property
    def native_name(self) -> str:
        return "संस्कृतम्"

    @property
    def family(self) -> LanguageFamily:
        return LanguageFamily.INDO_ARYAN

    @property
    def scripts(self) -> list[Script]:
        return [Script.DEVANAGARI, Script.LATIN]

    @property
    def dialects(self) -> list[DialectInfo]:
        return [
            DialectInfo("Classical Sanskrit", "शास्त्रीय संस्कृतम्", "Literary", 0.0),
            DialectInfo("Vedic Sanskrit", "वैदिक संस्कृतम्", "Vedic texts", 0.0),
        ]

    def detect_pattern(self, text: str) -> float:
        """Detect Sanskrit text (Devanagari or IAST transliteration)."""
        if not text or not text.strip():
            return 0.0

        normalized = text.lower().strip()

        # Check for Devanagari
        devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))

        # Sanskrit-specific Devanagari words
        sanskrit_words = {
            "नमस्ते", "धन्यवाद", "कृपया", "भवतः", "अस्मि", "स्मि",
            "वयम्", "त्वम्", "सः", "सा", "तत्", "यत्", "किम्",
            "अस्ति", "सन्ति", "अहम्", "ब्रह्म", "आत्मन्",
            "कर्ष", "विभु", "ओष्का", "त्रिमूर्ति", "त्रिदेवी",
        }

        words = set(re.findall(r'[\u0900-\u097F]+', normalized))
        hits = len(words & sanskrit_words)

        if devanagari_chars > 0:
            confidence = min(0.3 + hits * 0.15, 0.9)
            return confidence

        # IAST transliteration detection
        iast_patterns = [
            r'\b(a|i|u|rī|lī|e|ai|o|au)\s',
            r'ḥ\b', r'ṁ\b', r'ḥ\b',
        ]
        iast_hits = sum(1 for p in iast_patterns if re.search(p, normalized))
        if iast_hits > 0:
            return min(0.4 + iast_hits * 0.1, 0.8)

        return 0.0

    def get_greeting(self) -> str:
        greetings = [
            "नमस्ते! अहं कर्षः अस्मि।",
            "नमस्कार! किम् अस्ति सहाय्यम्?",
            "प्रणाम! भवतः किम् इच्छति?",
        ]
        return random.choice(greetings)

    def get_farewell(self) -> str:
        farewells = [
            "पुनर् मिलामः!",
            "धन्यवादः! शुभम् भवतु।",
        ]
        return random.choice(farewells)

    def get_error(self) -> str:
        errors = [
            "क्षम्यताम्, किञ्चित् दोषः अस्ति।",
            "क्षमा क्रियताम्, एतत् न शक्यते।",
        ]
        return random.choice(errors)

    def get_thinking(self) -> str:
        thinking = [
            "चिन्तयामि...",
            "विचारयामि...",
        ]
        return random.choice(thinking)
