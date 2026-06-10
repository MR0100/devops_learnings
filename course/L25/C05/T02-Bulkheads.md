# L25/C05/T02 — Bulkheads

## Learning Objectives

- Apply bulkhead pattern
- Isolate failures

## Bulkhead

Ship metaphor:
- Compartments
- Leak in one doesn't sink ship
- Isolate damage

## Pattern

Isolate resources per dependency:
- Connection pool
- Thread pool
- Memory

If one dep fails: only that pool exhausted.

## Example

Without bulkhead:
```python
# One pool for all
pool = ConnectionPool(max=100)

call_service_a(pool)  # If slow, uses 100 conns
call_service_b(pool)  # Blocked: no conns
```

A's slowness affects B.

## With Bulkhead

```python
pool_a = ConnectionPool(max=50)
pool_b = ConnectionPool(max=50)

call_service_a(pool_a)  # Uses A's 50
call_service_b(pool_b)  # Has own 50
```

A's slowness doesn't affect B.

## Resilience4j

```java
Bulkhead bulkhead = Bulkhead.ofDefaults("svc");
bulkhead.executeSupplier(() -> callService());
```

If too many concurrent: reject.

## Tradeoff

- More resources allocated (total)
- Less sharing
- Stronger isolation

## Use Cases

### Multi-Tenant
Per tenant: own pool.
One bad tenant: doesn't affect others.

### Mixed Workloads
Read vs write: own pools.

### Per Endpoint
/api/slow: own pool.
/api/fast: not affected.

## K8s

Pod-level isolation:
- Different deployments
- Different resource limits

For: macro bulkhead.

## Service Mesh

```yaml
trafficPolicy:
  connectionPool:
    tcp:
      maxConnections: 100
    http:
      http1MaxPendingRequests: 50
      http2MaxRequests: 1000
```

Per upstream.

## Best Practices

- Per critical dependency
- Per tenant (multi-tenant)
- Per endpoint pattern
- Monitor saturation

## Common Mistakes

- One pool for all
- Pools too small (throttling normal)
- No monitoring

## Quick Refs

```
Bulkhead: isolated pools
Per dependency or tenant or endpoint
Tools: Resilience4j, service mesh
```

## Interview Prep

**Mid**: "What's bulkhead."

**Senior**: "Apply bulkhead."

**Staff**: "Multi-tenant isolation."

## Next Topic

→ [T03 — Retries with Backoff & Jitter](T03-Retries.md)
