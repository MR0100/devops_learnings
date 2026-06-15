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

## Why Observability Ships With the App

The point of this layer in the capstone is to prove you build systems you can
*operate*, not just deploy. Anyone can `helm install` Grafana — the signal a
reviewer looks for is whether the **three pillars correlate**: from a metric
spike you can reach the trace, and from the trace you can reach the logs for
that exact request. That click-path is what an interviewer means by
"production-grade observability." (The dedicated correlation deep-dive is C03/T04.)

### Rationale & Trade-offs

- **OTel SDK over vendor agents** — one instrumentation standard, swap backends
  later without touching app code. Trade-off: a bit more setup than a turnkey
  agent.
- **Loki/Tempo over a heavyweight ELK + Jaeger-on-Cassandra** — both store to
  cheap object storage and index minimally, which keeps the capstone's run rate
  near zero. Trade-off: you query logs/traces by label/ID, not arbitrary
  full-text, so label discipline matters.
- **SLO-based alerts over static thresholds** — page on user-visible symptoms
  (error budget burn) instead of CPU%, so you get fewer, more meaningful pages.

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

## Acceptance Criteria

- The sample app exposes `/metrics`, emits OTel traces, and logs JSON with a
  `trace_id`
- Grafana shows RED metrics (rate/errors/duration) per service
- A log line's `trace_id` links to its trace; the trace links back to its logs
- An injected error burns the SLO and fires exactly one meaningful alert (to
  Slack), with a runbook link in the annotation

## Quick Refs

```
Metrics: Prometheus    Logs: Loki    Traces: Tempo
UI: Grafana            SDK: OTel
Glue: trace_id in logs + exemplars on histograms
Alert on SLO burn, not raw thresholds; runbook link in every alert
```

## Interview Prep

**Junior**: "What are the three pillars of observability?" — Metrics (numbers
over time, e.g. request rate and latency), logs (discrete event records), and
traces (the path of a single request across services). Grafana is the UI that
ties them together.

**Mid**: "How do you correlate a metric spike with the actual slow request?" — I
instrument with the OTel SDK so the app attaches the active `trace_id` as an
exemplar on its latency histogram and puts the same `trace_id` in its logs. In
Grafana, an exemplar on the latency panel links straight to the trace in Tempo,
and the trace links to the request's logs in Loki. So a spike is one or two
clicks from the exact request and its logs.

**Senior**: "Why SLO-based alerting instead of threshold alerts, and how do you
avoid alert fatigue?" — Threshold alerts (CPU > 80%) fire on conditions that
often aren't user-visible, so they're noisy and get ignored. SLO/burn-rate
alerts fire on the symptom that matters — error budget being consumed too fast —
which means fewer, higher-signal pages. Multi-window burn rate (fast + slow
windows) catches both acute outages and slow erosion while suppressing flapping.
Every alert links to a runbook, or it's not ready to page anyone.

**Staff**: "An app team says observability is 'the platform's job.' How do you
push back?" — Correlation only works if the app participates — propagating trace
context, emitting `trace_id` in logs, exposing meaningful metrics. The platform
can *provide* the SDK config, dashboards-as-code, and default SLOs as a golden
path (the IDP capstone scaffolds exactly this), but it can't retrofit
instrumentation the app never emits. So the framing is: the platform makes the
right thing the easy thing — instrumentation comes free in the service template
— and in exchange teams own the signals their service produces. That's the
shared-responsibility model that actually scales past a handful of services.

## Next Topic

→ [T05 — Security Gates](T05-CICD-Security.md)
