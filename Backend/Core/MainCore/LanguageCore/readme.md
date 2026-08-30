# LanguageCore — Multi-Language Umbrella

## Architecture

```
LanguageCore/
├── LanguageCore.py          ← Umbrella router, detection, singleton
├── BaseLanguage.py          ← Abstract base class for all language cores
├── Languages/               ← Individual language implementations
│   ├── HindiCore.py         ← Hindi + Hinglish + 8 dialects
│   ├── EnglishCore.py       ← English + 5 dialect variants
│   ├── SanskritCore.py      ← Sanskrit (Classical + Vedic)
│   ├── MarathiCore.py       ← Marathi + 4 dialects
│   ├── BengaliCore.py       ← Bengali + 4 dialects
│   ├── TamilCore.py         ← Tamil + 3 dialects
│   ├── TeluguCore.py        ← Telugu + 3 dialects
│   ├── GujaratiCore.py      ← Gujarati + 3 dialects
│   ├── KannadaCore.py       ← Kannada + 3 dialects
│   ├── MalayalamCore.py     ← Malayalam + 3 dialects
│   ├── PunjabiCore.py       ← Punjabi + 4 dialects
│   └── UrduCore.py          ← Urdu + 3 dialects
└── readme.md
```

## Supported Languages (12)

| Code | Language | Family | Scripts |
|------|----------|--------|---------|
| hi | Hindi | Indo-Aryan | Devanagari, Latin (Hinglish) |
| en | English | Germanic | Latin |
| sa | Sanskrit | Indo-Aryan | Devanagari, Latin (IAST) |
| mr | Marathi | Indo-Aryan | Devanagari |
| bn | Bengali | Indo-Aryan | Bengali |
| ta | Tamil | Dravidian | Tamil |
| te | Telugu | Dravidian | Telugu |
| gu | Gujarati | Indo-Aryan | Gujarati |
| kn | Kannada | Dravidian | Kannada |
| ml | Malayalam | Dravidian | Malayalam |
| pa | Punjabi | Indo-Aryan | Gurmukhi |
| ur | Urdu | Indo-Aryan | Arabic |

## Usage

```python
from Backend.Core.MainCore.LanguageCore.LanguageCore import LanguageCore

core = LanguageCore.get_instance()

# Detect language
det = core.detect("namaste kya haal hai")
print(det.language_code)  # "hi"
print(det.confidence)     # 0.90

# Get templates
greeting = core.get_greeting("hi")
error = core.get_error("en")

# Check specific language
core.is_language("hello", "en")  # True
```

## Adding a New Language

1. Create `Languages/NewLangCore.py`
2. Extend `LanguageCoreBase`
3. Implement all required methods
4. Register in `LanguageCore._register_languages()`

```python
from ..BaseLanguage import LanguageCoreBase, LanguageFamily, Script

class EsperantoCore(LanguageCoreBase):
    @property
    def code(self) -> str:
        return "eo"
    # ... implement all abstract methods
```

## Design Decisions

- **Umbrella pattern**: One router, many language-specific cores. Clean separation.
- **Detection scoring**: Each core returns 0.0-1.0 confidence. Highest wins.
- **Script detection**: Fast-path for Devanagari, Bengali, Tamil, etc. before word analysis.
- **Dialect awareness**: Each core declares dialect variants with region metadata.
- **Extensible**: New languages added by dropping in a single file.
