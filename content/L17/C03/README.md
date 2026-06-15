# L17/C03 — PromQL

## Topics

- **T01 Instant vs Range Vectors** — Core data types in PromQL
- **T02 Aggregation & Functions** — sum, avg, rate, histogram_quantile, etc.
- **T03 Recording Rules** — Precompute expensive queries
- **T04 Alerting Rules** — Conditions that fire alerts

## Vector Types

### Instant Vector
A set of samples at one point in time:
```promql
http_requests_total                              # all series
http_requests_total{service="api"}               # filtered
```

### Range Vector
A series of samples over time window:
```promql
http_requests_total[5m]                          # last 5 minutes
```

Only useful inside functions (rate, increase, etc.) — not directly graphable.

### Scalar
Single number:
```promql
scalar(sum(http_requests_total))
```

### Conversion
- `vector(N)` — scalar to instant vector
- `scalar(V)` — single-element vector to scalar

## Selectors

```promql
metric_name                                      # all series
metric_name{label="value"}                       # exact match
metric_name{label!="value"}                      # not equal
metric_name{label=~"a|b"}                        # regex match
metric_name{label!~"x.*"}                        # regex no match
metric_name{service="api", env="prod"}           # multiple labels (AND)
```

## Rate

```promql
rate(http_requests_total[5m])
# Per-second average over the last 5 min
```

Always use `rate` for counters (which only go up). `irate` for instantaneous (last 2 samples) — noisier.

## Aggregations

```promql
sum(http_requests_total)                                    # sum over all series
sum by (service) (http_requests_total)                      # group by service
sum without (instance) (http_requests_total)                # everything except instance
avg(http_requests_total)
max(http_requests_total)
min(http_requests_total)
count(up == 1)                                              # count of healthy series
```

## Histogram Quantiles

```promql
histogram_quantile(0.95,
  sum by (le, service) (rate(http_request_duration_seconds_bucket[5m]))
)
```

`le` (less-than-or-equal) is the bucket label. Histograms must be aggregated on `le` for quantile to be meaningful.

## Operators

Binary operations apply per-label-set match:

```promql
errors_per_second / requests_per_second                       # ratio
http_requests_total - http_requests_total offset 1d          # diff vs yesterday
http_5xx_total > 100                                          # filter (returns matching)
```

## Time Shifting

```promql
http_requests_total offset 1w                                 # week ago
```

## Subqueries

Rate over rate (less common):
```promql
max_over_time(rate(http_requests_total[5m])[1h:5m])
# Max 5-min rate over the last hour, sampled every 5 min
```

## Recording Rules

Precompute expensive queries:
```yaml
groups:
- name: api_recordings
  interval: 30s
  rules:
  - record: instance:http_requests:rate5m
    expr: rate(http_requests_total[5m])
  - record: service:http_requests:rate5m
    expr: sum by (service) (instance:http_requests:rate5m)
  - record: service:http_request_duration_p95:5m
    expr: |
      histogram_quantile(0.95,
        sum by (le, service) (rate(http_request_duration_seconds_bucket[5m]))
      )
```

Reduces query cost; recorded series live in TSDB.

## Alerting Rules

```yaml
groups:
- name: api
  rules:
  - alert: HighErrorRate
    expr: |
      sum(rate(http_requests_total{status=~"5.."}[5m]))
      / sum(rate(http_requests_total[5m])) > 0.05
    for: 5m
    labels:
      severity: critical
      team: api
    annotations:
      summary: "5% error rate on API"
      description: "{{ $value | humanizePercentage }} 5xx over last 5 min"
      runbook: https://runbooks.example.com/HighErrorRate
```

- `expr` — PromQL condition
- `for` — must be true continuously this long (filters flaps)
- `labels` — added to alert (used for routing in Alertmanager)
- `annotations` — for humans (summary, description, runbook URL)

## SLO Burn Rate Alerts

Multi-window, multi-burn-rate (Google SRE pattern):

```yaml
- alert: SLOBurnFast
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[1h]))
      / sum(rate(http_requests_total[1h]))
    ) > (14.4 * 0.001)
    and
    (
      sum(rate(http_requests_total{status=~"5.."}[5m]))
      / sum(rate(http_requests_total[5m]))
    ) > (14.4 * 0.001)
  for: 2m
  labels: { severity: page }
  annotations: { summary: "SLO burning fast" }
```

Burn rate of 14.4× exhausts a 30-day budget in 2 days. Two windows (1h + 5m) reduce false positives.

## Common Recipes

```promql
# Request rate by service
sum by (service) (rate(http_requests_total[5m]))

# Error percentage
100 * sum by (service) (rate(http_requests_total{status=~"5.."}[5m]))
/ sum by (service) (rate(http_requests_total[5m]))

# p99 latency
histogram_quantile(0.99,
  sum by (le, service) (rate(http_request_duration_seconds_bucket[5m]))
)

# Apdex (target T=0.5s, tolerating threshold 4T=2s)
# satisfied + tolerating/2, all over total.
# Buckets are cumulative, so the tolerating count is le="2" MINUS le="0.5".
(sum(rate(http_request_duration_seconds_bucket{le="0.5"}[5m]))
 + (sum(rate(http_request_duration_seconds_bucket{le="2"}[5m]))
    - sum(rate(http_request_duration_seconds_bucket{le="0.5"}[5m]))) / 2)
/ sum(rate(http_request_duration_seconds_count[5m]))

# Top 5 noisiest hosts
topk(5, sum by (instance) (rate(http_requests_total[5m])))

# Memory usage % per pod
100 * container_memory_working_set_bytes
/ container_spec_memory_limit_bytes

# Pods restarting frequently
sum by (pod) (changes(kube_pod_container_status_restarts_total[1h])) > 5
```

## Interview Themes

- "Walk me through PromQL — instant vs range vector"
- "Write a query for p95 latency"
- "SLO burn-rate alerts — explain"
- "Recording rules — when?"
- "Why use rate() for counters?"
