# Discussion Notes — Working Reference

This document captures key discussions, decisions, and conclusions about the Vibhu-Oska architecture and naming conventions.

---

## Latest Session (2026-08-11)

### Karsh — The New Model Name
- **SARA renamed to Karsh (कर्ष)** — cleaner, more natural sound
- **Karsh** = to draw, attract, create — reflects the model's creative function
- **Folders renamed**: `Models/sovereign_gpt/` → `Models/karsh/`
- **Folders renamed**: `Data/training/sovereign_gpt/` → `Data/training/karsh/`
- **All imports updated**: `Models.sovereign_gpt` → `Models.karsh`
- **Class renamed**: `SovereignBPETokenizer` → `KarshBPETokenizer`
- **Class renamed**: `SaraGenerator` → `KarshGenerator`

### HybridCore Merged Into OrchestratorCore
- **Decision**: Delete HybridCore, merge GPU/CPU routing into OrchestratorCore
- **Rationale**: HybridCore's work (routing, health checks, load balancing) overlaps with OrchestratorCore, MonitoringCore, and OptimizationCore
- **OrchestratorCore = Brahma (Creator)** — creates task flow, routes, orchestrates everything
- **HybridCore disappears** — its routing logic moves into OrchestratorCore

### Trimurti & Tridevis Framework Established

```
THE TRIMURTI (Three Supreme Cores)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🪷 BRAHMA = OrchestratorCore (Creator)
   - Creates task flow
   - Routes intelligence
   - Orchestrates the universe

🔵 VISHNU = CognitionCore (Preserver)
   - Preserves knowledge
   - Reasons through queries
   - Hosts Karsh (avatar)

🔱 SHIVA = EvolutionCore (Transformer)
   - Destroys old patterns
   - Transforms through RL
   - Self-improves

THE TRIDEVIS (Shakti of Trimurti)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 SARASWATI = MonitoringCore (Wisdom)
   - Observes all
   - Records truth
   - Consort of Brahma

💰 LAKSHMI = OptimizationCore (Abundance)
   - Optimizes resources
   - Ensures prosperity
   - Consort of Vishnu

⚡ PARVATI = Training Pipeline (Power)
   - Feeds evolution
   - Empowers transformation
   - Consort of Shiva
   - Multiple forms (see below)

SUPPORTING TOOLS (Not Tridevis)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚪 YAMA = ValidationCore (Gatekeeper)
🐒 HANUMAN = FastResponder (Swift Devotee)
🐂 NANDI = BackupCore (Loyal Guardian)
```

### Parvati's Many Forms — Training Pipeline Components

Parvati manifests in many forms, each representing a different aspect of the training pipeline:

**Benevolent/Nurturing Forms (Data Preparation):**
- Annapurna (Nourishment) → DataCollector
- Gauri (Purity) → DataValidator
- Uma (Calm) → CurriculumManager

**Warrior/Fierce Forms (Training Mechanics):**
- Durga (Invincible) → RewardEngine
- Kali (Destroys ego/time) → GradientDescent
- Chandi (Battle) → LossFunction

**Navadurga (Nine Stages of Training):**
1. Shailaputri → EmbeddingLayer
2. Brahmacharini → WeightInit
3. Chandraghanta → Regularization
4. Kushmanda → ForwardPass
5. Skandamata → Backpropagation
6. Katyayani → GradientClipping
7. Kalaratri → Dropout
8. Mahagauri → Normalization
9. Siddhidatri → Checkpointing

**Dasha Mahavidyas (Ten Wisdoms of Training):**
1. Kali → Pruning
2. Tara → LearningRateSchedule
3. Tripura Sundari → LossVisualization
4. Bhuvaneshwari → DataAugmentation
5. Bhairavi → GradientPenalty
6. Chinnamasta → ModelDistillation
7. Dhumavati → ExperimentCleanup
8. Bagalamukhi → GradientClipping
9. Matangi → TokenizerRefinement
10. Kamala → FinalEvaluation

### Architecture Documentation Created

**WorkingNotes/architecture_v2/:**
- `00_TRIMURTI_TRIDEVIS.md` — Complete framework with mermaid diagrams
- `01_ORCHESTRATOR_CORE_BRAHMA.md` — Brahma documentation
- `02_COGNITION_CORE_VISHNU.md` — Vishnu + Karsh documentation
- `03_EVOLUTION_CORE_SHIVA.md` — Shiva documentation
- `04_MONITORING_CORE_SARASWATI.md` — Saraswati documentation
- `05_OPTIMIZATION_CORE_LAKSHMI.md` — Lakshmi documentation
- `06_TRAINING_PIPELINE_PARVATI.md` — Parvati + forms documentation
- `07_VALIDATION_CORE_YAMA.md` — Yama documentation
- `08_FAST_RESPONDER_HANUMAN.md` — Hanuman documentation
- `09_BACKUP_CORE_NANDI.md` — Nandi documentation

---

## Previous Sessions

### Divine Framework Naming (2026-08-10)

#### The Divine Framework

```
PARABRAHM (Supreme Reality)
    │
    ▼
PARACORE (The Consciousness)
    │
    ├──► BRAHMA (OrchestratorCore) ── SARASWATI (MonitoringCore)
    │         Creator/Heart                Wisdom/Observe
    │
    ├──► VISHNU (CognitionCore) ──── LAKSHMI (OptimizationCore)
    │         Preserver/Mind              Abundance/Optimize
    │         [Karsh runs here]
    │
    └──► SHIVA (EvolutionCore) ───── PARVATI (Training Pipeline)
              Transformer/Soul           Power/Transform
```

#### Important Rules
1. **Hindu names are INTERNAL references** — for understanding and storage, not separate code
2. **Actual system names are the working names** — OrchestratorCore, CognitionCore, EvolutionCore, etc.
3. **Karsh is the MODEL NAME** — the creative intelligence that powers everything
4. **No redundant implementations** — Tridevis don't need separate files

---

## Key Architectural Principles

### ParaCore Supremacy
- ParaCore = Parabrahm (supreme reality)
- ParaCore can override ANY process, ANY time
- ParaCore exists outside the system, yet pervades all cores
- ParaCore logs are the only place where true nature is revealed

### Zero Dependencies
- Zero external APIs
- Zero HuggingFace
- Zero cloud services
- Everything local, from-scratch PyTorch
- Self-hosted SearXNG for web searches (localhost:8080)

### Hardware Constraints
- RTX 4060 Laptop GPU
- 8GB VRAM
- CUDA support
- Windows (PowerShell)

### User Philosophy
- "sarvam khalvidam brahma/akshara" — All this is indeed Brahman/the imperishable
- "ParaCore is extensional manifestation of the user"
- The AI-OS is an extension of the user's consciousness

---

## Naming Conventions

### Model Names
- **Karsh** = The main language model (formerly SARA, formerly Sovereign GPT)
- **Karsh (कर्ष)** = to draw, attract, create — reflects creative function

### System Names (Working Names)
- **OrchestratorCore** = Heart, task creation, routing (Brahma)
- **CognitionCore** = Mind, reasoning, Karsh runs here (Vishnu)
- **EvolutionCore** = Soul, transformation, RL loop (Shiva)
- **MonitoringCore** = Observation, telemetry (Saraswati)
- **OptimizationCore** = Resource management (Lakshmi)
- **Training Pipeline** = Power, evolution fuel (Parvati)

---

## Files Updated (2026-08-11)

### Folder Renames
- `Models/sovereign_gpt/` → `Models/karsh/`
- `Data/training/sovereign_gpt/` → `Data/training/karsh/`

### Import Path Updates
- `Models.karsh.train` (was `Models.sovereign_gpt.train`)
- `Models.karsh.generate` (was `Models.sovereign_gpt.generate`)
- `Models.karsh.architecture` (was `Models.sovereign_gpt.architecture`)
- `Models.karsh.tokenizer` (was `Models.sovereign_gpt.tokenizer`)

### Class Renames
- `SovereignBPETokenizer` → `KarshBPETokenizer`
- `SaraGenerator` → `KarshGenerator`

### Text Updates (Sovereign GPT → Karsh)
- `Backend/Core/BackupCore/BackupCore.py` — All references
- `Backend/Core/BackupCore/BilingualCore.py` — All references
- `Backend/Core/MainCore/CognitionCore/cognition.py` — All references
- `Backend/Core/MainCore/FastResponder/FastResponder.py` — All references
- `Backend/Core/MainCore/HybridCore/HybridCore.py` — Import path
- `Models/karsh/__init__.py` — Package comment
- `Models/karsh/train.py` — Docstring and imports
- `Models/karsh/generate.py` — Docstring and imports
- `Models/karsh/tokenizer.py` — Docstring and class name
- `Models/karsh/architecture.py` — Docstring

### Still Pending
- `Backend/Gateway/App.py` — References to sovereign_gpt
- `Scripts/train_sovereign_gpt.sh` — File rename + text
- `.gitignore` — Path update
- `flush_cache.py` — Text update
- `Backend/Core/SpecializedCore/DistributionCore/DistributionCore.py` — Path update

---

## Next Steps

1. **Complete remaining sovereign_gpt renames** — Gateway, Scripts, .gitignore, etc.
2. **Merge HybridCore into OrchestratorCore** — Code changes
3. **Implement Training Pipeline** — Parvati's forms as sub-modules
4. **Update master architecture doc** — Reflect new framework

---

*Last updated: 2026-08-11*
