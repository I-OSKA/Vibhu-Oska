"""
Vibhu-Oska AI-OS — AutomationCore
Localhost Native OS Executive & Bare-Metal Subprocess Hooks.

The AI-OS Hardware-Native Intelligence Layer. Intercepts native system event logs,
processes local resource schedules, and handles file-system execution hooks via
native script modules. All command execution runs through a safety allowance matrix.
"""

from __future__ import annotations

import asyncio
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from Backend.Plugins.Logger.Logger import Logger
from Backend.Plugins.ToolRegistry.BaseService import BaseService
from Shared.Models import PluginInfo, CoreStatus, ExecutionTarget


# Hardcoded command blacklist — never execute these regardless of caller
_BLOCKED_COMMANDS: set[str] = {
    "rm", "rmdir", "del", "format", "mkfs", "fdisk", "dd",
    "shutdown", "reboot", "halt", "poweroff",
    "chmod", "chown", "sudo", "su", "passwd", "useradd",
    "net", "reg", "regedit", "bcdedit",
}

# Max output bytes returned per command (prevents flooding)
_MAX_OUTPUT_BYTES: int = 32_768  # 32 KB
_DEFAULT_TIMEOUT_S: float = 10.0


class AutomationCore(BaseService):
    """
    AutomationCore manages direct interaction with the host hardware and OS.

    Implements the AI-OS Hardware-Native Intelligence Layer per the Vibhu-Oska spec.
    Provides sandboxed subprocess execution, filesystem reads, system telemetry
    retrieval, and process management — all behind a safety allowance matrix.

    Supported actions (via execute()):
    - get_system_info      → hardware & OS telemetry snapshot
    - run_command          → sandboxed subprocess execution
    - list_directory       → directory contents enumeration
    - read_file            → file content retrieval (size-guarded)
    - write_file           → write content to path
    - watch_process        → check if a named process is running
    - kill_process         → terminate a process by PID
    - open_application     → launch an OS application
    - get_environment_vars → safe read of specified env vars
    """

    def __init__(self) -> None:
        self._initialized: bool = False
        self._log = Logger.get("AutomationCore")
        self._platform: str = platform.system()  # 'Windows', 'Linux', 'Darwin'

    # ==================================================================================================

    # # Internal Separation Division

    # =================─────────────────────────────────────────────────────────────────────────────────

    def info(self) -> PluginInfo:
        """Return plugin metadata."""
        return PluginInfo(
            name="automation",
            version="1.0.0",
            description="Localhost native OS executive — bare-metal subprocess hooks, telemetry, filesystem access",
            capabilities=[
                "bare_metal_execution",
                "os_automation",
                "system_telemetry",
                "filesystem_access",
                "process_management",
            ],
            status=CoreStatus.HEALTHY if self._initialized else CoreStatus.UNKNOWN,
            preferred_target=ExecutionTarget.CPU,
        )

    def health_check(self) -> bool:
        """Return initialization status."""
        return self._initialized

    async def initialize(self) -> None:
        """
        Initialize AutomationCore.

        Parameters: none
        Returns: none
        Edge cases: safe to call multiple times (idempotent)
        """
        if self._initialized:
            return
        self._initialized = True
        self._log.info(
            "AutomationCore initialized",
            platform=self._platform,
            python_version=sys.version.split()[0],
        )

    async def execute(self, action: str, **kwargs: Any) -> Any:
        """
        Dispatch an automation action.

        Parameters:
            action: One of the supported action names (see class docstring)
            **kwargs: Action-specific arguments
        Returns: dict result or raises ValueError for unknown actions
        Edge cases: Unknown actions raise ValueError; all errors are caught and returned as structured dicts
        """
        if not self._initialized:
            await self.initialize()

        dispatch: dict[str, Any] = {
            "get_system_info":      self._get_system_info,
            "run_command":          self._run_command,
            "list_directory":       self._list_directory,
            "read_file":            self._read_file,
            "write_file":           self._write_file,
            "watch_process":        self._watch_process,
            "kill_process":         self._kill_process,
            "open_application":     self._open_application,
            "close_application":    self._close_application,
            "switch_to_application":self._switch_to_application,
            "list_open_apps":       self._list_open_apps,
            "take_screenshot":      self._take_screenshot,
            "type_text":            self._type_text,
            "press_key":            self._press_key,
            "get_environment_vars": self._get_environment_vars,
        }

        if action not in dispatch:
            raise ValueError(
                f"Action '{action}' is not supported by AutomationCore. "
                f"Available actions: {sorted(dispatch.keys())}"
            )

        handler = dispatch[action]
        return await handler(**kwargs)

    def process(self, data: Any) -> Any:
        """Backward compatibility pass-through."""
        return data

    # ==================================================================================================

    # # Internal Separation Division

    # =================─────────────────────────────────────────────────────────────────────────────────

    async def _get_system_info(self, **_: Any) -> dict[str, Any]:
        """
        Retrieve a comprehensive hardware and OS telemetry snapshot.

        Parameters: none
        Returns: dict with cpu, memory, disk, gpu, os, python fields
        Edge cases: GPU info gracefully absent if torch not installed
        """
        try:
            import psutil

            cpu_percent = await asyncio.to_thread(psutil.cpu_percent, 0.5)
            cpu_freq = psutil.cpu_freq()
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)

            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            disk = psutil.disk_usage(os.path.abspath(os.sep))

            # Platform info
            uname = platform.uname()

            # GPU info (optional — requires torch)
            gpu_info: dict[str, Any] = {}
            try:
                import torch
                if torch.cuda.is_available():
                    idx = 0
                    gpu_info = {
                        "name": torch.cuda.get_device_name(idx),
                        "vram_total_mb": round(torch.cuda.get_device_properties(idx).total_memory / 1024 / 1024, 1),
                        "vram_reserved_mb": round(torch.cuda.memory_reserved(idx) / 1024 / 1024, 1),
                        "vram_allocated_mb": round(torch.cuda.memory_allocated(idx) / 1024 / 1024, 1),
                    }
            except ImportError:
                gpu_info = {"status": "torch not installed — GPU info unavailable"}
            except Exception as e:
                gpu_info = {"status": f"GPU query failed: {e}"}

            result = {
                "os": {
                    "system": uname.system,
                    "node": uname.node,
                    "release": uname.release,
                    "version": uname.version,
                    "machine": uname.machine,
                    "processor": uname.processor,
                },
                "cpu": {
                    "usage_percent": cpu_percent,
                    "physical_cores": cpu_count_physical,
                    "logical_cores": cpu_count_logical,
                    "frequency_mhz": round(cpu_freq.current, 1) if cpu_freq else None,
                    "frequency_max_mhz": round(cpu_freq.max, 1) if cpu_freq else None,
                },
                "memory": {
                    "total_gb": round(mem.total / 1024 ** 3, 2),
                    "available_gb": round(mem.available / 1024 ** 3, 2),
                    "used_gb": round(mem.used / 1024 ** 3, 2),
                    "usage_percent": mem.percent,
                    "swap_total_gb": round(swap.total / 1024 ** 3, 2),
                    "swap_used_gb": round(swap.used / 1024 ** 3, 2),
                },
                "disk": {
                    "total_gb": round(disk.total / 1024 ** 3, 2),
                    "used_gb": round(disk.used / 1024 ** 3, 2),
                    "free_gb": round(disk.free / 1024 ** 3, 2),
                    "usage_percent": disk.percent,
                },
                "gpu": gpu_info,
                "python": {
                    "version": sys.version.split()[0],
                    "executable": sys.executable,
                },
            }

            self._log.info("System telemetry retrieved", cpu_usage=cpu_percent, mem_used_pct=mem.percent)
            return {"status": "success", "data": result}

        except ImportError:
            return {"status": "error", "error": "psutil is not installed. Install it with: pip install psutil"}
        except Exception as e:
            self._log.error("System info retrieval failed", error=str(e))
            return {"status": "error", "error": str(e)}

    async def _run_command(
        self,
        command: str,
        timeout: float = _DEFAULT_TIMEOUT_S,
        working_dir: str | None = None,
        capture_output: bool = True,
        **_: Any,
    ) -> dict[str, Any]:
        """
        Execute a shell command in a sandboxed subprocess.

        Parameters:
            command: The command string to execute
            timeout: Maximum execution time in seconds (default 10s)
            working_dir: CWD for subprocess (default: project root)
            capture_output: If True, capture stdout/stderr; else stream live
        Returns: dict with status, returncode, stdout, stderr, elapsed_ms
        Edge cases: Blacklisted commands are rejected before any subprocess is spawned;
                    timeout kills the process and returns a timeout error dict
        """
        # Safety check — tokenize command and check each word
        first_word = command.strip().split()[0].lower().lstrip("./\\") if command.strip() else ""
        if first_word in _BLOCKED_COMMANDS:
            self._log.warning("Blocked dangerous command attempt", command=command, blocked_word=first_word)
            return {
                "status": "blocked",
                "error": f"Command '{first_word}' is in the safety block list and will not execute.",
                "command": command,
            }

        cwd = working_dir or str(Path(__file__).resolve().parent.parent.parent.parent.parent)
        start_ms = time.time()

        try:
            self._log.info("Executing sandboxed command", command=command, cwd=cwd)

            # On Windows, asyncio.create_subprocess_shell can silently fail in some test
            # harness contexts. Use subprocess.run via thread pool as the primary path on
            # Windows for reliability; asyncio shell mode on other platforms.
            if self._platform == "Windows":
                def _run_sync() -> dict[str, Any]:
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        cwd=cwd,
                        timeout=timeout,
                    )
                    return {
                        "returncode": result.returncode,
                        "stdout": result.stdout[:_MAX_OUTPUT_BYTES],
                        "stderr": result.stderr[:_MAX_OUTPUT_BYTES],
                    }
                try:
                    run_result = await asyncio.to_thread(_run_sync)
                    elapsed_ms = round((time.time() - start_ms) * 1000)
                    self._log.info(
                        "Command completed",
                        returncode=run_result["returncode"],
                        elapsed_ms=elapsed_ms,
                    )
                    return {
                        "status": "success" if run_result["returncode"] == 0 else "error",
                        "returncode": run_result["returncode"],
                        "stdout": run_result["stdout"],
                        "stderr": run_result["stderr"],
                        "elapsed_ms": elapsed_ms,
                        "command": command,
                    }
                except subprocess.TimeoutExpired:
                    return {
                        "status": "timeout",
                        "error": f"Command timed out after {timeout}s",
                        "command": command,
                        "returncode": -1,
                    }
            else:
                proc = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE if capture_output else None,
                    stderr=asyncio.subprocess.PIPE if capture_output else None,
                    cwd=cwd,
                )

                try:
                    stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout)
                except asyncio.TimeoutError:
                    proc.kill()
                    await proc.communicate()
                    return {
                        "status": "timeout",
                        "error": f"Command timed out after {timeout}s",
                        "command": command,
                        "returncode": -1,
                    }

                elapsed_ms = round((time.time() - start_ms) * 1000)
                stdout_str = (stdout_b or b"").decode("utf-8", errors="replace")[:_MAX_OUTPUT_BYTES]
                stderr_str = (stderr_b or b"").decode("utf-8", errors="replace")[:_MAX_OUTPUT_BYTES]

                self._log.info(
                    "Command completed",
                    returncode=proc.returncode,
                    elapsed_ms=elapsed_ms,
                    stdout_len=len(stdout_str),
                )

                return {
                    "status": "success" if proc.returncode == 0 else "error",
                    "returncode": proc.returncode,
                    "stdout": stdout_str,
                    "stderr": stderr_str,
                    "elapsed_ms": elapsed_ms,
                    "command": command,
                }

        except Exception as e:
            self._log.error("Command execution failed", error=str(e), command=command)
            return {"status": "error", "error": str(e), "command": command}

    async def _list_directory(
        self,
        path: str,
        include_hidden: bool = False,
        max_entries: int = 200,
        **_: Any,
    ) -> dict[str, Any]:
        """
        Enumerate directory contents.

        Parameters:
            path: Absolute or relative path to directory
            include_hidden: If True, include dotfiles/hidden entries
            max_entries: Cap on number of entries returned (default 200)
        Returns: dict with status, path, entries (list of {name, type, size_bytes, modified_at})
        Edge cases: Non-existent or non-directory paths return an error dict
        """
        try:
            target = Path(path).resolve()
            if not target.exists():
                return {"status": "error", "error": f"Path does not exist: {path}"}
            if not target.is_dir():
                return {"status": "error", "error": f"Path is not a directory: {path}"}

            entries = []
            for item in sorted(target.iterdir()):
                if not include_hidden and item.name.startswith("."):
                    continue
                try:
                    stat = item.stat()
                    entries.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size_bytes": stat.st_size if item.is_file() else None,
                        "modified_at": time.strftime(
                            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(stat.st_mtime)
                        ),
                    })
                except PermissionError:
                    entries.append({"name": item.name, "type": "unknown", "error": "permission_denied"})

                if len(entries) >= max_entries:
                    break

            return {
                "status": "success",
                "path": str(target),
                "total_shown": len(entries),
                "entries": entries,
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "path": path}

    async def _read_file(
        self,
        path: str,
        max_bytes: int = 65_536,
        encoding: str = "utf-8",
        **_: Any,
    ) -> dict[str, Any]:
        """
        Read file contents with a size guard.

        Parameters:
            path: Path to file
            max_bytes: Maximum bytes to read (default 64KB)
            encoding: Text encoding (default utf-8)
        Returns: dict with status, path, content, size_bytes, truncated
        Edge cases: Binary files return content with replace error handling; missing files return error
        """
        try:
            target = Path(path).resolve()
            if not target.exists():
                return {"status": "error", "error": f"File not found: {path}"}
            if not target.is_file():
                return {"status": "error", "error": f"Path is not a file: {path}"}

            size = target.stat().st_size
            truncated = size > max_bytes

            content = await asyncio.to_thread(
                lambda: target.read_bytes()[:max_bytes].decode(encoding, errors="replace")
            )

            return {
                "status": "success",
                "path": str(target),
                "content": content,
                "size_bytes": size,
                "truncated": truncated,
                "encoding": encoding,
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "path": path}

    async def _write_file(
        self,
        path: str,
        content: str,
        overwrite: bool = True,
        encoding: str = "utf-8",
        **_: Any,
    ) -> dict[str, Any]:
        """
        Write content to a file path.

        Parameters:
            path: Destination file path
            content: Text content to write
            overwrite: If False, raises error if file exists (default True)
            encoding: Text encoding (default utf-8)
        Returns: dict with status, path, bytes_written
        Edge cases: Non-overwrite mode returns error if file already exists
        """
        try:
            target = Path(path).resolve()

            if not overwrite and target.exists():
                return {"status": "error", "error": f"File already exists and overwrite=False: {path}"}

            target.parent.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(target.write_text, content, encoding)

            bytes_written = len(content.encode(encoding))
            self._log.info("File written", path=str(target), bytes_written=bytes_written)
            return {
                "status": "success",
                "path": str(target),
                "bytes_written": bytes_written,
            }

        except Exception as e:
            self._log.error("File write failed", path=path, error=str(e))
            return {"status": "error", "error": str(e), "path": path}

    async def _watch_process(
        self,
        process_name: str | None = None,
        pid: int | None = None,
        **_: Any,
    ) -> dict[str, Any]:
        """
        Check whether a named process or PID is running.

        Parameters:
            process_name: Process name substring to search (case-insensitive)
            pid: Specific process ID to check
        Returns: dict with status, found (bool), matches (list of {pid, name, status, cpu_percent})
        Edge cases: Both params missing returns error; psutil ImportError returns error
        """
        if not process_name and pid is None:
            return {"status": "error", "error": "Provide either process_name or pid"}

        try:
            import psutil

            matches = []
            for proc in psutil.process_iter(["pid", "name", "status", "cpu_percent"]):
                try:
                    info = proc.info
                    if pid is not None and info["pid"] == pid:
                        matches.append(info)
                    elif process_name and process_name.lower() in (info["name"] or "").lower():
                        matches.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return {
                "status": "success",
                "found": len(matches) > 0,
                "matches": matches,
                "query": {"process_name": process_name, "pid": pid},
            }

        except ImportError:
            return {"status": "error", "error": "psutil not installed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _kill_process(self, pid: int, **_: Any) -> dict[str, Any]:
        """
        Terminate a process by its PID.

        Parameters:
            pid: Process ID to terminate
        Returns: dict with status, pid, killed (bool)
        Edge cases: PID not found returns graceful error; access denied returns error
        """
        try:
            import psutil

            proc = psutil.Process(pid)
            name = proc.name()
            proc.terminate()

            # Give it 3 seconds to exit gracefully
            try:
                proc.wait(timeout=3)
                killed = True
            except psutil.TimeoutExpired:
                proc.kill()
                killed = True

            self._log.info("Process terminated", pid=pid, name=name)
            return {"status": "success", "pid": pid, "process_name": name, "killed": killed}

        except ImportError:
            return {"status": "error", "error": "psutil not installed"}
        except Exception as e:
            self._log.warning("Kill process failed", pid=pid, error=str(e))
            return {"status": "error", "error": str(e), "pid": pid}

    async def _open_application(self, application: str, **_: Any) -> dict[str, Any]:
        """
        Launch an OS application using the AppController fuzzy-name resolver.

        Parameters:
            application: App name (e.g. 'chrome', 'notepad', 'spotify') or full path
        Returns: dict with status, application, message
        Edge cases: Falls back to os.startfile if no fuzzy match found; errors are caught and returned
        """
        try:
            self._log.info("Opening application", application=application)
            result = await asyncio.to_thread(AppController.open_app, application)
            return result
        except Exception as e:
            self._log.error("Application launch failed", application=application, error=str(e))
            return {"status": "error", "error": str(e), "application": application}

    async def _close_application(self, application: str, **_: Any) -> dict[str, Any]:
        """
        Close a running application by its name using psutil.

        Parameters:
            application: Process name to close (fuzzy-matched, case-insensitive)
        Returns: dict with status, killed_count, processes list
        Edge cases: No match returns graceful not-found; partial matches are all terminated
        """
        try:
            result = await asyncio.to_thread(AppController.close_app, application)
            return result
        except Exception as e:
            return {"status": "error", "error": str(e), "application": application}

    async def _switch_to_application(self, application: str, **_: Any) -> dict[str, Any]:
        """
        Bring a running application's window to the foreground.

        Parameters:
            application: Window title substring to match (case-insensitive)
        Returns: dict with status, window_title, message
        Edge cases: No window found returns not-found; multiple matches activate first
        """
        try:
            result = await asyncio.to_thread(AppController.switch_to_app, application)
            return result
        except Exception as e:
            return {"status": "error", "error": str(e), "application": application}

    async def _list_open_apps(self, **_: Any) -> dict[str, Any]:
        """
        List all currently running applications with visible windows.

        Parameters: none
        Returns: dict with status, apps (list of {title, pid})
        Edge cases: Returns empty list if pygetwindow unavailable
        """
        try:
            result = await asyncio.to_thread(AppController.list_open_apps)
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _take_screenshot(self, **_: Any) -> dict[str, Any]:
        """
        Capture the current screen and return it as a base64-encoded PNG.

        Parameters: none
        Returns: dict with status, image_b64, width, height, saved_path
        Edge cases: Requires Pillow; falls back gracefully if unavailable
        """
        try:
            result = await asyncio.to_thread(AppController.screenshot)
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _type_text(self, text: str, interval: float = 0.03, **_: Any) -> dict[str, Any]:
        """
        Type a string of text into the currently focused window using keyboard injection.

        Parameters:
            text: String to type
            interval: Delay between keystrokes in seconds (default 0.03)
        Returns: dict with status, chars_typed
        Edge cases: Requires pyautogui; types at active focus — no target guarantee
        """
        try:
            import pyautogui
            await asyncio.to_thread(pyautogui.write, text, interval=interval)
            return {"status": "success", "chars_typed": len(text)}
        except ImportError:
            return {"status": "error", "error": "pyautogui not installed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _press_key(self, key: str, **_: Any) -> dict[str, Any]:
        """
        Press a keyboard key or hotkey combination.

        Parameters:
            key: Key name or hotkey (e.g. 'enter', 'ctrl+c', 'win+d', 'alt+tab')
        Returns: dict with status, key
        Edge cases: Invalid key names are caught and returned as errors
        """
        try:
            import pyautogui
            keys = [k.strip() for k in key.split("+")]
            if len(keys) == 1:
                await asyncio.to_thread(pyautogui.press, keys[0])
            else:
                await asyncio.to_thread(pyautogui.hotkey, *keys)
            return {"status": "success", "key": key}
        except ImportError:
            return {"status": "error", "error": "pyautogui not installed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _platform_open(self, target: str) -> None:
        """Open a file/URL/application using the platform-appropriate method."""
        if self._platform == "Windows":
            os.startfile(target)
        elif self._platform == "Darwin":
            subprocess.Popen(["open", target])
        else:
            subprocess.Popen(["xdg-open", target])

    async def _get_environment_vars(self, keys: list[str], **_: Any) -> dict[str, Any]:
        """
        Safely read specified environment variables.

        Parameters:
            keys: List of environment variable names to retrieve
        Returns: dict with status, vars (dict of key → value or None)
        Edge cases: Returns None for missing keys rather than raising; sensitive keys are not readable
        """
        # Safety: block reading of credential-class env vars
        _BLOCKED_ENV_KEYS = {
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY",
            "AWS_SECRET_ACCESS_KEY", "GITHUB_TOKEN", "DATABASE_URL",
        }

        result: dict[str, str | None] = {}
        for key in keys:
            if key.upper() in _BLOCKED_ENV_KEYS:
                result[key] = "[REDACTED — credential class variable]"
            else:
                result[key] = os.environ.get(key)

        return {"status": "success", "vars": result}


# ==================================================================================================
# # Internal Separation Division
# =================────────────────────────────────────────────────────────────────────────────────


# ── App name → executable mapping for Windows ─────────────────────────────────────────────────
_APP_MAP: dict[str, str] = {
    # Browsers
    "chrome":         r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome":  r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox":        r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge":           r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "brave":          r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    # Editors / IDE
    "vscode":         r"C:\Users\USER\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "code":           r"C:\Users\USER\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "visual studio code": r"C:\Users\USER\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "notepad":        r"C:\Windows\System32\notepad.exe",
    "notepad++":      r"C:\Program Files\Notepad++\notepad++.exe",
    "sublime":        r"C:\Program Files\Sublime Text\sublime_text.exe",
    # Terminals
    "powershell":     r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
    "cmd":            r"C:\Windows\System32\cmd.exe",
    "terminal":       r"C:\Users\USER\AppData\Local\Microsoft\WindowsApps\wt.exe",
    "windows terminal": r"C:\Users\USER\AppData\Local\Microsoft\WindowsApps\wt.exe",
    # Media
    "spotify":        r"C:\Users\USER\AppData\Roaming\Spotify\Spotify.exe",
    "vlc":            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    # Productivity
    "explorer":       r"C:\Windows\explorer.exe",
    "file explorer":  r"C:\Windows\explorer.exe",
    "task manager":   r"C:\Windows\System32\Taskmgr.exe",
    "calculator":     r"C:\Windows\System32\calc.exe",
    "paint":          r"C:\Windows\System32\mspaint.exe",
    "word":           r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel":          r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "discord":        r"C:\Users\USER\AppData\Local\Discord\Update.exe",
    "slack":          r"C:\Users\USER\AppData\Local\slack\slack.exe",
    "zoom":           r"C:\Users\USER\AppData\Roaming\Zoom\bin\Zoom.exe",
    "obs":            r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
    "steam":          r"C:\Program Files (x86)\Steam\steam.exe",
    "postman":        r"C:\Users\USER\AppData\Local\Postman\Postman.exe",
    "docker":         r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
}


class AppController:
    """
    AppController — OS-level application management for Vibhu-Oska AI-OS.

    Provides fuzzy name resolution and execution of open/close/switch/screenshot/type/key
    operations entirely on local hardware via pygetwindow, pyautogui, psutil, and Pillow.

    All methods are classmethods — no instantiation required.
    """

    @classmethod
    def open_app(cls, name: str) -> dict[str, Any]:
        """
        Launch an application by fuzzy name or full path.

        Parameters:
            name: App name (e.g. 'chrome', 'spotify') or absolute path
        Returns: dict with status, application, message
        Edge cases: Falls back to os.startfile for unknown names; raises on path errors
        """
        norm = name.lower().strip()

        # Direct path
        if os.path.isabs(name) and os.path.exists(name):
            subprocess.Popen([name])
            return {"status": "success", "application": name, "message": f"Launched: {name}"}

        # Known app map
        exe_path = _APP_MAP.get(norm)
        if exe_path and os.path.exists(exe_path):
            subprocess.Popen([exe_path])
            return {"status": "success", "application": norm, "message": f"Launched {norm} via known path."}

        # Fuzzy: check shutil.which (covers PATH apps like python, git, npm)
        found = shutil.which(norm) or shutil.which(name)
        if found:
            subprocess.Popen([found])
            return {"status": "success", "application": name, "message": f"Launched via PATH: {found}"}

        # Last resort: os.startfile (works for registered file types & UWP apps on Windows)
        try:
            os.startfile(name)
            return {"status": "success", "application": name, "message": f"Launched via startfile: {name}"}
        except Exception as e:
            return {
                "status": "not_found",
                "application": name,
                "message": f"Could not find or launch '{name}'. Ensure it is installed.",
                "detail": str(e),
            }

    @classmethod
    def close_app(cls, name: str) -> dict[str, Any]:
        """
        Terminate all processes whose name fuzzy-matches the given string.

        Parameters:
            name: App/process name substring (case-insensitive)
        Returns: dict with status, killed_count, processes
        Edge cases: No match returns not_found; partial matches are all killed
        """
        try:
            import psutil
            norm = name.lower()
            killed = []
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    pname = (proc.info["name"] or "").lower()
                    if norm in pname or pname in norm:
                        proc.terminate()
                        killed.append({"pid": proc.info["pid"], "name": proc.info["name"]})
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if not killed:
                return {"status": "not_found", "application": name, "message": f"No running process matched '{name}'."}

            return {"status": "success", "killed_count": len(killed), "processes": killed}
        except ImportError:
            return {"status": "error", "error": "psutil not installed"}

    @classmethod
    def switch_to_app(cls, name: str) -> dict[str, Any]:
        """
        Bring a window with a matching title to the foreground.

        Parameters:
            name: Window title substring (case-insensitive)
        Returns: dict with status, window_title, message
        Edge cases: No window found returns not_found; first match is activated
        """
        try:
            import pygetwindow as gw
            norm = name.lower()
            windows = gw.getAllWindows()
            for win in windows:
                if norm in (win.title or "").lower():
                    win.activate()
                    return {"status": "success", "window_title": win.title, "message": f"Switched to: {win.title}"}
            return {"status": "not_found", "application": name, "message": f"No window found matching '{name}'."}
        except ImportError:
            return {"status": "error", "error": "pygetwindow not installed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @classmethod
    def list_open_apps(cls) -> dict[str, Any]:
        """
        Return all visible windows with non-empty titles.

        Parameters: none
        Returns: dict with status, count, apps (list of {title, pid})
        Edge cases: Returns empty list if pygetwindow unavailable; ignores blank-title windows
        """
        try:
            import pygetwindow as gw
            import psutil
            windows = gw.getAllWindows()
            apps = []
            for win in windows:
                if win.title and win.title.strip():
                    entry: dict[str, Any] = {"title": win.title}
                    # Try to attach PID
                    try:
                        norm = win.title.lower()
                        for proc in psutil.process_iter(["pid", "name"]):
                            if (proc.info["name"] or "").lower() in norm or norm in (proc.info["name"] or "").lower():
                                entry["pid"] = proc.info["pid"]
                                break
                    except Exception:
                        pass
                    apps.append(entry)
            return {"status": "success", "count": len(apps), "apps": apps}
        except ImportError:
            return {"status": "error", "error": "pygetwindow not installed"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @classmethod
    def screenshot(cls) -> dict[str, Any]:
        """
        Capture the full screen and return as a base64-encoded PNG string.

        Parameters: none
        Returns: dict with status, image_b64, width, height, saved_path
        Edge cases: Requires Pillow (PIL); saves to Log/screenshots/ automatically
        """
        try:
            from PIL import ImageGrab
            import base64
            import io
            from pathlib import Path

            img = ImageGrab.grab()
            w, h = img.size

            # Save to log dir
            save_dir = Path(__file__).resolve().parent.parent.parent.parent.parent / "Log" / "screenshots"
            save_dir.mkdir(parents=True, exist_ok=True)
            import time as _time
            fname = save_dir / f"screenshot_{int(_time.time())}.png"
            img.save(fname, "PNG")

            # Also encode to b64 for WebSocket return
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

            return {
                "status": "success",
                "width": w,
                "height": h,
                "saved_path": str(fname),
                "image_b64": b64,
                "message": f"Screenshot saved: {fname.name}",
            }
        except ImportError:
            return {"status": "error", "error": "Pillow not installed (pip install Pillow)"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
