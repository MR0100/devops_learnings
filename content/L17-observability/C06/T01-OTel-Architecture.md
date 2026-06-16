# L17/C06/T01 — OpenTelemetry Architecture

## Learning Objectives

- Understand OTel
- Install collector

## OpenTelemetry

CNCF; vendor-agnostic observability:
- SDK (in apps)
- Collector (intermediate)
- Exporters (to backends)
- Semantic conventions
- OTLP protocol

For: future-proof instrumentation.

## Why

- One SDK; many backends
- Avoid vendor lock-in
- Standard semantics

Before: per-vendor SDK (Datadog, NR, etc.).
Now: OTel + exporter to vendor.

## Components

### SDK
In-app library:
```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("operation"):
    ...
```

### Collector
Receives, processes, exports:
```
App OTLP → Collector → Backend (Datadog / Jaeger / etc.)
```

### Exporters
- OTLP
- Jaeger
- Prometheus
- Datadog
- many more

## Collector Config

```yaml
# collector.yaml
receivers:
  otlp:
    protocols:
      grpc: { endpoint: 0.0.0.0:4317 }
      http: { endpoint: 0.0.0.0:4318 }

processors:
  batch:
  memory_limiter:
    check_interval: 1s
    limit_mib: 1000

exporters:
  otlp:
    endpoint: tempo:4317
  prometheus:
    endpoint: 0.0.0.0:8889

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, memory_limiter]
      exporters: [otlp]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
```

## Run Collector

```bash
docker run -p 4317:4317 -p 4318:4318 \
  -v $(pwd)/collector.yaml:/etc/otel/config.yaml \
  otel/opentelemetry-collector-contrib
```

## SDKs

Available for:
- Python
- JS / TS
- Java
- .NET
- Go
- Rust
- C++
- PHP
- Ruby

## Auto-Instrumentation

```bash
# Python
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install

OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
OTEL_SERVICE_NAME=my-app \
opentelemetry-instrument python app.py
```

Auto-instruments:
- Flask / FastAPI / Django
- requests
- SQLAlchemy
- Redis
- etc.

## Java Agent

```bash
java -javaagent:opentelemetry-javaagent.jar \
  -Dotel.service.name=my-app \
  -Dotel.exporter.otlp.endpoint=http://localhost:4317 \
  -jar myapp.jar
```

Zero-code instrumentation.

## Pipelines

### Traces
App → SDK → Collector → Tempo/Jaeger

### Metrics
App → SDK → Collector → Prometheus

### Logs
App → SDK / fluent-bit → Collector → Loki

For: unified pipeline.

## Resource Attributes

```python
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "my-app",
    "service.version": "1.0.0",
    "deployment.environment": "production",
})
```

Attached to every span/metric.

## Context Propagation

```python
# Auto via HTTP middleware
# In app, span tracks request

# Manual
from opentelemetry import context
ctx = context.get_current()
```

For: cross-service traces.

## Baggage

Per-request data:
```python
from opentelemetry import baggage
baggage.set_baggage("user_id", "alice")
```

Propagated across spans.

For: user / tenant context.

## Collector Modes

### Agent (Per-Host / Per-Pod)
Daemon. Apps send local.

### Gateway (Central)
Cluster. Apps send to load-balanced gateway.

```
Pattern:
App → Agent (sidecar/daemonset) → Gateway → Backend
```

Layered:
- Agent: fast, local
- Gateway: enrich, route, aggregate

## Processors

- batch
- memory_limiter
- attributes (rename, drop, add)
- filter
- resource
- tail_sampling (intelligent sampling)
- transform

## Tail Sampling

Smart sampling:
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
      - name: random
        type: probabilistic
        probabilistic: { sampling_percentage: 10 }
```

Keep errors + slow + 10% random.

For: focused trace storage.

## Exporters

```yaml
exporters:
  # Multiple backends
  otlp: { endpoint: tempo:4317 }
  datadog: { api: { key: $DD_API_KEY } }
  prometheus: { endpoint: 0.0.0.0:8889 }
  debug: { verbosity: detailed }   # formerly the "logging" exporter
```

Send to many.

## OTLP

Protocol:
- gRPC (4317)
- HTTP/protobuf (4318)

Binary; efficient.

For: standard between SDKs and Collector.

## Best Practices

- Auto-instrumentation start
- Resource attributes (service, env, version)
- Collector agent + gateway pattern
- Tail sampling for traces
- Batch processor
- Memory limiter

## Common Mistakes

- Direct SDK to backend (no collector)
- No tail sampling (cost)
- Missing resource attrs
- No batch (high overhead)
- Wrong protocol (HTTP vs gRPC)

## Migration

From vendor SDK:
1. Add OTel SDK
2. Configure collector
3. Test parallel
4. Remove vendor SDK
5. Update exporter to vendor (via OTel)

For: gradual.

## Quick Refs

```bash
# Env vars
OTEL_SERVICE_NAME=my-app
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_RESOURCE_ATTRIBUTES=env=prod,version=1.0
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.1

# Auto-inst
opentelemetry-instrument python app.py
java -javaagent:agent.jar -jar app.jar

# Collector
otel-collector --config=collector.yaml
```

## Interview Prep

**Mid**: "What's OpenTelemetry."

**Senior**: "OTel architecture."

**Staff**: "Vendor-neutral observability."

## Next Topic

→ [T02 — Semantic Conventions](T02-Semantic-Conventions.md)
