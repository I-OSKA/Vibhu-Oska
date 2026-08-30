"""
Vibhu-Oska AI-OS — FileSystemCore Specialist
Handles file system tasks: pathlib, os, shutil, watchdog, inotify, permissions.
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

log = logging.getLogger("FileSystemCore")


class FileSystemCore(BaseSpecialist):
    """
    File system specialist for Vibhu-Oska.
    
    Handles:
    - File and directory operations
    - Path manipulation
    - File monitoring
    - Permission management
    - Archive operations
    """

    def __init__(self) -> None:
        super().__init__(
            name="FileSystemCore",
            domain=SpecialistDomain.REAL_WORLD,
            capabilities=SpecialistCapabilities(
                domains=["file_system", "automation", "monitoring"],
                subdomains=["pathlib", "os", "shutil", "watchdog", "inotify"],
                max_complexity=6,
                estimated_latency_ms=150.0,
                requires_model=False,
                supported_formats=["text", "code"],
            ),
        )
        self._initialized = False

    async def initialize(self, **kwargs: Any) -> None:
        """Initialize FileSystemCore specialist."""
        self._initialized = True
        log.info("FileSystemCore initialized.")

    async def process(self, input_data: dict[str, Any]) -> SpecialistResult:
        """
        Process a file system task.
        
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
                "specialist": "FileSystemCore",
                "task_type": self._classify_task(prompt),
            },
        )

    def _generate_response(self, prompt: str) -> str:
        """Generate a response based on the prompt."""
        prompt_lower = prompt.lower()
        
        if "pathlib" in prompt_lower or "path" in prompt_lower:
            return self._pathlib_response(prompt)
        elif "permission" in prompt_lower or "chmod" in prompt_lower:
            return self._permission_response(prompt)
        elif "watch" in prompt_lower or "monitor" in prompt_lower:
            return self._monitoring_response(prompt)
        elif "archive" in prompt_lower or "zip" in prompt_lower or "tar" in prompt_lower:
            return self._archive_response(prompt)
        else:
            return self._general_response(prompt)

    def _pathlib_response(self, prompt: str) -> str:
        """Generate pathlib response."""
        return (
            "Python Pathlib:\n"
            "1. Use Path() for cross-platform paths\n"
            "2. / operator for path joining\n"
            "3. .stem/.suffix for file parts\n"
            "4. .glob()/.rglob() for pattern matching\n"
            "5. .mkdir(parents=True) for directories\n"
            "6. .read_text()/.write_text() for I/O"
        )

    def _permission_response(self, prompt: str) -> str:
        """Generate permission response."""
        return (
            "File Permissions:\n"
            "1. os.chmod() for permission changes\n"
            "2. stat module for permission constants\n"
            "3. Octal notation: 0o755, 0o644\n"
            "4. Use pathlib.Path.chmod() for modern code\n"
            "5. Check with os.access()\n"
            "6. Consider umask for default permissions"
        )

    def _monitoring_response(self, prompt: str) -> str:
        """Generate monitoring response."""
        return (
            "File Monitoring:\n"
            "1. watchdog: Cross-platform file events\n"
            "2. inotify: Linux-specific efficient monitoring\n"
            "3. Use FileSystemEventHandler for callbacks\n"
            "4. Implement debouncing for rapid changes\n"
            "5. Handle moved/created/deleted events\n"
            "6. Use Observer for persistent monitoring"
        )

    def _archive_response(self, prompt: str) -> str:
        """Generate archive response."""
        return (
            "Archive Operations:\n"
            "1. shutil.make_archive() for creation\n"
            "2. shutil.unpack_archive() for extraction\n"
            "3. zipfile for ZIP files\n"
            "4. tarfile for TAR/GZ files\n"
            "5. Use compression level parameters\n"
            "6. Handle large files with streaming"
        )

    def _general_response(self, prompt: str) -> str:
        """Generate general response."""
        return (
            f"FileSystemCore received your query about file systems.\n"
            f"Query: {prompt[:100]}{'...' if len(prompt) > 100 else ''}\n"
            f"For specific help, try including keywords like 'pathlib', 'permission', 'watch', or 'archive'."
        )

    def _classify_task(self, prompt: str) -> str:
        """Classify the task type."""
        prompt_lower = prompt.lower()
        if "pathlib" in prompt_lower or "path" in prompt_lower:
            return "pathlib"
        elif "permission" in prompt_lower or "chmod" in prompt_lower:
            return "permissions"
        elif "watch" in prompt_lower or "monitor" in prompt_lower:
            return "monitoring"
        elif "archive" in prompt_lower or "zip" in prompt_lower:
            return "archives"
        else:
            return "general"
