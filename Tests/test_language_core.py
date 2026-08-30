"""Tests for LanguageCore module — 12-language umbrella with detection, greetings, and farewells."""

import pytest

from Backend.Core.MainCore.LanguageCore.LanguageCore import LanguageCore
from Backend.Core.MainCore.LanguageCore.BaseLanguage import Script, LanguageFamily


class TestLanguageCore:
    @pytest.fixture
    def core(self):
        return LanguageCore.get_instance()

    def test_singleton(self):
        a = LanguageCore.get_instance()
        b = LanguageCore.get_instance()
        assert a is b

    def test_detect_english(self, core):
        result = core.detect("Hello, how are you doing today?")
        assert result.language_code == "en"

    def test_detect_hindi(self, core):
        result = core.detect("नमस्ते, आप कैसे हैं?")
        assert result.language_code == "hi"

    def test_get_greeting_english(self, core):
        greeting = core.get_greeting("en")
        assert isinstance(greeting, str)
        assert len(greeting) > 0

    def test_get_greeting_hindi(self, core):
        greeting = core.get_greeting("hi")
        assert isinstance(greeting, str)
        assert len(greeting) > 0

    def test_get_farewell_english(self, core):
        farewell = core.get_farewell("en")
        assert isinstance(farewell, str)
        assert len(farewell) > 0

    def test_list_languages(self, core):
        langs = core.list_languages()
        assert isinstance(langs, list)
        codes = [l["code"] for l in langs]
        assert "en" in codes
        assert "hi" in codes

    def test_get_language(self, core):
        lang = core.get_language("en")
        assert lang is not None
