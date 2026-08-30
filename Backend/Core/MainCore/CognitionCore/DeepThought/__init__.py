"""
Vibhu-Oska AI-OS — DeepThought (CognitionCore Sub-Module)

MCTS-inspired multi-path reflection loop for complex reasoning.

This is NOT a separate core — it's a reasoning MODE within CognitionCore.
When activated, Karsh explores multiple reasoning paths, scores them,
and selects the best response through simulated "deep thought."

Usage:
    from Backend.Core.MainCore.CognitionCore.DeepThought import DeepThoughtEngine
    engine = DeepThoughtEngine()
    result = await engine.reflect(prompt, context, generate_fn)
"""

from .DeepThoughtEngine import DeepThoughtEngine, ThoughtNode, ThoughtPath

__all__ = ["DeepThoughtEngine", "ThoughtNode", "ThoughtPath"]
