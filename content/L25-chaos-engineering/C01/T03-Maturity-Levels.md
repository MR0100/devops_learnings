# L25/C01/T03 — Chaos Maturity Levels

## Learning Objectives

- Assess maturity
- Plan growth

## Levels

### L1: Ad-hoc
- Manual
- Lower env
- No automation

### L2: Scheduled
- Cron jobs
- Lower envs
- Some metrics

### L3: Production (Limited)
- Production chaos
- Small scope
- Controlled

### L4: Continuous
- Many experiments
- Production
- Automated

### L5: Org-Wide
- Standard practice
- All teams
- Culture

## L1 → L2

- Pick tool (Chaos Mesh, Litmus)
- Define experiments
- Schedule

## L2 → L3

- Build observability
- Define steady state
- Limit blast
- Run in prod (small)

## L3 → L4

- Automate
- Continuous
- Multiple experiments
- Multiple teams

## L4 → L5

- Org-wide policy
- Mandatory PRR
- Game days regular

## Assessment

For your org:
- Observability mature?
- Postmortems blameless?
- Team capacity?
- Culture (blameless)?

## Prerequisites

Before chaos:
- Monitoring solid
- Alerts configured
- Runbooks ready
- Rollback fast

If not: don't start.

## Investment

L1 → L4: years.

Per team:
- Tool setup
- Hypothesis defined
- Game days
- Observability

## Real Examples

### Netflix
L5 (creators).

### Many enterprises
L2-L3.

### Startups
L1.

## Culture

L5 requires:
- Psychological safety
- Postmortems valued
- Learning culture

## Tooling Per Level

| | L1 | L2 | L3+ |
|---|---|---|---|
| Tool | kubectl delete | Chaos Mesh / Litmus | + Flagger / FIS |
| Schedule | manual | cron | event-driven |
| Scope | one pod | namespace | region |

## Best Practices

- Crawl-walk-run
- Trust over time
- Invest in observability first
- Reach L3 before claiming chaos

## Common Mistakes

- Claim L5 at L1 (marketing)
- Skip prerequisites
- No culture investment

## Quick Refs

```
L1: Ad-hoc
L2: Scheduled
L3: Production limited
L4: Continuous
L5: Org-wide standard

Prereqs: observability, alerts, runbooks
```

## Interview Prep

**Mid**: "Chaos levels."

**Senior**: "Assess maturity."

**Staff**: "Org chaos strategy."

## Next Topic

→ Move to [L25/C02 — Tools](../C02/README.md)
