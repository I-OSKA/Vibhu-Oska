"""
Vibhu-Oska AI-OS — JavaScriptCore Specialist
Handles JavaScript/TypeScript specific tasks: ES2024, Node.js, React, Vue, Svelte.
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

log = logging.getLogger("JavaScriptCore")


class JavaScriptCore(BaseSpecialist):
    """
    JavaScript/TypeScript specialist for Vibhu-Oska.
    
    Handles:
    - ES2024+ JavaScript
    - TypeScript types and generics
    - Node.js runtime
    - React, Vue, Svelte frameworks
    - Bundlers (Vite, Webpack)
    - Testing (Jest, Vitest)
    """

    def __init__(self) -> None:
        super().__init__(
            name="JavaScriptCore",
            domain=SpecialistDomain.CODING,
            capabilities=SpecialistCapabilities(
                domains=["code_generation", "code_review", "debugging", "refactoring"],
                subdomains=["javascript", "typescript", "react", "vue", "svelte", "node"],
                max_complexity=8,
                estimated_latency_ms=200.0,
                requires_model=False,
                supported_formats=["text", "code"],
            ),
        )
        self._initialized = False

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize JavaScriptCore specialist."""
        self._initialized = True
        log.info("JavaScriptCore initialized.")

    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process a JavaScript/TypeScript related task.
        
        Args:
            input_data: Must contain 'prompt' or 'content' with the task
            
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
                "specialist": "JavaScriptCore",
                "language": "javascript",
                "task_type": self._classify_task(prompt),
            },
        )

    def _generate_response(self, prompt: str) -> str:
        """Generate a response based on the prompt."""
        prompt_lower = prompt.lower()
        
        if "typescript" in prompt_lower or "type" in prompt_lower:
            return self._typescript_response(prompt)
        elif "react" in prompt_lower:
            return self._react_response(prompt)
        elif "node" in prompt_lower or "server" in prompt_lower:
            return self._node_response(prompt)
        elif "async" in prompt_lower or "promise" in prompt_lower:
            return self._async_response(prompt)
        else:
            return self._general_response(prompt)

    def _typescript_response(self, prompt: str) -> str:
        """Generate TypeScript response."""
        return (
            "TypeScript Best Practices:\n"
            "1. Use strict mode in tsconfig.json\n"
            "2. Prefer interfaces over type aliases for objects\n"
            "3. Use utility types: Partial, Required, Pick, Omit\n"
            "4. Leverage type inference where possible\n"
            "5. Use branded types for nominal typing\n"
            "6. Implement discriminated unions for state management"
        )

    def _react_response(self, prompt: str) -> str:
        """Generate React response."""
        return (
            "React Best Practices:\n"
            "1. Use functional components with hooks\n"
            "2. Memoize expensive computations with useMemo\n"
            "3. Use useCallback for stable callback references\n"
            "4. Implement proper key props in lists\n"
            "5. Use React Query for server state\n"
            "6. Implement error boundaries"
        )

    def _node_response(self, prompt: str) -> str:
        """Generate Node.js response."""
        return (
            "Node.js Best Practices:\n"
            "1. Use async/await over callbacks\n"
            "2. Implement proper error handling\n"
            "3. Use environment variables for config\n"
            "4. Implement rate limiting\n"
            "5. Use connection pooling for databases\n"
            "6. Implement proper logging"
        )

    def _async_response(self, prompt: str) -> str:
        """Generate async response."""
        return (
            "JavaScript Async Patterns:\n"
            "1. Use async/await over .then() chains\n"
            "2. Implement proper error handling with try/catch\n"
            "3. Use Promise.all() for parallel execution\n"
            "4. Use Promise.allSettled() for fault tolerance\n"
            "5. Implement proper timeout handling\n"
            "6. Use AbortController for cancellable requests"
        )

    def _general_response(self, prompt: str) -> str:
        """Generate general response."""
        return (
            f"JavaScriptCore received your query about JavaScript/TypeScript.\n"
            f"Query: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n"
            f"For specific help, try including keywords like 'typescript', 'react', 'node', or 'async'."
        )

    def _classify_task(self, prompt: str) -> str:
        """Classify the task type."""
        prompt_lower = prompt.lower()
        if "typescript" in prompt_lower or "type" in prompt_lower:
            return "typescript"
        elif "react" in prompt_lower:
            return "react"
        elif "node" in prompt_lower or "server" in prompt_lower:
            return "node"
        elif "async" in prompt_lower or "promise" in prompt_lower:
            return "async"
        else:
            return "general"
