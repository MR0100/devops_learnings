# L26/C02/T03 — Cost Tools (CUR + Athena, CUDOS, Cloudability, Vantage)

## Learning Objectives

- Use cost tools
- Build reports

## AWS Cost & Usage Report (CUR)

Most detailed:
- Per-resource
- Per-hour
- All costs

Setup:
```bash
aws billing create-report-definition ...
```

Delivered to S3.

## Athena on CUR

Query SQL:
```sql
SELECT product_servicename, SUM(line_item_unblended_cost) AS cost
FROM aws_cur
WHERE month = '2026-01'
GROUP BY product_servicename
ORDER BY cost DESC;
```

## CUDOS

AWS-built dashboards:
- Pre-built QuickSight
- CUR-powered
- Free

For: starting point.

## Vantage

Multi-cloud SaaS:
- Combined view
- Anomaly detection
- Budgets

For: managed; cross-cloud.

## CloudHealth (VMware)

Enterprise:
- Multi-cloud
- Governance
- Recommendations

For: enterprise.

## Cloudability (Apptio)

Similar:
- Reports
- Optimization
- TBM (Technology Business Management)

## OpenCost

K8s-focused open source:
- Per-namespace cost
- Workload cost
- Multi-cloud

For: K8s allocation.

## Kubecost

Built on OpenCost:
- UI
- More features (paid)

## CloudZero

Modern cost intelligence.

## ProsperOps

Auto-managed Savings Plans / RIs.

## Native Tools

- AWS Cost Explorer (basic)
- Azure Cost Management
- GCP Billing Reports

For: free; basic.

## Choose

| | Native | CUR + Athena | Vantage | CloudHealth |
|---|---|---|---|---|
| Cost | free | low (Athena) | $$ | $$$ |
| Multi-cloud | no | no | yes | yes |
| Custom reports | no | yes | some | yes |
| K8s | no | no | basic | partial |

For: start native; add tools as needed.

## CUDOS Dashboards

Free; powerful:
- Cost trends
- Top spenders
- Anomalies

Deploy:
```bash
git clone aws/cudos-dashboards
# Follow CloudFormation deploy
```

## Build Custom

CUR + Athena + Grafana:
- Cheap
- Flexible
- Tailored

## Reports

- Per service
- Per team
- Per project
- Trend
- Anomalies

## Alerts

```
If team cost > budget × 1.1: alert
```

Via SNS / Slack.

## Best Practices

- CUR + Athena for detail
- CUDOS for visualization
- Vantage / CloudHealth for managed
- Anomaly alerts
- Regular review

## Common Mistakes

- Cost Explorer only (limited)
- No anomaly detection
- One-time look (no continuous)

## Quick Refs

```sql
-- CUR query
SELECT product_servicename, SUM(line_item_unblended_cost)
FROM aws_cur
WHERE ...
GROUP BY ...
```

```bash
# Cost Explorer
aws ce get-cost-and-usage --time-period Start=...,End=... --granularity MONTHLY --metrics UnblendedCost
```

## Interview Prep

**Mid**: "Cost tools."

**Senior**: "CUR analysis."

**Staff**: "FinOps tooling."

## Next Topic

→ Move to [L26/C03 — Compute Optimization](../C03/README.md)
