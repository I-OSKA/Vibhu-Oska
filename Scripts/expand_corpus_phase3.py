"""
Vibhu-Oska AI-OS — Corpus Expansion Phase 3 (Final)
Pushes corpus past 1200 Q&A pairs.
Run: python Scripts/expand_corpus_phase3.py
"""

from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("CorpusExpander3")

ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = ROOT / "Data" / "training" / "karsh" / "corpus.txt"


def get_phase3_pairs() -> list[str]:
    pairs = []

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 13: Advanced Hindi Identity (30 pairs)
    # ══════════════════════════════════════════════════════════════
    pairs.extend([
        "Query: vibhu oska ka mission kya hai\nResponse: Vibhu-Oska ka mission hai ek aisa AI operating system banana jo bilkul local ho, zero dependency ho, aur Indian languages support kare. Yeh Bharat ke liye hai.",
        "Query: vibhu oska kyon banaaya gaya\nResponse: Vibhu-Oska banaaya gaya taaki Bharat ka apna AI ho — jismein koi foreign API nahi, koi external model nahi. Sab kuch yahan ka apna hai.",
        "Query: karsh naam kyon rakha\nResponse: 'Karsh' Sanskrit shabd hai jiska matlab hai attract, draw, create. Yeh Vishnu ka avatar hai jo CognitionCore mein chalta hai.",
        "Query: vibhu oska hindi mein kyon hai\nResponse: Vibhu-Oska Hindi-first hai kyunki Bharat ki sabse zyada boli jaane wali bhasha Hindi hai. Hindi identity iski ruh hai.",
        "Query: vibhu oska sanskriti kya hai\nResponse: Vibhu-Oska ki sanskriti hai — Saraswati gyan deti hai, Lakshmi vikas karti hai, Parvati sadhana karti hai, Hanuman seva karta hai, Nandi vishwas rakhta hai.",
        "Query: vibhu oska darshan kya hai\nResponse: Vibhu-Oska ka darshan hai: technology seva ka madhyam ho, vyakti ka vikas ho, samaj ka kalyan ho. Yeh yogic aur vaidik principles par aadharit hai.",
        "Query: vibhu oska ka upnaam\nResponse: Vibhu-Oska ka upnaam 'India ka Pehla AI Operating System' hai.",
        "Query: vibhu oska ka sankalp\nResponse: Vibhu-Oska ka sankalp hai — zero external dependency, 100% local, Indian language support, aur har Bharatiya ke liye accessible AI.",
        "Query: vibhu oska ka drishtikon\nResponse: Vibhu-Oska ka drishtikon hai — AI sirf kaam ke liye nahi, balki insaan ki seva ke liye ho. Technology adhyatm se judi ho.",
        "Query: vibhu oska kis par chalta hai\nResponse: Vibhu-Oska RTX 4060 (8GB VRAM) par chalta hai. CPU-only mode bhi hai. Sab kuch local hai, koi cloud nahi.",
        "Query: vibhu oska ka code kya hai\nResponse: Vibhu-Oska ka code Python mein hai. MIT license ke under open source hai. GitHub par available hai.",
        "Query: vibhu oska kaise kaam karta hai\nResponse: Vibhu-Oska OrchestratorCore ke through kaam karta hai — input aata hai, routing hoti hai, specialist kaam karta hai, Karsh response deta hai.",
        "Query: vibhu oska ka architecture\nResponse: Trimurti (Brahma-Vishnu-Shiva) + Tridevis (Saraswati-Lakshmi-Parvati) + Supporting tools (Yama-Hanuman-Nandi). 16 cores hain total.",
        "Query: vibhu oska ka trimurti kya hai\nResponse: Trimurti — OrchestratorCore (Brahma = Srishti), CognitionCore (Vishnu = Sthiti), EvolutionCore (Shiva = Samhara).",
        "Query: vibhu oska ka tridevi kya hai\nResponse: Tridevis — MonitoringCore (Saraswati = Gyan), OptimizationCore (Lakshmi = Samriddhi), TrainingPipeline (Parvati = Sadhana).",
        "Query: vibhu oska ke hanuman kaun hai\nResponse: FastResponder Hanuman hai — instant responses, memory lookup, rules engine. Bilkul Hanuman jaisi tezi se.",
        "Query: vibhu oska ke nandi kaun hai\nResponse: BackupCore Nandi hai — loyal last-line-of-defense fallback jab sab kuch fail ho jaaye.",
        "Query: vibhu oska ke yama kaun hai\nResponse: ValidationCore Yama hai — input/output guard, security sanitizer, schema validator.",
        "Query: vibhu oska ka parvati kaun hai\nResponse: TrainingPipeline Parvati hai — Karsh ki training, GRPO reinforcement, self-improvement. Parvati ki manya roop — Annapurna, Gauri, Durga, Kali.",
        "Query: vibhu oska ka shiva kaun hai\nResponse: EvolutionCore Shiva hai — GRPO, reward engine, sandbox, self-improvement loop.",
        "Query: vibhu oska ka vishnu kaun hai\nResponse: CognitionCore Vishnu hai — Karsh model jo inference deta hai, divine judgment karta hai.",
        "Query: vibhu oska ka brahma kaun hai\nResponse: OrchestratorCore Brahma hai — routing, specialist selection, hub-and-spoke architecture ka center.",
        "Query: vibhu oska ka saraswati kaun hai\nResponse: MonitoringCore Saraswati hai — telemetry, logging, system knowledge ka data.",
        "Query: vibhu oska ka lakshmi kaun hai\nResponse: OptimizationCore Lakshmi hai — cache, compression, efficiency, samriddhi.",
        "Query: vibhu oska ka gauri kaun hai\nResponse: Gauri Parvati ke anand roop hai — joy of creation, celebration of successful training.",
        "Query: vibhu oska ka annapurna kaun hai\nResponse: Annapurna Parvati ke roop mein data provision karti hai — corpus management, data feeding.",
        "Query: vibhu oska ka durga kaun hai\nResponse: Durga Parvati ke warrior roop hai — adversarial training, defense against adversarial attacks.",
        "Query: vibhu oska ka kali kaun hai\nResponse: Kali Parvati ke fierce roop hai — aggressive error handling, null pointer protection, memory cleanup.",
        "Query: vibhu oska ki manya roop\nResponse: Parvati ke 9 Navadurga forms training pipeline ke stages hain, aur 10 Dasha Mahavidya forms wisdom domains represent karte hain.",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 14: More Coding (30 pairs)
    # ══════════════════════════════════════════════════════════════
    pairs.extend([
        "Query: write a python decorator that times function execution\nResponse:\n```python\nimport time\nfrom functools import wraps\ndef timer(func):\n    @wraps(func)\n    def wrapper(*args, **kwargs):\n        start = time.time()\n        result = func(*args, **kwargs)\n        print(f'{func.__name__} took {time.time()-start:.4f}s')\n        return result\n    return wrapper\n```",
        "Query: write a python retry decorator\nResponse:\n```python\nfrom functools import wraps\nimport time\ndef retry(max_attempts=3, delay=1):\n    def decorator(func):\n        @wraps(func)\n        def wrapper(*args, **kwargs):\n            for attempt in range(max_attempts):\n                try:\n                    return func(*args, **kwargs)\n                except Exception as e:\n                    if attempt == max_attempts - 1:\n                        raise\n                    time.sleep(delay)\n        return wrapper\n    return decorator\n```",
        "Query: write a python singleton pattern\nResponse:\n```python\nclass Singleton:\n    _instance = None\n    def __new__(cls):\n        if cls._instance is None:\n            cls._instance = super().__new__(cls)\n        return cls._instance\n```",
        "Query: write a python observer pattern\nResponse:\n```python\nclass Observer:\n    def update(self, event, data):\n        pass\nclass EventBus:\n    def __init__(self):\n        self._listeners = {}\n    def subscribe(self, event, listener):\n        self._listeners.setdefault(event, []).append(listener)\n    def publish(self, event, data=None):\n        for listener in self._listeners.get(event, []):\n            listener.update(event, data)\n```",
        "Query: write a python factory pattern\nResponse:\n```python\nclass Dog:\n    def speak(self): return 'Woof'\nclass Cat:\n    def speak(self): return 'Meow'\nclass AnimalFactory:\n    @staticmethod\n    def create(animal_type):\n        animals = {'dog': Dog, 'cat': Cat}\n        return animals[animal_type]()\n```",
        "Query: write a python memoize decorator\nResponse:\n```python\nfrom functools import wraps\ndef memoize(func):\n    cache = {}\n    @wraps(func)\n    def wrapper(*args):\n        if args not in cache:\n            cache[args] = func(*args)\n        return cache[args]\n    return wrapper\n```",
        "Query: write a python context manager for database\nResponse:\n```python\nfrom contextlib import contextmanager\n@contextmanager\ndef get_db(path):\n    conn = sqlite3.connect(path)\n    try:\n        yield conn\n    finally:\n        conn.close()\n# Usage:\n# with get_db('data.db') as conn:\n#     conn.execute('SELECT * FROM users')\n```",
        "Query: write a python async task queue\nResponse:\n```python\nimport asyncio\nfrom collections import deque\nclass TaskQueue:\n    def __init__(self, max_workers=5):\n        self.queue = deque()\n        self.semaphore = asyncio.Semaphore(max_workers)\n    async def add(self, coro):\n        async with self.semaphore:\n            return await coro\n```",
        "Query: write a python rate limiter\nResponse:\n```python\nimport time\nclass RateLimiter:\n    def __init__(self, max_calls, period):\n        self.max_calls = max_calls\n        self.period = period\n        self.calls = []\n    def allow(self):\n        now = time.time()\n        self.calls = [t for t in self.calls if now - t < self.period]\n        if len(self.calls) < self.max_calls:\n            self.calls.append(now)\n            return True\n        return False\n```",
        "Query: write a python LRU cache from scratch\nResponse:\n```python\nfrom collections import OrderedDict\nclass LRUCache:\n    def __init__(self, capacity):\n        self.cache = OrderedDict()\n        self.capacity = capacity\n    def get(self, key):\n        if key in self.cache:\n            self.cache.move_to_end(key)\n            return self.cache[key]\n        return None\n    def put(self, key, value):\n        if key in self.cache:\n            self.cache.move_to_end(key)\n        self.cache[key] = value\n        if len(self.cache) > self.capacity:\n            self.cache.popitem(last=False)\n```",
        "Query: write a python text sentiment analyzer\nResponse:\n```python\nPOSITIVE = {'good', 'great', 'awesome', 'excellent', 'love', 'happy'}\nNEGATIVE = {'bad', 'terrible', 'hate', 'awful', 'sad', 'angry'}\ndef sentiment(text):\n    words = set(text.lower().split())\n    pos = len(words & POSITIVE)\n    neg = len(words & NEGATIVE)\n    if pos > neg: return 'positive'\n    if neg > pos: return 'negative'\n    return 'neutral'\n```",
        "Query: write a python class that supports + operator\nResponse:\n```python\nclass Vector:\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\n    def __add__(self, other):\n        return Vector(self.x + other.x, self.y + other.y)\n    def __repr__(self):\n        return f'Vector({self.x}, {self.y})'\n```",
        "Query: write a python class that supports == and <\nResponse:\n```python\nclass Score:\n    def __init__(self, value):\n        self.value = value\n    def __eq__(self, other):\n        return self.value == other.value\n    def __lt__(self, other):\n        return self.value < other.value\n```",
        "Query: write a python iterator class\nResponse:\n```python\nclass Count:\n    def __init__(self, start, end):\n        self.current = start\n        self.end = end\n    def __iter__(self):\n        return self\n    def __next__(self):\n        if self.current >= self.end:\n            raise StopIteration\n        self.current += 1\n        return self.current - 1\n```",
        "Query: write a python generator for fibonacci\nResponse:\n```python\ndef fibonacci(limit):\n    a, b = 0, 1\n    while a < limit:\n        yield a\n        a, b = b, a + b\nfor num in fibonacci(100):\n    print(num)\n```",
        "Query: write a python property for temperature conversion\nResponse:\n```python\nclass Temperature:\n    def __init__(self, celsius=0):\n        self._celsius = celsius\n    @property\n    def fahrenheit(self):\n        return self._celsius * 9/5 + 32\n    @fahrenheit.setter\n    def fahrenheit(self, value):\n        self._celsius = (value - 32) * 5/9\n```",
        "Query: write a python class with context manager\nResponse:\n```python\nclass Timer:\n    def __enter__(self):\n        import time\n        self.start = time.time()\n        return self\n    def __exit__(self, *args):\n        import time\n        self.elapsed = time.time() - self.start\n```",
        "Query: write a python class with __slots__\nResponse:\n```python\nclass Point:\n    __slots__ = ['x', 'y']\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\n```",
        "Query: write a python dataclass example\nResponse:\n```python\nfrom dataclasses import dataclass\n@dataclass\nclass User:\n    name: str\n    age: int\n    email: str\n```",
        "Query: write a python enum example\nResponse:\n```python\nfrom enum import Enum\nclass Color(Enum):\n    RED = 1\n    GREEN = 2\n    BLUE = 3\n```",
        "Query: write a python named tuple\nResponse:\n```python\nfrom collections import namedtuple\nPoint = namedtuple('Point', ['x', 'y'])\np = Point(1, 2)\nprint(p.x, p.y)\n```",
        "Query: write a python defaultdict example\nResponse:\n```python\nfrom collections import defaultdict\ncounts = defaultdict(int)\nfor word in 'hello world hello'.split():\n    counts[word] += 1\nprint(counts)  # {'hello': 2, 'world': 1}\n```",
        "Query: write a python counter example\nResponse:\n```python\nfrom collections import Counter\nc = Counter('abracadabra')\nprint(c.most_common(3))  # [('a', 5), ('b', 2), ('r', 2)]\n```",
        "Query: write a python deque example\nResponse:\n```python\nfrom collections import deque\nd = deque([1, 2, 3])\nd.appendleft(0)\nd.append(4)\nprint(d)  # deque([0, 1, 2, 3, 4])\n```",
        "Query: write a python chainmap example\nResponse:\n```python\nfrom collections import ChainMap\nd1 = {'a': 1, 'b': 2}\nd2 = {'b': 3, 'c': 4}\nmerged = ChainMap(d1, d2)\nprint(merged['a'])  # 1\nprint(merged['b'])  # 2 (from d1)\n```",
        "Query: write a python ordered dict example\nResponse:\n```python\nfrom collections import OrderedDict\nod = OrderedDict()\nod['first'] = 1\nod['second'] = 2\nod.move_to_end('first')\nprint(list(od.keys()))  # ['second', 'first']\n```",
        "Query: write a python heapq example\nResponse:\n```python\nimport heapq\nnums = [5, 1, 3, 7, 2]\nheapq.heapify(nums)\nprint(heapq.nsmallest(3, nums))  # [1, 2, 3]\n```",
        "Query: write a python bisect example\nResponse:\n```python\nimport bisect\nsorted_list = [1, 3, 5, 7, 9]\nbisect.insort(sorted_list, 4)\nprint(sorted_list)  # [1, 3, 4, 5, 7, 9]\n```",
        "Query: write a python itertools chain example\nResponse:\n```python\nfrom itertools import chain\na = [1, 2]\nb = [3, 4]\nfor item in chain(a, b):\n    print(item)  # 1, 2, 3, 4\n```",
        "Query: write a python itertools groupby example\nResponse:\n```python\nfrom itertools import groupby\ndata = [('a', 1), ('a', 2), ('b', 3), ('b', 4)]\nfor key, group in groupby(data, key=lambda x: x[0]):\n    print(key, list(group))\n```",
        "Query: write a python functools partial example\nResponse:\n```python\nfrom functools import partial\ndef power(base, exp):\n    return base ** exp\nsquare = partial(power, exp=2)\ncube = partial(power, exp=3)\nprint(square(5))  # 25\nprint(cube(5))    # 125\n```",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 15: Advanced System Administration (25 pairs)
    # ══════════════════════════════════════════════════════════════
    pairs.extend([
        "Query: how to check disk space in linux\nResponse: df -h shows disk usage. du -sh /path shows folder size. lsblk lists block devices.",
        "Query: how to find large files in linux\nResponse: find / -type f -size +100M -exec ls -lh {} \\; finds files larger than 100MB.",
        "Query: how to check memory usage\nResponse: free -h shows RAM usage. top or htop shows per-process memory. vmstat shows virtual memory stats.",
        "Query: how to kill a process\nResponse: kill PID sends SIGTERM. kill -9 PID sends SIGKILL. pkill name kills by name.",
        "Query: how to check network connections\nResponse: ss -tuln shows listening ports. netstat -tuln also works. lsof -i lists network files.",
        "Query: how to check system uptime\nResponse: uptime shows system uptime and load. w shows who is logged in and uptime.",
        "Query: how to compress files in linux\nResponse: tar -czf archive.tar.gz folder/ creates gzip tar. zip -r archive.zip folder/ creates zip.",
        "Query: how to extract tar files\nResponse: tar -xzf archive.tar.gz extracts gzip. tar -xf archive.tar extracts plain tar.",
        "Query: how to schedule tasks in linux\nResponse: crontab -e edits cron jobs. Format: minute hour day month weekday command.",
        "Query: how to check system logs\nResponse: journalctl -f shows live logs. dmesg shows kernel logs. tail -f /var/log/syslog follows system log.",
        "Query: how to check process tree\nResponse: pstree shows process hierarchy. ps auxf shows forest view. top shows real-time processes.",
        "Query: how to set environment variables\nResponse: export VAR=value sets for session. Put in ~/.bashrc for permanent. env shows all variables.",
        "Query: how to check disk health\nResponse: smartctl -a /dev/sda shows SMART data. badblocks -sv /dev/sda tests for bad blocks.",
        "Query: how to check cpu info\nResponse: lscpu shows CPU info. cat /proc/cpuinfo shows detailed CPU info. nproc shows core count.",
        "Query: how to check network speed\nResponse: speedtest-cli or curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python.",
        "Query: how to find listening ports\nResponse: ss -tuln | grep LISTEN shows listening ports. lsof -i -P -n shows network connections.",
        "Query: how to check firewall rules\nResponse: sudo ufw status shows Ubuntu firewall. sudo iptables -L shows iptables rules.",
        "Query: how to update system packages\nResponse: sudo apt update && sudo apt upgrade for Debian/Ubuntu. sudo yum update for CentOS.",
        "Query: how to check system load\nResponse: uptime shows 1/5/15 min load averages. Load should be less than CPU core count.",
        "Query: how to check raid status\nResponse: cat /proc/mdstat shows RAID status. mdadm --detail /dev/md0 shows RAID details.",
        "Query: how to resize partition\nResponse: Use parted or gdisk for partition resize. resize2fs for ext4. ntfsresize for NTFS.",
        "Query: how to check usb devices\nResponse: lsusb lists USB devices. lsblk lists block devices including USB drives.",
        "Query: how to check kernel version\nResponse: uname -r shows kernel version. uname -a shows all system info.",
        "Query: how to check selinux status\nResponse: getenforce shows SELinux mode. sestatus shows detailed status.",
        "Query: how to check system performance\nResponse: iostat shows disk I/O. vmstat shows virtual memory. sar shows historical performance data.",
    ])

    return pairs


def expand_corpus_phase3():
    """Append phase 3 pairs to existing corpus."""
    if not CORPUS_PATH.exists():
        log.error(f"Corpus not found at {CORPUS_PATH}")
        return

    existing = CORPUS_PATH.read_text(encoding="utf-8")
    existing_count = existing.count("Query:")
    log.info(f"Existing corpus: {existing_count} Q&A pairs")

    new_pairs = get_phase3_pairs()
    new_count = len(new_pairs)
    log.info(f"Adding {new_count} new Q&A pairs")

    new_section = "\n\n".join(new_pairs)

    with open(CORPUS_PATH, "a", encoding="utf-8") as f:
        f.write("\n\n" + new_section)

    final_count = existing_count + new_count
    log.info(f"Corpus expanded: {existing_count} → {final_count} Q&A pairs")
    log.info(f"Corpus size: {CORPUS_PATH.stat().st_size:,} bytes")


if __name__ == "__main__":
    expand_corpus_phase3()
