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

## Quick Refs

```
Selectors: metric{labels}
Range: [5m]
Rate: rate() / irate() / increase()
Aggregation: sum/avg/min/max/topk/quantile [by/without (labels)]
Histogram: histogram_quantile(0.99, sum by (le) (rate(metric_bucket[5m])))
```

## Interview Prep

**Junior**: "Range vs instant."

**Mid**: "rate vs irate."

**Senior**: "Common queries."

## Next Topic

→ [T02 — Aggregation & Functions](T02-Aggregation-Functions.md)
