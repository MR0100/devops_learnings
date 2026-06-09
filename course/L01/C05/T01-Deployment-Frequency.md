# L01/C05/T01 — Deployment Frequency

## Learning Objectives

- Compute Deployment Frequency for your team
- Understand what counts as a "deploy" (definitional traps)
- Identify the engineering capabilities that drive DF

## Definition

> The frequency at which an organization successfully releases to production.

Common time windows: per day, per week, per month.

## What Counts as a Deploy?

This is contested. Use the following test:

> A deploy is *one promotion to production of a versioned artifact, intended to serve customer traffic*.

This means:
- ✅ Releasing v2.4.1 to prod
- ✅ A canary that becomes full rollout
- ❌ A revert (counts as its own deploy because the artifact changes)
- ❌ A config-only change (debatable — count if it can affect prod; treat separately for analysis)
- ❌ A staging deploy
- ❌ An infrastructure change unless it changes the runtime behavior

## How to Measure

```
DF = count(prod_deploys) / time_window
```

Source data:
- CI/CD system audit log
- ArgoCD / Flux sync history
- Tag pushes to a release branch
- Cloud provider deployment APIs (CodeDeploy, etc.)

## Benchmarks (DORA 2023)

| Performer | DF |
|---|---|
| Elite | Multiple times per day |
| High | Daily to weekly |
| Medium | Weekly to monthly |
| Low | Less than monthly |

## Engineering Capabilities That Drive DF

The following capabilities (from DORA's Continuous Delivery research) strongly correlate with high DF:

1. **Trunk-based development** — no long-lived branches
2. **Continuous integration** — every commit triggers a build
3. **Comprehensive test automation** — high confidence to ship
4. **Test data management**
5. **Empowered teams** — they decide when to deploy
6. **Deployment automation** — push-button or zero-button
7. **Loosely-coupled architecture** — services can deploy independently

## Common Bottlenecks (and Fixes)

| Bottleneck | Fix |
|---|---|
| Long-lived feature branches | Trunk-based dev + feature flags |
| Manual approval gates | Automated quality gates |
| Big-bang releases coordinating teams | Service decoupling + independent pipelines |
| Slow test suite | Test pyramid + parallelism + caching |
| Manual smoke tests post-deploy | Automated synthetic monitoring |

## Pitfalls

- **Counting wrong**: counting all CI runs inflates the number
- **Per-team variance hidden**: an org-wide average hides teams in the basement
- **Ignoring failed deploys**: counting only successful inflates DF
- **Pursuing as vanity**: deploying nothing 100 times is still DF=100

## Real-World Example

A SaaS company moves from weekly releases to per-commit deploys:

| Quarter | DF | LT | CFR | MTTR |
|---|---|---|---|---|
| Q1 (before) | 1/week | 7 days | 8% | 90 min |
| Q2 (trunk-based) | 5/week | 2 days | 12% | 75 min |
| Q3 (canaries+flags) | 20/week | 6 hours | 6% | 30 min |
| Q4 (mature) | 50/week | 1 hour | 3% | 12 min |

Note how all four metrics improve together — that's the DORA "speed and stability rise together" finding in action.

## Interview Prep

**Mid**: "Define Deployment Frequency. What counts as a deploy?"

**Senior**: "Our DF is once per week. What capabilities would you invest in to get to daily?"

**Staff**: "Our DF is high but CFR is rising. What's happening and what's your plan?"
- Either testing is gapped, observability misses regressions, or canary signal is weak. Probably all three. Plan: contract tests, canary scorecards, automated rollback triggers.

## Next Topic

→ [T02 — Lead Time for Changes](T02-Lead-Time.md)
