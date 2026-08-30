"""
Vibhu-Oska AI-OS — PunjabiCore
Punjabi language support (Gurmukhi script).
"""

from __future__ import annotations

import random
import re
from ..BaseLanguage import DialectInfo, LanguageCoreBase, LanguageFamily, Script


class PunjabiCore(LanguageCoreBase):
    """Punjabi language core — supports Standard Punjabi."""

    @property
    def code(self) -> str:
        return "pa"

    @property
    def name(self) -> str:
        return "Punjabi"

    @property
    def native_name(self) -> str:
        return "ਪੰਜਾਬੀ"

    @property
    def family(self) -> LanguageFamily:
        return LanguageFamily.INDO_ARYAN

    @property
    def scripts(self) -> list[Script]:
        return [Script.GURMUKHI]

    @property
    def dialects(self) -> list[DialectInfo]:
        return [
            DialectInfo("Standard Punjabi", "ਮਾਨਕ ਪੰਜਾਬੀ", "Punjab", 0.0),
            DialectInfo("Majhi", "ਮਾਝੀ", "Central Punjab", 0.0),
            DialectInfo("Malwai", "ਮਾਲਵੈ", "Malwa region", 0.05),
            DialectInfo("Doabi", "ਦੋਆਬੀ", "Doaba region", 0.05),
        ]

    def detect_pattern(self, text: str) -> float:
        if not text:
            return 0.0
        gurmukhi_chars = len(re.findall(r'[\u0A00-\u0A7F]', text))
        if gurmukhi_chars == 0:
            return 0.0
        punjabi_tokens = {
            "ਮੈਂ", "ਤੂੰ", "ਉਹ", "ਇਹ", "ਉਹ",
            "ਕੀ", "ਕਿਉਂ", "ਕਿਵੇਂ", "ਤੁਸੀਂ", "ਅਸੀਂ",
            "ਕਰੋ", "ਕਹੋ", "ਦਿਖਾਓ", "ਖੋਲ੍ਹੋ", "ਬੰਦ ਕਰੋ", "ਲਿਖੋ",
            "ਧੰਨਵਾਦ", "ਨਮਸਤੇ", "ਸਤ ਸ੍ਰੀ ਅਕਾਲ",
        }
        words = set(re.findall(r'[\u0A00-\u0A7F]+', text.lower()))
        hits = len(words & punjabi_tokens)
        return min(0.3 + hits * 0.12, 0.9) if hits > 0 else 0.1

    def get_greeting(self) -> str:
        return random.choice(["ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਕਰਸ਼ ਹਾਂ.", "ਨਮਸਤੇ! ਤੁਹਾਡੀ ਕੀ ਮਦਦ ਚਾਹੀਦੀ ਹੈ?"])

    def get_farewell(self) -> str:
        return random.choice(["ਫਿਰ ਮਿਲੇਂਗੇ!", "ਧੰਨਵਾਦ! ਚੰਗੇ ਰਹੋ."])

    def get_error(self) -> str:
        return random.choice(["ਮਾਫ਼ ਕਰਨਾ, ਕੁਝ ਗਲਤ ਹੋ ਗਿਆ.", "ਮਾਫ਼ ਕਰਨਾ, ਇਹ ਸੰਭਵ ਨਹੀਂ ਹੈ."])

    def get_thinking(self) -> str:
        return random.choice(["ਸੋਚ ਰਿਹਾ ਹਾਂ...", "ਪ੍ਰਕਿਰਿਆ ਹੋ ਰਹੀ ਹੈ..."])
