# SpecializedCore — Domain Expert Engines

Domain-specific engines that handle specialized tasks outside the main reasoning loop. Each core owns a specific capability domain.

## Architecture

```mermaid
graph TB
    subgraph "SpecializedCore"
        DC[DataCore<br/>Memory Store]
        AC[AutomationCore<br/>OS Execution]
        DES[DesignCore<br/>UI Generation]
        IG[ImageGenerationCore<br/>Image Creation]
        DIST[DistributionCore<br/>Stubvi Build]

        subgraph "CodingDomain (9 Specialists)"
            PY[PythonCore]
            JS[JavaScriptCore]
            SQL[SQLCore]
            GO[GoCore]
            RS[RustCore]
            CPP[CppCore]
            SH[BashShellCore]
            RX[RegexCore]
            CR[CodingRouter]
        end

        subgraph "RealWorldDomain (10 Specialists)"
            FS[FileSystemCore]
            NW[NetworkCore]
            DB[DatabaseAdminCore]
            SEC[SecurityCore]
            SA[SystemAdminCore]
            CL[CloudCore]
            EX[ExcelCore]
            WS[WebScrapingCore]
            KN[KnowledgeCore]
            RW[RealWorldRouter]
        end
    end

    CR --> PY
    CR --> JS
    CR --> SQL
    RW --> FS
    RW --> NW
    RW --> DB
```

## Directory Structure

| Directory | Purpose |
|---|---|
| `DataCore/` | Dual memory: ChromaDB (vectors) + SQLite (relational) + GraphRAG |
| `AutomationCore/` | OS command execution, file I/O, process management |
| `DesignCore/` | HTML/CSS template generation, dark-mode glassmorphism |
| `ImageGenerationCore/` | Local image generation pipeline |
| `DistributionCore/` | Stubvi compilation, telemetry, public build packaging |
| `CodingDomain/` | 9 language specialists + router for code tasks |
| `RealWorldDomain/` | 10 real-world specialists + router for system tasks |
| `VoiceCore/` | Voice I/O (wake word, TTS, transcription) — Phase 3 |
