"""
Vibhu-Oska AI-OS — KnowledgeCore Specialist
Handles general knowledge tasks: facts, science, math, history, philosophy, reasoning.
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

log = logging.getLogger("KnowledgeCore")


class KnowledgeCore(BaseSpecialist):
    """
    General knowledge specialist for Vibhu-Oska.
    
    Handles:
    - Factual questions
    - Scientific concepts
    - Mathematical reasoning
    - Historical information
    - Philosophical discussions
    """

    def __init__(self) -> None:
        super().__init__(
            name="KnowledgeCore",
            domain=SpecialistDomain.REAL_WORLD,
            capabilities=SpecialistCapabilities(
                domains=["knowledge", "reasoning", "education"],
                subdomains=["science", "math", "history", "philosophy", "facts"],
                max_complexity=7,
                estimated_latency_ms=200.0,
                requires_model=False,
                supported_formats=["text"],
            ),
        )
        self._initialized = False

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize KnowledgeCore specialist."""
        self._initialized = True
        log.info("KnowledgeCore initialized.")

    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process a knowledge task.
        
        Args:
            input_data: Must contain 'prompt' or 'content' with the question
            
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
            confidence=0.7,
            metadata={
                "specialist": "KnowledgeCore",
                "task_type": self._classify_task(prompt),
            },
        )

    def _generate_response(self, prompt: str) -> str:
        """Generate a response based on the prompt."""
        prompt_lower = prompt.lower()
        
        if "science" in prompt_lower or "physics" in prompt_lower or "chemistry" in prompt_lower:
            return self._science_response(prompt)
        elif "math" in prompt_lower or "calculate" in prompt_lower:
            return self._math_response(prompt)
        elif "history" in prompt_lower:
            return self._history_response(prompt)
        elif "philosophy" in prompt_lower:
            return self._philosophy_response(prompt)
        else:
            return self._general_response(prompt)

    def _science_response(self, prompt: str) -> str:
        """Generate science response."""
        return (
            "Scientific Concepts:\n"
            "1. Physics: Laws of motion, thermodynamics, quantum mechanics\n"
            "2. Chemistry: Periodic table, chemical bonds, reactions\n"
            "3. Biology: Cell structure, genetics, evolution\n"
            "4. Earth Science: Geology, meteorology, oceanography\n"
            "5. Scientific Method: Observation, hypothesis, experiment\n"
            "6. Peer review and replication in science"
        )

    def _math_response(self, prompt: str) -> str:
        """Generate math response."""
        return (
            "Mathematical Concepts:\n"
            "1. Algebra: Variables, equations, functions\n"
            "2. Calculus: Derivatives, integrals, limits\n"
            "3. Statistics: Probability, distributions, hypothesis testing\n"
            "4. Linear Algebra: Vectors, matrices, transformations\n"
            "5. Discrete Math: Logic, sets, combinatorics\n"
            "6. Number Theory: Primes, modular arithmetic"
        )

    def _history_response(self, prompt: str) -> str:
        """Generate history response."""
        return (
            "Historical Information:\n"
            "1. Ancient civilizations: Mesopotamia, Egypt, Greece, Rome\n"
            "2. Medieval period: Feudalism, Crusades, Renaissance\n"
            "3. Modern era: Industrial Revolution, World Wars\n"
            "4. Cultural movements: Enlightenment, Romanticism\n"
            "5. Technological history: Printing press, computers\n"
            "6. Primary sources and historiography"
        )

    def _philosophy_response(self, prompt: str) -> str:
        """Generate philosophy response."""
        return (
            "Philosophical Concepts:\n"
            "1. Metaphysics: Nature of reality, existence\n"
            "2. Epistemology: Knowledge, truth, justification\n"
            "3. Ethics: Moral principles, right and wrong\n"
            "4. Logic: Valid reasoning, fallacies\n"
            "5. Aesthetics: Beauty, art, taste\n"
            "6. Major philosophers: Socrates, Kant, Nietzsche"
        )

    def _general_response(self, prompt: str) -> str:
        """Generate general response."""
        return (
            f"KnowledgeCore received your knowledge question.\n"
            f"Query: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n"
            f"For specific help, try including keywords like 'science', 'math', 'history', or 'philosophy'."
        )

    def _classify_task(self, prompt: str) -> str:
        """Classify the task type."""
        prompt_lower = prompt.lower()
        if "science" in prompt_lower or "physics" in prompt_lower:
            return "science"
        elif "math" in prompt_lower or "calculate" in prompt_lower:
            return "math"
        elif "history" in prompt_lower:
            return "history"
        elif "philosophy" in prompt_lower:
            return "philosophy"
        else:
            return "general"
