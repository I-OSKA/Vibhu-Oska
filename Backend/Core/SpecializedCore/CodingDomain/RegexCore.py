"""
Vibhu-Oska AI-OS — RegexCore Specialist
Handles Regular Expression tasks: PCRE, RE2, capture groups, lookaheads, performance.
"""

from __future__ import annotations

import logging
from typing import Any

from Shared.interfaces.BaseSpecialist import (
    BaseSpecialist,
    SpecialistDomain,
    SpecialistCapabilities,
    SpecialistResult,
)

log = logging.getLogger("RegexCore")


class RegexCore(BaseSpecialist):
    """
    Regular Expression specialist for Vibhu-Oska.
    
    Handles:
    - Pattern writing and optimization
    - Capture groups and backreferences
    - Lookaheads and lookbehinds
    - Performance tuning
    - Cross-flavor compatibility (PCRE, RE2, JavaScript)
    """

    def __init__(self) -> None:
        super().__init__(
            name="RegexCore",
            domain=SpecialistDomain.CODING,
            capabilities=SpecialistCapabilities(
                domains=["code_generation", "code_review", "debugging", "optimization"],
                subdomains=["regex", "pcre", "re2", "pattern"],
                max_complexity=7,
                estimated_latency_ms=100.0,
                requires_model=False,
                supported_formats=["text", "code"],
            ),
        )
        self._initialized = False

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize RegexCore specialist."""
        self._initialized = True
        log.info("RegexCore initialized.")

    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process a Regex related task.
        
        Args:
            input_data: Must contain 'prompt' or 'content' with the regex task
            
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

        response = self._generate_response(prompt)
        
        return SpecialistResult(
            success=True,
            output=response,
            confidence=0.8,
            metadata={
                "specialist": "RegexCore",
                "language": "regex",
                "task_type": self._classify_task(prompt),
            },
        )

    def _generate_response(self, prompt: str) -> str:
        """Generate a response based on the prompt."""
        prompt_lower = prompt.lower()
        
        if "email" in prompt_lower or "url" in prompt_lower or "phone" in prompt_lower:
            return self._common_patterns_response(prompt)
        elif "capture" in prompt_lower or "group" in prompt_lower:
            return self._capture_groups_response(prompt)
        elif "lookahead" in prompt_lower or "lookbehind" in prompt_lower:
            return self._lookaround_response(prompt)
        elif "performance" in prompt_lower or "slow" in prompt_lower or "optimize" in prompt_lower:
            return self._optimization_response(prompt)
        else:
            return self._general_response(prompt)

    def _common_patterns_response(self, prompt: str) -> str:
        """Generate common patterns response."""
        return (
            "Common Regex Patterns:\n"
            "Email: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$\n"
            "URL: ^https?://[^\\s/$.?#].[^\\s]*$\n"
            "Phone (US): ^\\(?\\d{3}\\)?[-.\\s]?\\d{3}[-.\\s]?\\d{4}$\n"
            "IP Address: ^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$\n"
            "Date (YYYY-MM-DD): ^\\d{4}-\\d{2}-\\d{2}$\n"
            "Hex Color: ^#?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$"
        )

    def _capture_groups_response(self, prompt: str) -> str:
        """Generate capture groups response."""
        return (
            "Regex Capture Groups:\n"
            "1. (pattern) - capturing group\n"
            "2. (?:pattern) - non-capturing group\n"
            "3. (?<name>pattern) - named capturing group\n"
            "4. \\1, \\2 - backreferences\n"
            "5. Group 0 = entire match\n"
            "6. Use groups for extraction and validation"
        )

    def _lookaround_response(self, prompt: str) -> str:
        """Generate lookaround response."""
        return (
            "Regex Lookaround:\n"
            "1. (?=pattern) - positive lookahead\n"
            "2. (?!pattern) - negative lookahead\n"
            "3. (?<=pattern) - positive lookbehind\n"
            "4. (?<!pattern) - negative lookbehind\n"
            "5. Lookaround doesn't consume characters\n"
            "6. Use for context-aware matching"
        )

    def _optimization_response(self, prompt: str) -> str:
        """Generate optimization response."""
        return (
            "Regex Performance:\n"
            "1. Avoid catastrophic backtracking\n"
            "2. Use non-capturing groups when possible\n"
            "3. Anchor patterns with ^ and $\n"
            "4. Use specific character classes over .\n"
            "5. Prefer possessive quantifiers or atomic groups\n"
            "6. Test with tools like regex101.com"
        )

    def _general_response(self, prompt: str) -> str:
        """Generate general response."""
        return (
            f"RegexCore received your query about Regular Expressions.\n"
            f"Query: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n"
            f"For specific help, try including keywords like 'email', 'capture', 'lookahead', or 'performance'."
        )

    def _classify_task(self, prompt: str) -> str:
        """Classify the task type."""
        prompt_lower = prompt.lower()
        if "email" in prompt_lower or "url" in prompt_lower or "phone" in prompt_lower:
            return "common_patterns"
        elif "capture" in prompt_lower or "group" in prompt_lower:
            return "capture_groups"
        elif "lookahead" in prompt_lower or "lookbehind" in prompt_lower:
            return "lookaround"
        elif "performance" in prompt_lower or "optimize" in prompt_lower:
            return "optimization"
        else:
            return "general"
