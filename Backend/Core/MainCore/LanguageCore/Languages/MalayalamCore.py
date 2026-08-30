"""
Vibhu-Oska AI-OS — MalayalamCore
Malayalam language support.
"""

from __future__ import annotations

import random
import re
from ..BaseLanguage import DialectInfo, LanguageCoreBase, LanguageFamily, Script


class MalayalamCore(LanguageCoreBase):
    """Malayalam language core."""

    @property
    def code(self) -> str:
        return "ml"

    @property
    def name(self) -> str:
        return "Malayalam"

    @property
    def native_name(self) -> str:
        return "മലയാളം"

    @property
    def family(self) -> LanguageFamily:
        return LanguageFamily.DRAVIDIAN

    @property
    def scripts(self) -> list[Script]:
        return [Script.MALAYALAM]

    @property
    def dialects(self) -> list[DialectInfo]:
        return [
            DialectInfo("Standard Malayalam", "സാധാരണ മലയാളം", "Kerala", 0.0),
            DialectInfo("Malabar Malayalam", "മലബാർ മലയാളം", "North Kerala", 0.05),
            DialectInfo("Central Travancore", "മധ്യ ത്രിവേണ്ഡ്", "Central Kerala", 0.05),
        ]

    def detect_pattern(self, text: str) -> float:
        if not text:
            return 0.0
        malayalam_chars = len(re.findall(r'[\u0D00-\u0D7F]', text))
        if malayalam_chars == 0:
            return 0.0
        malayalam_tokens = {
            "ഞാൻ", "നീ", "അവൻ", "അത്", "ഇത്",
            "എന്ത്", "എങ്ങനെ", "എന്തുകൊണ്ട്", "നിങ്ങൾ", "ഞങ്ങൾ",
            "ചെയ്യുക", "പറയുക", "കാണിക്കുക", "തുറക്കുക", "അടയ്ക്കുക", "എഴുതുക",
            "നന്ദി", "നമസ്തേ", "നമസ്കാരം",
        }
        words = set(re.findall(r'[\u0D00-\u0D7F]+', text.lower()))
        hits = len(words & malayalam_tokens)
        return min(0.3 + hits * 0.12, 0.9) if hits > 0 else 0.1

    def get_greeting(self) -> str:
        return random.choice(["നമസ്കാരം! ഞാൻ കർഷ്.", "നമസ്തേ! നിങ്ങൾക്ക് എന്ത് സഹായം വേണം?"])

    def get_farewell(self) -> str:
        return random.choice(["വീണ്ടും കാണാം!", "നന്ദി! നന്നായിരിക്കൂ."])

    def get_error(self) -> str:
        return random.choice(["ക്ഷമിക്കണം, എന്തോ തെറ്റ് സംഭവിച്ചു.", "ക്ഷമിക്കണം, ഇത് സാധ്യമല്ല."])

    def get_thinking(self) -> str:
        return random.choice(["ചിന്തിക്കുന്നു...", "പ്രോസസ്സ് ചെയ്യുന്നു..."])
