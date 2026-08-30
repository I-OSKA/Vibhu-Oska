"""
Vibhu-Oska AI-OS — IntentClassifier
Classifies user intent into domains for routing.
"""

from __future__ import annotations

import re
import logging
from typing import Any, Optional

log = logging.getLogger("IntentClassifier")


class Intent:
    CODING = "coding"
    REAL_WORLD = "real_world"
    SIMPLE = "simple"
    COMPLEX = "complex"
    UNKNOWN = "unknown"


class IntentClassifier:
    """
    Classifies user intent into domains for specialist routing.

    Uses a combination of:
    1. Keyword matching (fast path)
    2. Pattern recognition
    3. Router model (if available)
    """

    CODING_KEYWORDS = {
        "code", "python", "javascript", "function", "class", "debug",
        "error", "exception", "import", "variable", "loop", "array",
        "list", "dict", "string", "int", "float", "bool", "compile",
        "build", "test", "refactor", "git", "commit", "push", "pull",
        "api", "endpoint", "database", "sql", "query", "html", "css",
        "react", "fastapi", "flask", "django", "pytorch", "tensor",
    }

    REAL_WORLD_KEYWORDS = {
        "search", "research", "find", "lookup", "web", "internet",
        "file", "folder", "directory", "copy", "move", "delete",
        "system", "process", "service", "install", "update", "config",
        "network", "dns", "http", "ssh", "deploy", "docker", "server",
        "translate", "language", "calendar", "schedule", "remind",
    }

    SIMPLE_KEYWORDS = {
        "hello", "hi", "hey", "thanks", "ok", "yes", "no",
        "what time", "what date", "status", "help", "who are you",
    }

    def __init__(self, router_model: Any = None) -> None:
        self._router_model = router_model
        self._classification_count: int = 0

    def classify(self, prompt: str) -> dict[str, Any]:
        """
        Classify a prompt into an intent.

        Returns:
            {
                "domain": str,
                "subdomain": str,
                "confidence": float,
                "method": str,
            }
        """
        self._classification_count += 1
        norm = prompt.lower().strip()

        # Fast path: keyword matching
        score_coding = sum(1 for kw in self.CODING_KEYWORDS if kw in norm)
        score_realworld = sum(1 for kw in self.REAL_WORLD_KEYWORDS if kw in norm)
        score_simple = sum(1 for kw in self.SIMPLE_KEYWORDS if kw in norm)

        # Simple queries
        if score_simple > 0 and score_coding == 0 and score_realworld == 0:
            return {
                "domain": Intent.SIMPLE,
                "subdomain": "greeting" if any(w in norm for w in ["hello", "hi", "hey"]) else "status",
                "confidence": 0.9,
                "method": "keyword",
            }

        # Coding
        if score_coding > score_realworld and score_coding > 0:
            subdomain = self._detect_coding_subdomain(norm)
            return {
                "domain": Intent.CODING,
                "subdomain": subdomain,
                "confidence": min(0.9, 0.5 + score_coding * 0.1),
                "method": "keyword",
            }

        # Real world
        if score_realworld > 0:
            subdomain = self._detect_realworld_subdomain(norm)
            return {
                "domain": Intent.REAL_WORLD,
                "subdomain": subdomain,
                "confidence": min(0.9, 0.5 + score_realworld * 0.1),
                "method": "keyword",
            }

        # Default: complex
        return {
            "domain": Intent.COMPLEX,
            "subdomain": "general",
            "confidence": 0.5,
            "method": "default",
        }

    def _detect_coding_subdomain(self, prompt: str) -> str:
        if any(w in prompt for w in ["review", "bug", "error", "fix"]):
            return "code_review"
        if any(w in prompt for w in ["test", "assert", "pytest"]):
            return "testing"
        if any(w in prompt for w in ["refactor", "optimize", "clean"]):
            return "refactoring"
        if any(w in prompt for w in ["doc", "readme", "comment"]):
            return "documentation"
        if any(w in prompt for w in ["security", "vulnerability", "auth"]):
            return "security"
        return "general"

    def _detect_realworld_subdomain(self, prompt: str) -> str:
        if any(w in prompt for w in ["search", "research", "web", "find"]):
            return "web_research"
        if any(w in prompt for w in ["file", "folder", "read", "write"]):
            return "file_management"
        if any(w in prompt for w in ["system", "process", "install"]):
            return "system_admin"
        if any(w in prompt for w in ["network", "dns", "http"]):
            return "network_ops"
        if any(w in prompt for w in ["sql", "database", "query"]):
            return "database_ops"
        if any(w in prompt for w in ["deploy", "docker", "ci", "cd"]):
            return "devops"
        return "general"

    def get_metrics(self) -> dict[str, Any]:
        return {"classification_count": self._classification_count}
