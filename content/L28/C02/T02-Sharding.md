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

**Junior**: "What is sharding?" — Splitting one logical dataset across multiple database instances, each holding a subset, so you can scale write throughput and storage beyond a single machine. A routing rule (hash, range, or lookup) decides which shard owns a given key.

**Mid**: "How do you choose a shard key?" — Three properties: high cardinality (so data spreads), even access distribution (so no shard gets hot), and alignment with your common queries (so most queries hit one shard, not all). For a SaaS app, tenant_id or user_id usually wins; a low-cardinality key like country or status creates hot shards.

**Senior**: "What goes wrong with a bad shard key, and how do you fix it?" — A low-cardinality or skewed key creates a hot shard that bottlenecks the whole system while others sit idle — and cross-shard queries (scatter-gather) become slow because they fan out to every shard. Fixes: pick a higher-cardinality key, salt or hash the key to spread, denormalize to keep related data co-located, and design queries to hit a single shard. Resharding to fix it later is painful, which is why the key choice is up-front and hard to change.

**Staff**: "Design a sharded data layer and handle the operational realities." — Hash-based sharding on a high-cardinality key (consistent hashing so adding a shard remaps ~1/N, not everything), a routing layer (Vitess/Citus/ProxySQL or app-level) so the app doesn't hardcode shard math, and co-location of joinable data on the same shard to avoid cross-shard joins. The realities I'd call out: resharding needs an online migration with dual-writes, cross-shard transactions are expensive (avoid or use sagas), and I'd monitor per-shard load to catch an emerging hot shard before it tips over.

## Next Topic

→ [T03 — Replication Patterns](T03-Replication-Patterns.md)
