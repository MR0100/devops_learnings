# L06/C05/T03 — Logging, Tracing, Metrics in Tools

## Learning Objectives

- Add observability to your tool
- Structured output

## Why Observability in Tools

When a tool runs in CI / cron / on someone else's machine, the only debug signal you have is its output. Good observability:
- Helps debug failures
- Audits actions
- Enables monitoring (when tool runs continuously)

## Three Pillars

| | Purpose | Format |
|---|---|---|
| Logs | What happened | Lines / events |
| Metrics | How much / how fast | Counters, gauges |
| Traces | Request path | Span tree |

For one-shot CLIs: mostly logs. For long-running daemons: all three.

## Structured Logging

Plain:
```
2026-06-09 10:00:00 Starting deploy for myapp
```

Structured:
```json
{"time":"2026-06-09T10:00:00Z","level":"info","msg":"deploy.start","service":"myapp","version":"v1.2.3","user":"alice"}
```

Why structured:
- Parsable (jq, grep, query in Splunk/Loki)
- Filter by field
- Aggregate (count by service)

### Python
```python
import logging
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "time": self.formatTime(record),
            "level": record.levelname,
            "msg": record.getMessage(),
            **getattr(record, "extra", {}),
        })

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.info("deploy.start", extra={"service": "myapp"})
```

Or use `structlog`:
```python
import structlog
log = structlog.get_logger()
log.info("deploy.start", service="myapp", version="v1.2.3")
```

### Go
Use `slog` (stdlib 1.21+):
```go
import "log/slog"

logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
logger.Info("deploy.start", "service", "myapp", "version", "v1.2.3")
```

Or `zap` (faster):
```go
import "go.uber.org/zap"

logger, _ := zap.NewProduction()
defer logger.Sync()
logger.Info("deploy.start",
    zap.String("service", "myapp"),
    zap.String("version", "v1.2.3"),
)
```

## Log Levels

| Level | When |
|---|---|
| DEBUG | Verbose; off by default |
| INFO | Normal events |
| WARN | Something off but not broken |
| ERROR | Operation failed |
| FATAL | Cannot continue; exit |

User controls: `mytool -v` (debug), `--quiet` (warn+).

## What to Log

**Always**:
- Start/end of major operations
- Errors (with context: what were we doing?)
- Decisions (chose X because Y)
- External calls (URL, status, duration)

**Don't**:
- Secrets (tokens, passwords)
- PII (emails, names — unless needed)
- Tight loops (10000 logs/sec swamps anything)

## Stderr vs Stdout

- **stdout**: tool's output / data
- **stderr**: logs, errors, progress

This lets users:
```bash
mytool get-data > data.json 2> debug.log
```

Or pipe data:
```bash
mytool get-data | jq '.users[]'
```

## Request IDs

Every external request gets an ID; propagate:
```python
import uuid
req_id = uuid.uuid4().hex[:8]
log.info("api.call", req_id=req_id, url=url)
# Pass via X-Request-Id header
headers = {"X-Request-Id": req_id}
```

Lets you correlate logs across distributed systems.

## Tracing

For tools that make many calls:
```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("deploy"):
    with tracer.start_as_current_span("validate"):
        validate()
    with tracer.start_as_current_span("apply"):
        apply()
```

Send to Jaeger/Tempo/etc. for visualization.

Useful when tool calls many APIs (which is slow?).

## Metrics

For long-running daemons:
```python
from prometheus_client import Counter, Histogram, start_http_server

deployments_total = Counter("deployments_total", "Total", ["service", "status"])
deploy_duration = Histogram("deploy_duration_seconds", "Duration")

with deploy_duration.time():
    deploy()
deployments_total.labels(service="myapp", status="success").inc()

start_http_server(9090)  # Prometheus scrapes
```

CLIs: not usually metrics; emit duration / count at end:
```
$ mytool deploy
✓ Deployed myapp v1.2.3 in 47s
  API calls: 12
  Modified: 3 resources
```

## Audit Logging

For destructive ops, send to durable log:
```python
audit_log({
    "user": current_user(),
    "action": "delete",
    "target": "pod/web-1",
    "namespace": "prod",
    "time": now(),
})
```

Send to immutable store (CloudTrail, syslog, dedicated SIEM).

## OpenTelemetry

Standard for instrumentation:
- Logs, Metrics, Traces unified
- SDKs for every language
- Vendor-neutral (export to Datadog, NewRelic, Jaeger, Honeycomb)

```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp import ...

# Auto-instrument requests, boto3, etc.
```

For new tools: OTel from day 1.

## Examples

### CLI with Verbose Mode
```bash
$ mytool deploy myapp
✓ Deployed in 12s

$ mytool deploy myapp -v
[INFO] starting deploy
[INFO] cluster: prod-us-east-1
[INFO] current image: v1.2.2
[INFO] target image: v1.2.3
[INFO] applying...
[INFO] rollout started
[INFO] waiting (timeout 5m)
[INFO] rollout complete
✓ Deployed in 12s
```

### Daemon with Metrics
```
GET /metrics
mytool_operations_total{service="myapp",status="success"} 1234
mytool_operations_total{service="myapp",status="failure"} 5
mytool_operation_duration_seconds_bucket{le="1"} 100
mytool_operation_duration_seconds_bucket{le="5"} 500
```

## Performance Concerns

Logging can be slow:
- Async / buffered
- Sample (every 100th)
- Lazy format (don't compute if not enabled)
- Avoid string formatting in hot path

```python
log.debug("processed %d items", n)         # cheap
log.debug(f"processed {expensive()} items") # always runs expensive
```

## Common Mistakes

- Logging secrets
- Single-line per request (use JSON)
- Logs only on success (errors lost)
- No request IDs (can't correlate)
- All to stdout (mixes with data)
- DEBUG always on (perf cost; noise)

## Testing Logs

```python
def test_logs(caplog):
    with caplog.at_level(logging.INFO):
        deploy("myapp")
    assert "deploy.start" in caplog.text
```

## Interview Prep

**Mid**: "Structured logging — why."

**Senior**: "Trace vs log."

**Staff**: "OTel migration — adopt it."

## Next Topic

→ [T04 — Configuration: Env, Files, Flags](T04-Configuration.md)
