# L18/C06/T02 — Zipkin

## Learning Objectives

- Know Zipkin
- Compare to others

## Zipkin

Original tracing backend (Twitter, 2012):
- Java
- Simple model
- Multiple storage
- Web UI

Predates Jaeger but similar.

## Install

```bash
docker run -d -p 9411:9411 openzipkin/zipkin
```

K8s:
```bash
helm install zipkin openzipkin/zipkin
```

## Architecture

- **Collector**: receives spans
- **Storage**: in-memory, MySQL, Cassandra, ES
- **Query**: API
- **UI**: web

Single binary typical (collector + query + UI).

## Send Traces

OTel:
```bash
OTEL_EXPORTER_ZIPKIN_ENDPOINT=http://zipkin:9411/api/v2/spans
OTEL_TRACES_EXPORTER=zipkin
```

Native (Brave for Java, others):
```java
Tracing tracing = Tracing.newBuilder()
  .localServiceName("my-app")
  .spanReporter(...)
  .build();
```

## UI

http://localhost:9411

Search by:
- Service name
- Time range
- Tags

## B3 Propagation

Zipkin invented B3 headers:
```
X-B3-TraceId
X-B3-SpanId
X-B3-ParentSpanId
X-B3-Sampled
```

Or single:
```
b3: traceId-spanId-sampled
```

For: legacy. W3C TraceContext now preferred.

## Storage

- In-memory (dev)
- MySQL (simple)
- Cassandra (scale)
- Elasticsearch (search)

For prod: Cassandra or ES.

## Compared

| | Zipkin | Jaeger |
|---|---|---|
| Origin | Twitter | Uber |
| Lang | Java | Go |
| Headers | B3 | uber + W3C |
| UI | minimal | richer |
| Adoption | declining | growing |

## When Zipkin

- Legacy apps (B3)
- Java shops
- Simple needs

## When Jaeger / Tempo

- Modern
- Better UI
- More features

## Migration

From Zipkin to OTel + Tempo/Jaeger:
1. Add OTel SDK
2. Multi-propagator (B3 + W3C)
3. Test
4. Switch backend
5. Remove Zipkin

For: phase out.

## Status

Zipkin maintained but mindshare shifted to Jaeger / Tempo.

For new: use OTel + Tempo/Jaeger.

## Mature OSS

Zipkin reliable for what it does. Many production deployments.

## Quick Refs

```bash
# Run
docker run -p 9411:9411 openzipkin/zipkin

# UI
http://localhost:9411

# OTel exporter
OTEL_TRACES_EXPORTER=zipkin
OTEL_EXPORTER_ZIPKIN_ENDPOINT=http://zipkin:9411/api/v2/spans

# Headers
X-B3-TraceId, X-B3-SpanId, X-B3-Sampled
b3: TraceId-SpanId-Sampled
```

## Interview Prep

**Mid**: "Zipkin vs Jaeger."

**Senior**: "Legacy tracing."

## Next Topic

→ [T03 — Tempo](T03-Tempo.md)
