# L24/C01/T01 — Load Balancing Algorithms

## Learning Objectives

- Pick LB algorithm
- Trade-offs

## Round Robin

Each request to next backend:
```
Req 1 → Backend A
Req 2 → Backend B
Req 3 → Backend C
Req 4 → Backend A
```

Simple. Even distribution if equal backends.

## Weighted Round Robin

```
Backend A: weight 3
Backend B: weight 1

3 reqs A, 1 req B, repeat
```

For: heterogeneous backends.

## Least Connections

Pick backend with fewest active:
```
A: 5 conns
B: 3 conns
C: 8 conns
→ Route to B
```

For: long-lived connections.

## Weighted Least Connections

Connections / weight; pick lowest.

For: weighted + long-lived.

## Hash

Route by hash of:
- Client IP
- Header
- URL path

```
hash(client_ip) % N → backend
```

For: session affinity.

## Consistent Hashing

Ring of backends:
```
Backends → ring positions
Request hash → nearest backend
Add/remove backend: only some keys move
```

For: caching / sharding.

## Random

Pick random:
- Simple
- Approximate even

For: stateless, no preference.

## Two Random Choices

Pick 2 random; least loaded:
- Almost as even as least connections
- O(1) decision

For: efficient.

## Least Response Time

Route to backend with lowest current latency:
- Tracks per-backend latency

For: heterogeneous performance.

## Choosing

| Algorithm | When |
|---|---|
| Round robin | equal backends; stateless |
| Weighted RR | heterogeneous |
| Least conn | long connections (DB pool) |
| Hash | session affinity |
| Consistent hash | distributed cache |
| Random | simple stateless |
| 2 choices | scale + balance |
| Least latency | mixed perf |

## Examples

### Web Tier
Round robin or random.

### DB Connections
Least connections.

### CDN
Consistent hashing.

### Microservice → Other Microservice
Round robin or random; mesh handles.

## Health Checks

(See T02.)

Unhealthy backend excluded.

## Per-Connection vs Per-Request

L4: per connection (sticks).
L7: per request (more even).

For HTTP: per-request often better.

## Failover

If backend fails:
- Detect (health check)
- Remove from pool
- Recheck periodically

For: resilience.

## Slow Start

New backend:
- Start with low weight
- Ramp up
- Avoid cold-start overload

For: deploy.

## Outlier Detection (Envoy)

```yaml
outlier_detection:
  consecutive_5xx: 5
  interval: 30s
  base_ejection_time: 30s
```

Eject misbehaving.

For: auto-handle bad.

## Best Practices

- Round robin baseline
- Least connections for long
- Consistent hash for cache
- Health checks
- Outlier detection
- Slow start

## Common Mistakes

- Hash on session ID (sticky pain)
- Round robin for heterogeneous (overloaded)
- No health check
- No outlier detection

## Real Examples

### Cloudflare
Anycast + consistent hash + outlier.

### Google
Maglev (consistent hash variant).

### AWS NLB
Flow hash (5-tuple).

## Quick Refs

```
nginx upstream:
  round_robin (default)
  least_conn
  ip_hash
  hash $request_uri consistent

HAProxy balance:
  roundrobin
  leastconn
  source
  uri

Envoy lb_policy:
  ROUND_ROBIN
  LEAST_REQUEST
  RING_HASH
  MAGLEV
  RANDOM
```

## Interview Prep

**Mid**: "Name the common load-balancing algorithms." — Round-robin (even rotation), weighted round-robin (capacity-aware), least-connections (route to the backend with fewest active conns — good for long-lived/variable requests), least-response-time, IP/consistent hash (sticky by key), and power-of-two-choices (random pick of 2, take the lighter). Pick based on request uniformity and whether you need affinity.

**Senior**: "How do you pick an algorithm by use case?" — Uniform short requests → round-robin or weighted RR. Long-lived or uneven requests (websockets, slow queries) → least-connections so a slow backend doesn't keep getting work. Need cache affinity or session stickiness → consistent hashing on a key. Heterogeneous backends → weighted variants. Power-of-two-choices gives near-least-connections quality without global state, which matters at high QPS.

**Staff**: "Why consistent hashing, and what problem does it solve?" — Plain `hash(key) % N` remaps almost every key when N changes, destroying cache locality and causing a mass reshuffle on scale/failure. Consistent hashing places nodes and keys on a ring so adding/removing a node only moves ~1/N of keys. Virtual nodes smooth out uneven distribution. It's how you get sticky routing (cache servers, sharded stores) that degrades gracefully when the backend set changes, instead of a stampede of misses.

## Next Topic

→ [T02 — Health Checks](T02-Health-Checks.md)
