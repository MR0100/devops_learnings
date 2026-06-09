# L17/C06 — OpenTelemetry

## Topics

- **T01 OTel Architecture (SDK, Collector, Exporters)** — How OTel components fit
- **T02 Semantic Conventions** — Standard attribute names
- **T03 Auto-Instrumentation** — Zero code-changes for common frameworks
- **T04 OTLP Protocol** — Wire format

## Why OTel

Before OTel, every observability vendor had its own SDK:
- Datadog tracer
- New Relic agent
- Prometheus client lib
- OpenTracing (one project), OpenCensus (another) — both pre-OTel
- And many more

OTel merged OpenTracing + OpenCensus. Standard SDK + standard protocol + vendor-neutral.

## Architecture

```
[Your App]
   ↓ OTel SDK (manual or auto-instrumented)
   ↓ OTLP (gRPC or HTTP)
[OTel Collector] (sidecar / DaemonSet / standalone)
   ├─ receivers (OTLP, Prometheus, Jaeger, Zipkin)
   ├─ processors (batch, attributes, filter, sample)
   └─ exporters (Prometheus, Loki, Tempo, Jaeger, Datadog, ...)
   ↓
[Backends]
```

## SDK

Per-language SDK creates spans, metrics, logs:

### Python
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="otel-collector:4317")))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_payment") as span:
    span.set_attribute("user_id", 42)
    span.set_attribute("amount_cents", 1234)
    # ... work ...
```

### Go
```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
)

tracer := otel.Tracer("checkout")
ctx, span := tracer.Start(ctx, "process_payment")
defer span.End()
span.SetAttributes(attribute.Int("user_id", 42))
```

## Auto-Instrumentation

Many languages support auto-instrumenting common libraries:
- **Java**: `-javaagent:otel-javaagent.jar` (instruments HTTP, JDBC, Kafka, etc.)
- **Python**: `opentelemetry-instrument python app.py`
- **Node**: `--require '@opentelemetry/auto-instrumentations-node/register'`

Zero code changes for HTTP server/client, DB drivers, message queues, etc.

## Collector

A Go binary that receives, processes, and exports telemetry. Modular via YAML config.

```yaml
receivers:
  otlp:
    protocols:
      grpc: {}
      http: {}
  prometheus:
    config:
      scrape_configs:
        - job_name: 'kubernetes-pods'
          kubernetes_sd_configs: [{role: pod}]

processors:
  batch:
    timeout: 10s
  memory_limiter:
    limit_mib: 1024
  resource:
    attributes:
      - key: cluster
        value: prod-us-east-1
        action: insert
  filter:
    traces:
      span:
        - 'attributes["http.url"] == "/healthz"'        # drop healthz traces

exporters:
  otlp/tempo:
    endpoint: tempo.tempo.svc:4317
  prometheusremotewrite:
    endpoint: http://mimir.mimir.svc:9009/api/v1/push
  loki:
    endpoint: http://loki.loki.svc:3100/loki/api/v1/push

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, resource, filter, batch]
      exporters: [otlp/tempo]
    metrics:
      receivers: [otlp, prometheus]
      processors: [batch]
      exporters: [prometheusremotewrite]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [loki]
```

### Deployment Patterns
- **Sidecar**: per pod (heavyweight)
- **Agent (DaemonSet)**: per node — most common
- **Gateway**: central tier for transformations, sampling, fan-out

Common: agent on every node + gateway for org-wide processing.

## Semantic Conventions

Standard attribute names so dashboards work across services.

```
service.name = "checkout"          # required
service.version = "1.2.3"
deployment.environment = "prod"
host.name = "..."

http.method = "GET"
http.route = "/api/users/{id}"
http.status_code = 200
http.url = "https://..."

db.system = "postgresql"
db.statement = "SELECT ..."

messaging.system = "kafka"
messaging.destination.name = "orders"
```

Spans, metrics, logs all use the same conventions. Standard names mean tools (Jaeger, Tempo, Datadog) can show service maps, latency charts, etc., consistently.

## OTLP Protocol

- Protobuf over gRPC (preferred) or HTTP/JSON
- Batches of spans / metrics / logs
- Resource attributes (which service/host) + per-record attributes

Single protocol replaces per-vendor wire formats.

## Sampling

### Head Sampling
Decide at trace start. Cheap; lose interesting traces.
- TraceIdRatioBasedSampler (e.g., 10%)
- ParentBased (respect upstream decisions)

### Tail Sampling (in Collector)
Decide after trace complete. Keep:
- All errors
- Slow ones (p99 latency)
- Random sample of the rest

```yaml
processors:
  tail_sampling:
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow
        type: latency
        latency: { threshold_ms: 1000 }
      - name: random-10pct
        type: probabilistic
        probabilistic: { sampling_percentage: 10 }
```

## Logs in OTel

Newer than traces/metrics; rapidly maturing.
- Bridge existing loggers (slog, log4j, etc.) to OTel
- Correlate via trace_id / span_id automatically

## Migration

Migrate vendor lock-in to OTel:
1. Instrument with OTel SDK
2. Collector → existing vendor
3. Later: Collector → new vendor (no app change)

Decouples app code from observability backend.

## Interview Themes

- "OTel architecture — what does the Collector do?"
- "Auto-instrumentation — how?"
- "Head vs tail sampling — tradeoffs"
- "Semantic conventions — why care?"
- "Migrate from Datadog SDK to OTel — strategy"
