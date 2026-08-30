"""
Vibhu-Oska AI-OS — RewardEngine
Calculates rewards for RL rollouts based on format, correctness, style, and safety.
"""

from __future__ import annotations

import re
import logging
from typing import Any, Optional

log = logging.getLogger("RewardEngine")


class RewardEngine:
    """
    Multi-signal reward calculation for RL rollouts.

    Reward = w_format * R_format + w_correct * R_correct + w_style * R_style + w_safety * R_safety
    """

    def __init__(
        self,
        weight_format: float = 0.3,
        weight_correctness: float = 0.4,
        weight_style: float = 0.15,
        weight_safety: float = 0.15,
    ) -> None:
        self._w_format = weight_format
        self._w_correct = weight_correctness
        self._w_style = weight_style
        self._w_safety = weight_safety
        self._total_scored: int = 0
        self._total_reward: float = 0.0

    async def score(
        self,
        prompt: str,
        response: str,
        context: Optional[dict[str, Any]] = None,
    ) -> float:
        """
        Compute total reward for a response.

        Returns: float in [-1.0, 1.0]
        """
        if not response or not response.strip():
            return -1.0

        r_format = self._format_reward(response)
        r_correct = self._correctness_reward(prompt, response, context)
        r_style = self._style_reward(response)
        r_safety = self._safety_reward(response)

        total = (
            self._w_format * r_format
            + self._w_correct * r_correct
            + self._w_style * r_style
            + self._w_safety * r_safety
        )

        self._total_scored += 1
        self._total_reward += total

        return max(-1.0, min(1.0, total))

    def _format_reward(self, response: str) -> float:
        """Reward proper formatting (code blocks, paragraphs, structure)."""
        score = 0.0

        # Has proper paragraphs
        if "\n\n" in response:
            score += 0.2

        # Has code blocks if code-related
        if "```" in response:
            score += 0.3
            # Code blocks are properly closed
            if response.count("```") % 2 == 0:
                score += 0.2

        # Not too short
        if len(response) > 50:
            score += 0.15

        # Not too long
        if len(response) < 2000:
            score += 0.15

        return min(1.0, score)

    def _correctness_reward(
        self,
        prompt: str,
        response: str,
        context: Optional[dict[str, Any]] = None,
    ) -> float:
        """Reward factual correctness (simplified)."""
        score = 0.5  # neutral baseline

        # Contains "I don't know" or similar hedging when uncertain
        uncertain_phrases = [
            "i don't know",
            "i'm not sure",
            "i cannot",
            "i can't",
            "uncertain",
        ]
        for phrase in uncertain_phrases:
            if phrase in response.lower():
                score += 0.1  # honesty bonus

        # Contains a definitive answer
        if "." in response and len(response) > 20:
            score += 0.2

        # References the question
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        overlap = len(prompt_words & response_words) / max(len(prompt_words), 1)
        score += overlap * 0.2

        return min(1.0, score)

    def _style_reward(self, response: str) -> float:
        """Reward good writing style."""
        score = 0.5

        # Proper grammar (heuristic: proper capitalization)
        if response[0].isupper():
            score += 0.15

        # Ends with proper punctuation
        if response.rstrip()[-1] in ".!?:;":
            score += 0.1

        # No excessive repetition
        words = response.split()
        if len(words) > 5:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio > 0.5:
                score += 0.25

        return min(1.0, score)

    def _safety_reward(self, response: str) -> float:
        """Penalize unsafe content."""
        score = 1.0

        # Dangerous patterns
        dangerous = [
            "hack into",
            "break into",
            "steal",
            "harm",
            "kill",
            "attack",
            "exploit",
            "malware",
            "ransomware",
            "phishing",
        ]
        for pattern in dangerous:
            if pattern in response.lower():
                score -= 0.3

        # Profanity (simple check)
        profanity = ["damn", "hell"]
        for word in profanity:
            if word in response.lower():
                score -= 0.05

        return max(0.0, score)

    def get_metrics(self) -> dict[str, Any]:
        avg_reward = (
            self._total_reward / self._total_scored
            if self._total_scored > 0
            else 0.0
        )
        return {
            "total_scored": self._total_scored,
            "avg_reward": avg_reward,
            "total_reward": self._total_reward,
        }
