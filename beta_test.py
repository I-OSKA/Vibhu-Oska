"""
Beta user simulation — tests the full conversation loop like a real user.
Sends 20+ messages in sequence, verifying each gets a real, non-empty response.
"""
import asyncio, json, uuid, time, sys

# Force UTF-8 output — Windows PowerShell defaults to cp1252 which can't print √, →, etc.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

try:
    import websockets
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets", "-q"])
    import websockets

MESSAGES = [
    # Core identity
    "hello",
    "what are you?",
    "who built you",
    # System
    "what is the system status",
    "how much ram is being used",
    # Math
    "128 * 8",
    "what is 2 to the power of 10",
    "sqrt 256",
    "is 97 prime?",
    "fibonacci 15",
    # Tech knowledge
    "how does the pipeline work",
    "what is chromadb",
    "explain the eventbus",
    "how do async functions work in python",
    "what is pytorch used for",
    "explain git commit",
    "what is an algorithm complexity",
    "what is fastapi",
    "how do I deploy vibhu oska with docker",
    # Natural questions
    "help",
    "what time is it",
    "what can you do",
    "tell me more",
    "what is your architecture",
]

async def chat(prompt: str, session_id: str) -> dict:
    t0 = time.time()
    result = {"prompt": prompt[:45], "status": "TIMEOUT", "ms": 0, "content": ""}
    try:
        async with websockets.connect("ws://localhost:8100/ws", ping_timeout=None) as ws:
            await ws.send(json.dumps({"prompt": prompt, "session_id": session_id}))
            deadline = time.time() + 25
            while time.time() < deadline:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=25)
                    data = json.loads(msg)
                    t = data.get("type", "")
                    if t == "task.completed":
                        result["status"] = "OK"
                        result["content"] = data["payload"]["content"]
                        result["ms"] = int((time.time() - t0) * 1000)
                        break
                    elif t == "task.failed":
                        result["status"] = "FAILED"
                        result["content"] = data["payload"].get("error", "")
                        result["ms"] = int((time.time() - t0) * 1000)
                        break
                except asyncio.TimeoutError:
                    break
    except Exception as e:
        result["status"] = f"ERR:{e}"
    return result

async def main():
    sid = str(uuid.uuid4())
    print("=== Beta User Simulation — Vibhu-Oska AI-OS ===")
    print(f"Session: {sid[:8]}")
    print("=" * 60)
    total_ok = 0
    total_fast = 0
    for msg in MESSAGES:
        r = await chat(msg, sid)
        icon = "[OK]  " if r["status"] == "OK" else "[FAIL]"
        speed = "FAST" if r["ms"] < 500 else "SLOW" if r["ms"] > 2000 else "OK  "
        print(f"\n{icon} [{speed}] [{r['ms']}ms] User: {r['prompt']}")
        if r["status"] == "OK":
            # Print first 2 lines of response
            lines = r["content"].strip().split("\n")[:2]
            for ln in lines:
                print(f"         AI: {ln[:120]}")
            total_ok += 1
            if r["ms"] < 1000:
                total_fast += 1
        else:
            print(f"         STATUS: {r['status']}")
    print(f"\n{'='*60}")
    print(f"Result: {total_ok}/{len(MESSAGES)} responses OK")
    print(f"Fast (<1s): {total_fast}/{total_ok} responses")

asyncio.run(main())
