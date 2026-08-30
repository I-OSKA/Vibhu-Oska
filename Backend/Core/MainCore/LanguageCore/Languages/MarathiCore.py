"""
Vibhu-Oska AI-OS — MarathiCore
Marathi language support with regional dialect awareness.
"""

from __future__ import annotations

import random
import re
from ..BaseLanguage import DialectInfo, LanguageCoreBase, LanguageFamily, Script


class MarathiCore(LanguageCoreBase):
    """Marathi language core — supports Standard Marathi and Varhadi dialect."""

    @property
    def code(self) -> str:
        return "mr"

    @property
    def name(self) -> str:
        return "Marathi"

    @property
    def native_name(self) -> str:
        return "मराठी"

    @property
    def family(self) -> LanguageFamily:
        return LanguageFamily.INDO_ARYAN

    @property
    def scripts(self) -> list[Script]:
        return [Script.DEVANAGARI]

    @property
    def dialects(self) -> list[DialectInfo]:
        return [
            DialectInfo("Standard Marathi", "मानक मराठी", "Maharashtra", 0.0),
            DialectInfo("Varhadi", "वारहाडी", "Vidarbha", 0.05),
            DialectInfo("Deshi", "देशी", "Western Maharashtra", 0.05),
            DialectInfo("Konkani-influenced", "कोंकणी प्रभावित", "Konkan", 0.05),
        ]

    def detect_pattern(self, text: str) -> float:
        if not text or not text.strip():
            return 0.0

        marathi_tokens = {
            "आहे", "आहेत", "नाही", "करा", "करायचं", "काय", "कसं", "कुठे",
            "तुम्ही", "मी", "तो", "ती", "ते", "हे", "ही", "हं",
            "मला", "तुला", "त्याला", "तिला", "याला",
            "बोला", "सांगा", "द्या", "घ्या", "पहा", "लिहा",
            "धन्यवाद", "नमस्कार", "नमस्ते",
        }

        devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
        if devanagari_chars == 0:
            return 0.0

        words = set(re.findall(r'[\u0900-\u097F]+', text.lower()))
        hits = len(words & marathi_tokens)
        return min(0.3 + hits * 0.12, 0.9) if hits > 0 else 0.1

    def get_greeting(self) -> str:
        return random.choice([
            "नमस्कार! मी कर्ष आहे.",
            "नमस्ते! तुम्हाला काय मदत हवी आहे?",
            "प्रणाम! सांगा, काय करायचं आहे?",
        ])

    def get_farewell(self) -> str:
        return random.choice([
            "पुन्हा भेटू!",
            "धन्यवाद! छान राहा.",
        ])

    def get_error(self) -> str:
        return random.choice([
            "माफ करा, काहीतरी चूक झाली.",
            "क्षमा करा, हे शक्य नाही.",
        ])

    def get_thinking(self) -> str:
        return random.choice(["विचार करत आहे...", "प्रक्रिया होत आहे..."])
