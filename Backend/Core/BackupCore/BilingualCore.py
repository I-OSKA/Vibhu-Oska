"""
Vibhu-Oska AI-OS — BilingualCore
Hindi + English bilingual NLP layer.

Handles language detection, Hindi intent mapping, and bilingual response generation
entirely from scratch — no external translation APIs, no cloud services.
Supports: English, Hindi (Devanagari), Hinglish (Roman-script Hindi).
"""

from __future__ import annotations

import re
from typing import Optional


# ==================================================================================================
# # Internal Separation Division
# =================────────────────────────────────────────────────────────────────────────────────

# ── Devanagari Unicode range ───────────────────────────────────────────────────────────────────
_DEVANAGARI_RANGE = re.compile(r'[\u0900-\u097F]')

# ── Common Hinglish (Roman-script Hindi) keywords ────────────────────────────────────────────
_HINGLISH_TOKENS: set[str] = {
    # Greetings
    "namaste", "namaskar", "pranam", "jai", "sat", "sri",
    # Questions
    "kya", "kaun", "kaise", "kab", "kyun", "kyunki", "kahan", "kitna", "kitne", "kitni",
    # Verbs
    "hai", "hain", "ho", "tha", "thi", "the", "hoga", "hogi", "honge",
    "kar", "karo", "karo", "karna", "karta", "karti", "karein",
    "bolo", "batao", "dikhao", "kholo", "band", "karo", "chalao",
    # Pronouns / conjunctions
    "mujhe", "mera", "meri", "mere", "tum", "aap", "woh", "yeh", "ye",
    "aur", "ya", "lekin", "par", "ki", "ke", "ka", "ko", "se",
    # System / tech
    "status", "khabar", "jankari", "batao", "bata", "screenshot", "lo",
    "abhi", "kal", "aaj", "baaje", "baje", "waqt", "samay",
    # Numbers / math (Hinglish)
    "ka", "vargmool", "ghaat", "guna", "minus", "plus", "baar",
    # Common interjections
    "accha", "theek", "thik", "haan", "nahi", "nai", "ji", "sahib",
}

# ── Hindi OS command map: Hinglish phrase → English intent ────────────────────────────────────
_HI_OS_MAP: list[tuple[re.Pattern, str, str]] = [
    (re.compile(r'\b(chrome|chromium)\s*(kholo|open|chalu|start)\b', re.I), 'open_app', 'chrome'),
    (re.compile(r'\b(kholo|open|chalu|start)\s*(chrome|chromium)\b', re.I), 'open_app', 'chrome'),
    (re.compile(r'\b(notepad|notepad\+\+)\s*(kholo|open|chalu)\b', re.I), 'open_app', 'notepad'),
    (re.compile(r'\b(kholo|open|chalu)\s*(notepad)\b', re.I), 'open_app', 'notepad'),
    (re.compile(r'\b(spotify|gaane|music)\s*(kholo|chalu|bajao)\b', re.I), 'open_app', 'spotify'),
    (re.compile(r'\b(vscode|code|editor)\s*(kholo|chalu|open)\b', re.I), 'open_app', 'code'),
    (re.compile(r'\b(band\s*karo|band\s*kar|close\s*karo)\s*(\w+)\b', re.I), 'close_app', '__match_2__'),
    (re.compile(r'\b(\w+)\s*(band\s*karo|band\s*kar|close)\b', re.I), 'close_app', '__match_1__'),
    (re.compile(r'\b(screenshot|screen\s*shot)\s*(lo|le|lena|lijiye|lijie)\b', re.I), 'screenshot', ''),
    (re.compile(r'\b(screen\s*dikha|screen\s*dikhao)\b', re.I), 'screenshot', ''),
    (re.compile(r'\b(jo\s*apps?\s*chal\s*rahe|kaunse\s*apps?\s*khule|open\s*apps?\s*dikhao)\b', re.I), 'list_apps', ''),
]

# ── Hindi → English intent map (pattern → English routing key) ───────────────────────────────
_HI_INTENT_MAP: list[tuple[re.Pattern, str]] = [
    # Identity
    (re.compile(r'\b(tum\s*kaun\s*(ho|hain)|aap\s*kaun\s*(hain|ho)|tumhara\s*naam|kya\s*ho\s*tum|apna\s*parichay)\b', re.I), 'identity'),
    (re.compile(r'\b(tumhe\s*kisne|tumko\s*kisne|kisne\s*banaya|creator|bananewaala|banane\s*wala)\b', re.I), 'creator'),
    # Greetings
    (re.compile(r'^(namaste|namaskar|pranam|hi|hello|hey|haan|jai\s*hind|sat\s*sri)\s*[!.,?]?\s*$', re.I), 'greeting'),
    # Status
    (re.compile(r'\b(system\s*ka\s*status|system\s*kaisa\s*(hai|chal\s*raha)|health|theek\s*(hai|hain)|kya\s*haal)\b', re.I), 'status'),
    # Telemetry
    (re.compile(r'\b(ram|cpu|gpu|processor|memory)\s*(kitni|kitna|kya|kaisa|use|lag\s*rahi|lag\s*raha)\b', re.I), 'telemetry'),
    (re.compile(r'\b(cpu|ram|memory|disk)\s*(ka\s*)?(status|khabar|percentage|kitni)\b', re.I), 'telemetry'),
    # Time
    (re.compile(r'\b(abhi|aaj|kal)\s*(kitne|kya|kaun\s*sa)\s*baje|waqt\s*(kya|kitna)|samay\s*kya\b', re.I), 'time'),
    (re.compile(r'\b(time|waqt|samay)\s*(kya|kitna|batao|bolo)\b', re.I), 'time'),
    # Training
    (re.compile(r'\b(training|model|seekhna|seekh\s*raha|train\s*kar)\b', re.I), 'training'),
    # Memory
    (re.compile(r'\b(yaaddasht|memory|yaad\s*(rakhna|hai)|kuch\s*yaad)\b', re.I), 'memory'),
    # Help
    (re.compile(r'\b(help|madad|madat|sahayata|kya\s*kar\s*sakte|kya\s*karte)\b', re.I), 'help'),
    # Capability
    (re.compile(r'\b(kya\s*kar\s*sakte\s*ho|tumhari\s*kya\s*(capabilities|khaasiyat)|kya\s*kya\s*aata)\b', re.I), 'identity'),
    # Math
    (re.compile(r'\b(vargmool|square\s*root|jad)\b', re.I), 'math_sqrt'),
    (re.compile(r'\b(ghaat|power|ooth)\b', re.I), 'math_power'),
    (re.compile(r'\b(guna|multiply|곱|times\s*karo)\b', re.I), 'math_mul'),
    (re.compile(r'\b(factorial|vibhaajit|anukramank)\b', re.I), 'math_factorial'),
    (re.compile(r'\b(prime|assal|maulik\s*sankhya)\b', re.I), 'math_prime'),
    (re.compile(r'\b(fibonacci|fibo)\b', re.I), 'math_fib'),
    # Architecture
    (re.compile(r'\b(pipeline|vibhu.?oska|architecture|dhancha|banawat|cores?|kaise\s*kaam)\b', re.I), 'architecture'),
    # Affirmation
    (re.compile(r'^(theek|thik|accha|acha|haan|ji|samajh\s*gaya|shukriya|dhanyavad|thanks?)\s*[!.,]?\s*$', re.I), 'ack'),
]

# ── Hindi response templates ───────────────────────────────────────────────────────────────────
_HI_RESPONSES: dict[str, str] = {
    'greeting': (
        "Namaste! Main **Vibhu-Oska AI-OS** hoon — aapka locally-hosted AI operating system.\n\n"
        "Abhi main **BackupCore mode** mein kaam kar raha hoon jab tak Karsh train ho raha hai "
        "aapke RTX 4060 par.\n\n"
        "Main aapki madad kar sakta hoon:\n"
        "- System telemetry aur OS operations mein\n"
        "- Code analysis aur debugging mein\n"
        "- Architecture aur training guidance mein\n"
        "- Apps kholne aur band karne mein\n\n"
        "Aaj kya banana hai?"
    ),
    'identity': (
        "Main **Vibhu-Oska AI-OS** hoon — ek fully sovereign, locally-hosted artificial intelligence "
        "operating system, jo puri tarah se first principles se engineer kiya gaya hai.\n\n"
        "**Architecture:**\n"
        "- **BackupCore** — CPU-based intelligent reasoning (abhi active)\n"
        "- **Karsh** — 25M param custom PyTorch transformer (training phase)\n"
        "- **OrchestratorCore** — strategy routing: CPU vs GPU\n"
        "- **AutomationCore** — OS execution layer (apps, screenshots, automation)\n"
        "- **DataCore** — ChromaDB vectors + SQLite memory\n\n"
        "Zero external APIs. Sab kuch locally chalata hai."
    ),
    'creator': (
        "**Vibhu-Oska ko Harsh Dev Jha ne banaya hai** (handle: Inkesk).\n\n"
        "Har component — transformer weights se lekar tokenizer tak, training pipeline se lekar "
        "WebSocket gateway aur memory architecture tak — sab pure PyTorch primitives se "
        "first principles se engineer kiya gaya. Koi pretrained weights nahi, "
        "koi cloud APIs nahi, koi external AI services nahi."
    ),
    'status': (
        "**System Status: Operational**\n\n"
        "| Component | Status |\n"
        "|---|---|\n"
        "| BackupCore | ✅ Active |\n"
        "| Karsh | ⚠ Training Required |\n"
        "| OrchestratorCore Router | ✅ Loaded |\n"
        "| DataCore (ChromaDB + SQLite) | ✅ Online |\n"
        "| AutomationCore | ✅ Ready |\n"
        "| VoiceCore | ✅ Active |\n\n"
        "Telemetry ke liye poochiye: `RAM kitni use ho rahi hai`"
    ),
    'time': "{time_response}",
    'telemetry': "{telemetry_response}",
    'training': (
        "**Karsh Training Status:**\n\n"
        "- **Architecture**: 25M param decoder-only transformer\n"
        "- **Vocab**: 8,000 custom BPE tokens\n"
        "- **Corpus**: 300+ Q&A pairs (1200+ par expand ho raha hai)\n"
        "- **Hardware**: RTX 4060 Laptop GPU (8GB VRAM)\n"
        "- **Target**: 60 epochs, loss < 2.0\n\n"
        "Train karne ke liye: Train panel use karein `http://localhost:8100`\n"
        "Ya CLI se: `.venv\\Scripts\\python Models/karsh/train.py`"
    ),
    'memory': (
        "**Vibhu-Oska Memory Architecture:**\n\n"
        "**Vector Memory (ChromaDB):**\n"
        "- Semantic long-term memory store karta hai\n"
        "- Cosine similarity se nearest context retrieve karta hai\n"
        "- Conversations, documents, aur knowledge automatically index hote hain\n\n"
        "**Relational Memory (SQLite):**\n"
        "- Chat sessions, user preferences, task history\n"
        "- Knowledge graph entities aur relationships\n\n"
        "**Query karne ke liye:** Memory panel open karein."
    ),
    'help': (
        "**Vibhu-Oska AI-OS — Command Reference (Hindi + English)**\n\n"
        "**Chat:**\n"
        "- `kya haal hai` / `namaste` — greet karein\n"
        "- `system ka status kya hai` — system health\n"
        "- `ram kitni use ho rahi hai` — live telemetry\n\n"
        "**Apps Control:**\n"
        "- `chrome kholo` / `open chrome` — app launch\n"
        "- `spotify band karo` / `close spotify` — app close\n"
        "- `screenshot lo` / `take screenshot` — screen capture\n"
        "- `jo apps chal rahe hain dikhao` — list open apps\n\n"
        "**Math:**\n"
        "- `256 ka vargmool kya hai` — square root\n"
        "- `2 ka 10 ghaat` — power calculation\n"
        "- `97 prime hai kya` — prime check\n\n"
        "**Training:**\n"
        "- `model ka status kya hai` — training info\n"
    ),
    'architecture': (
        "**Vibhu-Oska Request Processing Pipeline:**\n\n"
        "```\n"
        "Trigger\n"
        "  → OrchestratorCore [System health check + task decomposition]\n"
        "  → ValidationCore [Input guard]\n"
        "  → DataCore       [Context/RAG retrieval]\n"
        "  → CognitionCore  [LLM/Transformer reasoning]\n"
        "  → ValidationCore [Output guard]\n"
        "  → UI Output / Action Execution\n"
        "```\n\n"
        "AbhI BackupCore fast-path use ho raha hai jab tak Karsh train nahi ho jaata."
    ),
    'ack': "Samajh gaya. Aage kya karna hai?",
    'math_sqrt': "{math_result}",
    'math_power': "{math_result}",
    'math_mul': "{math_result}",
    'math_factorial': "{math_result}",
    'math_prime': "{math_result}",
    'math_fib': "{math_result}",
    'fallback': (
        "Maafi chahta hoon, main abhi is specific query ko samajh nahi paya.\n\n"
        "Koshish karein:\n"
        "- Direct sawaal: `kya hai X?` / `kaise kaam karta hai Y?`\n"
        "- System query: `status` · `telemetry` · `time`\n"
        "- App control: `chrome kholo` · `screenshot lo`\n"
        "- Math: `256 ka vargmool` · `2 ka 10 ghaat`"
    ),
}


# ==================================================================================================
# # Internal Separation Division
# =================────────────────────────────────────────────────────────────────────────────────


class BilingualCore:
    """
    BilingualCore — Hindi + English NLP layer for Vibhu-Oska AI-OS.

    Provides language detection, Hindi intent mapping, and bilingual response generation.
    Built entirely from scratch — no external translation APIs or cloud services.

    Supports:
        - English (ASCII)
        - Hindi (Devanagari Unicode \u0900-\u097F)
        - Hinglish (Roman-script Hindi)

    Parameters: None
    Returns: Processed response strings
    Edge cases: Unknown language defaults to English path; math results passed through
    """

    # ── Language Detection ─────────────────────────────────────────────────────────────────────

    @staticmethod
    def detect_language(text: str) -> str:
        """
        Detect the language of the input text.

        Parameters:
            text: Raw user input string
        Returns: 'hi' (Hindi/Hinglish), 'en' (English)
        Edge cases: Mixed text with Devanagari → 'hi'; pure ASCII with no Hindi tokens → 'en'
        """
        # Devanagari characters → definitely Hindi
        if _DEVANAGARI_RANGE.search(text):
            return 'hi'

        # Check for Hinglish tokens (Roman-script Hindi)
        norm = text.lower()
        tokens = set(re.findall(r'\b\w+\b', norm))
        hi_token_count = len(tokens & _HINGLISH_TOKENS)

        # If 2+ Hinglish tokens found, treat as Hindi
        if hi_token_count >= 2:
            return 'hi'

        # Single-word Hinglish greetings
        if norm.strip() in {'namaste', 'namaskar', 'pranam', 'jai', 'kya', 'haan', 'nahi'}:
            return 'hi'

        return 'en'

    # ── OS Command Detection ───────────────────────────────────────────────────────────────────

    @staticmethod
    def extract_hindi_os_command(text: str) -> Optional[tuple[str, str]]:
        """
        Extract OS command intent from Hindi/Hinglish text.

        Parameters:
            text: Raw user input
        Returns: (action, target) tuple or None if not an OS command
        Edge cases: Returns None for non-OS text; target may be empty string for actions like screenshot
        """
        norm = text.lower()
        for pattern, action, target in _HI_OS_MAP:
            m = pattern.search(norm)
            if m:
                if target == '__match_1__':
                    t = m.group(1).strip()
                elif target == '__match_2__':
                    t = m.group(2).strip() if m.lastindex >= 2 else ''
                else:
                    t = target
                return (action, t)
        return None

    # ── Intent Mapping ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def map_hindi_intent(text: str) -> Optional[str]:
        """
        Map Hindi/Hinglish text to an internal intent key.

        Parameters:
            text: Normalized user input
        Returns: Intent key string or None if no match
        Edge cases: Returns None for unrecognized Hindi input → falls to Hindi fallback
        """
        norm = text.lower().strip()
        for pattern, intent in _HI_INTENT_MAP:
            if pattern.search(norm):
                return intent
        return None

    # ── Math in Hindi ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def extract_hindi_math(text: str) -> Optional[str]:
        """
        Handle Hindi math expressions and return a result string.

        Parameters:
            text: Raw user input (Hindi/Hinglish)
        Returns: Formatted math result string or None if not a math query
        Edge cases: Returns None for non-math text; large factorials capped at n<=20
        """
        import math
        norm = text.lower()

        # वर्गमूल / vargmool / square root
        if re.search(r'\b(vargmool|square\s*root|jad)\b', norm):
            n_m = re.search(r'(\d+\.?\d*)', text)
            if n_m:
                n = float(n_m.group(1))
                result = math.sqrt(n)
                display = int(result) if result == int(result) else round(result, 6)
                return f"\u221a{n_m.group(1)} = **`{display}`**"

        # घात / ghaat / power of
        power_m = re.search(
            r'(\d+)\s+ka\s+(\d+)\s+ghaat|(\d+)\s+(?:ghaat|power)\s+(\d+)',
            norm
        )
        if power_m:
            if power_m.group(1):
                base, exp = int(power_m.group(1)), int(power_m.group(2))
            else:
                base, exp = int(power_m.group(3)), int(power_m.group(4))
            result = base ** exp
            return f"`{base}^{exp}` = **`{result}`**"

        # Factorial
        if re.search(r'\bfactorial\b|\banukramank\b', norm):
            n_m = re.search(r'(\d+)', text)
            if n_m:
                n = int(n_m.group(1))
                if n <= 20:
                    return f"`{n}!` = **`{math.factorial(n)}`**"

        # Prime check
        if re.search(r'\b(prime|assal|maulik)\b', norm):
            n_m = re.search(r'(\d+)', text)
            if n_m:
                n = int(n_m.group(1))
                if n < 2:
                    return f"`{n}` prime **nahi hai**."
                is_prime = all(n % i != 0 for i in range(2, int(math.sqrt(n)) + 1))
                return f"`{n}` **{'prime hai' if is_prime else 'prime nahi hai'}**."

        # Fibonacci
        if re.search(r'\bfibonacci\b|\bfibo\b', norm):
            n_m = re.search(r'(\d+)', text)
            if n_m:
                n = int(n_m.group(1))
                if n <= 50:
                    a, b = 0, 1
                    for _ in range(n - 1):
                        a, b = b, a + b
                    return f"Fibonacci({n}) = **`{a if n == 1 else b}`**"

        return None

    # ── Response Generation ────────────────────────────────────────────────────────────────────

    @staticmethod
    def get_hindi_response(intent: str, context: dict | None = None) -> str:
        """
        Generate a Hindi response for the given intent key.

        Parameters:
            intent: Intent key from map_hindi_intent()
            context: Optional dict with template substitution values
        Returns: Formatted Hindi response string
        Edge cases: Unknown intent returns the fallback template
        """
        template = _HI_RESPONSES.get(intent, _HI_RESPONSES['fallback'])

        if context:
            for key, value in context.items():
                template = template.replace(f"{{{key}}}", str(value))

        return template

    # ── Main Entry Point ───────────────────────────────────────────────────────────────────────

    @classmethod
    def process(cls, text: str) -> Optional[str]:
        """
        Primary entry point. Detects language and processes Hindi/Hinglish input.

        Parameters:
            text: Raw user input string
        Returns: Hindi/bilingual response string, or None if language is English
        Edge cases: Returns None for English inputs (let BackupCore handle normally)
        """
        lang = cls.detect_language(text)
        if lang != 'hi':
            return None  # English → BackupCore handles it

        # 1. Check for OS commands first
        os_cmd = cls.extract_hindi_os_command(text)
        if os_cmd:
            action, target = os_cmd
            # Return a special marker that App.py/_reason can route to AutomationCore
            return f"__OS_CMD__{action}:{target}"

        # 2. Try math
        math_result = cls.extract_hindi_math(text)
        if math_result:
            return math_result

        # 3. Map intent
        intent = cls.map_hindi_intent(text)
        if intent and intent.startswith('math_'):
            return _HI_RESPONSES.get('fallback')  # math without numbers

        if intent:
            return cls.get_hindi_response(intent)

        # 4. Hindi fallback
        return _HI_RESPONSES['fallback']
