# L22/C07 — Event-Driven Architecture

## Topics

- **T01 Event Sourcing** — Store events as truth
- **T02 CQRS** — Separate read and write models
- **T03 Saga Pattern** — Distributed transactions
- **T04 Outbox Pattern** — Reliable event publishing

## Event-Driven Architecture (EDA)

> Services communicate by emitting events; consumers react.

### Why
- Decoupling (producer doesn't know consumers)
- Scalability (consumers scale independently)
- Replay (rebuild state from events)
- Audit (events are immutable)

### Vs Request-Response
- RR: synchronous, point-to-point, coupled
- EDA: asynchronous, broadcast, decoupled

## Event Sourcing

Store events as the source of truth. Derive current state by replaying events.

```
Events:
- OrderCreated  (id=1, items=[A,B])
- ItemAdded     (id=1, item=C)
- OrderPaid     (id=1, amount=99)

Current state = derived by replaying ↑
```

### Pros
- Audit log built-in
- Time-travel (state as of any point)
- Easy to add new derived views

### Cons
- Complex to operate
- Storage grows (events accumulate)
- Snapshotting needed for performance
- Schema evolution is hard

### Tools
- **EventStoreDB** — purpose-built
- **Kafka** as event store
- **Marten / Axon** — frameworks

## CQRS (Command Query Responsibility Segregation)

Separate read and write models.

```
Commands → Write model (event source, OLTP DB)
                ↓ events
Read model 1 (denormalized for screen A)
Read model 2 (search index)
Read model 3 (analytics warehouse)
```

### Pros
- Read model optimized per query
- Independent scaling
- Loose coupling

### Cons
- Eventual consistency between read and write
- More moving parts

### Often Pairs with Event Sourcing
- Write: append event
- Read: project events into materialized views

## Saga Pattern

Distributed transaction without 2PC.

A saga is a sequence of local transactions; each emits an event; if any fails, compensating transactions undo previous steps.

```
Step 1: ReserveInventory   → ok or fail
Step 2: ChargePayment      → ok or fail
Step 3: ShipOrder          → ok or fail

If Step 2 fails:
  Compensate Step 1: ReleaseInventory

If Step 3 fails:
  Compensate Step 2: RefundPayment
  Compensate Step 1: ReleaseInventory
```

### Choreography
Each service listens to events from others; decides what to do.
- Distributed; no central coordinator
- Can be hard to trace logic

### Orchestration
A coordinator (Step Functions, Temporal) drives the saga.
- Centralized; easier to reason about
- Coordinator is a SPOF (must be reliable)

## Outbox Pattern

Reliable event publishing from DB.

### Problem
- App does DB write + Kafka publish
- DB succeeds, Kafka fails → inconsistency
- Or vice versa

### Solution
1. In SAME DB transaction: write business data + insert event into outbox table
2. Async: outbox poller reads outbox → publishes to Kafka → marks published

```sql
BEGIN;
INSERT INTO orders (id, ...) VALUES (1, ...);
INSERT INTO outbox (event_type, payload) VALUES ('OrderCreated', '...');
COMMIT;
```

Outbox poller (separate process) takes from outbox → Kafka → deletes from outbox.

### Why It Works
- DB transaction atomic
- Even if app crashes after commit, event is in outbox
- Async poller eventually publishes (at-least-once)

### Implementations
- Custom poller
- Debezium watching outbox table (CDC)

## Inbox Pattern

Mirror of outbox for consumers:
- On receive, write to inbox table in same DB transaction as processing
- Idempotency: check inbox before processing

## Event Versioning

Schemas evolve.
- Use Schema Registry (Avro, Protobuf)
- Backward compatible by default
- Major version changes for breaking

## Common Mistakes

- **Events as RPC** (caller waits for reply) — not EDA
- **Tight coupling via event schemas** — every change breaks consumers
- **No idempotency in consumers** — at-least-once causes duplicates
- **Forgetting outbox** — direct publish from app code → inconsistency
- **No replay strategy** — events lost on bug; can't recover

## When EDA

| Yes | No |
|---|---|
| Many consumers of same event | Few simple services |
| Need replay / audit | Stateless RPC suffices |
| Decoupling critical | Tight integration acceptable |
| Different read/write scaling needs | Read = write at small scale |

EDA adds complexity. Use when benefits justify.

## Interview Themes

- "Event sourcing — pros + cons"
- "CQRS — explain"
- "Saga pattern — choreography vs orchestration"
- "Outbox pattern — what does it solve?"
- "EDA when?"
