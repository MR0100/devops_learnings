# L19/C01/T01 — The Google SRE Book in 90 Minutes

## Learning Objectives

- Grasp SRE philosophy
- Apply key principles

## Origins

Google SRE, 2003+ (Ben Treynor):
- Solve ops as software problem
- Engineers do ops with 50% time
- Apply software discipline to reliability

## Books

1. "Site Reliability Engineering" (2016)
2. "The Site Reliability Workbook" (2018)
3. "Building Secure & Reliable Systems" (2020)

## Key Concepts

### Service Level Objectives
Defined reliability targets.

### Error Budgets
Allowed unreliability.

### Toil Reduction
Automate repetitive work.

### Blameless Postmortems
Learn without blame.

### Capacity Planning
Forecast + provision.

### Distributed Systems
Design for failure.

## SRE vs DevOps

| | DevOps | SRE |
|---|---|---|
| Origin | culture | role + practice |
| Definition | broad | specific |
| Embraces | many tools | reliability engineering |
| At Google | (didn't exist) | invented SRE |

SRE = "concrete implementation of DevOps."

## Principles

### Embrace Risk
100% uptime impossible / wasteful.
- Pick SLO (e.g. 99.9%)
- Spend budget wisely
- Tolerate calculated risk

### Toil
Manual, repetitive, automatable work:
- Cap toil < 50%
- Engineers spend 50% on engineering

### Failure Is Inevitable
- Design for failure
- Test failure (chaos)
- Recover quickly

## Service Levels

### SLI (Indicator)
Measure quality.

### SLO (Objective)
Target.

### SLA (Agreement)
Customer-facing contract.

## Error Budget

```
SLO = 99.9%
Budget = 0.1% = 43 min/month
```

Use budget for:
- Risky deploys
- New features
- Experiments

When exhausted:
- Freeze risky changes
- Focus on reliability

## Toil

Definition:
- Manual
- Repetitive
- Automatable
- Tactical (not strategic)
- No enduring value
- Scales with service size

If all yes: it's toil. Automate.

## Toil Budget

< 50% of SRE time on toil.

If > 50%: at risk of burnout, no improvement.

Track. Reduce systematically.

## Engineering Work

Other 50%:
- Build automation
- Improve services
- Design
- Tools
- Capacity planning

For: meaningful work.

## Hierarchy of Reliability

```
1. Monitoring (must)
2. Incident response
3. Postmortem & root cause
4. Testing
5. Capacity planning
6. Development
7. Product (UX)
```

Foundation up.

Can't optimize step 5 if step 1 broken.

## Monitoring

- Metrics
- Logs
- Traces
- Synthetic checks

(See L17, L18.)

## Incident Response

Roles:
- IC (Incident Commander)
- Ops Lead
- Comms Lead
- Subject Experts

(See L19/C04.)

## Postmortems

Blameless:
- Focus on system + processes
- Not individuals
- Action items
- Shared

(See L19/C05.)

## Capacity Planning

- Forecast demand
- Account for growth
- Headroom for spikes
- Resource autoscale

(See L19/C06.)

## SRE Team Models

### Embedded
SRE in each product team.

### Centralized
SRE platform team supports many.

### Hybrid
Both.

For: scales differ.

## SLO-Driven

Everything tied to SLO:
- Alerts: burn rate
- Capacity: meet demand at SLO
- Postmortems: SLO impact
- Roadmap: budget direction

For: aligned.

## Continuous Improvement

- Postmortems → action items
- Toil tracking → automation
- SLO review → adjust
- Game days → resilience

## On-Call

- Sustainable rotation
- < 25% of time on-call
- Compensated (time off, $)
- Tooling support

(See L19/C03.)

## Production Readiness

Before launch:
- Monitoring
- Runbooks
- Capacity
- Reliability
- Security

Checklist enforced.

(See L19/C08.)

## Chaos Engineering

Deliberately break things:
- Find weaknesses
- Improve resilience
- Build muscle

(See L19/C07; L25.)

## Measuring SRE Success

- SLO compliance
- Toil %
- Incident rate
- MTTR
- DORA metrics

For: track.

## Culture

- Blameless
- Data-driven
- Continuous improvement
- Collaboration
- Calculated risk

For: thrives if cultivated.

## Best Practices

- Start with SLO
- Define toil; measure
- Postmortem every incident
- Blameless culture
- Automate
- Test failure modes

## Common Mistakes

- SLO too tight (eng can't meet)
- No EBP (budget meaningless)
- Blame culture (no learning)
- All toil (burnout)
- Skip postmortem

## Quick Refs

```
SLI:  measure
SLO:  target
SLA:  contract
EB:   1 - SLO

Toil: < 50% time
Eng:  > 50% time

Hierarchy:
  Monitor → Incident → Postmortem → Test → Capacity → Dev → UX
```

## Interview Prep

**Junior**: "What's SRE."

**Mid**: "SRE principles."

**Senior**: "SLO + EB."

**Staff**: "SRE org design."

## Next Topic

→ [T02 — Embracing Risk](T02-Embracing-Risk.md)
