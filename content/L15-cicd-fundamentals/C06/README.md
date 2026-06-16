# L15/C06 — Deployment Strategies

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Recreate.md) | Recreate | 0.5 hr |
| [T02](T02-Rolling-Update.md) | Rolling Update | 0.5 hr |
| [T03](T03-Blue-Green.md) | Blue/Green | 1 hr |
| [T04](T04-Canary.md) | Canary | 1 hr |
| [T05](T05-Shadow-Deployments.md) | Shadow Deployments | 0.5 hr |
| [T06](T06-AB-Testing.md) | A/B Testing | 0.5 hr |

## Recreate (Big Bang)

Tear down all old; start all new.

```
v1 v1 v1
   ↓ stop all
(no traffic)
   ↓ start v2
v2 v2 v2
```

### Use
- Schema incompatibility (old and new can't coexist)
- Dev environments
- Single-instance non-critical

### Cost
- Downtime (seconds to minutes)
- Not for production critical paths

## Rolling Update

Replace pods one (or N) at a time.

```
v1 v1 v1 v1
v1 v1 v1 v2
v1 v1 v2 v2
v1 v2 v2 v2
v2 v2 v2 v2
```

K8s default. Configurable:
```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 25%
      maxSurge: 25%
```

### Use
- Most cases
- Stateless services
- When can't have downtime

### Issues
- Both versions live simultaneously (must be backward-compatible)
- Slow rollout (10 min for large deploys)
- Hard to roll back fast if half-deployed bad version

## Blue/Green

Two complete environments. Switch traffic instantly.

```
Blue (v1) live
Green (v2) deployed but no traffic
   ↓ switch
Blue (v1) no traffic
Green (v2) live
```

### Implementation
- Two LB target groups
- DNS swap
- Service selector update (K8s)

### Pros
- Instant cutover
- Instant rollback (switch back)
- Test new env fully before switch

### Cons
- 2× capacity during switchover
- Long-lived blue/green is wasteful

## Canary

Gradual rollout of new version to subset of traffic.

```
99% → v1
1%  → v2 (canary)
   ↓ if SLOs stay green
90% → v1
10% → v2
   ↓
50/50
   ↓
100% → v2
```

### Implementation
- Mesh (Istio VirtualService weighted)
- Ingress controller (nginx-ingress with weights)
- AWS App Mesh / ALB weighted target groups
- Argo Rollouts / Flagger (automation)

### Argo Rollouts
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
spec:
  strategy:
    canary:
      steps:
      - setWeight: 5
      - pause: { duration: 5m }
      - setWeight: 25
      - pause: { duration: 5m }
      - analysis:
          templates:
          - templateName: success-rate
      - setWeight: 50
      - pause: { duration: 5m }
      - setWeight: 100
```

### Why It Wins
- Detect issues early on small impact
- Automated analysis (Flagger compares canary vs baseline metrics)
- Auto-rollback on bad signal

## Shadow Deployments

Send copy of production traffic to new version; don't return responses.

```
User → LB
        ├→ v1 (returns response)
        └→ v2 (response discarded)
```

### Use
- Validate v2 under real prod load
- Compare outputs to v1 (diff testing)
- Performance and behavior under real traffic without risk

### Cost
- Doubles backend load
- Side effects (writes!) need careful handling

## A/B Testing

Different versions to different user cohorts based on attributes (geo, beta flag, user ID hash).

```
User-Agent: iOS → v2
Country: JP → v3
User in beta cohort → v4
Else → v1
```

Not just deployment; product experimentation.

Tools: LaunchDarkly, Unleash, Split, Optimizely.

## Combining Strategies

Common production pattern:
- Blue/Green at infrastructure level
- Canary at the new version (5% → 100%)
- Feature flags within new version for A/B

## Choosing

| Need | Pick |
|---|---|
| Stateless web | Rolling (default) |
| Critical, must rollback fast | Blue/Green |
| Risky changes | Canary + automated analysis |
| Test under prod load | Shadow |
| Product experimentation | A/B with feature flags |
| Schema-incompat migration | Recreate (with maintenance window) |

## Pitfalls

- **Canary without metrics**: 1% gets bad, you don't notice
- **Blue/Green with shared DB**: schema changes don't blue/green well
- **Rolling with non-backward-compat changes**: chaos
- **A/B without separation of concerns**: deploy decisions polluted with product

## Interview Themes

- "Compare deployment strategies"
- "Walk me through canary with automated analysis"
- "Shadow deployment — what about writes?"
- "Blue/Green with stateful workloads — how?"
- "Decouple release from deploy — what does that mean?"
