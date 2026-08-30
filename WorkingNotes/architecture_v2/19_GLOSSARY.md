# Glossary of Terms

## Vibhu-Oska AI-OS

The overall operating system for the Vibhu-Oska AI assistant, encompassing all modules from foundation to frontend.

---

## Core Concepts

### Tri-Devas
The three fundamental components of Vibhu-Oska's intelligence architecture:
1. **Vibhu** - The supreme intelligence core (SARA)
2. **Oska** - The operational and execution layer
3. **AI-OS** - The operating system that unifies them

### Omni-powers
The complete set of capabilities available to the AI system, including reasoning, coding, real-world interaction, memory, and self-improvement.

### ParaCore
Parameter management system responsible for storing, retrieving, and managing all configuration parameters across the system. Handles persistence, versioning, and runtime updates.

### ParaCore Training
The process of fine-tuning and optimizing ParaCore parameters based on user feedback and system performance.

---

## Model Architecture

### SARA
The primary large language model used by Vibhu-Oska for reasoning, generation, and decision-making. Wrapped in a managed lifecycle with model swapping capability.

### MoE (Mixture of Experts)
An architecture pattern where multiple specialist models are selectively activated based on input. Used in Vibhu-Oska for routing requests to appropriate domain specialists.

### GRPO (Group Relative Policy Optimization)
A reinforcement learning technique used for fine-tuning models. More stable than PPO, used for:
- SARA domain adaptation
- Specialist parameter tuning
- Routing model training

### VRAM Budget
The allocation strategy for GPU video memory across system components:
- SARA: 60%
- CognitionCore: 20%
- Inference Buffer: 15%
- Reserve: 5%

---

## System Components

### EventBus
Publish-subscribe messaging system for inter-module communication. Supports synchronous and asynchronous event delivery with topic filtering.

### CognitionCore
The reasoning and thought processing pipeline. Handles chain-of-thought reasoning, planning, and decision decomposition.

### InferenceEngine
Batched inference scheduler that manages request queuing, batching, and GPU utilization for optimal throughput.

### TokenBudget
VRAM and token management system that prevents out-of-memory errors by tracking and limiting resource usage.

### ModelRegistry
Model lifecycle manager responsible for loading, unloading, caching, and swapping models in and out of GPU memory.

---

## Specialist System

### SpecialistBase
Abstract base class that all domain specialists must implement. Defines the interface for capability registration, request handling, and response generation.

### CapabilityRegistry
Dynamic registry that tracks which specialists have which capabilities. Enables capability-based routing without hard-coded dependencies.

### RoleAdapter
Maps user roles to appropriate specialist access levels. Controls which specialists can handle which types of requests.

### DomainRegistry
Registry of all registered specialist domains (Coding, RealWorld, etc.) with metadata and availability status.

---

## Domain Specialists

### Coding Specialists
Specialists focused on software development tasks:
- Code generation
- Code review
- Bug fixing
- Refactoring
- Testing

### RealWorld Specialists
Specialists that interact with external systems:
- Web browsing and scraping
- API integration
- File system operations
- Network requests

### Scrapers
Components that collect and parse data from external sources (websites, APIs, documentation).

---

## Response Pipeline

### FastResponder
Low-latency response system that provides quick answers for simple queries using caching and priority queuing.

### Response Cache
Storage layer for frequently requested responses, reducing latency and computational overhead.

### Priority Queue
Task scheduling system that ensures UI interactions and time-sensitive requests are processed first.

---

## Orchestration

### OrchestratorCore
Central routing system that directs incoming requests to appropriate specialists based on capability matching and MoE scoring.

### TaskRouter
Component within OrchestratorCore that implements the routing logic for request distribution.

### ValidatorChain
Sequential chain of validators that check input/output for:
- Format correctness
- Safety compliance
- Quality standards
- Policy adherence

---

## Self-Improvement

### EvolutionCore
Self-evolution system that improves system performance through:
- Feedback collection
- Parameter tuning
- Specialist performance tracking
- Periodic fine-tuning

### LearningLoop
Continuous improvement cycle that collects usage data, evaluates performance, and applies updates.

### OptimizationCore
System optimization engine that tunes parameters for performance, latency, and resource usage.

---

## Monitoring

### MonitoringCore
System health monitoring framework that tracks:
- CPU and memory usage
- GPU VRAM utilization
- Request latency
- Error rates
- Throughput

### MetricsCollector
Component that aggregates system metrics for analysis and alerting.

### AlertEngine
Proactive alerting system that notifies when thresholds are breached or anomalies detected.

---

## Data Management

### DataCore
Data storage and retrieval system managing:
- Structured data (SQLite)
- Unstructured data (files)
- Cache data (in-memory)

### BackupCore
Automated backup and restore system for system state, parameters, and user data.

### Storage Layer
Persistent storage implementation using SQLite for structured data and file system for artifacts.

---

## Automation

### AutomationCore
Workflow automation system for scheduling and executing recurring tasks.

### Workflows
Predefined sequences of operations that can be triggered by events or schedules.

---

## Frontend

### Next.js App
Modern React-based frontend providing:
- Chat interface
- System dashboard
- Configuration UI
- Real-time updates

### Flask Web App
Lightweight backend providing:
- Admin interface
- API endpoints
- Health checks
- System management

### UI Components
Shared React components used across the frontend applications.

---

## Configuration

### Constants
Global configuration values including:
- File paths
- API keys (encrypted)
- System limits
- Feature flags

### Environment Variables
Runtime configuration that varies by deployment environment.

### Config Keys
Named configuration entries stored in Constants.py and accessible via ParaCore.

---

## Communication

### Event Types
Named categories of events published through the EventBus:
- `PARAM_CHANGED` - Parameter update
- `MODEL_LOADED` - Model ready for inference
- `FAST_RESPONSE` - Cached response available
- `HEALTH_ALERT` - System health issue
- `DOMAIN_AVAILABLE` - New specialist registered

### Publish-Subscribe
Communication pattern where modules emit events without knowing who receives them, enabling loose coupling.

### Topic Filtering
EventBus capability to route events only to subscribers interested in specific event types.

---

## Testing

### Unit Tests
Tests that verify individual module functionality in isolation.

### Integration Tests
Tests that verify module interactions and data flow between components.

### End-to-End Tests
Tests that simulate complete user workflows from input to response.

### Performance Benchmarks
Tests that measure system performance metrics (latency, throughput, resource usage).

---

## Deployment

### Docker
Containerization technology used for consistent deployment across environments.

### Docker Compose
Multi-container orchestration for running all Vibhu-Oska services together.

### Health Check
Endpoints that report system status for monitoring and load balancing.

### Environment Configuration
Runtime settings that vary by deployment (development, staging, production).

---

## Agent System

### Agent A-H
Development agents responsible for specific domains:
- **A:** Foundation & ParaCore
- **B:** SARA & CognitionCore
- **C:** Specialist Framework & Coding Domains
- **D:** RealWorld Domains & FastResponder
- **E:** EvolutionCore & MonitoringCore
- **F:** OrchestratorCore & ValidationCore
- **G:** DataCore & AutomationCore
- **H:** Frontend Integration

### Status Files
Persistent files tracking agent progress, current tasks, and blockers.

### Coordination Protocol
Rules for agent communication and conflict resolution.

---

## Metrics

### Latency
Time between request submission and response delivery.

### Throughput
Number of requests processed per unit time.

### Cache Hit Rate
Percentage of requests served from cache without computation.

### Validation Pass Rate
Percentage of inputs/outputs passing validation checks.

### VRAM Utilization
Percentage of GPU video memory in use.

---

## Abbreviations

| Abbreviation | Full Term |
|--------------|-----------|
| AI-OS | Artificial Intelligence Operating System |
| VRAM | Video Random Access Memory |
| MoE | Mixture of Experts |
| GRPO | Group Relative Policy Optimization |
| PPO | Proximal Policy Optimization |
| LoRA | Low-Rank Adaptation |
| LRU | Least Recently Used |
| OOM | Out of Memory |
| E2E | End-to-End |
| API | Application Programming Interface |
| UI | User Interface |
| UX | User Experience |
| SQL | Structured Query Language |
| SQLite | Structured Query Language Lite |
| GPU | Graphics Processing Unit |
| CPU | Central Processing Unit |
| RAM | Random Access Memory |
| HTTP | HyperText Transfer Protocol |
| HTTPS | HyperText Transfer Protocol Secure |
| JSON | JavaScript Object Notation |
| YAML | YAML Ain't Markup Language |
| Markdown | Plain Text Formatting Syntax |
| CI/CD | Continuous Integration/Continuous Deployment |
| Docker | Container Platform |
| Compose | Multi-Container Orchestrator |
