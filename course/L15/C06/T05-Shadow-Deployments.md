# L15/C06/T05 — Shadow Deployments

## Learning Objectives

- Run shadow / mirror
- Use for risk-free testing

## Shadow / Mirror

Copy traffic to new version; users see only old:
```
Users → v1 (responds to users)
         ↓ mirror
        v2 (gets copies; responses discarded)
```

For: test in prod with no user impact.

## Why

- Real traffic patterns
- Discover bugs invisible to staging
- Compare metrics (old vs new)
- No user risk

## How

### Istio Mirror

```yaml
http:
- route:
  - destination:
      host: myapp
      subset: v1
  mirror:
    host: myapp
    subset: v2
  mirrorPercentage:
    value: 100
```

100% to v1 + 100% mirror to v2.

### Argo Rollouts

```yaml
strategy:
  canary:
    steps:
    - setMirrorRoute:
        name: mirror
        match:
        - method:
            exact: GET
        percentage: 100
```

## Limitations

### Stateful Side Effects
v2 receives POST → writes to DB.
DB now has duplicate records.

Mitigation:
- Filter only safe (GET)
- Sandbox DB for v2
- Stub side effects

### Cost
2× compute.

### Timing
Mirrored requests may delay v2 → backpressure.

## Use Cases

### Test New Version
v2 = candidate. Compare metrics to v1.

### Performance Test
v2 = optimized; see if faster.

### Bug Detection
v2 = supposed fix; verify no regression.

### ML Model
v2 = new model; compare predictions to v1 (offline analysis).

## Filter

```yaml
mirror:
  host: myapp-v2
mirrorPercentage:
  value: 10   # only 10% mirrored
```

For: lower cost.

Or:
```yaml
mirror:
  host: myapp-v2
- match:
  - method:
      exact: GET
```

Only safe methods.

## Compare Metrics

Mirror metric labels:
- `version=v1`
- `version=v2`

Grafana: dual graphs.
Differences = candidate behavior.

## Latency

v2 doesn't affect v1 latency (separate paths).
But: v2 must keep up.

If v2 slow: mirroring may drop.

## ML / AB Eval

Mirror requests to v2 model:
- Log v1 prediction
- Log v2 prediction
- Compare offline (shadow eval)

For: validate model before promote.

## Stateful Apps

Mirror writes problematic:
- Duplicate orders
- Send emails twice
- Charge twice

Mitigations:
- Mock external calls in v2
- Sandbox env
- Idempotent operations with mirror-aware key

## Mirror to Different Cluster

```yaml
mirror:
  host: myapp.shadow-cluster.svc.cluster.local
```

For: completely separate; lower risk.

## Combine with Canary

```
Phase 1: Mirror to v2 (validate behavior)
Phase 2: Canary 5% real traffic
Phase 3: Promote 100%
```

For: safest rollout.

## Monitoring

Watch:
- v2 error rate
- v2 latency
- v2 response equivalence (diff from v1?)
- Resource usage

For: catch issues.

## Response Diff

Tool: ngrep or custom:
- v1 response
- v2 response
- Diff

For: behavioral equivalence test.

GitHub Scientist: similar concept (in-process).

## Best Practices

- Use for read-mostly endpoints first
- Idempotent writes only (or sandboxed)
- Filter by method (GET safer)
- Lower percentage for cost
- Compare metrics
- Auto-rollback if v2 OOMs

## Common Mistakes

- Mirror all writes (duplicate side effects)
- v2 slow blocks v1 (backpressure)
- No filter (cost spike)
- Forget to disable mirror after

## Cleanup

```yaml
# Remove after validation
http:
- route: ...
# (mirror removed)
```

## Cost

- 2× resources during shadow
- Mirror requests bandwidth
- Mirror processing CPU

For: limited duration.

## Real Examples

### LinkedIn
Test new code paths via mirror.

### Facebook
Internal mirroring for ML.

### Twitter (X)
Heavy shadow testing.

## Limitations Summary

| | Mirror | Canary |
|---|---|---|
| User impact | None | Some |
| Real traffic | Yes | Yes |
| Side effects | Risky | Real |
| Speed | Quick eval | Hours |

For: complementary.

## Quick Refs

```yaml
# Istio
mirror:
  host: SERVICE
  subset: SUBSET
mirrorPercentage:
  value: 100

# Argo Rollouts
- setMirrorRoute:
    name: NAME
    match: [...]
    percentage: 100
```

## Interview Prep

**Mid**: "Shadow / mirror."

**Senior**: "When mirror."

**Staff**: "Risk-free testing."

## Next Topic

→ [T06 — A/B Testing](T06-AB-Testing.md)
