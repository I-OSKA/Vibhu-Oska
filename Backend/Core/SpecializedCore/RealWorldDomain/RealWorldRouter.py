"""
Vibhu-Oska AI-OS — RealWorldRouter Specialist
Routes real-world tasks to the appropriate specialist.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

from Shared.interfaces.BaseSpecialist import (
    BaseSpecialist,
    SpecialistDomain,
    SpecialistCapabilities,
    SpecialistResult,
)

log = logging.getLogger("RealWorldRouter")


class RealWorldRouter(BaseSpecialist):
    """
    Real-world domain router for Vibhu-Oska.
    
    Detects the task type and routes to the appropriate specialist.
    Falls back to general assistance if no specific specialist is available.
    """

    def __init__(self) -> None:
        super().__init__(
            name="RealWorldRouter",
            domain=SpecialistDomain.REAL_WORLD,
            capabilities=SpecialistCapabilities(
                domains=["system_admin", "data_analysis", "web_scraping", "file_system", "knowledge", "networking", "security", "cloud", "database"],
                subdomains=["excel", "web", "filesystem", "admin", "knowledge", "network", "security", "cloud", "database"],
                max_complexity=5,
                estimated_latency_ms=50.0,
                requires_model=False,
                supported_formats=["text", "code"],
            ),
        )
        self._specialists: dict[str, BaseSpecialist] = {}
        self._initialized = False

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize RealWorldRouter specialist."""
        self._initialized = True
        log.info("RealWorldRouter initialized.")

    def register_specialist(self, domain: str, specialist: BaseSpecialist) -> None:
        """Register a domain specialist."""
        self._specialists[domain.lower()] = specialist
        log.info(f"Registered real-world specialist: {domain} -> {specialist.name}")

    def detect_domain(self, prompt: str) -> Optional[str]:
        """Detect the domain from the prompt."""
        prompt_lower = prompt.lower()
        
        # Domain detection patterns
        patterns = {
            "excel": [r"\bexcel\b", r"\bspreadsheet\b", r"\bpivot\b", r"\bvba\b"],
            "web_scraping": [r"\bscrape\b", r"\bcrawl\b", r"\bbeautifulsoup\b", r"\bplaywright\b"],
            "file_system": [r"\bfile\b", r"\bdirectory\b", r"\bpath\b", r"\bwatch\b", r"\bpathlib\b"],
            "system_admin": [r"\bsystemd\b", r"\bdocker\b", r"\bkubernetes\b", r"\bfirewall\b"],
            "knowledge": [r"\bscience\b", r"\bmath\b", r"\bhistory\b", r"\bphilosophy\b", r"\bquantum\b"],
            "networking": [r"\bhttp\b", r"\brest\b", r"\bgraphql\b", r"\bwebsocket\b", r"\bgrpc\b"],
            "security": [r"\bsecurity\b", r"\bjwt\b", r"\boauth\b", r"\bencrypt\b", r"\bowasp\b"],
            "cloud": [r"\baws\b", r"\bgcp\b", r"\bazure\b", r"\bterraform\b", r"\blambda\b"],
            "database": [r"\bpostgresql\b", r"\bredis\b", r"\bmongodb\b", r"\bbackup\b", r"\bpostgres\b"],
        }
        
        for domain, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, prompt_lower):
                    return domain
        
        return None

    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process a real-world task by routing to the appropriate specialist.
        
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

        # Detect domain
        domain = self.detect_domain(prompt)
        
        if domain and domain in self._specialists:
            specialist = self._specialists[domain]
            log.info(f"Routing to {domain} specialist: {specialist.name}")
            return await specialist.process_with_tracking(input_data)
        
        # Fallback to general response
        return self._general_real_world_response(prompt)

    def _general_real_world_response(self, prompt: str) -> SpecialistResult:
        """Generate a general real-world response."""
        response = (
            "RealWorldRouter: I can help with real-world tasks.\n"
            "Detected query about general topics.\n\n"
            "Supported domains:\n"
            "- Excel, Web Scraping, File System\n"
            "- System Admin, Knowledge, Networking\n"
            "- Security, Cloud, Database\n\n"
            "Please specify the domain for more targeted assistance."
        )
        
        return SpecialistResult(
            success=True,
            output=response,
            confidence=0.5,
            metadata={
                "specialist": "RealWorldRouter",
                "detected_domain": None,
                "routing": "general",
            },
        )

    def get_registered_domains(self) -> list[str]:
        """Get list of registered domains."""
        return list(self._specialists.keys())
