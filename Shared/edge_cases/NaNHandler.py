"""
Vibhu-Oska AI-OS — NaN Handler
Detects NaN/inf in tensors, logs, alerts, and triggers fallback.
"""

from __future__ import annotations

import logging
from typing import Optional, Callable

import torch

log = logging.getLogger("NaNHandler")


class NaNHandler:
    """
    Detects and handles NaN/inf values in tensors.

    Usage:
        handler = NaNHandler()
        if handler.detect(tensor):
            handler.handle("training_loss")
    """

    def __init__(
        self,
        max_nan_before_fallback: int = 3,
        on_nan_detected: Optional[Callable[[str, int], None]] = None,
    ) -> None:
        self._nan_count: int = 0
        self._max_nan_before_fallback = max_nan_before_fallback
        self._on_nan_detected = on_nan_detected

    @property
    def nan_count(self) -> int:
        return self._nan_count

    @property
    def should_fallback(self) -> bool:
        return self._nan_count >= self._max_nan_before_fallback

    def detect(self, tensor: torch.Tensor) -> bool:
        """Check if tensor contains NaN or Inf values."""
        if not isinstance(tensor, torch.Tensor):
            return False
        has_nan = bool(torch.isnan(tensor).any().item())
        has_inf = bool(torch.isinf(tensor).any().item())
        return has_nan or has_inf

    def detect_gradients(self, model: torch.nn.Module) -> bool:
        """Check if any model gradients contain NaN or Inf."""
        for param in model.parameters():
            if param.grad is not None and self.detect(param.grad):
                return True
        return False

    def safe_loss_value(self, loss: torch.Tensor) -> float:
        """Extract loss value safely, returning inf if NaN/Inf detected."""
        if self.detect(loss):
            self._nan_count += 1
            if self._on_nan_detected:
                self._on_nan_detected("loss_nan", self._nan_count)
            log.warning(f"NaN/Inf detected in loss (count: {self._nan_count})")
            return float("inf")
        val = loss.item()
        if not isinstance(val, float) or val != val:  # NaN check
            self._nan_count += 1
            return float("inf")
        return val

    def handle(self, context: str) -> dict[str, any]:
        """
        Handle a NaN detection event.
        Returns action recommendations.
        """
        self._nan_count += 1
        log.warning(f"NaN detected in context '{context}' (total: {self._nan_count})")

        action = "skip_batch"
        if self.should_fallback:
            action = "switch_to_fp32"
            log.error(f"Too many NaNs ({self._nan_count}). Recommend switching to fp32.")

        return {
            "nan_count": self._nan_count,
            "context": context,
            "action": action,
            "should_fallback": self.should_fallback,
        }

    def reset(self) -> None:
        """Reset the NaN counter."""
        self._nan_count = 0

    def get_metrics(self) -> dict[str, int]:
        return {
            "nan_count": self._nan_count,
            "max_before_fallback": self._max_nan_before_fallback,
        }
