# L17/C01 — Three Pillars (and the Critique)

## Topics

- **T01 Metrics, Logs, Traces** — Canonical three pillars.
- **T02 Profiles as the 4th Pillar** — Continuous profiling joining the model.
- **T03 Continuous Observability** — Critique: pillars are silos; events + context > pillars.

## The Three Pillars

```
METRICS                LOGS                  TRACES
numeric, low card    text, high card        request flow
time-series           events                  causality
counters, gauges,    structured JSON         spans + parent links
histograms            per service/host        across services
```

### Metrics
- Aggregates over time
- Cheap to store
- Hard to slice by high-cardinality (user_id, request_id)
- Use: SLOs, dashboards, alerting

### Logs
- Detailed events
- Can carry context (request_id, user_id)
- Expensive at scale
- Use: investigation, audit

### Traces
- Causal graph of a request through services
- One trace = one request; many spans
- Sample heavily at high traffic
- Use: latency analysis, dependency mapping

## Adding Profiles

Continuous profiling captures CPU/memory hot paths over time:
- Tools: Pyroscope, Grafana Profiles, Parca, Polar Signals
- eBPF-based sampling (no app changes needed)
- Flame graphs at any point in time
- Use: optimize hot code, find regressions

## Adding Events

Deploys, config changes, scaling events — annotated on dashboards. Crucial for "why did this start happening?" investigation.

## The Critique (Honeycomb / Charity Majors)

> Pillars are a misleading abstraction. Real observability is asking arbitrary questions of system state. Pillars create silos that prevent correlation.

Better model:
- **Wide, structured events** with high cardinality
- Trace IDs link events
- Query across all dimensions

Honeycomb's product is built on this — one data type (events), arbitrary querying.

The truth is in between: pillars are operational reality (Prometheus, Loki, Tempo are separate); correlation via trace IDs ties them.

## Correlation in Practice

```
Alert: "p99 latency on /checkout > 1s for 5m"
   ↓
Grafana dashboard: latency, throughput, error rate
   ↓ click on latency exemplar (trace ID)
Tempo: trace shows database span took 800ms
   ↓ click "logs for this trace"
Loki: query logs filtered by trace_id, shows slow query log
   ↓
Pyroscope: profile during the time window shows DB driver hot
```

Each step jumps between pillars via trace_id. This is "observability that works."

## OpenTelemetry (OTel)

Unifies the three pillars under one SDK + protocol:
- One SDK per language (Go, Java, Python, Node, etc.)
- One protocol: OTLP (OpenTelemetry Protocol)
- One collector to receive, transform, export
- Backend-agnostic: send to Prometheus, Tempo, Loki, Datadog, etc.

Covered deeper in C06.

## Observability vs Monitoring

> Monitoring: known unknowns — predefined dashboards/alerts.
> Observability: unknown unknowns — ad-hoc query when surprise hits.

Mature systems do both. Monitoring catches known failures; observability investigates novel ones.

## SLI / SLO / SLA (Recap)

- **SLI** (Service Level Indicator) — a metric (e.g., success ratio)
- **SLO** (Service Level Objective) — a target (e.g., 99.9% over 30 days)
- **SLA** (Service Level Agreement) — contractual obligation (often less strict than SLO)

Covered deeper in C08.

## Interview Themes

- "Three pillars — and why some criticize them"
- "Add a fourth pillar: profiles — what does it solve?"
- "Correlate logs, metrics, traces — how?"
- "Observability vs monitoring"
- "OpenTelemetry — what's its role?"
