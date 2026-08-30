"""
Vibhu-Oska AI-OS — KannadaCore
Kannada language support.
"""

from __future__ import annotations

import random
import re
from ..BaseLanguage import DialectInfo, LanguageCoreBase, LanguageFamily, Script


class KannadaCore(LanguageCoreBase):
    """Kannada language core."""

    @property
    def code(self) -> str:
        return "kn"

    @property
    def name(self) -> str:
        return "Kannada"

    @property
    def native_name(self) -> str:
        return "ಕನ್ನಡ"

    @property
    def family(self) -> LanguageFamily:
        return LanguageFamily.DRAVIDIAN

    @property
    def scripts(self) -> list[Script]:
        return [Script.KANNADA]

    @property
    def dialects(self) -> list[DialectInfo]:
        return [
            DialectInfo("Standard Kannada", "ಮಾನಕ ಕನ್ನಡ", "Karnataka", 0.0),
            DialectInfo("North Karnataka", "ಉತ್ತರ ಕರ್ನಾಟಕ", "North Karnataka", 0.05),
            DialectInfo("Coastal Kannada", "ಕರಾವಳಿ ಕನ್ನಡ", "Coastal Karnataka", 0.05),
        ]

    def detect_pattern(self, text: str) -> float:
        if not text:
            return 0.0
        kannada_chars = len(re.findall(r'[\u0C80-\u0CFF]', text))
        if kannada_chars == 0:
            return 0.0
        kannada_tokens = {
            "ನಾನು", "ನೀನು", "ಅವನು", "ಅದು", "ಇದು",
            "ಯಾಕೆ", "ಹೇಗೆ", "ಏನು", "ನೀವು", "ನಾವು",
            "ಮಾಡು", "ಹೇಳು", "ತೋರಿಸು", "ತೆರೆ", "ಮುಚ್ಚು", "ಬರೆಯಿರಿ",
            "ಧನ್ಯವಾದ", "ನಮಸ್ಕಾರ",
        }
        words = set(re.findall(r'[\u0C80-\u0CFF]+', text.lower()))
        hits = len(words & kannada_tokens)
        return min(0.3 + hits * 0.12, 0.9) if hits > 0 else 0.1

    def get_greeting(self) -> str:
        return random.choice(["ನಮಸ್ಕಾರ! ನಾನು ಕರ್ಷ್.", "ನಮಸ್ತೇ! ನಿಮಗೆ ಯಾವ ಸಹಾಯ ಬೇಕು?"])

    def get_farewell(self) -> str:
        return random.choice(["ಮತ್ತೆ ಸಿಗೋಣ!", "ಧನ್ಯವಾದ! ಚೆನ್ನಾಗಿರಿ."])

    def get_error(self) -> str:
        return random.choice(["ಕ್ಷಮಿಸಿ, ಏನೋ ತಪ್ಪಾಗಿದೆ.", "ಕ್ಷಮಿಸಿ, ಇದು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ."])

    def get_thinking(self) -> str:
        return random.choice(["ಯೋಚಿಸುತ್ತಿದ್ದೇನೆ...", "ಪ್ರಕ್ರಿಯೆ ನಡೆಯುತ್ತಿದೆ..."])
