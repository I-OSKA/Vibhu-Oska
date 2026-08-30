"""
Vibhu-Oska AI-OS — SQLCore Specialist
Handles SQL specific tasks: PostgreSQL, SQLite, MySQL, query optimization, PL/pgSQL.
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

log = logging.getLogger("SQLCore")


class SQLCore(BaseSpecialist):
    """
    SQL specialist for Vibhu-Oska.
    
    Handles:
    - Query writing and optimization
    - Database design and normalization
    - Stored procedures and functions
    - Indexing strategies
    - Migration management
    - Performance tuning
    """

    def __init__(self) -> None:
        super().__init__(
            name="SQLCore",
            domain=SpecialistDomain.CODING,
            capabilities=SpecialistCapabilities(
                domains=["code_generation", "code_review", "debugging", "performance"],
                subdomains=["sql", "postgresql", "sqlite", "mysql", "database"],
                max_complexity=8,
                estimated_latency_ms=200.0,
                requires_model=False,
                supported_formats=["text", "code"],
            ),
        )
        self._initialized = False

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize SQLCore specialist."""
        self._initialized = True
        log.info("SQLCore initialized.")

    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process a SQL related task.
        
        Args:
            input_data: Must contain 'prompt' or 'content' with the SQL task
            
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
                "specialist": "SQLCore",
                "language": "sql",
                "task_type": self._classify_task(prompt),
            },
        )

    def _generate_response(self, prompt: str) -> str:
        """Generate a response based on the prompt."""
        prompt_lower = prompt.lower()
        
        if "optimize" in prompt_lower or "performance" in prompt_lower or "slow" in prompt_lower:
            return self._optimization_response(prompt)
        elif "index" in prompt_lower:
            return self._indexing_response(prompt)
        elif "join" in prompt_lower:
            return self._join_response(prompt)
        elif "schema" in prompt_lower or "design" in prompt_lower:
            return self._design_response(prompt)
        else:
            return self._general_response(prompt)

    def _optimization_response(self, prompt: str) -> str:
        """Generate optimization response."""
        return (
            "SQL Optimization:\n"
            "1. Use EXPLAIN ANALYZE to understand query plans\n"
            "2. Avoid SELECT * - specify needed columns\n"
            "3. Use appropriate JOIN types (INNER vs LEFT)\n"
            "4. Filter early with WHERE clauses\n"
            "5. Use LIMIT for large result sets\n"
            "6. Avoid functions on indexed columns in WHERE"
        )

    def _indexing_response(self, prompt: str) -> str:
        """Generate indexing response."""
        return (
            "SQL Indexing:\n"
            "1. Create indexes on frequently queried columns\n"
            "2. Use composite indexes for multi-column queries\n"
            "3. Consider partial indexes for filtered queries\n"
            "4. Monitor index usage with pg_stat_user_indexes\n"
            "5. Remove unused indexes to improve write performance\n"
            "6. Use covering indexes for index-only scans"
        )

    def _join_response(self, prompt: str) -> str:
        """Generate join response."""
        return (
            "SQL Joins:\n"
            "1. INNER JOIN: matching rows from both tables\n"
            "2. LEFT JOIN: all rows from left table\n"
            "3. RIGHT JOIN: all rows from right table\n"
            "4. FULL JOIN: all rows from both tables\n"
            "5. CROSS JOIN: Cartesian product\n"
            "6. Self JOIN: table joined with itself"
        )

    def _design_response(self, prompt: str) -> str:
        """Generate design response."""
        return (
            "SQL Database Design:\n"
            "1. Normalize to 3NF (avoid over-normalization)\n"
            "2. Use appropriate data types\n"
            "3. Define primary keys and foreign keys\n"
            "4. Add constraints (NOT NULL, UNIQUE, CHECK)\n"
            "5. Document schema with comments\n"
            "6. Plan for scalability from the start"
        )

    def _general_response(self, prompt: str) -> str:
        """Generate general response."""
        return (
            f"SQLCore received your query about SQL.\n"
            f"Query: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n"
            f"For specific help, try including keywords like 'optimize', 'index', 'join', or 'schema'."
        )

    def _classify_task(self, prompt: str) -> str:
        """Classify the task type."""
        prompt_lower = prompt.lower()
        if "optimize" in prompt_lower or "performance" in prompt_lower:
            return "optimization"
        elif "index" in prompt_lower:
            return "indexing"
        elif "join" in prompt_lower:
            return "joins"
        elif "schema" in prompt_lower or "design" in prompt_lower:
            return "design"
        else:
            return "general"
