# L17/C07/T03 — Dynatrace

## Learning Objectives

- Know Dynatrace
- Pick for enterprise

## Dynatrace

Enterprise APM:
- OneAgent (single agent)
- AI-driven (Davis)
- Auto-discovery
- Strong for monoliths + microservices

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

Anomaly detection + root cause:
- Auto-correlates issues
- Suggests causes
- Reduces alert noise

## DQL (Dynatrace Query Language)

Modern; replaces older:
```
fetch logs
| filter dt.event.type == "error"
| summarize count(), by:{service}
```

## Pricing

Per host hour (DPS - Dynatrace Platform Subscription):
- Expensive but inclusive

For: large enterprises with budget.

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

## Quick Refs

```bash
# Install OneAgent (paste from Dynatrace UI)
```

```
DQL queries via web UI / API
```

## Interview Prep

**Mid**: "What's Dynatrace."

**Senior**: "When Dynatrace."

## Next Topic

→ [T04 — Honeycomb](T04-Honeycomb.md)
