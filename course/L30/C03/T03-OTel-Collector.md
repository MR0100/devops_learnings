# L30/C03/T03 — OTel Collector Fleet

## Learning Objectives

- Deploy OTel
- Unified pipeline

## Topology

```
Apps → OTel Agent (DaemonSet) → OTel Gateway (Deployment)
                                       ↓
                          Mimir / Loki / Tempo
```

## Agent

Per-node:
```yaml
receivers:
  otlp:
    protocols:
      grpc:
      http:
  filelog:
    include: [/var/log/containers/*.log]

processors:
  batch:
  memory_limiter:
  k8sattributes:

exporters:
  otlp:
    endpoint: otel-gateway:4317

service:
  pipelines:
    traces: { receivers: [otlp], processors: [batch], exporters: [otlp] }
    metrics: { receivers: [otlp], processors: [batch], exporters: [otlp] }
    logs: { receivers: [filelog], processors: [batch], exporters: [otlp] }
```

## Gateway

Central:
```yaml
receivers:
  otlp: ...

processors:
  batch:
  tail_sampling:
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: sample
        type: probabilistic
        probabilistic: { sampling_percentage: 10 }

exporters:
  prometheus: { endpoint: 0.0.0.0:8889 }
  loki: { endpoint: http://loki:3100/loki/api/v1/push }
  otlp/tempo: { endpoint: tempo:4317 }
```

## App Instrumentation

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-agent:4317
OTEL_SERVICE_NAME=my-app
```

## Auto-Instrumentation

```bash
opentelemetry-instrument python app.py
```

## Multi-Cluster

Per cluster: agent + gateway.
Central observability: receive from all gateways.

## Best Practices

- Agent + Gateway pattern
- Tail sampling
- Resource attributes
- Multi-backend exporters

## Common Mistakes

- Direct to backend (no buffer)
- 100% sample (cost)
- No memory limiter (OOM)

## Quick Refs

```yaml
receivers / processors / exporters / service
```

```bash
helm install otel-collector open-telemetry/opentelemetry-collector
```

## Next Topic

→ Move to [L30/C04 — Project 4: Internal Developer Platform](../C04/README.md)
