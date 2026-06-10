# L28/C02/T02 — Sharding & Partitioning

## Learning Objectives

- Shard data
- Pick shard key

## Sharding

Split DB across multiple instances:
- Per shard: subset of data
- Routing: which shard?

For: horizontal scale.

## Why

- Beyond single instance
- Distribute load
- Independent scaling

## Strategies

### Range
By key range:
```
Shard 1: A-M
Shard 2: N-Z
```

Pros: simple range queries.
Cons: hot shards.

### Hash
Hash(key) % N → shard.

Pros: even distribution.
Cons: range queries hit all.

### Consistent Hash
Ring; minor rehash on add/remove.

For: scale-friendly.

### Directory
Lookup table key → shard.

Pros: flexible.
Cons: extra hop, hotspot.

## Shard Key Choice

Critical:
- High cardinality
- Even distribution
- Aligns with queries

## Hot Shards

If shard key uneven:
- One shard overloaded
- Bottleneck

For: avoid (random keys, salt).

## Cross-Shard Queries

Hit all shards:
- Slow
- Scatter-gather

For: design to avoid.

## Joins

Across shards: hard.

Mitigations:
- Denormalize
- Shard by foreign key
- Application-level

## Resharding

Add shard:
- Move data
- Slow
- Avoid often

For: plan growth.

## Tools

- Vitess (MySQL sharding; YouTube)
- Citus (Postgres sharding)
- MongoDB built-in sharding
- DynamoDB / Bigtable (auto-shard)

## Examples

### User-Based
shard_key = user_id
- All user's data on one shard
- Good for user queries
- Bad for cross-user

### Time-Based
shard_key = timestamp
- Recent data hot
- Old data cold
- Drop old by dropping shard

### Tenant
shard_key = tenant_id (SaaS)
- Tenant isolation
- Even if tenants vary in size

## Application Logic

Sharded DB → app aware:
```python
shard = hash(user_id) % num_shards
db = connect(shard)
db.query(...)
```

Or middleware (Vitess, ProxySQL):
- App connects to proxy
- Proxy routes

## Best Practices

- Choose shard key carefully
- High cardinality
- Hash for even distribution
- Plan resharding

## Common Mistakes

- Low cardinality shard key (hot shards)
- Cross-shard queries (slow)
- Hard to reshard

## Quick Refs

```
Strategies: range / hash / consistent hash / directory
Shard key: high cardinality, even
Hot shard: avoid
Cross-shard: design out
```

## Interview Prep

**Mid**: "What's sharding."

**Senior**: "Pick shard key."

**Staff**: "Sharded architecture."

## Next Topic

→ [T03 — Replication Patterns](T03-Replication-Patterns.md)
