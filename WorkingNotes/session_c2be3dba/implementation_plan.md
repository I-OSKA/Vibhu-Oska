# Vibhu-Oska AI-OS — Phase 3 Implementation Plan

> **Session**: July 29, 2026 | **Author**: Antigravity  
> **Baseline**: `vibhu_oska_project_proposal.md` + `GEMINI.md` Section 3 + AGENT_STATE_CACHE.md  
> **Current state**: 24/24 beta prompts OK · BackupCore intelligence live · Latency ~300ms (fast path)

---

## Context: Where We Are vs. Where We Need to Go

The core chat intelligence is now working. The system responds correctly to 24+ query types in under 300ms (BackupCore fast path). 

**The gap**: Vibhu-Oska is architected as an **AI-OS**, not a chatbot. Per the proposal §2.5 and GEMINI.md §3.9, it must be able to:

1. **Open and control apps on the device** — bare-metal OS execution
2. **Accept voice commands** — audio stream → intent → action
3. **Understand Hindi and English** — bilingual NLP from scratch
4. **See the screen** — vision pipeline for context-aware automation
5. **Train on a richer corpus** — domain knowledge + bilingual pairs

This plan builds those four capability pillars in sequence.

---

## What Needs to Be Built (This Session)

### Pillar 1 — App Control Layer (`AutomationCore` upgrade)

**Current state**: `AutomationCore.py` exists and can run subprocesses, read telemetry, and list processes. It cannot open apps by name, control windows, click UI elements, or interact with running programs.

**Target**: AI can receive `"open chrome"`, `"close spotify"`, `"switch to vscode"`, `"take screenshot"`, `"type [text] in notepad"` and execute them.

**Files to build/modify**:
- `Backend/Core/SpecializedCore/AutomationCore/AutomationCore.py` — add `AppController` class with:
  - `open_app(name)` — fuzzy-match app name → launch via `subprocess` / `os.startfile`
  - `close_app(name)` — `psutil` process termination
  - `list_open_apps()` — enumerate running windows
  - `switch_to_app(name)` — bring window to foreground via `pygetwindow`
  - `take_screenshot()` — PIL screenshot → base64 → return to UI
  - `type_text(text)` — `pyautogui` keyboard injection
  - `press_key(key)` — hotkey execution
- `Backend/Gateway/App.py` — wire new OS commands into `_route_to_specialized_core()`
- `BackupCore.py` — add OS command intent detection + response routing

**Dependencies (all local, no cloud)**:
- `pygetwindow` — window enumeration/focus (already in most Windows Python setups)
- `pyautogui` — keyboard/mouse automation (local, no cloud)
- `Pillow` — screenshots (already installed for ImageGenerationCore)
- `psutil` — already in requirements

---

### Pillar 2 — Bilingual NLP: Hindi + English

**Current state**: BackupCore is entirely English. No Hindi understanding or generation.

**Target**: AI understands Hindi input (Devanagari + Hinglish romanized), maps to internal intent, responds in the language the user used.

**Files to build**:
- `Backend/Core/BackupCore/BilingualCore.py` — new module:
  - `detect_language(text)` → `"en"` / `"hi"` / `"hinglish"`
  - `normalize_hindi(text)` — Devanagari → internal token form
  - `translate_intent_hi(norm)` → English intent key (rule-based, no cloud)
  - Hindi response templates for all 20+ BackupCore categories
  - Hinglish (Hindi written in Roman script) pattern matching
- `Backend/Core/BackupCore/BackupCore.py` — route to BilingualCore before English dispatch
- `Models/sara/train.py` — add Hindi Q&A pairs to corpus (~200 pairs to start)

**Hindi coverage (Phase 3)**:
- Greetings: `"namaste"`, `"kya haal hai"`, `"tum kaun ho"`, `"kya kar sakte ho"`
- Math: `"256 ka vargmool kya hai"`, `"10 ka 2 ghaat"`
- Status: `"system ka status kya hai"`, `"RAM kitni use ho rahi hai"`
- OS commands: `"chrome kholo"`, `"screenshot lo"`, `"spotify band karo"`
- Time: `"abhi kitne baje hain"`
- Identity: `"tumhara naam kya hai"`, `"tumhe kisne banaya"`

---

### Pillar 3 — Voice Command Daemon

**Current state**: Web Speech API is wired in the frontend JS but untested. No backend voice processing pipeline exists.

**Target**: Continuous microphone listening → wake-word detection → transcription → intent routing → execution → spoken response.

**Files to build**:
- `Backend/Core/SpecializedCore/VoiceCore/VoiceCore.py` — new module:
  - `WakeWordDetector` — listens continuously, fires on "Hey Vibhu" or "Oska"
  - `AudioTranscriber` — `whisper.cpp`-compatible model OR custom lightweight STT
  - `LanguageClassifier` — detect Hindi vs English from audio features
  - `VoiceResponseEngine` — TTS: pyttsx3 (local) with custom voice profile
  - WebSocket endpoint `/ws/voice` for real-time audio stream ingestion
- `Backend/Core/SpecializedCore/VoiceCore/__init__.py`
- `Frontend/web_app/templates/index.html` — enhance voice UI with visual waveform
- `Backend/Gateway/App.py` — register `/ws/voice` endpoint

**Note**: Wake-word and transcription use `sounddevice` + `scipy` for raw audio capture. No cloud STT. For Phase 3, we use `pyttsx3` for TTS (local, no cloud). The custom neural TTS engine from the proposal is a Phase 4+ item.

---

### Pillar 4 — Training Corpus Expansion (English + Hindi)

**Current state**: 300+ English Q&A pairs in `Models/sara/train.py`.

**Target**: 1200+ pairs including:
- 800+ English domain pairs (Vibhu-Oska architecture, Python, AI concepts, OS)
- 200+ Hindi pairs (bilingual coverage for all BackupCore categories)
- 100+ OS command pairs (`"open chrome" → "Opening Chrome..."`)
- 100+ conversational pairs (natural dialogue flows)

**Files to modify**:
- `Models/sara/train.py` — `CORPUS_QA` list expansion
- `Data/training/sara/corpus.txt` — persistent corpus file

---

## Proposed Changes

### Component: AutomationCore (App Control)

#### [MODIFY] [AutomationCore.py](file:///c:/Users/USER/Desktop/Extras/i-oska/Vibhu-Oska/Backend/Core/SpecializedCore/AutomationCore/AutomationCore.py)
Add `AppController` class with open/close/switch/screenshot/type/keypress operations. Wire into the OS execution router in `App.py`.

#### [MODIFY] [App.py](file:///c:/Users/USER/Desktop/Extras/i-oska/Vibhu-Oska/Backend/Gateway/App.py)
Extend `_route_to_specialized_core()` to detect app-control intents: `open [app]`, `close [app]`, `screenshot`, `type [text]`, `press [key]`.

---

### Component: Bilingual NLP

#### [NEW] [BilingualCore.py](file:///c:/Users/USER/Desktop/Extras/i-oska/Vibhu-Oska/Backend/Core/BackupCore/BilingualCore.py)
Language detection, Hindi normalization, intent mapping, Hindi response templates.

#### [MODIFY] [BackupCore.py](file:///c:/Users/USER/Desktop/Extras/i-oska/Vibhu-Oska/Backend/Core/BackupCore/BackupCore.py)
Route to BilingualCore at the top of `_reason()` before English dispatch.

---

### Component: VoiceCore

#### [NEW] `Backend/Core/SpecializedCore/VoiceCore/VoiceCore.py`
Wake-word detection, audio transcription, TTS response engine, WebSocket audio stream handler.

#### [NEW] `Backend/Core/SpecializedCore/VoiceCore/__init__.py`

#### [MODIFY] [App.py](file:///c:/Users/USER/Desktop/Extras/i-oska/Vibhu-Oska/Backend/Gateway/App.py)
Register `/ws/voice` endpoint. Initialize VoiceCore in lifespan.

#### [MODIFY] [index.html](file:///c:/Users/USER/Desktop/Extras/i-oska/Vibhu-Oska/Frontend/web_app/templates/index.html)
Add voice waveform visualizer and Hindi/English language toggle.

---

### Component: Training Corpus

#### [MODIFY] [train.py](file:///c:/Users/USER/Desktop/Extras/i-oska/Vibhu-Oska/Models/sara/train.py)
Expand `CORPUS_QA` to 1200+ pairs covering English + Hindi + OS commands + conversational flows.

---

## Open Questions

> [!IMPORTANT]
> **Voice input method**: The frontend already has Web Speech API (browser-based, routes to Google's STT). For true zero-cloud compliance, we need a local STT model. Options:
> 1. **`vosk`** — lightweight offline STT, supports Hindi + English, ~50MB model
> 2. **`whisper` (OpenAI)** — but run locally via `whisper` package (no API call, weights stored locally)  
>
> **My recommendation**: Use `vosk` with the `vosk-model-small-en-us` + `vosk-model-small-hi` local model files. Weights stay on-disk, no cloud call. Confirm?

> [!IMPORTANT]
> **TTS (voice responses)**: Current plan uses `pyttsx3` (Windows SAPI, completely local). But the proposal calls for a "custom neural voice synthesizer from scratch." For Phase 3, use `pyttsx3` as an immediate working solution, then build the custom TTS in Phase 4. Confirm this phasing?

> [!NOTE]
> **App control scope**: `pyautogui` gives us full keyboard/mouse automation but can be intrusive. Initial scope is: open, close, switch, screenshot, type. Full GUI automation (clicking specific buttons in apps) is Phase 4. Confirm?

---

## Verification Plan

### Automated Tests
```powershell
# After each component:
.venv\Scripts\python -m pytest Tests/ -q
.venv\Scripts\python -X utf8 beta_test.py
```

### Manual Verification
1. Type `"open chrome"` → Chrome launches
2. Type `"screenshot lo"` (Hindi) → screenshot taken, response in Hindi
3. Type `"kya haal hai"` → Hindi greeting response
4. Say "Hey Vibhu, open notepad" → voice command triggers → Notepad opens
5. Type `"list open apps"` → list of running applications returned

---

## Execution Order

1. **AutomationCore upgrade** (app control) — highest impact, no new dependencies needed
2. **BilingualCore** (Hindi NLP) — pure Python, no dependencies
3. **Corpus expansion** (1200+ pairs) — pure data, no code risk
4. **VoiceCore** (voice daemon) — new module, new deps, most complex
