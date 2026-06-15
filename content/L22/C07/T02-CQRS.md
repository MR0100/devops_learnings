# L22/C07/T02 — CQRS

## Learning Objectives

- Apply CQRS
- When to use

## CQRS

Command Query Responsibility Segregation:
- Separate write model (commands)
- Separate read model (queries)
- Different schemas optimized

## Why

CRUD:
- Same model for read + write
- Reads often need denormalized
- Writes need normalized

Conflict.

CQRS:
- Write model: normalized, transactional
- Read model: denormalized, fast

## Diagram

```
Command → Command Handler → Write Model (Postgres)
   ↓ event
Read Model (cache, materialized view, ES)
   ↑
Query → Query Handler
```

## Example

### Write
```python
def handle_place_order(cmd):
    with transaction:
        order = Order(...)
        save(order)
        emit(OrderPlaced(order))
```

### Read
```python
def get_order_view(order_id):
    return cache.get(f"order:{order_id}")
```

Different stores; updated via event.

## Update Read Model

Via event:
```python
def on_order_placed(event):
    cache.set(f"order:{event.order_id}", denormalized_view(event))
```

Or:
- Subscribe to Kafka
- Update read DB
- Materialized view

## Read Models Per View

- Order detail (Postgres)
- Order search (Elasticsearch)
- Order analytics (BigQuery)

Each tailored.

## Pros

- Each side optimized
- Scale independently
- Different schemas
- Flexible reads

## Cons

- Eventual consistency
- More moving parts
- Complexity
- Debug harder

## Eventual Consistency

Read after write:
- Write to write model
- Event propagates
- Read model updated (eventually)
- Read returns updated

Gap: ms-seconds.

For: tolerate.

## When CQRS

- Reads >> writes (10000:1)
- Different read views
- Event sourcing
- Audit / search

## When Not

- Simple CRUD
- Single read view
- Strong consistency needed

## With Event Sourcing

ES + CQRS:
- Events drive both write + read
- Replay rebuilds read

For: many advantages.

## Without ES

CQRS doesn't require ES:
- Write to normal DB
- Emit event
- Update read model

For: simpler.

## Outbox Pattern

(See T04.)

Reliably emit event with DB write.

## Examples

### Order System
- Write: Postgres normalized
- Read: ES for search + Redis for cache

### Social Feed
- Write: timeline events
- Read: per-user feed (precomputed)

### Banking
- Write: Postgres
- Read: BigQuery (analytics)

## Best Practices

- Separate clearly
- Idempotent read updates
- Monitor lag (write → read)
- Don't overuse (simple = stay CRUD)

## Common Mistakes

- CQRS for simple (overkill)
- Sync read on every write (loses benefit)
- Inconsistent read models
- Forget eventual consistency

## Quick Refs

```
Write side: handle command, save, emit event
Read side: subscribe, project, query
```

## Interview Prep

**Mid**: "What's CQRS."

**Senior**: "When CQRS."

**Staff**: "Read model design."

## Next Topic

→ [T03 — Saga Pattern](T03-Saga.md)
