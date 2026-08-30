"""
Vibhu-Oska AI-OS — ExcelCore Specialist
Handles Excel specific tasks: formulas, VBA, Power Query, pivot tables, openpyxl.
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

log = logging.getLogger("ExcelCore")


class ExcelCore(BaseSpecialist):
    """
    Excel specialist for Vibhu-Oska.
    
    Handles:
    - Formula writing and optimization
    - VBA/Macros
    - Power Query (M language)
    - Pivot tables
    - Data visualization
    - openpyxl/xlwings automation
    """

    def __init__(self) -> None:
        super().__init__(
            name="ExcelCore",
            domain=SpecialistDomain.REAL_WORLD,
            capabilities=SpecialistCapabilities(
                domains=["spreadsheet", "data_analysis", "automation"],
                subdomains=["excel", "vba", "power_query", "pivot_table", "openpyxl"],
                max_complexity=7,
                estimated_latency_ms=200.0,
                requires_model=False,
                supported_formats=["text", "code"],
            ),
        )
        self._initialized = False

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize ExcelCore specialist."""
        self._initialized = True
        log.info("ExcelCore initialized.")

    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process an Excel related task.
        
        Args:
            input_data: Must contain 'prompt' or 'content' with the Excel task
            
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
                "specialist": "ExcelCore",
                "task_type": self._classify_task(prompt),
            },
        )

    def _generate_response(self, prompt: str) -> str:
        """Generate a response based on the prompt."""
        prompt_lower = prompt.lower()
        
        if "formula" in prompt_lower:
            return self._formula_response(prompt)
        elif "vba" in prompt_lower or "macro" in prompt_lower:
            return self._vba_response(prompt)
        elif "pivot" in prompt_lower:
            return self._pivot_response(prompt)
        elif "power query" in prompt_lower or "m language" in prompt_lower:
            return self._power_query_response(prompt)
        else:
            return self._general_response(prompt)

    def _formula_response(self, prompt: str) -> str:
        """Generate formula response."""
        return (
            "Excel Formulas:\n"
            "1. VLOOKUP/INDEX-MATCH for lookups\n"
            "2. SUMIFS/COUNTIFS for conditional aggregation\n"
            "3. IF/IFS for conditional logic\n"
            "4. TEXT/DATE for formatting\n"
            "5. ARRAY FORMULAS for complex calculations\n"
            "6. Named ranges for readability"
        )

    def _vba_response(self, prompt: str) -> str:
        """Generate VBA response."""
        return (
            "Excel VBA:\n"
            "1. Use Sub for actions, Function for returns\n"
            "2. Declare variables with Option Explicit\n"
            "3. Use With blocks for object manipulation\n"
            "4. Implement error handling with On Error\n"
            "5. Use Range objects for cell manipulation\n"
            "6. Avoid Select/Activate - work with objects directly"
        )

    def _pivot_response(self, prompt: str) -> str:
        """Generate pivot table response."""
        return (
            "Excel Pivot Tables:\n"
            "1. Source data should be in tabular format\n"
            "2. Use slicers for interactive filtering\n"
            "3. Group dates by month/quarter/year\n"
            "4. Use calculated fields for custom metrics\n"
            "5. Apply conditional formatting for insights\n"
            "6. Refresh data connections regularly"
        )

    def _power_query_response(self, prompt: str) -> str:
        """Generate Power Query response."""
        return (
            "Power Query (M Language):\n"
            "1. Use Table.FromRows for data import\n"
            "2. Apply transformations step-by-step\n"
            "3. Use M functions for custom logic\n"
            "4. Merge queries for joins\n"
            "5. Append queries for unions\n"
            "6. Parameterize for dynamic data sources"
        )

    def _general_response(self, prompt: str) -> str:
        """Generate general response."""
        return (
            f"ExcelCore received your query about Excel.\n"
            f"Query: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n"
            f"For specific help, try including keywords like 'formula', 'vba', 'pivot', or 'power query'."
        )

    def _classify_task(self, prompt: str) -> str:
        """Classify the task type."""
        prompt_lower = prompt.lower()
        if "formula" in prompt_lower:
            return "formulas"
        elif "vba" in prompt_lower or "macro" in prompt_lower:
            return "vba"
        elif "pivot" in prompt_lower:
            return "pivot_tables"
        elif "power query" in prompt_lower:
            return "power_query"
        else:
            return "general"
