# L17/C04/T02 — Grafana Variables & Templating

## Learning Objectives

- Use variables effectively
- Build reusable dashboards

## Variable Types

### Query
Dynamic from datasource:
```
label_values(up, instance)
```

### Custom
Static list:
```
prod, staging, dev
```

### Constant
Single value; not in URL.

### Datasource
Pick datasource.

### Interval
```
1m,5m,15m,1h
```

### Ad hoc
Filter applied to all queries.

### Text Box
Free input.

## Query Variable

```
Datasource: Prometheus
Query: label_values(metric, label_name)
```

Examples:
```
label_values(up, instance)      # all instances
label_values(up{job="api"}, instance)  # filtered
```

## Use Variable

In panel:
```
rate(http_requests_total{instance="$instance"}[5m])
```

## Multi-Select

```
Selection: Multi-value
Include All: yes
Custom all value: .+
```

In query:
```
rate(metric{instance=~"$instance"}[5m])
```

`=~` for regex; multi works.

## Chained Variables

Cluster → service → pod:
```
$cluster = label_values(up, cluster)
$service = label_values(up{cluster="$cluster"}, service)
$pod     = label_values(up{cluster="$cluster", service="$service"}, pod)
```

For: progressive filter.

## Repeating Panels

```
Panel options → Repeat by variable: instance
```

One panel per value.

For: per-instance dashboards.

## Repeating Rows

Similar for whole rows.

## Built-in Variables

```
$__interval         # auto from time range
$__rate_interval    # for rate functions
$__from / $__to     # epoch start/end
$__timezone
$__dashboard
$__org
$__user.login
```

## $__rate_interval

```promql
rate(metric[$__rate_interval])
```

Grafana auto-calculates:
- 4 × scrape interval if range small
- bigger for larger time ranges

For: smart rate.

## Variable Refresh

- Never (cached)
- Dashboard load
- Time range change

For: stale or fresh.

## Show on Dashboard

- Visible (dropdown)
- Hidden (used in queries but not visible)

For: simplify UI.

## URL Variables

```
?var-service=api&var-env=prod
```

Shareable links.

## Use in Annotations

```promql
changes(version_info{service="$service"}[1m]) > 0
```

For: deploys per service.

## Template Examples

### Multi-Cluster
```
$cluster = label_values(up, cluster)
$namespace = label_values(up{cluster="$cluster"}, namespace)
$deployment = label_values(kube_deployment_status_replicas{cluster="$cluster", namespace="$namespace"}, deployment)
```

### Geographic
```
$region = label_values(metric, region)
$az = label_values(metric{region="$region"}, az)
```

### Per-Tenant
```
$tenant = label_values(metric{}, tenant)
```

## Best Practices

- Cluster + env at top
- Chained naturally
- Multi-select where useful
- Hidden vars for internal logic
- Refresh on dashboard load

## Common Mistakes

- No All option (when needed)
- Variable cardinality huge (slow query)
- Hardcoded values
- Inconsistent naming

## Cardinality Pitfall

```
$pod = label_values(metric, pod)
```

Millions of pods → slow.

Mitigate: filter first:
```
label_values(metric{cluster="$cluster", namespace="$namespace"}, pod)
```

## Datasource Variable

```
$datasource = type: prometheus
```

Switch dashboard between dev/staging/prod datasources.

For: same dashboard, different env.

## Variable Inspection

Edit dashboard → variable shows current value + options.

For: debug.

## Filter Helpers

Use variable in queries to scope:
```promql
sum by (service) (rate(http_requests_total{cluster="$cluster"}[$__rate_interval]))
```

Cluster scope.

## Apply All

For multi-select with "All":
```
custom all value: .*
```

Then in query:
```promql
metric{instance=~"$instance"}
```

`$instance` becomes `.*` for all.

## Repeating Per Variable

```
Repeat by: cluster
```

Per cluster, one panel.

Useful for:
- Per-region dashboards
- Per-service dashboards
- Per-tenant

## Best Templating Pattern

```
Cluster dropdown → All
Namespace → Multi  
Service   → Multi
Detail panels per service
```

## Quick Refs

```
Variable: $name
Multi-value: =~"$name"
Built-in: $__interval, $__rate_interval, $__from, $__to
Filter:   label_values(metric{label="$other"}, target)
Repeat:   panel/row option
```

## Interview Prep

**Mid**: "Grafana variables."

**Senior**: "Templating strategies."

## Next Topic

→ [T03 — Provisioning Dashboards as Code](T03-Dashboards-as-Code.md)
