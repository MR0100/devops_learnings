# L01/C05/T03 — Change Failure Rate

## Learning Objectives

- Define CFR
- Distinguish from "incident rate" (related but different)
- Identify CFR-driving practices

## Definition

> The percentage of deployments to production that result in a service degradation and require remediation (rollback, hotfix, patch).

## Formula

```
CFR = count(deploys_causing_failure) / count(all_deploys)
```

The numerator is the contested part. Use:

- A deploy is "failed" if it required a fix in the next deploy specifically to address it OR triggered a P0/P1 incident.
- Routine subsequent feature work is not "failure".

## Benchmarks (DORA 2023)

| Performer | CFR |
|---|---|
| Elite | 0–15% |
| High/Medium | 16–30% |
| Low | 46–60% |

> Note: 2022/2023 reports adjusted benchmarks; in some years, elite was 0-5%. CFR is the metric that has shifted most.

## How to Instrument

- Tag deploys with a unique ID (commit + timestamp)
- Tag incidents with the deploy that *introduced* them (incident postmortems link to deploys)
- Compute monthly

## Capabilities That Drive Low CFR

- Robust test automation (catches regressions)
- Canary deployments with auto-rollback
- Feature flags decoupling deploy from release
- Quality observability (catches issues fast)
- Smaller batches (less surface area per deploy)

## CFR vs Incident Rate

| Metric | Numerator | Denominator |
|---|---|---|
| CFR | Failed deploys | All deploys |
| Incident rate | Incidents | Time (per week/month) |

You can have low CFR and high incident rate (e.g., external dependencies failing). You can have high CFR and low incident rate (e.g., few deploys).

## CFR Math vs MTTR Math (a Cautionary Tale)

Suppose:
- DF = 100/day
- CFR = 5%
- MTTR per failed deploy = 30 min

Then: 5 failed deploys/day × 30 min = 2.5 hours of incident time per day = ~5% of business hours

If you halve CFR to 2.5% → ~1.25 hr/day of incident time.
If you halve MTTR to 15 min instead → ~1.25 hr/day of incident time.

**The lever you should pull depends on which is cheaper to halve.** Often CFR is cheaper than MTTR for early-stage orgs (better tests, canaries); MTTR cheaper for later-stage (better observability and runbooks).

## Common Bottlenecks

| Bottleneck | Fix |
|---|---|
| Tests don't catch regressions | Contract tests, integration coverage |
| Manual smoke tests post-deploy | Automated synthetic monitoring |
| Big-bang releases (10 services together) | Decouple, deploy independently |
| Canary signal weak / ignored | Quantitative canary scorecards |
| No auto-rollback | Argo Rollouts, Flagger, Spinnaker auto-canary analysis |

## Real-World Example

A team CFR is stuck at 20%. They investigate:

- 30% of failures came from a single service with weak tests → add contract tests, CFR for that service goes 40% → 10%
- 20% from missing canary on a high-traffic service → add canary, CFR drops 5%
- 15% from config drift between staging and prod → make IaC the source of truth, drops 4%

Org CFR moves 20% → 8% over 2 quarters.

## Interview Prep

**Mid**: "What's Change Failure Rate?"

**Senior**: "Our CFR is 30%. We can either invest in better testing or canary deployments. Which first?"
- Either is defensible. A great answer: canary first — it stops 90% of bad deploys *regardless of cause* with one investment, while testing requires per-service work.

**Staff**: "Design a CFR-reduction program for a multi-product company with shared infrastructure."

## Next Topic

→ [T04 — Mean Time to Recovery (MTTR)](T04-MTTR.md)
