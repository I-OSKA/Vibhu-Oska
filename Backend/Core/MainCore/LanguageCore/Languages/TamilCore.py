"""
Vibhu-Oska AI-OS — TamilCore
Tamil language support.
"""

from __future__ import annotations

import random
import re
from ..BaseLanguage import DialectInfo, LanguageCoreBase, LanguageFamily, Script


class TamilCore(LanguageCoreBase):
    """Tamil language core — supports Standard Tamil and dialects."""

    @property
    def code(self) -> str:
        return "ta"

    @property
    def name(self) -> str:
        return "Tamil"

    @property
    def native_name(self) -> str:
        return "தமிழ்"

    @property
    def family(self) -> LanguageFamily:
        return LanguageFamily.DRAVIDIAN

    @property
    def scripts(self) -> list[Script]:
        return [Script.TAMIL]

    @property
    def dialects(self) -> list[DialectInfo]:
        return [
            DialectInfo("Standard Tamil", "செந்தமிழ்", "Tamil Nadu", 0.0),
            DialectInfo("Madras Bashai", "மதராஸ் பாஷை", "Chennai", 0.05),
            DialectInfo("Jaffna Tamil", "யாழ்ப்பாணத் தமிழ்", "Sri Lanka", 0.05),
        ]

    def detect_pattern(self, text: str) -> float:
        if not text:
            return 0.0

        tamil_chars = len(re.findall(r'[\u0B80-\u0BFF]', text))
        if tamil_chars == 0:
            return 0.0

        tamil_tokens = {
            "நான்", "நீ", "அவன்", "அவள்", "இது", "அது",
            "என்ன", "ஏன்", "எப்படி", "நீங்கள்", "நாங்கள்",
            "செய்", "சொல்", "காட்டு", "திற", "மூடு", "எழுது",
            "நன்றி", "வணக்கம்", "வாழ்த்துக்கள்",
        }

        words = set(re.findall(r'[\u0B80-\u0BFF]+', text.lower()))
        hits = len(words & tamil_tokens)
        return min(0.3 + hits * 0.12, 0.9) if hits > 0 else 0.1

    def get_greeting(self) -> str:
        return random.choice([
            "வணக்கம்! நான் கர்ஷ்.",
            "வாழ்த்துக்கள்! உங்களுக்கு என்ன உதவி வேண்டும்?",
        ])

    def get_farewell(self) -> str:
        return random.choice(["மீண்டும் சந்திப்போம்!", "நன்றி! நல்லமாக இருங்கள்."])

    def get_error(self) -> str:
        return random.choice(["மன்னிக்கவும், ஏதோ தவறு நடந்தது.", "மன்னிக்கவும், இது சாத்தியமில்லை."])

    def get_thinking(self) -> str:
        return random.choice(["யோசிக்கிறேன்...", "செயலாக்கம் நடக்கிறது..."])
