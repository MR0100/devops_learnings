# L18/C04 — Collectors & Shippers

## Topics

- **T01 Fluentd** — Ruby+C, the original
- **T02 Fluent Bit** — Lightweight C
- **T03 Vector** — Modern Rust
- **T04 OpenTelemetry Collector for Logs** — Unified pipeline

## Fluentd

CNCF-graduated; mature; ~50 MB memory; plugin ecosystem in Ruby.

```ruby
<source>
  @type tail
  path /var/log/containers/*.log
  pos_file /var/log/fluentd-containers.pos
  tag kubernetes.*
  read_from_head true
  <parse>
    @type json
    time_key time
    time_format %Y-%m-%dT%H:%M:%S.%NZ
  </parse>
</source>

<filter kubernetes.**>
  @type kubernetes_metadata
</filter>

<match **>
  @type loki
  url http://loki:3100
  flush_interval 5s
  <label>
    namespace $.kubernetes.namespace_name
    pod $.kubernetes.pod_name
  </label>
</match>
```

## Fluent Bit

Sister project: C, ~1 MB memory, super-light. Almost always the right choice today.

```ini
[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            cri
    Tag               kube.*

[FILTER]
    Name                kubernetes
    Match               kube.*
    Merge_Log           On
    K8S-Logging.Parser  On
    K8S-Logging.Exclude On

[FILTER]
    Name    modify
    Match   *
    Add     cluster prod-us-east-1

[OUTPUT]
    Name   loki
    Match  *
    Url    http://loki:3100/loki/api/v1/push
    Labels job=fluent-bit, namespace=$kubernetes['namespace_name']
```

### Why Fluent Bit
- Tiny footprint (DaemonSet on every node)
- Performance: 10K+ events/sec/instance
- Built-in K8s metadata enrichment
- Many outputs (Loki, Elastic, S3, Splunk, Datadog, OTLP)

### Buffering
- Memory + disk
- Backpressure to source on backend slow
- Configurable per-output retry

## Vector (Datadog/Vector)

Rust-based, modern. Excellent performance + observability.

```toml
[sources.kubernetes_logs]
type = "kubernetes_logs"

[transforms.add_meta]
type = "remap"
inputs = ["kubernetes_logs"]
source = '''
.cluster = "prod-us-east-1"
.team = .kubernetes.pod_labels.team
'''

[transforms.parse_json]
type = "remap"
inputs = ["add_meta"]
source = '''
if exists(.message) {
  parsed, err = parse_json(.message)
  if err == null { . = merge(., parsed) }
}
'''

[sinks.loki]
type = "loki"
inputs = ["parse_json"]
endpoint = "http://loki:3100"
labels.namespace = "{{ kubernetes.namespace_name }}"
labels.pod = "{{ kubernetes.pod_name }}"
encoding.codec = "json"
```

### Why Vector
- Strong type system (VRL — Vector Remap Language)
- Routing, transforms, sinks all first-class
- Memory + disk buffer
- Excellent observability (self-metrics)
- Fast (Rust)

## OTel Collector for Logs

Same Collector that does traces + metrics:
```yaml
receivers:
  filelog:
    include: [/var/log/containers/*.log]
    operators:
      - type: container
      - type: json_parser

processors:
  resource:
    attributes:
      - key: cluster
        value: prod-us-east-1
        action: insert
  batch: {}

exporters:
  loki:
    endpoint: http://loki:3100/loki/api/v1/push

service:
  pipelines:
    logs:
      receivers: [filelog]
      processors: [resource, batch]
      exporters: [loki]
```

Use when you're standardizing on OTel for all telemetry.

## Choosing

| | Fluentd | Fluent Bit | Vector | OTel Collector |
|---|---|---|---|---|
| Memory | ~50 MB | ~1 MB | ~10 MB | ~50 MB |
| Performance | Medium | High | High | Medium-High |
| Language | Ruby | C | Rust | Go |
| Ecosystem | Large | Growing | Growing | OTel-aligned |
| Best for | Heritage | DaemonSet log collection | Hybrid pipelines | OTel adoption |

Recommendation: Fluent Bit for node DaemonSet. Vector for central pipeline. OTel Collector when standardizing.

## Patterns

### Node DaemonSet + Central Gateway

```
Node-level Fluent Bit (DaemonSet) → tails container logs
   ↓ ships to ↓
Central Vector (Deployment) → enriches, routes
   ↓
Loki / Datadog / S3 (multi-route)
```

Node DaemonSet keeps logic light per node. Central does heavy lifting.

### Backpressure Handling
- Local buffer (disk or memory)
- Output retries with backoff
- DLQ to file or alternate sink
- Drop policy (last resort)

## Common Issues

- **Multi-line logs** (Java stack traces) — configure multiline parser
- **Permission** on /var/log/containers (symlinks to /var/log/pods)
- **Log rotation** missed events (read_from_head + position file)
- **High CPU during JSON parse** at high rate — sample or skip parse for some streams

## Interview Themes

- "Compare Fluentd, Fluent Bit, Vector, OTel Collector"
- "Multi-line log handling"
- "Backpressure — how do shippers respond?"
- "DaemonSet vs sidecar pattern"
