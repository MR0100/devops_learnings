# L17/C07/T05 — Splunk Observability

## Learning Objectives

- Know Splunk
- Compare for log-heavy

## Splunk

Originally log analysis:
- Massive enterprise install base
- SPL query language
- Acquired SignalFx (metrics)
- Acquired Omnition / VictorOps

## Splunk Observability Cloud

= Renamed SignalFx + extras:
- Metrics
- Traces (APM)
- Logs (via Splunk Cloud)
- RUM
- Synthetics

## SignalFx (Metrics)

```bash
# Send via Smart Agent or OTel
OTEL_EXPORTER_OTLP_ENDPOINT=https://ingest.us0.signalfx.com
```

## SPL

```
index=app status=500 | stats count by host
index=app | timechart count
```

Rich log query.

## APM

Auto-instrument:
- AlwaysOn Profiling
- Distributed tracing
- Service maps

## When Splunk

- Existing Splunk for logs (extend)
- Enterprise SIEM use
- Compliance (SOC, audit)

## When Not

- Cloud-native startups (less common)
- Cost (Splunk priced for enterprise)

## Cost

Premium:
- Per GB indexed
- Various plans

For: large orgs only.

## Pros

- Enterprise-grade
- Log + obs unified
- Strong SIEM heritage

## Cons

- Cost
- UI dated (SPL learning)
- Vendor lock-in
- Less DevOps-native

## Compared

| | Splunk | Datadog | New Relic |
|---|---|---|---|
| Origin | logs | cloud APM | APM |
| Strength | log search | unified | NRQL |
| UI | dated | modern | modern |
| Cost | $$$$ | $$$ | $$$ |

## OTel

Splunk Observability accepts OTel.

## Quick Refs

```
SPL: index=X | stats count
APM: AlwaysOn Profiling enabled
OTel: ingest.signalfx.com endpoint
```

## Interview Prep

**Mid**: "What's Splunk."

**Senior**: "Enterprise APM."

## Next Topic

→ Move to [L17/C08 — SLI, SLO, Error Budgets](../C08/README.md)
