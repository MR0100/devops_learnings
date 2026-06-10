# L29/C02/T03 — Concurrency Problems

## Learning Objectives

- Solve concurrency
- Threads, locks

## Why

For DevOps / SRE:
- Often asked
- Practical
- System understanding

## Topics

- Producer-consumer
- Reader-writer
- Bounded queue
- Rate limiter
- Thread pool
- Async / Futures

## Producer-Consumer

```python
import threading
import queue

q = queue.Queue(maxsize=10)

def producer():
    while True:
        item = produce()
        q.put(item)

def consumer():
    while True:
        item = q.get()
        process(item)
        q.task_done()

threading.Thread(target=producer).start()
threading.Thread(target=consumer).start()
```

For: classic.

## Rate Limiter

Token bucket:
```python
import time
import threading

class RateLimiter:
    def __init__(self, rate):
        self.rate = rate
        self.tokens = 0
        self.last = time.time()
        self.lock = threading.Lock()
    
    def acquire(self):
        with self.lock:
            now = time.time()
            self.tokens = min(self.rate, self.tokens + (now - self.last) * self.rate)
            self.last = now
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False
```

For: API limits.

## Reader-Writer

Multiple readers + exclusive writer:
```python
class RWLock:
    def __init__(self):
        self.readers = 0
        self.lock = threading.Lock()
        self.write = threading.Lock()
    
    def acquire_read(self):
        with self.lock:
            self.readers += 1
            if self.readers == 1:
                self.write.acquire()
    
    def release_read(self):
        with self.lock:
            self.readers -= 1
            if self.readers == 0:
                self.write.release()
    
    def acquire_write(self):
        self.write.acquire()
    
    def release_write(self):
        self.write.release()
```

## Thread Pool

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(work, item) for item in items]
    results = [f.result() for f in futures]
```

## Async (Python)

```python
import asyncio

async def task():
    await asyncio.sleep(1)
    return result

results = await asyncio.gather(*[task() for _ in range(10)])
```

## Go Concurrency

```go
ch := make(chan int)
go func() { ch <- 1 }()
val := <-ch
```

For: idiomatic.

## Common Patterns

- Mutex
- Semaphore
- Conditions
- Channels (Go)
- Futures

## Pitfalls

- Deadlock
- Race condition
- Starvation
- Livelock

## Best Practices

- Smallest lock scope
- Avoid nested locks
- Use higher abstractions (queue)
- Test under load

## Common Mistakes

- No locking (race)
- Over-locking (slow)
- Deadlock (lock order)

## Quick Refs

```python
# Mutex
lock = threading.Lock()
with lock: ...

# Queue
q = queue.Queue()

# Pool
ThreadPoolExecutor

# Async
asyncio.gather
```

## Next Topic

→ [T04 — Systems Coding](T04-Systems-Coding.md)
