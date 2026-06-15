# L17/C07/T02 — New Relic

## Learning Objectives

- Use New Relic
- Compare to alternatives

## New Relic

One of the original APM vendors (founded 2008). Pioneered code-level
application monitoring before "observability" was a word. Today it is a
unified telemetry platform:

- Metrics, events, logs, and traces — internally stored as one data model
  ("MELT") in a single columnar database (NRDB).
- **NRQL** (New Relic Query Language) — SQL-like, runs across every data
  type, powers dashboards, alerts, and ad-hoc investigation.
- Consumption pricing: pay per **GB ingested** + per **full-platform user**.
  Generous free tier (100 GB/mo ingest, 1 full user).
- Historically strongest on the JVM and .NET runtimes; broad agent coverage.

The mental model that distinguishes New Relic: **everything is an event you
can query with NRQL.** A metric, a span, a log line, and a custom business
event all land in NRDB and are queryable with the same language. That makes
New Relic feel less like a fixed set of dashboards and more like a queryable
telemetry warehouse.

## Install Agent

```bash
NEW_RELIC_API_KEY=KEY \
NEW_RELIC_ACCOUNT_ID=ACCT \
bash -c "$(curl -L https://download.newrelic.com/install/newrelic-cli/scripts/install.sh)"
```

Or K8s Helm.

## APM

Auto-instrumented:
- Java, .NET, Node, Python, Ruby, Go, PHP

```bash
pip install newrelic
NEW_RELIC_LICENSE_KEY=KEY newrelic-admin run-program python app.py
```

## NRQL

The query language for everything in NRDB. SQL-like, with `FACET` (group
by), `TIMESERIES` (turn a query into a graph), and `SINCE`/`UNTIL` windows.

```
-- Throughput
SELECT count(*) FROM Transaction WHERE appName = 'api' SINCE 1 hour ago

-- Latency by endpoint
SELECT average(duration) FROM Transaction FACET name SINCE 1 hour ago

-- p95 latency as a time series
SELECT percentile(duration, 95) FROM Transaction
  TIMESERIES SINCE 6 hours ago

-- Error rate (%) — note the funnel/percentage helper
SELECT percentage(count(*), WHERE error IS true)
  FROM Transaction SINCE 1 day ago

-- Distribution
SELECT histogram(duration, 50, 100) FROM Transaction
```

Key data types you query: `Transaction` (APM web/non-web txns), `Span`
(distributed-trace spans), `Log`, `Metric`, and any custom event type you
emit. Because they share one store, you can join an SLI query, a deploy
marker, and a log filter in a single dashboard.

## OTel Support

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.nr-data.net:4317
OTEL_EXPORTER_OTLP_HEADERS=api-key=KEY
```

For: vendor-neutral.

## Pricing

Two axes — deliberately *not* per-host, which is the main structural
difference from Datadog:

- **Data ingest** — billed per GB into NRDB (first 100 GB/mo free). Data
  Plus tier raises retention and adds compliance features at a higher per-GB
  rate.
- **Users** — Basic (free, query/dashboard), Core, and Full Platform users.
  You pay for the people with full troubleshooting access, not for the
  number of monitored machines.

Why this matters: on a fleet of many small/ephemeral hosts (autoscaling,
serverless, K8s pods churning), per-host pricing punishes you and ingest
pricing does not. The flip side is that a chatty app emitting huge log/trace
volume drives the bill regardless of host count, so **the cost lever is data
volume (sampling, dropping, attribute pruning), not instance count.**

## Distributed Tracing

Auto-instrumented; cross-service.

```
Trace view: spans timeline + service map
```

## Logs in Context

Auto-correlation with traces via trace_id.

## Synthetic Monitoring

API + browser checks; scheduled.

## Alerts

Alert conditions are NRQL queries evaluated on a rolling window. You set a
threshold, a duration ("for at least N minutes"), and route the violation
through a **workflow** to destinations (PagerDuty, Slack, webhook).

```sql
-- Error count condition (static threshold)
SELECT count(*) FROM Transaction WHERE error IS true

-- Error rate as an SLI condition (better than raw count)
SELECT percentage(count(*), WHERE error IS true) FROM Transaction
```

Two NRQL-native alerting features worth knowing for interviews:

- **Baseline conditions** — alert on deviation from a learned dynamic
  baseline rather than a fixed number; useful for seasonal traffic.
- **Loss of signal** — fire (or resolve) when a stream *stops* reporting,
  which catches dead agents that a threshold alone would miss.

New Relic also ships managed **Service Levels** (SLI/SLO) that turn a "good
events / valid events" NRQL pair into error-budget burn — the same
multi-window burn-rate idea covered in L17/C08, but generated for you.

## Pros

- One platform
- NRQL powerful
- Free tier generous
- Strong APM

## Cons

- UI complex
- Pricing changes
- Less mindshare than Datadog

## When New Relic

- Free tier sufficient
- Java/.NET stack (strong)
- NRQL-comfortable

## Compared to Datadog

| | New Relic | Datadog |
|---|---|---|
| Pricing | per ingest + user | per host + ingest |
| Free tier | 100 GB | trial |
| UI | NRQL | dashboard |
| APM | strong | strong |
| Logs | strong | strong |
| RUM | yes | yes |

## OTel Migration

```bash
# Drop New Relic SDK
# Add OTel SDK
OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.nr-data.net:4317
```

## Best Practices

- **Instrument with OpenTelemetry** and send via OTLP, so the app stays
  portable and you can leave if pricing changes. Use the NR agent only where
  it buys you something OTel can't yet (e.g. deep runtime profiling).
- **Treat ingest as the budget.** Sample traces, drop high-volume debug
  logs at the edge, and prune fat attributes before they hit NRDB — that's
  where the bill is, not host count.
- **Build SLIs as NRQL `percentage()` queries** and let Service Levels track
  the error budget; alert on burn rate, not on raw counts.
- **Add deployment markers** (via the API/CI) so latency and error charts
  line up with releases — this is the fastest way to attribute a regression.
- **Prefer baseline / loss-of-signal conditions** for noisy or bursty
  signals instead of hand-tuned static thresholds.

## Common Mistakes

- **Indexing everything** — shipping all debug logs and 100% of traces, then
  being surprised by the GB bill. Sample and drop at source.
- **High-cardinality custom attributes** (raw user IDs, request IDs as facet
  keys) that blow up query cost and dashboard cardinality.
- **Static thresholds on seasonal traffic** — pages every Monday morning;
  use baselines.
- **No loss-of-signal alert**, so a crashed agent looks like "all healthy."
- **Locking into the proprietary agent/SDK** when OTel would have kept the
  instrumentation vendor-neutral.

## Quick Refs

```bash
# Install agent
newrelic install

# Send custom
newrelic event create-event --eventType=Custom --attributes='{"key":"value"}'
```

```sql
SELECT * FROM Transaction WHERE ...
```

## Interview Prep

**Junior**: "What is New Relic and what makes it different from a dashboard
tool like Grafana?" — It's a SaaS observability platform that stores metrics,
events, logs, and traces in one columnar database (NRDB) and lets you query
all of it with NRQL. Unlike a pure visualization layer, it ingests and
retains the telemetry itself, so it's the backend and the UI in one.

**Mid**: "How does New Relic's pricing model differ from Datadog's, and when
does that matter?" — New Relic bills on data ingested (GB) plus full-platform
users; Datadog bills primarily per host (plus ingest). On a large fleet of
small or ephemeral hosts — autoscaling groups, serverless, churning K8s pods
— per-host pricing punishes you while ingest pricing tracks actual data, so
New Relic is often cheaper there. The trade-off is that a chatty,
high-volume app drives the New Relic bill regardless of host count.

**Senior**: "Walk me through alerting in New Relic and how you'd avoid noisy
pages on bursty traffic." — Conditions are NRQL queries evaluated over a
rolling window with a threshold and a "for N minutes" duration, routed
through workflows to PagerDuty/Slack. For bursty or seasonal traffic I avoid
static thresholds and use baseline conditions, which alert on deviation from
a learned dynamic baseline, plus a loss-of-signal condition to catch dead
agents. For user-facing SLAs I express the SLI as a `percentage()` NRQL
query and alert on multi-window error-budget burn rather than raw error
counts.

**Staff**: "We're standardizing observability across many teams. Make the
case for instrumenting with OpenTelemetry and sending to New Relic versus
using New Relic's native agents." — Instrument once with OTel and export via
OTLP: the instrumentation becomes a vendor-neutral asset, so if pricing,
features, or strategy change we can repoint the exporter at a different
backend (or an OSS LGTM stack) without touching application code. We keep
native agents only where they deliver something OTel can't yet — for New
Relic that's mainly deep runtime profiling. Operationally I'd centralize
cost control on ingest (sampling, attribute pruning, edge log dropping) since
that's New Relic's billing axis, set per-team ingest budgets, and govern
custom-attribute cardinality so query cost stays predictable.

## Next Topic

→ [T03 — Dynatrace](T03-Dynatrace.md)
