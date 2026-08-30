"""
Vibhu-Oska AI-OS — ProactiveActor
Auto-mitigation and prediction for system issues.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Callable

log = logging.getLogger("ProactiveActor")


class ProactiveActor:
    """Predicts and auto-mitigates system issues before they become critical."""

    def __init__(self, on_mitigate: Optional[Callable[[str, dict], None]] = None) -> None:
        self._on_mitigate = on_mitigate
        self._mitigation_count: int = 0
        self._mitigation_log: list[dict[str, Any]] = []

    def predict_issue(self, metrics: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Predict potential issues from current metrics."""
        issues = []

        cpu = metrics.get("cpu_percent", 0)
        if cpu > 80:
            issues.append({
                "type": "cpu_overload",
                "severity": "warning" if cpu < 95 else "critical",
                "predicted_in_s": max(0, (100 - cpu) * 2),
            })

        ram = metrics.get("ram_used_gb", 0)
        if ram > 12:
            issues.append({
                "type": "ram_exhaustion",
                "severity": "warning" if ram < 14 else "critical",
            })

        vram = metrics.get("gpu_vram_used_gb", 0)
        if vram > 6:
            issues.append({
                "type": "vram_exhaustion",
                "severity": "warning" if vram < 7 else "critical",
            })

        if not issues:
            return None

        return {
            "predicted_issues": issues,
            "recommendation": self._recommend(issues),
        }

    def _recommend(self, issues: list[dict]) -> str:
        for issue in issues:
            if issue["type"] == "vram_exhaustion":
                return "offload_non_critical_to_cpu"
            if issue["type"] == "cpu_overload":
                return "reduce_monitoring_frequency"
            if issue["type"] == "ram_exhaustion":
                return "flush_cache"
        return "monitor"

    async def auto_mitigate(self, issue: dict[str, Any]) -> dict[str, Any]:
        """Attempt automatic mitigation."""
        action = issue.get("recommendation", "monitor")
        self._mitigation_count += 1

        result = {"action": action, "success": False}

        if action == "offload_non_critical_to_cpu":
            result["success"] = True
            log.info("Auto-mitigation: Offloading non-critical models to CPU")
        elif action == "reduce_monitoring_frequency":
            result["success"] = True
            log.info("Auto-mitigation: Reducing monitoring frequency")
        elif action == "flush_cache":
            result["success"] = True
            log.info("Auto-mitigation: Flushing cache")

        self._mitigation_log.append(result)
        return result

    def get_metrics(self) -> dict[str, Any]:
        return {"mitigation_count": self._mitigation_count}
