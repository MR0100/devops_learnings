# L24/C01 — Load Balancing Algorithms

## Topics

- **T01 Round Robin, Least Connections, Weighted, Consistent Hashing** — Common algorithms
- **T02 Health Checks** — Active vs passive
- **T03 Sticky Sessions** — Affinity

## Algorithms

### Round Robin
- Cycle through targets in order
- Simple
- Good when targets are identical
- Bad if backend latencies vary

### Weighted Round Robin
- Different targets get different shares
- Useful for heterogeneous fleet
- Or: gradual canary (90/10 split)

### Least Connections
- Route to target with fewest active connections
- Good for long-lived connections (WebSocket)
- Bad when connection ≠ work (some connections idle)

### Random
- Pick at random
- Equivalent to round-robin on average
- Easier to implement (no shared state)

### Power of Two Choices
- Pick 2 random; choose less loaded
- Surprisingly good performance
- Less coordination than maintaining state

### Least Response Time
- Track response time per target
- Route to fastest
- Adapts to backend health

### Consistent Hashing
- Hash request → assign to target
- Same request → same target (cache locality)
- Adding/removing target → only fraction of requests rerouted
- Used by: CDN cache servers, Memcached client routing

```
   targets on a ring:
        T1
   T6         T2
   T5         T3
        T4
   
   Request hash → walk clockwise → nearest target
```

### Hash Variants
- **Rendezvous (HRW)**: each request hashes to all targets; pick target with max hash; similar to consistent but no ring
- **Maglev** (Google): table-based; very efficient lookup

### EWMA (Exponentially Weighted Moving Average)
Used by Envoy, Linkerd. Weight = recent latency. Naturally avoids slow backends.

## Choosing Algorithm

| Need | Pick |
|---|---|
| Stateless equal targets | Round robin |
| Long-lived connections | Least connections |
| Cache locality | Consistent hashing |
| Heterogeneous fleet | Weighted |
| Adaptive to slow backends | EWMA / Least response time |

## Health Checks

### Active
LB pings target periodically:
```yaml
health_check:
  type: http
  path: /healthz
  interval: 5s
  timeout: 2s
  unhealthy_threshold: 3
  healthy_threshold: 2
```

After 3 consecutive failures, mark unhealthy. After 2 successes, recover.

### Passive
LB counts failed requests; if rate exceeds threshold, eject target.

```yaml
outlier_detection:
  consecutive_5xx: 5
  interval: 30s
  base_ejection_time: 30s
  max_ejection_percent: 50
```

### Best Practices
- Health endpoint must be lightweight
- Check actual dependencies (DB connectivity) only sometimes — full check would cascade failures
- Distinguish liveness (process up) from readiness (ready for traffic)
- Eviction thresholds: avoid evicting too many at once

## Sticky Sessions

Route same user/client to same backend.

### Methods
- **Cookie-based**: LB sets `JSESSIONID`; routes to matching backend
- **Source IP-based**: hash of client IP → target (problematic for NAT)
- **HTTP header**: custom header for routing

### Why Avoid
- Uneven load (some backends busy, others idle)
- Backend failure = sticky session loss
- Limits scalability

### When Sticky Sessions Are OK
- Stateful WebSocket (long-lived; tear down on backend failure)
- Cache locality benefits (rare)
- Legacy apps storing session locally

Better alternative: external session store (Redis), so any backend can serve any request.

## Load Balancer Tiers

### L4 (TCP)
- Routes based on 5-tuple (src IP, src port, dst IP, dst port, protocol)
- Fast; no inspection
- Examples: AWS NLB, GCP TCP LB, HAProxy in TCP mode

### L7 (HTTP)
- Routes based on URL, header, method
- Slower (inspects request); richer features
- Examples: AWS ALB, GCP HTTPS LB, Nginx, Envoy, HAProxy in HTTP mode

### L4+L7 Chain
- L4 in front for raw throughput; L7 behind for routing
- Common when L7 LB needs to scale

## Connection Draining

When removing target, finish in-flight requests before fully removing.

```yaml
target_group:
  deregistration_delay: 60s
```

Without draining: in-progress requests fail.

## Outlier Detection

Beyond health checks: detect targets that misbehave.

Envoy:
```yaml
outlier_detection:
  consecutive_5xx: 5             # 5 consec 5xx → eject
  consecutive_gateway_failure: 3
  interval: 10s
  base_ejection_time: 30s
  max_ejection_percent: 50       # don't eject all
```

Self-healing without manual intervention.

## Interview Themes

- "Compare LB algorithms"
- "Consistent hashing — when?"
- "Health check design"
- "Sticky sessions — pros and cons"
- "L4 vs L7"
- "Outlier detection vs health check"
