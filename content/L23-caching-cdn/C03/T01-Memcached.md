# L23/C03/T01 — Memcached: Simplicity vs Redis

## Learning Objectives

- Use Memcached
- Compare to Redis

## Memcached

Simple distributed cache:
- KV strings only
- No persistence
- Multi-threaded
- LRU

## Install

```bash
apt install memcached
memcached -m 1024 -p 11211 -u memcache
```

## Use

```python
import pymemcache

client = pymemcache.Client(('memcached', 11211))
client.set('key', 'value', expire=300)
client.get('key')
```

## Features (minimal)

- get / set
- add / replace / delete
- incr / decr
- TTL
- LRU
- Sharded (client-side consistent hashing)

## Vs Redis

| | Memcached | Redis |
|---|---|---|
| Data types | string only | many |
| Persistence | no | yes |
| Replication | no | yes |
| Threading | multi | single (mostly) |
| Memory | efficient slab | per-key overhead |
| Features | minimal | rich |

## When Memcached

- Pure cache
- Multi-threaded gains
- Simple model
- Low memory overhead

## When Redis

- Need persistence
- Data structures
- Pub/sub
- Scripting

For: Redis more common today.

## Multi-Thread

Memcached truly multi-threaded.

For: high throughput single instance.

## Memory Efficient

Slab allocator:
- Predictable
- Less overhead per key

For: large numbers small keys.

## Sharding

Client-side:
- Consistent hashing
- No central coordination
- Add/remove servers: minor rehash

For: simple scale.

## ElastiCache Memcached

AWS managed:
- Auto-discovery
- Multi-node
- No persistence

For: AWS managed cache.

## Best Practices

- Pure cache use
- TTL set
- Multi-node for size
- Monitor evictions

## Common Mistakes

- Use for state (no persist)
- Single node (memory wall)
- No monitoring

## Decline

Memcached share declined; Redis dominant.

For new: usually Redis.

## Quick Refs

```bash
# Stats
memcached-tool host:port stats / display

# Commands (text protocol)
get key
set key 0 60 5
value
quit
```

```python
client.set / get / delete / incr / decr
```

## Interview Prep

**Mid**: "Memcached vs Redis."

**Senior**: "When Memcached."

## Next Topic

→ Move to [L23/C04 — Application-Level Caching](../C04/README.md)
