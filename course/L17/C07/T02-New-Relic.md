# L17/C07/T02 — New Relic

## Learning Objectives

- Use New Relic
- Compare to alternatives

## New Relic

Commercial APM (one of original):
- Metrics, logs, traces, RUM
- NRQL query language
- Free tier (100 GB/mo)

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

```
SELECT count(*) FROM Transaction WHERE appName = 'api' SINCE 1 hour ago
SELECT average(duration) FROM Transaction FACET name SINCE 1 hour ago
SELECT histogram(duration, 50, 100) FROM Transaction
```

Query language for everything.

## OTel Support

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.nr-data.net:4317
OTEL_EXPORTER_OTLP_HEADERS=api-key=KEY
```

For: vendor-neutral.

## Pricing

User-based:
- Per ingest (GB)
- Per user (full access)
- Free tier

Often: less than Datadog.

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

```sql
SELECT count(*) FROM Transaction WHERE error IS true
```

Threshold + condition.

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

**Mid**: "What's New Relic."

**Senior**: "NR vs Datadog."

## Next Topic

→ [T03 — Dynatrace](T03-Dynatrace.md)
