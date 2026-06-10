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

## Next Topic

→ Move to [L29/C03 — System Design for SRE/DevOps](../C03/README.md)
