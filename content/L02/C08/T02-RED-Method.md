# L02/C08/T02 — The RED Method

## Learning Objectives

- Apply Tom Wilkie's RED method (Rate, Errors, Duration) to any request-driven service
- Understand why RED complements USE — services vs. resources — and when to use each
- Build RED metrics with the right instrumentation (counters + histograms) and read percentiles correctly
- Connect a RED symptom (rising p99 latency) to a USE cause (saturated resource)

## What the RED Method Is

USE diagnoses **resources**. RED diagnoses **services**. For every service (or endpoint), you monitor three signals:

| Signal | Definition | Typical metric |
|---|---|---|
| **Rate** | The number of requests per second the service is handling | `req/s` counter |
| **Errors** | The number of failed requests per second | `errors/s` counter (5xx, exceptions) |
| **Duration** | The distribution of time each request takes | latency histogram → p50/p90/p99 |

RED is the request-side mirror of USE. Where USE asks "is the disk saturated?", RED asks "are requests slow, failing, or surging?" Together they answer the two halves of nearly every incident: *the service is slow* (RED) *because a resource is saturated* (USE).

RED maps cleanly onto the Google SRE "Four Golden Signals" (Latency, Traffic, Errors, Saturation): Rate ≈ Traffic, Errors ≈ Errors, Duration ≈ Latency. The golden signals add Saturation, which is exactly the bridge back to USE.

## Why Three Signals, and Why These

- **Rate** is your demand baseline. A latency spike means nothing until you know whether traffic doubled (capacity) or stayed flat (regression). Rate also catches a *silent outage*: requests dropping to zero is as serious as errors climbing.
- **Errors** is the most direct measure of user pain. Track it as a **rate and a ratio** (errors / total), because 50 errors/s means one thing at 100 req/s and another at 50,000 req/s.
- **Duration** is *where* the pain is felt. You must track it as a **distribution**, never an average — averages hide the tail, and the tail is what your slowest, often most valuable, users experience.

## Instrumenting RED Correctly

Rate and Errors are **counters**; Duration is a **histogram**. In Prometheus terms:

```
# Rate: requests per second over 5m
sum(rate(http_requests_total{service="checkout"}[5m]))

# Errors: error ratio
sum(rate(http_requests_total{service="checkout",status=~"5.."}[5m]))
  /
sum(rate(http_requests_total{service="checkout"}[5m]))

# Duration: p99 latency from a histogram
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{service="checkout"}[5m])) by (le))
```

The critical instrumentation rule: **emit a histogram for duration**, not a gauge or a pre-computed average. Histograms let you compute any percentile after the fact and aggregate correctly across instances. A pre-averaged latency metric cannot be re-percentiled and cannot be summed across pods.

## Reading Percentiles

| Percentile | What it tells you |
|---|---|
| **p50 (median)** | The typical experience. Stable p50 + bad p99 = tail problem (GC pause, lock contention, cold cache). |
| **p90 / p95** | The edge of "normal". Where SLOs usually live. |
| **p99 / p99.9** | The tail. Dominated by retries, GC, queueing, slow dependencies, and saturated resources. |

A worked example. Your checkout service alert fires:

```
Rate:     1,200 req/s   (normal ~1,200 — traffic flat)
Errors:   0.02%         (normal — not an error problem)
Duration: p50  18 ms    (normal)
          p99 940 ms    (normal ~120 ms)  <-- the symptom
```

Flat rate + flat errors + p50 fine but p99 blown = a **tail latency** problem, not a capacity or correctness problem. Now you pivot to USE on the dependencies: check the database disk `await` (`iostat -xz 1`), CPU run-queue (`vmstat`), and GC/lock activity. RED told you *what hurts*; USE finds *why*.

## RED Across a Request Path

RED is most powerful applied **per service and per dependency hop**, so you can localize latency:

```
client → [edge/LB]  RED: rate, 5xx, duration
        → [API]     RED: rate, 5xx, duration
        → [auth]    RED: rate, 5xx, duration   <-- p99 spikes HERE
        → [db]      RED + USE (disk await, conns)
```

If the API's p99 is high but auth's p99 is also high while the API's *own* processing time is low, the latency is downstream in auth. Per-hop RED turns "the site is slow" into "auth's p99 regressed at 14:32".

A subtle trap on the Errors signal: count both the failures you *return* and the ones you *retry away*. If the API retries auth on a 5xx and eventually succeeds, the user sees success but the dependency is failing — instrument errors at each hop, not just at the edge, or you'll under-count and chase a latency mystery (retries inflate p99) without realizing a downstream is unhealthy. The same applies to client-side timeouts that the server never sees: a request the client abandoned still consumed a connection and a worker.

## RED vs USE — When to Use Each

| | USE | RED |
|---|---|---|
| Subject | Resources (CPU, disk, net, mem) | Services / endpoints |
| Metrics | Utilization, Saturation, Errors | Rate, Errors, Duration |
| Answers | "Is the hardware the bottleneck?" | "Are requests slow/failing/surging?" |
| Author | Brendan Gregg | Tom Wilkie |
| Direction | Bottom-up (from hardware) | Top-down (from user) |

Start RED at the user, follow it down per hop, and switch to USE the moment you reach the resource that's saturated. They are not alternatives — they are two ends of the same investigation.

## Common Mistakes

- **Alerting on averages.** Mean latency stays calm while p99 melts down. Always alert on a high percentile or, better, on an SLO error budget.
- **Errors as a count, not a ratio.** 100 errors/s is invisible at 100k req/s and catastrophic at 200 req/s. Track the ratio.
- **Forgetting Rate.** A latency or error graph is uninterpretable without the traffic context that produced it. Rate also catches the silent "requests went to zero" outage.
- **Pre-averaging duration at the source.** Once you emit an average, you can never recover p99 and you can't aggregate across instances. Emit histograms.
- **Stopping at RED.** RED tells you the service is slow; it does not tell you why. The next move is always USE on the implicated resource.

## Best Practices

- Instrument every service with the same three RED metrics and the same label conventions, so dashboards are uniform across the fleet.
- Use histograms for duration with bucket boundaries chosen around your SLO (e.g., dense buckets near 100–500 ms if that's your target).
- Define SLOs and error budgets on Errors and Duration; alert on **burn rate**, not instantaneous spikes, to cut noise.
- Apply RED per dependency hop so you can localize latency to a specific service instead of "the system".
- Pair every RED dashboard with the corresponding USE view so on-call can jump from symptom (slow service) to cause (saturated resource) in one click.

## Quick Refs

```promql
# Rate (req/s)
sum(rate(http_requests_total{service="$svc"}[5m]))

# Errors (ratio)
sum(rate(http_requests_total{service="$svc",status=~"5.."}[5m]))
  / sum(rate(http_requests_total{service="$svc"}[5m]))

# Duration (p99 from histogram)
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{service="$svc"}[5m])) by (le))

# Duration p50 / p90 / p99 in one expr (per le aggregation)
histogram_quantile(0.50, sum(rate(...bucket[5m])) by (le))
histogram_quantile(0.90, sum(rate(...bucket[5m])) by (le))
```

```
RED  = Rate, Errors, Duration        (services)
USE  = Utilization, Saturation, Errors (resources)
Golden Signals = Latency, Traffic, Errors, Saturation
```

## Interview Prep

**Junior**: "What does RED stand for?" — Rate (requests/sec), Errors (failed requests/sec), and Duration (the latency distribution) — the three signals you monitor for any request-driven service.

**Mid**: "Why track duration as a histogram instead of an average?" — Averages hide the tail; a histogram lets me compute p50/p90/p99 after the fact and aggregate correctly across instances, so I can see that p99 blew up even while the mean looks fine.

**Senior**: "Your service p99 spiked but rate and errors are flat — walk me through it." — Flat rate rules out a capacity surge and flat errors rules out correctness, so it's a tail-latency problem; I pivot to USE on dependencies (DB disk `await`, CPU run-queue, GC/lock contention) since something downstream is queueing only the slow requests.

**Staff**: "How do RED and USE fit into a fleet-wide observability strategy?" — RED is the top-down, user-facing layer (per service and per hop, driving SLOs and error-budget burn-rate alerts), and USE is the bottom-up resource layer; I wire dashboards so on-call goes from a RED symptom to the implicated host's USE view in one hop, which keeps MTTR low because every incident is "slow service (RED) → saturated resource (USE)".

## Next Topic

→ [T03 — Tracing Tools](T03-Tracing-Tools.md)
