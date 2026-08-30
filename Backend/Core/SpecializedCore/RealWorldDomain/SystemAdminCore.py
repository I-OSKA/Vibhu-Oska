"""
Vibhu-Oska AI-OS — SystemAdminCore Specialist
Handles system administration tasks: systemd, Docker, k8s, networking, firewall.
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

log = logging.getLogger("SystemAdminCore")


class SystemAdminCore(BaseSpecialist):
    """
    System administration specialist for Vibhu-Oska.
    
    Handles:
    - Service management (systemd)
    - Container orchestration (Docker, Kubernetes)
    - Network configuration
    - Firewall rules
    - Log analysis
    """

    def __init__(self) -> None:
        super().__init__(
            name="SystemAdminCore",
            domain=SpecialistDomain.REAL_WORLD,
            capabilities=SpecialistCapabilities(
                domains=["system_admin", "devops", "networking"],
                subdomains=["systemd", "docker", "kubernetes", "firewall", "ssh"],
                max_complexity=8,
                estimated_latency_ms=200.0,
                requires_model=False,
                supported_formats=["text", "code"],
            ),
        )
        self._initialized = False

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize SystemAdminCore specialist."""
        self._initialized = True
        log.info("SystemAdminCore initialized.")

    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process a system administration task.
        
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
                "specialist": "SystemAdminCore",
                "task_type": self._classify_task(prompt),
            },
        )

    def _generate_response(self, prompt: str) -> str:
        """Generate a response based on the prompt."""
        prompt_lower = prompt.lower()
        
        if "systemd" in prompt_lower or "service" in prompt_lower:
            return self._systemd_response(prompt)
        elif "docker" in prompt_lower or "container" in prompt_lower:
            return self._docker_response(prompt)
        elif "kubernetes" in prompt_lower or "k8s" in prompt_lower:
            return self._kubernetes_response(prompt)
        elif "firewall" in prompt_lower or "iptables" in prompt_lower:
            return self._firewall_response(prompt)
        else:
            return self._general_response(prompt)

    def _systemd_response(self, prompt: str) -> str:
        """Generate systemd response."""
        return (
            "systemd Administration:\n"
            "1. systemctl start/stop/restart/status\n"
            "2. journalctl for log viewing\n"
            "3. Create .service files in /etc/systemd/system/\n"
            "4. Use WantedBy for boot startup\n"
            "5. Implement restart policies\n"
            "6. Use timers for scheduled tasks"
        )

    def _docker_response(self, prompt: str) -> str:
        """Generate Docker response."""
        return (
            "Docker Administration:\n"
            "1. Multi-stage builds for efficiency\n"
            "2. Use .dockerignore to exclude files\n"
            "3. Implement health checks\n"
            "4. Use Docker Compose for multi-container\n"
            "5. Manage volumes for persistent data\n"
            "6. Implement proper logging drivers"
        )

    def _kubernetes_response(self, prompt: str) -> str:
        """Generate Kubernetes response."""
        return (
            "Kubernetes Administration:\n"
            "1. Use declarative YAML manifests\n"
            "2. Implement resource limits/requests\n"
            "3. Use namespaces for isolation\n"
            "4. Implement liveness/readiness probes\n"
            "5. Use ConfigMaps/Secrets for configuration\n"
            "6. Implement rolling updates"
        )

    def _firewall_response(self, prompt: str) -> str:
        """Generate firewall response."""
        return (
            "Firewall Configuration:\n"
            "1. ufw for Ubuntu/Debian simplicity\n"
            "2. firewalld for RHEL/CentOS\n"
            "3. iptables for low-level control\n"
            "4. Implement default deny policies\n"
            "5. Allow only necessary ports\n"
            "6. Log dropped packets for debugging"
        )

    def _general_response(self, prompt: str) -> str:
        """Generate general response."""
        return (
            f"SystemAdminCore received your query about system administration.\n"
            f"Query: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n"
            f"For specific help, try including keywords like 'systemd', 'docker', 'kubernetes', or 'firewall'."
        )

    def _classify_task(self, prompt: str) -> str:
        """Classify the task type."""
        prompt_lower = prompt.lower()
        if "systemd" in prompt_lower or "service" in prompt_lower:
            return "systemd"
        elif "docker" in prompt_lower or "container" in prompt_lower:
            return "docker"
        elif "kubernetes" in prompt_lower or "k8s" in prompt_lower:
            return "kubernetes"
        elif "firewall" in prompt_lower or "iptables" in prompt_lower:
            return "firewall"
        else:
            return "general"
