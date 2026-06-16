# L18/C01/T01 — Structured vs Unstructured Logs

## Learning Objectives

- Choose structured logging
- Migrate from unstructured

## Unstructured

```
2026-01-01 12:00:00 INFO User alice@example.com logged in from 1.2.3.4
2026-01-01 12:01:00 ERROR Failed to query DB: connection refused
```

Human-readable; machine-hostile.

## Structured

```json
{"ts": "2026-01-01T12:00:00Z", "level": "info", "msg": "User logged in", "user": "alice@example.com", "ip": "1.2.3.4"}
{"ts": "2026-01-01T12:01:00Z", "level": "error", "msg": "DB query failed", "err": "connection refused", "query": "SELECT ..."}
```

Machine-parseable.

## Why Structured

- Searchable (filter by user, level, etc.)
- Aggregatable (count by error)
- Correlatable (trace_id)
- Tooling friendly

## Why Not

- Verbose
- Slightly less readable raw
- More CPU to format

For: structured wins.

## Format

JSON most common.
- Pretty for humans (locally)
- Single-line for shipping

Or:
- logfmt (key=value)
- protobuf (binary)

## logfmt

```
ts=2026-01-01T12:00:00Z level=info msg="User logged in" user=alice@example.com ip=1.2.3.4
```

Compact; less verbose than JSON.

## Python

```python
import structlog
log = structlog.get_logger()

log.info("user_login", user="alice", ip="1.2.3.4")
```

Output:
```json
{"event": "user_login", "user": "alice", "ip": "1.2.3.4", "timestamp": "...", "level": "info"}
```

## Go

```go
import "log/slog"

slog.Info("user login", "user", "alice", "ip", "1.2.3.4")
```

Output:
```json
{"time":"...","level":"INFO","msg":"user login","user":"alice","ip":"1.2.3.4"}
```

## Node.js

```javascript
import pino from 'pino';
const logger = pino();

logger.info({ user: 'alice', ip: '1.2.3.4' }, 'User login');
```

## Java

```java
import org.slf4j.MDC;

MDC.put("user", "alice");
MDC.put("ip", "1.2.3.4");
log.info("user_login");
```

With logback JSON encoder.

## Common Fields

```json
{
  "ts": "...",
  "level": "info|warn|error",
  "service": "api",
  "version": "1.0.0",
  "env": "prod",
  "trace_id": "...",
  "span_id": "...",
  "msg": "Event description",
  ...event-specific...
}
```

## What to Log

### Always Structured
- User actions
- API calls
- DB queries
- External calls
- Errors

### Event Type
```json
{"event_type": "user_login", "user": "..."}
```

Filter by type.

## What NOT to Log

- Passwords
- API keys
- Credit cards
- PII (without masking)

For: compliance.

## Mask Sensitive

```python
log.info("login_attempt", user=user, ip=ip, password="[REDACTED]")
```

Or middleware that auto-redacts.

## Trace Correlation

```json
{"msg": "DB query", "trace_id": "abc", "span_id": "def", "duration_ms": 50}
```

Click trace → see related logs.

## Context Vars

Per-request:
```python
import structlog

log = structlog.get_logger().bind(request_id=req.id, user=req.user)
log.info("processing")  # request_id + user auto-included
log.info("done")
```

For: avoid repeating.

## Levels

(See T02.)

- debug
- info
- warn
- error
- fatal

## Time

ISO 8601 with timezone:
```
2026-01-01T12:00:00.123Z
```

UTC preferred.

## Sample

For volume:
```python
if random.random() < 0.01:
    log.debug("verbose_event", ...)
```

(See T03.)

## Performance

JSON serialization:
- ~1 µs per log line
- < 1% overhead typical

For: don't worry usually.

## Tools

Parsers:
- Loki / ELK / Splunk / Datadog: all accept JSON

Generators:
- structlog, slog, pino, zap, logback

## CI / Local

Pretty print for dev:
```bash
my_app | jq .
my_app | pino-pretty
```

JSON for prod.

## Migration

From unstructured:
1. Identify hot logs
2. Refactor to structured
3. Update parser pipelines
4. Phase out unstructured

## Best Practices

- JSON or logfmt
- Standard field names
- Trace correlation
- Mask sensitive
- Context vars per request
- Time UTC

## Common Mistakes

- Mix structured + unstructured
- Field name inconsistency
- Plaintext passwords logged
- No trace_id
- Log "the request" (which one?)

## Quick Refs

```
Python:    structlog
Go:        slog (stdlib)
Node:      pino, winston
Java:      logback + JSON encoder
Rust:      tracing
```

## Interview Prep

**Junior**: "What's the difference between structured and unstructured logs?" — Unstructured logs are free-text lines meant for humans; structured logs are key/value records (usually JSON or logfmt) that machines can parse, filter, and aggregate without regex.

**Mid**: "Why standardize field names across services?" — Consistent names like `trace_id`, `service`, and `level` let one query work across every service and let dashboards/alerts join data; inconsistent names (`userId` vs `user_id` vs `uid`) silently break filtering and correlation.

**Senior**: "How do structured logs enable trace correlation?" — Emitting `trace_id` and `span_id` on every line lets you pivot from a single log to the full distributed trace and back to all logs sharing that trace, turning isolated errors into an end-to-end request story.

**Staff**: "Design a logging strategy for a large org." — Mandate JSON/logfmt with a shared field schema and `trace_id`, redact PII at the source, sample by level and endpoint to control cost, and ship via a collector so backends (Loki/ELK/Splunk) stay swappable without touching app code.

## Next Topic

→ [T02 — Log Levels (and Why You're Wrong About Them)](T02-Log-Levels.md)
