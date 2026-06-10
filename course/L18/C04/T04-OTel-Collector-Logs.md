# L18/C04/T04 — OpenTelemetry Collector for Logs

## Learning Objectives

- Use OTel Collector for logs
- Unify pipeline

## OTel Collector

Already covered for traces/metrics. Now: logs.

## Why

- Unified pipeline (logs + traces + metrics)
- Vendor-neutral
- Rich processors

## Receivers

- otlp (logs via OTLP)
- filelog (read files)
- syslog
- kafka
- journald

## filelog

```yaml
receivers:
  filelog:
    include:
      - /var/log/containers/*.log
    operators:
      - type: container
      - type: regex_parser
        regex: '^(?P<time>\S+) (?P<level>\S+) (?P<message>.*)$'
```

## Processors

- batch
- attributes (add/remove)
- resource
- filter
- transform
- k8sattributes

## Transform

```yaml
processors:
  transform:
    log_statements:
      - context: log
        statements:
          - set(severity_text, "ERROR") where body matches "exception"
          - keep_keys(attributes, ["k8s.pod.name", "service.name"])
```

OTTL (transformation language).

## k8sattributes

```yaml
processors:
  k8sattributes:
    auth_type: serviceAccount
    passthrough: false
    extract:
      metadata:
        - k8s.pod.name
        - k8s.namespace.name
        - k8s.deployment.name
```

Auto-decorate.

## Exporters

```yaml
exporters:
  loki:
    endpoint: http://loki:3100/loki/api/v1/push
  elasticsearch:
    endpoints: ["http://es:9200"]
  splunk_hec:
    endpoint: ...
  datadog:
    api: { key: $DD_API_KEY }
```

## Pipeline

```yaml
service:
  pipelines:
    logs:
      receivers: [filelog]
      processors: [k8sattributes, batch]
      exporters: [loki]
```

## Tail Sampling for Logs

Decide based on context:
```yaml
processors:
  filter:
    logs:
      include:
        match_type: strict
        severity_number:
          min: 9   # WARN+
```

## Agent vs Gateway

Same as for traces:
- Agent (per-host)
- Gateway (central)

For: same architecture.

## Compared

| | OTel Collector | Fluent Bit | Vector |
|---|---|---|---|
| Logs | yes | yes | yes |
| Traces | yes | partial | yes |
| Metrics | yes | yes | yes |
| Lang | Go | C | Rust |
| OTel-native | yes | partial | yes |

For: unified OTel pipeline: OTel Collector.
For: pure log volume: Vector / Fluent Bit.

## Buffering

```yaml
exporters:
  loki:
    sending_queue:
      enabled: true
      num_consumers: 10
      queue_size: 5000
    retry_on_failure:
      enabled: true
      initial_interval: 5s
      max_elapsed_time: 5m
```

## Compression

```yaml
exporters:
  otlp:
    compression: gzip
```

## OTel Logs SDK

App emits logs via OTel:
```python
from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

provider = LoggerProvider()
provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
```

For: native instrumentation.

## Future Direction

OTel Logs is GA. Adoption growing.

Eventually: replace per-vendor log SDKs.

## Best Practices

- OTel Collector for unified
- Agent + Gateway pattern
- k8sattributes processor (K8s)
- Batch processor (throughput)
- Multiple exporters (fallback)

## Common Mistakes

- Skip OTel Collector
- No buffering
- Wrong receiver (filelog vs otlp)
- Heavy transforms (slow)

## Quick Refs

```yaml
receivers:
  filelog / otlp / syslog / journald

processors:
  batch / k8sattributes / transform / filter

exporters:
  loki / elasticsearch / otlp / datadog

service:
  pipelines:
    logs: { receivers, processors, exporters }
```

## Interview Prep

**Mid**: "OTel Collector for logs."

**Senior**: "Unified pipeline."

**Staff**: "OTel adoption."

## Next Topic

→ Move to [L18/C05 — Tracing Fundamentals](../C05/README.md)
