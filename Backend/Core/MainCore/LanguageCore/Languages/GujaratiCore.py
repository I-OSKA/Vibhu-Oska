"""
Vibhu-Oska AI-OS — GujaratiCore
Gujarati language support.
"""

from __future__ import annotations

import random
import re
from ..BaseLanguage import DialectInfo, LanguageCoreBase, LanguageFamily, Script


class GujaratiCore(LanguageCoreBase):
    """Gujarati language core."""

    @property
    def code(self) -> str:
        return "gu"

    @property
    def name(self) -> str:
        return "Gujarati"

    @property
    def native_name(self) -> str:
        return "ગુજરાતી"

    @property
    def family(self) -> LanguageFamily:
        return LanguageFamily.INDO_ARYAN

    @property
    def scripts(self) -> list[Script]:
        return [Script.GUJARATI]

    @property
    def dialects(self) -> list[DialectInfo]:
        return [
            DialectInfo("Standard Gujarati", "માનક ગુજરાતી", "Gujarat", 0.0),
            DialectInfo("Kutchi", "કચ્છી", "Kutch", 0.05),
            DialectInfo("Sindhi-influenced", "સિંધી પ્રભાવિત", "Saurashtra", 0.05),
        ]

    def detect_pattern(self, text: str) -> float:
        if not text:
            return 0.0
        gujarati_chars = len(re.findall(r'[\u0A80-\u0AFF]', text))
        if gujarati_chars == 0:
            return 0.0
        gujarati_tokens = {
            "હું", "તું", "તે", "આ", "એ", "શું", "કેમ", "કેવી રીતે",
            "તમે", "અમે", "તેઓ",
            "કરો", "કહો", "બતાવો", "ખોલો", "બંધ કરો", "લખો",
            "આભાર", "નમસ્તે", "નમસ્કાર",
        }
        words = set(re.findall(r'[\u0A80-\u0AFF]+', text.lower()))
        hits = len(words & gujarati_tokens)
        return min(0.3 + hits * 0.12, 0.9) if hits > 0 else 0.1

    def get_greeting(self) -> str:
        return random.choice(["નમસ્તે! હું કર્ષ છું.", "નમસ્કાર! તમને શું મદદ જોઈએ છે?"])

    def get_farewell(self) -> str:
        return random.choice(["ફરી મળીશું!", "આભાર! સારા રહો."])

    def get_error(self) -> str:
        return random.choice(["માફ કરશો, કંઈક ખોટું થયું.", "માફ કરશો, આ શક્ય નથી."])

    def get_thinking(self) -> str:
        return random.choice(["વિચારી રહ્યો છું...", "પ્રક્રિયા થઈ રહી છે..."])
