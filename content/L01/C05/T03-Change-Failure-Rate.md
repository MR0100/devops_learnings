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

## Common Mistakes

- **Defining "failure" inconsistently** — without a written rule (rollback, hotfix, degraded SLO, incident), CFR is uncomparable across teams and over time.
- **Counting only deploys that page** — silent regressions that need a follow-up fix are failures too; missing them flatters the number.
- **Reading CFR without volume** — 35% CFR at 2 deploys/week is very different from 35% at 50/day; always pair CFR with deploy frequency.
- **Slowing down to lower CFR** — fewer, bigger releases can drop the *rate* while making each failure larger and recovery slower.
- **Blaming the metric on people** — high CFR is a signal of weak tests, weak canary, or environment drift, not careless engineers.

## Best Practices

- **Write a precise failure definition** — e.g., "any deploy requiring rollback, hotfix, or causing an SLO breach within 1 hour" — and instrument it automatically.
- **Invest in canary first** — progressive delivery with a quantitative scorecard stops most bad deploys regardless of root cause, with one investment.
- **Add contract and integration tests** where regressions actually originate, not just more unit tests.
- **Make IaC the single source of truth** to kill staging/prod drift, a common silent CFR driver.
- **Wire automated rollback** (Argo Rollouts, Flagger, Spinnaker) so a failing canary self-heals before users notice.

## Quick Refs

**Formula**: `CFR = (deploys causing a failure) / (total deploys)` over a window. Define "failure" once, in writing.

**What usually counts as a failure**: rollback · hotfix/forward-fix · SLO breach attributable to the deploy · incident opened.

**Bottleneck → fix**

| Symptom | Lever |
|---|---|
| Tests miss regressions | Contract + integration tests |
| Bad deploys reach all users | Canary + scorecard |
| Staging ≠ prod | IaC as source of truth |
| Failures linger | Automated rollback |

**DORA 2023 benchmarks**: Elite/High ≈ 5–10% · Medium ≈ 10–15% · Low ≈ 40%+. Read CFR **with** deployment frequency, never alone.

## Interview Prep

**Mid**: "What's Change Failure Rate?"

**Senior**: "Our CFR is 30%. We can either invest in better testing or canary deployments. Which first?"
- Either is defensible. A great answer: canary first — it stops 90% of bad deploys *regardless of cause* with one investment, while testing requires per-service work.

**Staff**: "Design a CFR-reduction program for a multi-product company with shared infrastructure."

## Next Topic

→ [T04 — Mean Time to Recovery (MTTR)](T04-MTTR.md)
