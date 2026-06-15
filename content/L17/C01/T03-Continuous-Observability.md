# L17/C01/T03 — Continuous Observability

## Learning Objectives

- Adopt observability culture
- Avoid common gaps

## Continuous Observability

Always-on production insight:
- Real-time
- High cardinality
- Ad-hoc queries
- All requests traced (sampled)

For: debug unknown unknowns.

## Vs Monitoring

| | Monitoring | Observability |
|---|---|---|
| Known | known unknowns | unknown unknowns |
| Setup | dashboards / alerts pre-defined | query at runtime |
| Cardinality | low | high |
| Cost focus | low | higher |

Both needed.

## Observability Maturity

```
L0: Logs to stdout
L1: Metrics + dashboards
L2: Distributed traces
L3: Continuous profiling
L4: Wide events; high cardinality
L5: Auto-instrumentation; query everywhere
```

Aim for L3-L4.

## Pillars Coordinated

```
Metric high p99 → query trace_id with high latency → drill into spans → flame graph
```

For: incident workflow.

## Auto-Instrumentation

OpenTelemetry SDK with auto-instrumentation:
- HTTP frameworks
- DB clients
- Queue clients

```yaml
OTEL_TRACES_EXPORTER: otlp
OTEL_RESOURCE_ATTRIBUTES: service.name=myapp
```

For: minimal code changes.

## Tagging / Labeling

Every event:
- service
- version
- env
- region
- (request-specific: user, tenant, ...)

For: filter/group.

## High Cardinality

For deep observability:
- Per-user metrics OK in events
- Don't aggregate prematurely
- Sample but capture details

Tools: Honeycomb, Datadog APM.

## Distributed Tracing

End-to-end across services:
```
Service A → Service B → Service C → DB
   trace_id propagated
```

For: cross-service latency.

## Correlation

Use trace_id:
```json
{"ts": "...", "level": "error", "trace_id": "abc", "msg": "DB failed"}
```

In Grafana / Datadog: click metric spike → traces → logs.

## Service Maps

Auto-generated topology:
- Services
- Connections
- Latency edges

For: visualize.

## Anomaly Detection

ML on metrics:
- Sudden change
- Pattern breaks
- Multi-dim outliers

Tools: Datadog, Anomalo.

## Alerts vs Investigations

### Alerts
Pre-defined thresholds.
For: react.

### Investigations
Ad-hoc; explore.
For: understand.

Need both.

## SLO-Based Observability

Define SLOs:
- 99.9% availability
- p99 latency < 500ms

Burn rate alerts:
- "Burning error budget 14x → page"

(See L17/C08.)

## Honeycomb Approach

- Wide events
- Sampling
- Ad-hoc queries
- BubbleUp (auto-explore)

For: high-cardinality observability.

## Datadog Approach

- All pillars in one
- APM, RUM, Logs, Metrics
- Service maps
- Cost: $$$

## Self-Hosted

- Prometheus + Grafana
- Loki for logs
- Tempo for traces
- Pyroscope for profiles

OSS stack.

## Cost Management

- Sample traces (1-5%)
- Drop debug logs (sample)
- Retain hot data short (7-30 days)
- Archive cold (S3)
- Cardinality limits

## Time-Series DB

Prometheus: pull-based, sharded.
VictoriaMetrics: drop-in faster.
M3DB: Uber-built.
InfluxDB: push or pull.

For high scale: VictoriaMetrics / M3.

## Tracing Backend

- Jaeger
- Tempo (Grafana)
- X-Ray (AWS)
- Trace (GCP)

OSS: Tempo (S3 backed).

## Log Backend

- Loki (Grafana; cheap)
- ELK (Elasticsearch)
- Splunk (commercial)

OSS: Loki for cost.

## Wide Events Storage

- Honeycomb (commercial)
- ClickHouse (OSS)
- Druid

## Dev Experience

```bash
# Local dev with OTel
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 ./myapp
```

Send to local Jaeger / Tempo.

For: dev observability.

## Real-User Monitoring (RUM)

Browser metrics:
- Page load time
- Interactions
- JS errors

Tools: Datadog RUM, Sentry, Sentry Performance.

## Synthetic Monitoring

Scripted user flows:
```bash
# k6 / Cypress / Datadog
```

Run continuously; alert on failure.

For: detect external-facing issues.

## SLO Dashboard

Per service:
- Current SLO compliance
- Error budget remaining
- Burn rate

For: business view.

## On-Call Tooling

- PagerDuty
- Opsgenie
- VictorOps (Splunk)
- FireHydrant (incident mgmt)

For: respond + manage.

## Best Practices

- All three pillars instrumented
- Correlation via trace_id
- Sample traces (cost)
- Wide events for high cardinality
- SLO-driven alerts
- Dashboards per service
- On-call runbook tied to alerts

## Common Mistakes

- One pillar only
- No correlation
- All traces (cost)
- Low-cardinality only
- No SLOs
- Alert noise

## Cultural

Observability requires:
- Dev instruments
- SRE consumes
- Shared dashboards
- Postmortems use data

For: org-wide adoption.

## Cost vs Insight

More data = more cost + more insight.

Balance:
- Sample wisely
- Retain hot short
- Archive long
- Tag for queries

## Quick Refs

```
Pillars: metrics, logs, traces, profiles
Tools:   Prom, Loki/ELK, Tempo/Jaeger, Pyroscope
Or:      Datadog, Honeycomb, New Relic
Correlation: trace_id
SLO:     defined + burn alerts
```

## Interview Prep

**Mid**: "Continuous observability."

**Senior**: "Observability stack."

**Staff**: "Observability strategy."

## Next Topic

→ Move to [L17/C02 — Prometheus](../C02/README.md)
