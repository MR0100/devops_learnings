# L17/C07 — Commercial APM

## Topics

- **T01 Datadog** — Most popular APM
- **T02 New Relic** — Veteran APM
- **T03 Dynatrace** — Enterprise-focused
- **T04 Honeycomb** — Observability-first, high-cardinality
- **T05 Splunk Observability** — Splunk-acquired SignalFx

## Why Commercial APM

- Polished UI vs DIY Prometheus/Grafana
- Less ops burden than self-hosted
- Cross-pillar correlation (metrics, logs, traces, profiles unified)
- AI-driven anomaly detection (varies by vendor)
- SaaS (no infra)

Trade-off: cost and lock-in.

## Datadog

- All-in-one: APM, metrics, logs, traces, RUM, profiling, security
- Massive integration catalog
- Best-in-class UX
- Pay for: hosts, custom metrics, log ingest, trace volume, RUM events
- Cost spirals: easy to hit $1M+/year for medium companies

### When Datadog
- Want one tool that does most things
- Have budget
- Don't want to operate observability infra

### When Not
- Cost-sensitive
- OSS / cloud-native ethos
- Want full data ownership

## New Relic

- Pioneer of APM (founded 2008)
- Moved to "all-you-can-eat" pricing (per ingested GB + per user)
- Strong APM for Java/.NET/Ruby
- Less hip than Datadog; arguably better for traditional enterprise

## Dynatrace

- AI-driven causality (Davis AI)
- Smartscape (auto-discovered topology)
- Strong for monolith-heavy enterprises
- "Set it and forget it" promise

## Honeycomb

- Built around the observability critique: one data type (events), high cardinality, ad-hoc queries
- BubbleUp (auto-finds anomalies)
- Bee+SLO product
- More expensive per unit but powerful

### When Honeycomb
- Need to ask arbitrary questions
- High-cardinality dimensions (user IDs, request IDs)
- Mature observability culture

## Splunk Observability

- Acquired SignalFx (real-time metrics + traces)
- Streaming analytics (sub-second alerting)
- Pairs with Splunk Enterprise (logs)
- Enterprise pricing

## Choosing

| Need | Pick |
|---|---|
| All-in-one + budget | Datadog |
| Java-heavy traditional enterprise | New Relic / Dynatrace |
| High-cardinality investigations | Honeycomb |
| Existing Splunk shop | Splunk |
| OSS / cost-sensitive | Prometheus + Loki + Tempo (LGTM) |

## Cost Management

Common cost traps:
- Custom metrics with high-cardinality tags
- Log ingest from chatty apps
- RUM events from high-traffic frontends
- Trace volume without sampling

Mitigations:
- Sample
- Drop noisy logs at source
- Limit label cardinality
- Monthly cost reviews
- Per-team budgets

## OTel + Commercial

OpenTelemetry → Datadog/New Relic/Honeycomb all support OTLP as input.

Strategy:
1. Instrument with OTel SDK (vendor-neutral)
2. Send to Datadog (or alternative)
3. If costs balloon: switch to OSS or another vendor (no app changes)

## Interview Themes

- "Datadog vs Prometheus/Grafana"
- "Honeycomb's pitch — observability vs monitoring"
- "Cost management on commercial APM"
- "Why OTel makes vendor switching easier"
