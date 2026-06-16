# L22/C07/T01 — Event Sourcing

## Learning Objectives

- Apply event sourcing
- Trade-offs

## Event Sourcing

Store every change as event:
```
UserCreated(id=1, name="alice")
UserEmailChanged(id=1, email="a@b.com")
UserDeactivated(id=1)
```

State derived by replay.

## Vs CRUD

CRUD:
- Current state in DB
- Updates overwrite

Event Sourcing:
- Append-only log of events
- Current state = fold(events)

## Why

- Audit trail (free)
- Time travel
- Replay for new projections
- Event-driven natural

## Storage

- Kafka (compacted topic per aggregate)
- EventStoreDB
- Postgres (event table)

## Projections

Read models built from events:
```python
def apply(state, event):
    if isinstance(event, UserCreated):
        return {**state, 'name': event.name}
    if isinstance(event, UserEmailChanged):
        return {**state, 'email': event.email}
```

Replay events → current state.

## Snapshots

For performance:
- Periodic snapshot
- Replay only since

For: avoid replay millions.

## Aggregate

Domain entity:
- ID
- Events emitted
- State

## Commands → Events

```python
def handle_change_email(aggregate, command):
    aggregate.validate(command)
    event = UserEmailChanged(id=aggregate.id, email=command.new_email)
    aggregate.apply(event)
    return event
```

Event saved + emitted.

## Schema Evolution

Old events stay forever.

New events: new schema.

Code must handle:
- Old version (compatibility)
- New version

For: tricky.

## Pros

- Audit
- Replay
- Multiple read models (CQRS)
- Temporal queries

## Cons

- Complexity
- Schema evolution
- Storage cost
- Learning curve

## When

- Audit-required (finance, healthcare)
- Domain events natural
- Multiple read views

## When Not

- Simple CRUD
- Team unfamiliar
- No business need

## Combined with CQRS

(See T02.)

Event sourcing + CQRS often paired.

## Tools

- EventStoreDB
- Axon (Java)
- NEventStore (.NET)
- Postgres + own
- Kafka + projection apps

## Example: Bank

```
Account created
Deposit $100
Deposit $50
Withdraw $30
```

Balance: $120.

Audit: who, when. Easy.

## Best Practices

- Per aggregate stream
- Snapshots for long
- Version events
- Idempotent projections
- Document carefully

## Common Mistakes

- Skip snapshots (replay forever)
- No event versioning
- CRUD thinking with ES
- Overkill for simple domain

## Quick Refs

```
Event → Stream
Apply events → State
Snapshot periodically
Projection = read model
```

## Interview Prep

**Mid**: "What's event sourcing."

**Senior**: "Pros / cons."

**Staff**: "When ES."

## Next Topic

→ [T02 — CQRS](T02-CQRS.md)
