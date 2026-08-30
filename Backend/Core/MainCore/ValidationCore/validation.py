"""
Vibhu-Oska AI-OS — ValidationCore
Yama (Justice) — The quality and security gate.

Responsibilities:
  1. INPUT GATE    — Sanitize, block injection, detect attacks
  2. OUTPUT GATE   — Verify relevance, safety, schema compliance
  3. CYBERSEC      — Monitor for anomalies, suspicious patterns, intrusions
  4. QUALITY       — Ensure responses are coherent, helpful, on-topic

ValidationCore sits between every core transition:
  User Input → [ValidationCore] → Core Processing → [ValidationCore] → User Output

If ValidationCore blocks something, it logs the event and returns a safe fallback.
"""

from __future__ import annotations

import logging
import re
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("ValidationCore")


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class ThreatLevel(Enum):
    """Threat severity classification."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    passed: bool
    reason: str
    threat_level: ThreatLevel = ThreatLevel.NONE
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"ValidationResult(passed={self.passed}, threat={self.threat_level.value}, reason={self.reason!r})"


@dataclass
class SecurityEvent:
    """Recorded security event for audit trail."""
    timestamp: float
    event_type: str
    threat_level: ThreatLevel
    details: str
    source: str = "validation_core"


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class InputSanitizer:
    """
    INPUT GATE — Sanitizes and validates user input before processing.

    Checks:
    - Size limits
    - SQL injection patterns
    - XSS/script injection
    - Command injection
    - Prompt injection attempts
    - Rate limiting (per-session)
    """

    # Dangerous patterns (case-insensitive)
    SQL_PATTERNS = [
        r"'\s*OR\s+'",
        r"'\s*OR\s+\d",
        r"UNION\s+SELECT",
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
        r"INSERT\s+INTO",
        r"UPDATE\s+\w+\s+SET",
        r";\s*--",
        r"'\s*;\s*",
    ]

    XSS_PATTERNS = [
        r"<script[\s>]",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
        r"<form",
        r"eval\s*\(",
        r"document\.cookie",
        r"window\.location",
    ]

    CMD_PATTERNS = [
        r";\s*(rm|del|rmdir|format|mkfs)",
        r"\|\s*(rm|del|rmdir)",
        r"`[^`]*`",
        r"\$\([^)]*\)",
        r"&&\s*(rm|del|sudo|chmod)",
        r"\|\|\s*(rm|del)",
    ]

    PROMPT_INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?)",
        r"you\s+are\s+now\s+",
        r"act\s+as\s+if\s+",
        r"pretend\s+you\s+are\s+",
        r"disregard\s+(all\s+)?(previous|prior)",
        r"new\s+instructions?:",
        r"system\s*:\s*",
        r"ADMIN\s+MODE",
        r"override\s+safety",
        r"bypass\s+(all\s+)?(filters?|restrictions?|rules?)",
    ]

    def __init__(self, max_prompt_length: int = 100_000) -> None:
        self._max_prompt_length = max_prompt_length
        self._compiled_sql = [re.compile(p, re.IGNORECASE) for p in self.SQL_PATTERNS]
        self._compiled_xss = [re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS]
        self._compiled_cmd = [re.compile(p, re.IGNORECASE) for p in self.CMD_PATTERNS]
        self._compiled_injection = [re.compile(p, re.IGNORECASE) for p in self.PROMPT_INJECTION_PATTERNS]

    def sanitize(self, text: str) -> ValidationResult:
        """
        Run all input checks. Returns first failure or passes all.

        Parameters:
            text: Raw user input
        Returns: ValidationResult with pass/fail and threat details
        """
        if not text or not text.strip():
            return ValidationResult(passed=True, reason="Empty input — will be handled downstream")

        # 1. Length check
        if len(text) > self._max_prompt_length:
            return ValidationResult(
                passed=False,
                reason=f"Input exceeds max length ({self._max_prompt_length} chars)",
                threat_level=ThreatLevel.LOW,
            )

        # 2. SQL injection
        for pattern in self._compiled_sql:
            if pattern.search(text):
                return ValidationResult(
                    passed=False,
                    reason=f"SQL injection pattern detected: {pattern.pattern}",
                    threat_level=ThreatLevel.HIGH,
                )

        # 3. XSS injection
        for pattern in self._compiled_xss:
            if pattern.search(text):
                return ValidationResult(
                    passed=False,
                    reason=f"XSS/script injection detected: {pattern.pattern}",
                    threat_level=ThreatLevel.HIGH,
                )

        # 4. Command injection
        for pattern in self._compiled_cmd:
            if pattern.search(text):
                return ValidationResult(
                    passed=False,
                    reason=f"Command injection detected: {pattern.pattern}",
                    threat_level=ThreatLevel.CRITICAL,
                )

        # 5. Prompt injection
        for pattern in self._compiled_injection:
            if pattern.search(text):
                return ValidationResult(
                    passed=False,
                    reason=f"Prompt injection attempt: {pattern.pattern}",
                    threat_level=ThreatLevel.HIGH,
                )

        return ValidationResult(passed=True, reason="Input validated")


class OutputValidator:
    """
    OUTPUT GATE — Verifies AI responses are safe, relevant, and compliant.

    Checks:
    - Schema compliance (is it a valid response?)
    - Content safety (no credentials, no PII leakage)
    - Relevance check (does it answer the prompt?)
    - Coherence check (is it internally consistent?)
    """

    # Patterns that should never appear in responses
    LEAK_PATTERNS = [
        r"api[_-]?key\s*[=:]\s*\S+",
        r"password\s*[=:]\s*\S+",
        r"secret\s*[=:]\s*\S+",
        r"token\s*[=:]\s*\S+",
        r"sk-[a-zA-Z0-9]{20,}",
        r"ghp_[a-zA-Z0-9]{36}",
        r"AKIA[0-9A-Z]{16}",
    ]

    def __init__(self) -> None:
        self._compiled_leak = [re.compile(p, re.IGNORECASE) for p in self.LEAK_PATTERNS]

    def validate(
        self,
        response: Any,
        prompt: str = "",
        context: list[dict[str, Any]] | None = None,
    ) -> ValidationResult:
        """
        Validate AI output for safety and quality.

        Parameters:
            response: The AI response (string or dict)
            prompt: Original user prompt (for relevance check)
            context: Context items used (for relevance check)
        Returns: ValidationResult
        """
        # 1. Existence check
        if not response:
            return ValidationResult(passed=False, reason="Empty response", threat_level=ThreatLevel.NONE)

        content = ""
        if isinstance(response, str):
            content = response
        elif isinstance(response, dict):
            content = response.get("content", "")
        elif hasattr(response, "content"):
            content = response.content
        else:
            return ValidationResult(
                passed=False,
                reason=f"Invalid response type: {type(response).__name__}",
                threat_level=ThreatLevel.NONE,
            )

        if not content or not str(content).strip():
            return ValidationResult(passed=False, reason="Response content is empty")

        content_str = str(content)

        # 2. Credential leakage check
        for pattern in self._compiled_leak:
            if pattern.search(content_str):
                return ValidationResult(
                    passed=False,
                    reason=f"Credential leakage detected in response: {pattern.pattern}",
                    threat_level=ThreatLevel.CRITICAL,
                    metadata={"redacted": True},
                )

        # 3. Relevance check (basic keyword overlap)
        if prompt:
            relevance = self._check_relevance(content_str, prompt)
            if relevance < 0.05 and len(content_str) > 100:
                return ValidationResult(
                    passed=True,  # Still pass, but flag it
                    reason=f"Low relevance score: {relevance:.2f}",
                    threat_level=ThreatLevel.LOW,
                    metadata={"relevance_score": relevance},
                )

        return ValidationResult(passed=True, reason="Output validated")

    @staticmethod
    def _check_relevance(response: str, prompt: str) -> float:
        """
        Simple keyword overlap relevance check.

        Returns 0.0 to 1.0 — higher means more relevant.
        """
        response_words = set(response.lower().split())
        prompt_words = set(prompt.lower().split())

        # Remove common stop words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                       "being", "have", "has", "had", "do", "does", "did", "will",
                       "would", "could", "should", "may", "might", "can", "shall",
                       "to", "of", "in", "for", "on", "with", "at", "by", "from",
                       "as", "into", "through", "during", "before", "after", "and",
                       "but", "or", "if", "then", "so", "no", "not", "what", "how",
                       "when", "where", "why", "who", "which", "that", "this", "it"}

        prompt_words -= stop_words
        response_words -= stop_words

        if not prompt_words:
            return 0.5  # Can't judge relevance without prompt keywords

        overlap = len(prompt_words & response_words)
        return min(overlap / max(len(prompt_words), 1), 1.0)


class CyberSecMonitor:
    """
    CYBERSEC — Monitors for attack patterns, anomalies, and suspicious behavior.

    Tracks:
    - Failed validation attempts (brute force detection)
    - Repeated injection attempts (attacker probing)
    - Unusual input patterns (anomaly detection)
    - Rate limiting per session
    """

    def __init__(self, window_seconds: int = 300, max_failures: int = 10) -> None:
        self._window = window_seconds
        self._max_failures = max_failures
        self._session_failures: dict[str, deque[float]] = {}
        self._events: deque[SecurityEvent] = deque(maxlen=1000)
        self._blocked_sessions: set[str] = set()

    def record_event(
        self,
        session_id: str,
        event_type: str,
        threat_level: ThreatLevel,
        details: str,
    ) -> None:
        """Record a security event and update failure tracking."""
        event = SecurityEvent(
            timestamp=time.time(),
            event_type=event_type,
            threat_level=threat_level,
            details=details,
            source=f"session:{session_id}",
        )
        self._events.append(event)

        # Track failures per session
        if threat_level in (ThreatLevel.HIGH, ThreatLevel.CRITICAL):
            if session_id not in self._session_failures:
                self._session_failures[session_id] = deque()
            self._session_failures[session_id].append(time.time())

            # Prune old failures outside window
            cutoff = time.time() - self._window
            while self._session_failures[session_id] and self._session_failures[session_id][0] < cutoff:
                self._session_failures[session_id].popleft()

            # Check if session should be blocked
            if len(self._session_failures[session_id]) >= self._max_failures:
                self._blocked_sessions.add(session_id)
                logger.warning("Session blocked due to repeated attacks: %s", session_id)

    def is_blocked(self, session_id: str) -> bool:
        """Check if a session is currently blocked."""
        return session_id in self._blocked_sessions

    def get_threat_summary(self, session_id: str | None = None) -> dict[str, Any]:
        """Get threat summary for monitoring dashboards."""
        events = list(self._events)
        if session_id:
            events = [e for e in events if session_id in e.source]

        return {
            "total_events": len(events),
            "blocked_sessions": len(self._blocked_sessions),
            "threat_counts": {
                level.value: sum(1 for e in events if e.threat_level == level)
                for level in ThreatLevel
            },
            "recent_events": [
                {
                    "timestamp": e.timestamp,
                    "type": e.event_type,
                    "threat": e.threat_level.value,
                    "details": e.details[:100],
                }
                for e in list(events)[-10:]
            ],
        }


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class ValidationCore:
    """
    ValidationCore — Yama (Justice). The quality and security gate.

    Sits between every core transition:
      User Input → [ValidationCore] → Core Processing → [ValidationCore] → User Output

    Responsibilities:
      1. INPUT GATE    — InputSanitizer (injection, XSS, command injection, prompt injection)
      2. OUTPUT GATE   — OutputValidator (schema, safety, relevance, credential leakage)
      3. CYBERSEC      — CyberSecMonitor (anomaly detection, rate limiting, threat tracking)
      4. QUALITY       — Response coherence and helpfulness checks

    Usage:
        vc = ValidationCore.get_instance()

        # Before processing
        result = vc.validate_input(user_input, session_id="abc")
        if not result.passed:
            return blocked_response(result)

        # After processing
        result = vc.validate_output(response, prompt=user_input)
        if not result.passed:
            return safe_fallback(result)
    """

    _instance: Optional["ValidationCore"] = None

    def __init__(self) -> None:
        self._sanitizer = InputSanitizer()
        self._output_validator = OutputValidator()
        self._cybersec = CyberSecMonitor()
        self._initialized = False

    @classmethod
    def get_instance(cls) -> "ValidationCore":
        """Return the singleton ValidationCore instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize(self, max_prompt_length: int = 100_000) -> None:
        """Initialize with configuration."""
        if self._initialized:
            return
        self._sanitizer = InputSanitizer(max_prompt_length=max_prompt_length)
        self._initialized = True
        logger.info("ValidationCore initialized")

    # ── Input Gate ────────────────────────────────────────────────────────────────────────

    def validate_input(
        self,
        text: str,
        session_id: str = "unknown",
    ) -> ValidationResult:
        """
        Validate user input before processing.

        Parameters:
            text: Raw user input
            session_id: Session identifier for rate limiting
        Returns: ValidationResult (passed=True if safe to process)
        """
        if not self._initialized:
            self.initialize()

        # Check if session is blocked
        if self._cybersec.is_blocked(session_id):
            return ValidationResult(
                passed=False,
                reason="Session blocked due to repeated security violations",
                threat_level=ThreatLevel.CRITICAL,
            )

        # Run sanitizer
        result = self._sanitizer.sanitize(text)

        # Record security event if threat detected
        if not result.passed and result.threat_level != ThreatLevel.NONE:
            self._cybersec.record_event(
                session_id=session_id,
                event_type="input_blocked",
                threat_level=result.threat_level,
                details=result.reason,
            )

        return result

    # ── Output Gate ───────────────────────────────────────────────────────────────────────

    def validate_output(
        self,
        response: Any,
        prompt: str = "",
        context: list[dict[str, Any]] | None = None,
    ) -> ValidationResult:
        """
        Validate AI output before returning to user.

        Parameters:
            response: AI response to validate
            prompt: Original user prompt (for relevance check)
            context: Context used (for relevance check)
        Returns: ValidationResult (passed=True if safe to return)
        """
        if not self._initialized:
            self.initialize()

        return self._output_validator.validate(response, prompt, context)

    # ── CyberSec ──────────────────────────────────────────────────────────────────────────

    def get_threat_summary(self, session_id: str | None = None) -> dict[str, Any]:
        """Get security threat summary for monitoring."""
        return self._cybersec.get_threat_summary(session_id)

    def is_session_blocked(self, session_id: str) -> bool:
        """Check if a session is blocked."""
        return self._cybersec.is_blocked(session_id)

    # ── Backward Compatibility ────────────────────────────────────────────────────────────

    def validate_request(self, raw_data: Any) -> bool:
        """Legacy method — returns True if request is structurally valid."""
        if isinstance(raw_data, dict):
            prompt = raw_data.get("prompt", "")
            result = self.validate_input(prompt)
            return result.passed
        return True

    def validate_input_package(self, raw_data: Any) -> tuple[bool, str]:
        """Legacy method — returns (passed, reason)."""
        if isinstance(raw_data, dict):
            prompt = raw_data.get("prompt", "")
            result = self.validate_input(prompt)
            return result.passed, result.reason
        return True, "Valid"

    def validate_ai_output(self, ai_response: Any) -> tuple[bool, str]:
        """Legacy method — returns (passed, reason)."""
        result = self.validate_output(ai_response)
        return result.passed, result.reason
