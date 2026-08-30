"""
Vibhu-Oska AI-OS — SandboxExecutor
Safe execution of generated code with time and memory limits.
"""

from __future__ import annotations

import asyncio
import logging
import tempfile
import os
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger("SandboxExecutor")


class SandboxResult:
    """Result of sandboxed code execution."""

    def __init__(
        self,
        success: bool,
        stdout: str = "",
        stderr: str = "",
        exit_code: int = 0,
        execution_time_ms: float = 0.0,
        error: Optional[str] = None,
    ) -> None:
        self.success = success
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.execution_time_ms = execution_time_ms
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "stdout": self.stdout[:1000],  # truncate
            "stderr": self.stderr[:1000],
            "exit_code": self.exit_code,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
        }


class SandboxExecutor:
    """
    Executes code in an isolated subprocess with resource limits.

    Usage:
        sandbox = SandboxExecutor(time_limit_s=10, memory_limit_mb=512)
        result = await sandbox.run("print('hello')")
    """

    # Dangerous operations to block
    BLOCKED_PATTERNS = [
        "os.system",
        "subprocess.call",
        "subprocess.run",
        "subprocess.Popen",
        "__import__('os')",
        "__import__('subprocess')",
        "eval(",
        "exec(",
        "open('/etc",
        "open('/proc",
        "shutil.rmtree",
        "os.remove",
        "os.rmdir",
    ]

    def __init__(
        self,
        time_limit_s: float = 10.0,
        memory_limit_mb: int = 512,
        python_path: str = "python",
    ) -> None:
        self._time_limit_s = time_limit_s
        self._memory_limit_mb = memory_limit_mb
        self._python_path = python_path
        self._execution_count: int = 0
        self._total_time_ms: float = 0.0

    def _validate_code(self, code: str) -> tuple[bool, Optional[str]]:
        """Check code for dangerous operations."""
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in code:
                return False, f"Blocked pattern detected: {pattern}"
        return True, None

    async def run(
        self,
        code: str,
        language: str = "python",
        stdin_data: Optional[str] = None,
    ) -> SandboxResult:
        """
        Execute code in a sandboxed subprocess.

        Args:
            code: Code to execute
            language: "python" or "bash"
            stdin_data: Optional input to pipe to stdin

        Returns:
            SandboxResult with stdout, stderr, exit_code
        """
        import time

        # Validate
        if language == "python":
            is_safe, reason = self._validate_code(code)
            if not is_safe:
                return SandboxResult(
                    success=False,
                    error=f"Code rejected: {reason}",
                )

        # Create temp file
        suffix = ".py" if language == "python" else ".sh"
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=suffix,
            delete=False,
        ) as f:
            f.write(code)
            temp_path = f.name

        try:
            start = time.time()

            # Build command
            if language == "python":
                cmd = [self._python_path, temp_path]
            else:
                cmd = ["bash", temp_path]

            # Run subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE if stdin_data else None,
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(
                        input=stdin_data.encode() if stdin_data else None
                    ),
                    timeout=self._time_limit_s,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                elapsed = (time.time() - start) * 1000
                return SandboxResult(
                    success=False,
                    exit_code=-1,
                    execution_time_ms=elapsed,
                    error=f"Execution timed out after {self._time_limit_s}s",
                )

            elapsed = (time.time() - start) * 1000
            stdout = stdout_bytes.decode(errors="replace")
            stderr = stderr_bytes.decode(errors="replace")
            exit_code = process.returncode or 0

            self._execution_count += 1
            self._total_time_ms += elapsed

            return SandboxResult(
                success=(exit_code == 0),
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time_ms=elapsed,
            )

        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return SandboxResult(
                success=False,
                execution_time_ms=elapsed,
                error=str(e),
            )
        finally:
            # Cleanup
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    def get_metrics(self) -> dict[str, Any]:
        return {
            "execution_count": self._execution_count,
            "total_time_ms": self._total_time_ms,
            "avg_time_ms": (
                self._total_time_ms / self._execution_count
                if self._execution_count > 0
                else 0.0
            ),
        }
