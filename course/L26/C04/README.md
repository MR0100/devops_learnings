# L26/C04 — Storage Optimization

## Topics

- **T01 S3 Storage Class Analysis** — Find what to tier
- **T02 Intelligent Tiering** — Auto-tier
- **T03 Snapshot Cleanup** — Silent cost

## S3 Tiering

| Class | Use | Cost/GB-mo |
|---|---|---|
| Standard | Frequent | $0.023 |
| Intelligent-Tiering | Variable | $0.023 + $0.0025/1K objects |
| Standard-IA | Infrequent | $0.0125 |
| One Zone-IA | Single AZ IA | $0.01 |
| Glacier Instant | Archive ms retrieval | $0.004 |
| Glacier Flexible | Archive hours | $0.0036 |
| Glacier Deep Archive | 12+ hours | $0.00099 |

### Intelligent-Tiering
- Auto-moves objects between tiers based on access pattern
- $0.0025/1000 objects monitoring fee
- Best when access patterns unknown / variable
- Avoid for: tiny objects (monitoring fee dominates)

### Lifecycle Policies
```json
{
  "Rules": [{
    "ID": "log-lifecycle",
    "Status": "Enabled",
    "Filter": {"Prefix": "logs/"},
    "Transitions": [
      {"Days": 30, "StorageClass": "STANDARD_IA"},
      {"Days": 90, "StorageClass": "GLACIER_IR"},
      {"Days": 365, "StorageClass": "DEEP_ARCHIVE"}
    ],
    "Expiration": {"Days": 2555}
  }]
}
```

### Common Wins
- Logs: Standard → IA at 30 days → Glacier at 90
- Backups: lifecycle to Glacier Deep Archive
- Old user uploads: Intelligent-Tiering

## Snapshot Hygiene

EBS / RDS snapshots are silent cost growers.

### Per-Snapshot Cost
- EBS snapshot: $0.05/GB-mo (incremental; deltas only)
- RDS snapshot: ~free for first 100% of instance size; then $0.095/GB-mo

### Retention Policy
- Daily for 7 days
- Weekly for 4 weeks
- Monthly for 12 months
- Quarterly for years (compliance)

### Cleanup
- AWS Backup with lifecycle rules
- Custodian policies to delete old snapshots
- Tag snapshots with retention class; cleanup by tag

## Unattached Volumes

Resources accumulate:
- Terminated instances leave EBS volumes
- Old database backups not deleted

### Detection
```bash
aws ec2 describe-volumes --filters Name=status,Values=available
```

### Action
- Snapshot before delete (insurance)
- Delete after 30 days unattached

## Elastic IPs

$0.005/hr when NOT associated with running instance. Forgotten EIPs = waste.

```bash
aws ec2 describe-addresses --query 'Addresses[?!Association]'
```

Release if not needed.

## CloudWatch Logs

Per-GB ingest ($0.50) + per-GB storage ($0.03) + per-GB Insights query ($0.005).

### Optimization
- Set retention (default never expire — disastrous)
- Drop noisy logs at source (Fluent Bit filters)
- Move historical to S3 (subscription filter → Kinesis → S3)
- Use Loki/ELK for high volume (cheaper at scale)

```bash
aws logs put-retention-policy --log-group-name X --retention-in-days 30
```

## Data Transfer

Egress is expensive:
- To Internet: $0.05-0.09/GB
- Cross-region: $0.02/GB
- Cross-AZ: $0.01/GB each direction

### Cross-AZ Trap
Microservice chatter across AZs adds up.
- Topology-aware routing (K8s `internalTrafficPolicy: Local`)
- Topology spread + locality preferences
- Per-AZ caches

### NAT GW Data Processing
$0.045/GB for traffic through NAT GW.
- Use VPC Gateway Endpoints (S3, DynamoDB) — free
- Interface Endpoints (cheaper than NAT for AWS API calls)

## EBS Type Choice

| Type | Cost/GB-mo | IOPS | Throughput |
|---|---|---|---|
| gp3 | $0.08 | 3K baseline (provisionable to 16K) | 125 MB/s (to 1000) |
| gp2 | $0.10 | scaled with size | scaled |
| io2 | $0.125 + IOPS | up to 256K | high |
| st1 | $0.045 | low | 500 MB/s |
| sc1 | $0.015 | low | low |

**gp2 → gp3 migration**: 20% cheaper + provision IOPS independently. Most workloads benefit.

## Database Storage

- Right-size DB instances
- Use Aurora storage tier (auto-scaling)
- Archive old data (cold storage, then delete from main DB)
- Compress columns where possible

## Lambda Storage

- Function package size
- /tmp size (up to 10GB, but pay)
- EFS attached to Lambda (cheap shared storage)

## Network Cost Breakdown

Surprises often:
1. NAT GW data processing
2. Cross-AZ chatter
3. Inter-region replication
4. Egress to Internet from chatty services

Tools:
- VPC Flow Logs → Athena → top talkers
- AWS Cost Explorer cost by usage type

## Interview Themes

- "S3 lifecycle — design"
- "Snapshot cleanup strategy"
- "EBS gp2 vs gp3"
- "Cross-AZ chatter — diagnose and fix"
- "Common storage waste"
