# L23/C01/T03 — LRU, LFU, ARC

## Learning Objectives

- Understand eviction algorithms
- Pick for use case

## Why Eviction

Cache size limited.
Memory full → evict something.

Algorithm decides what.

## LRU

Least Recently Used:
- Track recency
- Evict oldest accessed

```
Cache: A(t=10), B(t=20), C(t=30)
Access B → B(t=40)
Insert D → evict A (oldest)
Cache: B(t=40), C(t=30), D(t=50)
```

## LFU

Least Frequently Used:
- Track access count
- Evict least accessed

```
Cache: A(count=10), B(count=20), C(count=5)
Insert D → evict C
```

Risk: old popular items dominate.

## LFU with Aging

Decay count over time:
- Recently popular > long-ago popular

For: balance.

## ARC

Adaptive Replacement Cache:
- Combines LRU + LFU
- Two lists: recency + frequency
- Dynamic balance

For: adaptive workload.

## TinyLFU

Probabilistic LFU:
- Bloom-filter-like counters
- Used in Caffeine

For: efficient LFU.

## Random

Evict random.
- Cheap
- Sometimes competitive

## FIFO

First In First Out:
- No access tracking
- Simple
- Worse than LRU usually

## CLOCK

Approximation of LRU:
- Cheaper to implement
- Pointer cycles through

For: kernel page caches.

## Comparing

| | Hit rate | Cost |
|---|---|---|
| LRU | good | medium |
| LFU | depends | medium |
| LFU-aged | better | medium |
| ARC | best (adaptive) | high |
| TinyLFU | great | medium |
| Random | OK | very low |
| FIFO | poor | very low |

## When LRU

- Default
- Recency-correlated access

## When LFU

- Popularity-correlated

## When ARC

- Mixed workload
- Don't know

## Use Cases

### Page Cache (OS)
LRU / CLOCK.

### Web Cache
LRU / LFU.

### DB Buffer Pool
LRU.

### CDN
Various; often LFU or LFU-aged.

## Redis Eviction

```ini
maxmemory-policy allkeys-lru     # LRU all keys
maxmemory-policy allkeys-lfu     # LFU
maxmemory-policy volatile-lru    # LRU only TTL'd keys
maxmemory-policy allkeys-random
maxmemory-policy noeviction      # error on full
```

For Redis cache: allkeys-lru usually.
For Redis with state: noeviction.

## Memcached

LRU by default.

## Caffeine (Java)

Window TinyLFU:
- Window: LRU
- Main: TinyLFU

For: state of art.

## Implementation Cost

LRU:
- Need linked list + hashmap
- O(1) ops

LFU:
- Need counter + sorted
- O(log N) often

For: LRU simpler.

## Workload Sensitivity

- LRU: good with locality
- LFU: good with stable popularity
- ARC: adapts

For: test with real workload.

## Real Examples

- Linux: CLOCK-like
- Memcached: LRU
- Redis: LRU or LFU choice
- Caffeine: TinyLFU
- PostgreSQL: clock-sweep (LRU-ish)

## Best Practices

- Default LRU
- Try LFU for popularity-stable
- Caffeine TinyLFU if Java
- Measure hit rate; tune

## Common Mistakes

- Wrong algorithm for workload
- No measurement
- Skipping tuning

## Quick Refs

```
LRU:  recent
LFU:  frequent
ARC:  adaptive
TinyLFU: efficient LFU
Random: cheap baseline

Redis: maxmemory-policy
Memcached: LRU default
Caffeine: TinyLFU
```

## Interview Prep

**Mid**: "LRU."

**Senior**: "LFU + variants."

**Staff**: "Cache algorithm choice."

## Next Topic

→ [T04 — Read-Through, Write-Through, Write-Back](T04-Read-Write-Patterns.md)
