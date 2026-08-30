"""
Vibhu-Oska AI-OS — UrduCore
Urdu language support (Nastaliq/Arabic script).
"""

from __future__ import annotations

import random
import re
from ..BaseLanguage import DialectInfo, LanguageCoreBase, LanguageFamily, Script


class UrduCore(LanguageCoreBase):
    """Urdu language core — supports Standard Urdu."""

    @property
    def code(self) -> str:
        return "ur"

    @property
    def name(self) -> str:
        return "Urdu"

    @property
    def native_name(self) -> str:
        return "اردو"

    @property
    def family(self) -> LanguageFamily:
        return LanguageFamily.INDO_ARYAN

    @property
    def scripts(self) -> list[Script]:
        return [Script.ARABIC]

    @property
    def dialects(self) -> list[DialectInfo]:
        return [
            DialectInfo("Standard Urdu", "معیاری اردو", "India/Pakistan", 0.0),
            DialectInfo("Dakhni", "دکنی", "Deccan", 0.05),
            DialectInfo("Rekhta", "ریختہ", "Literary", 0.05),
        ]

    def detect_pattern(self, text: str) -> float:
        if not text:
            return 0.0
        arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', text))
        if arabic_chars == 0:
            return 0.0
        urdu_tokens = {
            "میں", "تو", "وہ", "یہ", "وہ",
            "کیا", "کیوں", "کیسے", "تم", "ہم",
            "کرو", "کہو", "دکھاؤ", "کھولو", "بند کرو", "لکھو",
            "شکریہ", "سلام", "نमستے",
        }
        words = set(re.findall(r'[\u0600-\u06FF\u0750-\u077F]+', text.lower()))
        hits = len(words & urdu_tokens)
        return min(0.3 + hits * 0.12, 0.9) if hits > 0 else 0.1

    def get_greeting(self) -> str:
        return random.choice(["سلام! میں کرش ہوں.", "نمستے! آپ کو کیا مدد چاہیئے?"])

    def get_farewell(self) -> str:
        return random.choice(["پھر ملیں گے!", "شکریہ! خوش رہیں."])

    def get_error(self) -> str:
        return random.choice(["معذرت، کچھ غلط ہو گیا.", "معذرت، یہ ممکن نہیں ہے."])

    def get_thinking(self) -> str:
        return random.choice(["سوچ رہا ہوں...", "پروسیس ہو رہا ہے..."])
