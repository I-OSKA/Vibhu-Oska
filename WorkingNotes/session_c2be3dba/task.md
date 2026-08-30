# Phase 3 Task Tracker

## Pillar 1 — AutomationCore App Control
- [/] Read existing AutomationCore.py
- [ ] Add AppController class (open/close/switch/screenshot/type/keypress)
- [ ] Wire app-control intents in App.py _route_to_specialized_core
- [ ] Add BackupCore OS command routing + responses
- [ ] Install pygetwindow, pyautogui if missing

## Pillar 2 — BilingualCore (Hindi + English)
- [ ] Create Backend/Core/BackupCore/BilingualCore.py
- [ ] Language detector (en / hi / hinglish)
- [ ] Hindi intent mapper (rule-based, no cloud)
- [ ] Hindi response templates (all 20+ categories)
- [ ] Wire into BackupCore._reason() as first pass

## Pillar 3 — Corpus Expansion
- [ ] Expand CORPUS_QA to 1200+ pairs in train.py
- [ ] English domain pairs (architecture, Python, AI)
- [ ] Hindi pairs (200+ bilingual)
- [ ] OS command pairs (open/close/screenshot)
- [ ] Conversational flow pairs

## Pillar 4 — VoiceCore
- [ ] Create Backend/Core/SpecializedCore/VoiceCore/__init__.py
- [ ] Create VoiceCore.py (vosk STT + pyttsx3 TTS + wake word)
- [ ] Register /ws/voice endpoint in App.py
- [ ] Add voice waveform UI to index.html
- [ ] Test end-to-end voice command flow

## Cleanup
- [ ] Syntax check all modified files
- [ ] Run beta_test.py with new Hindi prompts
- [ ] Update AGENT_STATE_CACHE.md
