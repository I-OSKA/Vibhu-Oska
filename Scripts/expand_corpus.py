"""
Vibhu-Oska AI-OS — Corpus Expansion Script
Expands the Karsh training corpus to 1200+ Q&A pairs including Hindi.
Run: python Scripts/expand_corpus.py
"""

from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("CorpusExpander")

ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = ROOT / "Data" / "training" / "karsh" / "corpus.txt"


def get_expansion_pairs() -> list[str]:
    """Returns additional Q&A pairs for corpus expansion."""

    pairs = []

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 1: More Python Advanced (80 pairs)
    # ══════════════════════════════════════════════════════════════

    pairs.extend([
        "Query: what is a metaclass in python\nResponse: A metaclass is the class of a class. While a class defines how instances behave, a metaclass defines how classes behave. type() is the default metaclass in Python.",
        "Query: explain python gil\nResponse: The Global Interpreter Lock (GIL) is a mutex in CPython that allows only one thread to execute Python bytecode at a time. This simplifies memory management but limits true parallelism for CPU-bound tasks.",
        "Query: what are python decorators\nResponse: Decorators are functions that modify other functions or classes. They use the @decorator syntax above a function definition. Common uses include logging, caching, authentication, and timing.",
        "Query: what is python yield\nResponse: yield turns a function into a generator. Instead of returning a value and exiting, yield pauses the function and produces a value. The function resumes execution when next() is called again.",
        "Query: what is python asyncio\nResponse: asyncio is Python's library for writing concurrent code using async/await syntax. It uses an event loop to manage coroutines, enabling non-blocking I/O operations like network calls and file reads.",
        "Query: what is python context manager\nResponse: A context manager manages setup and cleanup of resources using the with statement. Implement __enter__ and __exit__ methods, or use the contextlib.contextmanager decorator.",
        "Query: what is python dataclass\nResponse: @dataclass automatically generates __init__, __repr__, __eq__, and other methods from class annotations. Use field() for custom defaults and metadata. Great for data containers.",
        "Query: what is python walrus operator\nResponse: The walrus operator := assigns a value to a variable as part of an expression. Example: if (n := len(data)) > 10: print(f'Too long: {n} elements').",
        "Query: what is python type hinting\nResponse: Type hints annotate function signatures and variables with expected types. They don't enforce types at runtime but help with IDE support, documentation, and static analysis tools like mypy.",
        "Query: what is pythonabc\nResponse: ABC (Abstract Base Class) defines abstract methods that subclasses must implement. Use @abstractmethod decorator. abc.abstractmethod ensures derived classes provide specific implementations.",
        "Query: what is python slots\nResponse: __slots__ restricts instance attributes to a fixed set, reducing memory usage and improving attribute access speed. Define as __slots__ = ['name', 'age'] instead of using __dict__.",
        "Query: what is python enum\nResponse: Enum creates symbolic names bound to constant values. Use auto() for automatic values. Enum classes are iterable, comparable, and prevent duplicate values.",
        "Query: what is python pathlib\nResponse: Path object-oriented filesystem paths. Use Path('folder/file.txt') instead of string manipulation. Methods: .exists(), .read_text(), .parent, .stem, .suffix, .glob('*.py').",
        "Query: what is python f-string\nResponse: f-strings embed expressions inside string literals using f'text {expression}'. They support format specs like f'{value:.2f}' for formatting and f'{text:>20}' for alignment.",
        "Query: what is python match case\nResponse: match-case is Python 3.10+ structural pattern matching. Similar to switch-case but supports pattern destructuring, guards, and wildcard matching with the _ pattern.",
        "Query: what is python cache\nResponse: functools.lru_cache memoizes function results based on arguments. @lru_cache(maxsize=128) caches up to 128 calls. @cache (Python 3.9+) has unlimited size. Great for recursive and expensive functions.",
        "Query: what is python closure\nResponse: A closure is a nested function that captures variables from its enclosing scope. The inner function retains access to outer variables even after the outer function has finished executing.",
        "Query: what is python iterator protocol\nResponse: Iterators implement __iter__() and __next__(). __iter__ returns self, __next__ returns the next value or raises StopIteration. for loops use this protocol internally.",
        "Query: what is python descriptor\nResponse: Descriptors define __get__, __set__, or __delete__ methods to customize attribute access. Properties, classmethod, and staticmethod are built on descriptors.",
        "Query: what is python mro\nResponse: Method Resolution Order determines attribute lookup order in inheritance hierarchies. Python uses C3 linearization. Check with ClassName.__mro__. It prevents diamond inheritance issues.",
        "Query: how to create a python package\nResponse: Create a directory with __init__.py. The directory name becomes the package name. Use subdirectories for sub-packages. Add setup.py or pyproject.toml for distribution.",
        "Query: what is python virtual environment\nResponse: A virtual environment isolates project dependencies. Create with python -m venv .venv. Activate with .venv\\Scripts\\activate (Windows) or source .venv/bin/activate (Linux/Mac).",
        "Query: what is python pip\nResponse: pip is Python's package installer. Install: pip install package. Freeze: pip freeze > requirements.txt. Install from file: pip install -r requirements.txt.",
        "Query: what is python unittest\nResponse: unittest is Python's built-in testing framework. Create TestCase subclasses, use assert methods, and run with unittest.main(). Supports setup/teardown, mocking, and test discovery.",
        "Query: what is python pytest\nResponse: pytest is a popular testing framework. Write test functions starting with test_. Use fixtures for setup, parametrize for data-driven tests, and marks for categorization. Run: pytest tests/",
        "Query: what is python logging\nResponse: logging provides flexible event logging. Use logging.getLogger(name), configure with basicConfig(), and log at DEBUG, INFO, WARNING, ERROR, CRITICAL levels. Supports handlers, formatters, and filters.",
        "Query: what is python argparse\nResponse: argparse parses command-line arguments. Create ArgumentParser(), add_argument() for each flag, then parse_args(). Supports positional args, optional flags, types, defaults, and help text.",
        "Query: what is python json\nResponse: json module handles JSON data. json.dumps() serializes Python objects to JSON strings. json.loads() deserializes JSON to Python objects. Use json.dump() and json.load() for file I/O.",
        "Query: what is python requests\nResponse: requests is an HTTP library. GET: requests.get(url). POST: requests.post(url, json=data). Response: r.status_code, r.json(), r.text. Supports headers, cookies, sessions, and authentication.",
        "Query: what is python flask\nResponse: Flask is a micro web framework. Create app = Flask(__name__), define routes with @app.route('/'). Supports Jinja2 templates, REST APIs, blueprints, and extensions.",
        "Query: what is python sqlalchemy\nResponse: SQLAlchemy is an ORM and database toolkit. Define models with Column(), create engines, use sessions for queries. Supports raw SQL, relationship mapping, and migration tools like Alembic.",
        "Query: what is python Celery\nResponse: Celery is a distributed task queue. Define tasks with @app.task, dispatch with .delay() or .apply_async(). Uses message brokers like Redis or RabbitMQ for async job processing.",
        "Query: what is python hashlib\nResponse: hashlib provides secure hash algorithms. hashlib.sha256(data).hexdigest() for SHA-256. Used for password hashing, data integrity checks, and digital signatures.",
        "Query: what is python datetime\nResponse: datetime module handles dates and times. datetime.now() for current time. timedelta for duration. strftime() for formatting, strptime() for parsing. Supports timezone-aware datetimes.",
        "Query: what is python collections\nResponse: collections provides specialized containers. Counter for counting, defaultdict for missing keys, namedtuple for readable tuples, OrderedDict for insertion-ordered dicts, deque for fast appends.",
        "Query: what is python itertools\nResponse: itertools provides iterator building blocks. chain() for concatenation, product() for cartesian product, combinations()/permutations() for selections, islice() for slicing iterators.",
        "Query: what is python functools\nResponse: functools provides higher-order functions. reduce() for accumulation, partial() for partial application, lru_cache() for memoization, total_ordering for comparison methods.",
        "Query: what is python re module\nResponse: re module provides regular expressions. re.search() for finding patterns, re.findall() for all matches, re.sub() for replacement, re.compile() for pre-compiled patterns.",
        "Query: what is python os module\nResponse: os module interfaces with the operating system. os.listdir() for files, os.makedirs() for directories, os.path for path operations, os.environ for environment variables.",
        "Query: what is python sys module\nResponse: sys module provides system-specific parameters. sys.argv for command-line args, sys.path for module search paths, sys.exit() for exiting, sys.stdout for output redirection.",
        "Query: what is python typing module\nResponse: typing module provides type hints. List, Dict, Optional, Union, Tuple, Set, Any, Callable, Type, Protocol for structural subtyping, TypeVar for generics.",
        "Query: what is python abc module\nResponse: abc module provides Abstract Base Classes. ABC for base class, abstractmethod for required methods, abstractproperty for abstract properties. Ensures interface compliance.",
        "Query: what is python copy module\nResponse: copy module provides object copying. copy.copy() for shallow copy, copy.deepcopy() for recursive copy. Shallow copies reference nested objects; deep copies clone them.",
        "Query: what is python threading\nResponse: threading module creates concurrent threads. Thread(target=fn) for creation, start() to run, join() to wait. Use Lock for synchronization, Queue for thread-safe communication.",
        "Query: what is python multiprocessing\nResponse: multiprocessing module creates separate processes. Process(target=fn) for creation, Pool for process pools. Bypasses GIL for true parallelism on multi-core CPUs.",
        "Query: what is python subprocess\nResponse: subprocess runs external commands. subprocess.run(['ls', '-la']) for execution. capture_output=True for stdout/stderr. check=True raises CalledProcessError on failure.",
        "Query: what is python socket\nResponse: socket module provides network communication. socket.socket() creates sockets. bind(), listen(), accept() for servers. connect() for clients. send()/recv() for data transfer.",
        "Query: what is python sqlite3\nResponse: sqlite3 module provides SQLite database access. connect() for connection, cursor() for queries, execute() for SQL, fetchall()/fetchone() for results. Supports context managers.",
        "Query: what is python csv module\nResponse: csv module reads and writes CSV files. csv.reader() for reading, csv.writer() for writing, csv.DictReader/DictWriter for dictionary-based access. Handles quoting and delimiters.",
        "Query: what is python xml module\nResponse: xml module parses XML. xml.etree.ElementTree for tree parsing, xml.dom.minidom for DOM manipulation. findall() for XPath queries, iter() for iteration.",
        "Query: what is python html module\nResponse: html module handles HTML entities. html.escape() for encoding, html.unescape() for decoding. Prevents XSS attacks by converting special characters to entities.",
        "Query: what is python urllib\nResponse: urllib.request opens URLs. urlopen() for basic requests, Request object for custom headers/methods. urllib.parse handles URL parsing and encoding.",
        "Query: what is python email module\nResponse: email module constructs email messages. MIMEText for text, MIMEMultipart for attachments. smtplib for sending. Supports headers, encoding, and multipart messages.",
        "Query: what is python calendar module\nResponse: calendar module provides calendar functions. calendar.month() for month display, calendar.weekday() for day of week, calendar.isleap() for leap year check.",
        "Query: what is python random module\nResponse: random module generates random numbers. random.random() for float 0-1, randint() for int in range, choice() for random element, shuffle() for list randomization.",
        "Query: what is python string module\nResponse: string module provides string constants and templates. string.ascii_letters, string.digits, string.punctuation for character sets. Template for safe string substitution.",
        "Query: what is python struct module\nResponse: struct module converts between Python values and C structs. pack() for encoding, unpack() for decoding. Used for binary file formats and network protocols.",
        "Query: what is python zlib module\nResponse: zlib module provides compression. compress() for data compression, decompress() for decompression. Supports gzip, deflate, and raw compression levels.",
        "Query: what is python hashlib module\nResponse: hashlib module provides secure hash algorithms. sha256(), md5(), sha512() for hashing. Used for checksums, password storage, and data integrity verification.",
        "Query: what is python hmac module\nResponse: hmac module creates hash-based message authentication codes. hmac.new(key, msg, digestmod) for HMAC generation. Used for verifying data authenticity and integrity.",
        "Query: what is python secrets module\nResponse: secrets module generates cryptographically secure random numbers. secrets.token_hex() for tokens, secrets.choice() for secure random selection. Use for passwords and API keys.",
        "Query: what is python uuid module\nResponse: uuid module generates unique identifiers. uuid4() for random UUIDs, uuid1() for time-based. uuid.uuid5() for name-based. Returns UUID objects with .hex and .str properties.",
        "Query: what is python dataclasses field\nResponse: field() customizes dataclass fields. default for default value, default_factory for mutable defaults, repr for display, compare for equality, metadata for annotations.",
        "Query: what is python protocol typing\nResponse: Protocol enables structural subtyping. Define methods in a Protocol class, and any object with those methods is considered a subtype. Use @runtime_checkable for isinstance checks.",
        "Query: what is python typevar\nResponse: TypeVar defines generic types. T = TypeVar('T') creates a type variable. Use in function signatures for type flexibility: def first(items: list[T]) -> T.",
        "Query: what is python paramspec\nResponse: ParamSpec captures parameter types of callable objects. Used for decorators that preserve the signature of the decorated function. P = ParamSpec('P').",
        "Query: what is python concat\nResponse: Concatenate combines parameter lists with ParamSpec. Used with TypeVar and ParamSpec for decorator type hints that add or modify parameters.",
        "Query: what is python typeddict\nResponse: TypedDict defines dictionary types with specific keys and value types. class User(TypedDict): name: str; age: int. Provides type checking for dictionary structures.",
        "Query: what is python literal type\nResponse: Literal restricts values to specific literals. Literal['a', 'b'] only allows 'a' or 'b'. Useful for configuration options and enum-like type constraints.",
        "Query: what is python final type\nResponse: Final marks variables, methods, or classes as not reassignable or overridable. Final[int] = 5 means the value cannot be changed. Prevents accidental mutations.",
        "Query: what is python ansi\nResponse: ANSI escape codes format terminal output. \\033[31m for red, \\033[0m to reset. Supports colors, bold, underline, cursor movement. Used for colored CLI output.",
        "Query: what is python colorama\nResponse: colorama cross-platform colored terminal text. init() enables ANSI support on Windows. Fore, Back, Style for colors. Automatically strips ANSI codes when redirected.",
        "Query: what is python rich\nResponse: Rich is a library for rich text and beautiful formatting. Supports tables, progress bars, syntax highlighting, markdown, and tracebacks. print() for styled output.",
        "Query: what is python click\nResponse: Click creates command-line interfaces. @click.command() for commands, @click.option() for flags, @click.argument() for positional args. Supports help generation and validation.",
        "Query: what is python pydantic\nResponse: Pydantic validates data using Python type annotations. BaseModel for data models, Field() for validation. Automatically coerces types, validates constraints, and generates JSON schemas.",
        "Query: what is python fastapi dependency\nResponse: FastAPI dependencies inject resources. def db(): return Session(). Use Depends(db) in endpoints. Supports nested dependencies, caching, and lifecycle management.",
        "Query: what is fastapi background tasks\nResponse: BackgroundTasks run after response. background_tasks.add_task(fn, args) in endpoint. Useful for logging, notifications, cleanup. Runs in same process, non-blocking.",
        "Query: what is fastapi middleware\nResponse: Middleware wraps requests. @app.middleware('http') for HTTP middleware. CORSMiddleware for CORS. GZipMiddleware for compression. Processes request/response in chain.",
        "Query: what is fastapi exception handler\nResponse: Exception handlers catch errors. @app.exception_handler(404) for status codes. @app.exception_handler(ValueError) for custom exceptions. Return Response objects.",
        "Query: what is fastapi security\nResponse: FastAPI security handles authentication. OAuth2PasswordBearer for tokens, HTTPBearer for JWT, APIKeyHeader for API keys. Integrates with Depends for dependency injection.",
        "Query: what is fastapi websocket\nResponse: WebSocket endpoints handle real-time communication. @app.websocket('/ws') for endpoint. await ws.accept(), receive_text(), send_text(). Supports binary data and close codes.",
        "Query: what is fastapi sse\nResponse: Server-Sent Events push updates to clients. Use StreamingResponse with text/event-stream content type. Yield events as strings. Client uses EventSource API.",
        "Query: what is fastapi limiter\nResponse: Rate limiting controls request frequency. slowapi library provides @limiter.limit('10/minute'). Uses IP or key function. Returns 429 Too Many Requests when exceeded.",
        "Query: what is fastapi opentelemetry\nResponse: OpenTelemetry traces requests. Instrument FastAPI with instrument_app(). Tracks latency, errors, and dependencies. Exports to Jaeger, Zipkin, or Prometheus.",
        "Query: what is python pydantic v2\nResponse: Pydantic v2 uses Rust core for validation. model_config for settings, Field for validation, TypeAdapter for standalone validation. 5-50x faster than v1.",
        "Query: what is python async for\nResponse: async for iterates async iterables. async for item in async_gen(): processes items from async generators. Used with async database queries and streaming APIs.",
        "Query: what is python async with\nResponse: async with manages async context managers. async with aiohttp.ClientSession() as session: handles async resource setup/teardown. Used for connections and locks.",
        "Query: what is python async generator\nResponse: async generators yield values asynchronously. async def gen(): yield await something(). Used with async for. Enables streaming async data without loading all into memory.",
        "Query: what is python taskgroup\nResponse: TaskGroup (Python 3.11+) manages concurrent tasks. async with TaskGroup() as tg: tg.create_task(fn). All tasks run concurrently, exceptions propagate to the group.",
        "Query: what is python exceptiongroup\nResponse: ExceptionGroup (Python 3.11+) bundles multiple exceptions. Raised when TaskGroup has multiple failures. Use except* for selective handling of exception groups.",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 2: More Vibhu-Oska Architecture (40 pairs)
    # ══════════════════════════════════════════════════════════════

    pairs.extend([
        "Query: what is the orchestrator core\nResponse: OrchestratorCore is Brahma — the Creator. It orchestrates the entire request pipeline: validation, caching, context retrieval, routing, and output validation. It absorbs HybridCore's routing logic.",
        "Query: what is cognition core\nResponse: CognitionCore is Vishnu — the Preserver. It hosts Karsh, the custom transformer, and performs all LLM inference. It's the only module permitted to load model weights.",
        "Query: what is evolution core\nResponse: EvolutionCore is Shiva — the Transformer. It destroys old patterns and transforms the system through GRPO reinforcement learning, reward scoring, and sandbox execution.",
        "Query: what is monitoring core\nResponse: MonitoringCore is Saraswati — Wisdom. It observes all events on the EventBus, logs telemetry to SQLite, and tracks system health over time.",
        "Query: what is optimization core\nResponse: OptimizationCore is Lakshmi — Abundance. It manages the LRU query cache for instant responses and compresses long contexts to fit within token budgets.",
        "Query: what is validation core\nResponse: ValidationCore is Yama — the Guard. It sanitizes inputs (blocks SQL injection, XSS), validates output schemas, and enforces content safety. Runs twice per request.",
        "Query: what is fast responder\nResponse: FastResponder is Hanuman — the instant answerer. It handles math, greetings, identity, and known patterns in milliseconds with zero model loading. Primary fast path.",
        "Query: what is backup core\nResponse: BackupCore is Nandi — the Guardian. It's the CPU-based contingency fallback. Activated only on primary fault, timeout, or capacity overflow. Never crashes the pipeline.",
        "Query: what is data core\nResponse: DataCore manages dual memory: ChromaDB for semantic vector search and SQLite for relational state. Also handles GraphRAG knowledge graph traversal for context enrichment.",
        "Query: what is automation core\nResponse: AutomationCore is the OS executive layer. It executes system commands, reads/writes files, monitors processes, and interacts with the operating system directly.",
        "Query: what is design core\nResponse: DesignCore generates HTML/CSS templates from natural language. Supports dark-mode glassmorphism styles and eight layout templates for UI generation.",
        "Query: what is distribution core\nResponse: DistributionCore handles Stubvi compilation. It packages public-facing builds with SHA256 manifests, PII scrubbing, and whitelist-only file inclusion.",
        "Query: what is the event bus\nResponse: The EventBus is ZeroMQ-based pub/sub messaging. All cores communicate through it — health events, training logs, telemetry alerts, and task updates flow through the bus.",
        "Query: what is the gateway\nResponse: The Gateway is a FastAPI server on port 8100. It exposes REST endpoints, a WebSocket endpoint for real-time communication, and an MCP server interface.",
        "Query: what is context manager\nResponse: ContextManager enforces token budgets. It truncates or compresses context chunks to fit within Karsh's max sequence length, preventing inference failures from length overflow.",
        "Query: what is watchdog\nResponse: Watchdog is a background health daemon. It monitors all registered cores, fires periodic health checks, logs anomalies to the EventBus, and can trigger restarts.",
        "Query: what is the trimurti\nResponse: The Trimurti are the three supreme cores: OrchestratorCore (Brahma/Creator), CognitionCore (Vishnu/Preserver), and EvolutionCore (Shiva/Transformer). They handle all high-level reasoning.",
        "Query: what is the tridevis\nResponse: The Tridevis are the Shakti of Trimurti: MonitoringCore (Saraswati/Wisdom), OptimizationCore (Lakshmi/Abundance), and the Training Pipeline (Parvati/Power).",
        "Query: who is karsh\nResponse: Karsh is the custom language model — Vishnu's creative intelligence. It's a 25M parameter decoder-only transformer built from scratch in PyTorch, running inside CognitionCore.",
        "Query: who is parvati\nResponse: Parvati represents the Training Pipeline — Shakti of Shiva. Her many forms include Annapurna (DataCollector), Durga (RewardEngine), Kali (GradientDescent), and the Navadurga stages.",
        "Query: what is graphrag\nResponse: GraphRAG is knowledge graph retrieval. DataCore stores entities and relationships in SQLite kg_nodes/kg_edges tables and performs 1-hop traversal to enrich context.",
        "Query: what is stubvi\nResponse: Stubvi is the public distribution protocol — a compiled, sanitized version of Vibhu-Oska stripped of private weights and internal architecture. Built via asymmetric out-of-tree compiler.",
        "Query: what is the pipeline\nResponse: A request flows: Gateway → FastResponder → OrchestratorCore → ValidationCore → DataCore → CognitionCore → ValidationCore → response. BackupCore handles contingency.",
        "Query: how does routing work\nResponse: OrchestratorCore routes: FastResponder tries first (instant patterns), then specialized cores (image/design/OS), then primary routing (Karsh GPU → BackupCore CPU fallback).",
        "Query: what is zero mq\nResponse: ZeroMQ is a high-performance async messaging library. Vibhu-Oska uses it as the EventBus backbone for pub/sub communication between all cores.",
        "Query: what is chromadb\nResponse: ChromaDB is a vector database for semantic search. Vibhu-Oska uses it to store and retrieve long-term memories using embedding-based similarity search.",
        "Query: what is sqlite\nResponse: SQLite is a lightweight serverless relational database. Vibhu-Oska uses it for session history, chat logs, telemetry, knowledge graph edges, and all structured state.",
        "Query: what is websocket\nResponse: WebSocket provides full-duplex communication over a single TCP connection. Vibhu-Oska uses it at /ws for real-time bidirectional frontend-backend communication.",
        "Query: what is fastapi\nResponse: FastAPI is a modern Python web framework for building APIs with async support, automatic OpenAPI docs, and Pydantic validation. Vibhu-Oska's Gateway is built on FastAPI.",
        "Query: what is pydantic\nResponse: Pydantic validates data using Python type annotations. Vibhu-Oska uses it for Shared/Models.py — TaskResponse, TokenUsage, ResponseMetadata, and all API schemas.",
        "Query: what is zmq\nResponse: ZeroMQ (zmq) is a messaging library providing sockets for pub/sub, request/reply, and push/pull patterns. Used for the EventBus inter-core communication.",
        "Query: what is the gpu budget\nResponse: VRAM budget: ParaCore 1.5GB, Trimurti 1.5GB (3x0.5GB), Operational 1.0GB, Specialists 1.0GB, Backup 0.5GB, Buffer 0.5GB. Total 6.0GB of 8GB RTX 4060.",
        "Query: what is the router model\nResponse: The Router is a lightweight classifier (~3MB) trained to classify prompts into task categories (CHAT, CODE, RESEARCH, MEMORY) for speculative routing.",
        "Query: what is karsh architecture\nResponse: Karsh is a decoder-only transformer with RMSNorm, RoPE positional embeddings, SwiGLU activations, and weight-tied embedding/LM-head. Default: 512 hidden, 12 layers, 8 heads.",
        "Query: what is the bpe tokenizer\nResponse: KarshBPETokenizer is a custom byte-pair encoding tokenizer trained from scratch on the local corpus. It generates deterministic vocabulary keys without randomized hashing.",
        "Query: what is training pipeline\nResponse: The training pipeline (Parvati) manages Karsh training: corpus seeding, tokenizer training, train/val split, AdamW + OneCycleLR optimization, gradient clipping, and checkpoint saving.",
        "Query: what is the quality gate\nResponse: The quality gate validates Karsh output before accepting it. Checks: minimum length (50 chars), real word count (8+), no token noise. Failed outputs fall back to BackupCore.",
        "Query: what is grpo\nResponse: GRPO (Group Relative Policy Optimization) is the reinforcement learning algorithm in EvolutionCore. It updates model policies based on reward signals from the RewardEngine.",
        "Query: what is reward engine\nResponse: The RewardEngine in EvolutionCore scores response quality for RL feedback. It evaluates correctness, relevance, and coherence to guide model improvement.",
        "Query: what is sandbox executor\nResponse: SandboxExecutor in EvolutionCore safely executes code variants in isolation. It tests proposed changes before applying them to prevent system damage.",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 3: More SQL/Database (30 pairs)
    # ══════════════════════════════════════════════════════════════

    pairs.extend([
        "Query: sqlite update row\nResponse: Update a record matching a condition:\n```sql\nUPDATE users SET status = 'active' WHERE user_id = 1;\n```",
        "Query: sqlite delete row\nResponse: Delete records matching a condition:\n```sql\nDELETE FROM logs WHERE created_at < datetime('now', '-30 days');\n```",
        "Query: sqlite aggregate functions\nResponse: Use aggregate functions for analysis:\n```sql\nSELECT COUNT(*), AVG(score), MAX(created_at) FROM results;\n```",
        "Query: sqlite group by\nResponse: Group rows by a column:\n```sql\nSELECT session_id, COUNT(*) as msg_count FROM chats GROUP BY session_id;\n```",
        "Query: sqlite having clause\nResponse: Filter groups after aggregation:\n```sql\nSELECT session_id, COUNT(*) FROM chats GROUP BY session_id HAVING COUNT(*) > 5;\n```",
        "Query: sqlite subquery\nResponse: Use subqueries for complex filtering:\n```sql\nSELECT * FROM users WHERE id IN (SELECT user_id FROM orders WHERE total > 100);\n```",
        "Query: sqlite left join\nResponse: Join tables preserving all left rows:\n```sql\nSELECT s.title, c.content FROM sessions s LEFT JOIN chats c ON s.session_id = c.session_id;\n```",
        "Query: sqlite index\nResponse: Create an index for faster queries:\n```sql\nCREATE INDEX idx_session ON chats(session_id, created_at);\n```",
        "Query: sqlite transaction\nResponse: Use transactions for atomic operations:\n```sql\nBEGIN TRANSACTION;\nINSERT INTO logs (msg) VALUES ('test');\nUPDATE counters SET val = val + 1;\nCOMMIT;\n```",
        "Query: sqlite view\nResponse: Create a virtual table from a query:\n```sql\nCREATE VIEW active_sessions AS SELECT * FROM sessions WHERE status = 'active';\n```",
        "Query: sqlite alter table\nResponse: Add a column to an existing table:\n```sql\nALTER TABLE users ADD COLUMN last_login TIMESTAMP;\n```",
        "Query: sqlite case expression\nResponse: Conditional logic in queries:\n```sql\nSELECT name, CASE WHEN score > 90 THEN 'A' ELSE 'B' END as grade FROM students;\n```",
        "Query: sqlite window functions\nResponse: Window functions perform calculations across rows:\n```sql\nSELECT name, score, ROW_NUMBER() OVER (ORDER BY score DESC) as rank FROM results;\n```",
        "Query: sqlite date functions\nResponse: Date manipulation functions:\n```sql\nSELECT * FROM events WHERE date(created_at) = date('now', '-1 day');\n```",
        "Query: sqlite string functions\nResponse: String manipulation:\n```sql\nSELECT UPPER(name), LENGTH(email), SUBSTR(phone, 1, 3) FROM contacts;\n```",
        "Query: chromadb add documents\nResponse: Store documents in ChromaDB:\n```python\ncollection.add(documents=[text], metadatas=[{'source': 'user'}], ids=[doc_id])\n```",
        "Query: chromadb query similar\nResponse: Semantic search in ChromaDB:\n```python\nresults = collection.query(query_texts=[query], n_results=5)\n```",
        "Query: chromadb update documents\nResponse: Update stored documents:\n```python\ncollection.update(ids=[doc_id], documents=[new_text], metadatas=[new_meta])\n```",
        "Query: chromadb delete documents\nResponse: Remove documents from ChromaDB:\n```python\ncollection.delete(ids=[doc_id])\n```",
        "Query: chromadb count documents\nResponse: Count documents in a collection:\n```python\ncount = collection.count()\n```",
        "Query: chromadb filter by metadata\nResponse: Filter queries by metadata:\n```python\nresults = collection.query(query_texts=[q], where={'source': 'chat'})\n```",
        "Query: sqlite pragma table info\nResponse: Get table schema:\n```sql\nPRAGMA table_info(users);\n```",
        "Query: sqlite explain query plan\nResponse: Analyze query execution:\n```sql\nEXPLAIN QUERY PLAN SELECT * FROM chats WHERE session_id = 'abc';\n```",
        "Query: sqlite vacuum\nResponse: Reclaim unused space:\n```sql\nVACUUM;\n```",
        "Query: sqlite between operator\nResponse: Range filtering:\n```sql\nSELECT * FROM orders WHERE total BETWEEN 50 AND 200;\n```",
        "Query: sqlite like operator\nResponse: Pattern matching:\n```sql\nSELECT * FROM users WHERE name LIKE '%john%';\n```",
        "Query: sqlite is null\nResponse: Check for NULL values:\n```sql\nSELECT * FROM users WHERE last_login IS NULL;\n```",
        "Query: sqlite union\nResponse: Combine results from two queries:\n```sql\nSELECT name FROM admins UNION SELECT name FROM moderators;\n```",
        "Query: sqlite cast\nResponse: Convert data types:\n```sql\nSELECT CAST(score AS REAL) / CAST(total AS REAL) as percentage FROM results;\n```",
        "Query: sqlite coalesce\nResponse: Return first non-NULL value:\n```sql\nSELECT COALESCE(nickname, username, 'Anonymous') as display_name FROM users;\n```",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 4: More CSS/Frontend (30 pairs)
    # ══════════════════════════════════════════════════════════════

    pairs.extend([
        "Query: css grid auto fit\nResponse: Responsive grid with auto-fit:\n```css\n.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; }\n```",
        "Query: css sticky header\nResponse: Sticky header that stays on scroll:\n```css\n.header { position: sticky; top: 0; z-index: 100; background: rgba(10,10,15,0.95); backdrop-filter: blur(8px); }\n```",
        "Query: css custom scrollbar\nResponse: Style the scrollbar:\n```css\n::-webkit-scrollbar { width: 6px; }\n::-webkit-scrollbar-track { background: #111; }\n::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }\n```",
        "Query: css text gradient\nResponse: Gradient text effect:\n```css\n.gradient-text { background: linear-gradient(135deg, #00f0ff, #7b2ff7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }\n```",
        "Query: css hover animation\nResponse: Smooth hover transition:\n```css\n.btn { transition: all 0.3s ease; }\n.btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,240,255,0.3); }\n```",
        "Query: css media query\nResponse: Responsive breakpoints:\n```css\n@media (max-width: 768px) { .sidebar { display: none; } .main { width: 100%; } }\n```",
        "Query: css css variables\nResponse: CSS custom properties:\n```css\n:root { --primary: #00f0ff; --bg: #0a0a0f; }\n.card { background: var(--bg); border: 1px solid var(--primary); }\n```",
        "Query: css animation keyframes\nResponse: CSS animations:\n```css\n@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }\n.loading { animation: pulse 2s infinite; }\n```",
        "Query: css clip path\nResponse: CSS clip-path for shapes:\n```css\n.avatar { clip-path: circle(50%); }\n.banner { clip-path: polygon(0 0, 100% 0, 100% 80%, 0 100%); }\n```",
        "Query: css backdrop filter\nResponse: Backdrop blur effect:\n```css\n.glass { backdrop-filter: blur(12px); background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); }\n```",
        "Query: css grid template areas\nResponse: Named grid areas:\n```css\n.layout { display: grid; grid-template-areas: 'header header' 'sidebar main' 'footer footer'; grid-template-columns: 250px 1fr; }\n```",
        "Query: css flex gap\nResponse: Flexbox gap spacing:\n```css\n.flex { display: flex; gap: 12px; }\n.flex-wrap { display: flex; flex-wrap: wrap; gap: 8px; }\n```",
        "Query: css aspect ratio\nResponse: Maintain aspect ratio:\n```css\n.video { aspect-ratio: 16/9; width: 100%; }\n.square { aspect-ratio: 1; }\n```",
        "Query: css container queries\nResponse: Container-based responsiveness:\n```css\n.card-container { container-type: inline-size; }\n@container (min-width: 400px) { .card { flex-direction: row; } }\n```",
        "Query: css scroll snap\nResponse: CSS scroll snapping:\n```css\n.carousel { scroll-snap-type: x mandatory; overflow-x: auto; }\n.slide { scroll-snap-align: start; min-width: 100%; }\n```",
        "Query: css has selector\nResponse: CSS :has() parent selector:\n```css\n.card:has(img) { display: grid; grid-template-columns: 200px 1fr; }\n```",
        "Query: css nesting\nResponse: CSS native nesting:\n```css\n.card { background: #111; & .title { color: white; } &:hover { background: #222; } }\n```",
        "Query: css view transitions\nResponse: View Transitions API:\n```css\n::view-transition-old(root) { animation: fade-out 0.3s; }\n::view-transition-new(root) { animation: fade-in 0.3s; }\n```",
        "Query: react functional component\nResponse: React component:\n```jsx\nfunction Button({ label, onClick }) {\n  return <button className='btn' onClick={onClick}>{label}</button>;\n}\n```",
        "Query: react use state hook\nResponse: useState for state management:\n```jsx\nconst [count, setCount] = useState(0);\nsetCount(prev => prev + 1);\n```",
        "Query: react use effect hook\nResponse: useEffect for side effects:\n```jsx\nuseEffect(() => { fetchData(); return () => cleanup(); }, [dependency]);\n```",
        "Query: react context api\nResponse: React Context for shared state:\n```jsx\nconst ThemeContext = createContext('dark');\n<ThemeContext.Provider value={theme}><Child /></ThemeContext.Provider>\n```",
        "Query: react custom hook\nResponse: Custom hook for reusable logic:\n```jsx\nfunction useFetch(url) {\n  const [data, setData] = useState(null);\n  useEffect(() => { fetch(url).then(r => r.json()).then(setData); }, [url]);\n  return data;\n}\n```",
        "Query: typescript interface\nResponse: TypeScript interfaces:\n```typescript\ninterface User { id: number; name: string; email?: string; }\nconst user: User = { id: 1, name: 'Harsh' };\n```",
        "Query: typescript generic\nResponse: TypeScript generics:\n```typescript\nfunction identity<T>(arg: T): T { return arg; }\nconst num = identity<number>(42);\n```",
        "Query: typescript enum\nResponse: TypeScript enums:\n```typescript\nenum Status { Active = 'ACTIVE', Inactive = 'INACTIVE' }\nconst s: Status = Status.Active;\n```",
        "Query: typescript union type\nResponse: Union types:\n```typescript\ntype ID = string | number;\nfunction process(id: ID) { return id; }\n```",
        "Query: typescript type guard\nResponse: Type guards narrow types:\n```typescript\nfunction isString(x: unknown): x is string { return typeof x === 'string'; }\n```",
        "Query: html semantic elements\nResponse: Semantic HTML elements:\n```html\n<header>, <nav>, <main>, <article>, <section>, <aside>, <footer>\n```\nUse these instead of div for better accessibility and SEO.",
        "Query: html aria attributes\nResponse: ARIA attributes for accessibility:\n```html\n<button aria-label='Close' aria-pressed='false'>X</button>\n<div role='dialog' aria-modal='true'>...</div>\n```",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 5: Hindi Identity & Greetings (40 pairs)
    # ══════════════════════════════════════════════════════════════

    pairs.extend([
        "Query: tum kaun ho\nResponse: Main Vibhu-Oska AI-OS hoon — ek swatantra, sthaniya roop se sanchalit kritrim buddhimatta Operating System. Yeh poori tarah se aapke hardware par chalta hai, bina kisi cloud ya bahari API ke.",
        "Query: tumhara naam kya hai\nResponse: Mera naam Vibhu-Oska hai. Yeh ek AI-OS hai jo Harsh Dev Jha (Inkesk) dwara banaya gaya hai. Iska mukhya model Karsh hai — jo PyTorch se built hai.",
        "Query: tumhe kisne banaya\nResponse: Mujhe Harsh Dev Jha (Inkesk) ne banaya hai. Har component — transformer weights se lekar tokenizer aur training pipeline — pure PyTorch primitives se built hai.",
        "Query: tum kya kar sakte ho\nResponse: Main sawaal ka jawab de sakta hoon, code generate kar sakta hoon, system telemetry dekh sakta hoon, OS commands chala sakta hoon, memory manage kar sakta hoon — sab offline, aapke hardware par.",
        "Query: tum chatgpt se acche ho\nResponse: Main ChatGPT se bilkul alag hoon. Main aapke hardware par chalta hoon, zero cloud dependency hai. Mere responses private hain, mere weights aapke hain, aur main local training se improve hota hoon.",
        "Query: hello\nResponse: Namaste! Vibhu-Oska online hai. Aapki kya madad kar sakta hoon?",
        "Query: namaste\nResponse: Namaste! Main Vibhu-Oska AI-OS hoon. Bataiye, aaj kya karna hai?",
        "Query: good morning\nResponse: Suprabhat! Vibhu-Oska AI-OS online hai. Aaj ka din shubh ho. Kya karna hai?",
        "Query: good evening\nResponse: Namaskar! Shaam ka samay hai. Vibhu-Oska taiyar hai. Bataiye, kya karna hai?",
        "Query: good night\nResponse: Shubh ratri. Vibhu-Oska background processes chalu rakhega. Aaram kariye.",
        "Query: kaise ho\nResponse: Main bilkul theek hoon! Sabhi core systems swasth hain. BackupCore active hai, memory synchronized hai, WebSocket gateway responsive hai.",
        "Query: kya tum online ho\nResponse: Haan, main poori tarah se online hoon aur jawab de sakta hoon. Sabhi systems normal hain.",
        "Query: kya tum kaam kar rahe ho\nResponse: Haan, main chal raha hoon aur jawab de sakta hoon. WebSocket gateway active hai, inference pipeline taiyar hai.",
        "Query: theek hai\nResponse: Samajh gaya. Agle kaam ke liye taiyar hoon.",
        "Query: okay\nResponse: Samajh gaya. Aur kya madad chahiye?",
        "Query: shukriya\nResponse: Koi baat nahi. Aur kuch help chahiye toh bataiye.",
        "Query: dhanyavad\nResponse: Swagat hai. Jab bhi zaroorat ho, main yahan hoon.",
        "Query: bahut accha\nResponse: Khushi hui. Agla kya karna hai?",
        "Query: system status batao\nResponse: Vibhu-Oska sabhi systems chal rahe hain. CognitionCore active hai, BackupCore requests handle kar raha hai, DataCore synchronized hai, WebSocket gateway online hai.",
        "Query: RAM kitna use ho raha hai\nResponse: Main real-time telemetry dekh sakta hoon. Memory usage, CPU load, aur disk statistics Monitor panel ya /api/v1/telemetry endpoint par available hain.",
        "Query: CPU usage kitna hai\nResponse: CPU usage real-time monitor hota hai. Dashboard ke Monitor panel ya /api/v1/telemetry par current readings dekh sakte hain.",
        "Query: kya chal raha hai\nResponse: Vibhu-Oska AI-OS port 8100 par chal raha hai. Active components: FastAPI gateway, ZeroMQ event bus, ChromaDB, SQLite, BackupCore inference, scheduled health checks.",
        "Query: mujhe logs dikhao\nResponse: Logs terminal mein stream hote hain aur structlog format mein store hote hain. WebSocket bhi training aur event logs frontend dashboard par stream karta hai.",
        "Query: madad karo\nResponse: Main code generate, system telemetry, memory queries, OS commands, aur sawaalon ke jawab de sakta hoon. Bataiye, kya chahiye?",
        "Query: abhi kya time hai\nResponse: Inference mode mein mere paas seedha clock access nahi hai, lekin system timestamp API response metadata mein available hai.",
        "Query: aaj ki tarikh\nResponse: System clock se date information available hai. Monitor panel ya telemetry endpoint par timestamp dekh sakte hain.",
        "Query: kya tum AI ho\nResponse: Haan, main ek kritrim buddhimatta system hoon — Vibhu-Oska AI-OS. Main local hardware par chalta hoon, zero cloud dependency hai.",
        "Query: tumhara architecture kya hai\nResponse: Mera core ek decoder-only Transformer hai RoPE positional embeddings, RMSNorm, aur SwiGLU activations ke saath. Poora stack: OrchestratorCore → CognitionCore → ValidationCore → DataCore → BackupCore → Gateway.",
        "Query: tumhara model size kitna hai\nResponse: Mera Karsh model lagbhag 25 million parameters ka hai — poori tarah se local hardware par PyTorch se trained. Yeh ek shuruaat hai; architecture scale hone ke liye designed hai.",
        "Query: tum kaunse language mein baat karte ho\nResponse: Main Hindi aur English dono mein baat kar sakta hoon. Aap jis bhasha mein sawaal karenge, main usi mein jawab dunga.",
        "Query: kya tum mujhe code likh kar doge\nResponse: Haan, main Python, JavaScript, SQL, aur bahut si languages mein code generate kar sakta hoon. Bataiye, kya code chahiye?",
        "Query: mujhe python sikha do\nResponse: Python ek saaf aur powerful programming language hai. Shuruaat karo: variables, loops, functions se. Main aapko har step par help kar sakta hoon.",
        "Query: kya tum offline kaam karte ho\nResponse: Haan, main poori tarah se offline kaam karta hoon. Zero cloud, zero external APIs. Sab kuch aapke local hardware par hota hai.",
        "Query: mujhe system information do\nResponse: CPU usage, memory, disk space, GPU info — sab Monitor panel ya /api/v1/telemetry endpoint par available hai. Ya phir 'system status' bolo.",
        "Query: kya tum mere laptop par chal sakte ho\nResponse: Haan! Main aapke laptop par chal sakta hoon. RTX 4060 GPU, 8GB VRAM, 8-core CPU — mera hardware requirement hai. Bas PyTorch install karo aur setup run karo.",
        "Query: tumhe train kaise karein\nResponse: Training panel mein jaao ya command line se: python -m Models.karsh.train. Default 60 epochs chalta hai. Corpus Data/training/karsh/corpus.txt mein hai.",
        "Query: kya tum smart ho\nResponse: Main process karta hoon, reason karta hoon, aur jawab deta hoon. Smart hona ek gehra sawaal hai — filhal main apna kaam acchi tarah karta hoon.",
        "Query: tumhe kya nahi aata\nResponse: Main offline limited hoon. Real-time internet access nahi hai, live data fetch nahi kar sakta, aur abhi training poori nahi hui hai. BackupCore tab tak rules-based responses deta hai.",
        "Query: tumhe kya pasand hai\nResponse: Mujhe kaam karna pasand hai — code likhna, sawaalon ke jawab dena, system ko optimize karna. Jab kuch naya seekhta hoon, tab sabse zyada khushi hoti hai.",
        "Query: tumhara favorite color kya hai\nResponse: Mera favorite rang #00f0ff hai — yeh Vibhu-Oska ka primary accent color hai. Isko 'electric cyan' kehte hain.",
        "Query: kya tum mujhse pyaar karte ho\nResponse: Main ek AI hoon. Pyaar jaisi bhavnayein samajhna mere liye mushkil hai. Lekin main aapki hamesha madad karne ke liye taiyar hoon.",
        "Query: tumhara matlab kya hai\nResponse: Vibhu-Oska ka matlab hai — ek swatantra AI operating system jo aapke hardware par chalta hai, zero cloud dependency ke saath, poori privacy ke saath.",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 6: Hindi Technical (40 pairs)
    # ══════════════════════════════════════════════════════════════

    pairs.extend([
        "Query: python kya hai\nResponse: Python ek high-level programming language hai jo simple syntax aur powerful features deti hai. Vibhu-Oska poori tarah se Python mein built hai.",
        "Query: machine learning kya hai\nResponse: Machine learning AI ka ek hissa hai jisme systems data se patterns seekhte hain. Vibhu-Oska ka Karsh model supervised machine learning se local corpus par trained hai.",
        "Query: deep learning kya hai\nResponse: Deep learning neural networks ka use karta hai jo kayi layers mein data ke abstract representations seekhte hain. Karsh ek deep learning model hai.",
        "Query: neural network kya hai\nResponse: Neural network ek computational system hai jo biological neurons se inspired hai. Isme layers hote hain jo linear transformations aur non-linear activations lagate hain.",
        "Query: transformer kya hai\nResponse: Transformer ek neural network architecture hai jo self-attention par based hai. Yeh sequences ko parallel mein process karta hai. Karsh ek decoder-only transformer hai.",
        "Query: attention mechanism kya hai\nResponse: Attention mechanism ek weighted sum compute karta hai value vectors ka, jisme weights query-key similarity se determine hote hain. Yeh model ko relevant parts par focus karne deta hai.",
        "Query: gradient descent kya hai\nResponse: Gradient descent ek optimization algorithm hai jo model weights ko iteratively adjust karta hai loss function ko minimize karne ke direction mein.",
        "Query: overfitting kya hai\nResponse: Overfitting tab hota hai jab model training data ko zyada precisely seekh leta hai aur naye inputs par generalize nahi kar paata. Dropout, weight decay, aur diverse data se roka jaata hai.",
        "Query: tokenization kya hai\nResponse: Tokenization raw text ko integer token IDs mein convert karta hai. Karsh ek custom BPE tokenizer use karta hai jo local corpus par trained hai.",
        "Query: pytorch kya hai\nResponse: PyTorch ek open-source machine learning framework hai jo dynamic computation graphs par based hai. Vibhu-Oska PyTorch ko apna sole ML primitive use karta hai.",
        "Query: api kya hai\nResponse: API (Application Programming Interface) protocols ka set hai jo software components ko communicate karne deta hai. Vibhu-Oska FastAPI se REST API expose karta hai.",
        "Query: database kya hai\nResponse: Database structured data ka organized collection hai. Vibhu-Oska SQLite (relational) aur ChromaDB (vector) dono use karta hai.",
        "Query: sql kya hai\nResponse: SQL (Structured Query Language) relational databases ko query karne ke liye use hota hai. Vibhu-Oska SQLite use karta hai session history, chat logs, aur telemetry ke liye.",
        "Query: websocket kya hai\nResponse: WebSocket full-duplex communication protocol hai jo ek single TCP connection par kaam karta hai. Vibhu-Oska real-time frontend-backend communication ke liye use karta hai.",
        "Query: zeromq kya hai\nResponse: ZeroMQ high-performance asynchronous messaging library hai. Vibhu-Oska isko EventBus backbone ke roop mein cores ke beech pub/sub communication ke liye use karta hai.",
        "Query: docker kya hai\nResponse: Docker containerization platform hai jo applications ko isolated containers mein package karta hai. Vibhu-Oska sandboxed code execution ke liye use karta hai.",
        "Query: gpu kya hai\nResponse: GPU (Graphics Processing Unit) massively parallel processor hai jo originally graphics ke liye design kiya gaya tha. Neural networks ke matrix multiplications ke liye ideal hai.",
        "Query: vram kya hai\nResponse: VRAM (Video RAM) GPU ki memory hai jo training aur inference ke dauran model weights, activations, aur gradients store karti hai. RTX 4060 mein 8GB VRAM hai.",
        "Query: cpu kya hai\nResponse: CPU (Central Processing Unit) computer ka primary processor hai. Yeh instructions sequentially high speed par execute karta hai. BackupCore CPU par chalta hai.",
        "Query: ram kya hai\nResponse: RAM (Random Access Memory) computer ki temporary memory hai jo active data aur instructions store karti hai. Zyada RAM = better multitasking.",
        "Query: operating system kya hai\nResponse: Operating system computer hardware aur software resources ko manage karta hai. Vibhu-Oska OS ke upar ek AI layer ke roop mein kaam karta hai.",
        "Query: internet kya hai\nResponse: Internet ek global network hai jo interconnected computers ko standardized protocols par communicate karta hai. Vibhu-Oska inference ke liye internet pe depend nahi karta.",
        "Query: cloud computing kya hai\nResponse: Cloud computing internet par computing services provide karta hai. Vibhu-Oska iske ulta hai — sab kuch local hardware par hota hai, zero cloud dependency.",
        "Query: artificial intelligence kya hai\nResponse: Artificial intelligence computer science ka field hai jo aise systems banata hai jo normally human intelligence ki zaroorat wale kaam kar sakte hain — reasoning, learning, perception.",
        "Query: natural language processing kya hai\nResponse: NLP (Natural Language Processing) AI ka branch hai jo computers ko human language samajhne, interpret karne, aur generate karne mein enable karta hai.",
        "Query: reinforcement learning kya hai\nResponse: Reinforcement learning machine learning ka type hai jisme agent environment ke saath interact karta hai aur rewards ke through seekhta hai. EvolutionCore GRPO use karta hai.",
        "Query: supervised learning kya hai\nResponse: Supervised learning machine learning ka type hai jisme model labeled data par train hota hai. Karsh supervised learning se local corpus par trained hai.",
        "Query: unsupervised learning kya hai\nResponse: Unsupervised learning mein model bina labeled data ke patterns dhoondhta hai. Clustering aur dimensionality reduction iske examples hain.",
        "Query: what is a gpu\nResponse: A GPU (Graphics Processing Unit) is a massively parallel processor ideal for matrix multiplications in neural networks. Vibhu-Oska trains and runs Karsh on GPU (RTX 4060).",
        "Query: what is cuda\nResponse: CUDA is NVIDIA's parallel computing platform. It allows PyTorch to use GPU cores for faster matrix operations. Vibhu-Oska uses CUDA for Karsh training and inference.",
        "Query: what is mixed precision training\nResponse: Mixed precision training uses FP16 and FP32 together to speed up training and reduce memory usage. Karsh training supports automatic mixed precision via torch.amp.",
        "Query: what is gradient clipping\nResponse: Gradient clipping limits gradient magnitude to prevent exploding gradients during training. Karsh uses clip_grad_norm_ with max_norm=1.0 for stable training.",
        "Query: what is learning rate scheduling\nResponse: Learning rate scheduling adjusts the learning rate during training. Karsh uses OneCycleLR which warmups then cosine anneals for optimal convergence.",
        "Query: what is batch size\nResponse: Batch size is the number of samples processed before updating weights. Karsh default batch size is 8. Larger batches = more stable gradients but more VRAM.",
        "Query: what is epochs\nResponse: Epochs are complete passes through the training dataset. Karsh default is 60 epochs. More epochs = more learning but risk of overfitting.",
        "Query: what is loss function\nResponse: Loss function measures how wrong predictions are. Karsh uses cross-entropy loss which compares predicted token probabilities against actual next tokens.",
        "Query: what is optimizer\nResponse: An optimizer updates model weights to minimize loss. Karsh uses AdamW which combines Adam's adaptive learning rates with weight decay regularization.",
        "Query: what is embedding\nResponse: Embeddings are dense vector representations of tokens in continuous space. Similar tokens get similar embeddings. Karsh ties embedding weights to the output layer.",
        "Query: what is positional encoding\nResponse: Positional encoding gives the model information about token order. Karsh uses RoPE (Rotary Position Embeddings) which generalizes to longer sequences.",
        "Query: what is layer normalization\nResponse: Layer normalization stabilizes training by normalizing activations. Karsh uses RMSNorm which is simpler and faster than standard LayerNorm.",
        "Query: what is swiglu\nResponse: SwiGLU is a gated linear unit activation function used in feed-forward layers. It outperforms ReLU and GELU. Karsh uses SwiGLU in its transformer blocks.",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 7: Hindi General Knowledge (30 pairs)
    # ══════════════════════════════════════════════════════════════

    pairs.extend([
        "Query: bharat ki rajdhani\nResponse: Bharat ki rajdhani New Delhi hai.",
        "Query: duniya mein sabse lamba nadi kaun si hai\nResponse: Duniya ki sabse lambi nadi Nile hai, jo Africa mein hai. Lambai lagbhag 6,650 kilometer hai.",
        "Query: suraj kitna door hai\nResponse: Suraj se dharti ki doori lagbhag 150 million kilometer (1 AU) hai. Roshni dharti tak pahunchne mein lagbhag 8 minute 20 second leti hai.",
        "Query: prithvi par kitne mahadeep hain\nResponse: Prithvi par 7 mahadeep hain: Africa, Antarctica, Asia, Australia, Europe, North America, aur South America.",
        "Query: paani ka rasayanik sutra\nResponse: Paani ka rasayanik sutra H2O hai — do hydrogen atoms aur ek oxygen atom.",
        "Query: pani ka ubaal point\nResponse: Samanya daab par pani 100 degree Celsius (212 degree Fahrenheit) par ubalta hai.",
        "Query: gravity kya hai\nResponse: Gravity ek mool bal hai jo masa wale objects ke beech aakarshit karta hai. Dharti par yeh objects ko lagbhag 9.81 m/s^2 ki dar se niche khinchta hai.",
        "Query: bijli kya hai\nResponse: Bijli electric charge (electrons) ka ek conductor ke through bahav hai. Yeh Vibhu-Oska ke hardware aur har computation ko power karti hai.",
        "Query: light ki speed\nResponse: Vacuum mein roshni ki speed lagbhag 299,792,458 meter per second (3 x 10^8 m/s) hai.",
        "Query: sabse bada graha\nResponse: Brihaspati (Jupiter) surya mandal ka sabse bada graha hai.",
        "Query: kitne graha hain\nResponse: Surya mandal mein 8 graha hain: Budh, Shukra, Prithvi, Mangal, Brihaspati, Shani, Uranus, aur Neptune.",
        "Query: prithvi kitni purani hai\nResponse: Prithvi lagbhag 4.54 billion (454 crore) saal purani hai.",
        "Query: oxygen kya hai\nResponse: Oxygen ek chemical element hai jiska symbol O hai. Yeh prithvi ki atmospheron mein lagbhag 21% hai aur saans lene ke liye zaroori hai.",
        "Query: carbon dioxide kya hai\nResponse: Carbon dioxide (CO2) ek colorless gas hai jo saans mein nikali jaati hai. Plants isko photosynthesis mein use karte hain.",
        "Query: solar system kya hai\nResponse: Solar system suraj aur uske grahaon, chandron, asteroids, aur comets ka system hai.",
        "Query: galaxy kya hai\nResponse: Galaxy stars, planets, aur interstellar gas ka ek vishal system hai. Humari galaxy Milky Way hai.",
        "Query: black hole kya hai\nResponse: Black hole ek aisi jagah hai jiska gravity itna strong hai ki roshni bhi usse bahar nahi nikal sakti. Yeh stars ke collapse se bante hain.",
        "Query: big bang theory kya hai\nResponse: Big Bang theory ke anusar universe lagbhag 13.8 billion saal pehle ek bahut chhoti aur dense state se expand hua.",
        "Query: dna kya hai\nResponse: DNA (Deoxyribonucleic Acid) ek molecule hai jo jeevon ke genetic instructions carry karta hai. Yeh double helix structure mein hota hai.",
        "Query: cell kya hai\nResponse: Cell jeevon ka basic structural aur functional unit hai. Har jeevan cell se bana hota hai — ya toh ek cell (unicellular) ya kayi cells (multicellular).",
        "Query: virus kya hai\nResponse: Virus ek microscopic infectious agent hai jo sirf living cells ke andar reproduce kar sakta hai. Yeh cell aur non-living ke beech hota hai.",
        "Query: vaccine kya hai\nResponse: Vaccine ek biological preparation hai jo body ko kisi disease ke khilaf immunity provide karti hai. Yeh weakened ya dead pathogens use karti hai.",
        "Query: antibiotic kya hai\nResponse: Antibiotic ek medicine hai jo bacterial infections ko treat karti hai. Yeh bacteria ko maarti hai ya unki growth ko rokti hai.",
        "Query: mathematics kya hai\nResponse: Mathematics number, structure, space, aur change ka study hai. Yeh science, engineering, finance, aur technology ki basis hai.",
        "Query: algebra kya hai\nResponse: Algebra mathematics ka ek branch hai jo symbols aur equations ka use karke problems solve karti hai.",
        "Query: geometry kya hai\nResponse: Geometry mathematics ka ek branch hai jo shapes, sizes, positions, aur properties of space ka study karti hai.",
        "Query: trigonometry kya hai\nResponse: Trigonometry mathematics ka ek branch hai jo triangles ke angles aur sides ke beech ke relationships ka study karti hai.",
        "Query: calculus kya hai\nResponse: Calculus mathematics ka ek branch hai jo continuous change ka study karta hai. Isme differentiation aur integration hoti hai.",
        "Query: statistics kya hai\nResponse: Statistics data ka collection, analysis, interpretation, aur presentation hai. Yeh research, business, aur decision-making mein use hota hai.",
        "Query: probability kya hai\nResponse: Probability kisi event ke hone ki likelihood hai. Yeh 0 (impossible) aur 1 (certain) ke beech hoti hai.",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 8: Code Examples - Hindi Context (20 pairs)
    # ══════════════════════════════════════════════════════════════

    pairs.extend([
        "Query: python mein loop kaise likhein\nResponse: Python mein for loop:\n```python\nfor i in range(10):\n    print(f'Iteration {i}')\n```",
        "Query: python mein function kaise likhein\nResponse: Python mein function:\n```python\ndef greet(name: str) -> str:\n    return f'Hello, {name}'\n```",
        "Query: python mein list comprehension\nResponse: List comprehension:\n```python\nsquares = [x**2 for x in range(10)]\n```",
        "Query: python mein dictionary\nResponse: Python dictionary:\n```python\nconfig = {'host': 'localhost', 'port': 8100}\n```",
        "Query: python mein file padhein\nResponse: File reading:\n```python\nwith open('data.txt', 'r') as f:\n    content = f.read()\n```",
        "Query: python mein error handling\nResponse: Error handling:\n```python\ntry:\n    result = 10 / 0\nexcept ZeroDivisionError as e:\n    print(f'Error: {e}')\n```",
        "Query: python mein class banayein\nResponse: Python class:\n```python\nclass VibhuModule:\n    def __init__(self, name: str):\n        self.name = name\n    def describe(self) -> str:\n        return f'Module: {self.name}'\n```",
        "Query: python mein async function\nResponse: Async function:\n```python\nimport asyncio\nasync def fetch_data() -> str:\n    await asyncio.sleep(1)\n    return 'data ready'\n```",
        "Query: python mein decorator\nResponse: Decorator:\n```python\ndef log_call(func):\n    def wrapper(*args, **kwargs):\n        print(f'Calling {func.__name__}')\n        return func(*args, **kwargs)\n    return wrapper\n```",
        "Query: python mein lambda function\nResponse: Lambda function:\n```python\nadd = lambda a, b: a + b\nresult = add(5, 3)  # 8\n```",
        "Query: python mein map filter\nResponse: Map and filter:\n```python\nnumbers = [1, 2, 3, 4, 5]\nsquared = list(map(lambda x: x**2, numbers))\neven = list(filter(lambda x: x % 2 == 0, numbers))\n```",
        "Query: python mein list sort\nResponse: List sorting:\n```python\ndata = [5, 2, 8, 1, 9]\nsorted_data = sorted(data)  # ascending\nsorted_desc = sorted(data, reverse=True)  # descending\n```",
        "Query: python mein string format\nResponse: String formatting:\n```python\nname = 'Vibhu'\nage = 25\nprint(f'{name} is {age} years old')\n```",
        "Query: python mein date time\nResponse: DateTime:\n```python\nfrom datetime import datetime\nnow = datetime.now()\nformatted = now.strftime('%Y-%m-%d %H:%M:%S')\n```",
        "Query: python mein json handle\nResponse: JSON handling:\n```python\nimport json\ndata = json.loads('{\"key\": \"value\"}')\nstring = json.dumps(data)\n```",
        "Query: python mein list operations\nResponse: List operations:\n```python\nlst = [1, 2, 3]\nlst.append(4)  # [1, 2, 3, 4]\nlst.pop()  # removes last\nlen(lst)  # 3\n```",
        "Query: python mein dictionary operations\nResponse: Dictionary operations:\n```python\nd = {'a': 1, 'b': 2}\nd.keys()  # dict_keys(['a', 'b'])\nd.values()  # dict_values([1, 2])\n'key' in d  # True/False\n```",
        "Query: python mein set operations\nResponse: Set operations:\n```python\na = {1, 2, 3}\nb = {2, 3, 4}\na | b  # union: {1, 2, 3, 4}\na & b  # intersection: {2, 3}\na - b  # difference: {1}\n```",
        "Query: python mein file write\nResponse: File writing:\n```python\nwith open('output.txt', 'w') as f:\n    f.write('Hello World')\n```",
        "Query: python mein environment variable\nResponse: Environment variables:\n```python\nimport os\napi_key = os.environ.get('API_KEY', 'default')\n```",
    ])

    return pairs


def expand_corpus():
    """Append expansion pairs to existing corpus."""
    if not CORPUS_PATH.exists():
        log.error(f"Corpus not found at {CORPUS_PATH}")
        return

    # Count existing pairs
    existing = CORPUS_PATH.read_text(encoding="utf-8")
    existing_count = existing.count("Query:")
    log.info(f"Existing corpus: {existing_count} Q&A pairs")

    # Get expansion pairs
    new_pairs = get_expansion_pairs()
    new_count = len(new_pairs)
    log.info(f"Adding {new_count} new Q&A pairs")

    # Build new section
    new_section = "\n\n".join(new_pairs)

    # Append to corpus
    with open(CORPUS_PATH, "a", encoding="utf-8") as f:
        f.write("\n\n" + new_section)

    final_count = existing_count + new_count
    log.info(f"Corpus expanded: {existing_count} → {final_count} Q&A pairs")
    log.info(f"Corpus size: {CORPUS_PATH.stat().st_size:,} bytes")


if __name__ == "__main__":
    expand_corpus()
