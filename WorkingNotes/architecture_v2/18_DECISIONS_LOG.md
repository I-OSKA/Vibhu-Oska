# Architectural Decisions Log

## Overview

This log records all significant architectural decisions made during the Vibhu-Oska AI-OS development. Each decision includes context, rationale, alternatives considered, and outcome.

---

## Decision 001: EventBus Architecture

**Date:** 2026-08-01  
**Status:** Accepted  
**Decision Maker:** Agent A

### Context
The system requires communication between multiple independent modules (ParaCore, SaraGPT, Specialists, Frontend) without tight coupling.

### Decision
Implement a publish-subscribe EventBus pattern with synchronous and asynchronous event delivery.

### Alternatives Considered
1. **Direct function calls** - Rejected: Creates tight coupling, hard to test
2. **Message queue (RabbitMQ)** - Rejected: Overkill for single-process system
3. **Observer pattern** - Rejected: Doesn't support async well
4. **EventBus with topic filtering** - Accepted

### Rationale
- Decouples modules
- Supports async operations
- Easy to test with mock subscribers
- Low overhead for in-process communication

### Consequences
- Modules must define event types upfront
- Event ordering must be considered
- Error handling in subscribers is critical

---

## Decision 002: Specialist Architecture

**Date:** 2026-08-02  
**Status:** Accepted  
**Decision Maker:** Agent C

### Context
Need a plugin-like system for domain specialists (Coding, RealWorld, etc.) that can be registered and discovered dynamically.

### Decision
Implement SpecialistBase class with CapabilityRegistry for dynamic discovery and RoleAdapter for role-based selection.

### Alternatives Considered
1. **Hard-coded specialist routing** - Rejected: Not extensible
2. **Abstract factory pattern** - Rejected: Doesn't support discovery
3. **Plugin system with entry points** - Rejected: Too complex for Python
4. **SpecialistBase + Registry** - Accepted

### Rationale
- Dynamic registration allows adding specialists without modifying core
- CapabilityRegistry enables capability-based routing
- RoleAdapter supports role-based access control

### Consequences
- Specialists must register themselves on startup
- Registry must be thread-safe
- Capability definitions must be maintained

---

## Decision 003: SARA Model Management

**Date:** 2026-08-03  
**Status:** Accepted  
**Decision Maker:** Agent B

### Context
Multiple LLM models may be needed (SARA, backup models, specialist models) with limited VRAM.

### Decision
Implement ModelRegistry with lazy loading, TokenBudget for VRAM management, and model swapping on demand.

### Alternatives Considered
1. **Load all models at startup** - Rejected: VRAM exhaustion
2. **Single model only** - Rejected: No fallback capability
3. **ModelRegistry with LRU eviction** - Accepted
4. **Model sharding across GPUs** - Rejected: Single GPU system

### Rationale
- Lazy loading reduces startup time
- TokenBudget prevents VRAM exhaustion
- LRU eviction keeps most-used models loaded
- Model swapping provides fallback capability

### Consequences
- Model loading adds latency on first use
- Must track model usage for eviction decisions
- TokenBudget must be conservative to avoid OOM

---

## Decision 004: VRAM Budget Allocation

**Date:** 2026-08-04  
**Status:** Accepted  
**Decision Maker:** Agent A, Agent B

### Context
Limited VRAM (8GB typical) must be shared between SARA, CognitionCore, and inference buffer.

### Decision
Implement static allocation with dynamic adjustment:
- SARA: 60% (4.8GB)
- CognitionCore: 20% (1.6GB)
- Inference Buffer: 15% (1.2GB)
- Reserve: 5% (0.4GB)

### Alternatives Considered
1. **Equal split** - Rejected: SARA needs more
2. **Dynamic allocation only** - Rejected: Complex, unpredictable
3. **Static allocation with emergency reserve** - Accepted
4. **No budget, let OOM kill** - Rejected: Unacceptable

### Rationale
- Static allocation is predictable
- Emergency reserve prevents crashes
- Dynamic adjustment allows flexibility
- Monitoring can trigger rebalancing

### Consequences
- Must monitor VRAM usage continuously
- Budget may need tuning per hardware
- Inference quality may degrade under pressure

---

## Decision 005: MoE (Mixture of Experts) for Specialists

**Date:** 2026-08-05  
**Status:** Accepted  
**Decision Maker:** Agent C, Agent B

### Context
Multiple specialists may be relevant for a single request, but invoking all is wasteful.

### Decision
Implement MoE-style routing where OrchestratorCore selects top-k specialists based on relevance scoring.

### Alternatives Considered
1. **All specialists** - Rejected: Wasteful
2. **Single specialist** - Rejected: Misses expertise
3. **Rule-based routing** - Rejected: Not adaptive
4. **MoE with learned routing** - Accepted

### Rationale
- MoE is proven in LLM architectures
- Learned routing improves over time
- Top-k selection balances quality and efficiency
- Relevance scoring can use embeddings

### Consequences
- Routing model must be trained
- Cold-start problem for new specialists
- Must monitor specialist utilization

---

## Decision 006: FastResponder Architecture

**Date:** 2026-08-06  
**Status:** Accepted  
**Decision Maker:** Agent D

### Context
Some requests need sub-second responses (UI interactions, simple queries) while others can take longer (complex reasoning).

### Decision
Implement FastResponder with response caching, priority queuing, and fallback to full pipeline.

### Alternatives Considered
1. **All requests same priority** - Rejected: UI would be sluggish
2. **Separate systems for fast/slow** - Rejected: Duplication
3. **FastResponder with cache + priority** - Accepted
4. **Edge computing offload** - Rejected: Complexity

### Rationale
- Cache hit provides instant response
- Priority queuing ensures UI responsiveness
- Fallback to full pipeline for complex requests
- Single system maintains consistency

### Consequences
- Cache invalidation must be handled
- Priority inversion possible
- Cache storage grows over time

---

## Decision 007: Frontend Technology Stack

**Date:** 2026-08-07  
**Status:** Accepted  
**Decision Maker:** Agent H

### Context
Need web interface for user interaction, system monitoring, and administration.

### Decision
Implement dual frontend:
- **Next.js** for modern React-based UI
- **Flask** for lightweight admin and API

### Alternatives Considered
1. **Next.js only** - Rejected: Overkill for admin
2. **Flask only** - Rejected: Limited UI capabilities
3. **Streamlit** - Rejected: Not production-ready
4. **Dual stack (Next.js + Flask)** - Accepted

### Rationale
- Next.js provides rich UI for main interface
- Flask provides simple admin and API endpoints
- Both can share backend modules
- Incremental migration possible

### Consequences
- Two codebases to maintain
- Deployment complexity increases
- Shared API contracts needed

---

## Decision 008: EvolutionCore Learning Strategy

**Date:** 2026-08-08  
**Status:** Accepted  
**Decision Maker:** Agent E

### Context
System should improve over time through feedback and usage patterns.

### Decision
Implement EvolutionCore with:
- Feedback collection from user interactions
- Parameter tuning via gradient-free optimization
- Specialist performance tracking
- Periodic model fine-tuning

### Alternatives Considered
1. **No evolution** - Rejected: System becomes stale
2. **Online learning only** - Rejected: Unstable
3. **Batch evolution with human review** - Rejected: Slow
4. **Hybrid: online + periodic batch** - Accepted

### Rationale
- Online learning captures immediate feedback
- Periodic batch stabilizes changes
- Human review prevents dangerous drift
- Performance tracking identifies what works

### Consequences
- Must track evolution history
- Rollback capability needed
- Evaluation metrics must be defined

---

## Decision 009: ValidationCore Strategy

**Date:** 2026-08-09  
**Status:** Accepted  
**Decision Maker:** Agent F

### Context
User inputs and system outputs must be validated for safety, quality, and format.

### Decision
Implement chain-of-validators pattern with:
- Input sanitization
- Format validation
- Safety filtering
- Quality scoring

### Alternatives Considered
1. **No validation** - Rejected: Security risk
2. **Single validator** - Rejected: Monolithic
3. **Chain of validators** - Accepted
4. **ML-based validation** - Rejected: Too slow

### Rationale
- Chain allows modular validation
- Each validator can be tested independently
- Order matters (sanitize before format)
- Failed validation provides clear feedback

### Consequences
- Chain order must be maintained
- Performance impact on every request
- Validator updates require testing

---

## Decision 010: MonitoringCore Alert Strategy

**Date:** 2026-08-10  
**Status:** Accepted  
**Decision Maker:** Agent E

### Context
System health must be monitored with proactive alerts for degradation.

### Decision
Implement MonitoringCore with:
- Metric collection (CPU, VRAM, latency, errors)
- Threshold-based alerts
- Proactive health checks
- Integration with EvolutionCore for self-healing

### Alternatives Considered
1. **No monitoring** - Rejected: Blind to issues
2. **Manual monitoring** - Rejected: Not scalable
3. **Threshold alerts only** - Rejected: Reactive
4. **Proactive monitoring + self-healing** - Accepted

### Rationale
- Proactive detection prevents failures
- Self-healing reduces manual intervention
- Metrics enable performance optimization
- Alert fatigue must be managed

### Consequences
- Thresholds need tuning
- False positives must be minimized
- Self-healing must be safe

---

## Decision 011: DataCore Persistence Strategy

**Date:** 2026-08-11  
**Status:** Accepted  
**Decision Maker:** Agent G

### Context
System state, user data, and logs must be persisted.

### Decision
Implement DataCore with:
- SQLite for structured data
- File system for logs and artifacts
- In-memory cache for hot data
- Periodic backup via BackupCore

### Alternatives Considered
1. **PostgreSQL** - Rejected: Overkill for single-user
2. **MongoDB** - Rejected: Schema flexibility not needed
3. **Pure file system** - Rejected: No query capability
4. **SQLite + files + cache** - Accepted

### Rationale
- SQLite is zero-config and reliable
- File system handles unstructured data well
- Cache provides fast access
- BackupCore handles durability

### Consequences
- SQLite has concurrency limits
- File cleanup must be managed
- Cache invalidation needed

---

## Decision 012: GRPO for Model Training

**Date:** 2026-08-12  
**Status:** Accepted  
**Decision Maker:** Agent B, Agent E

### Context
SARA and specialists need fine-tuning on domain data.

### Decision
Use Group Relative Policy Optimization (GRPO) for:
- SARA domain adaptation
- Specialist parameter tuning
- Routing model training

### Alternatives Considered
1. **Full fine-tuning** - Rejected: Expensive, catastrophic forgetting
2. **LoRA only** - Rejected: Limited capacity
3. **GRPO** - Accepted
4. **PPO** - Rejected: More complex, less stable

### Rationale
- GRPO is more stable than PPO
- Group relative scoring reduces variance
- Works well with limited compute
- Can be applied to routing decisions

### Consequences
- Requires group sampling
- Hyperparameter tuning needed
- Evaluation metrics must be defined

---

## Decision 013: Agent Coordination Protocol

**Date:** 2026-08-13  
**Status:** Accepted  
**Decision Maker:** All Agents

### Context
Multiple agents work on different modules simultaneously.

### Decision
Implement coordination via:
- Status files in `.agents/.opencode-notes/`
- EventBus for real-time coordination
- Dependency graph for build order
- Conflict resolution via Agent A (foundation owner)

### Alternatives Considered
1. **No coordination** - Rejected: Chaos
2. **Central coordinator** - Rejected: Bottleneck
3. **Status files + EventBus** - Accepted
4. **Git-based coordination only** - Rejected: Too slow

### Rationale
- Status files provide persistent state
- EventBus enables real-time sync
- Dependency graph prevents conflicts
- Foundation owner resolves disputes

### Consequences
- Agents must update status regularly
- EventBus failures block coordination
- Status files must be concise

---

## Decision 014: Testing Strategy

**Date:** 2026-08-14  
**Status:** Accepted  
**Decision Maker:** All Agents

### Context
System must be reliable and maintainable.

### Decision
Implement multi-level testing:
- Unit tests for each module
- Integration tests for module interactions
- End-to-end tests for user workflows
- Performance benchmarks for critical paths

### Alternatives Considered
1. **No testing** - Rejected: Unreliable
2. **Unit tests only** - Rejected: Miss integration issues
3. **Full test pyramid** - Accepted
4. **Test-driven development only** - Rejected: Too slow

### Rationale
- Unit tests catch logic errors
- Integration tests catch interface issues
- E2E tests catch workflow issues
- Benchmarks prevent regression

### Consequences
- Test maintenance overhead
- CI/CD pipeline needed
- Mocking external dependencies required

---

## Decision 015: Deployment Architecture

**Date:** 2026-08-15  
**Status:** Accepted  
**Decision Maker:** Agent H, Agent A

### Context
System must be deployable and maintainable.

### Decision
Implement single-machine deployment with:
- Docker containerization
- Docker Compose for services
- Environment-based configuration
- Health check endpoints

### Alternatives Considered
1. **Manual deployment** - Rejected: Error-prone
2. **Kubernetes** - Rejected: Overkill
3. **Docker Compose** - Accepted
4. **Serverless** - Rejected: Not suitable

### Rationale
- Docker provides consistency
- Compose manages multi-service
- Environment config is flexible
- Health checks enable monitoring

### Consequences
- Docker knowledge required
- Image size must be managed
- Secrets handling needed

---

## Summary of Decisions

| ID | Decision | Status | Date |
|----|----------|--------|------|
| 001 | EventBus Architecture | Accepted | 2026-08-01 |
| 002 | Specialist Architecture | Accepted | 2026-08-02 |
| 003 | SARA Model Management | Accepted | 2026-08-03 |
| 004 | VRAM Budget Allocation | Accepted | 2026-08-04 |
| 005 | MoE for Specialists | Accepted | 2026-08-05 |
| 006 | FastResponder Architecture | Accepted | 2026-08-06 |
| 007 | Frontend Technology Stack | Accepted | 2026-08-07 |
| 008 | EvolutionCore Learning Strategy | Accepted | 2026-08-08 |
| 009 | ValidationCore Strategy | Accepted | 2026-08-09 |
| 010 | MonitoringCore Alert Strategy | Accepted | 2026-08-10 |
| 011 | DataCore Persistence Strategy | Accepted | 2026-08-11 |
| 012 | GRPO for Model Training | Accepted | 2026-08-12 |
| 013 | Agent Coordination Protocol | Accepted | 2026-08-13 |
| 014 | Testing Strategy | Accepted | 2026-08-14 |
| 015 | Deployment Architecture | Accepted | 2026-08-15 |
