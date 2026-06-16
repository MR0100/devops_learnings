# L24/C01/T02 — Health Checks

## Learning Objectives

- Design health checks
- Avoid false positives

## Why

LB needs to know:
- Backend healthy?
- Route or skip?

For: reliability.

## Types

### TCP
Connect succeeds.
Cheap; broad.

### HTTP
GET /health → 200.
More signal.

### Custom
Script / exec.

## Liveness

Is process up?
- TCP enough usually
- HTTP /healthz simple

## Readiness

Can serve traffic?
- Dependencies up?
- Warm cache?
- DB connected?

```python
@app.get('/ready')
def ready():
    if not db.is_connected():
        return 503
    return 200
```

For: don't route during startup.

## K8s

```yaml
livenessProbe:
  httpGet: { path: /healthz, port: 8080 }
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet: { path: /ready, port: 8080 }
  initialDelaySeconds: 5
  periodSeconds: 5
```

Liveness: restart pod if fail.
Readiness: don't send traffic.

## startupProbe

For slow-starting:
```yaml
startupProbe:
  failureThreshold: 30
  periodSeconds: 10
# Up to 5 min for app to start
```

## Threshold

```yaml
healthyThreshold: 2     # 2 consecutive ok
unhealthyThreshold: 3   # 3 fails
```

For: avoid flap.

## Interval

```yaml
interval: 30s   # check every 30s
```

Faster: more load + sensitive.
Slower: detect failures later.

For: balance.

## Health Endpoint

```python
@app.get('/health')
def health():
    return {'status': 'ok'}
```

Simple. Don't:
- Hit DB on every check
- Return slow

For: fast endpoint.

## Deep Health Check

Verify deps:
```python
@app.get('/health/deep')
def deep_health():
    if not db.ping():
        return 503
    if not redis.ping():
        return 503
    return 200
```

Don't use for LB (cascading).
Use for human checks.

## Cascading Failures

Bad: LB health checks DB.
- DB slow → all backends fail health
- LB removes all
- Total outage

For: shallow check for LB.

## Failure Detection

For LB:
- Active (LB probes)
- Passive (failed requests count)

Envoy outlier detection: passive.

## Slow Start

After unhealthy → healthy:
- Ramp traffic
- Don't dump full load

For: warm-up.

## False Positives

Cause:
- Probe too aggressive
- Backend slow but OK
- Network blip

Mitigate:
- Threshold (2-3 consecutive)
- Reasonable timeout

## Best Practices

- Simple endpoint
- < 100 ms response
- No deep deps
- Sensible thresholds
- Slow start
- Liveness vs readiness clear

## Common Mistakes

- DB on health check (cascading)
- Threshold 1 (flapping)
- Slow endpoint
- No readiness (traffic during startup)
- No interval (constant load)

## Quick Refs

```yaml
# K8s
livenessProbe:
readinessProbe:
startupProbe:

# Nginx
upstream X {
  server backend1 max_fails=3 fail_timeout=30s;
}

# HAProxy
backend web
  option httpchk GET /health
  server web1 :80 check
```

## Interview Prep

**Mid**: "Health check."

**Senior**: "Liveness vs readiness."

**Staff**: "Avoid cascading failures."

## Next Topic

→ [T03 — Sticky Sessions](T03-Sticky-Sessions.md)
