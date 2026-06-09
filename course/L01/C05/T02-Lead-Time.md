# L01/C05/T02 — Lead Time for Changes

## Learning Objectives

- Define and compute Lead Time for Changes
- Distinguish from "lead time for ticket" (a related but different metric)
- Identify the bottlenecks that lengthen LT

## Definition

> The amount of time it takes a commit to get into production.

Note: from **code committed** to **code in production**, not from "ticket created" to production.

## How to Measure

```
LT = production_deploy_time - first_commit_time_in_change
```

Median (not mean) is preferred — long tail of outliers will skew mean.

Source data:
- Git commit timestamps
- CI pipeline timestamps
- Deploy completion timestamps

## Decomposing Lead Time

LT = sum of:
- PR review time
- CI time (build + test)
- Wait time (queues)
- Approval / change board time
- Deployment time
- Post-deploy verification time

The largest component is almost always one of: PR review wait, CI time, or change board.

## Benchmarks (DORA 2023)

| Performer | LT |
|---|---|
| Elite | < 1 hour |
| High | 1 day – 1 week |
| Medium | 1 week – 1 month |
| Low | 1 month – 6 months |

## Capabilities That Drive Low LT

- Trunk-based dev
- Fast CI (< 10 min)
- Automated quality gates (no human approvals for routine changes)
- Self-service deploy
- Loosely coupled architecture
- Small batch sizes

## Common Lead Time Distributions

A team's LT is usually log-normal:

```
freq
 │ ▆▆▆
 │ ███
 │ ███▅
 │ █████▃
 │ ██████▂▁           ▁
 └────────────────────────────► hours
   0  4  8  12  16  20  24   72
```

Outliers (e.g., 24h, 72h) usually indicate: stuck PR, hotfix, manual intervention, rollback. Investigating outliers reveals fixable systemic issues.

## Common Bottlenecks (Diagnosis Tree)

```
LT > 1 day?
├── PR review > 4 hr?
│   └── Code owner overload, low review SLA
├── CI > 10 min?
│   └── Slow tests, lack of parallelism, no caching
├── Wait for approver > 1 hr?
│   └── Manual gate; replace with automated check
└── Deploy time > 10 min?
    └── Big artifact, slow rollout, no canary
```

## Pitfalls

- **Conflating with ticket lead time**: LT is from commit, not ticket creation
- **Median hides variance**: report median + p90 + p99
- **Ignoring change size**: LT must be compared for similar-sized changes
- **Holiday windows**: filter out weekends/holidays for fair comparison

## Real-World Example

A team baseline: median LT = 3 days, p90 = 2 weeks.

| Investigation | Finding |
|---|---|
| CI took 45 min (was target 15) | Migrate to GitHub Actions matrix builds; LT drops 30 min/day |
| PR review SLA absent | Adopt 4-hour SLA + on-call reviewer; LT drops 6 hr |
| Change board for all changes | Pre-approve low-risk classes; LT drops 1 day |

Result: median LT goes from 3 days to 4 hours over 1 quarter.

## Interview Prep

**Mid**: "What is Lead Time for Changes?"

**Senior**: "Our LT is 5 days but our CI is 8 minutes. Where's the time going?"
- PR review, approvals, queueing. Suggest investigation: instrument PR-to-merge time, deploy frequency vs commit frequency.

**Staff**: "Design a strategy to reduce LT in a regulated environment that requires evidence for every change."

## Next Topic

→ [T03 — Change Failure Rate](T03-Change-Failure-Rate.md)
