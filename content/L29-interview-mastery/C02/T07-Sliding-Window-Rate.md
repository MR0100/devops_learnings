# L29/C02/T07 — Worked Example: Sliding-Window Rate Counting

## Learning Objectives

- Count events in a moving time window — the core of rate limiting, alerting, and SLO burn
- Implement the fixed-window, sliding-log, and sliding-window-counter variants and trade them off
- Bound memory so the solution survives a high-throughput stream, not just a toy test

## Why This Problem

"How many requests has this client made in the last 60 seconds?" underlies rate limiters, abuse detection, autoscaling triggers, and SLO error-budget burn-rate alerts. It's the time-series cousin of the array sliding-window pattern, and interviewers like it for DevOps because the naive answer (keep every timestamp) has an obvious memory problem that forces you to reason about accuracy-vs-memory — exactly the judgment the role needs. You should be able to write the precise version, explain why it doesn't scale, and offer the bounded approximation.

## The Problem

> Implement `hit(timestamp)` that records an event, and `count(timestamp)` that returns how many events occurred in the last W seconds (a moving window ending at `timestamp`).

This is LeetCode's "Logger / Hit Counter" generalized. Real version: per-client request counting for a rate limiter, where W = 60s and the limit is, say, 100 requests/minute.

## Step 1 — Clarify

- **Window length W** and whether it's a true sliding window (last W seconds, always) or a fixed window (per calendar minute).
- **Are timestamps monotonic?** Hits usually arrive in non-decreasing time; if they can arrive out of order, the data structure changes.
- **Granularity / scale:** millions of hits/sec? Then storing every timestamp is a non-starter — bucket them.
- **Exact or approximate?** This is the real fork: exact costs memory; approximate is O(1).

## Step 2 — Sliding Log (exact, the starting point)

Keep a queue of timestamps; on each `count`, evict everything older than `now - W`.

```python
from collections import deque

class SlidingLog:
    def __init__(self, window_seconds):
        self.window = window_seconds
        self.events = deque()          # timestamps, oldest at the left

    def hit(self, ts):
        self.events.append(ts)

    def count(self, ts):
        cutoff = ts - self.window
        while self.events and self.events[0] <= cutoff:
            self.events.popleft()      # drop events that fell out of the window
        return len(self.events)
```

This is **exact** and the natural first answer. Each `hit` is O(1); each `count` is amortized O(1) because every timestamp is evicted exactly once across the run. The fatal flaw to name out loud: **memory is O(events in the window)** — at 1M requests/sec with a 60s window that's 60M timestamps per client. Correct, but it won't survive production.

## Step 3 — Fixed-Window Counter (cheap, but bursty)

Drop to a single counter per fixed interval (e.g. per calendar minute). O(1) memory.

```python
import time

class FixedWindow:
    def __init__(self, window_seconds, limit):
        self.window = window_seconds
        self.limit = limit
        self.start = None
        self.count = 0

    def allow(self, ts):
        bucket = int(ts // self.window)
        if bucket != self.start:       # new window → reset
            self.start, self.count = bucket, 0
        if self.count < self.limit:
            self.count += 1
            return True
        return False
```

O(1) time and space. The flaw to state: the **boundary burst**. A client can send `limit` requests at 0:59 and another `limit` at 1:00 — `2 × limit` in a two-second span — because the counter resets at the window edge. Fine for coarse quotas; wrong for tight abuse limits.

## Step 4 — Sliding-Window Counter (the production answer)

The standard compromise (this is what Cloudflare's rate limiter and many gateways use): keep counters for the **current** and **previous** fixed windows, and weight the previous window by how much of it still overlaps the sliding window.

```python
class SlidingWindowCounter:
    def __init__(self, window_seconds, limit):
        self.window = window_seconds
        self.limit = limit
        self.cur_bucket = None
        self.cur = 0
        self.prev = 0

    def allow(self, ts):
        bucket = int(ts // self.window)
        if bucket != self.cur_bucket:
            # roll: current becomes previous, possibly skipping an empty window
            self.prev = self.cur if bucket == (self.cur_bucket or bucket) + 1 else 0
            self.cur = 0
            self.cur_bucket = bucket

        # fraction of the previous window still inside the sliding window
        elapsed = (ts % self.window) / self.window     # 0.0 .. 1.0 into current bucket
        estimate = self.prev * (1 - elapsed) + self.cur

        if estimate < self.limit:
            self.cur += 1
            return True
        return False
```

The estimate `prev × (1 − elapsed) + cur` linearly fades out the previous window as time advances. It's **O(1) memory** (two counters), smooths the boundary burst that breaks the fixed window, and is accurate enough that it's the de-facto industry default. The approximation assumes events were uniformly distributed in the previous window — call that assumption out; it's slightly off under bursty traffic but bounded and cheap.

## Step 5 — Relation to Token Bucket

Connect it to the other rate limiter (see [T03](T03-Concurrency-Problems.md)): token bucket allows a configurable burst then enforces a steady rate; sliding-window-counter enforces a smooth "N per window" with no separate burst allowance. Token bucket is better when you *want* to permit short bursts; sliding window is better when the contract is literally "no more than N per minute." Knowing which contract the question implies — burst-tolerant vs strict count — is the discriminating answer.

## Worked Trace

`SlidingLog(window=10)`, events at t = 1, 3, 8; then `count(t=11)`:

- cutoff = 11 − 10 = 1. Evict events `<= 1` → drop t=1.
- Remaining: `[3, 8]` → count = 2. (The event at t=1 has aged out of the 10s window.)

## Best Practices

- Start with the exact sliding log, then *immediately* name its memory cost — that pivot is the signal.
- Reach for the sliding-window counter as the production answer; it's O(1) and smooths boundaries.
- State the uniform-distribution assumption in the counter estimate so the interviewer knows you see the error.
- Bucket timestamps when granularity allows; per-second buckets cut memory by orders of magnitude with negligible accuracy loss.
- For a *fleet*, push the counters to a shared store (Redis) — in-process windows don't coordinate across replicas.

## Common Mistakes

- Storing every timestamp and never addressing the unbounded-memory problem.
- Using a fixed window for a strict abuse limit and missing the 2× boundary burst.
- Off-by-one on eviction (`<` vs `<=` at the cutoff) — decide whether the boundary event is in or out and be consistent.
- Assuming timestamps are monotonic when the problem allows out-of-order arrival.
- Forgetting that per-process counters under-count the true global rate across N replicas.

## Quick Refs

```
Sliding log:    deque of timestamps; exact; O(events) memory   ← don't ship
Fixed window:   one counter/interval; O(1); boundary 2x burst
Sliding-window  prev*(1-elapsed)+cur; O(1); industry default
  counter:      assumes uniform spread in prev window
Token bucket:   burst + steady rate (see T03) — different contract
Fleet:          counters in Redis; in-process windows don't coordinate
```

## Interview Prep

**Junior**: "Count events in the last 60 seconds." — A deque of timestamps: append on hit, and on count evict everything older than `now - 60` from the front, then return the length. Each timestamp is evicted once, so it's amortized O(1) per call — but I'd flag that memory grows with the number of events in the window.

**Mid**: "That uses too much memory — fix it." — Drop from storing every timestamp to counters. A fixed-window counter is O(1) but allows a 2× burst across the window boundary. The sliding-window counter fixes that: keep current and previous bucket counts and weight the previous one by how much of it still overlaps — O(1) memory, smooth boundaries. It's what most gateways actually use.

**Senior**: "Sliding-window counter vs token bucket — when each?" — Token bucket permits a configurable burst then a steady rate; the sliding window enforces a strict 'N per window' with no separate burst budget. If the contract is 'allow short spikes but cap sustained throughput' I use token bucket; if it's literally 'never more than N per minute' I use the sliding window. The deciding factor is whether bursts are desired or forbidden.

**Staff**: "Make it correct across a fleet of rate-limiter replicas." — In-process windows don't coordinate, so N replicas allow ~N× the intended rate. I'd centralize the counters in Redis (atomic increments with TTL per window, or a sliding-window Lua script), accept the network-hop latency, and design the failure mode explicitly: fail-open to protect availability or fail-closed to protect the backend when Redis is unreachable. That availability-vs-correctness choice is the real design decision, and I'd make it deliberately rather than by accident.

## Next Topic

→ Move to [L29/C03 — System Design for SRE/DevOps](../C03/README.md)
