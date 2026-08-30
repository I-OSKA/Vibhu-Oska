"""
Vibhu-Oska AI-OS — LanguageCore Package
Umbrella language processing hub with per-language cores.
"""

from .LanguageCore import LanguageCore, LanguageDetection
from .BaseLanguage import LanguageCoreBase, LanguageFamily, Script

__all__ = [
    "LanguageCore",
    "LanguageDetection",
    "LanguageCoreBase",
    "LanguageFamily",
    "Script",
]
