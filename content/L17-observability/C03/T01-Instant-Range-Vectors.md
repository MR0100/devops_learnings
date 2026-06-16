# L17/C03/T01 — PromQL: Instant vs Range Vectors

## Learning Objectives

- Distinguish vector types
- Write valid queries

## Vectors

### Instant Vector
Single sample per series at one time:
```promql
http_requests_total
```

Returns current value.

### Range Vector
Series of samples over time window:
```promql
http_requests_total[5m]
```

Returns last 5 min of samples per series.

## Use Cases

- Instant: current state, alerts
- Range: rates, deltas, aggregations over time

## Functions Require Range

```promql
rate(http_requests_total[5m])
```

`rate()`: takes range, returns instant.

```promql
sum(rate(http_requests_total[5m]))   # OK
sum(rate(http_requests_total))       # ERROR: needs range
```

## Common Functions

### rate()
Per-second rate:
```promql
rate(http_requests_total[5m])
```

For counters.

### irate()
Instantaneous rate (last 2 samples):
```promql
irate(http_requests_total[5m])
```

For gauges-like; less smoothing.

### increase()
Total over window:
```promql
increase(http_requests_total[1h])
```

= rate × duration.

### delta()
Change for gauges:
```promql
delta(memory_usage[5m])
```

### deriv()
Derivative (gauge change rate).

### predict_linear()
```promql
predict_linear(disk_usage[1h], 3600 * 24)
```

Predict in 24h.

## Selectors

### Label match
```promql
http_requests_total{service="api"}
http_requests_total{service!="api"}
http_requests_total{service=~"api|web"}    # regex
http_requests_total{service!~"test.*"}
```

### __name__
```promql
{__name__="http_requests_total"}
```

## Aggregation

```promql
sum(http_requests_total)
avg(http_requests_total)
min, max
count(http_requests_total)
topk(5, http_requests_total)
bottomk(5, http_requests_total)
quantile(0.99, http_requests_total)
```

## By / Without

```promql
sum by (service) (http_requests_total)
# Sum per service

sum without (instance) (http_requests_total)
# Sum, but drop instance label
```

## Examples

### Total RPS
```promql
sum(rate(http_requests_total[5m]))
```

### RPS per service
```promql
sum by (service) (rate(http_requests_total[5m]))
```

### Error rate
```promql
sum(rate(http_requests_total{code=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

### p99 latency
```promql
histogram_quantile(0.99,
  sum by (le) (rate(http_request_duration_bucket[5m]))
)
```

## Histogram Functions

### histogram_quantile()
```promql
histogram_quantile(0.95,
  sum by (le, service) (rate(http_request_duration_bucket[5m]))
)
```

`le`: bucket label. Sum across pods first.

### histogram_count() / sum() (newer)
For native histograms.

## Time Functions

```promql
time()                # current unix time
day_of_week()
hour()
minute()
```

## Subqueries

```promql
max_over_time(
  rate(http_requests_total[5m])[1h:1m]
)
```

Subquery: range vector over evaluated query.

## Arithmetic

```promql
metric_a + metric_b
metric_a / metric_b
metric_a * 100
```

Matched by labels.

## Comparison

```promql
metric_a > 100
metric_a == 0
```

Returns series where true.

## Set Operations

```promql
metric_a or metric_b
metric_a and metric_b
metric_a unless metric_b
```

By label match.

## Joins

### on / ignoring
```promql
rate(http_requests_total[5m])
/
on (service, instance)
metric_capacity
```

Match on labels.

### group_left / group_right
For 1:N joins:
```promql
metric_a * on (service) group_left (region) metric_b
```

## Common Mistakes

- Range on counter alone (need rate)
- rate over too-short window
- Forgetting `by` (high cardinality result)
- Wrong join (one-to-many without group_)

## Range Window

Rule of thumb: 4x scrape interval.

If scrape = 15s, use [1m] or [5m].

Too short: noisy.
Too long: lag.

## Aggregation Pre-Histogram

For histograms:
```promql
histogram_quantile(0.99, sum by (le) (rate(metric_bucket[5m])))
```

Sum across instances by `le` first. Then quantile.

Wrong:
```promql
avg(histogram_quantile(0.99, ...))   # wrong: avg of quantiles
```

## Best Practices

- **Always `rate()`/`increase()` a counter before aggregating** — a bare
  counter restarts to 0 on process restart, so `sum(counter)` is meaningless.
- **Size the range window to ~4× the scrape interval.** `rate()` needs at
  least two samples in the window; too short is noisy and gappy, too long
  lags and smooths over real spikes.
- **Aggregate histograms on `le` *before* `histogram_quantile`**, never
  average quantiles — `avg(histogram_quantile(...))` is statistically wrong.
- **Push label matchers as deep as possible.** Filter inside the innermost
  selector so the engine scans fewer series, instead of computing broadly and
  trimming at the end.
- **Use recording rules for hot/expensive expressions** (p99 latency, SLI
  ratios) so dashboards and alerts read a precomputed series — see T03.
- **`by`/`without` deliberately.** Forgetting `by` returns one giant series or
  explodes cardinality; name the labels you actually want to keep.
- **Reach for exemplars to jump from a metric spike to a trace** (below)
  rather than hand-correlating timestamps across tools.

## Exemplars (metric → trace correlation)

A histogram tells you p99 latency jumped; it can't tell you *which* request
was slow. **Exemplars** close that gap. An exemplar is a sample value
annotated with a trace ID (and labels) attached to a histogram bucket
observation — a pointer from the aggregate metric into one concrete trace.

```
# Exposition format: value, then exemplar after the # marker
http_request_duration_seconds_bucket{le="0.5"} 4283 # {trace_id="a1b2c3"} 0.48 1716910000
```

Workflow (the "metrics → traces" jump):

1. A dashboard panel built on `histogram_quantile(...)` shows a latency
   spike.
2. Grafana renders exemplars as dots on that panel; each dot carries a
   `trace_id`.
3. Click the dot → Grafana follows the configured trace data source (Tempo /
   Jaeger) → you land on the exact slow trace's waterfall.

Requirements: enable exemplar storage in Prometheus
(`--enable-feature=exemplar-storage`), instrument with an SDK that records
them (OpenTelemetry / Prometheus client libs do, when a trace is active), and
scrape via OpenMetrics so the `# {…}` annotations survive. Exemplars are
sampled, not stored per observation, so they cost little. This is the
concrete mechanism behind "correlate metrics, logs, and traces" from
L17/C01 — and why it's worth propagating `trace_id` everywhere.

## Native (Sparse) Histograms

Classic Prometheus histograms use **fixed, predefined buckets** (`le="0.5"`,
`le="2"`, …). Two problems: you must guess the bucket boundaries up front
(bad guesses make quantiles inaccurate), and every bucket is its own time
series, so good resolution means high cardinality and storage cost.

**Native histograms** (a.k.a. sparse histograms, GA-track in Prometheus
2.40+/3.x) store a single, structured sample with **exponential,
automatically-sized buckets** and only materialize buckets that actually have
observations:

- **One series instead of N** `_bucket` series → far lower cardinality.
- **No bucket guessing** — resolution adapts via a configurable factor.
- **Better quantile accuracy** across a wide value range.

Query side uses the same idea with native-histogram-aware functions:

```promql
histogram_quantile(0.95, rate(http_request_duration_seconds[5m]))
histogram_count(rate(http_request_duration_seconds[5m]))
histogram_sum(rate(http_request_duration_seconds[5m]))
```

Trade-offs: it's newer (feature-gated, evolving exposition format), needs
client SDK + storage + query support end-to-end, and the whole ecosystem
(remote-write backends, Grafana panels) is still catching up. Classic
fixed-bucket histograms remain the safe default when broad tooling
compatibility matters; reach for native histograms when bucket cardinality or
quantile accuracy is the pain point.

## Quick Refs

```
Selectors: metric{labels}
Range: [5m]
Rate: rate() / irate() / increase()
Aggregation: sum/avg/min/max/topk/quantile [by/without (labels)]
Histogram: histogram_quantile(0.99, sum by (le) (rate(metric_bucket[5m])))
Exemplars: histogram bucket + trace_id → click-through to trace
Native hist: histogram_quantile(0.95, rate(metric[5m]))  # no le, one series
```

## Interview Prep

**Junior**: "Range vs instant."

**Mid**: "rate vs irate."

**Senior**: "Common queries."

## Next Topic

→ [T02 — Aggregation & Functions](T02-Aggregation-Functions.md)
