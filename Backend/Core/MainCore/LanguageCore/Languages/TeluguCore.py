"""
Vibhu-Oska AI-OS — TeluguCore
Telugu language support.
"""

from __future__ import annotations

import random
import re
from ..BaseLanguage import DialectInfo, LanguageCoreBase, LanguageFamily, Script


class TeluguCore(LanguageCoreBase):
    """Telugu language core."""

    @property
    def code(self) -> str:
        return "te"

    @property
    def name(self) -> str:
        return "Telugu"

    @property
    def native_name(self) -> str:
        return "తెలుగు"

    @property
    def family(self) -> LanguageFamily:
        return LanguageFamily.DRAVIDIAN

    @property
    def scripts(self) -> list[Script]:
        return [Script.TELUGU]

    @property
    def dialects(self) -> list[DialectInfo]:
        return [
            DialectInfo("Standard Telugu", "ప్రామాణిక తెలుగు", "Andhra/Telangana", 0.0),
            DialectInfo("Rayalaseema", "రాయలసీమ", "Rayalaseema", 0.05),
            DialectInfo("Telangana", "తెలంగాణ", "Telangana", 0.05),
        ]

    def detect_pattern(self, text: str) -> float:
        if not text:
            return 0.0
        telugu_chars = len(re.findall(r'[\u0C00-\u0C7F]', text))
        if telugu_chars == 0:
            return 0.0
        telugu_tokens = {
            "నేను", "నువ్వు", "అతను", "అది", "ఇది",
            "ఎలా", "ఎందుకు", "ఏమిటి", "మీరు", "మేము",
            "చేయి", "చెప్పు", "చూపించు", "తెరువు", "మూసివేయి",
            "ధన్యవాదాలు", "నమస్కారం",
        }
        words = set(re.findall(r'[\u0C00-\u0C7F]+', text.lower()))
        hits = len(words & telugu_tokens)
        return min(0.3 + hits * 0.12, 0.9) if hits > 0 else 0.1

    def get_greeting(self) -> str:
        return random.choice(["నమస్కారం! నేను కర్ష్.", "నమస్తే! మీకు ఏ సహాయం కావాలి?"])

    def get_farewell(self) -> str:
        return random.choice(["మళ్ళీ కలుద్దాం!", "ధన్యవాదాలు! మంచిగా ఉండండి."])

    def get_error(self) -> str:
        return random.choice(["క్షమించండి, ఏదో తప్పు జరిగింది.", "క్షమించండి, ఇది సాధ్యం కాలేదు."])

    def get_thinking(self) -> str:
        return random.choice(["ఆలోచిస్తున్నాను...", "ప్రాసెస్ అవుతోంది..."])
