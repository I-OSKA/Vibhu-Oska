"""
Vibhu-Oska AI-OS — EnglishCore
English language support with dialect awareness (American, British, Australian, etc.)
"""

from __future__ import annotations

import random
import re
from ..BaseLanguage import DialectInfo, LanguageCoreBase, LanguageFamily, Script


class EnglishCore(LanguageCoreBase):
    """
    English language core — supports Standard English and dialect variants.

    Handles:
    - Latin script detection
    - English word patterns
    - Dialect variants (American, British, Australian, etc.)
    """

    @property
    def code(self) -> str:
        return "en"

    @property
    def name(self) -> str:
        return "English"

    @property
    def native_name(self) -> str:
        return "English"

    @property
    def family(self) -> LanguageFamily:
        return LanguageFamily.GERMANIC

    @property
    def scripts(self) -> list[Script]:
        return [Script.LATIN]

    @property
    def dialects(self) -> list[DialectInfo]:
        return [
            DialectInfo("American English", "American", "USA", 0.0),
            DialectInfo("British English", "British", "UK", 0.0),
            DialectInfo("Australian English", "Australian", "Australia", 0.0),
            DialectInfo("Indian English", "Indian", "India", 0.05),
            DialectInfo("Canadian English", "Canadian", "Canada", 0.0),
        ]

    def detect_pattern(self, text: str) -> float:
        """
        Detect if text is English.

        Uses common English word frequency analysis.
        """
        if not text or not text.strip():
            return 0.0

        normalized = text.lower().strip()
        words = set(re.findall(r'[a-z]+', normalized))

        english_words = {
            "what", "how", "when", "where", "why", "who", "which", "can",
            "could", "would", "should", "will", "do", "does", "is", "are",
            "was", "were", "have", "has", "had", "the", "a", "an", "this",
            "that", "my", "your", "his", "her", "its", "our", "their",
            "hello", "hi", "hey", "thanks", "please", "sorry", "yes", "no",
            "good", "bad", "great", "help", "show", "tell", "give", "make",
            "create", "write", "read", "open", "close", "start", "stop",
            "file", "folder", "code", "program", "system", "data",
        }

        hits = len(words & english_words)
        total_words = max(len(words), 1)
        confidence = min(hits / max(total_words * 0.3, 1), 0.95)

        return confidence

    def get_greeting(self) -> str:
        greetings = [
            "Hello! I'm Karsh.",
            "Hi there! How can I help you?",
            "Greetings! What can I do for you?",
            "Hey! Ready to assist.",
            "Welcome! What would you like to know?",
        ]
        return random.choice(greetings)

    def get_farewell(self) -> str:
        farewells = [
            "Goodbye! See you next time.",
            "Thank you! Have a great day.",
            "Take care! Feel free to return anytime.",
            "Bye! Let me know if you need anything else.",
        ]
        return random.choice(farewells)

    def get_error(self) -> str:
        errors = [
            "Sorry, something went wrong.",
            "Apologies, I couldn't process that.",
            "An error occurred. Please try again.",
        ]
        return random.choice(errors)

    def get_thinking(self) -> str:
        thinking = [
            "Thinking...",
            "Let me process that...",
            "Analyzing...",
        ]
        return random.choice(thinking)
