# L17/C03/T03 — Recording Rules

## Learning Objectives

- Use recording rules
- Precompute expensive queries

## Recording Rule

Pre-evaluates expression; stores result as new metric:
```yaml
groups:
  - name: service-rules
    interval: 30s
    rules:
      - record: service:requests:rate5m
        expr: sum by (service) (rate(http_requests_total[5m]))
```

## Why

- Speed up dashboards
- Cache expensive queries
- Aggregate for downstream

For: complex multi-series.

## Naming Convention

```
level:metric:operation
```

Examples:
- `instance:cpu_usage:rate1m`
- `service:requests:rate5m`
- `cluster:memory:sum`

## Config

```yaml
# alerts-rules.yml
groups:
  - name: aggregations
    interval: 30s
    rules:
      - record: service:requests:rate5m
        expr: |
          sum by (service) (rate(http_requests_total[5m]))

      - record: service:errors:rate5m
        expr: |
          sum by (service) (rate(http_requests_total{code=~"5.."}[5m]))

      - record: service:error_ratio
        expr: |
          service:errors:rate5m / service:requests:rate5m
```

```yaml
# prometheus.yml
rule_files:
  - 'alerts-rules.yml'
```

## Reload

```bash
curl -XPOST http://prom:9090/-/reload
```

## Evaluation Interval

Default: `evaluation_interval` (15s).
Override per group:
```yaml
groups:
  - name: slow
    interval: 5m
```

For: heavy queries.

## Use in Dashboards

```promql
service:requests:rate5m
```

Fast; no re-aggregation.

## Use in Alerts

```yaml
- alert: HighErrorRate
  expr: service:error_ratio > 0.05
```

Lighter than computing from scratch.

## Chain Rules

```yaml
- record: pod:cpu:rate
  expr: rate(container_cpu_seconds_total[5m])

- record: namespace:cpu:sum
  expr: sum by (namespace) (pod:cpu:rate)
```

Layer aggregations.

## Validation

```bash
promtool check rules rules.yml
```

For: pre-commit.

## When Recording Rules

- Query used many places (dashboards, alerts)
- Slow to compute
- Aggregates across many series

## When Not

- One-off
- Cheap query
- Cardinality already low

## Anti-Patterns

### Record High-Cardinality
```promql
sum by (user_id) (rate(...))
```

Bad: explodes series.

### Over-Recording
Every query recorded. Bloat.

For: balance.

## Performance

Eval cost:
- During each interval, all rules execute
- Aggregate dependencies (chained)

Heavy rules: increase interval (slower update).

## Group Order

Rules in a group: sequential.
Across groups: parallel.

For: same-group rules can depend on each other.

## Kubernetes Examples

```yaml
- record: namespace:kube_pod_container_resource_requests:cpu
  expr: |
    sum by (namespace, pod) (
      kube_pod_container_resource_requests{resource="cpu"}
    )

- record: node:node_cpu_utilization:ratio_rate1m
  expr: |
    1 - (
      sum by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m]))
      /
      count by (instance) (rate(node_cpu_seconds_total[1m]))
    )
```

For: dashboards.

## Operator (kube-prometheus-stack)

PrometheusRule CRD:
```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: service-rules
spec:
  groups:
    - name: service
      interval: 30s
      rules:
        - record: ...
          expr: ...
```

Operator auto-reloads Prom.

## Best Practices

- Naming convention strict
- For shared queries
- Validate via promtool
- Track rule eval time
- Limit chained depth (debug pain)
- Document each rule

## Common Mistakes

- High-cardinality recorded
- Too many rules
- No naming convention
- Skip validation
- Chained too deep

## Performance Monitoring

```promql
prometheus_rule_evaluation_duration_seconds
prometheus_rule_evaluations_total
prometheus_rule_evaluation_failures_total
```

For: monitor rule perf.

## Quick Refs

```yaml
groups:
  - name: NAME
    interval: 30s
    rules:
      - record: namespace:metric:op
        expr: PROMQL_EXPRESSION
```

```bash
promtool check rules FILE.yml
curl -XPOST /-/reload
```

## Interview Prep

**Mid**: "What's a recording rule."

**Senior**: "Naming convention."

**Staff**: "Rule architecture."

## Next Topic

→ [T04 — Alerting Rules](T04-Alerting-Rules.md)
