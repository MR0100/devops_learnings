# L27/C02/T03 — Active/Active vs Active/Passive

## Learning Objectives

- Choose pattern
- Trade-offs

## Active-Active

Both regions:
- Serve traffic
- Replicate data
- Failover instant

## Pros

- Lowest RTO/RPO
- Capacity in both
- Tested continuously

## Cons

- Conflict resolution (writes both)
- Cost: 2x
- Complexity

## Active-Passive

One active; other ready:
- Standby on failure

## Pros

- No conflicts
- Cheaper (passive scaled down or off)
- Simpler

## Cons

- Failover takes time
- Standby may not work (untested)

## Active-Active Patterns

### Sticky
User → same region
- Avoids conflict
- Geographic affinity

### Read-Write Split
Writes to one; reads any.
- One write region
- Read everywhere

### Multi-Master
Writes any region.
- Conflicts possible
- Last-Writer-Wins (LWW) or merge

## Conflict Resolution

### LWW
Newest wins.
- Simple
- Lost updates

### Merge
App-level merge logic.
- Better
- Complex

### CRDT
Conflict-free data types.
- Automatic merge
- Limited types

For: difficult; design carefully.

## Examples

### DynamoDB Global Tables
LWW.

### Spanner
Strong consistency multi-region (slower writes).

### Cassandra
Tunable; LWW typical.

### Custom
Per-domain logic.

## Active-Passive Setup

```
Primary (us-east-1): serves
Secondary (us-west-2): replica; DB read-only

On failure:
- Promote secondary DB
- Update DNS
- Traffic shifts
```

## Failover

Manual or automated:
- Detect failure
- Decide failover (avoid flapping)
- Execute (promote DB, DNS)
- Verify

## Practice

Quarterly:
- Drill failover
- Measure RTO

## When Active-Active

- Tier 1 critical
- Real-time global
- Budget allows
- Conflict resolution feasible

## When Active-Passive

- Tier 2
- Cost-sensitive
- Limited conflict tolerance
- Acceptable RTO

## Hybrid

Different tiers:
- Critical: active-active
- Important: active-passive
- Standard: backup-restore

## Best Practices

- Justify choice
- Test failover
- Document RTO actual
- Per service tier

## Common Mistakes

- Active-active for everything (cost)
- Active-passive without testing
- Manual failover (slow)
- No conflict resolution plan

## Quick Refs

```
A/A: both serve; conflict resolution
A/P: one serves; failover

Choose by:
- Tier
- Cost
- RTO needs
```

## Interview Prep

**Senior**: "Active patterns."

**Staff**: "Choose pattern."

## Next Topic

→ [T04 — Cells & Bulkheads](T04-Cells-Bulkheads.md)
