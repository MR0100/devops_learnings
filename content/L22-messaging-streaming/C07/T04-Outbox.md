# L22/C07/T04 — Outbox Pattern

## Learning Objectives

- Reliably emit events
- Handle dual writes

## Problem

```
Save to DB
Emit to Kafka
```

Two operations:
- DB success + Kafka fail: event lost
- DB fail + Kafka success: bogus event

Not atomic.

## Solution: Outbox

```
BEGIN TX
  Save record to DB
  Save event to outbox table
COMMIT TX

(Separate process)
Read outbox → emit to Kafka → mark sent
```

DB transaction = atomic.
Outbox guarantee: event will eventually emit.

## Schema

```sql
CREATE TABLE outbox (
  id UUID PRIMARY KEY,
  topic TEXT,
  payload JSONB,
  created_at TIMESTAMPTZ,
  sent_at TIMESTAMPTZ
);
```

## Producer

```python
with transaction:
    db.insert('orders', order_data)
    db.insert('outbox', {
        'topic': 'orders',
        'payload': order_data,
    })
# Transaction commits both
```

## Worker

Polls or CDC:
```python
while True:
    rows = db.fetch("SELECT * FROM outbox WHERE sent_at IS NULL LIMIT 100")
    for row in rows:
        kafka.send(row.topic, row.payload)
        db.update("UPDATE outbox SET sent_at = NOW() WHERE id = ?", row.id)
    sleep(1)
```

## Debezium for Outbox

CDC reads outbox automatically:
- Outbox row inserted
- Debezium captures
- Pushes to Kafka topic

```yaml
"outbox.table.event.id.column": "id",
"outbox.table.event.key.column": "aggregate_id",
"outbox.table.event.payload.column": "payload",
"outbox.routes.expression": "${routedByValue}"
```

For: no custom worker.

## At-Least-Once

Event may be emitted multiple times:
- Worker crashed before mark sent
- Restart, re-emit

Consumer: idempotent.

## Cleanup

Old outbox rows:
- After sent
- After N days

```sql
DELETE FROM outbox WHERE sent_at < NOW() - INTERVAL '7 days';
```

## Order

For ordering per aggregate:
- Sort by created_at
- Per-key partition in Kafka

## Performance

Outbox writes:
- Inline with business tx
- Small overhead

Worker:
- Async; doesn't block

## Compared to Two-Phase Commit

| | Outbox | 2PC |
|---|---|---|
| Atomicity | local DB | distributed |
| Complexity | low | high |
| Performance | good | bad |
| Failure modes | tolerable | catastrophic |

For: outbox better in practice.

## Alternatives

### Polling Publisher
Worker polls; similar to outbox.

### Listen/Notify (PG)
Postgres notifies; worker reads.

### Transactional Outbox + Inbox
On consumer side: inbox table for dedupe.

## Inbox Pattern

```sql
CREATE TABLE inbox (
  event_id UUID PRIMARY KEY,
  received_at TIMESTAMPTZ
);
```

Consumer:
```python
with transaction:
    if seen(event_id):
        return  # already processed
    process(event)
    record_seen(event_id)
```

For: exactly-once semantic.

## When Outbox

- Microservices DB + event
- Reliability matters
- Can't use 2PC

## Best Practices

- Outbox + Debezium
- Idempotent consumers
- Periodic cleanup
- Monitor lag (outbox → emit)

## Common Mistakes

- Dual writes without outbox
- No cleanup (table grows)
- No consumer dedupe
- Sync emit in business path (latency)

## Quick Refs

```sql
INSERT INTO outbox (...) IN BUSINESS TX

-- Worker
SELECT * FROM outbox WHERE sent_at IS NULL;
EMIT
UPDATE outbox SET sent_at = NOW();
```

## Interview Prep

**Mid**: "What's outbox."

**Senior**: "Dual-write problem."

**Staff**: "Reliable event publishing."

## Next Topic

→ Move to [L23 — Caching & CDN](../../L23-caching-cdn/README.md)
