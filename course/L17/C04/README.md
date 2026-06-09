# L17/C04 — Grafana

## Topics

- **T01 Datasources, Dashboards, Panels** — Core Grafana model
- **T02 Variables & Templating** — Dynamic dashboards
- **T03 Provisioning Dashboards as Code** — GitOps for dashboards
- **T04 Loki, Tempo, Mimir** — Grafana's open observability stack

## Datasources

Grafana queries from any backend:
- **Prometheus / Mimir / Cortex / Thanos / VictoriaMetrics** (metrics)
- **Loki** (logs)
- **Tempo / Jaeger / Zipkin** (traces)
- **Pyroscope** (profiles)
- **Elasticsearch / OpenSearch** (logs)
- **InfluxDB** (time series)
- **CloudWatch / Stackdriver / Azure Monitor**
- **Postgres / MySQL** (ad-hoc tables)
- **Datadog, New Relic** (commercial backends)

One Grafana, many datasources.

## Dashboards

A dashboard is JSON with:
- Title, tags
- Variables (templating)
- Rows
- Panels (visualizations + queries)

### Panel Types
- Time series (line / area / bar)
- Stat (single value)
- Gauge
- Table
- Logs (for Loki)
- Trace view (for Tempo)
- Heatmap
- Pie chart
- State timeline

## Variables

Make dashboards reusable across environments / services:
```
$service     → query Prometheus: label_values(http_requests_total, service)
$namespace   → query: label_values(kube_namespace_labels, namespace)
$interval    → interval: 1m, 5m, 1h (manual)
$cluster     → custom values: prod-us, prod-eu, staging
```

Use in queries:
```promql
sum(rate(http_requests_total{service="$service"}[$interval]))
```

Dropdowns at the top of the dashboard.

## Annotations

Vertical lines on time-series showing events:
- Deploys (from CI webhook)
- Incidents (from PagerDuty)
- Releases

Powerful for "did this change correlate with that issue?"

## Provisioning as Code

Don't make dashboards in the UI — they get lost / drift.

### Sources of truth
- JSON in Git
- Grafonnet (Jsonnet library)
- terraform-grafana-provider
- Helm chart deploying dashboards as ConfigMaps

### Provisioning Config
```yaml
# /etc/grafana/provisioning/dashboards/app.yaml
apiVersion: 1
providers:
  - name: 'app'
    folder: 'Application'
    type: file
    options:
      path: /var/lib/grafana/dashboards
```

Dashboards in `/var/lib/grafana/dashboards/*.json` auto-load.

### K8s Sidecar Pattern
Run a sidecar in Grafana pod watching for ConfigMaps with a specific label; auto-extract dashboard JSON. Used in kube-prometheus-stack.

## Alerting (Grafana 8+)

Grafana has its own alerting engine that:
- Queries any datasource (not just Prometheus)
- Unified UI for alerts
- Routes to contact points (Slack, PagerDuty, etc.)

Some teams still use Alertmanager for Prometheus alerts (more powerful routing); others go Grafana-only.

## Loki

Log aggregation, "like Prometheus but for logs". Indexes only labels (low cardinality).

```
{job="myapp"} |= "error"                              # contains
{job="myapp"} | json | level="error"                  # parse JSON, filter
sum by (level) (count_over_time({job="myapp"}[5m]))   # rate of logs
```

Backed by object storage (S3-cheap).

## Tempo

Distributed traces, backed by object storage. Query by trace ID or via service map.

```
{ resource.service.name = "checkout" && duration > 500ms }
```

Pairs with Grafana exemplars: metrics chart shows dots that link to traces.

## Mimir / Cortex

Multi-tenant Prometheus at scale. Mimir is Grafana's actively-developed fork.

## Pyroscope

Continuous profiling. Flame graphs over time. eBPF-based or SDK-based.

## "Single Pane of Glass" (LGTM Stack)

Grafana + Loki + Tempo + Mimir + Pyroscope. All from Grafana Labs. Single UI for metrics + logs + traces + profiles.

## Best Practices

- **Provision as code**
- **Variables**: minimize hardcoded service names
- **Sensible time defaults**: not "last 24h" for high-rate dashboards
- **Annotations**: deploys, incidents
- **Folders**: organize by team/domain
- **RBAC**: per-folder permissions
- **Datasource templating**: same dashboard across prod/staging

## Interview Themes

- "Walk me through dashboard provisioning as code"
- "Variables — how do you make a reusable dashboard?"
- "LGTM stack — what is it?"
- "Grafana alerting vs Alertmanager"
- "Loki vs ELK"
