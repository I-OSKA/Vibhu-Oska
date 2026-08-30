# Log — Runtime Logs & Artifacts

## Structure

```
Log/
├── screenshots/           ← AutomationCore screenshot captures
├── *.log                  ← Runtime log files
└── log.md
```

## Log Files

| File | Purpose |
|------|---------|
| `vibhu_oska.log` | Main application log |
| `training.log` | Model training logs |
| `events.jsonl` | EventBus event stream |

## Screenshot Storage

AutomationCore saves screenshots to `Log/screenshots/` with timestamps:
```
screenshot_1691234567.png
screenshot_1691234568.png
```

## Log Rotation

- Max log file size: 10MB
- Rotation: Keep last 5 files
- Old files archived with timestamps
