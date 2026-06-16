# L27/C03/T02 — Cross-Region Replication

## Learning Objectives

- Implement cross-region
- Common patterns

(Covered DB-specific in L21/C06/T03.)

## Patterns

### DB
- Streaming (Postgres / MySQL)
- Global tables (DynamoDB)
- Multi-region (Spanner, Cosmos)

### Object Storage
- S3 CRR
- GCS multi-region
- Azure GRS

### Cache
- ElastiCache Global Datastore
- Memorystore replication

### Files
- EFS replication
- Files cross-region

## S3 CRR

```bash
aws s3api put-bucket-replication ...
```

Async; minutes typical lag.

## Aurora Global

```bash
aws rds create-global-cluster ...
```

1-second lag; promote on failure.

## DynamoDB Global Tables

```bash
aws dynamodb update-table --replica-updates '...'
```

Active-active; LWW.

## Lag

Monitor:
- Replication lag metric per service

For: detect drift.

## Cost

Cross-region transfer:
- $0.02-0.04/GB
- For 1 TB/month: $20-40

## Examples

### Multi-Region App
Primary in us-east-1:
- App + DB
Secondary in us-west-2:
- DB replica
- App ready (warm standby)

## Failover

If primary down:
- Promote DB
- Shift DNS / traffic
- Recover

## Bidirectional

For active-active:
- Both directions
- Conflict resolution

## Pub/Sub Cross-Region

Kafka Mirror Maker 2.
Pub/Sub global.

## Best Practices

- Async cross-region
- Monitor lag
- Test failover
- Budget transfer cost

## Common Mistakes

- Sync cross-region (slow)
- No monitoring
- Forget transfer cost
- No failover plan

## Quick Refs

```
DB: Aurora Global, Spanner, DynamoDB Global
S3: CRR
Cache: ElastiCache Global Datastore
Pub/Sub: Global (GCP), Mirror Maker (Kafka)
```

## Interview Prep

**Mid**: "Cross-region replication."

**Senior**: "Implement."

**Staff**: "Multi-region data."

## Next Topic

→ [T03 — Conflict Resolution](T03-Conflict-Resolution.md)
