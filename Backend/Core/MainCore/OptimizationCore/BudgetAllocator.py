"""
Vibhu-Oska AI-OS — BudgetAllocator
Dynamic VRAM budget allocation per component.
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger("BudgetAllocator")


class BudgetAllocator:
    """Manages dynamic VRAM budgets across components."""

    def __init__(self, total_budget_gb: float = 6.0) -> None:
        self._total = total_budget_gb
        self._budgets: dict[str, float] = {}
        self._borrowed: dict[str, float] = {}

    def set_budget(self, name: str, budget_gb: float) -> None:
        """Set VRAM budget for a component."""
        self._budgets[name] = budget_gb

    def get_budget(self, name: str) -> float:
        """Get current budget for a component."""
        return self._budgets.get(name, 0.0)

    def borrow(self, from_name: str, to_name: str, amount_gb: float) -> bool:
        """Borrow VRAM from one component to another."""
        available = self._budgets.get(from_name, 0) - self._borrowed.get(from_name, 0)
        if amount_gb > available:
            return False
        self._borrowed[from_name] = self._borrowed.get(from_name, 0) + amount_gb
        self._budgets[to_name] = self._budgets.get(to_name, 0) + amount_gb
        log.info(f"Borrowed {amount_gb}GB from {from_name} to {to_name}")
        return True

    def return_borrowed(self, from_name: str, to_name: str, amount_gb: float) -> None:
        """Return borrowed VRAM."""
        self._borrowed[from_name] = max(0, self._borrowed.get(from_name, 0) - amount_gb)
        self._budgets[to_name] = max(0, self._budgets.get(to_name, 0) - amount_gb)

    def get_metrics(self) -> dict[str, Any]:
        return {"budgets": self._budgets.copy(), "borrowed": self._borrowed.copy()}
