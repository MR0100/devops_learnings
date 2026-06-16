# L19/C01/T02 — Embracing Risk

## Learning Objectives

- Calculate acceptable risk
- Use error budget

## Why Embrace Risk

100% reliability:
- Impossible in distributed systems
- Diminishing returns
- Slows innovation

Acceptable risk:
- Faster shipping
- Customer-acceptable
- Cost-effective

## Cost of Reliability

99% → 99.9% → 99.99% → 99.999%

Each "9":
- ~10× cost
- Diminishing user value

Choose right level per service.

## Service Tiers

- Critical (payment): 99.99%
- Important (search): 99.9%
- Internal (admin): 99%
- Non-critical (test): 99%

Tier matches business value.

## Error Budget Math

99.9% = 0.1% error budget = 43 min/month.

Use:
- Risky deploy (cost some)
- Experiment (calculated)
- Plan outages (maintenance)

## Spend Wisely

Like financial budget:
- Track spending
- Plan large purchases
- Save for opportunities

## When Budget Exhausted

EBP (Error Budget Policy):
- Freeze risky changes
- Focus on reliability
- Postmortem heavy

## When Budget Healthy

- Ship features
- Take calculated risks
- Innovate

For: pace bound by reliability.

## Risk Categories

### Calculated
Known unknown:
- Risky deploy
- New feature

Tradeoff: feature vs reliability.

### Operational
Hardware fails, deploys break.
Mitigate: design + automation.

### Catastrophic
Datacenter loss, region down.
Mitigate: multi-region.

## Acceptable Failure

For 99.9% SLO:
- 43 min outage/mo OK
- 60 sec/mo: ideal
- 5 min: routine

Plan for these.

## Risk Communication

To product:
- "99.99% costs 10× more"
- "Customers tolerate 5 min/month"
- Show data.

For: aligned tradeoffs.

## Risk Acceptance

Per service:
- Stakeholder agrees on SLO
- Sign-off
- Periodic review

## Game Days

Test failure handling:
- Inject failures
- Verify SLO
- Build confidence

(See L19/C07.)

## Chaos

Production:
- Random pod kill (Chaos Monkey)
- Latency injection
- Region failover

For: continuous risk validation.

## Risk Register

List risks:
- Description
- Probability
- Impact
- Mitigation
- Owner

Track + review quarterly.

## Risk vs Reliability Math

Probability of unrelated event:
```
P(A AND B) = P(A) × P(B)
```

Service A 99.9% × Service B 99.9% = 99.8%.

For: chained services degrade.

## Compose SLOs

If A depends on B (99.9%):
- A SLO ≤ 99.9%
- Likely 99.5%

(See L19/C02/T03.)

## Innovation Tax

Reliability investment ≠ feature shipping.

Balance:
- < 30% on reliability: insufficient
- 60% on reliability: paranoid

Aim: data-driven balance.

## Embrace Imperfection

Things will break. Plan:
- Detection
- Recovery
- Learning

For: graceful handling.

## Risk-Free Tax

Trying for 100%:
- Slows releases
- Burns out team
- Misses opportunities

## Best Practices

- SLO per service
- EBP enforced
- Risk register
- Game days
- Communicate tradeoffs

## Common Mistakes

- 99.999% for everything
- No EBP (budget ignored)
- No risk register
- Skip postmortems for "minor"

## Quick Refs

```
Cost per 9: 10×
Choose: 99.9% (good), 99.99% (important)
EB: 1 - SLO
Risk: P(A) × P(B) for chain
```

## Interview Prep

**Junior**: "Why don't we just aim for 100% uptime?" — 100% is effectively impossible in distributed systems and each additional nine costs roughly 10x more for diminishing user-perceptible value, so we pick a target that matches the service's business value.

**Mid**: "Why does SRE deliberately embrace risk?" — Because some unreliability is acceptable and the error budget that defines it (1 − SLO) is a resource you spend on faster shipping, risky deploys, and experiments rather than a number to drive to zero.

**Senior**: "How do you decide a service's SLO and defend the tradeoff?" — Tier the service by business impact (payments ~99.99%, internal admin ~99%), confirm the target with actual user tolerance and dependency math, then communicate to product that, e.g., 99.99% costs ~10x more than 99.9% so the extra nine has to earn its budget.

**Staff**: "How do you operationalize risk across an org?" — Maintain a risk register with probability/impact/owner per service, enforce error-budget policies so reliability investment is automatic when budgets burn, validate assumptions with game days and chaos, and target a data-driven reliability-vs-feature split (roughly 30–60% on reliability) rather than chasing risk-free perfection.

## Next Topic

→ [T03 — Eliminating Toil](T03-Eliminating-Toil.md)
