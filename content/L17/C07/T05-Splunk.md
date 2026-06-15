# L17/C07/T05 — Splunk Observability

## Learning Objectives

- Know Splunk
- Compare for log-heavy

## Splunk

Splunk started as the dominant **log analytics and SIEM** platform — a
search engine over machine data — and grew into observability by
acquisition:

- Massive enterprise + security install base; SPL is widely known.
- **SPL** (Search Processing Language) — a pipe-based query language over
  indexed events.
- Acquired **SignalFx** → the streaming metrics + APM engine that became
  Splunk Observability Cloud.
- Acquired **Omnition** (distributed tracing) and **VictorOps** (on-call /
  incident response, now Splunk On-Call).
- Splunk itself was acquired by **Cisco** (2024), pushing further
  network/security integration.

The key distinction: Splunk's center of gravity is **logs and security**, and
observability is the bolt-on. That's the opposite of Honeycomb (events) or
Datadog (cloud-native APM first). The strategic reason to pick Splunk
Observability is usually "we already run Splunk Enterprise for logs/SIEM."

## Splunk Observability Cloud

= Renamed SignalFx + extras:
- Metrics
- Traces (APM)
- Logs (via Splunk Cloud)
- RUM
- Synthetics

## SignalFx (Metrics)

The metrics + tracing core of Splunk Observability Cloud, and its real
differentiator: a **streaming analytics engine**. Instead of querying a
metrics database on a schedule, SignalFx computes on the data *as it
arrives*, which gives sub-second detection and alerting — valuable for
high-volume, latency-sensitive systems where a 1-minute scrape-and-evaluate
loop is too slow.

```bash
# Send via the Splunk OTel Collector (preferred) or OTLP
OTEL_EXPORTER_OTLP_ENDPOINT=https://ingest.us0.signalfx.com
```

The recommended path today is the **Splunk Distribution of the OpenTelemetry
Collector** (the older "Smart Agent" is deprecated), so instrumentation stays
OTel-standard while Splunk handles ingest and streaming analysis.

## SPL

Search Processing Language — Unix-pipe-style: a search term feeds a chain of
commands (`stats`, `timechart`, `eval`, `rex`). It's extremely powerful for
ad-hoc log forensics and is the skill most "Splunk shops" already have.

```
index=app status=500 | stats count by host
index=app | timechart count
index=app error | rex "user=(?<user>\w+)" | top user
```

Note the platform split: **SPL** queries log data in Splunk
Enterprise/Cloud, while the metrics/APM side (SignalFx) uses its own
**SignalFlow** streaming language. That two-language reality is a common
gotcha — you don't write SPL against the streaming metrics engine.

## APM

Splunk APM (the former Omnition tech on the SignalFx backend) does
**NoSample full-fidelity tracing** by default — it ingests 100% of spans and
samples on the backend, so it can compute exact error/latency stats and still
keep the interesting traces, rather than head-sampling at the edge.

- **AlwaysOn Profiling** — continuous code profiling correlated to traces.
- **Distributed tracing** with auto service maps from span data.
- **Tag spotlight / RED metrics** generated from trace data for fast
  breakdown by endpoint, status, and tag.

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

## Best Practices

- **Ship telemetry through the Splunk OTel Collector**, not the deprecated
  Smart Agent, so instrumentation is standard OTel and portable.
- **Lean on the streaming engine** for fast detectors where sub-second
  alerting actually matters; don't recreate slow scrape-and-evaluate loops.
- **Keep logs in Splunk only where you'll use them** — per-GB indexing is the
  cost driver, so route low-value logs to cheaper cold storage / S3 and index
  the rest.
- **Know which language to use where** — SPL for log search, SignalFlow for
  streaming metrics — and build dashboards on the right side of that split.
- **Use the existing Splunk SIEM/audit integration** as the reason to adopt;
  the unified log-plus-observability story is the differentiator.

## Common Mistakes

- **Indexing every log into Splunk** and being shocked by the per-GB bill —
  filter and tier before ingest.
- **Trying to write SPL against the metrics/APM (SignalFx) engine** — that's
  SignalFlow's job; the two-language split trips people up.
- **Sticking with the deprecated Smart Agent** instead of the OTel Collector,
  locking instrumentation to Splunk.
- **Choosing Splunk for a greenfield cloud-native startup** purely for
  observability — without an existing Splunk/SIEM footprint, the cost and the
  dated UX rarely justify it over Datadog or an OSS stack.
- **Ignoring the Cisco-era roadmap** when planning multi-year tooling — the
  acquisition shifts integration direction toward network/security.

## Quick Refs

```
SPL: index=X | stats count
APM: AlwaysOn Profiling enabled
OTel: ingest.signalfx.com endpoint
```

## Interview Prep

**Junior**: "What is Splunk known for?" — Splunk is the dominant log
analytics and SIEM platform — a search engine over machine data, queried with
SPL. It moved into observability (metrics, traces, RUM) mainly by acquiring
SignalFx, so its roots are logs and security, with APM added on top.

**Mid**: "What did the SignalFx acquisition give Splunk, and what's special
about it?" — SignalFx is Splunk's metrics and APM engine, and its
differentiator is a streaming analytics architecture: it computes on metrics
as they arrive rather than querying a database on a schedule, which enables
sub-second detection and alerting. It's the foundation of Splunk
Observability Cloud and is fed today through the Splunk OpenTelemetry
Collector.

**Senior**: "When would you choose Splunk Observability over Datadog?" — The
honest answer is "when you're already a Splunk shop." If the org runs Splunk
Enterprise for logs, SIEM, and audit/compliance, Splunk Observability extends
that with unified log-plus-trace context and reuses the team's SPL skills and
existing data. The streaming engine is also a genuine edge for very
high-volume, latency-sensitive alerting. I wouldn't pick it greenfield for a
cloud-native startup: it's enterprise-priced, the UX/SPL has a learning
curve, and there's a two-language split (SPL for logs, SignalFlow for
metrics) that adds friction.

**Staff**: "You're consolidating observability in a large enterprise that
already runs Splunk for security. Make the build-vs-consolidate call." — I'd
weigh the strong pull of consolidation — one platform for logs, SIEM, and
observability means shared data, shared on-call (Splunk On-Call), and one
audit story, which is worth a lot in a compliance-heavy enterprise — against
cost and lock-in. To keep options open I'd standardize instrumentation on
OpenTelemetry via the Splunk OTel Collector so the app layer stays portable,
govern log ingest aggressively (tier and route low-value logs out of the
indexed tier since per-GB is the cost driver), and factor in the Cisco-era
roadmap, which is steering Splunk toward deeper network/security integration.
If the security/SIEM gravity is real, consolidating on Splunk is defensible;
if it's just observability, an OSS or Datadog path is usually leaner.

## Next Topic

→ Move to [L17/C08 — SLI, SLO, Error Budgets](../C08/README.md)
