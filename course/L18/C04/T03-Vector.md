# L18/C04/T03 — Vector (Rust-Based)

## Learning Objectives

- Use Vector
- Compare to alternatives

## Vector

Datadog (originally Timber):
- Rust
- Logs + metrics + traces
- High performance
- VRL (Vector Remap Language)

## Install

```bash
helm install vector vector/vector
```

```bash
curl https://sh.vector.dev | sh
```

## Config

```toml
[sources.app_logs]
type = "file"
include = ["/var/log/app/*.log"]

[transforms.parse]
type = "remap"
inputs = ["app_logs"]
source = '''
  . = parse_json!(.message)
  .timestamp = parse_timestamp!(.ts, "%+")
'''

[sinks.es]
type = "elasticsearch"
inputs = ["parse"]
endpoints = ["http://elasticsearch:9200"]
mode = "bulk"
```

## VRL

Modern transformation:
```
. = parse_json!(.message)
.cluster = "prod"
del(.password)
.level = downcase(.level)
```

For: data manipulation.

## Sources

- File
- Kafka
- HTTP
- syslog
- journald
- Docker logs
- K8s

## Transforms

- remap (VRL)
- filter
- aggregate
- dedupe
- throttle
- route
- reduce

## Sinks

- Elasticsearch
- Loki
- Splunk
- Datadog
- AWS S3 / Kinesis / CloudWatch
- Kafka
- HTTP
- many more

## Performance

Benchmarks:
- 10× faster than Fluentd
- 2-5× faster than Fluent Bit

Rust: no GC, efficient.

## Memory

- 50-100 MB typical
- Configurable buffer

## Vector Roles

### Agent
Edge collection (sidecars).

### Aggregator
Central processing.

```toml
[sources.agent_input]
type = "vector"   # receives from other Vector
```

## Buffering

```toml
[sinks.es]
buffer.type = "disk"
buffer.max_size = "10G"
```

For: durability.

## Reload

```bash
vector --config vector.toml --watch-config
```

Hot reload.

## OTel

```toml
[sources.otel]
type = "opentelemetry"
mode = "grpc"
```

Receives OTLP.

## When Vector

- Multi-source/sink
- Performance critical
- VRL friendly
- Cost (replaces Logstash)

## When Not

- Existing Fluent investment
- Smaller ecosystem
- Less plugins (vs Fluentd)

## Compared

| | Vector | Fluent Bit | Fluentd | Logstash |
|---|---|---|---|---|
| Lang | Rust | C | Ruby | JRuby |
| Speed | very fast | fast | medium | slow |
| Memory | low | very low | medium | high |
| Transforms | VRL (powerful) | filters | filters | rich |
| Plugins | growing | many | many | many |

## Multi-Output

```toml
[sinks.loki]
inputs = ["parse"]
type = "loki"
...

[sinks.s3_backup]
inputs = ["parse"]
type = "aws_s3"
...
```

Send to both.

## Datadog Acquisition

Vector now Datadog's:
- Continues OSS
- Datadog uses internally

For: stable backing.

## VRL Examples

### Parse
```
. = parse_json!(.message)
```

### Add field
```
.hostname = "node-1"
```

### Drop sensitive
```
del(.password)
del(.api_key)
```

### Conditional
```
if .status == 500 {
  .alert = true
}
```

### Type conversion
```
.duration = to_int!(.duration_str)
```

## Tests

```toml
[[tests]]
name = "test"
inputs = [...]
outputs = [...]
```

For: validate.

## Best Practices

- Disk buffer
- Multi-sink
- VRL for clean transforms
- Tests for pipelines
- Monitor (Vector exposes metrics)

## Common Mistakes

- Memory buffer in prod
- Complex VRL (hard to read)
- No tests
- Single sink (no failover)

## Quick Refs

```toml
[sources.X]
type = "..."

[transforms.Y]
type = "remap"
inputs = ["X"]
source = '...'

[sinks.Z]
type = "..."
inputs = ["Y"]
```

```bash
vector --config vector.toml
vector validate vector.toml
```

## Interview Prep

**Mid**: "What's Vector."

**Senior**: "Vector vs Fluent."

**Staff**: "Log pipeline choice."

## Next Topic

→ [T04 — OpenTelemetry Collector for Logs](T04-OTel-Collector-Logs.md)
