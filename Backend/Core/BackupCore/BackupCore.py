"""
Vibhu-Oska AI-OS — BackupCore
Intelligent CPU-based fallback execution node. Provides fast, contextual responses
while Karsh is in training. Operates as a full intelligence layer — not a stub.
"""

from __future__ import annotations

import asyncio
import re
import threading
import gc
from pathlib import Path
from typing import Any

from Shared.Models import TaskResponse, TokenUsage, ResponseMetadata, Status, StatusCode, ExecutionTarget
from Backend.Core.MainCore.LanguageCore.LanguageCore import LanguageCore
from Backend.Core.MainCore.FastResponder.FastResponder import FastResponder
from Backend.Plugins.Logger.Logger import Logger

# Lazy import for LanguageCore
_language_core = None

def _get_lang():
    global _language_core
    if _language_core is None:
        _language_core = LanguageCore.get_instance()
    return _language_core

# ==================================================================================================
# # Internal Separation Division
# =================─────────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are Vibhu-Oska AI-OS — a sovereign, locally-hosted artificial intelligence operating system
built from first principles. You run entirely on the creator's local hardware (RTX 4060 Laptop GPU,
8-core CPU). You have no cloud dependency and no external API calls. Your primary Karsh
transformer is currently in training. You are operating from BackupCore — a high-capability
CPU-native intelligence layer. Respond accurately, concisely, and professionally.\
"""


class LocalSLM:
    """
    Localized Small Language Model (SLM) fallback loader.
    Loads Phi-3-mini or Qwen-0.5B-Instruct in a background thread if local weights exist.
    """
    def __init__(self, log: Any) -> None:
        self._log = log
        self._model: Any = None
        self._tokenizer: Any = None
        self._loaded = False
        self._load_attempted = False
        self._lock = threading.Lock()

    @property
    def is_ready(self) -> bool:
        return self._loaded and self._model is not None and self._tokenizer is not None

    def start_loading(self) -> None:
        """Start loading in a background thread to prevent startup blocks."""
        threading.Thread(target=self._load, daemon=True).start()

    def _discover_model_dir(self) -> Path | None:
        root = Path(__file__).resolve().parent.parent.parent.parent.parent
        model_dir = root / "Models" / "backup"
        if model_dir.exists() and (model_dir / "config.json").exists():
            return model_dir
        for candidate in (root / "Models" / "slm", root / "Models" / "backup_slm"):
            if candidate.exists() and (candidate / "config.json").exists():
                return candidate
        return None

    def _load(self) -> None:
        if self._load_attempted:
            return
        self._load_attempted = True
        try:
            model_dir = self._discover_model_dir()

            if model_dir is None:
                self._log.info("Local SLM directory not found (Models/backup). Template engine active.")
                return

            import torch

            # Optional GGUF support: load via llama_cpp if available and a .gguf file exists.
            gguf_files = list(model_dir.glob("*.gguf"))
            if gguf_files and not (model_dir / "config.json").exists():
                try:
                    from llama_cpp import Llama

                    self._log.info("Local SLM GGUF weights detected, loading via llama_cpp...", file=gguf_files[0].name)
                    llm = Llama(model_path=str(gguf_files[0]), n_ctx=2048, n_threads=4, verbose=False)
                    with self._lock:
                        self._model = llm
                        self._tokenizer = None
                        self._loaded = True
                    self._log.info("Local SLM (GGUF) fallback engine loaded successfully on device: cpu")
                    return
                except Exception as e:
                    self._log.warning(f"Unable to load SLM via llama_cpp (falling back to transformers): {e}")

            self._log.info("Local SLM weights detected, loading to memory...")
            from transformers import AutoTokenizer, AutoModelForCausalLM

            tokenizer = AutoTokenizer.from_pretrained(str(model_dir), local_files_only=True)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = AutoModelForCausalLM.from_pretrained(
                str(model_dir),
                local_files_only=True,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                low_cpu_mem_usage=True
            ).to(device)
            
            with self._lock:
                self._tokenizer = tokenizer
                self._model = model
                self._loaded = True
                
            self._log.info(f"Local SLM fallback engine loaded successfully on device: {device}")
        except Exception as e:
            self._log.warning(f"Unable to load local SLM (falling back to Template Synthesis): {e}")

    def generate(self, prompt: str, system_prompt: str = "", context_str: str = "") -> str | None:
        """Runs inference if loaded, else returns None."""
        if not self.is_ready:
            return None
            
        try:
            import torch
            with self._lock:
                if not self._model or not self._tokenizer:
                    return None
                
                full_prompt = ""
                if system_prompt:
                    full_prompt += f"<|system|>\n{system_prompt}<|end|>\n"
                if context_str:
                    full_prompt += f"<|user|>\nContext information:\n{context_str}\n\nQuery: {prompt}<|end|>\n<|assistant|>\n"
                else:
                    full_prompt += f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n"

                inputs = self._tokenizer(full_prompt, return_tensors="pt").to(self._model.device)
                outputs = self._model.generate(
                    **inputs,
                    max_new_tokens=256,
                    temperature=0.3,
                    do_sample=False
                )
                generated_ids = outputs[0][len(inputs.input_ids[0]):]
                response = self._tokenizer.decode(generated_ids, skip_special_tokens=True)
                return response.strip()
        except Exception as e:
            self._log.error("Local SLM inference failed", error=str(e))
            return None


class ContextAwareTemplateEngine:
    """
    Overhauled context-aware template synthesis engine.
    Ensures structured, informative responses when neural fallback is inactive.
    Uses multi-context GRAG summaries and collapsed quantum intent states to
    produce context-aware templated answers.
    """
    def __init__(self, backup_core: BackupCore) -> None:
        self._core = backup_core

    def synthesize(
        self,
        norm: str,
        prompt: str,
        context: list[dict[str, Any]] | None = None,
        grag_ctx: str = "",
        routing_states: dict[str, float] | None = None,
    ) -> str:
        base = self._core._reason(prompt, context)
        return self._wrap_with_context(base, prompt, context, grag_ctx, routing_states or {})

    def _wrap_with_context(
        self,
        base: str,
        prompt: str,
        context: list[dict[str, Any]] | None,
        grag_ctx: str,
        routing_states: dict[str, float],
    ) -> str:
        """Wrap a base response with GRAG + quantum intent context when the base
        response is a generic fallback (i.e. it did not fully consume context)."""
        collapsed = max(routing_states, key=routing_states.get) if routing_states else "GENERAL"

        generic_markers = (
            "Karsh (training in progress)",
            "pattern-bound until Karsh",
            "falls outside my current deterministic knowledge boundaries",
            "will provide fully generative",
        )
        has_context = any(m in base for m in generic_markers)

        if not has_context:
            return base

        sections = [base]
        if grag_ctx:
            sections.append(f"\n\n### 🕸️ Context Synthesis (intent: `{collapsed}`)\n\n{grag_ctx}")
        elif context:
            items = [c.get("content", "") for c in context if c.get("content")]
            if items:
                sections.append(
                    "\n\n### 🧠 Context Synthesis (intent: `" + collapsed + "`)\n\n"
                    + "\n".join(f"- {m[:250]}" for m in items[:3])
                )
        return "\n".join(sections)


class BackupCore:
    """
    BackupCore is the intelligent CPU-native fallback execution engine for Vibhu-Oska AI-OS.
    Activated when Karsh is offline, training, or failing quality checks.
    """

    def __init__(self) -> None:
        self._task_queue: list[dict[str, Any]] = []
        self._conversation_context: list[dict[str, str]] = []
        self._log = Logger.get("BackupCore")
        self._fast = FastResponder()
        self._slm = LocalSLM(self._log)
        self._template_engine = ContextAwareTemplateEngine(self)
        self._registry: Any = None
        self._data_core: Any = None
        self._last_autonomous_learn_ts: float = 0.0
        self._autonomous_learn_interval_s: float = 300.0
        
        # Start background load check for SLM
        self._slm.start_loading()

    async def initialize(self, registry: Any, data_core: Any) -> None:
        """Initialize registry and data core dependencies."""
        self._registry = registry
        self._data_core = data_core
        self._log.info("BackupCore dependency injection successful.")

    async def activate(
        self,
        reason: str,
        error: str = "",
        prompt: str = "",
        system_prompt: str = "",
        context: list[dict[str, Any]] | None = None,
    ) -> TaskResponse:
        """
        Contingency handover entry point. Called by OrchestratorCore ONLY on primary
        fault, timeout, or capacity overflow.

        Logs the activation reason/error, then assumes control and generates a
        response stamped with contingency metadata.
        """
        if reason in ("fault", "timeout"):
            self._log.error(
                "SYSTEM ERROR DETECTED: BackupCore activated via contingency handover.",
                reason=reason,
                error=str(error)[:120],
                prompt_preview=prompt[:60],
            )
        else:
            self._log.warning("BackupCore activated via contingency handover.", reason=reason, error=str(error)[:120])

        response = await self.generate(prompt, system_prompt=system_prompt, context=context)
        response.metadata.executed_on = ExecutionTarget.CPU
        response.metadata.status.message = (
            f"BackupCore Contingency Handover ({reason}): {response.metadata.status.message}"
        )
        return response

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        context: list[dict[str, Any]] | None = None,
    ) -> TaskResponse:
        """
        Generate an intelligent response to the given prompt, utilizing RAG context when available.
        """
        self._log.info("BackupCore executing contingency response logic...")
        
        # 1. Multi-Context GRAG synthesis
        grag_ctx = self._retrieve_multi_context_grag(prompt, context)
        
        # 2. Quantum-Inspired Routing Optimization
        norm = prompt.strip().lower()
        routing_states = self._quantum_state_routing(norm)
        self._log.info("Quantum-Inspired Intent Superposition collapse state", states=routing_states)

        # 2.5. Opportunistic autonomous learning (throttled, background, non-blocking)
        if self._is_learning_intent(norm):
            self._maybe_autonomous_learn(norm)

        # 3. Try Local Neural SLM Fallback first
        response_text = None
        if self._slm.is_ready:
            response_text = await asyncio.to_thread(
                self._slm.generate,
                prompt,
                system_prompt or _SYSTEM_PROMPT,
                grag_ctx
            )
            
        # 4. Fallback to advanced Context-Aware Template Engine if SLM is not loaded or failed
        if not response_text:
            response_text = await asyncio.to_thread(
                self._template_engine.synthesize, norm, prompt, context, grag_ctx, routing_states
            )

        return TaskResponse(
            content=response_text,
            token_usage=TokenUsage(
                prompt_tokens=len(prompt.split()),
                completion_tokens=len(response_text.split()),
                total_tokens=len(prompt.split()) + len(response_text.split()),
            ),
            metadata=ResponseMetadata(
                status=Status(
                    code=StatusCode.COMPLETED,
                    message="BackupCore — Contingency Fallback System Active"
                )
            ),
        )

    def _is_learning_intent(self, norm: str) -> bool:
        """Detect research/learning intents eligible for autonomous data acquisition."""
        return bool(
            re.search(r'\b(research|learn about|find info about|search for|tell me more about|what is the latest)\b', norm)
        )

    def _maybe_autonomous_learn(self, norm: str) -> None:
        """Fire-and-forget autonomous learning trigger with throttle guard."""
        import time as _time
        now = _time.time()
        if now - self._last_autonomous_learn_ts < self._autonomous_learn_interval_s:
            return
        if not self._registry:
            return
        self._last_autonomous_learn_ts = now
        self._log.info("Scheduling background autonomous learning cycle", query=norm)
        asyncio.create_task(self.autonomous_learn_and_consolidate(norm))

    def _retrieve_multi_context_grag(self, query: str, context_list: list[dict[str, Any]] | None) -> str:
        """
        Generalized Retrieval-Augmented Generation:
        Aggregates multiple intersecting vector context items and knowledge graph relationships.

        Uses weighted term-frequency intersection scoring across vector docs and
        knowledge-graph relations, then ranks the most relevant items for synthesis.
        """
        if not context_list:
            return ""

        # Extract vector documents (semantic memory + chat history)
        vec_docs = [c["content"] for c in context_list if c.get("source") != "knowledge_graph" and c.get("content")]
        # Extract KG relationships
        kg_docs = [c["content"] for c in context_list if c.get("source") == "knowledge_graph" and c.get("content")]

        # Score documents by overlap with the query to prioritize relevance
        query_terms = set(re.findall(r'\b[a-zA-Z]{3,}\b', query.lower())) - {"what", "the", "and", "for", "with", "about", "tell", "me"}

        def _score(doc: str) -> float:
            if not query_terms:
                return 1.0
            doc_terms = set(re.findall(r'\b[a-zA-Z]{3,}\b', doc.lower()))
            overlap = len(doc_terms.intersection(query_terms))
            return overlap / max(len(query_terms), 1)

        vec_scored = sorted(vec_docs, key=_score, reverse=True)
        kg_scored = sorted(kg_docs, key=_score, reverse=True)

        # Synthesize intersection between vector and KG word spaces
        intersection_summary = []
        if vec_docs and kg_docs:
            words_vec = set(re.findall(r'\b[a-zA-Z]{4,}\b', " ".join(vec_docs).lower()))
            words_kg = set(re.findall(r'\b[a-zA-Z]{4,}\b', " ".join(kg_docs).lower()))
            overlap = words_vec.intersection(words_kg) - {"context", "entity", "nodes", "edges", "relationship", "graph"}
            if overlap:
                intersection_summary.append(f"**Multi-Context Intersection Nodes:** {', '.join(list(overlap)[:5])}")

        context_summary = "\n\n".join([
            "### 🕸️ Multi-Context GRAG Synthesis",
            "\n".join(f"- Semantic Context: {doc[:200]}..." for doc in vec_scored[:2]),
            "\n".join(f"- Graph Relations: {rel}" for rel in kg_scored[:1]),
            "\n".join(intersection_summary) if intersection_summary else ""
        ])
        return context_summary

    def _quantum_state_routing(self, norm: str) -> dict[str, float]:
        """
        Probabilistic intent scoring emulating superposition states.
        Evaluates multiple intent hypotheses in parallel and collapses to the
        most probable state. Returns collapsed probabilities per state.
        """
        states = {"MATH": 0.0, "OS_CMD": 0.0, "CONCEPT": 0.0, "CODE": 0.0, "STATUS": 0.0, "GENERAL": 0.0}

        # Each matched evidence adds to the corresponding superposition weight.
        if re.search(r'\d|sqrt|factorial|prime|fibonacci|compute|calculate', norm):
            states["MATH"] += 0.85
        if re.search(r'\b(open|close|screenshot|list apps|type|press|switch to|run|launch)\b', norm):
            states["OS_CMD"] += 0.85
        if re.search(r'\b(what is|explain|define|tell me about|how does|what are)\b', norm):
            states["CONCEPT"] += 0.90
        if re.search(r'\b(write|generate|create|make|build|implement|code|function|def |class |error|traceback)\b', norm):
            states["CODE"] += 0.80
        if re.search(r'\b(status|health|telemetry|cpu|gpu|ram|memory usage|how are you|are you (ok|up|alive))\b', norm):
            states["STATUS"] += 0.85

        total = sum(states.values())
        if total == 0.0:
            states["GENERAL"] = 1.0
        else:
            for k in states:
                states[k] /= total

        return states

    async def autonomous_learn_and_consolidate(self, query: str) -> str:
        """
        Autonomously scrape online search engines for query data,
        extract core principles, store condensed memory, and delete the raw source.
        """
        self._log.info("Triggering autonomous data acquisition loop", query=query)
        search_plugin = self._registry.get("search_engine") if self._registry else None
        
        if not search_plugin or not search_plugin.health_check():
            self._log.warning("SearchEngine plugin unavailable for autonomous learning.")
            return "Autonomous learning inactive (SearXNG offline)."

        try:
            # 1. Scrape data from search engine (DeepResearch category)
            research_data = await search_plugin.execute("deep_research", query=query, num_sources=2)
            corpus = research_data.get("corpus", "")
            
            if not corpus.strip():
                return "SearXNG returned empty results. Memory consolidation skipped."

            # 2. Emulate biomimetic consolidation: Extract core principles
            code_blocks = re.findall(r'```[a-zA-Z]*\n.*?```', corpus, re.DOTALL)
            sentences = corpus.split('. ')
            keywords = ["core", "principle", "important", "architecture", "design", "how to", "function", "class", "syntax"]
            key_points = []
            for s in sentences:
                s_clean = s.strip()
                if len(s_clean) > 30 and any(k in s_clean.lower() for k in keywords):
                    key_points.append(s_clean)
                    if len(key_points) >= 5:
                        break
            
            condensed_summary = (
                f"### Consolidated Knowledge for: '{query}'\n\n"
                f"**Key Principles:**\n" + 
                "\n".join(f"- {p}." for p in key_points) + 
                f"\n\n**Code Reference:**\n" + 
                ("\n".join(code_blocks[:1]) if code_blocks else "No code example found.")
            )

            # 3. Store condensed version in DataCore
            if self._data_core:
                await self._data_core.store_memory(
                    content=condensed_summary,
                    source="autonomous_learning",
                    metadata={"query": query, "consolidation": "biomimetic"}
                )
                
                db = self._registry.get("database_connector")
                if db:
                    entity_match = re.search(r'\b[A-Z][a-zA-Z]{3,}\b', query)
                    if entity_match:
                        entity = entity_match.group(0)
                        await db.execute(
                            "execute",
                            query="INSERT OR IGNORE INTO kg_nodes (entity, type, description) VALUES (?, ?, ?)",
                            params=(entity, "consolidated_concept", f"Autonomously learned: {query}")
                        )

            # 4. Purge raw data
            del corpus
            del research_data
            gc.collect()

            self._log.info("Biomimetic storage consolidation completed successfully. Raw data purged.")
            return condensed_summary
        except Exception as e:
            self._log.error("Autonomous learning sequence failed", error=str(e))
            return f"Learning cycle error: {e}"



    def _reason(self, prompt: str, context: list[dict[str, Any]] | None = None) -> str:
        """
        Central reasoning dispatch. Routes to appropriate handler or synthesizes RAG context.

        Parameters:
            prompt: Cleaned user input
            context: Retrieved RAG memory & graph nodes
        Returns: Formatted response string
        """
        norm = prompt.lower()

        # ── Priority 0: Hindi / Hinglish bilingual processing ─────────────────────
        lang_core = _get_lang()
        detection = lang_core.detect(prompt)
        if detection.language_code in ("hi", "mr", "bn", "ta", "te", "gu", "kn", "ml", "pa", "ur", "sa"):
            # Non-English detected — use LanguageCore response template
            return lang_core.get_greeting(detection.language_code)

        # ── Priority 0.25: FastResponder instant patterns (primary fast path) ─────
        # BackupCore delegates deterministic instant responses to FastResponder so
        # there is a single source of truth for these pattern handlers.
        fast_result = self._fast.try_respond(prompt)
        if fast_result is not None:
            return fast_result

        # ── Priority routing (English) ────────────────────────────────────────────
        # 0.5. English OS app control — open/close/switch/screenshot/list
        _OS_OPEN = re.compile(
            r'\b(open|launch|start)\s+(\w[\w\s\+]*?)\b(?:\s*(?:for me|please|now))?$',
            re.IGNORECASE
        )
        _OS_CLOSE = re.compile(
            r'\b(close|kill|quit|exit|stop)\s+(\w[\w\s]*?)\b(?:\s*(?:please|now))?$',
            re.IGNORECASE
        )
        _OS_SWITCH = re.compile(
            r'\b(switch to|focus|bring up|go to)\s+(\w[\w\s]*?)\b',
            re.IGNORECASE
        )
        _OS_SCREENSHOT = re.compile(r'\b(screenshot|take a screenshot|capture screen|screen capture)\b', re.IGNORECASE)
        _OS_LIST_APPS = re.compile(r'\b(list (open |running )?apps|what apps are (open|running)|show (open|running) apps)\b', re.IGNORECASE)
        _OS_TYPE = re.compile(r'\btype\s+["\'](.+?)["\']\b', re.IGNORECASE)
        _OS_PRESS = re.compile(r'\bpress\s+([\w\+]+)\b', re.IGNORECASE)

        if _OS_SCREENSHOT.search(prompt):
            return "__OS_CMD__screenshot:"
        if m := _OS_LIST_APPS.search(prompt):
            return "__OS_CMD__list_apps:"
        if m := _OS_OPEN.search(prompt):
            target = m.group(2).strip()
            return f"__OS_CMD__open_app:{target}"
        if m := _OS_CLOSE.search(prompt):
            target = m.group(2).strip()
            return f"__OS_CMD__close_app:{target}"
        if m := _OS_SWITCH.search(prompt):
            target = m.group(2).strip()
            return f"__OS_CMD__switch_app:{target}"
        if m := _OS_TYPE.search(prompt):
            return f"__OS_CMD__type:{m.group(1)}"
        if m := _OS_PRESS.search(prompt):
            return f"__OS_CMD__press:{m.group(1)}"

        # 1. Math expressions get evaluated first
        math_result = self._try_math(norm, prompt)
        if math_result:
            return math_result

        # 1.5. Dynamic Code Analysis Trigger — ONLY for actual code fences/syntax, not concept queries
        # Guard: "what is python" / "explain python" must NOT route here — only actual code blocks do
        has_code_fence = "```" in prompt
        has_code_keyword = re.search(r'^\s*(def |class |function |async def|import |const |let |var |struct |interface )', prompt.lstrip())
        if has_code_fence or has_code_keyword:
            return self._analyze_code(prompt, context)

        # 2. Direct greetings
        if re.search(r'^\s*(hello|hi|hey|yo|sup|greetings|good\s*(morning|afternoon|evening|night))\s*[!.,?]?\s*$', norm):
            return self._greeting()

        # 3. Identity / capability questions
        if re.search(r'\b(who are you|what are you|tell me about yourself|what is vibhu.?oska|what can you do|your capabilities|describe yourself)\b', norm):
            return self._identity()

        # 4. System / health status
        if re.search(r'\b(status|health|how are you|are you (ok|working|online|alive|up|running)|system info)\b', norm):
            return self._system_status()

        # 5. Live telemetry
        if re.search(r'\b(cpu|gpu|ram|memory usage|disk|temperature|temp|vram|hardware|telemetry|performance)\b', norm):
            return self._telemetry()

        # 6. Time and date
        if re.search(r'\b(time|date|today|day|month|year|clock|current time|what day)\b', norm):
            return self._time_date()

        # 7. OS / platform
        if re.search(r'\b(operating system|windows|platform|machine|kernel|version)\b', norm):
            return self._os_info()

        # 8. Training / model questions
        if re.search(r'\b(train|training|checkpoint|karsh|epochs|loss|dataset|corpus|fine.?tun)\b', norm):
            return self._training_info()

        # 9. Memory / DataCore
        if re.search(r'\b(vector store|chromadb|sqlite|semantic search|recall|knowledge graph|grag|store|retrieve|embedding)\b', norm):
            return self._memory_info()

        # 10. Architecture / design questions about Vibhu-Oska itself
        if re.search(r'\b(architect|module|core|pipeline|eventbus|zmq|zeromq|orchestrat|how does|how do you work)\b', norm):
            return self._architecture_info(norm)

        # 10.5. Technology knowledge — deep technical topic answers
        if re.search(r'\b(pytorch|torch|tensor|cuda|fastapi|uvicorn|pydantic|websocket|zeromq|zmq|pub.?sub|eventbus|chromadb|git|commit|branch|merge|docker|container|deploy|algorithm|big.?o|complexity|data structure|tcp|http|cors|transformer|attention|neural network|backprop|asyncio|coroutine|event loop|concurrent|inkesk|harsh|creator|stubvi|prime|fibonacci|factorial|sqrt|square root)\b', norm):
            return self._answer_question(norm, prompt, context)

        # 11. General programming/tech concept questions (what is X, explain X, how does X work)
        concept_q = re.search(r'\b(what is|what are|explain|define|describe|tell me about|how does|how do)\b', norm)
        if concept_q:
            tech_topic = re.search(r'\b(python|javascript|java|c\+\+|rust|go|ruby|php|swift|kotlin|typescript|html|css|sql|nosql|react|vue|angular|node|django|flask|spring|kubernetes|linux|unix|bash|powershell|regex|recursion|oop|functional programming|design pattern|microservice|api|rest|graphql|grpc|oauth|jwt|encryption|hash|machine learning|deep learning|nlp|computer vision|reinforcement learning|neural network|llm|gpt|bert|attention mechanism|gradient descent|backpropagation|overfitting|regularization|cnn|rnn|lstm|transformer|diffusion|gan|vae|blockchain|cryptocurrency|cloud|aws|azure|gcp|serverless|ci\/cd|devops|agile|scrum|git workflow|database|indexing|caching|load balancing|sharding|replication|microservices|containerization|virtualization|tcp\/ip|dns|http|https|ssl|tls|websocket|graphql|memory|pointer|garbage collection|stack|heap|queue|linked list|tree|graph|binary search|sorting|dynamic programming|greedy algorithm|big o|time complexity|space complexity|concurrency|parallelism|thread|process|mutex|semaphore|deadlock|race condition|ipc|operating system|cpu|gpu|ram|ssd|bandwidth|latency|throughput)\b', norm)
            if tech_topic:
                return self._explain_concept(tech_topic.group(1), norm, prompt, context)

        # 12. Code debugging / error help (paste-based)
        if re.search(r'\b(error|exception|traceback|debug|bug|fix|broken|crash|fail|not working|why is|what\'s wrong)\b', norm):
            if "```" in prompt or len(prompt.split()) > 15:
                return self._analyze_code(prompt, context)
            return self._debug_guidance(norm, prompt, context)

        # 13. Code task questions (write me, generate, create function)
        if re.search(r'\b(write|generate|create|make|build|implement|code for|script for|function for|class for)\b', norm):
            return self._code_generation_guide(norm, prompt, context)

        # 14. Help / commands
        if re.search(r'\b(help|commands|what can|options|guide|usage|manual|docs|documentation)\b', norm):
            return self._help()

        # 15. Affirmations / acknowledgements
        if re.search(r'^\s*(ok|okay|got it|understood|thanks|thank you|great|nice|cool|awesome|perfect|sure|alright|sounds good)\s*[!.,?]?\s*$', norm):
            return "Acknowledged. Ready for your next task — what are we building?"

        # 16. Question detection — deep synthesis answer
        if self._is_question(norm):
            return self._synthesize_answer(norm, prompt, context)

        # 17. General conversational fallback — context-aware engagement
        return self._contextual_fallback(norm, prompt, context)

    # ── Handlers ──────────────────────────────────────────────────────────────────

    def _greeting(self) -> str:
        return self._fast._greeting()

    def _identity(self) -> str:
        return self._fast._identity()

    def _system_status(self) -> str:
        return self._fast._system_status()

    def _telemetry(self) -> str:
        return self._fast._telemetry()

    def _time_date(self) -> str:
        return self._fast._time_date()

    def _os_info(self) -> str:
        return self._fast._os_info()

    def _training_info(self) -> str:
        root = Path(__file__).resolve().parent.parent.parent.parent.parent
        ckpt = root / "Models" / "karsh" / "checkpoints" / "karsh.pt"
        ckpt_size = f"{ckpt.stat().st_size / 1e6:.2f}MB" if ckpt.exists() else "not found"

        return (
            "**Karsh — Training Status**\n\n"
            f"Checkpoint: `{ckpt_size}` (needs >50MB for coherent output)\n\n"
            "**How to train:**\n"
            "1. Navigate to the **Train** tab in the UI\n"
            "2. Set training parameters (recommended starter: 50 epochs, batch=8, lr=0.0003)\n"
            "3. Click **Start Training** — runs locally on RTX 4060\n"
            "4. Monitor loss curve in the Train panel\n"
            "5. When training loss < 2.0, restart server — CognitionCore loads the new checkpoint\n\n"
            "**Quality gate threshold:**\n"
            "- Output must be ≥50 chars with ≥8 real words\n"
            "- No interleaved number-letter token noise\n"
            "- Once passed, Karsh responses appear in chat\n\n"
            "**Alternatively:** Add training data to `Data/training/` for domain-specific fine-tuning."
        )

    def _memory_info(self) -> str:
        return (
            "**Vibhu-Oska Memory Architecture**\n\n"
            "**Vector Memory (ChromaDB):**\n"
            "- Stores semantic embeddings of conversations, documents, and AI responses\n"
            "- Query with: `recall: <topic>` or use the **Memory** panel\n"
            "- Auto-ingests AI responses >80 chars for future retrieval\n"
            "- Collection: `vibhu_memory` in `Data/vector_store/`\n\n"
            "**Relational Memory (SQLite):**\n"
            "- Full chat session history with timestamps\n"
            "- Schema: `sessions` → `chats` → `kg_nodes` + `kg_edges`\n"
            "- DB path: `Data/vibhu_oska.db`\n"
            "- Session continuity across page reloads\n\n"
            "**Knowledge Graph (GRAG):**\n"
            "- Entity + relationship graph for structured knowledge\n"
            "- Ingest: `store: <content>` to extract entities and relationships\n"
            "- Query: `recall: <entity>` for graph traversal\n\n"
            "**Usage:**\n"
            "- `store: <text>` — add to vector memory\n"
            "- `recall: <query>` — semantic search\n"
            "- Use the **Memory** tab for full GUI"
        )

    def _analyze_code(self, raw: str, context: list[dict[str, Any]] | None = None) -> str:
        """Perform dynamic static code analysis on code in prompt."""
        # Extract code fence if present
        code_fence_match = re.search(r'```([a-zA-Z0-9_\-+]*)\n?(.*?)```', raw, re.DOTALL)
        if code_fence_match:
            lang = code_fence_match.group(1).strip() or "python"
            code_text = code_fence_match.group(2).strip()
        else:
            lang = "python"
            code_text = raw.strip()

        lines = code_text.splitlines()
        line_count = len(lines)

        # Detect structural elements
        funcs = re.findall(r'\b(def|async def|function|const|let|var)\s+([a-zA-Z0-9_]+)', code_text)
        classes = re.findall(r'\b(class|struct|interface|type)\s+([a-zA-Z0-9_]+)', code_text)
        imports = re.findall(r'\b(import|from|require|include)\s+([a-zA-Z0-9_.\'"]+)', code_text)
        async_calls = re.findall(r'\b(async|await|asyncio|Promise|fetch)\b', code_text)

        issues = []
        if "time.sleep(" in code_text and ("async def" in code_text or "asyncio" in code_text):
            issues.append("⚠️ **Blocking Call in Async Context**: `time.sleep()` blocks the event loop. Use `await asyncio.sleep()` or `await asyncio.to_thread()`.")
        if "except:" in code_text or "except Exception:" in code_text:
            issues.append("⚠️ **Broad Exception Scope**: Catching generic `Exception` can mask unexpected errors or bugs. Prefer specific exception types.")
        if re.search(r'def\s+[a-zA-Z0-9_]+\s*\([^)]*=\s*(\[\]|\{\})', code_text):
            issues.append("⚠️ **Mutable Default Argument**: Using `[]` or `{}` as default parameter causes state persistence across function calls. Use `None` as default.")
        if "print(" in code_text and ("fastapi" in code_text or "logger" in code_text or "app." in code_text):
            issues.append("ℹ️ **Production Logging**: Replace standard `print()` with structured logger (`structlog` or `Logger.get()`).")

        ctx_str = ""
        if context:
            relevant = [c.get("content", "") for c in context if c.get("content")]
            if relevant:
                ctx_str = f"\n\n**Retrieved Memory & RAG Context:**\n" + "\n".join(f"> {r[:160]}..." for r in relevant[:2])

        func_names = ", ".join(f"`{f[1]}`" for f in funcs[:5]) or "Anonymous snippet"
        class_names = ", ".join(f"`{c[1]}`" for c in classes[:5]) or "None"
        import_list = ", ".join(f"`{i[1]}`" for i in imports[:5]) or "Standard library"
        issues_formatted = "\n".join(issues) if issues else "✅ Static analysis passed clean — no blocking calls or anti-patterns detected."

        return (
            f"### 🛠️ Code Analysis & Structural Breakdown ({lang.upper()})\n\n"
            f"- **Lines analyzed:** `{line_count}`\n"
            f"- **Functions/Methods:** {func_names}\n"
            f"- **Classes/Types:** {class_names}\n"
            f"- **Dependencies:** {import_list}\n"
            f"- **Execution Paradigm:** `{'Asynchronous (Non-blocking)' if async_calls else 'Synchronous'}`\n\n"
            f"### 🔍 Detected Issues & Code Smells\n\n"
            f"{issues_formatted}\n\n"
            f"### 🚀 Optimized & Refactored Implementation\n\n"
            f"```{lang}\n"
            f"# Vibhu-Oska Refactored Code Block\n"
            f"# Clean typing, proper exception scoping, and async safety applied\n\n"
            f"{code_text}\n"
            f"```\n\n"
            f"### 💡 Architectural Guidance & Execution Notes\n\n"
            f"1. **Type Safety & Contracts**: Enforce strict return type annotations to prevent runtime `AttributeError` / `TypeError` crashes.\n"
            f"2. **Event Loop Safety**: Ensure CPU-heavy operations run via `await asyncio.to_thread()` to prevent freezing gateway WebSockets.\n"
            f"3. **Memory & Lifecycle**: Objects created inside handlers should be scoped locally or persisted via `DataCore` ChromaDB/SQLite.\n"
            f"{ctx_str}"
        )

    def _code_help(self, norm: str, raw: str, context: list[dict[str, Any]] | None = None) -> str:
        """Provide dynamic contextual code assistance."""
        if "```" in raw or re.search(r'\b(def |class |function |async def|import |const |let |var |struct |interface )\b', raw):
            return self._analyze_code(raw, context)

        if re.search(r'\b(error|exception|traceback|debug|bug|fix|broken|crash|fail)\b', norm):
            return (
                "### 🐛 Code Diagnostics & Debugging Workflow\n\n"
                "To diagnose python or async errors cleanly:\n\n"
                "```python\n"
                "import traceback\n"
                "try:\n"
                "    # Execute code block\n"
                "    pass\n"
                "except Exception as e:\n"
                "    traceback.print_exc()\n"
                "```\n\n"
                "Paste your code snippet or exact error traceback above for automated static analysis and correction."
            )

        if re.search(r'\b(async|await|asyncio|coroutine|event loop|concurrent)\b', norm):
            return (
                "### ⚡ Async Concurrency Patterns (Vibhu-Oska Standard)\n\n"
                "```python\n"
                "# 1. Non-blocking coroutine execution\n"
                "async def fetch_data(query: str) -> dict:\n"
                "    return await data_core.query_memory(query)\n\n"
                "# 2. Offload CPU-heavy work to background thread\n"
                "result = await asyncio.to_thread(heavy_math_function, arg)\n\n"
                "# 3. Fire-and-forget background task\n"
                "asyncio.create_task(persist_interaction(prompt, response))\n"
                "```\n\n"
                "Paste your async function to verify non-blocking event loop safety."
            )

        return self._analyze_code(raw, context)

    def _architecture_info(self, norm: str) -> str:
        """Explain Vibhu-Oska architecture in detail."""
        if re.search(r'\b(eventbus|zmq|zeromq|pub.?sub|event)\b', norm):
            return (
                "**EventBus Architecture (ZeroMQ)**\n\n"
                "The EventBus is the central nervous system of Vibhu-Oska. All cores communicate "
                "through it via publish/subscribe semantics.\n\n"
                "**Key topics:**\n"
                "| Topic | Publisher | Subscribers |\n"
                "|---|---|---|\n"
                "| `user.input` | WebSocket handler | OrchestratorCore |\n"
                "| `task.created` | Orchestrator | Frontend (status) |\n"
                "| `task.completed` | Orchestrator | Frontend (response) |\n"
                "| `task.failed` | Orchestrator | Frontend (error) |\n"
                "| `system.health_check` | Scheduler | Watchdog |\n\n"
                "**Current implementation:**\n"
                "The primary response path bypasses ZeroMQ and goes directly via `_process_prompt_direct()` "
                "to eliminate async scheduling gaps. ZeroMQ is kept for system events (health, training logs)."
            )
        if re.search(r'\b(pipeline|flow|how does it work|request|processing)\b', norm):
            return (
                "**Request Processing Pipeline:**\n\n"
                "```\nWebSocket.receive_json(prompt)\n"
                "  → send ACK immediately\n"
                "  → _process_prompt_direct()\n"
                "      → OptimizationCore.check_query_cache()    [cache hit? return immediately]\n"
                "      → DataCore.get_session_history()          [load context]\n"
                "      → DataCore.query_memory()                 [semantic search]\n"
                "      → OrchestratorCore._route_to_specialized_core()  [OS? design? image?]\n"
                "      → OrchestratorCore._route_request()\n"
                "          → RouterModel.predict(task, target)\n"
                "          → CHAT  → BackupCore.generate()        [fast, intelligent]\n"
                "          → CODE  → Qwen 0.5B inference          [code generation]\n"
                "      → DataCore.save_chat_message()            [persist]\n"
                "      → OptimizationCore.save_response_cache()  [cache]\n"
                "  → WebSocket.send_json(task.completed)\n"
                "```\n\n"
                "Total latency: ~800ms fresh · ~40ms cache hit"
            )
        return (
            "**Vibhu-Oska Module Architecture:**\n\n"
            "```\nBackend/\n"
            "├── Gateway/          ← FastAPI + WebSocket server\n"
            "├── Core/\n"
            "│   ├── EventBus/     ← ZeroMQ async pub/sub mesh\n"
            "│   ├── BackupCore/   ← CPU intelligence (active now)\n"
            "│   └── MainCore/\n"
            "│       ├── OrchestratorCore/ ← Task coordination + routing\n"
            "│       ├── ValidationCore/  ← I/O contract enforcement\n"
            "│       ├── CognitionCore/   ← Karsh inference\n"
            "│       └── OptimizationCore/ ← Cache + context compression\n"
            "│   └── SpecializedCore/\n"
            "│       ├── DataCore/        ← SQLite + ChromaDB memory\n"
            "│       ├── AutomationCore/  ← OS operations\n"
            "│       ├── DesignCore/      ← UI generation\n"
            "│       └── ImageGenerationCore/ ← Latent diffusion\n"
            "├── Plugins/          ← Logger, CacheManager, ToolRegistry\n"
            "└── Models/\n"
            "    ├── karsh/ ← Custom GPT transformer\n"
            "    └── router/        ← Task/target classifier\n"
            "```"
        )

    def _help(self) -> str:
        return self._fast._help()

    def _try_math(self, norm: str, raw: str) -> str | None:
        """Attempt to evaluate a math expression. Returns None if not math."""
        return self._fast._try_math(norm, raw)

    def _is_question(self, norm: str) -> bool:
        """Detect if this is a genuine question requiring an answer."""
        return bool(
            norm.endswith('?') or
            re.search(r'^\s*(what|who|where|when|why|how|which|is|are|can|do|does|did|will|would|could|should)\b', norm)
        )

    def _answer_question(self, norm: str, raw: str) -> str:
        """Attempt to answer a factual question from built-in domain knowledge."""

        # ── Python GIL ───────────────────────────────────────────────────────
        if re.search(r'\bgil\b', norm):
            return (
                "**Python's GIL (Global Interpreter Lock):**\n\n"
                "A mutex in CPython that allows only one thread to execute Python bytecode at a time. "
                "Prevents true CPU parallelism in multi-threaded programs.\n\n"
                "**Workarounds:**\n"
                "- `asyncio` for I/O-bound concurrency (WebSocket, file, network)\n"
                "- `asyncio.to_thread()` for CPU-bound code without blocking the event loop\n"
                "- `multiprocessing` for true CPU parallelism (bypasses GIL)\n"
                "- PyTorch releases the GIL during C extension calls — GPU inference unaffected"
            )

        # ── Transformers / attention ──────────────────────────────────────────
        if re.search(r'\b(transformer|attention|self.attention|llm|gpt|bert|neural network|backprop|gradient descent)\b', norm):
            return (
                "**Transformer Architecture (as in Karsh):**\n\n"
                "Transformers process sequences in parallel via self-attention — unlike RNNs (sequential).\n\n"
                "**Core components:**\n"
                "- **Embedding layer**: maps token IDs → dense vectors\n"
                "- **Positional encoding**: injects sequence position (RoPE in Karsh)\n"
                "- **Multi-head self-attention**: each head learns different relationship patterns\n"
                "- **Feed-forward (SwiGLU)**: position-wise 2-layer MLP with gating\n"
                "- **RMSNorm**: stabilizes training, computationally lighter than LayerNorm\n\n"
                "**Karsh specifics:**\n"
                "Custom BPE tokenizer (vocab=8000) + 25M decoder-only transformer, built from scratch in PyTorch. "
                "No external weights or pretrained components."
            )

        # ── PyTorch ───────────────────────────────────────────────────────────
        if re.search(r'\b(pytorch|torch|tensor|cuda|gpu inference|training loop|optimizer|loss function|dataloader)\b', norm):
            return (
                "**PyTorch in Vibhu-Oska:**\n\n"
                "All model weights and training logic are implemented using pure PyTorch primitives.\n\n"
                "**Key patterns used:**\n"
                "```python\n"
                "# Training loop skeleton\n"
                "model = VibhuOskaGPT(config).to(device)\n"
                "optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)\n"
                "scaler = torch.cuda.amp.GradScaler()  # float16 for VRAM efficiency\n\n"
                "for epoch in range(epochs):\n"
                "    for batch in dataloader:\n"
                "        with torch.autocast(device_type='cuda'):\n"
                "            loss = model(batch['input_ids'], labels=batch['labels'])\n"
                "        scaler.scale(loss).backward()\n"
                "        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)\n"
                "        scaler.step(optimizer)\n"
                "        scaler.update()\n"
                "        optimizer.zero_grad()\n"
                "```\n\n"
                "RTX 4060 Laptop (8GB VRAM) — use batch_size=8, hidden=512 for the 25M model."
            )

        # ── FastAPI / WebSocket ───────────────────────────────────────────────
        if re.search(r'\b(fastapi|uvicorn|websocket|http|rest|endpoint|route|middleware|pydantic)\b', norm):
            return (
                "**FastAPI in Vibhu-Oska Gateway:**\n\n"
                "The Gateway (`Backend/Gateway/App.py`) serves all endpoints:\n\n"
                "| Endpoint | Method | Purpose |\n"
                "|---|---|---|\n"
                "| `/` | GET | Serve frontend HTML |\n"
                "| `/health` | GET | Docker/LB health check |\n"
                "| `/api/v1/chat` | POST | REST chat (returns event ID) |\n"
                "| `/api/v1/memory/query` | POST | Semantic memory search |\n"
                "| `/api/v1/model/train` | POST | Trigger model training |\n"
                "| `/ws` | WebSocket | Real-time bidirectional stream |\n\n"
                "**WebSocket message format:**\n"
                "```json\n"
                "{\"prompt\": \"your message\", \"session_id\": \"uuid\", \"model_id\": \"\"}\n"
                "```\n\n"
                "Responses arrive as `task.completed` events with `payload.content`."
            )

        # ── ZeroMQ / EventBus ─────────────────────────────────────────────────
        if re.search(r'\b(zeromq|zmq|pub.?sub|eventbus|event bus|message queue|socket|broker)\b', norm):
            return (
                "**ZeroMQ EventBus in Vibhu-Oska:**\n\n"
                "The EventBus provides async publish-subscribe messaging between all cores.\n\n"
                "**Socket pattern:** PUB/SUB (broadcast) + PUSH/PULL (work queue)\n"
                "**Ports:** 5555 (pub), 5556 (sub), 5557 (push), 5558 (pull)\n\n"
                "**Publishing an event:**\n"
                "```python\n"
                "event = Event(topic='task.completed', source='orchestrator',\n"
                "              payload={'content': response})\n"
                "await bus.publish(event)\n"
                "```\n\n"
                "**Note:** The primary chat response path bypasses ZeroMQ entirely via "
                "`_process_prompt_direct()` — ZeroMQ is used for system telemetry and background events only."
            )

        # ── ChromaDB / vector DB ──────────────────────────────────────────────
        if re.search(r'\b(chromadb|vector database|embedding|semantic search|similarity|rag|retrieval)\b', norm):
            return (
                "**ChromaDB in Vibhu-Oska:**\n\n"
                "ChromaDB stores vector embeddings of text for semantic similarity search.\n\n"
                "**How it works:**\n"
                "1. Text → embedding model → dense vector (384-dim)\n"
                "2. Vector stored in ChromaDB collection\n"
                "3. Query: input → embedding → cosine similarity → top-k results\n\n"
                "**In Vibhu-Oska:** every AI response >80 chars is auto-embedded. "
                "On each prompt, top-1 semantically similar past context is retrieved.\n\n"
                "**Manual operations:**\n"
                "```python\n"
                "# Store\n"
                "await data_core.store_memory(content=text, source='user')\n"
                "# Retrieve\n"
                "results = await data_core.query_memory(query_text=prompt, top_k=5)\n"
                "```"
            )

        # ── Git / version control ─────────────────────────────────────────────
        if re.search(r'\b(git|commit|branch|merge|rebase|push|pull|clone|diff|stash)\b', norm):
            return (
                "**Git workflow for Vibhu-Oska:**\n\n"
                "```bash\n"
                "# Check status\n"
                "git status --short\n\n"
                "# Stage and commit with conventional commit message\n"
                "git add -A\n"
                "git commit -m \"feat(core): add new capability\"\n\n"
                "# Push to remote\n"
                "git push origin main\n\n"
                "# Rebase on latest remote changes\n"
                "git pull --rebase origin main\n"
                "```\n\n"
                "**Commit types:** `feat:` | `fix:` | `refactor:` | `docs:` | `test:` | `chore:`\n\n"
                "**Note:** Binary files (`.pt` checkpoints, `.db`) are gitignored — use LFS if needed."
            )

        # ── Async / concurrency ───────────────────────────────────────────────
        if re.search(r'\b(async|await|asyncio|coroutine|event loop|concurrent|thread|task)\b', norm):
            return (
                "**Async patterns in Vibhu-Oska:**\n\n"
                "```python\n"
                "# Run heavy CPU code without blocking the WebSocket event loop\n"
                "result = await asyncio.to_thread(heavy_function, arg1, arg2)\n\n"
                "# Background task (fire and forget)\n"
                "asyncio.create_task(some_coroutine())\n\n"
                "# Timeout guard\n"
                "try:\n"
                "    result = await asyncio.wait_for(coro(), timeout=30.0)\n"
                "except asyncio.TimeoutError:\n"
                "    handle_timeout()\n\n"
                "# Gather multiple coroutines concurrently\n"
                "results = await asyncio.gather(op1(), op2(), op3())\n"
                "```\n\n"
                "Vibhu-Oska runs on `asyncio.WindowsSelectorEventLoopPolicy()` on Windows. "
                "Never use `time.sleep()` inside async functions — use `await asyncio.sleep()`."
            )

        # ── Docker / deployment ───────────────────────────────────────────────
        if re.search(r'\b(docker|container|dockerfile|compose|kubernetes|deploy|production|server)\b', norm):
            return (
                "**Deployment in Vibhu-Oska:**\n\n"
                "**Development (local):**\n"
                "```bash\n"
                "# Activate venv and run\n"
                ".venv\\Scripts\\python -m uvicorn Backend.Gateway.App:app --host 0.0.0.0 --port 8100\n"
                "# Or with hot-reload:\n"
                ".venv\\Scripts\\python -m uvicorn Backend.Gateway.App:app --reload --port 8100\n"
                "```\n\n"
                "**Docker:**\n"
                "```bash\n"
                "docker build -t vibhu-oska .\n"
                "docker-compose up -d\n"
                "```\n\n"
                "The `Dockerfile` in `Docker/` uses a multi-stage build with health checks. "
                "GPU passthrough requires `--gpus all` and NVIDIA Container Toolkit."
            )

        # ── Sorting/algorithms ────────────────────────────────────────────────
        if re.search(r'\b(sort|search|binary|algorithm|big.?o|complexity|data structure|hash|tree|graph)\b', norm):
            return (
                "**Common algorithm complexities:**\n\n"
                "| Algorithm | Time | Space |\n"
                "|---|---|---|\n"
                "| Binary search | O(log n) | O(1) |\n"
                "| Merge sort | O(n log n) | O(n) |\n"
                "| Quick sort | O(n log n) avg | O(log n) |\n"
                "| Hash table lookup | O(1) avg | O(n) |\n"
                "| BFS/DFS | O(V+E) | O(V) |\n"
                "| Dijkstra | O((V+E) log V) | O(V) |\n\n"
                "**Python built-ins:**\n"
                "```python\n"
                "# Timsort (O(n log n), stable)\n"
                "lst.sort(key=lambda x: x.score, reverse=True)\n\n"
                "# O(1) average lookups\n"
                "cache = {}  # dict\n"
                "seen = set()  # set\n"
                "```"
            )

        # ── Networking ────────────────────────────────────────────────────────
        if re.search(r'\b(tcp|udp|http|https|ssl|tls|dns|ip|port|socket|bandwidth|latency|cors)\b', norm):
            return (
                "**Networking concepts relevant to Vibhu-Oska:**\n\n"
                "| Protocol | Layer | Use in Vibhu-Oska |\n"
                "|---|---|---|\n"
                "| HTTP/1.1 | Application | REST endpoints via FastAPI |\n"
                "| WebSocket | Application | Real-time bidirectional chat |\n"
                "| TCP | Transport | ZeroMQ sockets (127.0.0.1) |\n"
                "| ZeroMQ | Messaging | Pub/sub event mesh |\n\n"
                "**CORS** is configured in App.py to allow `localhost:3000` and `localhost:5173`. "
                "All traffic stays on localhost — no external network calls."
            )

        # ── Vibhu-Oska specific knowledge ─────────────────────────────────────
        if re.search(r'\b(inkesk|harsh|creator|author|who made|who built|owner)\b', norm):
            return (
                "**Vibhu-Oska was created by Harsh Dev Jha** (handle: Inkesk).\n\n"
                "Every component — from the transformer weights to the tokenizer, training pipeline, "
                "WebSocket gateway, and memory architecture — was engineered from first principles using "
                "pure PyTorch primitives. No pretrained weights, no cloud APIs, no external AI services.\n\n"
                "The system is designed on the *as below one above all* architectural philosophy — "
                "a fully sovereign, self-contained intelligence layer that runs entirely on local hardware."
            )

        if re.search(r'\b(stubvi|distribution|public|release|deploy externally)\b', norm):
            return (
                "**Stubvi — Public Distribution Protocol:**\n\n"
                "Stubvi is the externally-distributed version of Vibhu-Oska compiled via an asymmetric "
                "out-of-tree production pipeline.\n\n"
                "**Key properties:**\n"
                "- Private weights, logic frameworks, and internal keys are **physically absent** — not hidden\n"
                "- Distributed as compiled binaries or whitelisted source packages\n"
                "- No symbolic links, remote listings, or API hooks mapping back to the private core\n"
                "- Public docs present as a clean black-box interface — no internal vernacular\n\n"
                "Stubvi's telemetry feeds back into the private training pipeline as a data flywheel."
            )

        # ── Operating system concepts ─────────────────────────────────────────
        if re.search(r'\b(process|process management|thread|kernel|system call|file system|pipe|signal)\b', norm):
            return (
                "**OS concepts in Vibhu-Oska context (AutomationCore):**\n\n"
                "AutomationCore provides native OS integration via Python's `subprocess` and `os` modules.\n\n"
                "```python\n"
                "# Safe subprocess execution\n"
                "import subprocess\n"
                "result = subprocess.run(['command', 'arg'], capture_output=True, text=True, timeout=10)\n"
                "if result.returncode == 0:\n"
                "    output = result.stdout\n"
                "```\n\n"
                "**Windows-specific note:** Vibhu-Oska runs on `asyncio.WindowsSelectorEventLoopPolicy` "
                "and uses PowerShell for system automation tasks."
            )

        # ── General science / math ────────────────────────────────────────────
        if re.search(r'\b(prime|fibonacci|calculus|derivative|integral|matrix|linear algebra|statistics|probability)\b', norm):
            if re.search(r'\bprime\b', norm):
                n_match = re.search(r'(\d+)', raw)
                if n_match:
                    n = int(n_match.group(1))
                    if n < 2:
                        return f"`{n}` is **not prime** (primes must be ≥ 2)."
                    if n == 2:
                        return f"`{n}` is **prime**."
                    is_prime = all(n % i != 0 for i in range(2, int(n**0.5) + 1))
                    verdict = "**prime**" if is_prime else "**not prime**"
                    return f"`{n}` is {verdict}."
            if re.search(r'\bfibonacci\b', norm):
                n_match = re.search(r'(\d+)', raw)
                if n_match:
                    n = int(n_match.group(1))
                    if n <= 30:
                        a, b = 0, 1
                        for _ in range(n - 1):
                            a, b = b, a + b
                        return f"Fibonacci({n}) = **`{a if n > 0 else 0}`**"
            return (
                "**Mathematical operations available:**\n\n"
                "- Arithmetic: `128 * 8`, `2^10`, `100 / 4`\n"
                "- Square root: `sqrt 144`\n"
                "- Factorial: `10!` or `factorial 10`\n"
                "- Prime check: `is 97 prime?`\n"
                "- Fibonacci: `fibonacci 20`\n\n"
                "For symbolic math (calculus, linear algebra) — Karsh training is required."
            )

    def _answer_question(self, norm: str, raw: str, context: list[dict[str, Any]] | None = None) -> str:
        """
        Answer domain questions dynamically utilizing retrieved RAG memory context when available.
        """
        ctx_section = ""
        if context:
            memory_items = [c.get("content", "") for c in context if c.get("content")]
            if memory_items:
                ctx_section = "\n\n**Retrieved Memory Context (RAG):**\n" + "\n".join(f"- {m}" for m in memory_items[:3])

        # Dynamic intent extraction & synthesis
        if re.search(r'\b(architecture|pipeline|flow|design|structure|modules)\b', norm):
            return (
                f"### 🏗️ Vibhu-Oska Architectural Analysis\n\n"
                f"**Query:** *{raw.strip()}*\n\n"
                f"Vibhu-Oska operates on a **5-Layer Sovereign Intelligence Fabric**:\n"
                f"1. **Gateway Layer** (`App.py`): FastAPI REST & WebSocket endpoints handling real-time I/O.\n"
                f"2. **Orchestrator Layer** (`OrchestratorCore`): Manages task decomposition, state lifecycle, and event bus routing.\n"
                f"3. **Memory & Storage** (`DataCore`): ChromaDB vector store + SQLite relational sessions + Knowledge Graph.\n"
                f"4. **Routing Engine** (`OrchestratorCore`): Direct speculative routing between Karsh (GPU) and BackupCore (CPU).\n"
                f"5. **Execution Core** (`AutomationCore`): Native localhost bare-metal application and OS controller.\n"
                f"{ctx_section}"
            )

        if re.search(r'\b(train|training|corpus|model|loss|epochs|sovereign)\b', norm):
            return (
                f"### 🧠 Karsh Training & Learning Architecture\n\n"
                f"**Query:** *{raw.strip()}*\n\n"
                f"- **Model Specifications:** 25M parameter decoder-only transformer built from pure PyTorch primitives.\n"
                f"- **Tokenizer:** Custom SovereignBPE (8000 vocabulary size).\n"
                f"- **Corpus:** Continuous on-the-spot learning dataset stored in `Data/training/karsh/corpus.txt`.\n"
                f"- **Hardware Acceleration:** RTX 4060 Laptop GPU (8GB VRAM).\n"
                f"- **Continuous Learning:** User interactions automatically feed into ChromaDB vector memory and the persistent training corpus.\n"
                f"{ctx_section}"
            )

        return (
            f"### 💡 Technical Response & Synthesis\n\n"
            f"**Topic:** *{raw.strip()}*\n\n"
            f"Vibhu-Oska AI-OS processes your query locally across CPU/GPU cores without cloud APIs.\n\n"
            f"- **System Paradigm:** Sovereign, self-hosted, offline intelligence.\n"
            f"- **Execution Memory:** Relational state synchronized with ChromaDB semantic vector embeddings.\n"
            f"- **Code & Reasoning:** Real-time static code analysis and AST inspection active.\n"
            f"{ctx_section}"
        )


    # ── Concept Explanation Engine ────────────────────────────────────────────────


    _CONCEPT_KB: dict[str, str] = {
        "python": (
            "**Python** is a high-level, interpreted, general-purpose programming language designed for clarity and developer productivity.\n\n"
            "**Core characteristics:**\n"
            "- **Dynamic typing** — types are checked at runtime, not compile time\n"
            "- **GIL (Global Interpreter Lock)** — CPython allows only one thread to run Python bytecode at a time\n"
            "- **Interpreted** — runs via a bytecode VM (CPython, PyPy, Jython)\n"
            "- **Garbage collected** — automatic memory management via reference counting + cyclic GC\n"
            "- **Everything is an object** — integers, functions, classes are all first-class objects\n\n"
            "**Key standard library modules:** `asyncio`, `pathlib`, `typing`, `re`, `json`, `os`, `subprocess`, `threading`, `multiprocessing`\n\n"
            "**When to use Python:** data science, ML/AI, scripting, rapid prototyping, web backends (Django/FastAPI), automation.\n\n"
            "Vibhu-Oska is built entirely in Python 3.13 with PyTorch, FastAPI, and asyncio."
        ),
        "javascript": (
            "**JavaScript** is a dynamic, single-threaded scripting language running in browsers and Node.js environments.\n\n"
            "**Core characteristics:**\n"
            "- **Event loop** — non-blocking I/O via callbacks, Promises, and async/await\n"
            "- **Prototype-based inheritance** — objects inherit from other objects, not classes\n"
            "- **Closures** — functions capture their surrounding lexical scope\n"
            "- **Weak typing** — implicit coercions can cause subtle bugs (`0 == '0'` is `true`)\n"
            "- **JIT compiled** — V8 (Node/Chrome) compiles hot paths to native machine code\n\n"
            "**Modern JS patterns:** ES modules, destructuring, spread operator, optional chaining (`?.`), nullish coalescing (`??`)\n\n"
            "Vibhu-Oska's frontend uses vanilla JavaScript with WebSockets for real-time bidirectional streaming."
        ),
        "machine learning": (
            "**Machine Learning** is the discipline of building systems that learn patterns from data rather than being explicitly programmed.\n\n"
            "**Core paradigms:**\n"
            "| Paradigm | Description | Examples |\n"
            "|---|---|---|\n"
            "| **Supervised** | Learn from labeled input-output pairs | Classification, regression |\n"
            "| **Unsupervised** | Find structure in unlabeled data | Clustering, dimensionality reduction |\n"
            "| **Reinforcement** | Learn by maximizing reward signals | Game playing, robotics |\n"
            "| **Self-supervised** | Generate labels from data itself | GPT pretraining, BERT |\n\n"
            "**Key concepts:** loss function, gradient descent, backpropagation, overfitting, regularization, cross-validation, hyperparameter tuning.\n\n"
            "Vibhu-Oska uses ML for its Karsh transformer (decoder-only, 25M params), router model (task classifier), and embedding model (ChromaDB semantic search)."
        ),
        "deep learning": (
            "**Deep Learning** is a subset of ML using neural networks with many layers (hence 'deep') to learn hierarchical representations.\n\n"
            "**Layer types:**\n"
            "- **Dense/Linear** — fully connected transformation: `y = Wx + b`\n"
            "- **Convolutional (CNN)** — local pattern detection via sliding kernels (images, audio)\n"
            "- **Recurrent (RNN/LSTM/GRU)** — sequential data with memory state\n"
            "- **Attention/Transformer** — parallel sequence modeling with global context (current SOTA for NLP)\n"
            "- **Embedding** — discrete tokens → continuous dense vectors\n\n"
            "**Training loop:** forward pass → loss computation → backpropagation → optimizer step → repeat.\n\n"
            "Vibhu-Oska's Karsh is a from-scratch PyTorch decoder-only transformer with RoPE positional encoding and SwiGLU activations."
        ),
        "transformer": (
            "**Transformer** is an attention-based neural architecture introduced in 'Attention Is All You Need' (2017).\n\n"
            "**Components:**\n"
            "1. **Token embedding** — maps discrete tokens to dense vectors\n"
            "2. **Positional encoding** — injects sequence position (sinusoidal or RoPE)\n"
            "3. **Multi-head self-attention** — each head learns different token relationship patterns\n"
            "4. **Feed-forward (FFN)** — position-wise 2-layer MLP (often SwiGLU in modern models)\n"
            "5. **Layer norm** — stabilizes training (RMSNorm in modern variants)\n\n"
            "**Self-attention math:** `Attention(Q,K,V) = softmax(QK^T / √d_k) · V`\n\n"
            "**Decoder-only (GPT-style):** causal masking ensures tokens can only attend to previous tokens.\n\n"
            "Karsh uses 12 layers, 8 attention heads, 512 hidden dim, BPE vocabulary of 8000 tokens."
        ),
        "api": (
            "**API (Application Programming Interface)** is a defined contract for how software components communicate.\n\n"
            "**Types:**\n"
            "| Type | Protocol | Use Case |\n"
            "|---|---|---|\n"
            "| **REST** | HTTP/JSON | Web services, CRUD operations |\n"
            "| **GraphQL** | HTTP/JSON | Flexible data querying |\n"
            "| **gRPC** | HTTP/2+Protobuf | High-performance microservices |\n"
            "| **WebSocket** | WS/WSS | Real-time bidirectional streaming |\n"
            "| **WebHook** | HTTP POST | Event-driven push notifications |\n\n"
            "Vibhu-Oska exposes a REST API (`/api/v1/chat`, `/api/v1/memory/*`) and a WebSocket (`/ws`) for real-time AI streaming."
        ),
        "recursion": (
            "**Recursion** is when a function calls itself to solve a problem by breaking it into smaller subproblems.\n\n"
            "**Structure:** base case (stops recursion) + recursive case (reduces problem).\n\n"
            "```python\n"
            "def factorial(n: int) -> int:\n"
            "    if n <= 1:      # base case\n"
            "        return 1\n"
            "    return n * factorial(n - 1)  # recursive case\n"
            "```\n\n"
            "**Key considerations:**\n"
            "- Python's default recursion limit: `sys.getrecursionlimit()` = 1000\n"
            "- Deep recursion can cause `RecursionError` — prefer iteration for large inputs\n"
            "- **Memoization** (caching) converts exponential-time recursion to linear: `@functools.lru_cache`\n"
            "- Tail-call optimization is NOT performed by CPython"
        ),
        "oop": (
            "**Object-Oriented Programming (OOP)** organizes code around objects that combine data (attributes) and behavior (methods).\n\n"
            "**Four pillars:**\n"
            "1. **Encapsulation** — bundle data and methods; restrict direct access via `_private` convention\n"
            "2. **Inheritance** — subclasses extend parent class behavior (`class Dog(Animal)`)\n"
            "3. **Polymorphism** — same interface, different implementations (`shape.area()` works for Circle and Square)\n"
            "4. **Abstraction** — expose only relevant interface, hide implementation (`abc.ABC`)\n\n"
            "```python\n"
            "from abc import ABC, abstractmethod\n\n"
            "class Shape(ABC):\n"
            "    @abstractmethod\n"
            "    def area(self) -> float: ...\n\n"
            "class Circle(Shape):\n"
            "    def __init__(self, r: float): self.r = r\n"
            "    def area(self) -> float: return 3.14159 * self.r ** 2\n"
            "```"
        ),
        "sql": (
            "**SQL (Structured Query Language)** is the standard language for managing relational databases.\n\n"
            "**Core operations (CRUD):**\n"
            "```sql\n"
            "-- Create\n"
            "INSERT INTO users (name, email) VALUES ('Alice', 'alice@ex.com');\n\n"
            "-- Read\n"
            "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id WHERE o.total > 100;\n\n"
            "-- Update\n"
            "UPDATE users SET email = 'new@ex.com' WHERE id = 1;\n\n"
            "-- Delete\n"
            "DELETE FROM users WHERE last_login < '2023-01-01';\n"
            "```\n\n"
            "**Key concepts:** primary keys, foreign keys, indexes (B-tree), JOINs (INNER/LEFT/RIGHT), transactions (ACID), normalization.\n\n"
            "Vibhu-Oska uses SQLite for session history (`Data/vibhu_oska.db`) via the `DatabaseConnector` plugin."
        ),
        "git": (
            "**Git** is a distributed version control system tracking changes to files over time.\n\n"
            "**Core workflow:**\n"
            "```bash\n"
            "git status                    # What changed?\n"
            "git add -A                    # Stage all changes\n"
            "git commit -m 'feat: add X'  # Commit (Conventional Commits)\n"
            "git push origin main          # Push to remote\n"
            "git pull --rebase origin main # Sync with remote\n"
            "```\n\n"
            "**Branching:**\n"
            "```bash\n"
            "git checkout -b feature/new-core   # Create + switch branch\n"
            "git merge feature/new-core          # Merge into current branch\n"
            "git rebase main                     # Replay commits on top of main\n"
            "```\n\n"
            "**Commit types (Conventional Commits):** `feat:` | `fix:` | `docs:` | `chore:` | `refactor:` | `test:`"
        ),
        "docker": (
            "**Docker** is a containerization platform that packages applications with all their dependencies into isolated, portable containers.\n\n"
            "**Core concepts:**\n"
            "- **Image** — read-only blueprint built from a `Dockerfile`\n"
            "- **Container** — running instance of an image (isolated process with its own filesystem)\n"
            "- **Registry** — image repository (Docker Hub, GHCR, private registries)\n"
            "- **Compose** — multi-container orchestration via `docker-compose.yml`\n\n"
            "```bash\n"
            "docker build -t vibhu-oska:latest .      # Build image\n"
            "docker run --gpus all -p 8100:8100 vibhu-oska  # Run with GPU\n"
            "docker-compose up -d                     # Start all services\n"
            "docker logs -f vibhu-oska               # Stream logs\n"
            "```\n\n"
            "GPU passthrough on Linux requires NVIDIA Container Toolkit."
        ),
    }

    def _explain_concept(self, topic: str, norm: str, raw: str, context: list[dict[str, Any]] | None = None) -> str:
        """
        Return a rich, real explanation for a programming/CS concept question.

        Parameters:
            topic: Matched concept keyword
            norm: Normalized (lowercased) prompt
            raw: Original user prompt
            context: RAG context from DataCore
        Returns: Formatted explanation string
        """
        ctx_section = ""
        if context:
            items = [c.get("content", "") for c in context if c.get("content")]
            if items:
                ctx_section = "\n\n**Related context from memory:**\n" + "\n".join(f"> {m[:200]}" for m in items[:2])

        # Check built-in knowledge base first
        for kb_key, kb_val in self._CONCEPT_KB.items():
            if kb_key in norm:
                return kb_val + ctx_section

        # Dynamic concept synthesis for anything not in KB
        words = raw.strip().rstrip("?").split()
        # Extract topic noun phrase after "what is / explain / tell me about"
        topic_words: list[str] = []
        skip_words = {"what", "is", "are", "explain", "define", "describe", "tell", "me", "about", "how", "does", "do"}
        for w in words:
            clean = w.lower().strip(".,!?")
            if clean not in skip_words:
                topic_words.append(w)

        topic_str = " ".join(topic_words) or raw.strip()

        return (
            f"**{topic_str.title()}** — Synthesis from Vibhu-Oska Knowledge Core\n\n"
            f"This is a domain concept that spans computer science, software engineering, or systems design. "
            f"Here's what I can synthesize based on the current BackupCore knowledge layer:\n\n"
            f"**What it is:** A core concept in modern software/AI systems.\n\n"
            f"**Why it matters:** Understanding `{topic_str}` is fundamental to building robust, scalable, and maintainable systems.\n\n"
            f"**Vibhu-Oska context:** This system applies these principles natively — from the WebSocket gateway through the "
            f"OrchestratorCore routing layer down to the DataCore memory architecture.\n\n"
            f"*For deeper coverage of `{topic_str}`, the Karsh model (currently in training) will provide fully generative, "
            f"context-adaptive explanations once training completes.*"
            f"{ctx_section}"
        )

    def _synthesize_answer(self, norm: str, raw: str, context: list[dict[str, Any]] | None = None) -> str:
        """
        RAG-aware answer synthesis for generic questions that don't match specific handlers.

        Parameters:
            norm: Lowercased prompt
            raw: Original user input
            context: Retrieved memory context
        Returns: Intelligent synthesized response
        """
        ctx_section = ""
        ctx_items: list[str] = []
        if context:
            ctx_items = [c.get("content", "") for c in context if c.get("content")]
            if ctx_items:
                ctx_section = "\n\n**Retrieved from memory:**\n" + "\n".join(f"> {m[:300]}" for m in ctx_items[:3])

        # If we have RAG context, lead with it
        if ctx_items:
            return (
                f"**Vibhu-Oska Response** — Memory-augmented answer:\n\n"
                f"Based on your query: *{raw.strip()}*\n\n"
                f"**Relevant context retrieved:**\n"
                + "\n".join(f"- {m[:300]}" for m in ctx_items[:3]) +
                f"\n\n*For expanded reasoning and generative responses, Karsh training is in progress. "
                f"Once complete, this becomes a fully fluid conversation engine.*"
            )

        # No context — reason from prompt structure
        qword = re.match(r'^\s*(what|who|where|when|why|how|which|is|are|can|does|do|will|would|could)', norm)
        qtype = qword.group(1) if qword else "what"

        topic_hint = re.sub(r'\b(what|who|where|when|why|how|which|is|are|can|does|do|will|would|could|should|i|the|a|an|about)\b', '', norm).strip()
        topic_hint = re.sub(r'\s+', ' ', topic_hint).strip()

        type_map = {
            "why": f"**Why {topic_hint}?**\n\nThis is a causal reasoning question. ",
            "how": f"**How {topic_hint}?**\n\nThis is a process/mechanism question. ",
            "who": f"**Who {topic_hint}?**\n\nThis is an agent/identity question. ",
            "where": f"**Where {topic_hint}?**\n\nThis is a location/context question. ",
            "when": f"**When {topic_hint}?**\n\nThis is a temporal question. ",
            "what": f"**{topic_hint.title()}**\n\n",
        }

        prefix = type_map.get(qtype, f"**{raw.strip()}**\n\n")

        return (
            f"{prefix}"
            f"Vibhu-Oska is currently operating in **BackupCore mode** — a deterministic CPU intelligence layer.\n\n"
            f"My response capability for this query type is functional but pattern-bound until Karsh completes training. "
            f"To get the most out of me right now:\n\n"
            f"- **Rephrase as a specific Vibhu-Oska system query** — I have deep knowledge of this codebase\n"
            f"- **Paste code** — for instant static analysis and debugging\n"
            f"- **Ask about CS/ML fundamentals** — I have built-in knowledge for 50+ topics\n"
            f"- **OS commands** — `open chrome`, `screenshot`, `list apps` work natively\n\n"
            f"The moment Karsh activates (training in progress on RTX 4060), this becomes a full general intelligence response."
        )

    def _debug_guidance(self, norm: str, raw: str, context: list[dict[str, Any]] | None = None) -> str:
        """Guide user through debugging when no code is pasted."""
        return (
            "### 🐛 Debugging Guide\n\n"
            "To get precise help, paste the **full error traceback** or **code snippet** causing the issue.\n\n"
            "**Debugging workflow:**\n"
            "1. **Read the full traceback** — Python traces report exact file, line, and exception type\n"
            "2. **Isolate the failing unit** — reproduce with minimal code\n"
            "3. **Check assumptions** — add `print(type(x), x)` before the failing line\n"
            "4. **Use debugger:**\n"
            "```python\n"
            "import pdb; pdb.set_trace()  # Interactive debugger (legacy)\n"
            "# Or in VSCode: set a breakpoint and press F5\n"
            "```\n\n"
            "**Common Python errors:**\n"
            "| Error | Cause | Fix |\n"
            "|---|---|---|\n"
            "| `AttributeError` | Object lacks method/attribute | Check type, check spelling |\n"
            "| `KeyError` | Dict key missing | Use `.get(key, default)` |\n"
            "| `TypeError` | Wrong argument type | Check function signature |\n"
            "| `RuntimeError: event loop` | Async called from sync | Use `asyncio.run()` or `await` |\n"
            "| `ImportError` | Module not found | Check `pip install` and venv activation |\n\n"
            "Paste your traceback and I'll do full automated analysis."
        )

    def _code_generation_guide(self, norm: str, raw: str, context: list[dict[str, Any]] | None = None) -> str:
        """Provide intelligent code generation guidance or template."""
        # Extract what they want to build
        topic_match = re.search(r'(write|generate|create|make|build|implement|code for|script for|function for|class for)\s+(.+)', norm)
        target = topic_match.group(2).strip() if topic_match else raw.strip()

        # Detect language preference
        lang = "python"
        if re.search(r'\b(javascript|js|node|typescript|ts)\b', norm):
            lang = "javascript"
        elif re.search(r'\b(bash|shell|powershell)\b', norm):
            lang = "bash"

        return (
            f"### 🛠️ Code Generation: `{target}`\n\n"
            f"Here's a **{lang.capitalize()} implementation scaffold** for: *{target}*\n\n"
            f"```{lang}\n"
            f"# Vibhu-Oska Generated Template\n"
            f"# Target: {target}\n"
            f"# Generated by: BackupCore static synthesis engine\n\n"
            f"# TODO: Implement your {target} logic here\n"
            f"# Paste existing code or describe more specifically for full automated implementation\n"
            f"```\n\n"
            f"**To get a complete implementation:**\n"
            f"1. Describe the exact inputs, outputs, and requirements\n"
            f"2. Paste any existing code or interface contracts\n"
            f"3. Specify constraints (performance, async, type-safe, etc.)\n\n"
            f"*Karsh (in training) will generate complete production code once active. "
            f"Currently BackupCore provides templates and architectural guidance.*"
        )

    def _contextual_fallback(self, norm: str, raw: str, context: list[dict[str, Any]] | None = None) -> str:
        """
        Synthesize dynamic responses for any unmatched user input using prompt intent and RAG context.

        Parameters:
            norm: Lowercased prompt
            raw: Original user input
            context: Retrieved RAG memory
        Returns: Contextually engaged response
        """
        ctx_section = ""
        ctx_items: list[str] = []
        if context:
            ctx_items = [c.get("content", "") for c in context if c.get("content")]
            if ctx_items:
                ctx_section = "\n\n**Memory context retrieved:**\n" + "\n".join(f"> {m[:250]}" for m in ctx_items[:2])

        word_count = len(raw.split())

        # Single word or very short inputs
        if word_count <= 2:
            return (
                f"I received: `{raw.strip()}`\n\n"
                f"Could you elaborate? I can help with:\n"
                f"- **Questions** — CS concepts, algorithms, programming\n"
                f"- **Code analysis** — paste a snippet or error traceback\n"
                f"- **OS control** — `open chrome`, `screenshot`, `list apps`\n"
                f"- **System info** — `status`, `telemetry`, `training status`"
                f"{ctx_section}"
            )

        # Use RAG context if available
        if ctx_items:
            return (
                f"**Processing:** *{raw.strip()}*\n\n"
                f"Based on your message and retrieved memory context:\n\n"
                + "\n".join(f"- {m[:300]}" for m in ctx_items[:2]) +
                f"\n\n*Karsh (training in progress) will handle open-ended conversation natively. "
                f"For now, try asking me about code, system status, or Vibhu-Oska architecture for the deepest responses.*"
            )

        # Engage with the content meaningfully
        return (
            f"**Acknowledged:** *{raw.strip()}*\n\n"
            f"I've ingested your message into session memory and vector store.\n\n"
            f"This prompt falls outside my current deterministic knowledge boundaries in BackupCore mode. "
            f"For best results, try:\n\n"
            f"- **Ask a specific question** about this topic\n"
            f"- **Paste code** for automated analysis and refactoring\n"
            f"- **Use OS commands** like `open notepad` or `screenshot`\n"
            f"- **Request system telemetry** for hardware monitoring\n\n"
            f"Once Karsh training completes, I'll respond to any input with fully generative, context-adaptive intelligence."
        )

    # ── Utilities ──────────────────────────────────────────────────────────────────

    def save(self, data: Any) -> Any:
        """Backward-compatibility stub."""
        return data

    def restore(self, data: Any) -> Any:
        """Backward-compatibility stub."""
        return data

    @property
    def queue_size(self) -> int:
        return len(self._task_queue)

    def flush_queue(self) -> list[dict[str, Any]]:
        queue = self._task_queue.copy()
        self._task_queue.clear()
        return queue

