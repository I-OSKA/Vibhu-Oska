"""
Vibhu-Oska AI-OS — SecurityCore Specialist
Handles security tasks: OWASP, JWT, OAuth2, RBAC, encryption, pen testing.
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

log = logging.getLogger("SecurityCore")


class SecurityCore(BaseSpecialist):
    """
    Security specialist for Vibhu-Oska.
    
    Handles:
    - OWASP Top 10 vulnerabilities
    - Authentication (JWT, OAuth2)
    - Authorization (RBAC, ABAC)
    - Encryption (symmetric, asymmetric)
    - Security testing
    """

    def __init__(self) -> None:
        super().__init__(
            name="SecurityCore",
            domain=SpecialistDomain.REAL_WORLD,
            capabilities=SpecialistCapabilities(
                domains=["security", "authentication", "encryption"],
                subdomains=["owasp", "jwt", "oauth2", "rbac", "encryption", "pen_testing"],
                max_complexity=9,
                estimated_latency_ms=200.0,
                requires_model=False,
                supported_formats=["text", "code"],
            ),
        )
        self._initialized = False

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize SecurityCore specialist."""
        self._initialized = True
        log.info("SecurityCore initialized.")

    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process a security task.
        
        Args:
            input_data: Must contain 'prompt' or 'content' with the task
            
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
                "specialist": "SecurityCore",
                "task_type": self._classify_task(prompt),
            },
        )

    def _generate_response(self, prompt: str) -> str:
        """Generate a response based on the prompt."""
        prompt_lower = prompt.lower()
        
        if "owasp" in prompt_lower or "vulnerability" in prompt_lower:
            return self._owasp_response(prompt)
        elif "jwt" in prompt_lower or "token" in prompt_lower:
            return self._jwt_response(prompt)
        elif "oauth" in prompt_lower:
            return self._oauth_response(prompt)
        elif "encrypt" in prompt_lower or "cipher" in prompt_lower:
            return self._encryption_response(prompt)
        else:
            return self._general_response(prompt)

    def _owasp_response(self, prompt: str) -> str:
        """Generate OWASP response."""
        return (
            "OWASP Top 10:\n"
            "1. Injection (SQL, NoSQL, LDAP)\n"
            "2. Broken Authentication\n"
            "3. Sensitive Data Exposure\n"
            "4. XML External Entities (XXE)\n"
            "5. Broken Access Control\n"
            "6. Security Misconfiguration\n"
            "7. Cross-Site Scripting (XSS)\n"
            "8. Insecure Deserialization\n"
            "9. Using Components with Known Vulnerabilities\n"
            "10. Insufficient Logging & Monitoring"
        )

    def _jwt_response(self, prompt: str) -> str:
        """Generate JWT response."""
        return (
            "JWT Implementation:\n"
            "1. Use RS256 for asymmetric signing\n"
            "2. Set appropriate expiration times\n"
            "3. Include essential claims only\n"
            "4. Validate signature and claims\n"
            "5. Use refresh tokens for long sessions\n"
            "6. Store securely (httpOnly cookie)"
        )

    def _oauth_response(self, prompt: str) -> str:
        """Generate OAuth response."""
        return (
            "OAuth2 Implementation:\n"
            "1. Use Authorization Code flow with PKCE\n"
            "2. Validate state parameter\n"
            "3. Store tokens securely\n"
            "4. Implement token refresh\n"
            "5. Use scopes for least privilege\n"
            "6. Validate redirect URIs"
        )

    def _encryption_response(self, prompt: str) -> str:
        """Generate encryption response."""
        return (
            "Encryption Best Practices:\n"
            "1. Use AES-256-GCM for symmetric encryption\n"
            "2. Use RSA-2048+ for asymmetric encryption\n"
            "3. Implement proper key management\n"
            "4. Use TLS for data in transit\n"
            "5. Use encryption for data at rest\n"
            "6. Implement proper IV/nonce generation"
        )

    def _general_response(self, prompt: str) -> str:
        """Generate general response."""
        return (
            f"SecurityCore received your security query.\n"
            f"Query: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n"
            f"For specific help, try including keywords like 'owasp', 'jwt', 'oauth', or 'encrypt'."
        )

    def _classify_task(self, prompt: str) -> str:
        """Classify the task type."""
        prompt_lower = prompt.lower()
        if "owasp" in prompt_lower or "vulnerability" in prompt_lower:
            return "owasp"
        elif "jwt" in prompt_lower or "token" in prompt_lower:
            return "jwt"
        elif "oauth" in prompt_lower:
            return "oauth"
        elif "encrypt" in prompt_lower or "cipher" in prompt_lower:
            return "encryption"
        else:
            return "general"
