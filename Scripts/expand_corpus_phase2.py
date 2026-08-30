"""
Vibhu-Oska AI-OS — Corpus Expansion Phase 2
Adds remaining pairs to reach 1200+ Q&A pairs.
Run: python Scripts/expand_corpus_phase2.py
"""

from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("CorpusExpander2")

ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = ROOT / "Data" / "training" / "karsh" / "corpus.txt"


def get_phase2_pairs() -> list[str]:
    pairs = []

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 9: Advanced Python Patterns (40 pairs)
    # ══════════════════════════════════════════════════════════════
    pairs.extend([
        "Query: what is python dataclass field default factory\nResponse: default_factory creates mutable defaults safely:\n```python\nfrom dataclasses import dataclass, field\n@dataclass\nclass Config:\n    tags: list = field(default_factory=list)\n```",
        "Query: what is python slots\nResponse: __slots__ restricts attributes for memory efficiency:\n```python\nclass Point:\n    __slots__ = ['x', 'y']\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\n```",
        "Query: what is python descriptor protocol\nResponse: Descriptors customize attribute access via __get__, __set__, __delete__. Properties and classmethod are built on descriptors.",
        "Query: what is python metaclass\nResponse: Metaclasses define how classes are created. type() is the default. Override __new__ or __init__ to customize class creation.",
        "Query: what is python abstract method\nResponse: @abstractmethod in ABC forces subclasses to implement methods:\n```python\nfrom abc import ABC, abstractmethod\nclass Base(ABC):\n    @abstractmethod\n    def run(self): pass\n```",
        "Query: what is python __call__\Response: __call__ makes instances callable:\n```python\nclass Multiplier:\n    def __init__(self, factor):\n        self.factor = factor\n    def __call__(self, x):\n        return x * self.factor\ndouble = Multiplier(2)\nprint(double(5))  # 10\n```",
        "Query: what is python property\nResponse: Properties wrap methods as attributes:\n```python\nclass Circle:\n    def __init__(self, radius):\n        self._radius = radius\n    @property\n    def area(self):\n        return 3.14159 * self._radius ** 2\n```",
        "Query: what is python staticmethod\nResponse: @staticmethod defines methods that don't access instance or class state:\n```python\nclass Math:\n    @staticmethod\n    def add(a, b):\n        return a + b\n```",
        "Query: what is python classmethod\nResponse: @classmethod receives the class as first argument:\n```python\nclass Factory:\n    @classmethod\n    def create(cls):\n        return cls()\n```",
        "Query: what is python __repr__\Response: __repr__ returns developer-friendly string representation:\n```python\nclass User:\n    def __repr__(self):\n        return f'User(name={self.name!r})'\n```",
        "Query: what is python __str__\Response: __str__ returns user-friendly string:\n```python\nclass User:\n    def __str__(self):\n        return f'User: {self.name}'\n```",
        "Query: what is python __eq__\Response: __eq__ defines equality comparison:\n```python\nclass Point:\n    def __eq__(self, other):\n        return self.x == other.x and self.y == other.y\n```",
        "Query: what is python __hash__\Response: __hash__ makes objects usable in sets and as dict keys:\n```python\nclass Point:\n    def __hash__(self):\n        return hash((self.x, self.y))\n```",
        "Query: what is python __lt__\Response: __lt__ defines less-than comparison for sorting:\n```python\nfrom functools import total_ordering\n@total_ordering\nclass Item:\n    def __lt__(self, other):\n        return self.price < other.price\n```",
        "Query: what is python contextlib\nResponse: contextlib simplifies context managers:\n```python\nfrom contextlib import contextmanager\n@contextmanager\ndef timer():\n    start = time.time()\n    yield\n    print(f'{time.time()-start:.2f}s')\n```",
        "Query: what is python typing protocol\nResponse: Protocol enables structural subtyping:\n```python\nfrom typing import Protocol\nclass Drawable(Protocol):\n    def draw(self) -> None: ...\n```",
        "Query: what is python typing generic\nResponse: Generics with TypeVar:\n```python\nfrom typing import TypeVar, List\nT = TypeVar('T')\ndef first(items: List[T]) -> T:\n    return items[0]\n```",
        "Query: what is python walrus operator\nResponse: := assigns in expressions:\n```python\nif (n := len(data)) > 10:\n    print(f'Long: {n}')\n```",
        "Query: what is python structural pattern matching\nResponse: match-case (Python 3.10+):\n```python\nmatch command:\n    case 'quit': sys.exit()\n    case 'hello': print('Hi')\n    case _: print('Unknown')\n```",
        "Query: what is python exception chaining\nResponse: Exception chaining with from:\n```python\ntry:\n    open('missing.txt')\nexcept FileNotFoundError as e:\n    raise RuntimeError('Failed') from e\n```",
        "Query: what is python suppress\nResponse: contextlib.suppress ignores specific exceptions:\n```python\nfrom contextlib import suppress\nwith suppress(FileNotFoundError):\n    os.remove('maybe.txt')\n```",
        "Query: what is python cached_property\nResponse: cached_property computes once then caches:\n```python\nfrom functools import cached_property\nclass Data:\n    @cached_property\n    def processed(self):\n        return expensive_computation()\n```",
        "Query: what is python total_ordering\nResponse: total_ordering fills in comparison methods from __eq__ and one of __lt__, __gt__, etc.",
        "Query: what is python singledispatch\nResponse: singledispatch enables function overloading by type:\n```python\nfrom functools import singledispatch\n@singledispatch\ndef process(data): raise TypeError\n@process.register(str)\ndef _(data): return data.upper()\n```",
        "Query: what is python annotated\nResponse: typing.get_type_hints() retrieves annotations at runtime. Used for dependency injection and validation.",
        "Query: what is python dataclass asdict\nResponse: asdict converts dataclass to dict:\n```python\nfrom dataclasses import asdict\nuser_dict = asdict(user_instance)\n```",
        "Query: what is python dataclass astuple\nResponse: astuple converts dataclass to tuple:\n```python\nfrom dataclasses import astuple\nuser_tuple = astuple(user_instance)\n```",
        "Query: what is python __post_init__\Response: __post_init__ runs after __init__ in dataclasses:\n```python\n@dataclass\nclass User:\n    name: str\n    email: str\n    def __post_init__(self):\n        self.email = self.email.lower()\n```",
        "Query: what is python frozen dataclass\nResponse: frozen=True makes dataclass immutable:\n```python\n@dataclass(frozen=True)\nclass Point:\n    x: int\n    y: int\n```",
        "Query: what is python __slots__ with dataclass\nResponse: @dataclass(slots=True) (Python 3.10+) generates __slots__ automatically.",
        "Query: what is python weakref\nResponse: weakref creates weak references that don't prevent garbage collection:\n```python\nimport weakref\nref = weakref.ref(obj)\nprint(ref())  # obj or None\n```",
        "Query: what is python __init_subclass__\Response: __init_subclass__ hooks into subclass creation:\n```python\nclass Base:\n    def __init_subclass__(cls, **kwargs):\n        print(f'Subclass created: {cls.__name__}')\n```",
        "Query: what is python __set_name__\Response: __set_name__ is called when a descriptor is assigned to a class attribute. Used for automatic attribute naming in descriptors.",
        "Query: what is python __class_getitem__\Response: __class_getitem__ enables generic syntax on classes:\n```python\nclass MyList:\n    def __class_getitem__(cls, item):\n        return list\n```",
        "Query: what is python __fspath__\Response: __fspath__ enables objects to be used with os.fspath() and path-like operations.",
        "Query: what is python __bytes__\Response: __bytes__ returns bytes representation, called by bytes(obj).",
        "Query: what is python __format__\Response: __format__ customizes format() and f-string formatting:\n```python\nclass Money:\n    def __format__(self, spec):\n        return f'${self.amount:,.2f}'\n```",
        "Query: what is python __enter__ __exit__\Response: __enter__ and __exit__ define context manager protocol. __enter__ returns value, __exit__ handles cleanup.",
        "Query: what is python __aiter__ __anext__\Response: __aiter__ and __anext__ define async iteration protocol for async for loops.",
        "Query: what is python __len__\Response: __len__ returns collection length, called by len(obj).",
        "Query: what is python __getitem__\Response: __getitem__ enables indexed access: obj[key]. Also enables iteration if __iter__ is defined.",
        "Query: what is python __setitem__\Response: __setitem__ enables indexed assignment: obj[key] = value.",
        "Query: what is python __contains__\Response: __contains__ enables 'in' operator: if x in obj.",
        "Query: what is python __iter__\Response: __iter__ returns iterator, enables for x in obj.",
        "Query: what is python __next__\Response: __next__ returns next item from iterator. Raises StopIteration when exhausted.",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 10: More Hindi General Knowledge (40 pairs)
    # ══════════════════════════════════════════════════════════════
    pairs.extend([
        "Query: bharat ka rashtriya phool\nResponse: Bharat ka rashtriya phool kamal (lotus) hai.",
        "Query: bharat ka rashtriya pakshi\nResponse: Bharat ka rashtriya pakshi mor (peacock) hai.",
        "Query: bharat ka rashtriya pashu\nResponse: Bharat ka rashtriya pashu gaay hai.",
        "Query: bharat ka rashtriya tree\nResponse: Bharat ka rashtriya vriksh bargad (banyan tree) hai.",
        "Query: bharat ka rashtriya nadi\nResponse: Bharat ki rashtriya nadi Ganga hai.",
        "Query: bharat ka rashtriya khel\nResponse: Bharat ka rashtriya khel hockey hai.",
        "Query: bharat ka rashtriya gan\nResponse: Bharat ka rashtriya gan 'Jana Gana Mana' hai.",
        "Query: bharat ka rashtriya dhwaj\nResponse: Bharat ka rashtriya dhwaj Tiranga hai — kesariya, safed, aur hari rang ke saath.",
        "Query: bharat ka pehla rashtrapati\nResponse: Bharat ke pehla rashtrapati Dr. Rajendra Prasad the.",
        "Query: bharat ka pehla pradhan mantri\nResponse: Bharat ke pehla pradhan mantri Jawaharlal Nehru the.",
        "Query: bharat ka sabse lamba nadi\nResponse: Bharat ki sabse lambi nadi Ganga hai (2,525 km).",
        "Query: bharat ka sabse uuncha peak\nResponse: Bharat ka sabse uuncha peak K2 (Godwin-Austen) hai (8,611m), lekin siyasi roop se Mount Everest (8,849m) sabse uuncha maana jaata hai.",
        "Query: bharat ka rajya kitna hai\nResponse: Bharat mein 28 rajya aur 8 kendra shasanit pradesh hain.",
        "Query: bharat ki bhashayein\nResponse: Bharat mein 22 anumat bhashayein hain. Hindi sabse zyada boli jaane wali bhasha hai.",
        "Query: hindi kya hai\nResponse: Hindi Bharat ki rajbhasha hai. Devanagari lipi mein likhi jaati hai. Yeh Sanskrit se viksit hui hai.",
        "Query: sanskrit kya hai\nResponse: Sanskrit ek prachin bhasha hai jo Vedic literature mein use hoti hai. Ise devbhasha bhi kehte hain.",
        "Query: diwali kab manayi jaati hai\nResponse: Diwali kartik mahine mein manayi jaati hai — October ya November mein. Ise roshni ka tyohaar kehte hain.",
        "Query: holi kab manayi jaati hai\nResponse: Holi phalgun mahine (March) mein manayi jaati hai. Ise rangon ka tyohaar kehte hain.",
        "Query: ganesh chaturthi kab hai\nResponse: Ganesh Chaturthi Bhadrapad mahine (August-September) mein manayi jaati hai.",
        "Query: navratri kab hai\nResponse: Navratri Ashwin mahine (September-October) mein 9 din manayi jaati hai.",
        "Query: makar sankranti kab hai\nResponse: Makar Sankranti 14 January ko manayi jaati hai. Yeh suryanamaskar ka tyohaar hai.",
        "Query: independence day kab hai\nResponse: Bharat ka swatantrata diwas 14 August ko manaya jaata hai.",
        "Query: republic day kab hai\nResponse: Bharat ka ganatantra diwas 26 January ko manaya jaata hai.",
        "Query: gandhi jayanti kab hai\nResponse: Mahatma Gandhi ki jayanti 2 October ko manayi jaati hai.",
        "Query: teachers day kab hai\nResponse: Shikshak diwas 5 September ko manaya jaata hai — Dr. Radhakrishnan ki jayanti par.",
        "Query: childrens day kab hai\nResponse: Bal Diwas 14 November ko manaya jaata hai — Jawaharlal Nehru ki jayanti par.",
        "Query: yoga day kab hai\nResponse: Antarrashtriya Yog Diwas 21 June ko manaya jaata hai.",
        "Query: bharat ka sabse bada mahasagar\nResponse: Bharat ke dakshin mein Indian Ocean hai.",
        "Query: himalaya kya hai\nResponse: Himalaya duniya ki sabse uunchi pahadi chain hai. Bharat ke uttar mein sthit hai aur isme sagar se uunchi chotiyain hain.",
        "Query: thar desert kahan hai\nResponse: Thar Marusthal Bharat ke pashchim (Rajasthan) mein hai. Yeh duniya ki sabse ghani abadi wali desert hai.",
        "Query: ganga nadi kitni lambi hai\nResponse: Ganga ki lambai 2,525 kilometer hai. Yeh Gangotri glacier se nikalti hai aur Bangal ki khadi mein milti hai.",
        "Query: yamuna nadi kahan se aati hai\nResponse: Yamuna Yamunotri glacier se nikalti hai aur Ganga mein Allahabad (Prayagraj) par milti hai.",
        "Query: brahmaputra nadi kahan se aati hai\nResponse: Brahmaputra Tibet se nikalti hai, Arunachal Pradesh mein Bharat mein pravesh karti hai, aur Bangladesh mein Ganga se milti hai.",
        "Query: qutub minar kitna uuncha hai\nResponse: Qutub Minar 72.5 meter uuncha hai. Yeh 1200 AD mein banaya gaya tha.",
        "Query: taj mahal kahan hai\nResponse: Taj Mahal Agra, Uttar Pradesh mein hai. Ise Shah Jahan ne apni biwi Mumtaz Mahal ki yaad mein banwaya tha.",
        "Query: red fort kahan hai\nResponse: Red Fort (Lal Qila) Delhi mein hai. Ise Shah Jahan ne 1638 mein banwaya tha.",
        "Query: gateway of india kahan hai\nResponse: Gateway of India Mumbai, Maharashtra mein hai. Yeh 1924 mein banaya gaya tha.",
        "Query: india gate kahan hai\nResponse: India Gate New Delhi mein hai. Yeh World War I ke shaheedon ki yaad mein banaya gaya hai.",
        "Query: hawa mahal kahan hai\nResponse: Hawa Mahal Jaipur, Rajasthan mein hai. Ise 1799 mein banaya gaya tha.",
        "Query: charminar kahan hai\nResponse: Charminar Hyderabad, Telangana mein hai. Ise 1591 mein banaya gaya tha.",
        "Query: victoria memorial kahan hai\nResponse: Victoria Memorial Kolkata, West Bengal mein hai. Yeh British kaal ka memorial hai.",
        "Query: golden temple kahan hai\nResponse: Golden Temple (Harmandir Sahib) Amritsar, Punjab mein hai. Yeh Sikh dharam ka sabse pavitra sthal hai.",
        "Query: varanasi kya hai\nResponse: Varanasi (Banaras) Bharat ka sabse purana shehar hai. Yeh Ganga kinare sthit hai aur Hindu teerth sthal hai.",
        "Query: kumbh mela kab lagta hai\nResponse: Kumbh Mela har 12 saal mein lagta hai — Prayagraj, Haridwar, Nashik, aur Ujjain mein.",
        "Query: bharat ka sabse lamba pul\nResponse: Bharat ka sabse lamba pul Atal Setu (Mumbai Trans Harbour Link) hai — 21.8 km.",
        "Query: bharat ka sabse bada stadium\nResponse: Bharat ka sabse bada stadium Narendra Modi Stadium (Ahmedabad) hai — 1,32,000 capacity.",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 11: Advanced System Design (30 pairs)
    # ══════════════════════════════════════════════════════════════
    pairs.extend([
        "Query: what is load balancing\nResponse: Load balancing distributes incoming requests across multiple servers to prevent overload and ensure high availability.",
        "Query: what is rate limiting\nResponse: Rate limiting controls how many requests a client can make in a time window. Prevents abuse and ensures fair resource usage.",
        "Query: what is caching\nResponse: Caching stores frequently accessed data in fast storage (memory) to avoid expensive recomputation or database queries.",
        "Query: what is connection pooling\nResponse: Connection pooling maintains a set of reusable database connections to avoid the overhead of creating new connections for each request.",
        "Query: what is circuit breaker\nResponse: Circuit breaker pattern prevents cascading failures. After N failures, the circuit opens and requests fail fast instead of waiting for timeouts.",
        "Query: what is retry with backoff\nResponse: Retry with exponential backoff waits increasing intervals between retries. Prevents overwhelming a failing service.",
        "Query: what is message queue\nResponse: Message queues decouple producers and consumers. Messages are stored until consumed, enabling async processing and fault tolerance.",
        "Query: what is pub sub pattern\nResponse: Publish-subscribe decouples message senders from receivers. Publishers send to topics, subscribers receive from topics they're interested in.",
        "Query: what is api gateway\nResponse: An API gateway is a single entry point for all API requests. It handles routing, authentication, rate limiting, and request/response transformation.",
        "Query: what is microservices architecture\nResponse: Microservices decompose an application into small, independent services that communicate via APIs. Each service owns its data and logic.",
        "Query: what is monolith architecture\nResponse: A monolith is a single, unified application where all components run as one unit. Simpler to develop initially but harder to scale.",
        "Query: what is event sourcing\nResponse: Event sourcing stores all changes as a sequence of events instead of current state. Enables audit trails, time travel, and replay.",
        "Query: what is CQRS\nResponse: CQRS (Command Query Responsibility Segregation) separates read and write models. Commands modify state, queries read state. Enables optimization of each path.",
        "Query: what is database sharding\nResponse: Sharding splits a database horizontally across multiple servers. Each shard holds a subset of data, enabling horizontal scaling.",
        "Query: what is replication\nResponse: Replication copies data across multiple servers. Master-slave for read scaling, master-master for both read/write scaling.",
        "Query: what is consensus algorithm\nResponse: Consensus algorithms (Raft, Paxos) ensure distributed nodes agree on a single value. Used for leader election and data consistency.",
        "Query: what is eventual consistency\nResponse: Eventual consistency guarantees that all nodes will converge to the same state eventually, though not immediately. Used in distributed systems.",
        "Query: what is CAP theorem\nResponse: CAP theorem states a distributed system can only guarantee two of three: Consistency, Availability, Partition tolerance. Most systems choose AP or CP.",
        "Query: what is observability\nResponse: Observability is the ability to understand system internal state from external outputs. Three pillars: logs, metrics, and traces.",
        "Query: what is distributed tracing\nResponse: Distributed tracking follows requests across service boundaries. Tools like Jaeger and Zipkin visualize request flow and latency.",
        "Query: what is health check\nResponse: Health checks verify service availability. Liveness checks ensure a service is running. Readiness checks ensure a service can handle requests.",
        "Query: what is graceful degradation\nResponse: Graceful degradation means a system continues operating at reduced functionality when parts fail, instead of complete failure.",
        "Query: what is chaos engineering\nResponse: Chaos engineering intentionally injects failures into a system to test resilience and identify weaknesses before they cause outages.",
        "Query: what is blue green deployment\nResponse: Blue-green deployment maintains two identical environments. Traffic switches from blue (current) to green (new) for zero-downtime deployments.",
        "Query: what is canary deployment\nResponse: Canary deployment gradually rolls out changes to a small subset of users before full deployment. Enables monitoring for issues.",
        "Query: what is feature flag\nResponse: Feature flags enable or disable features without code changes. Allow gradual rollouts, A/B testing, and instant feature toggles.",
        "Query: what is idempotency\nResponse: Idempotency means performing an operation multiple times has the same effect as once. Critical for API reliability and retry safety.",
        "Query: what is backpressure\nResponse: Backpressure is a feedback mechanism where a consumer tells a producer to slow down when overwhelmed. Prevents system overload.",
        "Query: what is circuit breaker timeout\nResponse: Circuit breaker timeout determines how long to wait before transitioning from open to half-open state to test if the service recovered.",
        "Query: what is bulkhead pattern\nResponse: Bulkhead pattern isolates components so failure in one doesn't cascade to others. Like ship bulkheads that prevent sinking.",
    ])

    # ══════════════════════════════════════════════════════════════
    # CATEGORY 12: More Vibhu-Oska Usage (30 pairs)
    # ══════════════════════════════════════════════════════════════
    pairs.extend([
        "Query: vibhu oska ko kaise install karein\nResponse: Git clone karo, Python virtual environment banao, pip install -r requirements.txt, aur setup script run karo.",
        "Query: vibhu oska ko kaise start karein\nResponse: python -m uvicorn Backend.Gateway.App:app --host 0.0.0.0 --port 8100 --reload se start karo.",
        "Query: vibhu oska ka port kya hai\nResponse: Default port 8100 hai. WebSocket port 8101 hai. Dono config/default.yaml mein configure kar sakte ho.",
        "Query: vibhu oska ka github\nResponse: Vibhu-Oska ka source code GitHub par available hai. Repository name Vibhu-Oska hai.",
        "Query: vibhu oska mein memory kaise kaam karti hai\nResponse: Dual memory: ChromaDB semantic vectors ke liye, SQLite relational state ke liye. GraphRAG knowledge graph traversal bhi hai.",
        "Query: vibhu oska mein training kaise hoti hai\nResponse: Training panel ya command line se python -m Models.karsh.train run karo. 60 epochs default hain. RTX 4060 par ~25 minute lagta hai.",
        "Query: vibhu oska ka backup core kya hai\nResponse: BackupCore CPU-based contingency fallback hai. Jab Karsh fail hota hai tab yeh rules-based responses deta hai.",
        "Query: vibhu oska ka event bus kya hai\nResponse: ZeroMQ-based pub/sub messaging system hai jo sabhi cores ke beech communication karta hai.",
        "Query: vibhu oska mein kitne cores hain\nResponse: Trimurti (3) + Tridevis (3) + Specialized (7) + Supporting (3) = total 16 cores hain.",
        "Query: vibhu oska ka hardware requirement\nResponse: RTX 4060 (8GB VRAM), 8-core CPU, 16GB RAM. Minimum: CPU-only mode mein chal sakta hai.",
        "Query: vibhu oska kis language mein hai\nResponse: Vibhu-Oska poori tarah se Python mein built hai. Frontend HTML/CSS/JavaScript mein hai.",
        "Query: vibhu oska open source hai\nResponse: Haan, Vibhu-Oska open source hai. Framework, plugins, aur architecture code MIT license ke under hai.",
        "Query: vibhu oska mein kaun kaun si languages hain\nResponse: CodingDomain mein 9 specialists hain: Python, JavaScript, SQL, Go, Rust, C++, Shell, Regex.",
        "Query: vibhu oska ka specialist kya hai\nResponse: Specialists domain-specific experts hain jo particular tasks handle karte hain — coding, system admin, design, etc.",
        "Query: vibhu oska mein websocket kaise use karein\nResponse: ws://localhost:8100/ws par connect karo. JSON messages bhejo: {\"prompt\": \"...\", \"session_id\": \"...\"}.",
        "Query: vibhu oska ka session kya hai\nResponse: Session ek conversation context hai jo user interactions ko track karta hai. SQLite mein store hota hai.",
        "Query: vibhu oska mein cache kaise kaam karta hai\nResponse: OptimizationCore LRU cache use karta hai. Identical queries cached response return karte hain instantly.",
        "Query: vibhu oska ka graphrag kya hai\nResponse: GraphRAG knowledge graph retrieval hai. Entities aur relationships SQLite mein store hoti hain aur context enrichment ke liye traverse hoti hain.",
        "Query: vibhu oska ka watchdog kya hai\nResponse: Watchdog background health daemon hai jo sabhi registered cores ko monitor karta hai.",
        "Query: vibhu oska ka context manager kya hai\nResponse: ContextManager token budget enforce karta hai. Long contexts ko truncate ya compress karta hai model ke sequence length budget mein.",
        "Query: vibhu oska ka validation core kya hai\nResponse: ValidationCore input/output guard hai. Inputs sanitize karta hai (SQL injection, XSS block) aur output schema validate karta hai.",
        "Query: vibhu oska ka fast responder kya hai\nResponse: FastResponder deterministic instant patterns handle karta hai — math, greetings, identity. Milliseconds mein response deta hai.",
        "Query: vibhu oska ka optimization core kya hai\nResponse: OptimizationCore LRU query cache aur context compression manage karta hai.",
        "Query: vibhu oska ka monitoring core kya hai\nResponse: MonitoringCore EventBus subscribe karta hai aur sabhi telemetry events ko SQLite mein log karta hai.",
        "Query: vibhu oska ka evolution core kya hai\nResponse: EvolutionCore Shiva hai — GRPO reinforcement learning, reward engine, aur sandbox execution ke through self-improvement karta hai.",
        "Query: vibhu oska ka design core kya hai\nResponse: DesignCore HTML/CSS templates generate karta hai natural language se. Dark-mode glassmorphism styles support karta hai.",
        "Query: vibhu oska ka automation core kya hai\nResponse: AutomationCore OS executive layer hai. System commands, file I/O, process management, aur hardware telemetry handle karta hai.",
        "Query: vibhu oska ka distribution core kya hai\nResponse: DistributionCore Stubvi compilation handle karta hai. Public builds ko SHA256 manifests, PII scrubbing, aur whitelist ke saath package karta hai.",
        "Query: vibhu oska ka image generation core kya hai\nResponse: ImageGenerationCore local image generation pipeline hai.",
        "Query: vibhu oska ka voice core kya hai\nResponse: VoiceCore voice I/O handle karega — wake word detection, audio transcription, aur TTS. Phase 3 mein implement hoga.",
    ])

    return pairs


def expand_corpus_phase2():
    """Append phase 2 pairs to existing corpus."""
    if not CORPUS_PATH.exists():
        log.error(f"Corpus not found at {CORPUS_PATH}")
        return

    existing = CORPUS_PATH.read_text(encoding="utf-8")
    existing_count = existing.count("Query:")
    log.info(f"Existing corpus: {existing_count} Q&A pairs")

    new_pairs = get_phase2_pairs()
    new_count = len(new_pairs)
    log.info(f"Adding {new_count} new Q&A pairs")

    new_section = "\n\n".join(new_pairs)

    with open(CORPUS_PATH, "a", encoding="utf-8") as f:
        f.write("\n\n" + new_section)

    final_count = existing_count + new_count
    log.info(f"Corpus expanded: {existing_count} → {final_count} Q&A pairs")
    log.info(f"Corpus size: {CORPUS_PATH.stat().st_size:,} bytes")


if __name__ == "__main__":
    expand_corpus_phase2()
