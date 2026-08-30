# CodingDomain — Code Specialists

9 language-specific specialists and a router for code generation, analysis, and refactoring tasks.

## Architecture

```mermaid
graph TB
    CR[CodingRouter] --> PY[PythonCore<br/>Python expert]
    CR --> JS[JavaScriptCore<br/>JS/TS expert]
    CR --> SQL[SQLCore<br/>SQL expert]
    CR --> GO[GoCore<br/>Go expert]
    CR --> RS[RustCore<br/>Rust expert]
    CR --> CPP[CppCore<br/>C/C++ expert]
    CR --> SH[BashShellCore<br/>Shell/Bash expert]
    CR --> RX[RegexCore<br/>Regex expert]

    CR --> |"classify language"| PROMPT[User Prompt]
    PY --> |"generate code"| RESP[Response]
    JS --> |"generate code"| RESP
```

## Specialists

| Specialist | Language | Capabilities |
|------------|----------|--------------|
| `PythonCore` | Python | FastAPI, PyTorch, asyncio, dataclasses |
| `JavaScriptCore` | JS/TS | React, Node.js, WebSocket, ES6+ |
| `SQLCore` | SQL | SQLite, PostgreSQL, schema design |
| `GoCore` | Go | Goroutines, channels, HTTP servers |
| `RustCore` | Rust | Ownership, traits, async |
| `CppCore` | C/C++ | Templates, RAII, systems programming |
| `BashShellCore` | Shell | Bash, PowerShell, automation |
| `RegexCore` | Regex | Pattern matching, parsing |
| `CodingRouter` | — | Classifies prompt → specialist |
