# L18/C06/T02 — Zipkin

## Learning Objectives

- Explain Zipkin's architecture and where it fits in the tracing landscape
- Send traces to Zipkin from OpenTelemetry and understand B3 propagation
- Decide when Zipkin is appropriate versus migrating to OTel + Tempo/Jaeger

## Zipkin

Zipkin is the original open-source distributed-tracing backend, created at Twitter in 2012 and inspired by Google's Dapper paper. It is written in Java, uses a deliberately simple span model, supports several pluggable storage backends, and ships with a web UI for searching and visualizing traces. It predates Jaeger and shares much of the same design, so the two are conceptually similar; Jaeger has since taken most of the community mindshare, but Zipkin remains a stable, widely-deployed option.

## Install

```bash
docker run -d -p 9411:9411 openzipkin/zipkin
```

K8s:
```bash
helm install zipkin openzipkin/zipkin
```

## Architecture

Zipkin has four logical components: a **collector** that receives reported spans, a **storage** layer (in-memory, MySQL, Cassandra, or Elasticsearch), a **query** service that exposes a span-search API, and a **web UI**. In most deployments all four run together as a single self-contained binary, which makes it easy to stand up — one container gives you collection, storage, query, and UI.

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

Zipkin invented the **B3 propagation headers**, which carry trace identity across service hops:

```
X-B3-TraceId
X-B3-SpanId
X-B3-ParentSpanId
X-B3-Sampled
```

There is also a compact single-header form:

```
b3: traceId-spanId-sampled
```

B3 was the de-facto standard before W3C Trace Context existed and you'll still encounter it in older services. For new systems, prefer W3C `traceparent`; when both must coexist, run a multi-propagator that understands B3 and W3C so traces stay connected during the transition.

## Storage

Zipkin supports several storage backends, each suited to a different scale: in-memory for development, MySQL for simple low-volume setups, Cassandra for high write throughput, and Elasticsearch when you also want search and ELK integration. For production, choose Cassandra or Elasticsearch — in-memory loses data on restart and MySQL won't keep up with real trace volume.

## Compared

| | Zipkin | Jaeger |
|---|---|---|
| Origin | Twitter | Uber |
| Lang | Java | Go |
| Headers | B3 | uber + W3C |
| UI | minimal | richer |
| Adoption | declining | growing |

## When Zipkin

Zipkin is a reasonable choice when you already have legacy services emitting B3 headers, when you're a Java shop with existing Brave instrumentation, or when your needs are simple enough that one self-contained binary beats a more complex stack.

## When Jaeger / Tempo

Reach for Jaeger or Tempo when you want a modern stack with a richer UI, more features, and active community momentum. Tempo in particular gives you S3-backed storage that is far cheaper at high span volume, and Jaeger offers a strong Kubernetes Operator.

## Migration

To migrate off Zipkin toward OpenTelemetry with Tempo or Jaeger, instrument your apps with the OTel SDK, run a multi-propagator that speaks both B3 and W3C so old and new services keep sharing traces, test that traces stay connected end to end, switch the backend over, and finally remove Zipkin once nothing depends on it. Doing it in this order lets you phase Zipkin out gradually instead of in a risky big-bang cutover.

## Status

Zipkin is still maintained and reliable for what it does, with many production deployments, but community mindshare has clearly shifted to Jaeger and Tempo. For new projects, standardize on OpenTelemetry instrumentation and pick Tempo or Jaeger as the backend rather than starting fresh on Zipkin.

## Common Mistakes

- Using in-memory storage in production, so all trace data is lost on restart
- Standing up a single-node backend with no HA for trace storage
- Sampling at 100% and overwhelming storage and the collector
- Mixing B3-only and W3C-only services without a multi-propagator, which silently splits traces
- Writing new code against the native Brave/Zipkin SDK instead of OpenTelemetry, locking yourself to one backend

## Best Practices

- Instrument with the OpenTelemetry SDK and export to Zipkin, so the backend stays swappable
- Run a multi-propagator (B3 + W3C) anywhere old and new services interoperate
- Use Cassandra or Elasticsearch for production storage with replication for HA
- Sample at the source (1–5% in prod) and keep errors/slow traces
- Treat Zipkin as a stepping stone — plan the path to OTel + Tempo/Jaeger for new work

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

**Junior**: "What is Zipkin?" — The original open-source distributed-tracing backend (Twitter, 2012), a Java system with a collector, pluggable storage, a query API, and a simple web UI, usually run as a single binary.

**Mid**: "Zipkin vs Jaeger — how do they compare?" — Both are OSS tracing backends with similar models; Zipkin (Java, B3 headers, minimal UI) came first but adoption is declining, while Jaeger (Go, richer UI, native OTLP/W3C support) has the community momentum, so new projects generally pick Jaeger or Tempo.

**Senior**: "You inherit services emitting B3 headers — how do you modernize tracing?" — Add OpenTelemetry instrumentation and run a multi-propagator so services accept and emit both B3 and W3C, keeping traces connected; then migrate the backend to Tempo or Jaeger and phase B3 out once everything speaks W3C.

**Staff**: "Justify keeping or replacing Zipkin in a platform decision." — Keep it only if it's a stable, low-risk fit for existing B3/Java services and replacing it isn't worth the churn; replace it when you want cheaper S3-backed storage (Tempo), unified OTel signals, or richer querying — and in either case standardize new instrumentation on OpenTelemetry so the backend stays a swappable detail.

## Next Topic

→ [T03 — Tempo](T03-Tempo.md)
