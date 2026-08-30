"""
Vibhu-Oska AI-OS — BaseSpecialist Abstract Interface
All specialists must inherit from this base class for consistent routing and execution.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class SpecialistDomain(str, Enum):
    """Domain classification for specialists."""
    CODING = "coding"
    REAL_WORLD = "real_world"


@dataclass
class SpecialistCapabilities:
    """Describes what a specialist can do."""
    domains: list[str]                              # e.g., ["code_review", "bug_detection"]
    subdomains: list[str]                           # e.g., ["python", "javascript"]
    max_complexity: int = 10                        # 1-10 scale
    estimated_latency_ms: float = 500.0             # typical response time
    requires_model: bool = True                     # needs ML inference
    supported_formats: list[str] = field(default_factory=lambda: ["text"])


@dataclass
class SpecialistResult:
    """Result from a specialist execution."""
    success: bool
    output: str
    confidence: float                               # 0.0 - 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class BaseSpecialist(ABC):
    """
    Abstract base class for all Vibhu-Oska specialists.

    Provides:
    - Capability registration for routing
    - Input validation before processing
    - Standard result format
    - Performance tracking
    """

    def __init__(
        self,
        name: str,
        domain: SpecialistDomain,
        capabilities: SpecialistCapabilities,
    ) -> None:
        self._name = name
        self._domain = domain
        self._capabilities = capabilities
        self._total_requests: int = 0
        self._successful_requests: int = 0
        self._total_latency_ms: float = 0.0
        self._initialized: bool = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def domain(self) -> SpecialistDomain:
        return self._domain

    @property
    def capabilities(self) -> SpecialistCapabilities:
        return self._capabilities

    @property
    def avg_latency_ms(self) -> float:
        if self._total_requests == 0:
            return 0.0
        return self._total_latency_ms / self._total_requests

    @property
    def success_rate(self) -> float:
        if self._total_requests == 0:
            return 0.0
        return self._successful_requests / self._total_requests

    def can_handle(self, domain: str, subdomain: str = "") -> bool:
        """Check if this specialist can handle a given task."""
        if domain not in self._capabilities.domains:
            return False
        if subdomain and subdomain not in self._capabilities.subdomains:
            return False
        return True

    def validate_input(self, input_data: dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input before processing.
        Returns (is_valid, error_message).
        Override in subclasses for custom validation.
        """
        if "prompt" not in input_data and "content" not in input_data:
            return False, "Input must contain 'prompt' or 'content' key"
        return True, None

    @abstractmethod
    async def initialize(self, **kwargs: Any) -> None:
        """Initialize the specialist. Must be called before process()."""
        ...

    @abstractmethod
    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process an input and return a result.
        Must be implemented by all specialists.
        """
        ...

    async def process_with_tracking(self, input_data: dict[str, Any]) -> SpecialistResult:
        """Process with automatic performance tracking."""
        import time

        self._total_requests += 1
        start = time.time()

        try:
            result = await self.process(input_data)
            elapsed_ms = (time.time() - start) * 1000
            self._total_latency_ms += elapsed_ms

            if result.success:
                self._successful_requests += 1

            result.metadata["latency_ms"] = elapsed_ms
            result.metadata["specialist"] = self._name
            return result

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            self._total_latency_ms += elapsed_ms
            return SpecialistResult(
                success=False,
                output="",
                confidence=0.0,
                error=str(e),
                metadata={"latency_ms": elapsed_ms, "specialist": self._name},
            )

    async def get_metrics(self) -> dict[str, Any]:
        """Return performance metrics for monitoring."""
        return {
            "name": self._name,
            "domain": self._domain.value,
            "total_requests": self._total_requests,
            "successful_requests": self._successful_requests,
            "success_rate": self.success_rate,
            "avg_latency_ms": self.avg_latency_ms,
            "initialized": self._initialized,
        }

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} name={self._name} "
            f"domain={self._domain.value} success_rate={self.success_rate:.2f}>"
        )
