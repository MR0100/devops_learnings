# L30/C05/T03 — Cost Dashboards

## Learning Objectives

- Visualize cost
- Per-team

## OpenCost

```bash
helm install opencost opencost-charts/opencost
```

Allocates K8s cost:
- Per namespace
- Per pod
- Per label

## Grafana

Datasource: Prometheus (OpenCost metrics).

Dashboards:
- Total cost
- Per team
- Per namespace
- Trends

## Sample Queries

```promql
sum by (namespace) (
  pod_memory_request_avg{} * pod_memory_unit_price
  + pod_cpu_request_avg{} * pod_cpu_unit_price
)
```

For: per-namespace cost.

## Showback

Monthly report:
```
Team A: $20k
Team B: $15k
Team C: $10k
```

Trend up/down.

## CUR + Athena (AWS)

For non-K8s:
```sql
SELECT line_item_resource_tags_user_team, SUM(line_item_unblended_cost)
FROM cur
WHERE month = '2026-01'
GROUP BY 1
ORDER BY 2 DESC
```

## CUDOS

AWS-built dashboards:
- Pre-built
- QuickSight

For: starting point.

## Vantage / Cloudability

Commercial:
- Multi-cloud
- Anomaly detection

## Alerts

```promql
# Budget exceeded
sum(team_cost{team="A"}) > 25000
```

Notify Slack.

## Best Practices

- Per-team visibility
- Tagging strict
- Anomaly alerts
- Quarterly review

## Common Mistakes

- No tagging
- No alerts
- Dashboard nobody sees

## Quick Refs

```
OpenCost: K8s allocation
CUR + Athena: AWS detail
CUDOS: AWS dashboards
Vantage: multi-cloud SaaS
```

## Next Topic

→ Move to [L30/C06 — Portfolio Presentation](../C06/README.md)
