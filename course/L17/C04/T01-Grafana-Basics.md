# L17/C04/T01 — Grafana: Datasources, Dashboards, Panels

## Learning Objectives

- Build Grafana dashboards
- Query datasources

## Grafana

Visualization platform:
- Multi-datasource
- Dashboards
- Alerts
- Variables

## Install

```bash
helm install grafana grafana/grafana
```

Or:
```bash
docker run -p 3000:3000 grafana/grafana
```

Default: admin/admin.

## Datasources

```
Configuration → Datasources → Add
```

Common:
- Prometheus
- Loki
- Tempo
- InfluxDB
- Elasticsearch
- MySQL / Postgres
- Cloudwatch / Stackdriver / Azure Monitor

## Add Prometheus

```yaml
url: http://prometheus:9090
access: proxy
```

Test connection.

## Dashboard

Panel types:
- Time series (graph)
- Gauge
- Stat
- Bar chart
- Table
- Heatmap
- Logs (from Loki)
- Pie chart
- Histogram
- Geomap

## Create Panel

1. Add panel
2. Select datasource (Prometheus)
3. Query
4. Visualize
5. Title / format

## Query Editor

```promql
sum by (service) (rate(http_requests_total[5m]))
```

Legend: `{{service}}`.

## Time Range

Top right; e.g. Last 1h, Last 24h, etc.

## Refresh

Auto-refresh: 5s, 10s, 1m, etc.

## Variables

Dropdown selectors:
```
Name: service
Type: query
Query: label_values(http_requests_total, service)
```

Use in panels:
```promql
rate(http_requests_total{service="$service"}[5m])
```

Multi-value:
```promql
rate(http_requests_total{service=~"$service"}[5m])
```

For: dynamic dashboards.

## Variable Types

- Query (from datasource)
- Custom (static list)
- Text box
- Constant
- Datasource
- Interval (custom time)
- Ad hoc

## Annotations

Mark events on graphs:
- Deployments
- Incidents
- Releases

```
Query: changes(version_info[1m]) > 0
```

Vertical line on graph.

## Alerting (Grafana)

Or alert via Alertmanager.

Grafana alerting:
```
Edit panel → Alert tab → New alert
```

Or:
```
Alert rules → New alert rule
```

For: simple. Prom Alertmanager more powerful.

## Permissions

Org / team based:
- Admin
- Editor
- Viewer

Per dashboard / folder.

## Dashboard JSON

```
Settings → JSON Model
```

Versioned. Backup-able.

## Provisioning

```yaml
# /etc/grafana/provisioning/dashboards/default.yml
apiVersion: 1
providers:
  - name: default
    folder: ''
    type: file
    options:
      path: /var/lib/grafana/dashboards
```

Auto-load JSON from path.

For: GitOps.

## Plugins

Many community:
- Worldmap (geo)
- Status panel
- Statsd
- Custom data sources

## Folder Structure

Organize:
- Per team
- Per service
- Per role (overview, debug)

## Templating Examples

### Cluster
```
label_values(up, cluster)
```

### Service per cluster
```
label_values(up{cluster="$cluster"}, service)
```

### Time interval
```
$__interval        # auto-calculated
1m,5m,15m,1h       # custom
```

## Use $__interval

```promql
rate(metric[$__rate_interval])
```

Auto-adjusts to time range.

## Stats Panel

```
Reduce: last / max / mean
Color thresholds: 0=green, 100=yellow, 500=red
```

For: single number.

## Tables

Show raw values:
```
Format: Table
```

Multiple columns from labels.

## Heatmap

For latency histograms:
- X: time
- Y: bucket
- Color: density

For: latency distribution over time.

## Best Practices

- Variables (don't hardcode service)
- Sensible color thresholds
- Title clear (what + unit)
- Folders organized
- Provisioning (versioned)
- Snapshot for incidents

## Common Mistakes

- Hardcoded services (rebuilt per env)
- No units (ms vs s)
- Cluttered panels
- Manual dashboards (no Git)
- Wrong color (red for OK)

## Loki Integration

Add datasource: Loki URL.

Query logs:
```
{service="api"} |~ "error"
```

Time-correlate with metrics.

## Tempo

Trace datasource:
- View traces by trace_id
- Link from logs

For: end-to-end.

## Explore

Ad-hoc query view:
- Metrics
- Logs
- Traces
- Side-by-side

For: investigation.

## Quick Refs

```
Datasource: prom / loki / tempo / cloudwatch / ...
Variable:   $name
Template:   {{ label }}
Interval:   $__interval
```

## Interview Prep

**Junior**: "What's Grafana."

**Mid**: "Variables."

**Senior**: "Dashboard design."

**Staff**: "Observability dashboards at scale."

## Next Topic

→ [T02 — Variables & Templating](T02-Variables-Templating.md)
