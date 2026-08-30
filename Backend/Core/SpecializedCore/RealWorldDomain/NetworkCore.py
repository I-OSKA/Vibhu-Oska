"""
Vibhu-Oska AI-OS — NetworkCore Specialist
Handles networking tasks: HTTP/2/3, WebSocket, gRPC, REST, GraphQL, DNS, TLS.
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

log = logging.getLogger("NetworkCore")


class NetworkCore(BaseSpecialist):
    """
    Network specialist for Vibhu-Oska.
    
    Handles:
    - HTTP/HTTPS protocols
    - WebSocket connections
    - gRPC services
    - REST API design
    - GraphQL schemas
    - DNS configuration
    - TLS/SSL security
    """

    def __init__(self) -> None:
        super().__init__(
            name="NetworkCore",
            domain=SpecialistDomain.REAL_WORLD,
            capabilities=SpecialistCapabilities(
                domains=["networking", "api_design", "security"],
                subdomains=["http", "websocket", "grpc", "rest", "graphql", "dns", "tls"],
                max_complexity=8,
                estimated_latency_ms=200.0,
                requires_model=False,
                supported_formats=["text", "code"],
            ),
        )
        self._initialized = False

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize NetworkCore specialist."""
        self._initialized = True
        log.info("NetworkCore initialized.")

    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process a networking task.
        
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
                "specialist": "NetworkCore",
                "task_type": self._classify_task(prompt),
            },
        )

    def _generate_response(self, prompt: str) -> str:
        """Generate a response based on the prompt."""
        prompt_lower = prompt.lower()
        
        if "rest" in prompt_lower or "api" in prompt_lower:
            return self._rest_response(prompt)
        elif "graphql" in prompt_lower:
            return self._graphql_response(prompt)
        elif "websocket" in prompt_lower or "ws" in prompt_lower:
            return self._websocket_response(prompt)
        elif "grpc" in prompt_lower:
            return self._grpc_response(prompt)
        elif "tls" in prompt_lower or "ssl" in prompt_lower or "certificate" in prompt_lower:
            return self._tls_response(prompt)
        else:
            return self._general_response(prompt)

    def _rest_response(self, prompt: str) -> str:
        """Generate REST API response."""
        return (
            "REST API Design:\n"
            "1. Use proper HTTP methods (GET, POST, PUT, DELETE)\n"
            "2. Resource-based URLs (/users/{id})\n"
            "3. Status codes (200, 201, 400, 404, 500)\n"
            "4. Pagination for large collections\n"
            "5. HATEOAS for discoverability\n"
            "6. Versioning (URL, header, or query)"
        )

    def _graphql_response(self, prompt: str) -> str:
        """Generate GraphQL response."""
        return (
            "GraphQL Design:\n"
            "1. Schema-first development\n"
            "2. Use queries for reads, mutations for writes\n"
            "3. Implement proper error handling\n"
            "4. Use DataLoader for N+1 problem\n"
            "5. Implement query complexity limits\n"
            "6. Use subscriptions for real-time"
        )

    def _websocket_response(self, prompt: str) -> str:
        """Generate WebSocket response."""
        return (
            "WebSocket Implementation:\n"
            "1. Use ws:// or wss:// protocol\n"
            "2. Implement heartbeats for connection health\n"
            "3. Handle reconnection logic\n"
            "4. Use JSON for message serialization\n"
            "5. Implement room/channel patterns\n"
            "6. Handle binary data efficiently"
        )

    def _grpc_response(self, prompt: str) -> str:
        """Generate gRPC response."""
        return (
            "gRPC Services:\n"
            "1. Define .proto files for service contracts\n"
            "2. Use protocol buffers for serialization\n"
            "3. Implement streaming (unary, server, bidirectional)\n"
            "4. Use interceptors for middleware\n"
            "5. Implement deadline/timeout handling\n"
            "6. Use load balancing (client-side or proxy)"
        )

    def _tls_response(self, prompt: str) -> str:
        """Generate TLS/SSL response."""
        return (
            "TLS/SSL Security:\n"
            "1. Use Let's Encrypt for free certificates\n"
            "2. Implement certificate rotation\n"
            "3. Use TLS 1.3 for better performance\n"
            "4. Implement HSTS headers\n"
            "5. Use OCSP stapling\n"
            "6. Monitor certificate expiration"
        )

    def _general_response(self, prompt: str) -> str:
        """Generate general response."""
        return (
            f"NetworkCore received your networking query.\n"
            f"Query: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n"
            f"For specific help, try including keywords like 'rest', 'graphql', 'websocket', 'grpc', or 'tls'."
        )

    def _classify_task(self, prompt: str) -> str:
        """Classify the task type."""
        prompt_lower = prompt.lower()
        if "rest" in prompt_lower or "api" in prompt_lower:
            return "rest"
        elif "graphql" in prompt_lower:
            return "graphql"
        elif "websocket" in prompt_lower or "ws" in prompt_lower:
            return "websocket"
        elif "grpc" in prompt_lower:
            return "grpc"
        elif "tls" in prompt_lower or "ssl" in prompt_lower:
            return "tls"
        else:
            return "general"
