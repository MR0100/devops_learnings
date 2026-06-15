# L17 — Monitoring & Observability

## Overview

You can't operate what you can't see. This lecture covers the observability stack used at every modern company: Prometheus, Grafana, OpenTelemetry, and the SLO discipline.

**8 chapters, 28 topics.**

## Chapter Map

### [C01](C01/) — Three Pillars (and the Critique)
- T01 Metrics, Logs, Traces
- T02 Profiles as the 4th Pillar
- T03 Continuous Observability

### [C02](C02/) — Prometheus
- T01 Architecture (Server, Pushgateway, Alertmanager)
- T02 Service Discovery
- T03 Scrape Configs & Relabeling
- T04 Storage (TSDB, WAL)
- T05 Federation & Remote Write
- T06 Thanos, Cortex, Mimir for Long-Term Storage

### [C03](C03/) — PromQL
- T01 Instant vs Range Vectors
- T02 Aggregation & Functions
- T03 Recording Rules
- T04 Alerting Rules

### [C04](C04/) — Grafana
- T01 Datasources, Dashboards, Panels
- T02 Variables & Templating
- T03 Provisioning Dashboards as Code
- T04 Grafana Loki, Tempo, Mimir

### [C05](C05/) — Alertmanager
- T01 Routing Tree
- T02 Silences, Inhibitions
- T03 Receivers (PagerDuty, Slack, OpsGenie)
- T04 Alert Hygiene

### [C06](C06/) — OpenTelemetry
- T01 OTel Architecture (SDK, Collector, Exporters)
- T02 Semantic Conventions
- T03 Auto-Instrumentation
- T04 OTLP Protocol

### [C07](C07/) — Commercial APM
- T01 Datadog
- T02 New Relic
- T03 Dynatrace
- T04 Honeycomb
- T05 Splunk Observability

### [C08](C08/) — SLI, SLO, Error Budgets
- T01 Defining Good SLIs
- T02 SLO Math & Rolling Windows
- T03 Burn Rate Alerts
- T04 Error Budget Policies

## Three Pillars (& Beyond)

```
Metrics                Logs                  Traces
(numeric, low card)   (text, high cardin.)  (request flow)

      Profiles
      (CPU/memory hot paths)

      Events
      (deploy markers)

      → All correlated by trace_id / span_id
```

## Prometheus Architecture

```
[Targets] ← scrape →  [Prometheus Server]
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          [Alerting]    [Storage      [Grafana]
          [Rules]       (TSDB)]       (query)
              │
              ▼
        [Alertmanager] → PagerDuty, Slack
```

## SLO Mental Model

```
SLI: a metric (e.g., success ratio of HTTP /api/v1/payments)
SLO: a target for the SLI (e.g., 99.9% over 30 days)
Error budget: 1 - SLO = 0.1% of requests can fail/month
Burn rate: how fast you're using budget
```

A team with SLOs and an error budget *policy* makes data-driven tradeoffs between speed and reliability.

## PromQL Essentials

```promql
# Request rate per service
sum by (service) (rate(http_requests_total[5m]))

# 95th percentile latency
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# Error ratio
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m]))

# Multi-window burn rate (long + short)
(slo_error_budget_remaining < 0.5) and (rate(errors[1h]) > 14 * rate(errors[5m]))
```

## Common Alerts (Anti-Patterns)

- Threshold alerts ("CPU > 80%") → page on cause not symptom
- "Disk space < 10%" → too late; alert at trend (will fill in 4 hours)
- Per-component alerts → cascade noise; use SLO burn instead

## Recommended Reading

- *Site Reliability Engineering* — Google (free online)
- *The SRE Workbook* — Chapter 4 (SLOs in practice)
- *Observability Engineering* — Charity Majors et al.
- Prometheus docs

## Interview Themes

- "Three pillars — and limits"
- "Design alerts based on SLO burn rate"
- "Where does OpenTelemetry fit?"
- "Compare Prometheus and Datadog"
- "How do you scale Prometheus to 100M time series?"

## Next

→ [L18 — Logging & Distributed Tracing](../L18/README.md)
