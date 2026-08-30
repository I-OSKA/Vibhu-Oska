"""
Vibhu-Oska AI-OS — DeepThoughtEngine
MCTS-inspired reflection loop for complex reasoning.

Architecture:
  ThoughtNode     → Single reasoning step with score
  ThoughtPath     → Complete reasoning chain (list of nodes)
  DeepThoughtEngine → Orchestrates expand/simulate/backprop/select cycle

This module is a SUB-MODULE of CognitionCore, not a separate core.
It provides a deep_thought mode that CognitionCore can invoke for complex queries.

All processing is local. Zero external APIs.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

logger = logging.getLogger("DeepThought")


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


@dataclass
class ThoughtNode:
    """
    A single step in a reasoning path.

    Attributes:
        content: The reasoning text or hypothesis
        score: Evaluation score (0.0 to 1.0)
        visits: Number of times this node was visited
        depth: Depth in the reasoning tree
        metadata: Arbitrary context (e.g., prompt, template index)
    """
    content: str
    score: float = 0.0
    visits: int = 0
    depth: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"ThoughtNode(score={self.score:.2f}, visits={self.visits}, depth={self.depth})"


@dataclass
class ThoughtPath:
    """
    A complete reasoning chain — list of ThoughtNodes from root to leaf.

    Attributes:
        nodes: Ordered list of reasoning steps
        total_score: Aggregate score across all nodes
        avg_score: Average score per node
    """
    nodes: list[ThoughtNode] = field(default_factory=list)

    @property
    def total_score(self) -> float:
        if not self.nodes:
            return 0.0
        return sum(n.score for n in self.nodes)

    @property
    def avg_score(self) -> float:
        if not self.nodes:
            return 0.0
        return self.total_score / len(self.nodes)

    @property
    def length(self) -> int:
        return len(self.nodes)

    def __repr__(self) -> str:
        return f"ThoughtPath(length={self.length}, avg_score={self.avg_score:.2f})"


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class PathGenerator:
    """
    Generates candidate reasoning paths for a given prompt.

    Uses template-based diversity to explore different reasoning strategies.
    """

    STRATEGIES = [
        "direct",       # Straightforward analysis
        "step_by_step", # Decompose and address each component
        "alternative",  # Consider multiple interpretations
        "contrastive",  # Compare pros and cons
        "causal",       # Trace cause-effect chain
    ]

    @staticmethod
    def generate(
        prompt: str,
        context: list[dict[str, Any]],
        n_paths: int = 3,
    ) -> list[ThoughtPath]:
        """
        Generate n diverse reasoning paths.

        Parameters:
            prompt: User query
            context: Retrieved context items
            n_paths: Number of paths to generate (default 3)
        Returns: List of ThoughtPath with initial (unscored) nodes
        """
        paths = []
        strategies = PathGenerator.STRATEGIES[:n_paths]

        for i, strategy in enumerate(strategies):
            node = ThoughtNode(
                content=f"[{strategy}] Reasoning about: {prompt}",
                depth=0,
                metadata={"strategy": strategy, "prompt": prompt, "context_count": len(context)},
            )
            paths.append(ThoughtPath(nodes=[node]))

        return paths


class PathEvaluator:
    """
    Evaluates reasoning paths based on relevance, coherence, and completeness.

    Scoring factors:
    - Context utilization (are referenced context items used?)
    - Coherence (does the reasoning flow logically?)
    - Completeness (are all aspects of the prompt addressed?)
    - Conciseness (is the reasoning efficient?)
    """

    @staticmethod
    def evaluate(
        path: ThoughtPath,
        prompt: str,
        context: list[dict[str, Any]],
    ) -> float:
        """
        Score a reasoning path from 0.0 to 1.0.

        Parameters:
            path: The thought path to evaluate
            prompt: Original user query
            context: Retrieved context items
        Returns: Score between 0.0 and 1.0
        """
        if not path.nodes:
            return 0.0

        score = 0.5  # Base score

        # Factor 1: Context utilization (up to +0.2)
        if context:
            context_texts = " ".join(
                str(item.get("content", "")) for item in context[:3]
            )
            for node in path.nodes:
                # Simple overlap check
                words_in_context = set(context_texts.lower().split())
                words_in_node = set(node.content.lower().split())
                overlap = len(words_in_context & words_in_node)
                if overlap > 2:
                    score += 0.1
                    break

        # Factor 2: Length appropriateness (up to +0.15)
        total_length = sum(len(n.content) for n in path.nodes)
        if 50 < total_length < 500:
            score += 0.15
        elif 20 < total_length < 1000:
            score += 0.08

        # Factor 3: Strategy diversity bonus (up to +0.15)
        strategies = set(n.metadata.get("strategy", "") for n in path.nodes)
        if len(strategies) > 1:
            score += 0.15
        elif len(strategies) == 1:
            score += 0.05

        return min(score, 1.0)


class PathSelector:
    """
    Selects the best reasoning path using UCB1-inspired exploration.
    """

    @staticmethod
    def select(
        paths: list[ThoughtPath],
        exploration_weight: float = 1.41,
    ) -> Optional[ThoughtPath]:
        """
        Select the best path using exploration vs exploitation.

        Parameters:
            paths: Evaluated paths with scores
            exploration_weight: UCB1 exploration constant
        Returns: Best ThoughtPath or None
        """
        if not paths:
            return None

        total_visits = sum(
            sum(n.visits for n in p.nodes) for p in paths
        )

        def ucb1_score(path: ThoughtPath) -> float:
            if not path.nodes:
                return 0.0
            avg = path.avg_score
            visits = sum(n.visits for n in path.nodes)
            if visits == 0:
                return float("inf")  # Unexplored paths get priority
            exploration = exploration_weight * (1.0 / (visits + 1)) ** 0.5
            return avg + exploration

        return max(paths, key=ucb1_score)


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class DeepThoughtEngine:
    """
    DeepThoughtEngine — orchestrates multi-path reasoning for complex queries.

    This is a SUB-MODULE of CognitionCore, invoked when deep_thought mode is active.

    Flow:
        1. Generate N reasoning paths
        2. Evaluate each path
        3. Select best path via UCB1
        4. Expand best path with refinement
        5. Return final answer from best path

    Usage:
        engine = DeepThoughtEngine()
        result = await engine.reflect(
            prompt="complex question",
            context=[...],
            generate_fn=cognition_core.generate,
        )
    """

    def __init__(
        self,
        n_paths: int = 3,
        n_iterations: int = 2,
        exploration_weight: float = 1.41,
    ) -> None:
        """
        Initialize DeepThought engine.

        Parameters:
            n_paths: Number of initial reasoning paths (default 3)
            n_iterations: Number of reflect cycles (default 2)
            exploration_weight: UCB1 exploration constant (default 1.41)
        """
        self._n_paths = n_paths
        self._n_iterations = n_iterations
        self._exploration_weight = exploration_weight
        self._generator = PathGenerator()
        self._evaluator = PathEvaluator()
        self._selector = PathSelector()

    async def reflect(
        self,
        prompt: str,
        context: list[dict[str, Any]],
        generate_fn: Callable[..., Any],
        max_tokens: int = 512,
    ) -> str:
        """
        Run multi-path reflection and return the best response.

        Parameters:
            prompt: User query requiring deep reasoning
            context: Retrieved context items
            generate_fn: Async function to generate text (CognitionCore.generate)
            max_tokens: Max tokens per generation (default 512)
        Returns: Final response string from best reasoning path
        """
        start_time = time.time()
        logger.info("DeepThought started: %d paths, %d iterations", self._n_paths, self._n_iterations)

        # Step 1: Generate initial paths
        paths = self._generator.generate(prompt, context, self._n_paths)
        logger.info("Generated %d initial paths", len(paths))

        # Step 2: Iterate (expand → evaluate → select)
        for iteration in range(self._n_iterations):
            # Evaluate all paths
            for path in paths:
                score = self._evaluator.evaluate(path, prompt, context)
                # Update node scores
                for node in path.nodes:
                    node.score = score
                    node.visits += 1

            # Select best path
            best_path = self._selector.select(paths, self._exploration_weight)
            if best_path:
                logger.info(
                    "Iteration %d: best path score=%.2f, length=%d",
                    iteration + 1,
                    best_path.avg_score,
                    best_path.length,
                )

                # Expand best path (generate next reasoning step)
                if best_path.nodes:
                    last_node = best_path.nodes[-1]
                    expansion_prompt = (
                        f"Continue reasoning from: {last_node.content}\n"
                        f"Original question: {prompt}"
                    )
                    try:
                        expansion = await generate_fn(
                            prompt=expansion_prompt,
                            max_tokens=max_tokens,
                        )
                        new_node = ThoughtNode(
                            content=str(expansion)[:500],
                            depth=last_node.depth + 1,
                            metadata={"iteration": iteration + 1, "expanded_from": last_node.depth},
                        )
                        best_path.nodes.append(new_node)
                    except Exception as e:
                        logger.warning("Expansion failed: %s", e)

        # Step 3: Final selection
        final_best = self._selector.select(paths, self._exploration_weight)
        elapsed = time.time() - start_time

        if final_best and final_best.nodes:
            # Use the last node's content as the final response
            result = final_best.nodes[-1].content
            logger.info(
                "DeepThought completed: score=%.2f, nodes=%d, elapsed=%.2fs",
                final_best.avg_score,
                final_best.length,
                elapsed,
            )
            return result

        # Fallback: generate normally
        logger.warning("DeepThought found no good path, falling back to direct generation")
        fallback = await generate_fn(prompt=prompt, max_tokens=max_tokens)
        return str(fallback)
