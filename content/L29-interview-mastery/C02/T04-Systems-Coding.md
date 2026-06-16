# L29/C02/T04 — Systems Coding

## Learning Objectives

- Solve systems problems
- Practical DevOps coding

## Systems Coding

Build a small system:
- Rate limiter
- LRU cache
- Log parser
- URL shortener (small)
- Job scheduler

For: real-world DevOps.

## Why

- More relevant than LeetCode
- Some companies prefer
- Shows engineering judgment

## Example: LRU Cache

```python
from collections import OrderedDict

class LRU:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```

For: cache eviction.

## Example: Rate Limiter

(See T03.)

Token bucket / sliding window.

## Example: Log Parser

Parse nginx logs:
```python
import re

pattern = r'(\S+) - - \[([^\]]+)\] "(\S+) (\S+) HTTP/[\d.]+" (\d+) (\d+)'

def parse(line):
    m = re.match(pattern, line)
    if m:
        return {
            'ip': m.group(1),
            'time': m.group(2),
            'method': m.group(3),
            'path': m.group(4),
            'status': int(m.group(5)),
            'size': int(m.group(6)),
        }
```

For: real DevOps.

## Example: Top K Logs

```python
from collections import Counter

def top_k_paths(log_lines, k):
    paths = [parse(line)['path'] for line in log_lines]
    return Counter(paths).most_common(k)
```

## Example: Distributed ID

Snowflake-like:
```python
import time

class Snowflake:
    def __init__(self, worker_id):
        self.worker_id = worker_id
        self.sequence = 0
        self.last_ts = 0
    
    def next_id(self):
        ts = int(time.time() * 1000)
        if ts == self.last_ts:
            self.sequence += 1
        else:
            self.sequence = 0
        self.last_ts = ts
        return (ts << 22) | (self.worker_id << 12) | self.sequence
```

The signal in a Snowflake question is whether you surface the **edge cases** the skeleton above ignores: (1) **sequence overflow** — only 12 bits, so >4096 IDs in one millisecond must *block until the next millisecond* rather than collide; (2) **clock running backward** (NTP correction) — you must detect `ts < last_ts` and either wait or refuse, or you'll emit duplicate IDs; and (3) thread safety — concurrent `next_id()` calls need a lock around the sequence increment. Naming these unprompted turns a 20-line snippet into a strong-hire answer.

## Format

```
Time: 45-60 min
Interview: walk through approach
Code: clean, modular
Test: walk through example
```

## Best Practices

- Clean code
- Modular
- Edge cases
- Test
- Trade-offs

## Common Mistakes

- Big functions (monolithic)
- No tests
- Premature optimization
- No comments

## Quick Refs

```
Problems:
- LRU cache
- Rate limiter
- Log parser
- URL shortener
- Top K
- Snowflake ID
```

## Interview Prep

**Junior**: "Implement an LRU cache." — An `OrderedDict`: `get` moves the key to the end and returns it; `put` inserts/updates, moves to end, and evicts the oldest (`popitem(last=False)`) when over capacity. I'd mention that in a 'real' interview without `OrderedDict` you'd build it from a hash map plus a doubly-linked list for O(1) move-and-evict, and offer that version if they want the underlying mechanics.

**Mid**: "Why is systems coding different from LeetCode?" — It rewards engineering judgment over algorithmic tricks. The grader is watching for clean decomposition, named edge cases, sane data-structure choices, and a worked test — not the cleverest one-liner. I keep functions small, name a TTL/eviction policy explicitly, and trade off simplicity against the requirements rather than over-engineering.

**Senior**: "Find the top-K endpoints in a multi-gigabyte log." — Stream it: a `Counter` (hash map) over a single pass, then a heap of size K to extract the top-K — O(n log K) time, O(unique-keys) memory. If the key space doesn't fit in memory I shard by hashing the key, aggregate per shard, then merge — the classic map-reduce shape. I'd state the memory bound out loud because that's the real constraint at log scale.

**Staff**: "Design a distributed ID generator." — Snowflake: time-ordered 64-bit IDs as `timestamp | worker_id | sequence`. The depth is in the failure modes: block on sequence overflow within a millisecond, refuse or wait when the clock moves backward (NTP), and assign worker IDs without collision (ZooKeeper/etcd lease or static config). I'd compare against UUIDv4 (no coordination, but random and index-unfriendly) and ULID, and justify the choice by the index-locality and roughly-sortable requirements.

## Next Topic

→ [T05 — Worked Example: Top-K from Logs](T05-Top-K-Logs.md)
