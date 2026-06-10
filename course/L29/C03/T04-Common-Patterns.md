# L29/C03/T04 — Common Patterns at Each Level

## Learning Objectives

- Match patterns to level
- Show appropriately

## Patterns

### LB (all levels)
- Round robin
- Health checks

### Cache (mid+)
- Read-through
- Cache-aside
- LRU

### Sharding (senior+)
- By key
- Consistent hash

### Replication (senior+)
- Sync / async
- Single / multi leader

### Queue (mid+)
- Decouple
- Async

### CDN (mid+)
- Edge cache

### Sync / Async (all)
- API
- Background jobs

## Per Level

### Mid (L4)
- LB + DB + cache
- Single region

### Senior (L5)
- Multi-AZ
- Sharding
- Read replicas
- Queues

### Staff (L6)
- Multi-region
- Consistency trade-offs
- Cell architecture
- Custom optimizations

### Sr Staff / Principal (L7+)
- Org-wide trade-offs
- Long-term evolution
- Strategic infrastructure

## Show

For your level:
- Cover expected
- Reach for next level

For: stretch.

## Trade-Offs

- Consistency vs availability
- Cost vs performance
- Complexity vs maintainability

For: senior+.

## Examples

### URL Shortener (Mid)
- LB + Web + KV + Cache

### URL Shortener (Senior)
- Above + sharding + multi-region read

### URL Shortener (Staff)
- Above + multi-region writes + global LB + cost optimization

## Best Practices

- Know patterns
- Match level
- Stretch slightly
- Don't over-engineer

## Common Mistakes

- Under-cover (junior signal)
- Over-engineer (paranoid signal)
- One pattern (limited)

## Quick Refs

```
Mid: LB / Cache / DB
Senior: Multi-AZ / Sharding / Replication / Queue
Staff: Multi-region / CAP trade-off / Cell
```

## Interview Prep

**Mid**: "Patterns."

**Senior**: "Show range."

**Staff**: "Trade-offs."

## Next Topic

→ Move to [L29/C04 — Behavioral / Leadership Interviews](../C04/README.md)
