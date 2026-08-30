"""
Vibhu-Oska AI-OS -- Desktop Manifestation Layer

Two modes:
1. TRAY: Small indicator top-right + Ctrl+Shift+Space = mini chat bubble
2. WALLPAPER: Ctrl+Shift+W = fullscreen AI-OS overlay over desktop

Usage:
    .venv\\Scripts\\python Backend\\Desktop\\Manifestation.py
"""
from __future__ import annotations

import asyncio
import json
import math
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import random
import logging

logger = logging.getLogger("Manifestation")

BACKEND_WS_URL = "ws://localhost:8100/ws"
BACKEND_HTTP   = "http://localhost:8100"
HOTKEY_MINI    = "<Control-Shift-space>"
HOTKEY_FULL    = "<Control-Shift-w>"
HOTKEY_HIDE    = "<Escape>"
SESSION_ID     = f"desktop_{int(time.time())}"

C_BG       = "#080c14"
C_PANEL    = "#0d1521"
C_ACCENT   = "#00d4ff"
C_ACCENT2  = "#7c3aed"
C_TEXT     = "#e2e8f0"
C_TEXT_DIM = "#64748b"
C_BORDER   = "#1e293b"
C_AI_BG    = "#0f1c2e"
C_RED      = "#f43f5e"
C_GREEN    = "#10b981"
C_GOLD     = "#fbbf24"

# ── Settings & Themes Management ─────────────────────────────────────────────────────────────

DEFAULT_SETTINGS = {
    "theme": "Electric Cyan",
    "hotkey_mini": "<Control-Shift-space>",
    "hotkey_full": "<Control-Shift-w>",
    "hotkey_hide": "<Escape>",
    "performance_mode": False,
    "balanced_mode": False,
    "min_particles": 10,
    "max_particles": 100
}

THEMES = {
    "Electric Cyan": {
        "bg": "#080c14",
        "panel": "#0d1521",
        "accent": "#00d4ff",
        "accent2": "#7c3aed",
        "text": "#e2e8f0",
        "text_dim": "#64748b",
        "border": "#1e293b",
        "ai_bg": "#0f1c2e"
    },
    "Plasma Purple": {
        "bg": "#0a0512",
        "panel": "#120b20",
        "accent": "#bd93f9",
        "accent2": "#ff79c6",
        "text": "#f8f8f2",
        "text_dim": "#6272a4",
        "border": "#282a36",
        "ai_bg": "#1d1233"
    },
    "Solar Amber": {
        "bg": "#0f0c05",
        "panel": "#1b140b",
        "accent": "#ffb86c",
        "accent2": "#f1fa8c",
        "text": "#f8f8f2",
        "text_dim": "#8b826b",
        "border": "#342818",
        "ai_bg": "#2c1f0e"
    },
    "Crimson Red": {
        "bg": "#0f0505",
        "panel": "#1c0b0b",
        "accent": "#ff5555",
        "accent2": "#ff79c6",
        "text": "#f8f8f2",
        "text_dim": "#8b6b6b",
        "border": "#341818",
        "ai_bg": "#2d0f0f"
    }
}

def get_settings_path() -> str:
    app_data = os.environ.get("APPDATA")
    if app_data:
        base_dir = os.path.join(app_data, "Vibhu-Oska")
    else:
        base_dir = os.path.join(os.path.expanduser("~"), ".config", "vibhu-oska")
    return os.path.join(base_dir, "manifestation_settings.json")

def save_settings(settings: dict) -> bool:
    path = get_settings_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        os.replace(tmp_path, path)
        return True
    except Exception as e:
        logger.error("Failed to save settings: %s", e)
        return False

def load_settings() -> dict:
    path = get_settings_path()
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_SETTINGS, **data}
    except Exception:
        pass
    save_settings(DEFAULT_SETTINGS)
    return DEFAULT_SETTINGS.copy()

# ── Extensible Hotkey Conflict Checks ─────────────────────────────────────────────────────────

CONFLICTS_FILE = os.path.join(os.path.dirname(get_settings_path()), "hotkey_conflicts.txt")
OVERRIDES_FILE = os.path.join(os.path.dirname(get_settings_path()), "hotkey_overrides.txt")

def load_conflict_list() -> set[str]:
    conflicts = {
        "<control-c>", "<control-v>", "<control-x>", "<control-a>", "<control-z>", 
        "<control-s>", "<control-o>", "<control-f>", "<control-alt-delete>",
        "<alt-f4>", "<control-q>", "<control-escape>", "<alt-tab>"
    }
    try:
        if os.path.exists(CONFLICTS_FILE):
            with open(CONFLICTS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip().lower()
                    if line and not line.startswith("#"):
                         conflicts.add(line)
    except Exception:
        pass
    try:
        if os.path.exists(OVERRIDES_FILE):
            with open(OVERRIDES_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip().lower()
                    if line.startswith("-"):
                        conflicts.discard(line[1:].strip())
                    elif line and not line.startswith("#"):
                        conflicts.add(line)
    except Exception:
        pass
    return conflicts

def validate_hotkey(hotkey: str) -> bool:
    if not hotkey:
        return False
    if not (hotkey.startswith("<") and hotkey.endswith(">")):
        return False
    conflicts = load_conflict_list()
    if hotkey.lower() in conflicts:
        return False
    return True

def translate_hotkey(hotkey: str) -> str:
    """Translate control/command modifiers cross-platform."""
    if sys.platform == "darwin":
        hotkey = hotkey.replace("Control", "Command").replace("control", "command")
    return hotkey

# ── Bounded UI Update Queue ─────────────────────────────────────────────────────────────────

class UIUpdateQueue:
    """Thread-safe bounded queue for updating Tkinter widgets from background threads."""
    def __init__(self, root: tk.Tk, maxsize: int = 50) -> None:
        self._root = root
        self._q = queue.Queue(maxsize=maxsize)
        self._polling = False

    def put(self, func: callable, *args, **kwargs) -> None:
        try:
            if self._q.full():
                try:
                    self._q.get_nowait()
                except queue.Empty:
                    pass
            self._q.put_nowait((func, args, kwargs))
            if not self._polling:
                self._start_polling()
        except Exception:
            pass

    def _start_polling(self) -> None:
        self._polling = True
        self._poll()

    def _poll(self) -> None:
        for _ in range(5):
            try:
                func, args, kwargs = self._q.get_nowait()
                func(*args, **kwargs)
            except queue.Empty:
                break
        if not self._q.empty():
            self._root.after(10, self._poll)
        else:
            self._polling = False

# ── WebSocket Client ────────────────────────────────────────────────────────────────────────

class VibhuWSClient(threading.Thread):
    """
    Persistent WebSocket connection to Vibhu-Oska backend.

    Parameters:
        on_message: Callable(str) - fired when AI sends a response
        on_status:  Callable(str) - fired on connection state change
    Returns: None
    Edge cases: Auto-reconnects with 3s delay on any disconnect/error.
    """

    def __init__(self, on_message, on_status) -> None:
        super().__init__(daemon=True)
        self._on_msg    = on_message
        self._on_status = on_status
        self._q: queue.Queue[str | None] = queue.Queue()
        self._running   = True

    def send(self, prompt: str) -> None:
        """Queue a prompt for delivery to AI."""
        self._q.put(prompt)

    def stop(self) -> None:
        """Signal graceful shutdown."""
        self._running = False
        self._q.put(None)

    def run(self) -> None:
        asyncio.run(self._loop())

    async def _loop(self) -> None:
        while self._running:
            try:
                from websockets.asyncio.client import connect
                self._on_status("CONNECTING")
                async with connect(BACKEND_WS_URL) as ws:
                    self._on_status("ONLINE")
                    done, _ = await asyncio.wait(
                        {asyncio.create_task(self._recv(ws)),
                         asyncio.create_task(self._send_loop(ws))},
                        return_when=asyncio.FIRST_COMPLETED
                    )
            except Exception as exc:
                self._on_status(f"OFFLINE - {str(exc)[:40]}")
                await asyncio.sleep(3)

    async def _recv(self, ws) -> None:
        async for raw in ws:
            try:
                msg = json.loads(raw)
                t   = msg.get("type", "")
                if t == "task.completed":
                    c = msg.get("payload", {}).get("content", "")
                    if c:
                        self._on_msg(c)
                elif t == "task.failed":
                    self._on_msg("Error: " + msg.get("payload", {}).get("error", ""))
            except Exception:
                pass

    async def _send_loop(self, ws) -> None:
        loop = asyncio.get_running_loop()
        while True:
            prompt = await loop.run_in_executor(None, self._q.get)
            if prompt is None:
                return
            await ws.send(json.dumps({"prompt": prompt, "session_id": SESSION_ID}))


# ── Neural Canvas ───────────────────────────────────────────────────────────────────────────

class NeuralCanvas:
    """
    Animated particle network background (~30fps on tkinter Canvas).

    Parameters:
        canvas: Target tk.Canvas widget
        color:  Particle/edge colour string
    """

    def __init__(self, canvas: tk.Canvas, color: str = C_ACCENT) -> None:
        self._c      = canvas
        self._color  = color
        self._nodes: list[dict] = []
        self._active = False
        self._job    = None
        self._mx = None
        self._my = None
        self._consecutive_slow_frames = 0
        self._consecutive_fast_frames = 0
        
        self._c.bind("<Motion>", self._on_mouse_move)
        self._c.bind("<Leave>", self._on_mouse_leave)

    def _on_mouse_move(self, e) -> None:
        self._mx = e.x
        self._my = e.y

    def _on_mouse_leave(self, e) -> None:
        self._mx = None
        self._my = None

    def start(self, n: int = 40) -> None:
        w = self._c.winfo_width()  or 400
        h = self._c.winfo_height() or 300
        phi = 0.618033
        self._nodes = [{"x": w*(i/max(n,1)), "y": h*((i*phi)%1.0),
                        "vx": math.sin(i*0.7)*0.5, "vy": math.cos(i*0.9)*0.5,
                        "r": 1.5+(i%3)} for i in range(n)]
        self._active = True
        self._tick()

    def stop(self) -> None:
        self._active = False
        if self._job:
            try:
                self._c.after_cancel(self._job)
            except Exception:
                pass
            self._job = None

    def _tick(self) -> None:
        if not self._active:
            return
        start_time = time.time()
        try:
            c = self._c
            w, h = c.winfo_width(), c.winfo_height()
            if w <= 1: w = 800
            if h <= 1: h = 600
            c.delete("n")

            mx, my = self._mx, self._my
            for nd in self._nodes:
                if mx is not None and my is not None:
                    dx = mx - nd["x"]
                    dy = my - nd["y"]
                    # Optimized bounds checks (150px) to prevent heavy distance calculations
                    if abs(dx) < 150 and abs(dy) < 150:
                        dist = math.sqrt(dx*dx + dy*dy)
                        if 0 < dist < 150:
                            easing = (1.0 - (dist / 150.0)) ** 3
                            force = easing * 0.4
                            nd["vx"] += (dx / dist) * force
                            nd["vy"] += (dy / dist) * force

                nd["x"] += nd["vx"]; nd["y"] += nd["vy"]
                
                speed = math.sqrt(nd["vx"]**2 + nd["vy"]**2)
                if speed > 3.0:
                    nd["vx"] = (nd["vx"] / speed) * 3.0
                    nd["vy"] = (nd["vy"] / speed) * 3.0

                if nd["x"] < 0 or nd["x"] > w: nd["vx"] *= -1
                if nd["y"] < 0 or nd["y"] > h: nd["vy"] *= -1
                
                nd["x"] = max(0, min(nd["x"], w))
                nd["y"] = max(0, min(nd["y"], h))

                x, y, r = nd["x"], nd["y"], nd["r"]
                c.create_oval(x-r, y-r, x+r, y+r, fill=self._color, outline="",
                              tags="n", stipple="gray50")
            ns = self._nodes
            for i in range(len(ns)):
                for j in range(i+1, len(ns)):
                    dx = ns[i]["x"]-ns[j]["x"]; dy = ns[i]["y"]-ns[j]["y"]
                    if abs(dx) < 110 and abs(dy) < 110:
                        d  = math.sqrt(dx*dx+dy*dy)
                        if d < 110:
                            c.create_line(ns[i]["x"], ns[i]["y"], ns[j]["x"], ns[j]["y"],
                                          fill=self._color, width=0.5, tags="n",
                                          stipple="gray25" if d > 70 else "gray50")

            elapsed_ms = (time.time() - start_time) * 1000.0
            
            app = VibhuDesktopApp.get_instance()
            perf_mode = False
            balanced_mode = False
            min_nodes = 10
            max_nodes = 100
            if app:
                perf_mode = app._settings.get("performance_mode", False)
                balanced_mode = app._settings.get("balanced_mode", False)
                min_nodes = app._settings.get("min_particles", 10)
                max_nodes = app._settings.get("max_particles", 100)

            if perf_mode:
                target_nodes = 25
            elif balanced_mode:
                target_nodes = 50
            else:
                target_nodes = max_nodes

            # Hysteresis adaptive scaling based on frame latency
            if elapsed_ms > 40.0:  # < 25 FPS (log alert and reduce immediately)
                self._consecutive_slow_frames += 1
                self._consecutive_fast_frames = 0
            elif elapsed_ms > 22.0: # < 45 FPS
                self._consecutive_slow_frames += 1
                self._consecutive_fast_frames = 0
            elif elapsed_ms < 12.0: # Good performance
                self._consecutive_slow_frames = 0
                self._consecutive_fast_frames += 1
            else:
                self._consecutive_slow_frames = 0
                self._consecutive_fast_frames = 0

            if not perf_mode and not balanced_mode:
                current_n = len(self._nodes)
                if self._consecutive_slow_frames >= 3 and current_n > min_nodes:
                    new_n = max(min_nodes, current_n - 5)
                    self._nodes = self._nodes[:new_n]
                    logger.warning("Dynamic GPU throttle. Nodes: %d -> %d (frame: %.1fms)", current_n, new_n, elapsed_ms)
                    self._consecutive_slow_frames = 0
                elif self._consecutive_fast_frames >= 5 and current_n < target_nodes:
                    new_n = min(target_nodes, current_n + 2)
                    while len(self._nodes) < new_n:
                        self._nodes.append({
                            "x": random.uniform(0, w), "y": random.uniform(0, h),
                            "vx": random.uniform(-1.0, 1.0), "vy": random.uniform(-1.0, 1.0),
                            "r": random.uniform(1.5, 4.5)
                        })
                    self._consecutive_fast_frames = 0

            self._job = c.after(16, self._tick)  # Capped at 60 FPS (16.6ms)
        except tk.TclError:
            pass


# ── Chat helpers ────────────────────────────────────────────────────────────────────────────

def _make_chat(parent: tk.Widget) -> tk.Text:
    """
    Build a styled read-only chat Text widget inside parent.

    Returns: Configured tk.Text widget
    """
    frame = tk.Frame(parent, bg=C_BG)
    frame.pack(fill="both", expand=True, padx=4, pady=4)
    t = tk.Text(frame, bg=C_BG, fg=C_TEXT, font=("Segoe UI", 10), wrap="word",
                state="disabled", relief="flat", bd=0, padx=8, pady=6,
                cursor="arrow", spacing1=4, spacing3=4)
    sb = ttk.Scrollbar(frame, command=t.yview)
    t.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    t.pack(fill="both", expand=True)
    t.tag_configure("user", foreground=C_ACCENT2, font=("Segoe UI", 10, "bold"))
    t.tag_configure("ai",   foreground=C_ACCENT,  font=("Segoe UI", 10, "bold"))
    t.tag_configure("msg",  foreground=C_TEXT)
    t.tag_configure("dim",  foreground=C_TEXT_DIM, font=("Segoe UI", 8))
    t.tag_configure("type", foreground=C_ACCENT,   font=("Segoe UI", 9))
    return t


def chat_append(t: tk.Text, role: str, label: str, content: str) -> None:
    """Append a message to the chat widget."""
    t.configure(state="normal")
    t.insert("end", f"\n{label} . {time.strftime('%H:%M')}\n", role)
    t.insert("end", content + "\n", "msg")
    t.see("end")
    t.configure(state="disabled")


def chat_typing(t: tk.Text) -> None:
    """Show typing indicator."""
    t.configure(state="normal")
    t.insert("end", "\n... thinking\n", "type")
    t.mark_set("tm", "end-2l")
    t.see("end")
    t.configure(state="disabled")


def chat_clear_typing(t: tk.Text) -> None:
    """Remove typing indicator."""
    try:
        t.configure(state="normal")
        t.delete(t.index("tm"), "end")
        t.configure(state="disabled")
    except Exception:
        pass


# ── Mini Floating Bubble ────────────────────────────────────────────────────────────────────

class MiniBubble(tk.Toplevel):
    """
    Compact always-on-top chat window (380x480px) activated via hotkey.

    Parameters:
        parent:    Root Tk()
        ws_client: Active VibhuWSClient
    """

    def __init__(self, parent: tk.Tk, ws: VibhuWSClient) -> None:
        super().__init__(parent)
        self._ws  = ws
        self._dx  = self._dy = 0
        self._t:  tk.Text  | None = None
        self._sl: tk.Label | None = None
        self._iv  = tk.StringVar()
        self._init_window()
        self._build()

    def _init_window(self) -> None:
        self.title("Vibhu-Oska")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.95)
        self.configure(bg=C_BG)
        
        # Geometry clamp failover
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        if sw <= 0: sw = 1920
        if sh <= 0: sh = 1080
        
        x = max(0, min(sw - 400, sw - 400))
        y = max(0, min(sh - 520, sh - 520))
        self.geometry(f"380x480+{x}+{y}")
        
        self.bind("<ButtonPress-1>", lambda e: (setattr(self, "_dx", e.x), setattr(self, "_dy", e.y)))
        self.bind("<B1-Motion>",     lambda e: self.geometry(
            f"+{self.winfo_x()+e.x-self._dx}+{self.winfo_y()+e.y-self._dy}"))
        self.bind(HOTKEY_HIDE, lambda e: self.withdraw())
        self.bind(HOTKEY_MINI, lambda e: self.toggle())

    def _build(self) -> None:
        self._bar = tk.Frame(self, bg=C_PANEL, height=36)
        self._bar.pack(fill="x"); self._bar.pack_propagate(False)
        self._bar.bind("<ButtonPress-1>", lambda e: (setattr(self, "_dx", e.x), setattr(self, "_dy", e.y)))
        self._bar.bind("<B1-Motion>",     lambda e: self.geometry(
            f"+{self.winfo_x()+e.x-self._dx}+{self.winfo_y()+e.y-self._dy}"))
        
        self._title_lbl = tk.Label(self._bar, text="VIBHU-OSKA", font=("Segoe UI", 11, "bold"),
                 fg=C_ACCENT, bg=C_PANEL)
        self._title_lbl.pack(side="left", padx=10)
        
        self._sl = tk.Label(self._bar, text="O", font=("Segoe UI", 12), fg=C_RED, bg=C_PANEL)
        self._sl.pack(side="right", padx=8)
        
        self._close_btn = tk.Button(self._bar, text="x", fg=C_TEXT_DIM, bg=C_PANEL, bd=0, font=("Segoe UI", 8),
                  activeforeground=C_RED, activebackground=C_PANEL,
                  command=self.withdraw)
        self._close_btn.pack(side="right", padx=2)

        self._t = _make_chat(self)
        chat_append(self._t, "ai", "Vibhu-Oska", "AI-OS initialized. Ready for input.")

        self._row = tk.Frame(self, bg=C_PANEL, pady=6)
        self._row.pack(fill="x", side="bottom")
        self._inp = tk.Entry(self._row, textvariable=self._iv, font=("Segoe UI", 10),
                       bg=C_BG, fg=C_TEXT, insertbackground=C_ACCENT, relief="flat", bd=0)
        self._inp.pack(side="left", fill="x", expand=True, padx=(10,4), ipady=6)
        self._inp.bind("<Return>", self._send)
        self._inp.focus_set()
        
        self._send_btn = tk.Button(self._row, text="Send", font=("Segoe UI", 8), fg=C_BG, bg=C_ACCENT, bd=0, padx=8,
                  command=self._send)
        self._send_btn.pack(side="right", padx=(0,10))

    def update_theme(self, colors: dict) -> None:
        self.configure(bg=colors["bg"])
        self._bar.configure(bg=colors["panel"])
        self._title_lbl.configure(fg=colors["accent"], bg=colors["panel"])
        self._sl.configure(bg=colors["panel"])
        self._close_btn.configure(fg=colors["text_dim"], bg=colors["panel"], activebackground=colors["panel"])
        self._row.configure(bg=colors["panel"])
        self._inp.configure(bg=colors["bg"], fg=colors["text"], insertbackground=colors["accent"])
        self._send_btn.configure(fg=colors["bg"], bg=colors["accent"])
        
        # Redraw chat tags
        self._t.configure(bg=colors["bg"], fg=colors["text"])
        self._t.tag_configure("user", foreground=colors["accent2"])
        self._t.tag_configure("ai",   foreground=colors["accent"])
        self._t.tag_configure("msg",  foreground=colors["text"])
        self._t.tag_configure("dim",  foreground=colors["text_dim"])
        self._t.tag_configure("type", foreground=colors["accent"])

    def toggle(self) -> None:
        if self.winfo_viewable():
            self.withdraw()
        else:
            self.deiconify(); self.lift()

    def _send(self, _=None) -> None:
        txt = self._iv.get().strip()
        if not txt or not self._t: return
        self._iv.set("")
        chat_append(self._t, "user", "You", txt)
        chat_typing(self._t)
        self._ws.send(txt)

    def on_ai(self, content: str) -> None:
        if self._t: chat_clear_typing(self._t); chat_append(self._t, "ai", "Vibhu-Oska", content)

    def on_status(self, s: str) -> None:
        color = C_GREEN if "ONLINE" in s else (C_GOLD if "CONNECTING" in s else C_RED)
        if self._sl:
            try: self._sl.configure(fg=color)
            except Exception: pass


# ── Wallpaper / AI-OS Overlay ───────────────────────────────────────────────────────────────

class WallpaperOverlay(tk.Toplevel):
    """
    Fullscreen AI-OS skin rendered as an interactive desktop layer.
    Neural background animation, chat panel, hardware telemetry, live clock.

    Parameters:
        parent: Root Tk()
        ws:     Active VibhuWSClient
    """

    def __init__(self, parent: tk.Tk, ws: VibhuWSClient) -> None:
        super().__init__(parent)
        self._ws  = ws
        self._nc: NeuralCanvas | None = None
        self._t:  tk.Text  | None = None
        self._tl: tk.Label | None = None
        self._cl: tk.Label | None = None
        self._sl: tk.Label | None = None
        self._iv  = tk.StringVar()
        self._init_window()
        self._build()
        self.after(100,  self._start_nc)
        self.after(200,  self._clock_tick)
        self.after(1500, self._poll_telem)

    def _init_window(self) -> None:
        self.title("Vibhu-Oska AI-OS")
        self.overrideredirect(True)
        self.attributes("-topmost", False)
        self.attributes("-alpha", 0.92)
        
        app = VibhuDesktopApp.get_instance()
        colors = THEMES.get(app._settings["theme"], THEMES["Electric Cyan"]) if app else THEMES["Electric Cyan"]
        self.configure(bg=colors["bg"])
        
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        if sw <= 0: sw = 1920
        if sh <= 0: sh = 1080
        self.geometry(f"{sw}x{sh}+0+0")
        self.lower()
        self.bind(HOTKEY_HIDE, lambda e: self._close())
        self.bind(HOTKEY_FULL, lambda e: self._close())

    def _build(self) -> None:
        app = VibhuDesktopApp.get_instance()
        colors = THEMES.get(app._settings["theme"], THEMES["Electric Cyan"]) if app else THEMES["Electric Cyan"]
        
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        if sw <= 0: sw = 1920
        if sh <= 0: sh = 1080
        
        self._bg = tk.Canvas(self, bg=colors["bg"], highlightthickness=0)
        self._bg.place(x=0, y=0, width=sw, height=sh)

        # Chat panel (left)
        self._cp = tk.Frame(self, bg=colors["panel"])
        self._cp.place(x=20, y=60, width=540, height=sh-140)
        self._hdr = tk.Frame(self._cp, bg=colors["panel"])
        self._hdr.pack(fill="x")
        self._title_lbl = tk.Label(self._hdr, text="VIBHU-OSKA COGNITION CORE",
                 font=("Segoe UI", 11, "bold"), fg=colors["accent"], bg=colors["panel"])
        self._title_lbl.pack(side="left", padx=12, pady=8)
        self._sl = tk.Label(self._hdr, text="O INIT", font=("Segoe UI", 8),
                            fg=colors["accent"], bg=colors["panel"])
        self._sl.pack(side="right", padx=8)
        self._divider = tk.Frame(self._cp, bg=colors["border"], height=1)
        self._divider.pack(fill="x", padx=8)

        self._t = _make_chat(self._cp)
        chat_append(self._t, "ai", "Vibhu-Oska", "AI-OS Wallpaper Mode active.")

        self._row = tk.Frame(self._cp, bg=colors["panel"], pady=6)
        self._row.pack(fill="x", side="bottom")
        self._inp = tk.Entry(self._row, textvariable=self._iv, font=("Segoe UI", 11),
                       bg=colors["ai_bg"], fg=colors["text"], insertbackground=colors["accent"],
                       relief="flat", bd=0)
        self._inp.pack(side="left", fill="x", expand=True, ipady=8, padx=(8,6))
        self._inp.bind("<Return>", self._send)
        self._inp.focus_set()
        
        self._send_btn = tk.Button(self._row, text="SEND", font=("Segoe UI", 9, "bold"),
                   fg=colors["bg"], bg=colors["accent"], bd=0, padx=10,
                   command=self._send)
        self._send_btn.pack(side="right", padx=(0,8))

        # Telemetry panel (right)
        self._rp = tk.Frame(self, bg=colors["panel"])
        self._rp.place(x=sw-340, y=60, width=320, height=360)
        self._telem_lbl = tk.Label(self._rp, text="SYSTEM TELEMETRY",
                 font=("Segoe UI", 10, "bold"), fg=colors["accent"], bg=colors["panel"])
        self._telem_lbl.pack(pady=(10,4))
        self._divider2 = tk.Frame(self._rp, bg=colors["border"], height=1)
        self._divider2.pack(fill="x", padx=8)
        self._tl = tk.Label(self._rp, text="Connecting...", font=("Cascadia Code", 9),
                            fg=colors["text_dim"], bg=colors["panel"], justify="left", wraplength=290)
        self._tl.pack(padx=12, pady=8, anchor="w")

        # Clock
        self._cl = tk.Label(self, text="--:--:--", font=("Segoe UI", 36, "bold"),
                            fg=colors["accent"], bg=colors["bg"])
        self._cl.place(x=sw-340, y=440, width=320)

        # Footer
        self._footer_lbl = tk.Label(self, text="Esc or Ctrl+Shift+W to exit overlay",
                 font=("Segoe UI", 8), fg=colors["text_dim"], bg=colors["bg"])
        self._footer_lbl.place(x=0, y=sh-22, width=sw)

    def update_theme(self, colors: dict) -> None:
        self.configure(bg=colors["bg"])
        self._bg.configure(bg=colors["bg"])
        if self._nc:
            self._nc._color = colors["accent"]
            
        self._cp.configure(bg=colors["panel"])
        self._hdr.configure(bg=colors["panel"])
        self._title_lbl.configure(fg=colors["accent"], bg=colors["panel"])
        self._sl.configure(bg=colors["panel"])
        self._divider.configure(bg=colors["border"])
        self._row.configure(bg=colors["panel"])
        self._inp.configure(bg=colors["ai_bg"], fg=colors["text"], insertbackground=colors["accent"])
        self._send_btn.configure(fg=colors["bg"], bg=colors["accent"])
        
        self._rp.configure(bg=colors["panel"])
        self._telem_lbl.configure(fg=colors["accent"], bg=colors["panel"])
        self._divider2.configure(bg=colors["border"])
        self._tl.configure(fg=colors["text_dim"], bg=colors["panel"])
        self._cl.configure(fg=colors["accent"], bg=colors["bg"])
        self._footer_lbl.configure(fg=colors["text_dim"], bg=colors["bg"])

        # Redraw chat tags
        self._t.configure(bg=colors["bg"], fg=colors["text"])
        self._t.tag_configure("user", foreground=colors["accent2"])
        self._t.tag_configure("ai",   foreground=colors["accent"])
        self._t.tag_configure("msg",  foreground=colors["text"])
        self._t.tag_configure("dim",  foreground=colors["text_dim"])
        self._t.tag_configure("type", foreground=colors["accent"])

    def _start_nc(self) -> None:
        app = VibhuDesktopApp.get_instance()
        colors = THEMES.get(app._settings["theme"], THEMES["Electric Cyan"]) if app else THEMES["Electric Cyan"]
        self._nc = NeuralCanvas(self._bg, colors["accent"])
        
        # Adapt particle counts from presets
        n = 55
        if app:
            if app._settings.get("performance_mode", False):
                n = 25
            elif app._settings.get("balanced_mode", False):
                n = 50
            else:
                n = app._settings.get("max_particles", 100)
        self._nc.start(n=n)

    def _clock_tick(self) -> None:
        try:
            if self._cl: self._cl.configure(text=time.strftime("%H:%M:%S"))
            self.after(1000, self._clock_tick)
        except tk.TclError: pass

    def _poll_telem(self) -> None:
        import urllib.request
        try:
            # Poll backend health summary
            with urllib.request.urlopen(f"{BACKEND_HTTP}/api/v1/telemetry", timeout=2) as r:
                data = json.loads(r.read())
                th   = data.get("thermal", {})
                txt  = "\n".join(f"{k}: {v}" for k, v in th.items())[:400] or "Backend online"
                if self._tl: self._tl.configure(text=txt, fg=C_TEXT)
        except Exception as exc:
            if self._tl: self._tl.configure(text=str(exc)[:80], fg=C_TEXT_DIM)
        try: self.after(5000, self._poll_telem)
        except tk.TclError: pass

    def _send(self, _=None) -> None:
        txt = self._iv.get().strip()
        if not txt or not self._t: return
        self._iv.set("")
        chat_append(self._t, "user", "You", txt)
        chat_typing(self._t)
        self._ws.send(txt)

    def on_ai(self, content: str) -> None:
        if self._t: chat_clear_typing(self._t); chat_append(self._t, "ai", "Vibhu-Oska", content)

    def on_status(self, s: str) -> None:
        color = C_GREEN if "ONLINE" in s else (C_GOLD if "CONNECTING" in s else C_RED)
        lbl   = "ONLINE" if "ONLINE" in s else s[:20]
        if self._sl:
            try: self._sl.configure(text=f"O {lbl}", fg=color)
            except Exception: pass

    def _close(self) -> None:
        if self._nc: self._nc.stop()
        try: self.destroy()
        except Exception: pass


# ── App Controller ──────────────────────────────────────────────────────────────────────────

class VibhuDesktopApp:
    """
    Master controller for the Desktop Manifestation Layer.
    Owns the WS client, tray indicator, mini bubble, and overlay.
    """
    _instance = None

    @classmethod
    def get_instance(cls) -> VibhuDesktopApp:
        return cls._instance

    def __init__(self) -> None:
        VibhuDesktopApp._instance = self
        self._settings = load_settings()

        # Enforce single-instance process lock via high socket port
        import socket
        try:
            self._lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._lock_socket.bind(("127.0.0.1", 64209))
        except OSError:
            # Duplicate instance error dialog
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Vibhu-Oska", "Another instance of Manifestation is already running.")
            sys.exit(1)

        self._root    = tk.Tk()
        self._root.withdraw()
        
        # Thread-safe UI update queue
        self._ui_queue = UIUpdateQueue(self._root)
        
        self._mini:    MiniBubble       | None = None
        self._overlay: WallpaperOverlay | None = None

        # Cross-platform translated hotkey strings
        self._hk_mini = translate_hotkey(self._settings["hotkey_mini"])
        self._hk_full = translate_hotkey(self._settings["hotkey_full"])

        self._ws = VibhuWSClient(self._on_ai, self._on_status)
        self._ws.start()

        self._build_tray()
        
        colors = THEMES.get(self._settings["theme"], THEMES["Electric Cyan"])
        self._mini = MiniBubble(self._root, self._ws)
        self._mini.update_theme(colors)
        self._mini.withdraw()

        # Multi-monitor bounds binding hotkeys
        self._root.bind_all(self._hk_mini, lambda e: self._toggle_mini())
        self._root.bind_all(self._hk_full, lambda e: self._toggle_overlay())
        self._root.protocol("WM_DELETE_WINDOW", self._quit)

        print("\n  Vibhu-Oska Desktop Layer Active")
        print("  Ctrl+Shift+Space  - Mini Chat")
        print("  Ctrl+Shift+W      - AI-OS Overlay")
        print("  Esc               - Hide\n")

    def _build_tray(self) -> None:
        colors = THEMES.get(self._settings["theme"], THEMES["Electric Cyan"])
        
        self._tray = tk.Toplevel(self._root)
        self._tray.overrideredirect(True)
        self._tray.attributes("-topmost", True)
        self._tray.attributes("-alpha", 0.88)
        self._tray.configure(bg=colors["bg"])
        
        sw = self._tray.winfo_screenwidth()
        if sw <= 0: sw = 1920
        self._tray.geometry(f"130x26+{sw-140}+2")
        
        self._fr = tk.Frame(self._tray, bg=colors["panel"])
        self._fr.pack(fill="both", expand=True)
        self._td = tk.Label(self._fr, text="O", font=("Segoe UI", 9), fg=C_RED, bg=colors["panel"])
        self._td.pack(side="left", padx=(6,2))
        self._lbl = tk.Label(self._fr, text="VIBHU-OSKA", font=("Segoe UI", 7, "bold"),
                 fg=colors["text_dim"], bg=colors["panel"])
        self._lbl.pack(side="left")

        self._menu = tk.Menu(self._tray, tearoff=0, bg=colors["panel"], fg=colors["text"],
                       activebackground=colors["accent2"], activeforeground=colors["text"])
        self._menu.add_command(label="Mini Chat  (Ctrl+Shift+Space)", command=self._toggle_mini)
        self._menu.add_command(label="AI-OS Overlay  (Ctrl+Shift+W)", command=self._toggle_overlay)
        
        # Color Theme Dropdown
        self._theme_menu = tk.Menu(self._menu, tearoff=0, bg=colors["panel"], fg=colors["text"],
                             activebackground=colors["accent2"], activeforeground=colors["text"])
        for theme_name in THEMES.keys():
            self._theme_menu.add_command(label=theme_name, command=lambda t=theme_name: self._apply_theme(t))
        self._menu.add_cascade(label="Themes", menu=self._theme_menu)

        # Performance Preset Cascade
        self._perf_menu = tk.Menu(self._menu, tearoff=0, bg=colors["panel"], fg=colors["text"],
                             activebackground=colors["accent2"], activeforeground=colors["text"])
        self._perf_menu.add_command(label="Sovereign Mode (100 Particles)", command=lambda: self._apply_perf_preset(False, False))
        self._perf_menu.add_command(label="Balanced Mode (50 Particles)", command=lambda: self._apply_perf_preset(False, True))
        self._perf_menu.add_command(label="Performance Mode (25 Particles)", command=lambda: self._apply_perf_preset(True, False))
        self._menu.add_cascade(label="Performance Preset", menu=self._perf_menu)
        
        self._menu.add_separator()
        self._menu.add_command(label="Exit", command=self._quit)

        def popup(e): self._menu.tk_popup(e.x_root, e.y_root)
        for w in (self._fr, self._tray):
            w.bind("<Button-3>", popup)
            w.bind("<Double-Button-1>", lambda e: self._toggle_mini())

    def _apply_theme(self, theme_name: str) -> None:
        if theme_name not in THEMES:
            return
        self._settings["theme"] = theme_name
        save_settings(self._settings)
        
        colors = THEMES[theme_name]
        
        # Apply theme updates locally
        self._tray.configure(bg=colors["bg"])
        self._fr.configure(bg=colors["panel"])
        self._td.configure(bg=colors["panel"])
        self._lbl.configure(fg=colors["text_dim"], bg=colors["panel"])
        
        self._menu.configure(bg=colors["panel"], fg=colors["text"], activebackground=colors["accent2"])
        self._theme_menu.configure(bg=colors["panel"], fg=colors["text"], activebackground=colors["accent2"])
        self._perf_menu.configure(bg=colors["panel"], fg=colors["text"], activebackground=colors["accent2"])

        if self._mini and self._mini.winfo_exists():
            self._mini.update_theme(colors)
        if self._overlay and self._overlay.winfo_exists():
            self._overlay.update_theme(colors)

    def _apply_perf_preset(self, perf: bool, balanced: bool) -> None:
        self._settings["performance_mode"] = perf
        self._settings["balanced_mode"] = balanced
        save_settings(self._settings)
        
        if self._overlay and self._overlay.winfo_exists():
            if self._overlay._nc:
                self._overlay._nc.stop()
                n = 25 if perf else (50 if balanced else self._settings["max_particles"])
                self._overlay._nc.start(n=n)

    def _toggle_mini(self) -> None:
        if self._mini is None:
            self._mini = MiniBubble(self._root, self._ws); return
        if self._mini.winfo_viewable(): self._mini.withdraw()
        else: self._mini.deiconify(); self._mini.lift()

    def _toggle_overlay(self) -> None:
        if self._overlay is not None:
            try: self._overlay._close()
            except Exception: pass
            self._overlay = None; return
        self._overlay = WallpaperOverlay(self._root, self._ws)

    def _on_ai(self, content: str) -> None:
        # Route through thread-safe update queue
        self._ui_queue.put(self._dispatch_ai, content)

    def _dispatch_ai(self, content: str) -> None:
        if self._mini and self._mini.winfo_exists():
            try: self._mini.on_ai(content)
            except Exception: pass
        if self._overlay and self._overlay.winfo_exists():
            try: self._overlay.on_ai(content)
            except Exception: pass

    def _on_status(self, s: str) -> None:
        # Route through thread-safe update queue
        self._ui_queue.put(self._dispatch_status, s)

    def _dispatch_status(self, s: str) -> None:
        color = C_GREEN if "ONLINE" in s else (C_GOLD if "CONNECTING" in s else C_RED)
        try: self._td.configure(fg=color)
        except Exception: pass
        if self._mini and self._mini.winfo_exists():
            try: self._mini.on_status(s)
            except Exception: pass
        if self._overlay and self._overlay.winfo_exists():
            try: self._overlay.on_status(s)
            except Exception: pass

    def _quit(self) -> None:
        self._ws.stop()
        
        # Release localhost process socket
        try:
            self._lock_socket.close()
        except Exception:
            pass

        try: self._root.quit(); self._root.destroy()
        except Exception: pass

    def run(self) -> None:
        self._root.mainloop()


if __name__ == "__main__":
    VibhuDesktopApp().run()
