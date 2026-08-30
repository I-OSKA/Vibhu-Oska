"""
Vibhu-Oska AI-OS — BashShellCore Specialist
Handles Shell/Bash specific tasks: bash/zsh/fish, awk, sed, grep, systemd, cron.
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

log = logging.getLogger("BashShellCore")


class BashShellCore(BaseSpecialist):
    """
    Shell/Bash specialist for Vibhu-Oska.
    
    Handles:
    - Bash/zsh/fish scripting
    - Text processing (awk, sed, grep, find)
    - System administration (systemd, cron)
    - Pipeline design
    - Process management
    - Environment configuration
    """

    def __init__(self) -> None:
        super().__init__(
            name="BashShellCore",
            domain=SpecialistDomain.CODING,
            capabilities=SpecialistCapabilities(
                domains=["code_generation", "code_review", "debugging", "automation"],
                subdomains=["bash", "shell", "awk", "sed", "grep", "systemd", "cron"],
                max_complexity=7,
                estimated_latency_ms=150.0,
                requires_model=False,
                supported_formats=["text", "code"],
            ),
        )
        self._initialized = False

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize BashShellCore specialist."""
        self._initialized = True
        log.info("BashShellCore initialized.")

    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process a Shell/Bash related task.
        
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
                "specialist": "BashShellCore",
                "language": "bash",
                "task_type": self._classify_task(prompt),
            },
        )

    def _generate_response(self, prompt: str) -> str:
        """Generate a response based on the prompt."""
        prompt_lower = prompt.lower()
        
        if "awk" in prompt_lower or "sed" in prompt_lower or "grep" in prompt_lower:
            return self._text_processing_response(prompt)
        elif "systemd" in prompt_lower or "service" in prompt_lower:
            return self._systemd_response(prompt)
        elif "cron" in prompt_lower or "schedule" in prompt_lower:
            return self._cron_response(prompt)
        elif "pipeline" in prompt_lower or "pipe" in prompt_lower:
            return self._pipeline_response(prompt)
        else:
            return self._general_response(prompt)

    def _text_processing_response(self, prompt: str) -> str:
        """Generate text processing response."""
        return (
            "Shell Text Processing:\n"
            "1. grep: pattern matching and filtering\n"
            "2. sed: stream editing and substitution\n"
            "3. awk: field processing and reporting\n"
            "4. find: file search with actions\n"
            "5. xargs: build command lines from stdin\n"
            "6. cut/paste: column-based processing"
        )

    def _systemd_response(self, prompt: str) -> str:
        """Generate systemd response."""
        return (
            "systemd Service Management:\n"
            "1. Create .service files in /etc/systemd/system/\n"
            "2. Use [Unit] for dependencies and description\n"
            "3. [Service] for execution and restart policies\n"
            "4. [Install] for target installation\n"
            "5. systemctl daemon-reload after changes\n"
            "6. Use journalctl for log viewing"
        )

    def _cron_response(self, prompt: str) -> str:
        """Generate cron response."""
        return (
            "Cron Job Scheduling:\n"
            "1. Format: minute hour day month weekday command\n"
            "2. Use crontab -e for editing\n"
            "3. Special strings: @reboot, @daily, @weekly\n"
            "4. Redirect output for logging\n"
            "5. Use absolute paths in cron jobs\n"
            "6. Consider anacron for intermittent systems"
        )

    def _pipeline_response(self, prompt: str) -> str:
        """Generate pipeline response."""
        return (
            "Shell Pipeline Design:\n"
            "1. Chain commands with pipes (|)\n"
            "2. Use tee for branching output\n"
            "3. Process substitution for parallel ops\n"
            "4. Use xargs for argument passing\n"
            "5. Implement proper error handling\n"
            "6. Quote variables to prevent word splitting"
        )

    def _general_response(self, prompt: str) -> str:
        """Generate general response."""
        return (
            f"BashShellCore received your query about Shell/Bash.\n"
            f"Query: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n"
            f"For specific help, try including keywords like 'awk', 'systemd', 'cron', or 'pipeline'."
        )

    def _classify_task(self, prompt: str) -> str:
        """Classify the task type."""
        prompt_lower = prompt.lower()
        if "awk" in prompt_lower or "sed" in prompt_lower or "grep" in prompt_lower:
            return "text_processing"
        elif "systemd" in prompt_lower or "service" in prompt_lower:
            return "systemd"
        elif "cron" in prompt_lower or "schedule" in prompt_lower:
            return "cron"
        elif "pipeline" in prompt_lower or "pipe" in prompt_lower:
            return "pipeline"
        else:
            return "general"
