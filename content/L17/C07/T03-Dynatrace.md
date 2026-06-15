# L17/C07/T03 — Dynatrace

## Learning Objectives

- Know Dynatrace
- Pick for enterprise

## Dynatrace

Enterprise-grade observability built around three pillars that distinguish
it from Datadog/New Relic:

- **OneAgent** — a single host agent that auto-discovers and instruments
  everything on the box (processes, runtimes, containers) with no per-app
  setup and no code changes.
- **Davis AI** — a deterministic causal-AI engine that builds a dependency
  graph and pinpoints *root cause*, not just "something is anomalous."
- **Smartscape** — a continuously updated real-time topology of every
  service, process, host, and network link.

The pitch is "set it and forget it": deploy OneAgent, and the platform
discovers the topology, instruments the stack, and tells you the root cause
of problems automatically. It is strongest in large, heterogeneous estates
(legacy monoliths next to microservices) where manual instrumentation
doesn't scale and the org wants answers, not just dashboards.

## OneAgent

```bash
/tmp/Dynatrace-OneAgent.sh
```

Auto-instruments:
- JVM
- .NET
- Node
- Python
- PHP

No code changes. Process injection.

## Smartscape

Auto topology:
- Services
- Processes
- Hosts
- Network
- Real-time

For: complex environments.

## Davis AI

Davis is the headline differentiator. Unlike ML "anomaly detectors" that
flag statistical outliers and leave you to correlate them, Davis uses the
Smartscape **dependency graph** plus high-frequency metrics to do causal
analysis:

- **Deterministic, not probabilistic** — given the topology and timing, it
  walks the dependency edges to find the originating fault rather than
  guessing from correlation alone.
- **Problem cards** — related events across services collapse into a single
  "problem" with an identified root cause, the affected services, and the
  business impact, instead of fifty separate alerts for one outage.
- **Alert-noise reduction** — because it groups symptoms under a root cause,
  one bad database doesn't page ten downstream teams.

For interviews, the line that lands: Davis answers *"what broke and why,"*
where most tools only answer *"what's abnormal."* The cost of that power is
that it leans on OneAgent's deep, proprietary topology data.

## DQL (Dynatrace Query Language)

Modern; replaces older:
```
fetch logs
| filter dt.event.type == "error"
| summarize count(), by:{service}
```

## Pricing

Dynatrace Platform Subscription (DPS) — usage-based across several units:

- **Full-stack monitoring** billed per **host memory-GiB-hour** (a 16 GiB
  host costs more than a 4 GiB host), which bakes in APM, infra, and logs in
  context for that host.
- **Infrastructure-only** monitoring at a lower per-host rate when you don't
  need code-level APM.
- Separate consumption for **log ingest/retention**, **DEM units** (RUM /
  synthetics), and **Davis data units** for custom-metric queries.

It is premium-priced and inclusive: you pay more per host but get the AI,
topology, and APM bundled rather than as add-ons. The structural catch is
the **host memory-GiB-hour** unit — large-memory hosts (big JVMs, databases)
are expensive, so right-sizing and infra-only tiering are the main cost
levers. Aimed at large enterprises with budget, not cost-sensitive startups.

## Pros

- Auto-everything
- AI insights
- Strong Java/.NET
- Enterprise features

## Cons

- Premium pricing
- Vendor lock-in (OneAgent proprietary)
- Less devops-friendly
- Learning curve

## When Dynatrace

- Enterprise (large IT)
- Complex legacy + new
- Want AI auto-detect
- Compliance / on-prem capability

## When Not

- Smaller orgs
- Cost-sensitive
- DevOps-led culture (DD/NR fits better)

## Real Use

- Large enterprises (banks, telcos)
- Government

Less common in cloud-native startups.

## Compared

| | Dynatrace | Datadog | New Relic |
|---|---|---|---|
| Origin | enterprise | cloud-native | early APM |
| Agent | OneAgent (1) | per-thing | per-app |
| AI | Davis (strong) | Watchdog | Anomalies |
| Pricing | premium | mid | varies |
| K8s | strong | strong | strong |

## Best Practices

- **Let OneAgent and Davis do the discovery** before you build manual
  dashboards — the topology and root-cause are the product; reinventing them
  by hand wastes the investment.
- **Tier hosts** into full-stack vs infrastructure-only to control the
  per-memory-GiB-hour cost; not every box needs code-level APM.
- **Tag by management zone / team** so Smartscape and problem cards route to
  the right owners and Davis impact analysis is scoped correctly.
- **Use OpenTelemetry for custom spans/metrics** that OneAgent doesn't
  capture — Dynatrace ingests OTLP, so you can enrich the auto-data without
  abandoning the agent.
- **Right-size large-memory hosts** (JVMs, databases) deliberately; they
  dominate the bill on the memory-GiB-hour model.

## Common Mistakes

- **Treating Davis problem cards as raw alerts** and re-fanning them out to
  every team — that throws away the noise reduction that's the whole point.
- **Full-stack monitoring on hosts that only need infra metrics**, paying
  APM rates for nothing.
- **Ignoring the memory-GiB-hour unit** and being shocked when a few big
  database hosts dominate the invoice.
- **Building a second, parallel instrumentation stack** instead of using
  OneAgent's auto-data plus OTel enrichment.
- **Assuming OneAgent is portable** — it's proprietary, so an exit strategy
  needs OTel instrumentation underneath.

## Quick Refs

```bash
# Install OneAgent (paste from Dynatrace UI)
```

```
DQL queries via web UI / API
```

## Interview Prep

**Junior**: "What is Dynatrace and what is OneAgent?" — Dynatrace is an
enterprise observability platform. OneAgent is its single host agent: you
install it once per host and it auto-discovers and instruments the processes
and runtimes on that machine with no code changes, feeding metrics, traces,
and logs back to the platform.

**Mid**: "What makes Davis AI different from the ML anomaly detection in other
APM tools?" — Most tools flag statistical outliers and leave you to correlate
them. Davis is causal: it uses the real-time dependency topology (Smartscape)
plus the timing of events to walk the dependency graph and identify the
originating root cause, then collapses all the downstream symptoms into one
"problem" card. So instead of fifty alerts for one outage you get one
problem with a named cause and a list of affected services.

**Senior**: "When would you choose Dynatrace over Datadog or a Prometheus +
Grafana stack?" — Dynatrace wins in large, heterogeneous enterprise estates —
legacy monoliths alongside microservices — where manual instrumentation
doesn't scale and the org wants automatic root-cause, not just dashboards.
OneAgent's auto-discovery plus Davis's causal analysis reduce both setup and
alert-triage effort. I'd *not* pick it for a small, cost-sensitive,
DevOps-led shop: it's premium-priced on a per-memory-GiB-hour model and
OneAgent is proprietary, so Datadog or an OSS stack usually fits that culture
better.

**Staff**: "Leadership loves the 'set it and forget it' pitch but worries
about lock-in and cost. How do you adopt Dynatrace responsibly?" — I'd lean
on OneAgent and Davis for what they're uniquely good at — auto-topology and
causal root-cause — while keeping the *instrumentation* portable by emitting
custom spans and metrics through OpenTelemetry (Dynatrace ingests OTLP). That
gives an exit path: the OTel layer can repoint to another backend if needed.
On cost, I'd govern the memory-GiB-hour unit directly: tier hosts into
full-stack vs infrastructure-only, right-size large-memory hosts, and put
log/DEM/Davis-data consumption under per-team budgets so the inclusive
pricing doesn't drift.

## Next Topic

→ [T04 — Honeycomb](T04-Honeycomb.md)
