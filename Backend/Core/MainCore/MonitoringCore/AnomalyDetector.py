"""
Vibhu-Oska AI-OS — AnomalyDetector
Pattern recognition and trend analysis for system metrics.
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger("AnomalyDetector")


class AnomalyDetector:
    """Detects anomalies in system metrics using trend analysis."""

    def __init__(self, window_size: int = 10) -> None:
        self._window_size = window_size
        self._history: dict[str, list[float]] = {}
        self._anomaly_count: int = 0

    def add_datapoint(self, metric: str, value: float) -> None:
        """Add a datapoint to the history."""
        if metric not in self._history:
            self._history[metric] = []
        self._history[metric].append(value)
        if len(self._history[metric]) > self._window_size * 3:
            self._history[metric] = self._history[metric][-self._window_size * 3:]

    def detect(self, metric: str, current_value: float) -> dict[str, Any]:
        """Detect if current value is anomalous."""
        history = self._history.get(metric, [])
        if len(history) < self._window_size:
            return {"anomaly": False, "reason": "insufficient_data"}

        recent = history[-self._window_size:]
        mean = sum(recent) / len(recent)
        std = (sum((x - mean) ** 2 for x in recent) / len(recent)) ** 0.5 + 1e-8

        z_score = (current_value - mean) / std

        if abs(z_score) > 3.0:
            self._anomaly_count += 1
            return {
                "anomaly": True,
                "z_score": z_score,
                "mean": mean,
                "std": std,
                "severity": "critical" if abs(z_score) > 5 else "warning",
            }

        return {"anomaly": False, "z_score": z_score}

    def get_metrics(self) -> dict[str, Any]:
        return {"anomaly_count": self._anomaly_count}
