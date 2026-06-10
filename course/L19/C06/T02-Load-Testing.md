# L19/C06/T02 — Load Testing in Anger

## Learning Objectives

- Test at real scale
- Find limits

## Why "In Anger"

Test:
- Real production-like infra
- Real data shape
- Real load patterns
- Realistic durations

Not toy.

## Goals

- Find breaking point
- Identify bottlenecks
- Validate capacity
- Confirm SLO holds

## Approaches

### Synthetic Load
Generate fake requests.

### Replay Production
Capture + replay.

### Shadow Production
Mirror real to test (See L15/C06/T05).

### Live Test
Inject real traffic to candidate.

## Tools

- k6 (modern, scriptable)
- JMeter (mature, GUI)
- Locust (Python)
- Gatling (Scala)
- wrk (simple, fast)
- Vegeta (Go)

(See L15/C04/T04.)

## Production-Like

Test env must be:
- Same instance types
- Same DB scale
- Same network
- Same data shape

Differences = wrong results.

## Realistic Data

```python
# Bad: same user repeatedly (cache hit)
# Good: random users from real distribution

users = load_real_user_sample()
random.choice(users)
```

## Realistic Patterns

- Diurnal (peak/trough)
- Burst (spikes)
- Sustained

Not just steady.

## Test Phases

### Smoke
1 user; verify works.

### Load
Expected peak; verify SLO.

### Stress
2x expected; find break.

### Spike
0 → max in seconds.

### Soak
Hours of sustained; find leaks.

## Stress Test

```javascript
// k6
options: {
  stages: [
    { duration: '5m', target: 500 },
    { duration: '5m', target: 1000 },
    { duration: '5m', target: 2000 },
    { duration: '5m', target: 5000 },
    { duration: '5m', target: 10000 },  // break point?
  ],
}
```

Find: where does it fail?

## Capacity Confirmation

Test forecasted peak + 50%.

If holds SLO: provision matches forecast.

## Bottleneck Identification

Profile during:
- CPU
- Memory
- Disk
- Network
- DB connections
- Lock contention

Find: what saturates first.

## Database Limits

```sql
SHOW MAX_CONNECTIONS;
```

Connection pool limits.

For: tune.

## Network Saturation

```
1 Gbps NIC: 125 MB/s
After: drops
```

For: SDN limits.

## CPU Limits

When > 70% sustained:
- Latency creeps
- Eventually saturates

For: provision for headroom.

## Memory Pressure

When > 90%:
- GC pressure
- Swapping
- OOM

## Lock Contention

```
goroutines / threads waiting
```

Identify hot locks. Refactor.

## Cache Hit Rate

During load:
- Hit rate?
- If drops: backend overwhelmed

For: cache size adequate?

## SLO Validation

```javascript
thresholds: {
  http_req_duration: ['p(99)<500'],
  http_req_failed: ['rate<0.01'],
}
```

Test SLO at projected peak.

## Pre-Launch Checklist

- Smoke test pass
- Load test at projected peak pass
- Stress test identifies break
- Soak finds no leaks
- Failover verified

## Production Caveats

Test on prod-like:
- Costs (running large infra for test)
- Risk (real load)

Test windows:
- Off-peak
- Coordinated

## Capacity Buffer

Test confirms: provision X for SLO.

Add buffer:
- 50% for known surge
- 100% for unprecedented

## Tooling

### k6
```bash
k6 run --vus 1000 --duration 30m test.js
```

### Distributed
k6 Cloud or operator.

For massive: millions VUs.

## Results

```
RPS:     50,000
p99:     180 ms
Errors:  0.05%
CPU:     65%
DB:      45% conn
```

Per-resource utilization.

## Comparison

Before vs after deploy:
- p99 baseline: 100 ms
- After: 150 ms

Regression detected.

For: CI integration.

## Game Day

Production stress test:
- Inject failures
- High load
- Verify recovery

(See L19/C07/T03.)

## Best Practices

- Production-like env
- Realistic data
- Stages (smoke → load → stress)
- Profile during
- SLO validation
- Regression check

## Common Mistakes

- Test in dev (different)
- Same user repeated (cache)
- One run = decision (variance)
- Skip soak
- No baselines

## Quick Refs

```javascript
// k6
options: {
  stages: [
    { duration: '5m', target: 100 },   // smoke
    { duration: '5m', target: 1000 },   // load
    { duration: '5m', target: 5000 },   // stress
  ],
  thresholds: {
    http_req_duration: ['p(99)<500'],
    http_req_failed: ['rate<0.01'],
  }
}
```

## Interview Prep

**Mid**: "Load test types."

**Senior**: "Find break point."

**Staff**: "Capacity validation."

## Next Topic

→ [T03 — Headroom Management](T03-Headroom-Management.md)
