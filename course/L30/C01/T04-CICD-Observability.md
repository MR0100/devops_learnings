# L30/C01/T04 — Observability Stack

## Learning Objectives

- Add observability
- Demonstrate

## Stack

- Prometheus (metrics)
- Loki (logs)
- Tempo (traces)
- Grafana (UI)
- OTel Collector (gateway)

## Helm Install

```bash
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack
helm install loki grafana/loki-stack
helm install tempo grafana/tempo
helm install grafana grafana/grafana
helm install opentelemetry-collector open-telemetry/opentelemetry-collector
```

## App Instrumentation

```python
# Python
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

tracer = trace.get_tracer(__name__)
```

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
OTEL_SERVICE_NAME=my-app
```

## Dashboards

Pre-built:
- K8s overview
- Per-service RED metrics
- DB performance
- Cost (OpenCost)

## Alerts

```yaml
- alert: HighErrorRate
  expr: |
    sum(rate(http_requests_total{code=~"5.."}[5m]))
    /
    sum(rate(http_requests_total[5m]))
    > 0.05
  for: 10m
  labels: { severity: critical }
  annotations:
    summary: "High error rate"
    runbook: "https://..."
```

## Slack Integration

```yaml
# Alertmanager
receivers:
  - name: slack
    slack_configs:
      - api_url: ${SLACK_URL}
        channel: '#alerts'
```

## Trace Correlation

```python
import logging
from opentelemetry.instrumentation.logging import LoggingInstrumentor

LoggingInstrumentor().instrument(set_logging_format=True)
```

Logs include trace_id; Grafana links.

## Best Practices

- All 3 pillars
- Correlate via trace_id
- Standard dashboards
- Alerts SLO-based

## Common Mistakes

- Only metrics
- No correlation
- Too many alerts
- No runbooks

## Quick Refs

```
Metrics: Prometheus
Logs: Loki
Traces: Tempo
UI: Grafana
SDK: OTel
```

## Next Topic

→ [T05 — Security Gates](T05-CICD-Security.md)
