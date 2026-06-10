# L21/C04/T01 — DynamoDB Operations

## Learning Objectives

- Operate DynamoDB
- Tune cost / perf

## DynamoDB

AWS managed NoSQL:
- Key-value + document
- Single-digit ms latency
- Massive scale
- Serverless

## Tables

```bash
aws dynamodb create-table \
  --table-name users \
  --attribute-definitions AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

## Capacity Modes

### On-Demand
Pay per request.
For: unpredictable.

### Provisioned
RCU/WCU reserved.
For: predictable. Cheaper if known.

## Read Capacity Unit (RCU)

1 strongly consistent read of 4 KB / sec.
Or 2 eventually consistent.

## Write Capacity Unit (WCU)

1 write of 1 KB / sec.

## Auto-Scaling

```bash
aws application-autoscaling register-scalable-target \
  --service-namespace dynamodb \
  --resource-id table/users \
  --scalable-dimension dynamodb:table:ReadCapacityUnits \
  --min-capacity 5 --max-capacity 500
```

## Indexes

### Local Secondary
Same partition key; alt sort key.

### Global Secondary
Different partition key.

```bash
aws dynamodb update-table \
  --table-name users \
  --attribute-definitions ... \
  --global-secondary-index-updates ...
```

For: query patterns.

## Single-Table Design

Hot pattern:
- One table per app
- All entities
- PK structured

For: better cost + perf at scale.

## DAX

DynamoDB Accelerator (cache):
- Microsecond reads
- In front of table
- For read-heavy

```bash
aws dax create-cluster ...
```

## Streams

Change data capture:
- Each update emits event
- Lambda trigger

For: replication, analytics.

## Global Tables

Multi-region:
- Active-active
- Last writer wins

For: low latency global.

## Backup

- Continuous backups (PITR)
- On-demand snapshots
- Export to S3

```bash
aws dynamodb create-backup --table-name users --backup-name daily
```

## Restore

```bash
aws dynamodb restore-table-from-backup ...
```

## Cost

- Storage: $0.25/GB/mo
- WCU: $0.00065/hr (provisioned) or $1.25/M (on-demand)
- RCU: $0.00013/hr or $0.25/M

For: tune.

## Hot Partitions

If single partition hot:
- Throttling
- Slow

For: distribute keys (random prefix, hash).

## Best Practices

- On-demand for unpredictable
- Provisioned + auto-scale for steady
- Single-table design at scale
- DAX for read-heavy
- Streams for CDC
- PITR enabled

## Common Mistakes

- Over-provision (cost)
- Hot partition
- Scan operations (use Query)
- No GSI for access pattern

## Quick Refs

```bash
aws dynamodb create-table / put-item / get-item / query / scan
aws dynamodb create-backup
aws dynamodb describe-time-to-live
```

## Interview Prep

**Mid**: "DynamoDB."

**Senior**: "Single-table."

**Staff**: "DynamoDB at scale."

## Next Topic

→ [T02 — MongoDB](T02-MongoDB.md)
