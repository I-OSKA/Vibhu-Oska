"""
Vibhu-Oska AI-OS — BaseCore Abstract Interface
All cores must inherit from this base class for consistent lifecycle management.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional


class CoreState(str, Enum):
    """Lifecycle states for all cores."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    DEGRADED = "degraded"
    ERROR = "error"
    STOPPING = "stopping"
    STOPPED = "stopped"


class BaseCore(ABC):
    """
    Abstract base class for all Vibhu-Oska cores.

    Provides:
    - Standard lifecycle: init → start → stop → health_check
    - State management with state transitions
    - Error tracking and recovery hooks
    - VRAM budget awareness
    """

    def __init__(self, name: str, vram_budget_gb: float = 0.0) -> None:
        self._name = name
        self._state = CoreState.IDLE
        self._vram_budget_gb = vram_budget_gb
        self._vram_used_gb: float = 0.0
        self._error_count: int = 0
        self._last_error: Optional[str] = None
        self._initialized: bool = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> CoreState:
        return self._state

    @property
    def vram_budget_gb(self) -> float:
        return self._vram_budget_gb

    @property
    def vram_used_gb(self) -> float:
        return self._vram_used_gb

    @property
    def is_healthy(self) -> bool:
        return self._state in (CoreState.IDLE, CoreState.RUNNING)

    @property
    def error_count(self) -> int:
        return self._error_count

    def _set_state(self, new_state: CoreState) -> None:
        """Transition to a new state. Override for custom behavior."""
        old_state = self._state
        self._state = new_state
        self._on_state_change(old_state, new_state)

    def _on_state_change(self, old: CoreState, new: CoreState) -> None:
        """Hook for state change notifications. Override in subclasses."""
        pass

    def _record_error(self, error: str) -> None:
        """Record an error for tracking and recovery."""
        self._error_count += 1
        self._last_error = error

    @abstractmethod
    async def initialize(self, **kwargs: Any) -> None:
        """Initialize the core. Must be called before start()."""
        ...

    @abstractmethod
    async def start(self) -> None:
        """Start the core. Sets state to RUNNING."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Stop the core gracefully. Sets state to STOPPED."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if core is healthy, False otherwise."""
        ...

    async def get_metrics(self) -> dict[str, Any]:
        """Return current metrics for monitoring. Override for custom metrics."""
        return {
            "name": self._name,
            "state": self._state.value,
            "vram_budget_gb": self._vram_budget_gb,
            "vram_used_gb": self._vram_used_gb,
            "error_count": self._error_count,
            "last_error": self._last_error,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self._name} state={self._state.value}>"
