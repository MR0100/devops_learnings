# L26/C02 — Cost Visibility

## Topics

- **T01 Cost Allocation Tags** — Attribute spend
- **T02 Showback vs Chargeback** — Accountability models
- **T03 Tools (CUR + Athena, CUDOS, Cloudability, Vantage)** — Implementations
- **T04 Unit Economics (Cost per Request & per Tenant)** — Normalize spend by value

## Tagging Strategy

Without tags, you can't allocate. Strategy:

### Required Tags (enforced)
- `team` (which team owns)
- `env` (prod / staging / dev)
- `cost-center` (finance grouping)
- `product` (which product/service)
- `managed-by` (terraform / manual / etc.)
- `created-by` (user or automation)

### Recommended
- `service-tier` (tier-1/2/3 for SLO)
- `data-class` (sensitivity)
- `lifecycle` (temporary/permanent)

### Enforcement
- SCPs / Organization Policies block resource creation without tags
- Tag policies for normalization (capitalize "Team" consistently)
- AWS Config / Cloud Custodian to flag/remediate

### Activating Cost Tags (AWS)
Required step: Billing → Cost Allocation Tags → activate each tag. Cost data takes 24h to appear after activation.

## Untaggable Costs

Some costs don't tag:
- Egress (per-flow, not per-resource)
- NAT GW data processing
- LB-hours (sometimes assignable, sometimes not)
- Backup storage cross-region

Apportion via heuristics: assign to team that owns the source/destination.

## Showback vs Chargeback

### Showback
- Show each team their cost
- No financial reckoning
- Awareness, not penalty
- First step in FinOps maturity

### Chargeback
- Bill each team for their cost
- Financial accountability
- Internal cross-charging
- Mature orgs

Most orgs: showback first; chargeback later if culture supports.

## Cost & Usage Report (CUR)

AWS detailed billing data (hourly, per-resource).
- Delivered to S3 daily
- Massive (TBs/year for large orgs)
- Queryable via Athena

### Setup
```
Billing Console → Cost & Usage Reports → Create report
Format: Parquet (recommended)
Granularity: HOURLY
Resource IDs: Include
Time granularity: HOURLY
```

### Athena Query Example
```sql
SELECT
  line_item_resource_tags['user_team'] AS team,
  product_servicecode AS service,
  ROUND(SUM(line_item_unblended_cost), 2) AS cost_usd
FROM cur
WHERE year='2026' AND month='06'
GROUP BY 1, 2
ORDER BY cost_usd DESC
LIMIT 50;
```

## CUDOS Dashboards (AWS)

AWS-published QuickSight dashboards using CUR. Free.
- Cost trend by service
- Top resources
- RI/SP coverage
- Unused resources

Deploy via the [Cloud Intelligence Dashboards](https://github.com/aws-samples/aws-cudos-framework-deployment) framework.

## Commercial Tools

### Vantage
- Modern UX
- Multi-cloud
- Anomaly detection
- Kubecost integration

### Cloudability (Apptio)
- Mature; enterprise
- Anomaly detection
- Optimization recommendations

### Cloud Custodian (OSS)
- Policy engine
- Auto-remediation (stop idle resources, etc.)

### Steampipe + Athena
- SQL over cloud APIs and CUR
- Free / OSS
- Powerful for ad-hoc analysis

## Real-Time vs Batch

CUR is daily; not real-time. For anomaly detection:
- AWS Cost Anomaly Detection (free, ML-based)
- Real-time metrics from Vantage / Cloudability

## Per-Service Cost Attribution

Beyond tags, derive cost per service via:
- Resource grouping (all EC2 with tag → service X)
- Network attribution (egress from VPC → service X)
- DB attribution (queries per service via tags or routing)

K8s adds complexity: shared infrastructure, per-pod attribution. Kubecost solves this.

## Cost Dashboards Per Team

Each team gets:
- Last 30 days cost trend
- Top resources
- Anomalies
- RI/SP utilization (their resources)
- Forecast next month
- Budget remaining

Make it part of regular work, not occasional review.

## Engineering Workflow Integration

Surface cost where decisions are made:
- **PR**: Infracost shows cost delta of a PR
- **Slack**: weekly cost report bot
- **Grafana**: cost dashboards alongside operational ones
- **Backstage**: service catalog with current cost

If engineers don't see cost, they can't optimize it.

## Common Visibility Gaps

- Untagged resources (~30-50% in many orgs)
- Cross-account spend (org-level CUR helps)
- Marketplace charges (separate from infra)
- Reserved Instance "leakage" (one team's RI helping another's bill)
- DataDog / Splunk ingest costs (not always in cloud bill)

Plug these gaps systematically.

## Interview Themes

- "Tagging strategy"
- "Showback vs chargeback"
- "CUR — what's in it?"
- "Allocate K8s costs"
- "Untaggable costs — handle?"
