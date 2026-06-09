# L08/C06/T04 — DynamoDB Streams & Single-Table Design

## Learning Objectives

- Use Streams for CDC
- Apply single-table patterns

## DynamoDB Streams

Change Data Capture: 24-hour log of item modifications.

Each item change → stream record:
- Type (INSERT, MODIFY, REMOVE)
- Keys
- Old image / new image (configurable)

## Enable

```bash
aws dynamodb update-table --table-name X --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES
```

View types:
- KEYS_ONLY
- NEW_IMAGE
- OLD_IMAGE
- NEW_AND_OLD_IMAGES

## Consume

### Lambda Trigger
```bash
aws lambda create-event-source-mapping \
  --function-name MyFn \
  --event-source-arn arn:aws:dynamodb:...:stream/... \
  --starting-position LATEST
```

Lambda invoked with batched records.

### Kinesis Data Streams
For longer retention (24h → 365 days), use Kinesis Data Streams for DynamoDB.

## Use Cases

### Replicate
DynamoDB → Stream → Lambda → other DB.

### Audit
Every change → S3 / CloudTrail-style log.

### Aggregate
Item updated → recalculate sum / count → cache.

### Notify
New item → SNS → email / SMS / Slack.

### Search
Item changed → index in OpenSearch.

### Cross-Region
Manual via Stream + Lambda (or use Global Tables which uses this under hood).

## Lambda Pattern

```python
def lambda_handler(event, context):
    for record in event["Records"]:
        event_type = record["eventName"]    # INSERT/MODIFY/REMOVE
        keys = record["dynamodb"]["Keys"]
        if "NewImage" in record["dynamodb"]:
            new = record["dynamodb"]["NewImage"]
        if "OldImage" in record["dynamodb"]:
            old = record["dynamodb"]["OldImage"]
        process(...)
```

Idempotent: stream replay possible.

## Order Guarantees

Within a partition: ordered.
Across partitions: not guaranteed.

Per-PK ordering = guaranteed.

## Concurrency

Lambda concurrency per stream shard. More shards = more parallel.

## Failure Handling

Lambda fails → Stream retries.
- Max age (1 hr - 14 days)
- Max retries (2 default)
- After: DLQ (SQS / SNS)
- Or split: bisect batch on failure to find bad record

```yaml
DestinationConfig:
  OnFailure:
    Destination: arn:aws:sqs:...:dlq
MaximumRecordAgeInSeconds: 3600
BisectBatchOnFunctionError: true
```

## Cost

Streams: free.
Lambda: per-request + duration.

For 1M writes/day → Lambda invokes batched: typically <$10/mo.

## Global Tables

Multi-region active-active. Uses Streams internally.

Conflict: last-writer-wins (timestamp).

```bash
aws dynamodb update-table --table-name X --replica-updates 'Create={RegionName=us-west-2}'
```

## Single-Table Design

Storing many entity types in one DynamoDB table; PK/SK encodes.

Why:
- Get user + orders in ONE query (vs many tables)
- Lower cost (single table = less RCU/WCU baseline)
- Better perf (no JOIN)

Tradeoff: complex schema; harder to evolve.

## Single-Table Example

User and their orders, friends, etc.

```
Table: my-app

PK              SK              Type      Data
USER#alice      PROFILE         user      name:Alice, email:...
USER#alice      ORDER#1         order     amount:50, date:...
USER#alice      ORDER#2         order     amount:75, date:...
USER#alice      FRIEND#bob      friend    since:2024-01-01
USER#bob        PROFILE         user      name:Bob, ...
USER#bob        ORDER#1         order     ...
```

Query: `PK=USER#alice` returns ALL alice data.
Query: `PK=USER#alice, SK begins_with ORDER#` returns alice orders.

## Designing Single-Table

Steps:
1. List access patterns
2. Identify entities + relationships
3. Decide PK partition strategy
4. Decide SK structure
5. Map each pattern to (Get or Query)
6. Add GSIs for remaining patterns

## Common Patterns

### Adjacency List
Graph-like:
```
USER#alice    FRIEND#bob       (alice friends bob)
USER#bob      FRIEND#alice     (bob friends alice)
```

Reciprocal entries; query either direction.

### Inverted Index
Find all in some category:
```
GSI1: PK=CATEGORY#tech, SK=ARTICLE#123
GSI1: PK=CATEGORY#tech, SK=ARTICLE#456
```

Query GSI1 PK=CATEGORY#tech returns articles in tech.

### Hierarchical
```
PK=ORG#acme
SK=DEPT#engineering / TEAM#platform / USER#alice
SK=DEPT#engineering / TEAM#platform / USER#bob
SK=DEPT#marketing / ...
```

Query org's structure.

### Sparse GSI
GSI on attribute only some items have:
```
attribute "highValueOrder": true (on subset of orders)
GSI on highValueOrder=true
```

Query GSI for high-value orders only. Efficient.

## Schema Versioning

Add field; existing items lack it. App handles both old/new.

For breaking: backfill (migration job updates each item).

DynamoDB has no schema migration tool; you write it.

## Tools

- NoSQL Workbench (visualize schema)
- dynamoose (Node ORM)
- pynamodb (Python ORM)
- DynamoDB Local for dev

## Anti-Patterns

- "DynamoDB like RDBMS" (table per entity; many JOINs)
- Scan everything
- Hot partition (all writes one PK)
- Storing big blobs (use S3, link)
- Unbounded item growth (item >400 KB)

## Best Practices

- Access patterns FIRST
- Single-table when multiple-related-entities
- Provisioned for steady
- TTL for ephemeral
- Compress large
- Monitor throttling
- Backups (PITR)

## Migration

From RDBMS:
1. Map access patterns
2. Pick PK/SK
3. ETL to DynamoDB
4. Refactor app for new queries

Or two-phase:
1. Write to both (RDB + DynamoDB)
2. Validate
3. Cut reads to DynamoDB
4. Stop writes to RDB

## When NOT Single-Table

- Few entities; simple
- Access patterns evolve frequently
- Team unfamiliar
- High write to one entity

For: separate tables OK.

## DAX

In-memory cache for DynamoDB. Microsecond reads. Use when:
- Read-heavy
- Same items repeatedly read
- Latency-critical

Cost: ~$60+/mo per node.

## Common Mistakes

- Scan over Query
- Single-table without thinking through
- Hot partition
- No backup
- Item size limits hit
- Cross-table queries (Why DynamoDB then?)

## Quick Refs

```bash
# Stream
aws dynamodb update-table --table-name X --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES

# Global table
aws dynamodb update-table --table-name X --replica-updates 'Create={RegionName=eu-west-1}'

# Lambda trigger
aws lambda create-event-source-mapping --function-name MyFn --event-source-arn ... --starting-position LATEST
```

## Interview Prep

**Mid**: "DynamoDB Streams use case."

**Senior**: "Single-table schema for X."

**Staff**: "Migration from MySQL to DynamoDB."

## Next Topic

→ [T05 — ElastiCache (Redis & Memcached)](T05-ElastiCache.md)
