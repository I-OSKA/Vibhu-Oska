"""
Vibhu-Oska AI-OS — AlertSystem
Notification hierarchy for system alerts.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Callable

log = logging.getLogger("AlertSystem")


class AlertLevel:
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertSystem:
    """
    Notification hierarchy:
    1. Log warning (always)
    2. Notify OptimizationCore (if resource issue)
    3. Notify OrchestratorCore (if emotional issue)
    4. Notify Orchestrator (if action needed)
    5. Notify ParaCore (if critical)
    """

    def __init__(self) -> None:
        self._handlers: dict[str, Callable] = {}
        self._alert_count: int = 0
        self._alert_log: list[dict[str, Any]] = []

    def register_handler(self, level: str, handler: Callable) -> None:
        """Register a handler for an alert level."""
        self._handlers[level] = handler

    def alert(
        self,
        level: str,
        message: str,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Send an alert."""
        self._alert_count += 1

        alert = {
            "level": level,
            "message": message,
            "context": context or {},
            "alert_id": self._alert_count,
        }

        self._alert_log.append(alert)

        log_method = {
            AlertLevel.INFO: log.info,
            AlertLevel.WARNING: log.warning,
            AlertLevel.ERROR: log.error,
            AlertLevel.CRITICAL: log.critical,
        }.get(level, log.info)

        log_method(f"[{level.upper()}] {message}")

        # Notify handler if registered
        if level in self._handlers:
            try:
                self._handlers[level](alert)
            except Exception as e:
                log.error(f"Alert handler failed: {e}")

        return alert

    def get_metrics(self) -> dict[str, Any]:
        return {"alert_count": self._alert_count}
