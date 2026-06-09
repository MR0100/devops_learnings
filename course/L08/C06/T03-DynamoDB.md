# L08/C06/T03 — DynamoDB Deep Dive (Partition Keys, GSI, LSI)

## Learning Objectives

- Design DynamoDB schemas
- Use indexes correctly

## DynamoDB

Fully managed key-value + document. Predictable single-digit ms latency at any scale.

## Tables

- Primary key: partition key (PK), optionally sort key (SK)
- Items: up to 400 KB
- Attributes: any type (S, N, B, BOOL, M, L, NULL, SS, NS, BS)

```bash
aws dynamodb create-table \
  --table-name Users \
  --attribute-definitions AttributeName=user_id,AttributeType=S \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

## Partition Key

Hash → partition.

Equal access across partitions → optimal.
Skewed → hot partition (throttling).

E.g., `user_id`: probably good distribution.
`country`: bad (most users US; one partition hot).

## Sort Key (Optional)

Range within partition:
```
PK=USER#alice, SK=PROFILE
PK=USER#alice, SK=ORDER#1
PK=USER#alice, SK=ORDER#2
PK=USER#alice, SK=ORDER#3
```

Query returns range:
```
Query PK=USER#alice, SK begins_with ORDER#
```

## Single-Table Design

Store many entity types in one table; PK/SK encode entity:
- USER#alice / PROFILE
- USER#alice / ORDER#1
- ORDER#1 / DETAIL
- PRODUCT#xyz / DETAIL

Powerful but advanced.

## Capacity Modes

### On-Demand
Pay per request:
- $1.25/M writes
- $0.25/M reads (eventual)
- $0.50/M reads (strong)

No capacity planning. Auto-scales.

For: unknown load, spiky.

### Provisioned
Set RCU/WCU; cheaper steady-state:
- 1 WCU = 1 write/sec of 1 KB
- 1 RCU = 2 eventually-consistent reads/sec of 4 KB

Auto-scaling available.

For: predictable.

Roughly: provisioned cheaper if 30%+ utilization.

## Consistency

- **Eventually consistent** (default): 1 RCU; lower latency
- **Strongly consistent**: 2× RCU; can't read across replicas

For most: eventual fine. For balance / counter / etc.: strong.

## Reads

```python
# Get
response = table.get_item(Key={"user_id": "alice"})
item = response["Item"]

# Query (PK + optional SK)
response = table.query(
    KeyConditionExpression=Key("user_id").eq("alice"),
)

# Scan (avoid)
response = table.scan()    # reads entire table; expensive
```

Always prefer Query over Scan.

## Writes

```python
# Put
table.put_item(Item={"user_id": "alice", "name": "Alice"})

# Update
table.update_item(
    Key={"user_id": "alice"},
    UpdateExpression="SET age = :a",
    ExpressionAttributeValues={":a": 30}
)

# Delete
table.delete_item(Key={"user_id": "alice"})

# Conditional
table.put_item(
    Item={...},
    ConditionExpression="attribute_not_exists(user_id)"
)
```

## GSI (Global Secondary Index)

Alternate access pattern. Different PK / SK.

```
Base table: PK=user_id
GSI1: PK=email, SK=created_at
```

Query by email via GSI.

Cost: extra storage + writes (every base write replicates to GSI).

Up to 20 GSIs per table.

Eventually consistent only.

## LSI (Local Secondary Index)

Same PK; different SK.

```
Base: PK=user_id, SK=created_at
LSI: PK=user_id, SK=order_status
```

Up to 5 LSIs. Must be created at table creation; can't add later.

Strongly consistent option.

Most use GSIs; LSIs less flexible.

## Capacity Per Index

Each GSI has own RCU/WCU (provisioned mode).

## Cost Calculation

For 1000 items, each 1 KB, 100 reads/sec eventual, 50 writes/sec:
- Provisioned: 50 WCU, 50 RCU (eventual)
- $0.00065/WCU/hr × 50 × 24 × 30 = $23/mo write
- $0.00013/RCU/hr × 50 × 24 × 30 = $4.6/mo read
- Storage: 1 GB × $0.25 = $0.25
- Total: ~$28/mo

On-demand:
- 100 × 3600 × 24 × 30 / 1M × $0.25 = $65/mo reads
- 50 × 3600 × 24 × 30 / 1M × $1.25 = $162/mo writes
- Total: $227/mo

Provisioned much cheaper at steady.

On-demand wins when sporadic.

## Hot Partition

If one PK gets disproportionate traffic: that partition throttles.

DynamoDB internally has many partitions; even distribution of work = optimal.

Solutions:
- Better PK design
- Random suffix (write-shard pattern):
  - Original PK: country=US
  - Sharded: PK=US#1, US#2, ... US#10 (random)
  - Read: aggregate across shards
- Adaptive capacity (some hot partition absorbed)

## Adaptive Capacity

DynamoDB auto-redistributes capacity to hot partitions when possible. Doesn't always save.

## Throttling

If exceed capacity: ProvisionedThroughputExceededException.

Mitigation:
- Backoff retry
- More capacity
- Better key design

## Backups

PITR: any second within 35 days; restore as new table.
On-demand: persist beyond.

Restore creates new table. Source untouched.

## Streams

Change data capture. 24-hr retention.

```
Item created/modified/deleted → Stream record
```

Trigger:
- Lambda
- Kinesis
- Replicate to other regions

(Covered T04.)

## TTL

Auto-delete:
```
Set ttl = future_epoch_seconds
```

DynamoDB deletes within 48 hr. Free.

For: sessions, caches, ephemeral data.

## Transactions

Up to 100 items / 4 MB across tables:
```python
client.transact_write_items(
    TransactItems=[
        {"Put": {...}},
        {"Update": {...}}
    ]
)
```

Cost: 2× standard.

## Encryption

KMS-encrypted at rest. Default AWS-managed; custom KMS for sensitive.

In transit: HTTPS only.

## VPC Endpoint

Gateway endpoint for DynamoDB. Free. Avoid NAT for DB traffic.

## DAX

DynamoDB Accelerator: in-memory cache. Microsecond reads. Optional.

For ultra-hot reads. $$$ extra.

Cache-aside vs DAX: DAX is transparent; app code unchanged.

## Global Tables

Multi-region, multi-master:
- Replicate writes across regions
- Last-writer-wins conflict
- Eventually consistent
- RPO: seconds

For: global apps.

## Auto Scaling (Provisioned Mode)

Target tracking:
- "Keep WCU 70% utilized"
- Auto-scales up/down

CloudWatch + Application Auto Scaling.

## Limits

- Table: unlimited size
- Item: 400 KB
- Partition key value: 2048 bytes
- Sort key: 1024 bytes
- Attribute name: 255 bytes
- 20 GSIs, 5 LSIs per table

## Patterns

### Time-Series
```
PK=device_id
SK=timestamp
```

Query device's data in time range.

### Multi-Tenant
```
PK=tenant_id#entity_type
SK=entity_id
```

Each tenant isolated; queries filtered.

### Counters
```python
table.update_item(
    Key={"id": "counter1"},
    UpdateExpression="ADD count :inc",
    ExpressionAttributeValues={":inc": 1}
)
```

Atomic increment.

## Schema Design Process

1. List access patterns (what queries)
2. Group entities
3. Design PK/SK to satisfy 80% via query
4. Use GSI for the rest
5. Validate cost

No data-model-first; access-pattern-first.

## Migration RDB → DynamoDB

Rethink. Joins gone. Pre-compute access patterns.

DMS can help; data model redesign manual.

## Local Dev

DynamoDB Local: embedded version:
```bash
docker run -p 8000:8000 amazon/dynamodb-local
```

## Common Mistakes

- Choosing NoSQL when SQL fits
- Hot partition (bad PK)
- Many small writes (batch)
- Scan in production
- GSI overuse (write amplification)
- Storing huge items (use S3, link)

## Best Practices

- Access-pattern-first design
- Batch writes
- Query > Scan
- Use TTL for ephemeral
- Monitor throttling
- Sparse GSI (efficient)
- Compress big attrs

## Cost Optimization

- Provisioned mode for steady
- On-demand for sporadic
- TTL for ephemeral
- Sparse GSI
- Right capacity (don't over-provision)

## Quick Refs

```bash
# Create
aws dynamodb create-table --table-name X --attribute-definitions ... --key-schema ... --billing-mode PAY_PER_REQUEST

# Put
aws dynamodb put-item --table-name X --item '{"id":{"S":"1"},"name":{"S":"alice"}}'

# Query
aws dynamodb query --table-name X --key-condition-expression "id = :v" --expression-attribute-values '{":v":{"S":"1"}}'
```

## Interview Prep

**Mid**: "DynamoDB vs RDS."

**Senior**: "Schema for X access patterns."

**Staff**: "Hot partition mitigation."

## Next Topic

→ [T04 — DynamoDB Streams & Single-Table Design](T04-DynamoDB-Streams.md)
