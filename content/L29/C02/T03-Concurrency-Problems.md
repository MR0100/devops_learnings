# L29/C02/T03 — Concurrency Problems

## Learning Objectives

- Solve the canonical concurrency problems out loud, not just in your head
- Reason about locks, conditions, queues, and channels well enough to defend a design choice
- Recognize and name the four failure modes — deadlock, race, starvation, livelock — on sight

## Why It Matters for DevOps / SRE

Concurrency is the single most DevOps-relevant slice of the coding loop. The work you actually do — health-checkers fanning out to thousands of hosts, a metrics agent draining a buffer while scrapers fill it, a deploy controller reconciling state under contention — *is* concurrency. So interviewers reach for it: a thread-safe queue or a rate limiter tests whether you understand the systems you operate, not just whether you can invert a tree.

These problems also expose judgment that pure algorithm puzzles hide. There is rarely one right answer; the signal is whether you reach for the *smallest* synchronization that's correct, whether you can articulate what breaks under contention, and whether you know when to drop down to a primitive versus lean on a higher-level abstraction like a `queue.Queue`.

## Topics

- Producer-consumer (bounded queue)
- Reader-writer lock
- Rate limiter (token bucket, sliding window)
- Thread pool / worker pool
- Async / Futures
- Go channels (CSP-style)

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

This is the canonical pattern and the right default answer: `queue.Queue` is already thread-safe and bounded, so `put` blocks when full (back-pressure on the producer) and `get` blocks when empty. You almost never need to hand-roll a condition variable here — and saying so is itself a signal that you reach for the right abstraction. The follow-up to expect: "now do it with a raw `Lock` and `Condition`," to confirm you understand what the queue is doing underneath.

## Rate Limiter

The token bucket is the most-asked DevOps concurrency problem because it *is* how API gateways and load shedders work. A bucket holds up to `rate` tokens; tokens refill continuously at `rate` per second; each call spends one. Spare tokens let a burst through, then the steady refill rate caps sustained throughput.

```python
import time
import threading

class RateLimiter:
    def __init__(self, rate):
        self.rate = rate
        self.tokens = rate          # start full so a fresh limiter allows an initial burst
        self.last = time.time()
        self.lock = threading.Lock()

    def acquire(self):
        with self.lock:
            now = time.time()
            # refill: elapsed seconds × rate, capped at the bucket capacity
            self.tokens = min(self.rate, self.tokens + (now - self.last) * self.rate)
            self.last = now
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False
```

The critical detail interviewers watch for: **initialize the bucket full** (`self.tokens = rate`), not empty. Starting at `0` means the very first `acquire()` returns `False` until tokens accrue — a classic bug that breaks the burst semantics the pattern exists to provide. State out loud that "capacity" (max burst) and "rate" (sustained) can be separate parameters; here they're collapsed into `rate` for brevity, but a real limiter takes both. Compare with the **sliding-window** approach (count timestamps in the last N seconds) when asked about precision vs memory: token bucket is O(1) memory; a precise sliding log is O(requests).

## Reader-Writer

Multiple readers may hold the lock simultaneously; a writer needs it exclusively. The implementation below is **reader-preferring**: the first reader grabs the write lock, the last reader releases it, and a counter (guarded by its own mutex) tracks how many readers are active. Call out the trade-off unprompted — reader-preferring locks can **starve writers** under a steady stream of readers; a fair or writer-preferring variant fixes that at the cost of read throughput. Naming that starvation risk is the senior signal here.

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

Go is the idiomatic choice for systems-coding rounds because channels make the producer-consumer and worker-pool patterns disappear into a few lines, and the race detector (`go test -race`) is a real tool you'd cite. The Go mantra — "don't communicate by sharing memory; share memory by communicating" — is worth saying out loud: a worker pool is `N` goroutines ranging over a jobs channel, results flowing back on a second channel, with a `sync.WaitGroup` or a closed channel signaling completion. If the interviewer is DevOps-flavored, offering the Go version after the Python one reads as fluency in the stack you'd actually operate.

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

## Interview Prep

**Junior**: "Implement a thread-safe producer-consumer." — I reach for `queue.Queue(maxsize=N)`: it's already thread-safe and bounded, so `put` blocks the producer when full and `get` blocks the consumer when empty. I'd name that this gives me back-pressure for free, and only hand-roll a `Lock` + `Condition` if asked to show what the queue does underneath.

**Mid**: "Build a token-bucket rate limiter." — A bucket of capacity `C` refilling at `rate` tokens/sec under a lock; each call refills `elapsed × rate` (capped at `C`), then spends a token if one's available. The detail I call out is initializing the bucket *full*, not empty — otherwise the first call wrongly fails and you lose the burst allowance the pattern exists for. I'd contrast it with a sliding window: token bucket is O(1) memory and allows bursts; a precise sliding log is exact but O(requests) memory.

**Senior**: "Your reader-writer lock starves writers — fix it." — The reader-preferring version lets a steady stream of readers indefinitely block a waiting writer. I'd switch to a fair lock: once a writer is queued, new readers wait behind it, so the writer is guaranteed to acquire after the in-flight readers drain. I'd state the trade-off — slightly lower read throughput for bounded writer latency — and tie it to a real case like a config cache that's read-hot but must accept updates promptly.

**Staff**: "How would you rate-limit a fleet, not one process?" — In-process token buckets don't coordinate, so N replicas allow N× the intended rate. I'd move the counter to a shared store — a Redis token bucket (e.g. atomic `INCR`/`GCRA` via a Lua script) or an envoy/gateway-level global limiter — accept the added latency and failure-mode of a network hop, and design the fallback: fail-open vs fail-closed when the limiter store is unreachable, which is a deliberate availability-vs-correctness call I'd make explicitly.

## Next Topic

→ [T04 — Systems Coding](T04-Systems-Coding.md)
