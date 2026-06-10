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

**Mid**: "LB algorithms."

**Senior**: "Pick by use case."

**Staff**: "Consistent hashing."

## Next Topic

→ [T02 — Health Checks](T02-Health-Checks.md)
