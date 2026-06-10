# L17/C08/T01 — Defining Good SLIs

## Learning Objectives

- Pick SLIs
- Measure correctly

## SLI

Service Level Indicator: quantitative measure of service quality.

Examples:
- Availability: % successful requests
- Latency: p99 response time
- Throughput: requests/sec
- Correctness: % correct results

## User-Centric

SLI measures what users experience.

NOT:
- Internal metrics (CPU)
- Resource saturation
- Backend stats

YES:
- HTTP success rate
- Page load time
- Time to first byte

## Categories

### Request-Based
For request/response (web, RPC):
- Availability
- Latency
- Throughput

### Window-Based
For pipelines, batch:
- % of windows meeting SLO

### Quality
- Correctness
- Freshness

## Good SLI

- Measurable
- User-facing
- Linear correlation with user happiness
- Aggregate over time

## SLI Formula

Typically:
```
good_events / total_events
```

Examples:
- Successful requests / total requests
- Requests under 500ms / total requests

## Availability SLI

```promql
sum(rate(http_requests_total{code!~"5..", code!="429"}[5m]))
/
sum(rate(http_requests_total[5m]))
```

Note: exclude rate-limited (429); it's intentional.

## Latency SLI

```promql
sum(rate(http_request_duration_bucket{le="0.5"}[5m]))
/
sum(rate(http_request_duration_count[5m]))
```

% of requests under 500ms.

## SLI for Async

For pipelines (Kafka consumers, batch):
- Freshness: % records processed within X seconds
- Throughput: events/sec
- Correctness: % correct outputs

## SLI per Endpoint

```promql
sum by (endpoint) (rate(http_requests_total{code!~"5.."}[5m]))
/
sum by (endpoint) (rate(http_requests_total[5m]))
```

Per critical endpoint.

## Not All Requests Equal

- Critical (checkout): tight SLO
- Less critical (analytics): loose SLO

Weight or separate SLIs.

## Anti-Patterns

### Internal Metric SLI
"CPU < 80%" not user-facing.

### Too Many SLIs
Pick 3-5 critical ones.

### Vanity Metrics
"Number of requests" — not quality.

### Composite Without Care
"Availability AND latency" — confused signal.

## Multi-Window

Track:
- 5 min (alerts)
- 1 hr (recent)
- 28 days (SLO compliance)

## Aggregation

Customer-facing: aggregate per user.

```
% users who had < 1% errors today
```

Better than aggregate over requests.

## SLI Examples

### Web API
- Availability: non-5xx / total
- Latency: < 200ms / total

### Database
- Availability: queries succeed
- Latency: p99 < 100ms
- Freshness: replication lag < 5s

### Batch Pipeline
- Freshness: latest record within 10 min
- Completeness: records processed / received

### Search
- Availability: queries succeed
- Latency: < 500ms
- Quality: relevance score

## Synthetic SLI

Scripted requests measure SLI from outside:
- Avoid in-server measurement bias
- Real user perspective

```bash
# Synthetic check every minute
curl -m 5 https://api/health
```

## Real-User vs Synthetic

### Real User
- Actual experience
- Variance (network, device)

### Synthetic
- Controlled
- Trends visible
- Misses real issues

Both useful.

## SLI Specification

Define:
- What is being measured
- How (query)
- When (windows)
- Who is responsible

## SLI vs Metric

Metric: any measurement.
SLI: subset; user-facing critical.

For: SLIs are special.

## Choosing SLIs

For a service:
- What promises do you make to users?
- What hurts users when broken?
- What can you measure reliably?

## Best Practices

- User-facing
- Few (3-5)
- Per endpoint if needed
- Aggregable
- Stable definition (don't change often)

## Common Mistakes

- Internal metric as SLI
- Too many SLIs
- Vague definition
- Change SLI without versioning

## SLI Catalog

Standard across org:
- Web service: availability + latency
- Async: freshness + throughput

For: consistency.

## Quick Refs

```
SLI:        good / total
Availability: non-5xx / total
Latency:    < threshold / total
Freshness:  recent within X / total
Correctness: correct / total
```

## Interview Prep

**Junior**: "What's SLI."

**Mid**: "Good SLI examples."

**Senior**: "SLI selection."

**Staff**: "SLI catalog."

## Next Topic

→ [T02 — SLO Math & Rolling Windows](T02-SLO-Math.md)
