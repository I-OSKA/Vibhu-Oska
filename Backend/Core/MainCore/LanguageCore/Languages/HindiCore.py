"""
Vibhu-Oska AI-OS — HindiCore
Hindi language support with dialect awareness (Bhojpuri, Rajasthani, Marwari, etc.)

Hindi is Vibhu-Oska's primary identity language — Karsh responds in Hindi by default
when the user speaks Hindi.
"""

from __future__ import annotations

import random
import re
from ..BaseLanguage import DialectInfo, LanguageCoreBase, LanguageFamily, Script


class HindiCore(LanguageCoreBase):
    """
    Hindi language core — supports Hindi, Hinglish (Romanized Hindi), and related dialects.

    Handles:
    - Devanagari script detection
    - Romanized Hindi (Hinglish) detection
    - Dialect variants (Bhojpuri, Rajasthani, etc.)
    - Hindi-specific greetings, errors, thinking messages
    """

    @property
    def code(self) -> str:
        return "hi"

    @property
    def name(self) -> str:
        return "Hindi"

    @property
    def native_name(self) -> str:
        return "हिन्दी"

    @property
    def family(self) -> LanguageFamily:
        return LanguageFamily.INDO_ARYAN

    @property
    def scripts(self) -> list[Script]:
        return [Script.DEVANAGARI, Script.LATIN]  # Latin for Hinglish

    @property
    def dialects(self) -> list[DialectInfo]:
        return [
            DialectInfo("Standard Hindi", "मानक हिन्दी", "Delhi/UP", 0.0),
            DialectInfo("Bhojpuri", "भोजपुरी", "Bihar/UP", 0.05),
            DialectInfo("Rajasthani", "राजस्थानी", "Rajasthan", 0.05),
            DialectInfo("Marwari", "मारवाड़ी", "Marwar", 0.05),
            DialectInfo("Awadhi", "अवधी", "Awadh", 0.05),
            DialectInfo("Bundeli", "बुंदेली", "Bundelkhand", 0.05),
            DialectInfo("Braj", "ब्रज", "Braj region", 0.05),
            DialectInfo("Magahi", "मगही", "Magadh", 0.05),
        ]

    def detect_pattern(self, text: str) -> float:
        """
        Detect if text is Hindi (Devanagari or Romanized/Hinglish).

        Scoring:
        - Pure Devanagari script → high confidence
        - Romanized Hindi words → medium confidence
        - Mixed script → medium confidence
        """
        if not text or not text.strip():
            return 0.0

        normalized = text.lower().strip()
        words = set(re.findall(r'[a-z\u0900-\u097F]+', normalized))

        # Check for Devanagari script
        devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
        total_chars = len(text.replace(" ", ""))

        if total_chars > 0 and devanagari_chars / max(total_chars, 1) > 0.3:
            return 0.95  # Almost certainly Hindi

        # Check for Romanized Hindi words
        hindi_tokens = {
            "kya", "hai", "hain", "ho", "hum", "tum", "aap", "mein", "main",
            "yeh", "woh", "us", "un", "ka", "ke", "ki", "ko", "se", "par",
            "ne", "ya", "aur", "bhi", "ab", "phir", "kab", "kahan", "kyun",
            "kaise", "kaun", "nahi", "haan", "theek", "accha", "bura",
            "karo", "karna", "karta", "karti", "hoon", "raha", "rahi",
            "gaya", "gai", "de", "do", "le", "lo", "ja", "aa", "bol",
            "sun", "dekh", "likh", "padh", "samjho", "batao", "puchho",
            "jawaab", "sawaal", "prashn", "dhan", "paisa", "rupe",
            "namaste", "namaskar", "pranam", "ji", "sahib",
            "khana", "peena", "so", "uth", "baith", "chal", "ruk",
        }

        hits = len(words & hindi_tokens)
        total_words = max(len(words), 1)
        confidence = min(hits / max(total_words * 0.4, 1), 0.9)

        return confidence

    def get_greeting(self) -> str:
        greetings = [
            "नमस्ते! मैं कर्ष हूँ।",
            "नमस्कार! आपकी क्या सेवा करूँ?",
            "प्रणाम! बताइए, क्या मदद चाहिए?",
            "अभिवादन! मैं आपकी सहायता के लिए हूँ।",
            "नमस्ते जी! बोलिए।",
        ]
        return random.choice(greetings)

    def get_farewell(self) -> str:
        farewells = [
            "अलविदा! फिर मिलते हैं।",
            "धन्यवाद! शुभ दिन।",
            "नमस्ते! अच्छा रहे।",
            "फिर आइएगा!",
        ]
        return random.choice(farewells)

    def get_error(self) -> str:
        errors = [
            "क्षमा करें, कुछ गड़बड़ हो गई।",
            "माफ़ कीजिए, यह काम नहीं हो पाया।",
            "क्षमा कीजिए, अभी यह संभव नहीं है।",
        ]
        return random.choice(errors)

    def get_thinking(self) -> str:
        thinking = [
            "सोच रहा हूँ...",
            "विचार कर रहा हूँ...",
            "प्रसंस्करण हो रहा है...",
        ]
        return random.choice(thinking)
