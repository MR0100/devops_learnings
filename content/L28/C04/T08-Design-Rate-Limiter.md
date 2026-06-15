# L28/C04/T08 — Design a Rate Limiter

## Learning Objectives

- Design a distributed rate limiter
- Derive capacity from traffic, not assert it
- Reason about the accuracy / cost / latency trade-off

## Requirements

### Functional
- Limit requests per client (per API key / user / IP)
- Multiple rules: e.g. 100 req/min per user, 10k req/min per org
- Reject over-limit requests with `429` + `Retry-After`
- Limits configurable at runtime (no redeploy)
- Work across many API gateway instances (shared counters)

### Non-Functional
- Adds < 5 ms p99 to the request path
- Fails **open** under limiter outage (availability > strict enforcement) — state this assumption; some shops choose fail-closed
- Limit accuracy "good enough" — small over-admission at boundaries is acceptable
- Scales to the gateway's full traffic

## Estimation (back-of-envelope, derived)

Start from the traffic the gateway already serves:
```
peak_qps              = 1,000,000 req/s   (given/assumed peak)
checks_per_request    = 1                 (one limiter check per request)
limiter_qps           = peak_qps × checks_per_request = 1M ops/s
```

Counter memory — one counter per active client per window:
```
active_clients        = 10M               (distinct keys in a window)
bytes_per_counter     ≈ 50 B              (key + count + TTL overhead)
counter_memory        = 10M × 50 B        = 500 MB
```
That fits comfortably in one Redis node's RAM, so the bottleneck is **ops/s, not memory**. 1M ops/s exceeds a single Redis instance (~100k–200k ops/s), so we must **shard by key** — derived, not assumed.

```
shards_needed = limiter_qps / per_node_qps = 1M / 150k ≈ 7 → round to 8–10 shards
```

## High-Level Design

```
Client → API Gateway (N instances)
              │  each instance: check limit
              ▼
        Rate-Limiter library
              │ key = hash(client_id) → shard
              ▼
        Redis cluster (sharded counters)   ← config from control plane
              │
        allow → forward to backend
        deny  → 429 + Retry-After
```

- The check runs **in the gateway process** (a library), calling a shared store. Keeps latency low and avoids a separate network hop to a limiter service.
- Counters live in a **sharded Redis cluster** so no single instance owns all keys.
- Rules are pushed from a control plane (config service) and cached locally with a short TTL.

## Deep Dive: Algorithm

| Algorithm | Accuracy | Burst handling | Cost |
|---|---|---|---|
| Fixed window | Low (2× burst at boundary) | Poor | 1 counter, cheapest |
| Sliding window log | Exact | Exact | Stores every timestamp — expensive |
| Sliding window counter | Good | Good | 2 counters + interpolation |
| Token bucket | Good | Allows controlled bursts | 2 fields (tokens, last_refill) |
| Leaky bucket | Smooth | Shapes to constant rate | Queue state |

**Fixed-window boundary problem**: with a 100/min limit, a client can send 100 at 00:59 and 100 at 01:00 — 200 in 2 seconds. **Sliding-window counter** fixes this cheaply:
```
rate ≈ count_current_window
     + count_previous_window × (1 − elapsed_fraction_of_current_window)
```
For controlled bursts (let a client burst then settle), prefer **token bucket**: refill `rate` tokens/sec up to a cap; each request costs one token; deny when empty.

**Atomicity matters.** Read-modify-write across the network races under concurrency. Do the check-and-decrement atomically inside Redis with a Lua script (or `INCR` + `EXPIRE` for fixed window):
```lua
-- fixed-window: returns 1 if allowed
local c = redis.call('INCR', KEYS[1])
if c == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
if c > tonumber(ARGV[2]) then return 0 else return 1 end
```

## Deep Dive: Distributed Counting

Two designs, with an explicit trade:
- **Centralized (shared Redis)**: every gateway hits the same shard for a key → accurate, but adds a network RTT (~0.5 ms same-DC) and concentrates load on hot keys.
- **Local + sync**: each gateway keeps a local counter and periodically reconciles. Sub-millisecond and survives store outage, but over-admits during the sync gap.

Hybrid for hot keys: each gateway gets a **local sub-budget** (e.g. limit/N per instance) and only consults the central store when it nears its slice — bounds both error and central load.

## Bottlenecks & Failure Modes

- **Hot key** (one giant tenant): a single key pins one shard. Mitigate with local sub-budgets, or replicate the key across shards and sum.
- **Redis down**: fail **open** (allow) per our NFR, and alarm; a brief unlimited window beats a full outage. (Flip to fail-closed only for abuse-critical endpoints.)
- **Clock skew** across gateways corrupts sliding windows → use the store's server time, not local wall clock.
- **Thundering herd on `Retry-After`**: jitter the retry hint so denied clients don't all return at the same instant.
- **Config lag**: a limit change must propagate; bound staleness with a short local-cache TTL (e.g. 10 s).

## Trade-Offs

- **Accuracy vs latency**: exact (sliding log / central store) costs a network hop; approximate (local) is fast but over-admits.
- **Fail-open vs fail-closed**: availability vs abuse protection — decide per endpoint.
- **In-gateway library vs standalone limiter service**: library = no extra hop, but couples deploys; service = independent scaling, extra RTT.
- **Memory vs precision**: sliding-window log is exact but O(requests) memory; counter approximations are O(1).

## Real Examples

- **Stripe**: token-bucket, per-key, returns `429` with `Retry-After`.
- **Envoy / Cloudflare**: rate limiting at the edge before traffic reaches origin.
- **GitHub API**: documented limits with `X-RateLimit-Remaining` / `-Reset` headers.

## Best Practices

- Return `429` + `Retry-After` and `X-RateLimit-*` headers (never `500`)
- Atomic check-and-decrement (Lua / single command)
- Limit at the edge, before expensive work
- Make limits runtime-configurable
- Add jitter to retry hints

## Common Mistakes

- Non-atomic read-modify-write (races over-admit)
- Fixed window with no awareness of the boundary burst
- Global counter with no sharding (single hot node)
- `500` instead of `429` on limit
- Hard-coded limits requiring redeploy

## Quick Refs

```
samples: ops/s = peak_qps × checks/req
shards  = ops/s / per_node_qps

Algorithms:
  fixed window      — cheap, boundary burst
  sliding counter   — good + cheap
  token bucket      — controlled bursts
  leaky bucket      — smoothing

Atomic INCR+EXPIRE / Lua
429 + Retry-After + X-RateLimit-*
Fail open (default)
```

## Interview Prep

**Mid**: "Which algorithm would you use and why?" — Sliding-window counter for most APIs: it fixes the fixed-window boundary burst with only two counters and cheap interpolation; token bucket if the product needs to allow controlled bursts.

**Senior**: "How do you make the counter correct when many gateway instances check the same key?" — Do the check-and-decrement atomically in the shared store (Lua script or `INCR`+`EXPIRE`), not as a read-modify-write in the app; that removes the race. Shard counters by key so load spreads, and reach for local sub-budgets only when a hot key saturates one shard.

**Staff**: "The limiter's Redis cluster just went down — what happens to the API?" — It fails open per our NFR: requests are allowed and we alarm, because a brief unlimited window is better than a full outage. We'd pre-decide fail-closed only for abuse-critical endpoints (auth, payments), keep a degraded local-counter fallback to bound the blast radius, and treat the central store as best-effort accuracy, not a hard dependency.

**Principal**: "Design rate limiting for a multi-tenant platform with wildly uneven tenants." — Tiered limits per plan pushed from a control plane; per-key sharding with hot-key replication for whales; local sub-budgets per gateway to cap central load and bound error; cost-based limiting (weight by request expense, not just count); and an org-level ceiling above per-user limits so one tenant can't starve the fleet.

## Next Topic

→ [T09 — Design a Distributed Queue / Job Scheduler](T09-Design-Distributed-Queue.md)
