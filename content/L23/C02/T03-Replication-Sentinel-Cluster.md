# L23/C02/T03 — Redis Replication, Sentinel, Cluster

## Learning Objectives

- Set up HA Redis
- Cluster vs Sentinel

## Replication

Master → replicas:
- Async stream
- Read-only replicas

```
replicaof master-host 6379
```

For: read scaling, HA basis.

## Lag

Replicas eventually catch up.

For: not strong consistency.

## Sentinel

Auto-failover:
- 3+ Sentinels monitor master
- If down: elect new master
- Notify clients

```
sentinel monitor mymaster 192.168.1.1 6379 2
sentinel down-after-milliseconds mymaster 5000
```

Quorum: 2 (of 3+ Sentinels) needed.

For: single shard HA.

## Cluster

Sharded:
- 16384 hash slots
- 3+ masters + replicas
- Auto-shard

```bash
redis-cli --cluster create m1:6379 m2:6379 m3:6379 \
  s1:6379 s2:6379 s3:6379 \
  --cluster-replicas 1
```

For: scale beyond one node.

## Hash Slot

```
slot = CRC16(key) % 16384
```

Slot → master.

## Hash Tags

```
{user:1}:profile
{user:1}:settings
```

Both same slot. For: MULTI / transactions across keys.

## Client

Cluster-aware client:
- Knows shard map
- Routes to master
- Updates on MOVED redirect

For: most language clients support.

## Failover

Master down:
- Replica promotes
- Slots re-mapped
- Client retries

For: auto.

## Resharding

```bash
redis-cli --cluster reshard host:port
```

Move slots between masters.

For: rebalance.

## Sentinel vs Cluster

| | Sentinel | Cluster |
|---|---|---|
| Scale | 1 master | N masters |
| Data | < 100 GB | huge |
| Setup | simpler | complex |
| Multi-key | yes | hash tags only |

For: cluster if > 100 GB or > 100k ops/sec.

## Operational

### Sentinel
- 3 Sentinel + 1 master + N replicas
- 4+ nodes total

### Cluster
- 6+ nodes (3 masters + 3 replicas min)
- More complex

## Read Scaling

Both:
- Read from replicas
- READONLY command

For: offload reads.

## Cloud Native

- ElastiCache (cluster mode or not)
- MemoryDB (cluster, durable)
- Cosmos for Redis
- Memorystore

For: managed.

## Cluster Mode in Cloud

ElastiCache cluster mode:
- Sharded
- Auto-failover
- Less ops

## Best Practices

- Sentinel for < 100 GB
- Cluster for huge
- 3+ Sentinels / 3+ masters
- Read from replicas
- Test failover

## Common Mistakes

- 1 master no replica (SPOF)
- 2 Sentinels (split brain)
- Cluster for small data (overkill)
- Cross-slot ops without hash tag

## Quick Refs

```bash
# Sentinel
sentinel monitor / failover / ckquorum

# Cluster
redis-cli --cluster create
redis-cli --cluster reshard
redis-cli --cluster check
CLUSTER INFO / NODES / SLOTS
```

## Interview Prep

**Mid**: "HA Redis."

**Senior**: "Sentinel vs cluster."

**Staff**: "Redis platform."

## Next Topic

→ [T04 — Lua Scripting](T04-Lua-Scripting.md)
