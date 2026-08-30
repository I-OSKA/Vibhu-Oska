"""
Vibhu-Oska AI-OS — RustCore Specialist
Handles Rust specific tasks: ownership, borrowing, async, web, CLI, WASM.
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

log = logging.getLogger("RustCore")


class RustCore(BaseSpecialist):
    """
    Rust specialist for Vibhu-Oska.
    
    Handles:
    - Safe systems programming
    - Ownership and borrowing
    - Async/await with Tokio
    - Web frameworks (Axum, Actix)
    - CLI tools (Clap)
    - WASM compilation
    - FFI interop
    """

    def __init__(self) -> None:
        super().__init__(
            name="RustCore",
            domain=SpecialistDomain.CODING,
            capabilities=SpecialistCapabilities(
                domains=["code_generation", "code_review", "debugging", "performance"],
                subdomains=["rust", "tokio", "axum", "clap", "wasm", "ffi"],
                max_complexity=9,
                estimated_latency_ms=250.0,
                requires_model=False,
                supported_formats=["text", "code"],
            ),
        )
        self._initialized = False

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize RustCore specialist."""
        self._initialized = True
        log.info("RustCore initialized.")

    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process a Rust related task.
        
        Args:
            input_data: Must contain 'prompt' or 'content' with the Rust task
            
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
                "specialist": "RustCore",
                "language": "rust",
                "task_type": self._classify_task(prompt),
            },
        )

    def _generate_response(self, prompt: str) -> str:
        """Generate a response based on the prompt."""
        prompt_lower = prompt.lower()
        
        if "ownership" in prompt_lower or "borrow" in prompt_lower or "lifetime" in prompt_lower:
            return self._ownership_response(prompt)
        elif "async" in prompt_lower or "tokio" in prompt_lower:
            return self._async_response(prompt)
        elif "web" in prompt_lower or "axum" in prompt_lower or "actix" in prompt_lower:
            return self._web_response(prompt)
        elif "wasm" in prompt_lower:
            return self._wasm_response(prompt)
        else:
            return self._general_response(prompt)

    def _ownership_response(self, prompt: str) -> str:
        """Generate ownership/borrowing response."""
        return (
            "Rust Ownership & Borrowing:\n"
            "1. Each value has exactly one owner\n"
            "2. Borrowing: &T for shared, &mut T for exclusive\n"
            "3. Lifetimes ensure references are valid\n"
            "4. Use Clone for explicit duplication\n"
            "5. Move semantics by default (no implicit copy)\n"
            "6. Use Cow<str> for clone-on-write efficiency"
        )

    def _async_response(self, prompt: str) -> str:
        """Generate async response."""
        return (
            "Rust Async/Await:\n"
            "1. Use Tokio as the async runtime\n"
            "2. async fn returns impl Future\n"
            "3. .await suspends until future completes\n"
            "4. Use tokio::spawn for concurrent tasks\n"
            "5. Channels (mpsc) for inter-task communication\n"
            "6. Use async-trait for async in trait objects"
        )

    def _web_response(self, prompt: str) -> str:
        """Generate web framework response."""
        return (
            "Rust Web Development:\n"
            "1. Axum: Tower-based, type-safe routing\n"
            "2. Actix: Actor-based, high performance\n"
            "3. Use extractors for request parsing\n"
            "4. Middleware with Tower services\n"
            "5. Serde for JSON serialization\n"
            "6. SQLx for async database access"
        )

    def _wasm_response(self, prompt: str) -> str:
        """Generate WASM response."""
        return (
            "Rust WASM:\n"
            "1. Use wasm-pack for building\n"
            "2. wasm-bindgen for JS interop\n"
            "3. web-sys for Web API access\n"
            "4. js-sys for JavaScript types\n"
            "5. Use #[wasm_bindgen] for exports\n"
            "6. Optimize with wasm-opt"
        )

    def _general_response(self, prompt: str) -> str:
        """Generate general response."""
        return (
            f"RustCore received your query about Rust.\n"
            f"Query: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n"
            f"For specific help, try including keywords like 'ownership', 'async', 'web', or 'wasm'."
        )

    def _classify_task(self, prompt: str) -> str:
        """Classify the task type."""
        prompt_lower = prompt.lower()
        if "ownership" in prompt_lower or "borrow" in prompt_lower:
            return "ownership"
        elif "async" in prompt_lower or "tokio" in prompt_lower:
            return "async"
        elif "web" in prompt_lower or "axum" in prompt_lower:
            return "web"
        elif "wasm" in prompt_lower:
            return "wasm"
        else:
            return "general"
