# L18/C01 — Logging Fundamentals

## Topics

- **T01 Structured vs Unstructured Logs** — Why structured wins
- **T02 Log Levels (and Why You're Wrong About Them)** — Common misuse
- **T03 Sampling Strategies** — When you can't ship everything

## Structured Logging

JSON or key=value per line. Searchable, filterable, type-aware.

### Unstructured (bad)
```
2026-06-09 12:00:00 ERROR Payment failed for user 42 amount $1234
```

To find "all failures > $1000" requires regex. Brittle.

### Structured (good)
```json
{
  "ts": "2026-06-09T12:00:00Z",
  "level": "error",
  "service": "payments",
  "trace_id": "abc123",
  "span_id": "def456",
  "user_id": 42,
  "amount_cents": 123400,
  "currency": "USD",
  "msg": "payment failed",
  "error": "card_declined",
  "card_brand": "visa"
}
```

Query "all failures > $1000" trivially via Loki / Elastic / etc.

### Libraries
- Go: `slog` (stdlib, 1.21+), `zap`, `zerolog`
- Python: `structlog`, `loguru`
- Node: `pino`, `bunyan`
- Java: Logback + JSON encoder, log4j2 + JsonLayout

### slog Example (Go)
```go
import "log/slog"

logger := slog.New(slog.NewJSONHandler(os.Stderr, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))

logger.Info("payment processed",
    "user_id", 42,
    "amount_cents", 1234,
    "trace_id", traceID,
)
```

### structlog Example (Python)
```python
import structlog
log = structlog.get_logger()
log.info("payment processed", user_id=42, amount_cents=1234, trace_id=trace_id)
```

## Log Levels

Standard:
- DEBUG: detailed info; off in prod
- INFO: notable events (request started, finished)
- WARN: unexpected but recoverable
- ERROR: failure that user sees
- FATAL: process is dying

### Common Misuse

- "INFO logs everywhere" — chat-bot dialog, useless noise
- "WARN for things we should fix later" — accumulates; never seen
- "ERROR for handled exceptions" — pollutes ERROR signal
- "FATAL but the process keeps running" — meaningless

### Rules of Thumb
- Log INFO once at "request started" and once at "request finished"
- Log WARN when something is unusual but doesn't fail (cache miss, retry triggered)
- Log ERROR only when the user's request fails
- Log DEBUG only when debugging actively (with flag)
- Set per-package levels for noisy libraries

### Alerting on Error Logs
Don't. Errors happen routinely (validation, 404s). Alert on **rates** of errors, not single occurrences.

## Sampling

At high throughput, shipping every log is expensive. Sample.

### Strategies
- **Constant rate**: keep 10% of INFO; 100% of ERROR
- **Per-customer**: keep all logs for premium customers
- **Trace-based**: keep logs for traces sampled in
- **Adaptive**: shed load when ingestion lags

### Pino sampling example
```javascript
const logger = pino({
  base: { service: 'api' },
  level: 'info',
  hooks: {
    logMethod(args, method, level) {
      if (level === 30 /* info */) {  // 10% sample
        if (Math.random() > 0.1) return;
      }
      method.apply(this, args);
    }
  }
});
```

### Drop at Source vs at Collector
- At source: less CPU/memory in app; can lose useful logs
- At collector: more flexibility; pay for ingestion to collector

## Cardinality Discipline

For Loki (and any label-indexed log store):
- Use **labels** for low-cardinality (service, env, level)
- Use **fields** in the log body for high-cardinality (user_id, trace_id)

Treating user_id as a label in Loki → millions of streams → explodes index.

## Personal / Sensitive Data

- Don't log: passwords, tokens, full SSN, full credit card
- Log: hashed identifiers, last 4 digits, type but not value
- Comply with GDPR (right to deletion)
- Mask in shipper if needed (Fluent Bit redact filter)

## Trace Correlation

Always include trace_id, span_id in logs:
```json
{"msg": "db query", "trace_id": "abc123", "span_id": "def456", "duration_ms": 45}
```

OTel auto-injects via context. Manual when needed.

Then in your observability UI: click trace → see all logs for that trace.

## Log vs Metric vs Trace Decision

| Use Case | Use |
|---|---|
| "How often does X happen?" | Metric (counter) |
| "What's the rate / distribution?" | Metric (histogram) |
| "What happened in this request?" | Trace |
| "What were the details of this specific event?" | Log |
| "How are we trending over weeks?" | Metric |
| "Did this incident affect customer Y?" | Log query by user_id |

## Interview Themes

- "Why structured logging?"
- "Log levels — common mistakes"
- "Sampling strategies"
- "Why high-cardinality labels are bad in Loki"
- "Correlate logs and traces — how?"
