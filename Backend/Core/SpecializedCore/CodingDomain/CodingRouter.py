"""
Vibhu-Oska AI-OS — CodingRouter Specialist
Routes coding tasks to the appropriate language specialist.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

from Shared.interfaces.BaseSpecialist import (
    BaseSpecialist,
    SpecialistDomain,
    SpecialistCapabilities,
    SpecialistResult,
)

log = logging.getLogger("CodingRouter")


class CodingRouter(BaseSpecialist):
    """
    Coding domain router for Vibhu-Oska.
    
    Detects the programming language and routes to the appropriate specialist.
    Falls back to general coding assistance if no specific specialist is available.
    """

    def __init__(self) -> None:
        super().__init__(
            name="CodingRouter",
            domain=SpecialistDomain.CODING,
            capabilities=SpecialistCapabilities(
                domains=["code_generation", "code_review", "debugging", "refactoring", "testing"],
                subdomains=["python", "cpp", "rust", "javascript", "go", "sql", "bash", "regex"],
                max_complexity=5,
                estimated_latency_ms=50.0,
                requires_model=False,
                supported_formats=["text", "code"],
            ),
        )
        self._specialists: dict[str, BaseSpecialist] = {}
        self._initialized = False

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize CodingRouter specialist."""
        self._initialized = True
        log.info("CodingRouter initialized.")

    def register_specialist(self, language: str, specialist: BaseSpecialist) -> None:
        """Register a language specialist."""
        self._specialists[language.lower()] = specialist
        log.info(f"Registered coding specialist: {language} -> {specialist.name}")

    def detect_language(self, prompt: str) -> Optional[str]:
        """Detect the programming language from the prompt."""
        prompt_lower = prompt.lower()
        
        # Language detection patterns
        patterns = {
            "python": [r"\bpython\b", r"\bdef\b.*\(", r"\bimport\b.*\bfrom\b", r"\basync\b.*\bdef\b"],
            "cpp": [r"\bcpp\b", r"\bc\+\+", r"\bstd::", r"\btemplate\b.*<", r"\bcout\b", r"\bC\+\+"],
            "rust": [r"\brust\b", r"\bfn\b.*\(", r"\blet\b.*\bmut\b", r"\bimpl\b", r"\btrait\b"],
            "javascript": [r"\bjavascript\b", r"\bjs\b", r"\btypescript\b", r"\bts\b", r"\bconst\b.*=", r"\blet\b.*="],
            "go": [r"\bgolang\b", r"\bgoroutine", r"\bchan\b", r"\binterface\b.*\{", r"\bfunc\b.*\("],
            "sql": [r"\bsql\b", r"\bselect\b.*\bfrom\b", r"\binsert\b.*\binto\b", r"\bupdate\b.*\bset\b"],
            "bash": [r"\bbash\b", r"\bshell\b", r"\bawk\b", r"\bsed\b", r"\bgrep\b", r"\bsystemd\b"],
            "regex": [r"\bregex\b", r"\bpattern\b", r"\bmatch\b", r"\bcapture\b", r"\blookahead\b"],
        }
        
        for language, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, prompt_lower):
                    return language
        
        return None

    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process a coding task by routing to the appropriate specialist.
        
        Args:
            input_data: Must contain 'prompt' or 'content' with the coding task
            
        Returns:
            SpecialistResult with the response
        """
        prompt = input_data.get("prompt") or input_data.get("content", "")
        
        if not prompt:
            return SpecialistResult(
                success=False,
                output="",
                confidence=0.0,
                error="No prompt provided",
            )

        # Detect language
        language = self.detect_language(prompt)
        
        if language and language in self._specialists:
            specialist = self._specialists[language]
            log.info(f"Routing to {language} specialist: {specialist.name}")
            return await specialist.process_with_tracking(input_data)
        
        # Fallback to general coding response
        return self._general_coding_response(prompt)

    def _general_coding_response(self, prompt: str) -> SpecialistResult:
        """Generate a general coding response."""
        response = (
            "CodingRouter: I can help with programming tasks.\n"
            "Detected query about general coding.\n\n"
            "Supported languages:\n"
            "- Python, C++, Rust, JavaScript/TypeScript\n"
            "- Go, SQL, Shell/Bash, Regular Expressions\n\n"
            "Please specify the language for more targeted assistance."
        )
        
        return SpecialistResult(
            success=True,
            output=response,
            confidence=0.5,
            metadata={
                "specialist": "CodingRouter",
                "detected_language": None,
                "routing": "general",
            },
        )

    def get_registered_languages(self) -> list[str]:
        """Get list of registered languages."""
        return list(self._specialists.keys())
