# L17/C06/T04 — OTLP Protocol

## Learning Objectives

- Understand OTLP
- Choose transport

## OTLP

OpenTelemetry Protocol:
- Wire format
- gRPC or HTTP
- Protobuf
- Three signals: traces, metrics, logs

## Transports

### gRPC (port 4317)
- Binary protobuf
- Streaming
- Efficient
- Default for Collector

### HTTP/Protobuf (port 4318)
- Protobuf payload over HTTP
- Easier through proxies
- Stateless

### HTTP/JSON (port 4318)
- Less efficient
- Debuggable
- Not preferred

## Schema

```protobuf
message TraceData {
  repeated ResourceSpans resource_spans = 1;
}

message ResourceSpans {
  Resource resource = 1;
  repeated ScopeSpans scope_spans = 2;
}

message Span {
  bytes trace_id = 1;
  bytes span_id = 2;
  string name = 4;
  fixed64 start_time_unix_nano = 8;
  fixed64 end_time_unix_nano = 9;
  repeated KeyValue attributes = 10;
  ...
}
```

For: efficient binary.

## Endpoints

```
http://collector:4317   # gRPC
http://collector:4318/v1/traces
http://collector:4318/v1/metrics
http://collector:4318/v1/logs
```

## TLS

```
https://collector:4317   # gRPC + TLS
https://collector:4318/v1/traces
```

For: production.

## Auth

### Header
```
Authorization: Bearer TOKEN
```

### mTLS
Cert-based.

### API Key
```
X-API-Key: KEY
```

(Vendor-specific.)

## Configuration

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://collector:4317
OTEL_EXPORTER_OTLP_HEADERS=Authorization=Bearer%20TOKEN
OTEL_EXPORTER_OTLP_PROTOCOL=grpc   # or http/protobuf, http/json
OTEL_EXPORTER_OTLP_COMPRESSION=gzip
OTEL_EXPORTER_OTLP_TIMEOUT=10000   # 10s
OTEL_EXPORTER_OTLP_CERTIFICATE=/path/to/ca.crt
```

## Per-Signal

```bash
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://traces:4317
OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=https://metrics:4317
OTEL_EXPORTER_OTLP_LOGS_ENDPOINT=https://logs:4317
```

For: different backends.

## Performance

OTLP:
- ~10-50% smaller than JSON
- gRPC streaming reduces overhead
- Compression (gzip)

For high-volume: gRPC.

## Compression

```bash
OTEL_EXPORTER_OTLP_COMPRESSION=gzip
```

For: bandwidth savings.

## Batch / Buffering

SDK batches:
- Configurable size + interval
- Memory pressure handling
- Retry on failure

## Backpressure

If collector slow:
- SDK queue fills
- New spans dropped
- Memory limited

Tune queue + collector capacity.

## Multi-Backend

```yaml
# Collector
exporters:
  otlp/jaeger: { endpoint: jaeger:4317 }
  otlp/datadog: { endpoint: datadog.com:4317, headers: {api-key: ...} }

service:
  pipelines:
    traces:
      exporters: [otlp/jaeger, otlp/datadog]
```

Send to both.

## Encoding

Protobuf default. Compact.

Alternative: JSON (debug only).

## Compatibility

OTLP versions:
- Currently 1.x stable
- Backward compatible

## Common Backends

- Tempo (Grafana)
- Jaeger
- Datadog
- New Relic
- Honeycomb
- AWS X-Ray (via OTLP-X-Ray bridge)
- Google Cloud Trace
- Azure Monitor

All accept OTLP (directly or via exporter).

## Direct vs Collector

### Direct (App → Backend)
```
App SDK → Backend OTLP endpoint
```

Simpler; less ops.

### Via Collector
```
App SDK → Collector → Backend
```

- Buffering
- Processors
- Multi-backend
- Sampling decisions

For prod: Collector.

## Sampling Decision

### Head Sampling
SDK decides at start.

### Tail Sampling
Collector decides at end (sees full trace).

Better for: keep error traces, drop normal.

## Receiver in Collector

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
        tls:
          cert_file: cert.pem
          key_file: key.pem
      http:
        endpoint: 0.0.0.0:4318
```

## Best Practices

- gRPC for high-volume
- TLS in prod
- Compression on
- Batch processor
- Memory limiter
- Multi-backend via Collector

## Common Mistakes

- HTTP/JSON in prod (large)
- No TLS
- No batching (overhead)
- Wrong endpoint port

## Debugging

```bash
# Logging exporter
exporters:
  logging:
    verbosity: detailed

# tcpdump / wireshark
# OR
otel-cli (CLI for sending test OTLP)
```

## otel-cli

```bash
# Send test
otel-cli span --name "test" --kind server
```

For: testing pipelines.

## Quick Refs

```
OTLP gRPC:   4317
OTLP HTTP:   4318

Endpoints:
  /v1/traces
  /v1/metrics
  /v1/logs

Env:
  OTEL_EXPORTER_OTLP_ENDPOINT
  OTEL_EXPORTER_OTLP_PROTOCOL
  OTEL_EXPORTER_OTLP_HEADERS
  OTEL_EXPORTER_OTLP_COMPRESSION
```

## Interview Prep

**Mid**: "OTLP."

**Senior**: "Transport choice."

**Staff**: "Telemetry pipeline."

## Next Topic

→ Move to [L17/C07 — Commercial APM](../C07/README.md)
