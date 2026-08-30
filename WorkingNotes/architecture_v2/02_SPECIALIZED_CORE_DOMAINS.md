# Vibhu-Oska AI-OS — Specialized Core Domains (Complete)

**Total: 20 Specialist Domains**  
**Architecture**: Each specialist = independent micro-model (10-20M params) + corpus + checkpoints + router  
**VRAM**: 2 hot-swapped at a time (~2.4 GB), rest cold-loaded (2-3s) with 4-bit quantization

---

## Coding Domain (10 Specialists)

### 1. PythonCore (~15M params)
**Corpus Target**: 5,000 Q&A pairs  
**Sources**: Python docs, stdlib, PyPI top 200, RealPython, GeeksforGeeks, Python Weekly
```
corpus/
├── basics.txt              # syntax, types, control flow, functions
├── stdlib_os_sys.txt       # os, sys, pathlib, subprocess, platform
├── stdlib_collections.txt  # itertools, collections, functools, operator
├── stdlib_data.txt         # json, csv, sqlite3, pickle, shelve, dbm
├── stdlib_concurrency.txt  # threading, multiprocessing, concurrent.futures
├── stdlib_async.txt        # asyncio, aiohttp, aiofiles, async generators
├── stdlib_network.txt      # urllib, http, socket, ssl, email
├── oop.txt                 # classes, inheritance, protocols, ABC, dataclasses
├── testing.txt             # pytest, unittest, mock, hypothesis, coverage
├── packaging.txt           # pip, poetry, pyproject.toml, wheel, setuptools
├── debugging.txt           # pdb, logging, traceback, cProfile, py-spy
├── patterns.txt            # decorators, context managers, descriptors, metaclasses
├── type_hints.txt          # typing, generics, overload, Protocol, TypedDict
├── data_science.txt        # numpy, pandas, polars, matplotlib basics
├── web_fastapi.txt         # FastAPI, Starlette, Pydantic, dependency injection
├── web_flask_django.txt    # Flask, Django, ORM, templates, auth
├── advanced.txt            # C-extensions, GIL, memoryview, __slots__, cython
└── ml_pytorch.txt          # torch, torchvision, lightning, transformers basics
```

**Capabilities**: Code gen, debugging, refactoring, explanation, test writing, performance optimization, async patterns, packaging

---

### 2. CppCore (~15M params)
**Corpus Target**: 4,000 Q&A pairs  
**Sources**: cppreference, C++ Core Guidelines, LLVM docs, Effective Modern C++, CppCon talks
```
corpus/
├── basics.txt              # syntax, types, control flow, functions
├── memory.txt              # RAII, smart pointers, allocators, custom new/delete
├── templates.txt           # templates, concepts, variadic, template metaprogramming
├── stl_containers.txt      # vector, map, unordered_map, deque, span, array
├── stl_algorithms.txt      # algorithms, ranges, views, execution policies
├── concurrency.txt         # thread, mutex, condition_variable, atomic, futures
├── coroutines.txt          # coroutines, generators, async, structured concurrency
├── modules.txt             # C++20 modules, partition, interface, implementation
├── concepts.txt            # concepts, requires, constraints, refinement
├── cmake.txt               # CMake, FetchContent, target_link_libraries, presets
├── qt.txt                  # Qt6, signals/slots, QML, model/view, networking
├── embedded.txt            # bare metal, constexpr, bit manipulation, registers
├── performance.txt         # profiling, perf, cache, SIMD, branch prediction
├── interop.txt             # C interop, Python bindings (pybind11), WASM
└── modernization.txt       # C++17/20/23 migration, deprecated patterns
```

**Capabilities**: Systems code, memory management, templates, concurrency, CMake, Qt, embedded, performance tuning

---

### 3. RustCore (~15M params)
**Corpus Target**: 4,000 Q&A pairs  
**Sources**: Rust Book, Reference, std docs, tokio, serde, clap, axum, bevy, Rustlings
```
corpus/
├── basics.txt              # syntax, ownership, borrowing, lifetimes, traits
├── memory.txt              # Box, Rc, Arc, Cell, RefCell, Pin, UnsafeCell
├── async.txt               # async/await, futures, tokio, async-std, executors
├── concurrency.txt         # channels, mutex, rwlock, atomics, crossbeam, rayon
├── error_handling.txt      # Result, Option, ?, thiserror, anyhow, eyre
├── serde.txt               # serialize, deserialize, derive, custom formats
├── cli.txt                 # clap, argparse, completions, subcommands
├── web_axum.txt            # axum, tower, hyper, middleware, extractors
├── web_actix.txt           # actix-web, actors, websockets, testing
├── database.txt            # sqlx, diesel, redis, mongodb, migrations
├── wasm.txt                # wasm-bindgen, wasm-pack, web-sys, js-sys
├── ffi.txt                 # cxx, bindgen, C interop, extern "C"
├── macros.txt              # declarative, procedural, derive, attribute
├── testing.txt             # unit, integration, property (proptest), mockall
├── performance.txt         # criterion, flamegraph, perf, SIMD, allocators
└── patterns.txt            # builder, newtype, typestate, RAII, interior mutability
```

**Capabilities**: Safe systems code, async, web, CLI, WASM, FFI, macros, performance

---

### 4. JavaScriptCore (~15M params)
**Corpus Target**: 5,000 Q&A pairs  
**Sources**: MDN, TypeScript Handbook, Node.js docs, React/Vue/Svelte docs, bundler docs
```
corpus/
├── basics.txt              # ES2024, syntax, types, control flow, modules
├── typescript.txt          # types, generics, inference, utility types, decorators
├── node_runtime.txt        # fs, path, stream, events, worker_threads, cluster
├── node_api.txt            # http, https, net, crypto, os, process, child_process
├── react_core.txt          # hooks, context, suspense, server components, RSC
├── react_advanced.txt      # performance, testing, RTL, Zustand, Jotai, TanStack
├── vue_core.txt            # composition API, reactivity, Pinia, Nuxt 3
├── svelte_core.txt         # runes, stores, actions, transitions, SvelteKit
├── bundlers.txt            # Vite, Webpack, Rollup, esbuild, Turbopack, config
├── testing.txt             # Vitest, Jest, Playwright, Cypress, MSW
├── tooling.txt             # ESLint, Prettier, TypeScript, biome, oxc
├── frameworks_next.txt     # Next.js 14+, App Router, Server Actions, Middleware
├── frameworks_remix.txt    # Remix, loaders, actions, SSR, hydration
├── state_mgmt.txt          # Redux, Zustand, Jotai, Recoil, Signals, RxJS
├── performance.txt         # Core Web Vitals, bundle analysis, lazy loading
└── wasm_js.txt             # wasm-bindgen, wasm-pack, performance, interop
```

**Capabilities**: Full-stack JS/TS, React/Vue/Svelte/Next/Remix, bundlers, testing, performance

---

### 5. GoCore (~12M params)
**Corpus Target**: 3,000 Q&A pairs  
**Sources**: Go docs, Effective Go, stdlib, gRPC, Kubernetes client-go
```
corpus/
├── basics.txt              # syntax, types, control flow, error handling
├── concurrency.txt         # goroutines, channels, select, sync, context
├── interfaces.txt          # interfaces, generics, type constraints, embedding
├── modules.txt             # go.mod, go.work, replace, vendor, versioning
├── testing.txt             # testing, testify, ginkgo, fuzzing, benchmarks
├── web_stdlib.txt          # net/http, chi, gin, echo, middleware, routing
├── grpc.txt                # protobuf, gRPC, interceptors, streaming, reflection
├── database.txt            # database/sql, GORM, sqlc, pgx, migrations
├── observability.txt       # logging, metrics (prometheus), tracing (otel)
├── deployment.txt          # Docker, build tags, cross-compile, static linking
├── wasm.txt                # GOOS=js GOARCH=wasm, syscall/js, TinyGo
├── ffi.txt                 # cgo, CGO_ENABLED, C interop, shared libraries
└── kubernetes.txt          # client-go, controller-runtime, operators, CRDs
```

**Capabilities**: Concurrent services, gRPC, Kubernetes operators, CLI tools, WASM

---

### 6. SQLCore (~10M params)
**Corpus Target**: 3,000 Q&A pairs  
**Sources**: PostgreSQL docs, SQLite docs, MySQL docs, Use The Index Luke, pgMustard
```
corpus/
├── basics.txt              # SELECT, JOIN, WHERE, GROUP BY, window functions
├── postgresql.txt          # PG-specific: CTE, lateral, JSONB, advisory locks
├── sqlite.txt              # SQLite-specific: pragma, FTS, virtual tables
├── mysql.txt               # MySQL-specific: hints, partitioning, GTID
├── optimization.txt        # EXPLAIN, indexes, statistics, vacuum, partitioning
├── advanced.txt            # recursive CTE, lateral join, materialized views
├── plpgsql.txt             # functions, triggers, procedures, transactions
├── replication.txt         # streaming, logical, synchronous, failover
├── security.txt            # RLS, grants, roles, column encryption, audit
├── orm.txt                 # SQLAlchemy, Django ORM, Prisma, Drizzle, sqlc
├── timeseries.txt          # TimescaleDB, continuous aggregates, compression
├── graph.txt               # recursive queries, pgRouting, graph algorithms
└── migration.txt           # Flyway, Liquibase, golang-migrate, versioning
```

**Capabilities**: Query optimization, schema design, advanced SQL, replication, ORM patterns

---

### 7. BashShellCore (~8M params)
**Corpus Target**: 2,000 Q&A pairs  
**Sources**: GNU Bash manual, zsh manual, fish docs, awk/sed/grep manuals, systemd docs
```
corpus/
├── bash_basics.txt         # syntax, variables, arrays, functions, expansion
├── bash_advanced.txt       # traps, coprocesses, namerefs, associative arrays
├── zsh.txt                 # zsh features, completion, globbing, hooks
├── fish.txt                # fish syntax, abbreviations, universal variables
├── awk.txt                 # patterns, actions, fields, arrays, regex
├── sed.txt                 # addresses, commands, hold space, regex
├── grep.txt                # PCRE, fixed strings, context, color, performance
├── find.txt                # predicates, actions, xargs, parallel
├── systemd.txt             # units, services, timers, sockets, journald
├── cron.txt                # crontab, systemd timers, anacron, at
├── ssh.txt                 # config, keys, agent, tunneling, multiplexing
├── tmux.txt                # sessions, windows, panes, scripting, plugins
├── package_mgmt.txt        # apt, dnf, pacman, brew, nix, flatpak
└── scripting.txt           # best practices, shellcheck, bats, CI/CD
```

**Capabilities**: Shell scripting, system admin, automation, text processing, scheduling

---

### 8. RegexCore (~8M params)
**Corpus Target**: 2,000 Q&A pairs  
**Sources**: PCRE docs, RE2 docs, regex101, regular-expressions.info, Rust regex crate
```
corpus/
├── basics.txt              # literals, classes, quantifiers, anchors, groups
├── lookaround.txt          # lookahead, lookbehind, atomic groups, possessive
├── backreference.txt       # numbered, named, recursive, subroutine calls
├── conditionals.txt        # (?(cond)yes|no), DEFINE, recursion
├── unicode.txt             # properties, scripts, blocks, grapheme clusters
├── performance.txt         # catastrophic backtracking, RE2, DFA vs NFA
├── pcre.txt                # PCRE2 features, JIT, callouts, limits
├── re2.txt                 # RE2 syntax, linear time, no backtracking
├── rust_regex.txt          # regex crate, bytes, Unicode, performance
├── python_re.txt           # re module, regex module, verbose mode
├── js_regex.txt            # RegExp, sticky, unicode, dotAll, named groups
└── practical.txt           # email, URL, IP, date, parsing, validation
```

**Capabilities**: Complex pattern matching, performance optimization, cross-language regex

---

### 9. CodingRouter (~5M params)
**Architecture**: Multi-class classifier (9 languages + "general")  
**Input**: Prompt + context → Output: language, confidence, subdomain
```
Training Data:
├── Labeled prompts from all coding corpora
├── "write a python function" → python, 0.98
├── "C++ template metaprogramming" → cpp, 0.95
├── "async await pattern" → general, 0.7 (could be python/js/rust)
└── "debug this code" → language detection from code snippet
```

**Routing Logic**: 
1. Explicit language mention → direct route
2. Code snippet analysis → language detection
3. Keyword + embedding similarity → confidence scoring
4. Below threshold → "general" → CognitionCore fallback

---

## RealWorld Domain (10 Specialists)

### 1. ExcelCore (~12M params)
**Corpus Target**: 3,000 Q&A pairs  
**Sources**: Microsoft Excel docs, ExcelJet, MrExcel, Contextures, VBA docs, Power Query M
```
corpus/
├── formulas.txt            # VLOOKUP, INDEX/MATCH, XLOOKUP, LAMBDA, LET
├── advanced_formulas.txt   # array formulas, dynamic arrays, spill ranges
├── pivot_tables.txt        # fields, calculated fields, grouping, slicers
├── power_query.txt         # M language, data transformation, folding
├── power_pivot.txt         # DAX, measures, calculated columns, time intelligence
├── charts.txt              # chart types, dynamic charts, sparklines, formatting
├── vba_basics.txt          # macros, modules, events, user forms, error handling
├── vba_advanced.txt        # classes, interfaces, WinAPI, COM, DLL calls
├── office_scripts.txt      # TypeScript for Excel Online, Power Automate
├── data_validation.txt     # rules, custom formulas, dependent dropdowns
├── conditional_fmt.txt     # rules, formulas, icon sets, data bars
├── tables.txt              # structured references, total rows, slicers
├── external_data.txt       # Power Query, ODBC, OData, web queries
├── automation.txt          # Power Automate, Office Scripts, Python in Excel
└── performance.txt         # calculation modes, volatile functions, binary
```

**Capabilities**: Formula writing, VBA, Power Query, Power Pivot, charts, automation

---

### 2. WebScrapingCore (~12M params)
**Corpus Target**: 4,000 Q&A pairs  
**Sources**: BeautifulSoup, lxml, Playwright, Selenium, Scrapy, httpx, aiohttp docs
```
corpus/
├── http_basics.txt         # requests, httpx, aiohttp, sessions, auth, cookies
├── parsing_bs4.txt         # BeautifulSoup, selectors, find/find_all, CSS, XPath
├── parsing_lxml.txt        # lxml, XPath, CSSSelect, iterparse, performance
├── playwright.txt          # browser automation, selectors, waiting, network
├── selenium.txt            # WebDriver, waits, actions, grid, headless
├── scrapy.txt              # spiders, pipelines, middleware, settings, contracts
├── selectors.css           # CSS selectors, pseudo-classes, combinators
├── selectors.xpath         # XPath 1.0/2.0, axes, functions, optimization
├── anti_bot.txt            # headers, rotation, proxies, CAPTCHA, fingerprinting
├── rate_limiting.txt       # semaphores, token bucket, retry, backoff
├── robots_txt.txt          # parsing, crawl-delay, sitemaps, politeness
├── dynamic_content.txt     # SPA, infinite scroll, shadow DOM, WASM
├── data_extraction.txt     # tables, lists, forms, pagination, infinite scroll
├── storage.txt             # JSON, CSV, SQLite, Parquet, incremental
├── monitoring.txt          # logging, metrics, alerting, dashboards
└── legal_ethics.txt        # ToS, robots.txt, GDPR, rate limits, attribution
```

**Capabilities**: Static/dynamic scraping, selector engineering, anti-bot, scaling, legal compliance

---

### 3. FileSystemCore (~10M params)
**Corpus Target**: 3,000 Q&A pairs  
**Sources**: Python pathlib/os/shutil, watchdog, inotify, rsync, rclone docs
```
corpus/
├── pathlib.txt             # Path, PurePath, glob, rglob, resolve, relative_to
├── os_shutil.txt           # walk, scandir, copy, move, remove, copytree
├── permissions.txt         # chmod, chown, ACLs, umask, stat, access
├── symlinks.txt            # symlink, readlink, realpath, junction, reparse
├── archives.txt            # tar, gzip, zip, 7z, rar, compression levels
├── watching.txt            # watchdog, inotify, kqueue, FSEvents, recursive
├── sync.txt                # rsync, rclone, robocopy, delta sync, filters
├── large_files.txt         # memory-map, streaming, chunked, sparse files
├── cross_platform.txt      # Windows/Unix paths, case sensitivity, line endings
├── cleanup.txt             # temp files, deduplication, empty dirs, age-based
├── search.txt              # grep, ripgrep, fd, locate, indexed search
├── atomic.txt              # write+rename, flock, fcntl, transactional
└── forensic.txt            # timestamps, metadata, alternate data streams
```

**Capabilities**: Advanced FS ops, sync, watching, permissions, cross-platform, forensics

---

### 4. SystemAdminCore (~12M params)
**Corpus Target**: 4,000 Q&A pairs  
**Sources**: systemd, Docker, Kubernetes, Linux man pages, networking, firewall docs
```
corpus/
├── systemd.txt             # units, services, timers, sockets, drop-ins, journalctl
├── docker.txt              # images, containers, compose, networks, volumes, buildkit
├── kubernetes_basics.txt   # pods, services, deployments, configmaps, secrets
├── kubernetes_advanced.txt # operators, CRDs, helm, kustomize, admission webhooks
├── networking.txt          # ip, ss, netstat, iptables, nftables, wireguard
├── firewall.txt            # ufw, firewalld, iptables, nftables, rulesets
├── ssh.txt                 # config, keys, agent, tunneling, multiplexing, CA
├── logging.txt             # journald, rsyslog, logrotate, structured logging
├── monitoring.txt          # prometheus, node_exporter, alerting, grafana
├── package_mgmt.txt        # apt, dnf, pacman, rpm, dpkg, repositories
├── users_groups.txt        # useradd, usermod, sudo, PAM, LDAP, SSO
├── storage.txt             # LVM, ZFS, btrfs, RAID, mount, fstab, quotas
├── kernel.txt              # sysctl, modules, parameters, /proc, /sys
├── hardening.txt           # CIS, Lynis, auditd, SELinux, AppArmor
└── cloud_init.txt          # cloud-init, ignition, user-data, metadata
```

**Capabilities**: Linux admin, containerization, K8s, networking, security, monitoring

---

### 5. KnowledgeCore (~15M params)
**Corpus Target**: 5,000 Q&A pairs  
**Sources**: Wikipedia, Britannica, science/math sites, philosophy, reasoning benchmarks
```
corpus/
├── science_physics.txt     # mechanics, thermodynamics, quantum, relativity
├── science_chemistry.txt   # periodic table, reactions, organic, inorganic
├── science_biology.txt     # cell, genetics, evolution, ecology, anatomy
├── math_basics.txt         # algebra, calculus, linear algebra, statistics
├── math_advanced.txt       # topology, analysis, number theory, category theory
├── computer_science.txt    # algorithms, complexity, automata, compilers, crypto
├── history.txt             # world history, timelines, civilizations, wars
├── geography.txt           # countries, capitals, coordinates, climate, GIS
├── philosophy.txt          # ethics, epistemology, metaphysics, logic, philosophers
├── logic_reasoning.txt     # propositional, predicate, modal, proof systems
├── linguistics.txt         # phonology, syntax, semantics, typology, NLP
├── economics.txt           # micro, macro, game theory, behavioral, finance
├── psychology.txt          # cognitive, behavioral, developmental, social
├── general_facts.txt       # trivia, records, measurements, constants
└── critical_thinking.txt   # fallacies, biases, argument analysis, evidence
```

**Capabilities**: General QA, reasoning, fact retrieval, cross-domain synthesis

---

### 6. NetworkCore (~12M params)
**Corpus Target**: 3,000 Q&A pairs  
**Sources**: RFCs, HTTP/2/3 specs, gRPC, GraphQL, DNS, TLS, load balancer docs
```
corpus/
├── http_1.txt              # HTTP/1.1, headers, methods, status, chunked
├── http_2.txt              # frames, streams, multiplexing, server push, HPACK
├── http_3.txt              # QUIC, streams, 0-RTT, connection migration
├── websocket.txt           # frames, masking, ping/pong, extensions, compression
├── grpc.txt                # protobuf, unary/streaming, interceptors, reflection
├── graphql.txt             # schema, queries, mutations, subscriptions, federation
├── rest_api.txt            # design, versioning, pagination, filtering, HATEOAS
├── dns.txt                 # records, resolution, DNSSEC, DoH, DoT, EDNS
├── tls.txt                 # certificates, chains, OCSP, stapling, mTLS, ACME
├── load_balancing.txt      # L4/L7, algorithms, health checks, sticky sessions
├── api_gateway.txt         # Kong, Traefik, Envoy, rate limiting, auth
├── service_mesh.txt        # Istio, Linkerd, sidecar, mTLS, traffic splitting
├── websockets_scale.txt    # pub/sub, presence, rooms, sharding, Redis adapter
└── performance.txt         # latency, throughput, connection pooling, keepalive
```

**Capabilities**: Protocol design, debugging, optimization, security, scaling

---

### 7. DatabaseAdminCore (~12M params)
**Corpus Target**: 3,000 Q&A pairs  
**Sources**: PostgreSQL admin, MySQL admin, Redis, MongoDB, Cassandra docs
```
corpus/
├── postgresql_admin.txt    # config, vacuum, analyze, replication, backup, PITR
├── mysql_admin.txt         # InnoDB, replication, GTID, backup, performance schema
├── redis.txt               # data structures, persistence, clustering, Lua scripts
├── mongodb.txt             # replica sets, sharding, aggregation, indexes, TTL
├── cassandra.txt           # data modeling, compaction, repair, hints, LWT
├── backup_recovery.txt     # pg_basebackup, pg_dump, Percona XtraBackup, WAL-G
├── replication.txt         # streaming, logical, synchronous, cascade, failover
├── partitioning.txt        # range, list, hash, native, declarative, pg_partman
├── vacuum.txt              # autovacuum, wraparound, freeze, index cleanup
├── connection_pooling.txt  # PgBouncer, PgPool, Odyssey, transaction vs session
├── extensions.txt          # PostGIS, TimescaleDB, Citus, pgvector, pg_cron
├── security.txt            # RLS, SSL, roles, grants, audit, pgaudit
├── monitoring.txt          # pg_stat_statements, pg_stat_monitor, explain.depesz
└── migration.txt           # zero-downtime, pgloader, logical replication, CDC
```

**Capabilities**: DB administration, replication, backup, partitioning, extensions, security

---

### 8. CloudCore (~12M params)
**Corpus Target**: 3,000 Q&A pairs  
**Sources**: AWS, GCP, Azure docs, Terraform, Ansible, Pulumi, Crossplane
```
corpus/
├── aws_core.txt            # EC2, S3, IAM, VPC, Lambda, CloudFormation, CDK
├── aws_advanced.txt        # ECS/EKS, RDS, DynamoDB, SQS/SNS, EventBridge
├── gcp_core.txt            # Compute, Storage, IAM, VPC, Cloud Run, Cloud Functions
├── gcp_advanced.txt        # GKE, Cloud SQL, Firestore, Pub/Sub, Dataflow
├── azure_core.txt          # VM, Storage, AD, VNet, Functions, Bicep, ARM
├── terraform.txt           # providers, modules, state, workspaces, testing
├── ansible.txt             # playbooks, roles, collections, inventory, vault
├── pulumi.txt              # TypeScript/Python/Go, stacks, providers, automation
├── crossplane.txt          # managed resources, compositions, providers, claims
├── serverless.txt          # Lambda, Cloud Run, Functions, event-driven, cold start
├── containers.txt          # ECS, EKS, GKE, AKS, Fargate, Cloud Run, Knative
├── observability.txt       # CloudWatch, Cloud Monitoring, Azure Monitor, logging
├── security.txt            # IAM policies, SCPs, KMS, Secrets Manager, GuardDuty
├── cost_optimization.txt   # rightsizing, savings plans, spot, FinOps, tagging
└── multi_cloud.txt         # patterns, challenges, tools, governance, identity
```

**Capabilities**: Cloud architecture, IaC, serverless, containers, security, cost optimization

---

### 9. SecurityCore (~12M params)
**Corpus Target**: 3,000 Q&A pairs  
**Sources**: OWASP, NIST, JWT, OAuth2, RBAC, crypto, pen testing, CTF writeups
```
corpus/
├── owasp_top10.txt         # injection, broken auth, sensitive data, XXE, etc.
├── authentication.txt      # JWT, OAuth2, OIDC, SAML, WebAuthn, passkeys, MFA
├── authorization.txt       # RBAC, ABAC, ReBAC, Casbin, OPA, policy as code
├── cryptography.txt        # AES, ChaCha20, RSA, ECC, Ed25519, TLS, PKI
├── hashing.txt             # bcrypt, Argon2, scrypt, PBKDF2, Blake3, salts
├── certificates.txt        # X.509, ACME, Let's Encrypt, mTLS, certificate pinning
├── network_security.txt    # firewalls, IDS/IPS, WAF, DDoS, zero trust, SASE
├── app_security.txt        # SAST, DAST, SCA, secrets scanning, SBOM, supply chain
├── pen_testing.txt         # recon, enumeration, exploitation, post-exploit, reporting
├── incident_response.txt   # detection, containment, eradication, recovery, lessons
├── compliance.txt          # SOC2, ISO27001, GDPR, HIPAA, PCI-DSS, FedRAMP
├── threat_modeling.txt     # STRIDE, PASTA, attack trees, DFD, mitigations
├── secrets_mgmt.txt        # Vault, AWS Secrets Manager, Doppler, 1Password, SOPS
└── secure_coding.txt       # input validation, output encoding, least privilege
```

**Capabilities**: Threat modeling, secure architecture, crypto, compliance, incident response

---

### 10. RealWorldRouter (~5M params)
**Architecture**: Multi-class classifier (10 domains + "general")  
**Input**: Prompt + context → Output: domain, confidence, urgency
```
Training Data:
├── Labeled prompts from all realworld corpora
├── "Excel formula for VLOOKUP" → excel, 0.99
├── "scrape product prices" → web_scraping, 0.97
├── "systemd service not starting" → system_admin, 0.95
├── "Kubernetes pod crashing" → cloud, 0.9
└── "how does TLS work" → security, 0.85 (could be network)
```

---

## Existing Specialized Cores (Moved to SpecializedCore/)

### DataCore (KEPT)
- ChromaDB vector store (semantic memory)
- SQLite relational (sessions, telemetry, KG)
- GraphRAG (1-hop entity traversal)
- Corpus: Internal — no external training needed

### AutomationCore (KEPT, MOVED)
- OS executive: subprocess, filesystem, telemetry, process mgmt
- Safety: command blacklist, output limits, timeout
- Corpus: Internal — no external training needed

### DesignCore (KEPT)
- HTML/CSS generation: 8 layouts, dark-mode glassmorphism
- Component library: cards, modals, tables, nav, stats
- Corpus: Internal templates

### ImageGenerationCore (KEPT)
- Local diffusion pipeline (SDXL/Flux distilled)
- Text-to-image, img2img, inpainting
- Corpus: Internal — model weights only

### VoiceCore (KEPT)
- STT: Whisper.cpp / Vosk
- TTS: Piper / Coqui
- Gesture: MediaPipe Hands
- Corpus: Internal — model weights only

### DistributionCore (KEPT)
- Stubvi compiler (asymmetric out-of-tree)
- PII scrubbing, SHA256 manifests, whitelist-only
- Corpus: Internal — no external training needed

### FastResponderCore (NEW)
- ~5M params, lightweight
- Handles: math, time, facts, greetings, simple queries
- Corpus: 2,000 Q&A pairs (generated from existing corpus patterns)
- Always hot in VRAM (~0.4 GB)

---

## Specialist Interface Contract

```python
# Backend/Core/SpecializedCore/__init__.py

class SpecialistBase(ABC):
    """All specialists MUST implement this interface."""
    
    # Static metadata (loaded at registry time)
    domain: str                    # "coding" | "realworld" | "existing"
    subdomain: str                 # "python" | "excel" | "data"
    model_params: int              # e.g., 15_000_000
    vram_mb_fp16: int              # e.g., 1200
    capabilities: List[str]        # ["code_gen", "debugging", "explanation"]
    corpus_size: int               # Q&A pairs
    checkpoint_path: Path
    tokenizer_path: Path
    
    @abstractmethod
    async def initialize(self) -> None:
        """Load model, tokenizer, warm up. Called once at startup."""
    
    @abstractmethod
    async def execute(self, prompt: str, context: List[Dict], **kwargs) -> SpecialistResponse:
        """Process request. Returns structured response."""
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Quick inference test. Returns True if healthy."""
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Cleanup: offload to CPU, release VRAM."""
    
    @abstractmethod
    def get_capabilities(self) -> SpecialistCapabilities:
        """Return static capability manifest."""

class SpecialistResponse:
    content: str
    confidence: float              # 0.0-1.0
    metadata: Dict                 # tokens, latency, model_info
    tool_calls: List[ToolCall]     # Optional tool invocations
    citations: List[Citation]      # For knowledge domains

class SpecialistCapabilities:
    domain: str
    subdomain: str
    model_params: int
    vram_mb_fp16: int
    supports_streaming: bool
    supports_tools: bool
    max_context_tokens: int
    supported_languages: List[str]  # For coding domains
```

---

## VRAM Allocation per Specialist

| Specialist | Params | VRAM (fp16) | VRAM (4-bit) | Load Time |
|------------|--------|-------------|--------------|-----------|
| PythonCore | 15M | 1.2 GB | 300 MB | 2.5s |
| CppCore | 15M | 1.2 GB | 300 MB | 2.5s |
| RustCore | 15M | 1.2 GB | 300 MB | 2.5s |
| JavaScriptCore | 15M | 1.2 GB | 300 MB | 2.5s |
| GoCore | 12M | 1.0 GB | 250 MB | 2.0s |
| SQLCore | 10M | 0.8 GB | 200 MB | 1.5s |
| BashShellCore | 8M | 0.6 GB | 150 MB | 1.0s |
| RegexCore | 8M | 0.6 GB | 150 MB | 1.0s |
| CodingRouter | 5M | 0.4 GB | 100 MB | 0.5s |
| ExcelCore | 12M | 1.0 GB | 250 MB | 2.0s |
| WebScrapingCore | 12M | 1.0 GB | 250 MB | 2.0s |
| FileSystemCore | 10M | 0.8 GB | 200 MB | 1.5s |
| SystemAdminCore | 12M | 1.0 GB | 250 MB | 2.0s |
| KnowledgeCore | 15M | 1.2 GB | 300 MB | 2.5s |
| NetworkCore | 12M | 1.0 GB | 250 MB | 2.0s |
| DatabaseAdminCore | 12M | 1.0 GB | 250 MB | 2.0s |
| CloudCore | 12M | 1.0 GB | 250 MB | 2.0s |
| SecurityCore | 12M | 1.0 GB | 250 MB | 2.0s |
| RealWorldRouter | 5M | 0.4 GB | 100 MB | 0.5s |
| FastResponderCore | 5M | 0.4 GB | 100 MB | 0.5s |

**Hot Slots**: 2 (swapped by VRAMManager)  
**Warm**: Router models + FastResponder + BackupCore pool  
**Cold**: All others (4-bit quantized in CPU RAM)

---

## Training Data Generation Pipeline

```python
# Scripts/generate_specialist_corpus.py

async def generate_specialist_corpus(domain: str, subdomain: str, target_pairs: int):
    """
    1. Seed: Manual curation (200 high-quality pairs per domain)
    2. Expand: Use CognitionCore (SARA) to generate variations
    3. Validate: Human review queue for quality
    4. Format: Query/Response pairs with code blocks preserved
    5. Split: 90% train / 10% val
    6. Repeat: 3x for tokenizer training
    """
    # Example for PythonCore:
    # - Seed: 200 manual pairs covering all corpus categories
    # - Generate: 4,800 synthetic via CognitionCore
    # - Review: 1,000 random sample human-verified
    # - Final: 5,000 pairs × 3 = 15,000 sequences for tokenizer
```

---

## Specialist Registry (Auto-Discovery)

```python
# Backend/Core/SpecializedCore/__init__.py

SPECIALIST_REGISTRY = {
    # Coding
    "python": {"class": "PythonCore", "domain": "coding", "router": "CodingRouter"},
    "cpp": {"class": "CppCore", "domain": "coding", "router": "CodingRouter"},
    "rust": {"class": "RustCore", "domain": "coding", "router": "CodingRouter"},
    "javascript": {"class": "JavaScriptCore", "domain": "coding", "router": "CodingRouter"},
    "go": {"class": "GoCore", "domain": "coding", "router": "CodingRouter"},
    "sql": {"class": "SQLCore", "domain": "coding", "router": "CodingRouter"},
    "bash": {"class": "BashShellCore", "domain": "coding", "router": "CodingRouter"},
    "regex": {"class": "RegexCore", "domain": "coding", "router": "CodingRouter"},
    
    # RealWorld
    "excel": {"class": "ExcelCore", "domain": "realworld", "router": "RealWorldRouter"},
    "web_scraping": {"class": "WebScrapingCore", "domain": "realworld", "router": "RealWorldRouter"},
    "filesystem": {"class": "FileSystemCore", "domain": "realworld", "router": "RealWorldRouter"},
    "system_admin": {"class": "SystemAdminCore", "domain": "realworld", "router": "RealWorldRouter"},
    "knowledge": {"class": "KnowledgeCore", "domain": "realworld", "router": "RealWorldRouter"},
    "network": {"class": "NetworkCore", "domain": "realworld", "router": "RealWorldRouter"},
    "database_admin": {"class": "DatabaseAdminCore", "domain": "realworld", "router": "RealWorldRouter"},
    "cloud": {"class": "CloudCore", "domain": "realworld", "router": "RealWorldRouter"},
    "security": {"class": "SecurityCore", "domain": "realworld", "router": "RealWorldRouter"},
    
    # Existing (no router needed)
    "data": {"class": "DataCore", "domain": "existing"},
    "automation": {"class": "AutomationCore", "domain": "existing"},
    "design": {"class": "DesignCore", "domain": "existing"},
    "image": {"class": "ImageGenerationCore", "domain": "existing"},
    "voice": {"class": "VoiceCore", "domain": "existing"},
    "distribution": {"class": "DistributionCore", "domain": "existing"},
    "fast_responder": {"class": "FastResponderCore", "domain": "existing"},
}
```

---

**End of Specialized Core Domains Document**
