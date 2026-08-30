# ValidationCore — Yama (Justice)

## Role
The quality AND security gate. Sits between every core transition:
```
User Input → [ValidationCore] → Core Processing → [ValidationCore] → User Output
```

## Architecture

```
ValidationCore
├── InputSanitizer          ← INPUT GATE
│   ├── SQL injection detection
│   ├── XSS/script injection blocking
│   ├── Command injection detection
│   ├── Prompt injection detection
│   └── Size limits
├── OutputValidator         ← OUTPUT GATE
│   ├── Schema compliance
│   ├── Credential leakage detection
│   ├── PII leakage detection
│   ├── Relevance check (keyword overlap)
│   └── Content safety
├── CyberSecMonitor         ← CYBERSEC
│   ├── Failed attempt tracking
│   ├── Brute force detection
│   ├── Session blocking
│   ├── Anomaly detection
│   └── Audit event logging
└── Quality Assurance       ← QUALITY
    ├── Response coherence
    └── Helpfulness scoring
```

## Input Gate (InputSanitizer)

| Check | Threat Level | Action |
|-------|-------------|--------|
| SQL injection | HIGH | Block + log |
| XSS/script injection | HIGH | Block + log |
| Command injection | CRITICAL | Block + log + alert |
| Prompt injection | HIGH | Block + log |
| Excessive length | LOW | Truncate/reject |

## Output Gate (OutputValidator)

| Check | Threat Level | Action |
|-------|-------------|--------|
| Empty response | NONE | Reject |
| Credential leakage | CRITICAL | Block + redact |
| Low relevance | LOW | Flag (still pass) |
| Schema mismatch | NONE | Reject |

## CyberSec Monitor

Tracks per-session:
- Failed validation attempts
- Repeated injection attempts
- Session blocking after N violations
- Audit trail of all security events

## Usage

```python
vc = ValidationCore.get_instance()

# Before processing
result = vc.validate_input(user_input, session_id="session_123")
if not result.passed:
    return {"error": result.reason}

# After processing
result = vc.validate_output(response, prompt=user_input)
if not result.passed:
    return safe_fallback

# Check threats
summary = vc.get_threat_summary()
```

## Adding New Checks

1. Add pattern to `InputSanitizer` or `OutputValidator`
2. Set appropriate `ThreatLevel`
3. Patterns auto-compiled on initialization
4. Events auto-logged via `CyberSecMonitor`
