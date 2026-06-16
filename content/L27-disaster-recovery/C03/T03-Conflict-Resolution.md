# L27/C03/T03 — Conflict Resolution

## Learning Objectives

- Resolve concurrent writes
- Pick strategy

## Conflicts

Multiple regions write same key:
- Race
- Diverge
- Need merge

## Strategies

### Last-Writer-Wins (LWW)
Newest wins (by timestamp).
- Simple
- Lost updates

### CRDT
Conflict-free Replicated Data Types:
- Auto-merge
- Math guarantees
- Limited types

### Versioning
Each write: version vector.
- Detect concurrent
- App resolves

### Application Logic
Custom merge:
- "If conflict on cart: merge items"
- Complex

## LWW

```python
record = max(replicas, key=lambda r: r.timestamp)
```

Simple. But: lost updates.

For: most use cases acceptable.

## DynamoDB Global Tables

LWW.

## Cassandra

LWW (default).

## CRDTs

Types:
- G-Counter (grow-only counter)
- PN-Counter (positive-negative)
- G-Set (grow-only set)
- OR-Set (observe-remove)
- LWW-Element-Set

Used in:
- Redis (some CRDTs)
- Riak
- AntidoteDB

For: counters, sets.

## Operational Transformation

For collaborative editing (Google Docs):
- Transform ops to merge

For: rich docs.

## Version Vectors

```
[us-east: 5, eu-west: 3]
```

Compare:
- A < B: A's events before B's
- A > B: opposite
- Concurrent: conflict

## Resolution Workflow

```
1. Detect conflict (version vector)
2. Decide: LWW / app logic / show to user
3. Resolve
4. Replicate resolution
```

## Examples

### Shopping Cart
Items added in different regions:
- Merge (union)
- Don't LWW (lose items)

### Counter
Increments in different regions:
- CRDT (PN-Counter)
- Add all increments

### Profile
Last update wins (usually OK).

## Mongo

Causal consistency:
- Read after own writes
- Consistent ordering per session

## Spanner

Sync; no conflicts (paxos).

For: strong consistency.

## Trade-Off

| | LWW | CRDT | App Logic |
|---|---|---|---|
| Complexity | low | medium | high |
| Data loss | possible | none | none |
| Use case | most | specific | specific |

## Hot Keys

Concurrent writes to same key:
- Worse for LWW
- CRDTs handle better
- Or shard

## Best Practices

- LWW default if acceptable
- CRDTs for counters/sets
- App logic for important state
- Document strategy

## Common Mistakes

- LWW for cart (lost items)
- Custom logic for trivial (overkill)
- No detection of conflicts

## Quick Refs

```
LWW: max(timestamp)
CRDT: type-specific merge
App: custom code
```

## Interview Prep

**Senior**: "Conflict resolution."

**Staff**: "Multi-region writes."

**Principal**: "Consistency tradeoffs."

## Next Topic

→ Move to [L27/C04 — Failover Mechanics](../C04/README.md)
