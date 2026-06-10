# L17/C03/T02 — PromQL Aggregation & Functions

## Learning Objectives

- Use aggregation operators
- Compose functions

## Aggregation Operators

```
sum(), avg(), min(), max(), count()
stddev(), stdvar()
topk(N, x), bottomk(N, x)
quantile(0.99, x)
group()
```

## sum / avg / min / max

```promql
sum(http_requests_total)            # total
avg(cpu_usage)                       # average
max(memory_usage)                    # peak
min(latency)                         # lowest
```

## count

```promql
count(up)                            # number of targets
count by (job) (up)                  # per job
```

## stddev / stdvar

```promql
stddev(latency_p99)                  # standard deviation
```

For: outlier detection.

## topk / bottomk

```promql
topk(5, http_requests_total)         # top 5 series
bottomk(3, free_memory)              # 3 lowest
```

## quantile

```promql
quantile(0.95, network_throughput)   # 95th percentile across series
```

## group

```promql
group by (service) (metric)
```

Returns series with `service` label; value 1.

For: existence check.

## by / without

```promql
sum by (service) (http_requests_total)
# Keep only service label

sum without (instance, pod) (http_requests_total)
# Drop instance + pod
```

## Math Functions

```promql
abs(x)
ceil(x)
floor(x)
round(x)
sqrt(x)
exp(x)
ln(x)
log2(x)
log10(x)
```

## Convert Functions

```promql
clamp_min(metric, 0)
clamp_max(metric, 100)
clamp(metric, 0, 100)
```

For: bound values.

## Rate Variants

### rate()
```promql
rate(counter[5m])
```

Average per-second over window.

Handles counter resets (process restart).

### irate()
```promql
irate(counter[5m])
```

Per-second between last 2 samples. Spiky.

### increase()
```promql
increase(counter[1h])
```

Total in window.

### resets()
```promql
resets(counter[1h])
```

Number of counter resets.

## delta() / deriv()

For gauges:
```promql
delta(gauge[5m])          # last - first
deriv(gauge[5m])          # per-second derivative
```

## Predict

```promql
predict_linear(disk_free[1h], 86400)
# Predicts disk_free in 24h
```

For: capacity alerts.

## Smoothing

### avg_over_time
```promql
avg_over_time(metric[1h])
```

Smooth noisy.

### max_over_time / min_over_time
```promql
max_over_time(latency[1h])
```

Peak over window.

### quantile_over_time
```promql
quantile_over_time(0.95, latency[1h])
```

Quantile over time.

### count_over_time
```promql
count_over_time(metric[1h])
```

Number of samples.

### sum_over_time
```promql
sum_over_time(samples[1h])
```

## Histogram Quantile

For latency:
```promql
histogram_quantile(0.99,
  sum by (le) (rate(http_request_duration_bucket[5m]))
)
```

Important: aggregate buckets by `le` first, then quantile.

## Composition

```promql
# Cluster-wide p99 of error rate
histogram_quantile(0.99,
  sum by (le) (
    rate(http_request_duration_bucket{code=~"5.."}[5m])
  )
)
```

Nested.

## Vector Matching

```promql
errors / total
```

Matches by all common labels.

```promql
errors / on (service) total
```

Match only on `service`.

```promql
errors / ignoring (instance) total
```

Match excluding `instance`.

## group_left / group_right

For many-to-one:
```promql
container_memory_usage * on (pod) group_left (deployment) pod_info
```

Add `deployment` label to memory metric via pod_info.

## Examples

### Cluster CPU
```promql
sum(rate(container_cpu_usage_seconds_total[5m]))
```

### Per-Service Error Rate
```promql
sum by (service) (rate(errors_total[5m]))
/
sum by (service) (rate(requests_total[5m]))
```

### Top 5 by Memory
```promql
topk(5, sum by (pod) (container_memory_working_set_bytes))
```

### p99 Latency Per Service
```promql
histogram_quantile(0.99,
  sum by (le, service) (rate(http_duration_bucket[5m]))
)
```

### Saturation Index
```promql
sum by (instance) (
  rate(node_cpu_seconds_total{mode="user"}[5m])
)
/
count by (instance) (
  rate(node_cpu_seconds_total[5m])
)
```

CPU per core.

## Alert Examples

### Error Rate
```promql
sum(rate(errors[5m])) / sum(rate(requests[5m])) > 0.05
```

### High Memory
```promql
container_memory_working_set_bytes / container_spec_memory_limit_bytes > 0.9
```

### Disk Will Fill
```promql
predict_linear(node_filesystem_avail_bytes[1h], 4 * 3600) < 0
```

Disk full in < 4 hours.

## Pitfalls

### Wrong Histogram Aggregation
```promql
# WRONG (mean of quantiles)
avg(histogram_quantile(0.99, rate(metric_bucket[5m])))

# RIGHT
histogram_quantile(0.99, sum by (le) (rate(metric_bucket[5m])))
```

### Cardinality Explosion
```promql
sum by (request_id) (...)   # millions
```

Don't aggregate by high-cardinality.

### Rate of Non-Counter
```promql
rate(gauge[5m])   # wrong
```

Use `delta` / `deriv` for gauges.

## Best Practices

- Aggregate before histogram_quantile
- Sensible windows (4x scrape)
- Avoid high-cardinality `by`
- Test in Grafana / Prom UI
- Build complex from simple

## Common Mistakes

- rate on gauge
- avg of quantiles
- Range vector mismatch
- Wrong join

## Quick Refs

```
Aggregation: sum/avg/min/max/topk/quantile
Modifiers:   by/without
Counter:     rate, irate, increase
Gauge:       delta, deriv
Window:      avg_over_time, max_over_time
Histogram:   histogram_quantile(q, sum by (le) (rate(...)))
```

## Interview Prep

**Mid**: "PromQL basics."

**Senior**: "Histogram quantiles."

**Staff**: "Complex queries."

## Next Topic

→ [T03 — Recording Rules](T03-Recording-Rules.md)
