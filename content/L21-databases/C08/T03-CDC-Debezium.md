# L21/C08/T03 — CDC (Debezium)

## Learning Objectives

- Stream DB changes
- Use Debezium

## CDC

Change Data Capture:
- Stream every DB change
- To Kafka / others
- Real-time

For: replication, analytics, search index.

## Why

- Sync DB → search (Elasticsearch)
- Sync DB → cache invalidation
- Sync DB → warehouse (analytics)
- Sync DB → other DB

## Methods

### Polling
SELECT * WHERE updated_at > last:
- Simple
- Misses deletes
- Lag

### Triggers
DB trigger writes to log table:
- Reliable
- Overhead

### Log-Based (Best)
Read DB's transaction log:
- Postgres: WAL
- MySQL: binlog
- Mongo: oplog

For: Debezium.

## Debezium

Open source CDC:
- Reads logs
- Emits to Kafka
- JSON / Avro messages

```yaml
# Connect config
{
  "name": "postgres-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "primary",
    "database.user": "debezium",
    "database.dbname": "mydb",
    "plugin.name": "pgoutput",
    "topic.prefix": "mydb"
  }
}
```

## Output

Per table:
- Topic: mydb.public.users
- Each change: INSERT, UPDATE, DELETE event

```json
{
  "op": "u",  // operation
  "before": {...},
  "after": {...},
  "ts_ms": ...
}
```

## Setup

```bash
# Kafka Connect
kafka-connect -d /etc/kafka-connect/
```

Install Debezium connector.

## Postgres Setup

```ini
wal_level = logical
max_replication_slots = 5
max_wal_senders = 10
```

Create user + publication:
```sql
CREATE USER debezium WITH REPLICATION PASSWORD '...';
CREATE PUBLICATION dbz_publication FOR ALL TABLES;
```

## Use Cases

### Search Index
Postgres → Debezium → Kafka → Elasticsearch updater.

Search always fresh.

### Cache Invalidation
Postgres update → Debezium → Redis cache delete.

### Data Warehouse
Postgres → Debezium → BigQuery (via Kafka).

Real-time analytics.

### Multi-DB Sync
Postgres → MySQL (different teams).

## Topics

One per table:
```
mydb.public.users
mydb.public.orders
mydb.public.payments
```

Consumers subscribe.

## Schema Evolution

Debezium handles:
- ADD COLUMN
- DROP COLUMN (with care)
- Schema registry (Avro)

## Performance

For 1k writes/sec:
- Modest
- One Connect worker

For 10k+: scale connector.

## Resource Use

- Per table: minimal
- Per connector: 1-2 GB RAM
- Kafka Connect: scalable

## Tools

- Debezium (open source)
- Striim (commercial)
- Fivetran (managed CDC)
- AWS DMS

## When CDC

- Need real-time
- Multiple consumers
- Existing event-driven

## When Not

- Batch OK
- Few consumers
- Complexity overhead

## Best Practices

- Per-table topic
- Schema registry
- Replication slot monitoring
- Compaction for snapshot-like consumers
- Handle deletes (tombstones)

## Common Mistakes

- Stale replication slot (WAL fills)
- No schema registry
- No retention tuning
- Drop column without consumer prep

## Quick Refs

```bash
# Debezium connector
POST /connectors  # create
GET /connectors/X/status
DELETE /connectors/X

# Postgres
SELECT * FROM pg_replication_slots;
SELECT pg_drop_replication_slot('debezium');
```

## Interview Prep

**Mid**: "What's CDC."

**Senior**: "Debezium."

**Staff**: "Event-driven architecture."

## Next Topic

→ Move to [L22 — Message Queues & Event Streaming](../../L22-messaging-streaming/README.md)
