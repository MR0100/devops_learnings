# L09/C03/T04 — Data Gravity & Egress Cost Traps

## Learning Objectives

- Understand data gravity
- Avoid egress surprises

## Data Gravity

Data is hard to move:
- Big
- Generative (creates more)
- Apps accrue around it
- Moving = expensive + slow

So: compute follows data.

## Egress Pricing

Out of cloud: charged.
- AWS: $0.05-0.09/GB
- GCP: $0.08-0.12/GB
- Azure: $0.05-0.087/GB
- Inter-region: lower but still real

In-cloud / same-region: usually free.

## Why Hyperscalers Charge

- Capacity (real bandwidth cost)
- Lock-in (incentive to stay)
- Recovery of inbound subsidies

Industry pressure: declining slowly. EU regulation.

## Real Cost Example

Migrate 1 PB out of AWS:
```
1 PB * $0.09/GB = $90,000+
```

Per month. Ongoing if continuous transfer.

## Same-Region Multi-Cloud

Megaport in same data center:
- AWS us-east-1 ↔ Azure eastus2 (same DC)
- Egress reduced (~$0.02/GB or less)

For: cross-cloud serious workloads.

## Egress Hot Spots

### Backups
DR to other cloud: continuous outbound.

### Analytics
Query data across clouds: each query = egress.

### CDN
CDN pulls from origin: subject to egress (though discounted).

### Replication
DB cross-region: per-write egress.

### Logs / Metrics
Sending to off-cloud SIEM: egress.

## Mitigations

### Co-locate
Put compute and data in same cloud + region.

### Caching
Cache reads locally; reduce origin pulls.

### Compression
gzip before transfer.

### Deduplication
For backups: dedup tools.

### Cloud-Specific Discounts
- AWS CloudFront discount with commit
- GCP Network Service Tiers (cheaper)

### Negotiate
Volume → discount.

## CloudFront Discount

CloudFront egress: cheaper than direct S3 egress.
And: AWS waives data transfer from S3 to CloudFront.

Use CDN even if no caching benefit.

## EU Regulation

EU Data Act (2024+):
- Cloud providers must allow data egress
- Reduced fees over time
- Cloud lock-in mitigation

Result: egress fees declining.

## AWS Free Egress for Leavers

AWS / Azure / GCP have announced free egress when leaving the cloud (limited cases).

For: migrations.

## Inter-Region

Cheaper than Internet egress but real:
- AWS us-east → us-west: $0.02/GB
- Cross-continent: more

For: replication budgets matter.

## VPC Endpoint / Private Endpoint

Direct internal access to managed services:
- S3 via VPC Endpoint: avoids NAT, free
- GCS via Private Service Connect: similar
- Azure Private Endpoint: similar

For: huge savings for intra-cloud API calls.

## Examples of Traps

### Trap 1: Cross-Cloud Replicate
```
Postgres in AWS RDS → read replica in GCP Cloud SQL
1 TB/day writes → $90/day egress = $2700/mo
```

Better: put both on same cloud or use logical replication with batching.

### Trap 2: SIEM Off-Cloud
```
1 TB/day logs → Splunk on-prem
Egress: $90/day = $2700/mo
```

Better: SIEM in same cloud.

### Trap 3: CDN Origin
```
CDN cache miss → origin pull
For uncacheable content: egress on every request
```

Better: tune cache; use compression.

### Trap 4: Backup to Other Cloud
```
100 TB / month backup AWS → GCS
$9000/mo egress
```

Better: backup within same cloud (cross-region).

## Egress Monitoring

### AWS
Cost Explorer + Athena queries on CUR (Cost and Usage Reports).

### GCP
Billing exports to BigQuery.

### Azure
Cost Management.

Alerts:
```
If egress > X TB/day → page
```

## Tools

- Vantage
- CloudZero
- Finout
- Open source: OpenCost

For: cost visibility.

## Architecture Patterns

### Hub-Spoke Storage
Hub: central data lake.
Spokes: compute close.

Move compute, not data.

### Event-Driven Replication
Pub/Sub on data write → small events to other cloud (not full data).

### Federated Queries
Query data in place; don't move.

E.g. BigQuery external tables on S3 (now: BigQuery Omni).

## BigQuery Omni

Query Azure / S3 data from BigQuery.

For: avoid data movement.

## Snowflake Cross-Cloud

Snowflake runs on any cloud; replicates between.

For: portability without lock-in.

## Best Practices

- Place compute near data (same cloud + region)
- Use Private Endpoints (no NAT egress)
- CDN for static
- Egress alerts
- Quarterly egress audit
- Avoid hot-path cross-cloud

## Common Mistakes

- Cross-cloud architecture without egress budget
- No alerts (surprise bills)
- SIEM off-cloud (continuous egress)
- DR to expensive other cloud
- Manual data moves for "flexibility"

## Cost Allocation

Tag egress by source:
```bash
# Cost Explorer
filter: usageType=DataTransfer-Out-Bytes
group by: tag:project
```

Charge to project owners.

## Audit

```sql
-- AWS CUR
SELECT line_item_usage_type, SUM(line_item_blended_cost)
FROM aws_billing
WHERE line_item_usage_type LIKE '%Out-Bytes%'
GROUP BY line_item_usage_type
ORDER BY 2 DESC;
```

For: identify top egress.

## Quick Refs

```
Same region same cloud: free
Cross-region same cloud: $0.02-0.04/GB
Cross-cloud via Internet: $0.05-0.12/GB
Cross-cloud via Megaport: $0.02-0.03/GB
```

## Interview Prep

**Mid**: "What's egress."

**Senior**: "Cross-cloud cost optimization."

**Staff**: "Architecture to minimize egress."

**Principal**: "Multi-cloud TCO including egress."

## Next Topic

→ Move to [L09/C04 — Service-by-Service Comparison](../C04/README.md)
