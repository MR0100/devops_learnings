# L17/C06/T03 — Auto-Instrumentation

## Learning Objectives

- Use auto-instrumentation
- Add custom spans

## Auto-Instrumentation

OTel detects + instruments common libraries automatically:
- HTTP servers / clients
- DB clients
- Message brokers
- gRPC

No code changes.

## Python

```bash
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install

# Run
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
OTEL_SERVICE_NAME=my-app \
opentelemetry-instrument python app.py
```

Auto-instruments:
- Flask, Django, FastAPI
- requests, urllib
- SQLAlchemy, psycopg2
- Redis, pymongo
- Celery, kombu

## Java

```bash
# Download agent
wget https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar

# Run
java -javaagent:opentelemetry-javaagent.jar \
  -Dotel.service.name=my-app \
  -Dotel.exporter.otlp.endpoint=http://localhost:4317 \
  -jar myapp.jar
```

Auto-instruments tons:
- Servlets, Spring, JAX-RS
- JDBC, Hibernate
- HTTP clients
- Many libraries

## Node.js

```bash
npm install --save @opentelemetry/auto-instrumentations-node

node -r ./tracing.js app.js
```

```js
// tracing.js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');

const sdk = new NodeSDK({
  serviceName: 'my-app',
  instrumentations: [getNodeAutoInstrumentations()],
});
sdk.start();
```

Auto:
- HTTP, Express, Fastify
- pg, mysql, mongo
- Redis
- gRPC

## .NET

```bash
dotnet add package OpenTelemetry.Instrumentation.AspNetCore
dotnet add package OpenTelemetry.Exporter.OpenTelemetryProtocol
```

```csharp
builder.Services.AddOpenTelemetry()
  .WithTracing(b => b
    .AddAspNetCoreInstrumentation()
    .AddHttpClientInstrumentation()
    .AddOtlpExporter());
```

## Go

Go lacks runtime auto-inst. Manual:
```go
import "go.opentelemetry.io/otel"

tracer := otel.Tracer("my-app")
ctx, span := tracer.Start(ctx, "my-operation")
defer span.End()
```

Plus contrib middlewares:
- otelmux
- otelgin
- otelpgx

## Custom Spans

```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

def process_order(order_id):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        # ... work ...
        if error:
            span.set_status(Status(StatusCode.ERROR))
            span.record_exception(e)
```

For: custom logic beyond auto.

## Add Attributes

```python
span.set_attribute("user.id", user_id)
span.set_attribute("order.total", total)
```

For: business-context.

## Events

```python
span.add_event("cache_miss", {"key": cache_key})
```

For: span timeline.

## Status

```python
from opentelemetry.trace import Status, StatusCode

span.set_status(Status(StatusCode.ERROR, "Description"))
```

## Exception

```python
span.record_exception(e)
```

Captures type, message, stacktrace.

## Disable Specific

```bash
OTEL_PYTHON_DISABLED_INSTRUMENTATIONS=requests,urllib3
```

For: avoid double-instrumentation.

## Configuration

```bash
OTEL_SERVICE_NAME=my-app
OTEL_RESOURCE_ATTRIBUTES=env=prod,version=1.0
OTEL_TRACES_EXPORTER=otlp
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.1   # 10%
OTEL_METRICS_EXPORTER=otlp
OTEL_LOGS_EXPORTER=otlp
OTEL_PROPAGATORS=tracecontext,baggage
```

## Logs

OTel Logs SDK:
- Auto-instrument logging frameworks
- Attach trace_id to logs

```python
import logging
from opentelemetry.instrumentation.logging import LoggingInstrumentor
LoggingInstrumentor().instrument(set_logging_format=True)

logger = logging.getLogger(__name__)
logger.info("Hello")
# Auto-emits with trace_id
```

## Metrics

```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)
counter = meter.create_counter("orders.placed")
counter.add(1, {"region": "us-east-1"})
```

For: custom metrics via OTel.

## SDK vs Auto-Inst

| | Auto | Manual |
|---|---|---|
| Setup | 1 command | code |
| Coverage | common libs | custom logic |
| Detail | standard | custom attrs |

Use both: auto for boilerplate, manual for business.

## Performance

Auto-inst overhead: 1-5%.

For high-perf: profile; selective instrumentation.

## Sampling

Trace sampler:
- always_on
- always_off
- parentbased
- traceidratio (0.0-1.0)

```bash
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.05   # 5%
```

For: cost control.

## Best Practices

- Auto-inst start
- Custom spans for business logic
- Standard attribute names
- Sampler tuned (1-5% prod)
- Logs + traces linked
- Resource attrs at init

## Common Mistakes

- All instrumentations (overhead)
- 100% sampling (cost)
- Custom names (lose conventions)
- High-cardinality span names

## Debugging

```bash
OTEL_LOG_LEVEL=debug
```

See what's emitted.

Or: logging exporter:
```yaml
exporters:
  logging:
    verbosity: detailed
```

## Quick Refs

```bash
# Python
opentelemetry-bootstrap -a install
opentelemetry-instrument python app.py

# Java
java -javaagent:agent.jar -jar app.jar

# Node
node -r ./tracing.js app.js

# Env
OTEL_SERVICE_NAME=...
OTEL_EXPORTER_OTLP_ENDPOINT=...
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.1
```

## Interview Prep

**Mid**: "Auto-instrumentation."

**Senior**: "When custom spans."

**Staff**: "Instrumentation strategy."

## Next Topic

→ [T04 — OTLP Protocol](T04-OTLP-Protocol.md)
