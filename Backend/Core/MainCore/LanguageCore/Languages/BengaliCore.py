"""
Vibhu-Oska AI-OS — BengaliCore
Bengali (Bangla) language support.
"""

from __future__ import annotations

import random
import re
from ..BaseLanguage import DialectInfo, LanguageCoreBase, LanguageFamily, Script


class BengaliCore(LanguageCoreBase):
    """Bengali language core — supports Standard Bengali and dialects."""

    @property
    def code(self) -> str:
        return "bn"

    @property
    def name(self) -> str:
        return "Bengali"

    @property
    def native_name(self) -> str:
        return "বাংলা"

    @property
    def family(self) -> LanguageFamily:
        return LanguageFamily.INDO_ARYAN

    @property
    def scripts(self) -> list[Script]:
        return [Script.BENGALI]

    @property
    def dialects(self) -> list[DialectInfo]:
        return [
            DialectInfo("Standard Bengali", "মানক বাংলা", "West Bengal", 0.0),
            DialectInfo("Bangladeshi Bengali", "বাংলাদেশি বাংলা", "Bangladesh", 0.05),
            DialectInfo("Rarhi", "রাঢ়ী", "olkata region", 0.05),
            DialectInfo("Varendra", "বরেন্দ্র", "North Bengal", 0.05),
        ]

    def detect_pattern(self, text: str) -> float:
        if not text:
            return 0.0

        bengali_chars = len(re.findall(r'[\u0980-\u09FF]', text))
        if bengali_chars == 0:
            return 0.0

        bengali_tokens = {
            "আমি", "তুমি", "সে", "এটা", "ওটা", "কি", "কেন", "কিভাবে",
            "আপনি", "আমাদের", "তোমাদের", "তাদের",
            "করো", "বলো", "দাও", "নাও", "দেখো", "লেখো",
            "ধন্যবাদ", "নমস্কার", "নমস্তে",
        }

        words = set(re.findall(r'[\u0980-\u09FF]+', text.lower()))
        hits = len(words & bengali_tokens)
        return min(0.3 + hits * 0.12, 0.9) if hits > 0 else 0.1

    def get_greeting(self) -> str:
        return random.choice([
            "নমস্কার! আমি কর্ষ।",
            "নমস্তে! আপনাকি কী সাহায্য দরকার?",
            "প্রণাম! বলুন, কী করতে পারি?",
        ])

    def get_farewell(self) -> str:
        return random.choice(["আবার দেখা হবে!", "ধন্যবাদ! ভালো থাকুন।"])

    def get_error(self) -> str:
        return random.choice(["দুঃখিত, কিছু ভুল হয়েছে।", "মাফ করুন, এটি সম্ভব হয়নি।"])

    def get_thinking(self) -> str:
        return random.choice(["ভাবছি...", "প্রক্রিয়া হচ্ছে..."])
