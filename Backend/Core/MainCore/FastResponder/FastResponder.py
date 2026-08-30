"""
Vibhu-Oska AI-OS — FastResponder
Lightweight deterministic instant-response engine that sits on the PRIMARY path.

Re-homed from BackupCore's fast pattern handlers (greetings, identity, status,
telemetry, time/date, OS info, help, acknowledgements, and math evaluation).

Protocol guarantees:
- FastResponder is part of the primary intelligence surface — it never carries
  contingency responsibilities.
- BackupCore remains a strict contingency layer (fault / capacity / timeout) and
  delegates its own instant-pattern responses to this module to avoid drift.
- No SLM, no model weights, no external APIs. Pure logic + live telemetry.
"""

from __future__ import annotations

import datetime
import math
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from Backend.Plugins.Logger.Logger import Logger


class FastResponder:
    """
    Instantly resolves deterministic prompt patterns and returns a formatted
    response string, or None to fall through to the full reasoning pipeline.
    """

    def __init__(self) -> None:
        self._log = Logger.get("FastResponder")

    # ==================================================================================================
    # # Top-Level Dispatch
    # ==================================================================================================

    def try_respond(self, prompt: str) -> str | None:
        """
        Attempt to resolve a prompt instantly via fast pattern matching.

        Parameters:
            prompt: Raw user input string
        Returns: Response string if pattern matched, None otherwise
        """
        norm = prompt.strip().lower()

        # 1. Math expressions resolve first — avoids any inference cold-start.
        math_result = self._try_math(norm, prompt)
        if math_result:
            return math_result

        # 2. Direct greetings
        if re.search(r'^\s*(hello|hi|hey|yo|sup|greetings|good\s*(morning|afternoon|evening|night))\s*[!.,?]?\s*$', norm):
            return self._greeting()

        # 3. Identity / capability questions
        if re.search(r'\b(who are you|what are you|tell me about yourself|what is vibhu.?oska|what can you do|your capabilities|describe yourself)\b', norm):
            return self._identity()

        # 4. System / health status (whole-line or short phrasing)
        if re.search(r'^\s*(status|health|how are you|are you (ok|working|online|alive|up|running)|system info)\s*[!.,?]?\s*$', norm):
            return self._system_status()

        # 5. Live telemetry (whole-line)
        if re.search(r'^\s*(telemetry|performance|hardware)\s*[!.,?]?\s*$', norm):
            return self._telemetry()

        # 6. Time and date (whole-line)
        if re.search(r'^\s*(what is the )?(time|date|current time|today|what day)\??\s*$', norm):
            return self._time_date()

        # 7. OS / platform (whole-line)
        if re.search(r'^\s*(what (operating system|platform|os)|which (os|platform))\??\s*$', norm):
            return self._os_info()

        # 8. Help / commands
        if re.search(r'^\s*(help|commands|what can you do|options|guide|usage)\s*[!.,?]?\s*$', norm):
            return self._help()

        # 9. Affirmations / acknowledgements
        if re.search(r'^\s*(ok|okay|got it|understood|thanks|thank you|great|nice|cool|awesome|perfect|sure|alright|sounds good)\s*[!.,?]?\s*$', norm):
            return "Acknowledged. Ready for your next task — what are we building?"

        return None

    # ==================================================================================================
    # # Instant Responders
    # ==================================================================================================

    def _greeting(self) -> str:
        now = datetime.datetime.now()
        hour = now.hour
        period = "morning" if hour < 12 else "afternoon" if hour < 18 else "evening"
        ts = now.strftime("%H:%M")
        return (
            f"Good {period} — it's {ts}. I am **Vibhu-Oska AI-OS**, your sovereign local intelligence layer.\n\n"
            f"Instant responses are served by **FastResponder** on the primary path.\n\n"
            f"I can help with:\n"
            f"- System telemetry and OS operations\n"
            f"- Code analysis and debugging\n"
            f"- Architecture and training guidance\n"
            f"- Memory queries (ChromaDB + knowledge graph)\n"
            f"- General knowledge and reasoning\n\n"
            f"What are we building today?"
        )

    def _identity(self) -> str:
        return (
            "I am **Vibhu-Oska AI-OS** — a fully sovereign, locally-hosted artificial intelligence "
            "operating system, engineered from first principles.\n\n"
            "**Architecture:**\n"
            "| Core | Role |\n"
            "|---|---|\n"
            "| **CognitionCore** | Karsh transformer (custom, training in progress) |\n"
            "| **FastResponder** | Deterministic instant responses (primary path) |\n"
            "| **BackupCore** | Intelligent CPU contingency fallback |\n"
            "| **OrchestratorCore** | Task decomposition, routing, and pipeline coordination |\n"
            "| **ValidationCore** | I/O contract enforcement (JSON schema + quality gate) |\n"
            "| **DataCore** | ChromaDB vector store + SQLite relational memory |\n"
            "| **AutomationCore** | Native OS integration and subprocess execution |\n"
            "| **DesignCore** | UI component generation and layout engine |\n"
            "| **EventBus** | ZeroMQ async mesh — connects all cores |\n\n"
            "**Execution pipeline:**\n"
            "`WebSocket → _process_prompt_direct → FastResponder → OrchestratorCore → [CognitionCore|BackupCore] → response`\n\n"
            "**Hardware:** RTX 4060 Laptop GPU · 8-core CPU\n\n"
            "Zero cloud dependencies. Zero external APIs. Entirely yours."
        )

    def _system_status(self) -> str:
        tel = self._get_telemetry()
        return (
            "**Vibhu-Oska AI-OS — System Status**\n\n"
            "| Component | Status |\n"
            "|---|---|\n"
            "| Gateway (FastAPI/Uvicorn) | ✅ Running |\n"
            "| EventBus (ZeroMQ) | ✅ Active |\n"
            "| DataCore (SQLite + ChromaDB) | ✅ Initialized |\n"
            "| OrchestratorCore | ✅ Active |\n"
            "| OrchestratorCore Router | ✅ Loaded |\n"
            "| FastResponder | ✅ Active (primary fast path) |\n"
            "| BackupCore | ✅ Contingency armed |\n"
            "| Karsh | ⚠ Training required |\n\n"
            f"**Live Hardware:**\n{tel}\n\n"
            "Operating in full offline sovereign mode. No external API calls."
        )

    def _telemetry(self) -> str:
        tel = self._get_telemetry()
        return f"**System Telemetry**\n{tel}"

    def _get_telemetry(self) -> str:
        """Pull live hardware metrics. Returns formatted string."""
        lines = []
        try:
            import psutil
            cpu_pct = psutil.cpu_percent(interval=0.2)
            cpu_freq = psutil.cpu_freq()
            freq_str = f" @ {cpu_freq.current:.0f}MHz" if cpu_freq else ""
            cores = psutil.cpu_count(logical=True)
            lines.append(f"CPU: {cpu_pct}% ({cores} cores{freq_str})")

            mem = psutil.virtual_memory()
            lines.append(f"Memory: {mem.used / 1e9:.2f}GB used / {mem.total / 1e9:.2f}GB total ({mem.percent}%)")

            disk = psutil.disk_usage("/")
            lines.append(f"Disk: {disk.free / 1e9:.2f}GB free / {disk.total / 1e9:.2f}GB total")
        except ImportError:
            lines.append("CPU: psutil not installed — install with `pip install psutil`")

        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                parts = [p.strip() for p in result.stdout.strip().split(",")]
                if len(parts) >= 5:
                    lines.append(
                        f"GPU: {parts[0]} — {parts[1]}% util · {parts[2]}MB/{parts[3]}MB VRAM · {parts[4]}°C"
                    )
        except Exception:
            lines.append("GPU: NVIDIA GeForce RTX 4060 Laptop (nvidia-smi unavailable)")

        return "\n".join(lines)

    def _time_date(self) -> str:
        now = datetime.datetime.now()
        tz = now.astimezone().tzname()
        return (
            f"**Current timestamp:** `{now.strftime('%A, %d %B %Y — %H:%M:%S')}` ({tz})\n\n"
            f"**ISO 8601:** `{now.isoformat()}`"
        )

    def _os_info(self) -> str:
        u = platform.uname()
        py = sys.version.split()[0]
        return (
            f"**Platform:** `{u.system} {u.release}` — `{u.machine}`\n"
            f"**Machine:** `{u.node}`\n"
            f"**Processor:** `{u.processor or platform.processor() or 'Unknown'}`\n"
            f"**Python:** `{py}`\n"
            f"**GPU:** NVIDIA GeForce RTX 4060 Laptop GPU\n"
            f"**Root:** `{Path(__file__).resolve().parent.parent.parent.parent.parent}`"
        )

    def _help(self) -> str:
        return (
            "**Vibhu-Oska AI-OS — Command Reference**\n\n"
            "**Chat:**\n"
            "- Type any message and press **Enter** or click **Send**\n"
            "- Instant patterns resolve via FastResponder (primary path)\n"
            "- Contingency reasoning is handled by BackupCore when Karsh is unavailable\n\n"
            "**Special query patterns:**\n"
            "| Pattern | Action |\n"
            "|---|---|\n"
            "| `status` / `system status` | Live hardware telemetry |\n"
            "| `N op N` (e.g. `128 * 8`) | Math evaluation |\n"
            "| `who are you` | Full architecture description |\n"
            "| `help` | This reference |\n\n"
            "**Panels:**\n"
            "| Tab | Purpose |\n"
            "|---|---|\n"
            "| **Chat** | Main conversation interface |\n"
            "| **Research** | Web search (requires SearXNG) |\n"
            "| **Tasks** | Active background task queue |\n"
            "| **Memory** | Vector store + knowledge graph |\n"
            "| **Monitor** | Live CPU/GPU/RAM charts |\n"
            "| **Train** | Karsh training controls |"
        )

    # ==================================================================================================
    # # Math Evaluation
    # ==================================================================================================

    def _try_math(self, norm: str, raw: str) -> str | None:
        """Attempt to evaluate a math expression. Returns None if not math."""
        # Detect math-like input
        if not re.search(r'\d', raw):
            # Also check natural-language math patterns
            if not re.search(r'\b(sqrt|square root|power|squared|cubed|factorial|fibonacci|prime)\b', norm):
                return None

        # Natural language: "2 to the power of 10", "2 power 10"
        power_match = re.search(
            r'(\d+\.?\d*)\s+(?:to\s+the\s+)?(?:power\s+of|\^|\*\*|raised\s+to)\s+(\d+\.?\d*)',
            norm
        )
        if power_match:
            try:
                a, b = float(power_match.group(1)), float(power_match.group(2))
                result = a ** b
                display = int(result) if result == int(result) else round(result, 6)
                return f"`{int(a) if a == int(a) else a}^{int(b) if b == int(b) else b}` = **`{display}`**"
            except Exception:
                pass

        # "N squared" / "N cubed"
        sq_match = re.search(r'(\d+)\s+squared', norm)
        if sq_match:
            n = int(sq_match.group(1))
            return f"`{n}^2` = **`{n*n}`**"

        cu_match = re.search(r'(\d+)\s+cubed', norm)
        if cu_match:
            n = int(cu_match.group(1))
            return f"`{n}^3` = **`{n*n*n}`**"

        # "X percent of Y"
        pct_match = re.search(r'(\d+\.?\d*)\s*%\s+of\s+(\d+\.?\d*)', norm)
        if pct_match:
            pct, val = float(pct_match.group(1)), float(pct_match.group(2))
            result = (pct / 100) * val
            display = int(result) if result == int(result) else round(result, 4)
            return f"`{pct}% of {val}` = **`{display}`**"

        # Direct expression patterns
        expr_match = re.search(
            r'(\d+\.?\d*)\s*([\+\-\*\/\^%]|\*\*|//)\s*(\d+\.?\d*)',
            raw.replace('×', '*').replace('÷', '/').replace('^', '**')
        )
        if expr_match:
            try:
                a_str, op, b_str = expr_match.group(1), expr_match.group(2), expr_match.group(3)
                a, b = float(a_str), float(b_str)
                if op in ('+',):    result = a + b
                elif op in ('-',):  result = a - b
                elif op in ('*', '×'): result = a * b
                elif op in ('/', '÷'):
                    if b == 0: return "`Division by zero` — undefined."
                    result = a / b
                elif op in ('**', '^'): result = a ** b
                elif op in ('%',): result = a % b
                elif op in ('//',): result = int(a) // int(b)
                else: return None

                # Clean up result display
                int_result = int(result) if result == int(result) else None
                display = int_result if int_result is not None else round(result, 6)
                expr_clean = f"{a_str} {op} {b_str}".replace('**', '^')
                return f"`{expr_clean}` = **`{display}`**"
            except Exception:
                pass

        # sqrt, factorial, etc.
        if re.search(r'\b(sqrt|square root)\b', norm):
            n_match = re.search(r'(\d+\.?\d*)', raw)
            if n_match:
                n = float(n_match.group(1))
                result = math.sqrt(n)
                display = int(result) if result == int(result) else round(result, 6)
                return f"\u221a{n_match.group(1)} = **`{display}`**"

        if re.search(r'\bfactorial\b|\b(\d+)!\b', norm):
            n_match = re.search(r'(\d+)', raw)
            if n_match:
                n = int(n_match.group(1))
                if n > 20:
                    return f"`{n}!` is astronomically large: **`{math.factorial(n)}`**"
                return f"`{n}!` = **`{math.factorial(n)}`**"

        return None

    def save(self, data: Any) -> Any:
        """Backward-compatibility stub."""
        return data

    def restore(self, data: Any) -> Any:
        """Backward-compatibility stub."""
        return data
