"""
Vibhu-Oska AI-OS — ResultSummator
Merges results from multiple specialists.
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger("ResultSummator")


class ResultSummator:
    """
    Collects and merges results from multiple specialists.

    Features:
    - Conflict resolution (priority-based)
    - Complementary result merging
    - Contradiction detection
    - Confidence scoring
    """

    def __init__(self) -> None:
        self._summation_count: int = 0

    def summarize(
        self,
        results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Merge multiple specialist results into one.

        Returns:
            {
                "output": str,
                "confidence": float,
                "source_count": int,
                "conflicts": list,
            }
        """
        self._summation_count += 1

        if not results:
            return {
                "output": "",
                "confidence": 0.0,
                "source_count": 0,
                "conflicts": [],
            }

        if len(results) == 1:
            r = results[0]
            return {
                "output": r.get("output", ""),
                "confidence": r.get("confidence", 0.5),
                "source_count": 1,
                "conflicts": [],
            }

        # Multiple results — merge
        outputs = []
        conflicts = []
        confidences = []

        for r in results:
            output = r.get("output", "")
            confidence = r.get("confidence", 0.5)
            outputs.append(output)
            confidences.append(confidence)

        # Check for contradictions
        if self._has_contradictions(outputs):
            conflicts.append({
                "type": "contradiction",
                "outputs": outputs,
            })

        # Merge outputs (weighted by confidence)
        merged_output = self._merge_outputs(outputs, confidences)

        # Average confidence (penalize if conflicts)
        avg_confidence = sum(confidences) / len(confidences)
        if conflicts:
            avg_confidence *= 0.7  # penalty for conflicts

        return {
            "output": merged_output,
            "confidence": avg_confidence,
            "source_count": len(results),
            "conflicts": conflicts,
        }

    def _has_contradictions(self, outputs: list[str]) -> bool:
        """Check if outputs contradict each other."""
        # Simplified: check for explicit negations
        negations = [" is not ", " is false ", " no ", " incorrect "]
        affirmations = [" is true ", " is correct ", " yes "]

        has_neg = any(any(n in o.lower() for n in negations) for o in outputs)
        has_aff = any(any(a in o.lower() for a in affirmations) for o in outputs)

        return has_neg and has_aff

    def _merge_outputs(
        self,
        outputs: list[str],
        confidences: list[float],
    ) -> str:
        """Merge outputs weighted by confidence."""
        if not outputs:
            return ""

        # Find highest confidence output
        best_idx = 0
        best_conf = 0.0
        for i, conf in enumerate(confidences):
            if conf > best_conf:
                best_conf = conf
                best_idx = i

        # Use best output, but append others if they add value
        best = outputs[best_idx]
        extras = [o for i, o in enumerate(outputs) if i != best_idx and o and o != best]

        if extras:
            combined = best + "\n\n**Additional perspectives:**\n"
            for extra in extras[:3]:  # limit to 3
                combined += f"- {extra}\n"
            return combined

        return best

    def get_metrics(self) -> dict[str, Any]:
        return {"summation_count": self._summation_count}
