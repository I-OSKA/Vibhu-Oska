# Vibhu-Oska AI-OS — OrchestratorCore Refactor (The Bus)

**Version**: 2.0  
**Core**: OrchestratorCore (The Bus)  
**Authority**: Level 2 — Operational Core  
**Managed By**: HybridCore (Creator)  
**Status**: Phase 0 — Documentation Complete

---

## Overview

The **OrchestratorCore** is refactored from a simple request router into **The Bus** — a sophisticated intent classifier, multi-specialist distributor, and result summator. It analyzes user needs, distributes work to appropriate specialized cores, and synthesizes responses into coherent final output.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
                            ORCHESTRATORCORE (THE BUS)                         
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    INTENT CLASSIFIER                                │   │
│  │  • Learned classifier (domain + subdomain + confidence)            │   │
│  │  • Keyword fallback for speed                                       │   │
│  │  • Multi-label: can route to MULTIPLE specialists                  │   │
│  │  • Output: Intent{domin, subdomain, confidence, requires_tools}    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│        ┌─────────────────────────────┼─────────────────────────────┐      │
│        ▼                             ▼                             ▼      │
│  ┌───────────────┐          ┌───────────────┐            ┌───────────────┐  │
│  │ CODING ROUTER │          │ REALWORLD RT  │            │ FAST RESPONDER│  │
│  │ (Sub-router)  │          │ (Sub-router)  │            │ DISPATCHER    │  │
│  │               │          │               │            │               │  │
│  │ • PythonCore  │          │ • ExcelCore   │            │ • Math        │  │
│  │ • CppCore     │          │ • WebScrape   │            │ • Time        │  │
│  │ • RustCore    │          │ • FileSystem  │            │ • Facts       │  │
│  │ • JS/TS Core  │          │ • SysAdmin    │            │ • Greetings   │  │
│  │ • GoCore      │          │ • Knowledge   │            │               │  │
│  │ • SQLCore     │          │ • Network     │            │ Bypasses full │  │
│  │ • BashCore    │          │ • DB Admin    │            │ pipeline for  │  │
│  │ • RegexCore   │          │ • Cloud       │            │ simple queries│  │
│  │               │          │ • Security    │            │               │  │
│  └───────────────┘          └───────────────┘            └───────────────┘  │
│        │                             │                             │        │
│        └─────────────────────────────┼─────────────────────────────┘        │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SPECIALIST ROUTER                                │   │
│  │  • Parallel dispatch to multiple specialists                        │   │
│  │  • Load balancing across hot specialists                            │   │
│  │  • Timeout & retry management                                       │   │
│  │  • Fallback chain: Specialist → Peer → CognitionCore → BackupCore  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    RESULT SUMMATOR                                  │   │
│  │  • Merge multiple specialist responses                              │   │
│  │  • Deduplicate overlapping content                                  │   │
│  │  • Resolve conflicts (voting, confidence weighting)                │   │
│  │  • Format unified response                                          │   │
│  │  • Citation aggregation                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    VALIDATION & FINALIZE                            │   │
│  │  • ValidationCore contract check (output)                           │   │
│  │  • Persistence to DataCore (session/memory)                         │   │
│  │  • EventBus publish: ORCHESTRATOR_SUMMATION                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. IntentClassifier (`IntentClassifier.py`)

```python
class IntentClassifier:
    """
    Classifies user intent into domain, subdomain, confidence, and metadata.
    Hybrid: Learned model + Keyword fallback.
    """
    
    DOMAINS = {
        "coding": {
            "subdomains": ["python", "cpp", "rust", "javascript", "go", "sql", "bash", "regex"],
            "keywords": ["code", "function", "class", "debug", "algorithm", "api", "library", "syntax"]
        },
        "realworld": {
            "subdomains": ["excel", "web_scraping", "filesystem", "system_admin", "knowledge", 
                          "network", "database_admin", "cloud", "security"],
            "keywords": ["excel", "spreadsheet", "scrape", "crawl", "file", "directory", "server", 
                        "docker", "kubernetes", "aws", "cloud", "security", "vpn", "firewall"]
        },
        "general": {
            "subdomains": ["chat", "reasoning", "math", "facts", "creative"],
            "keywords": ["what", "how", "why", "explain", "calculate", "define"]
        }
    }
    
    def __init__(self, config: IntentClassifierConfig):
        self.config = config
        self.learned_model = None  # Loaded on demand
        self.keyword_matcher = KeywordMatcher(self.DOMAINS)
        self.embedding_model = None  # For semantic similarity
    
    async def classify(self, prompt: str, context: List[Dict] = None) -> Intent:
        """
        Classify prompt intent.
        
        Returns:
            Intent(
                domain: str,              # "coding" | "realworld" | "general"
                subdomain: str,           # e.g., "python", "excel"
                confidence: float,        # 0.0 - 1.0
                requires_tools: bool,     # Needs tool use?
                requires_reasoning: bool, # Complex reasoning needed?
                urgency: str,             # "low" | "normal" | "high" | "critical"
                suggested_specialists: List[str],  # Ordered list
                metadata: Dict
            )
        """
        # 1. Fast keyword check (immediate, ~1ms)
        keyword_intent = self.keyword_matcher.match(prompt)
        
        # 2. If high confidence (>0.9), return early
        if keyword_intent.confidence > 0.9:
            return keyword_intent
        
        # 3. Learned model inference (slower, ~50ms)
        if self.learned_model:
            learned_intent = await self._learned_classify(prompt, context)
            
            # 4. Ensemble: combine keyword + learned
            return self._ensemble(keyword_intent, learned_intent)
        
        return keyword_intent
    
    def _ensemble(self, keyword: Intent, learned: Intent) -> Intent:
        """Combine keyword and learned predictions"""
        # Weight: learned 0.7, keyword 0.3
        # If they agree on domain, boost confidence
        # If they disagree, use learned but lower confidence
        pass
```

### 2. SpecialistRouter (`SpecialistRouter.py`)

```python
class SpecialistRouter:
    """
    Routes requests to appropriate specialists with parallel execution,
    load balancing, and fallback chains.
    """
    
    def __init__(
        self,
        specialist_registry: SpecialistRegistry,
        vram_manager: VRAMManager,
        event_bus: EventBus,
        config: SpecialistRouterConfig
    ):
        self.registry = specialist_registry
        self.vram = vram_manager
        self.event_bus = event_bus
        self.config = config
        
        # Fallback chain configuration
        self.fallback_chain = [
            "primary_specialist",      # First choice
            "peer_specialist",         # Same domain, different subdomain
            "cognition_core",          # General reasoning fallback
            "backup_core"              # Versatile backup
        ]
    
    async def route(
        self, 
        intent: Intent, 
        prompt: str, 
        context: List[Dict],
        request_id: str
    ) -> List[SpecialistResponse]:
        """
        Route to specialists based on intent.
        Returns list of responses (can be multiple for complex queries).
        """
        specialists = intent.suggested_specialists
        
        if not specialists:
            # No specific specialist → use CognitionCore
            return await self._call_cognition_core(prompt, context, request_id)
        
        # Prepare specialist requests
        tasks = []
        for spec_name in specialists:
            task = self._dispatch_to_specialist(spec_name, prompt, context, request_id)
            tasks.append(task)
        
        # Execute in parallel with timeout
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful responses
        valid_responses = [r for r in responses if isinstance(r, SpecialistResponse)]
        
        # If all failed, trigger fallback chain
        if not valid_responses:
            return await self._fallback_chain(prompt, context, request_id, intent)
        
        return valid_responses
    
    async def _dispatch_to_specialist(
        self, 
        specialist_name: str, 
        prompt: str, 
        context: List[Dict],
        request_id: str
    ) -> SpecialistResponse:
        """Dispatch single request to specialist with VRAM management"""
        
        # Ensure specialist is loaded (VRAM swap if needed)
        await self.vram.ensure_loaded(specialist_name)
        
        # Get specialist client
        specialist = self.registry.get(specialist_name)
        
        # Create request
        request = SpecialistRequest(
            request_id=request_id,
            domain=specialist.domain,
            subdomain=specialist.subdomain,
            prompt=prompt,
            context=context,
            priority=self._calculate_priority(specialist_name)
        )
        
        # Execute with timeout
        try:
            response = await asyncio.wait_for(
                specialist.execute(request),
                timeout=self.config.specialist_timeout_seconds
            )
            return response
        except asyncio.TimeoutError:
            # Try peer specialist
            peer = self._find_peer_specialist(specialist_name)
            if peer:
                return await self._dispatch_to_specialist(peer, prompt, context, request_id)
            raise
    
    async def _fallback_chain(
        self, 
        prompt: str, 
        context: List[Dict], 
        request_id: str,
        intent: Intent
    ) -> List[SpecialistResponse]:
        """Execute fallback chain when primary specialists fail"""
        
        for fallback in self.fallback_chain:
            if fallback == "primary_specialist":
                continue  # Already tried
            
            elif fallback == "peer_specialist":
                peer = self._find_peer_specialist(intent.suggested_specialists[0])
                if peer:
                    try:
                        return [await self._dispatch_to_specialist(peer, prompt, context, request_id)]
                    except:
                        continue
            
            elif fallback == "cognition_core":
                try:
                    return await self._call_cognition_core(prompt, context, request_id)
                except:
                    continue
            
            elif fallback == "backup_core":
                # Request backup from pool
                backup_id = await self._request_backup(intent.suggested_specialists[0])
                if backup_id:
                    try:
                        return await self._call_backup(backup_id, prompt, context, request_id)
                    except:
                        continue
        
        # Ultimate fallback: error response
        return [SpecialistResponse(
            content="I apologize, but I'm unable to process your request at the moment.",
            confidence=0.0,
            metadata={"error": "all_fallbacks_failed"}
        )]
```

### 3. ResultSummator (`ResultSummator.py`)

```python
class ResultSummator:
    """
    Merges multiple specialist responses into a unified, coherent final response.
    Handles: deduplication, conflict resolution, citation aggregation.
    """
    
    def __init__(self, config: SummatorConfig):
        self.config = config
        self.deduplicator = ResponseDeduplicator()
        self.conflict_resolver = ConflictResolver()
        self.formatter = ResponseFormatter()
    
    async def summate(
        self, 
        responses: List[SpecialistResponse], 
        original_prompt: str,
        intent: Intent
    ) -> SummatedResponse:
        """
        Combine multiple specialist responses.
        
        Process:
        1. Group by content type (code, explanation, facts, etc.)
        2. Deduplicate overlapping content
        3. Resolve conflicts (confidence-weighted voting)
        4. Aggregate citations
        5. Format unified response
        """
        
        if len(responses) == 1:
            return self._single_response(responses[0])
        
        # 1. Segment responses by type
        segments = self._segment_responses(responses)
        
        # 2. Deduplicate within each segment
        deduped = {}
        for seg_type, seg_responses in segments.items():
            deduped[seg_type] = self.deduplicator.deduplicate(seg_responses)
        
        # 3. Resolve conflicts across segments
        resolved = self.conflict_resolver.resolve(deduped, intent)
        
        # 4. Aggregate citations
        citations = self._aggregate_citations(responses)
        
        # 5. Format final response
        final_content = self.formatter.format(resolved, intent, citations)
        
        # 6. Compute overall confidence
        confidence = self._compute_confidence(responses, resolved)
        
        return SummatedResponse(
            content=final_content,
            confidence=confidence,
            specialist_contributions=[r.specialist_name for r in responses],
            citations=citations,
            metadata={
                "num_specialists": len(responses),
                "segments": list(resolved.keys()),
                "conflicts_resolved": self.conflict_resolver.last_conflict_count
            }
        )
    
    def _segment_responses(self, responses: List[SpecialistResponse]) -> Dict[str, List]:
        """Segment response content by type"""
        segments = defaultdict(list)
        
        for resp in responses:
            # Parse response into segments
            parsed = self._parse_response(resp.content)
            for seg_type, content in parsed.items():
                segments[seg_type].append({
                    "specialist": resp.specialist_name,
                    "content": content,
                    "confidence": resp.confidence,
                    "metadata": resp.metadata
                })
        
        return segments


class ConflictResolver:
    """
    Resolves conflicting information from multiple specialists.
    Uses confidence weighting and domain authority.
    """
    
    DOMAIN_AUTHORITY = {
        "python": {"python": 1.0, "cpp": 0.3, "javascript": 0.2},
        "excel": {"excel": 1.0, "knowledge": 0.3},
        "security": {"security": 1.0, "network": 0.5, "sysadmin": 0.5}
        # ... full matrix
    }
    
    def resolve(self, segments: Dict, intent: Intent) -> Dict:
        """Resolve conflicts within and across segments"""
        resolved = {}
        
        for seg_type, items in segments.items():
            if len(items) == 1:
                resolved[seg_type] = items[0]["content"]
                continue
            
            # Multiple items → resolve
            resolved[seg_type] = self._resolve_segment(items, intent)
        
        return resolved
    
    def _resolve_segment(self, items: List[Dict], intent: Intent) -> str:
        """Resolve single segment with multiple contributions"""
        
        # Score each contribution
        scored = []
        for item in items:
            specialist = item["specialist"]
            confidence = item["confidence"]
            
            # Domain authority bonus
            authority = self.DOMAIN_AUTHORITY.get(intent.subdomain, {}).get(specialist, 0.5)
            
            # Combined score
            score = confidence * 0.7 + authority * 0.3
            scored.append((score, item["content"], specialist))
        
        # Sort by score
        scored.sort(reverse=True, key=lambda x: x[0])
        
        # If top score significantly higher, use it
        if scored[0][0] > scored[1][0] + 0.2:
            return scored[0][1]
        
        # Otherwise, merge with attribution
        return self._merge_with_attribution(scored[:3])
```

### 4. FastResponderDispatcher (`FastResponderDispatcher.py`)

```python
class FastResponderDispatcher:
    """
    Handles lightweight queries that don't need specialist pipeline.
    Routes: math, time, facts, greetings, simple lookups.
    """
    
    FAST_PATTERNS = [
        (r"^what time", "time"),
        (r"^(hi|hello|hey)", "greeting"),
        (r"^\d+\s*[\+\-\*\/]\s*\d+", "math"),
        (r"^define\s+\w+", "definition"),
        (r"^who is\s+\w+", "fact"),
        (r"^what is\s+\w+\??$", "fact")
    ]
    
    def __init__(self, fast_responder: FastResponderCore, event_bus: EventBus):
        self.fast_responder = fast_responder
        self.event_bus = event_bus
    
    def should_use_fast_responder(self, prompt: str) -> Tuple[bool, str]:
        """Check if prompt matches fast response patterns"""
        for pattern, category in self.FAST_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                return True, category
        return False, ""
    
    async def dispatch(self, prompt: str, context: List[Dict]) -> Optional[SpecialistResponse]:
        """Execute fast response if applicable"""
        should_use, category = self.should_use_fast_responder(prompt)
        
        if not should_use:
            return None
        
        # Execute fast responder
        request = SpecialistRequest(
            request_id=f"fast_{int(time.time() * 1000)}",
            domain="utility",
            subdomain="fast_responder",
            prompt=prompt,
            context=context,
            priority="low"
        )
        
        return await self.fast_responder.execute(request)
```

---

## Request Flow (Complete)

```
┌──────────────────────────────────────────────────────────────────────────────┐
                            ORCHESTRATOR REQUEST FLOW                            
├──────────────────────────────────────────────────────────────────────────────┤
                                                                                 
  1. USER INPUT RECEIVED                                                          
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ Event: USER_INPUT(payload)                                          │  
     │ Payload: {prompt, context, session_id, user_id, metadata}          │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  2. FAST RESPONDER CHECK (Pre-filter)                                          
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ FastResponderDispatcher.should_use_fast_responder(prompt)          │  
     │ If YES → Execute fast responder → Return → DONE                    │  
     │ If NO  → Continue to intent classification                         │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  3. INTENT CLASSIFICATION                                                        
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ IntentClassifier.classify(prompt, context)                         │  
     │ Returns: Intent(domain, subdomain, confidence, specialists[])      │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  4. VALIDATION (Input)                                                           
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ ValidationCore.validate_input(prompt, intent)                      │  
     │ If FAIL → Return error response → DONE                             │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  5. SPECIALIST ROUTING                                                           
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ SpecialistRouter.route(intent, prompt, context, request_id)        │  
     │   → VRAMManager.ensure_loaded(specialists)                         │  
     │   → Parallel dispatch to specialists                               │  
     │   → Fallback chain if needed                                       │  
     │ Returns: List[SpecialistResponse]                                  │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  6. RESULT SUMMATION                                                             
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ ResultSummator.summate(responses, prompt, intent)                  │  
     │   → Segment → Deduplicate → Resolve conflicts → Format             │  
     │ Returns: SummatedResponse                                          │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  7. VALIDATION (Output)                                                          
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ ValidationCore.validate_output(summated_response)                  │  
     │ If FAIL → Log, possibly retry with different specialists           │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  8. PERSISTENCE & PUBLISH                                                        
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ DataCore.persist_session(session_id, prompt, response)             │  
     │ EventBus.publish(ORCHESTRATOR_SUMMATION, {                         │  
     │     request_id, responses[], final_response, metadata              │  
     │ })                                                                  │  
     └─────────────────────────────────────────────────────────────────────┘  
                                    │                                        
                                    ▼                                        
  9. RETURN TO USER                                                               
     ┌─────────────────────────────────────────────────────────────────────┐  
     │ Final response returned to frontend                                 │  
     └─────────────────────────────────────────────────────────────────────┘  
                                                                                 
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Configuration

```yaml
# Backend/Core/MainCore/OrchestratorCore/config.yaml
orchestrator_core:
  # Intent Classifier
  intent_classifier:
    learned_model_enabled: true
    keyword_fallback: true
    confidence_threshold: 0.7
    multi_label: true  # Can route to multiple specialists
    max_specialists_per_request: 3
  
  # Specialist Router
  specialist_router:
    parallel_execution: true
    max_parallel: 3
    specialist_timeout_seconds: 30
    retry_attempts: 1
    fallback_chain:
      - "primary_specialist"
      - "peer_specialist"
      - "cognition_core"
      - "backup_core"
  
  # Result Summator
  result_summator:
    deduplication_threshold: 0.85  # Cosine similarity
    conflict_resolution: "confidence_weighted"  # or "domain_authority"
    citation_aggregation: true
    max_response_length: 8192
  
  # Fast Responder
  fast_responder:
    enabled: true
    patterns:
      - "^what time"
      - "^(hi|hello|hey)"
      - "^\\d+\\s*[\\+\\-\\*\\/]\\s*\\d+"
      - "^define\\s+\\w+"
      - "^who is\\s+\\w+"
    max_latency_ms: 100
  
  # Validation
  validation:
    input_validation: true
    output_validation: true
    contract_strict: true
  
  # VRAM Integration
  vram:
    preload_specialists: true
    keep_hot: ["router", "fast_responder"]
    max_hot_specialists: 2
```

---

## File Structure

```
Backend/Core/MainCore/OrchestratorCore/
├── __init__.py
├── OrchestratorCore.py            # Main coordinator
├── IntentClassifier.py            # Intent classification
├── SpecialistRouter.py            # Multi-specialist dispatch
├── ResultSummator.py              # Response merging
├── FastResponderDispatcher.py     # Lightweight query handling
├── BackupCoordinator.py           # BackupCore fallback
├── TriDevasState.py               # Internal: routes to appropriate Deva
├── config.yaml
└── models/
    ├── intent_classifier.pt       # Learned intent model
    └── intent_tokenizer.json
```

---

## Integration Points

| Component | Interaction |
|-----------|-------------|
| **EventBus** | Subscribes: USER_INPUT; Publishes: ORCHESTRATOR_SUMMATION |
| **IntentClassifier** | Core classification engine |
| **SpecialistRouter** | Dispatches to specialists |
| **ResultSummator** | Merges responses |
| **FastResponderDispatcher** | Handles simple queries |
| **VRAMManager** | Ensures specialists loaded |
| **ValidationCore** | Input/output validation |
| **DataCore** | Session persistence |
| **BackupCore Pool** | Fallback via BackupCoordinator |
| **HybridCore** | Health monitoring, resource arbitration |
| **ParaCore** | Can OVERRIDE routing decisions |

---

## Events

| Event | Direction | Payload |
|-------|-----------|---------|
| `USER_INPUT` | Subscribe | `{prompt, context, session_id, user_id}` |
| `SPECIALIST_REQUEST` | Publish | `{request_id, domain, subdomain, prompt, context, priority}` |
| `SPECIALIST_RESPONSE` | Subscribe | `{request_id, domain, content, confidence, metadata}` |
| `ORCHESTRATOR_SUMMATION` | Publish | `{request_id, responses[], final_response, metadata}` |
| `FAST_RESPONDER_USED` | Publish | `{request_id, category, latency_ms}` |
| `FALLBACK_TRIGGERED` | Publish | `{request_id, fallback_level, reason}` |

---

## Metrics

```python
# Published via ORCHESTRATOR_SUMMATION and internal metrics
ORCHESTRATOR_METRICS = {
    "requests_total": int,
    "fast_responder_rate": float,        # % handled by fast responder
    "avg_specialists_per_request": float,
    "avg_latency_ms": float,
    "fallback_rate": float,              # % requiring fallback
    "fallback_by_level": Dict[str, int], # primary, peer, cognition, backup
    "summation_conflicts_resolved": int,
    "validation_failures": int,
    "intent_classification_accuracy": float,  # From feedback
    "specialist_utilization": Dict[str, float]  # Per specialist
}
```

---

## Tri-Devas Internal Routing (ParaCore Only)

```python
# Logged in ParaCore/TriDevasKnowledge.py
# "ORCHESTRATOR routed to DESTROYER (EvolutionCore) for self-improvement task"
# "ORCHESTRATOR routed to BALANCER (CognitionCore) for general reasoning"
# "ORCHESTRATOR routed to CREATOR (HybridCore) for resource arbitration"
# "ORCHESTRATOR fallback chain: python_core → cpp_core → cognition_core → backup_core_1"
```

---

*End of OrchestratorCore Refactor Documentation*
