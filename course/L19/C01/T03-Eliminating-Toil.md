# L19/C01/T03 — Eliminating Toil

## Learning Objectives

- Define toil
- Reduce systematically

## Toil

Work that is:
- Manual
- Repetitive
- Automatable
- Tactical (no long-term value)
- No enduring value
- Scales with service

If all yes: toil.

## Not Toil

- Engineering (build automation)
- Research
- Design
- Capacity planning
- Strategy

Different.

## Examples

### Toil
- Manual deploys
- Restart pods
- Disk full → expand
- Cert rotation manually
- Re-run failed job

### Not Toil
- Build deploy automation
- Design capacity model
- Refactor for resilience

## Toil Budget

< 50% of SRE time.

If > 50%: red flag.
- No improvement
- Burnout
- Resentment

## Measure

Track:
- Hours/week on toil
- Per category
- Trend

Tools: time tracking, JIRA tags, weekly survey.

## Reduce Strategies

### Automate
Script the manual.

### Eliminate
Don't do it (deprecate).

### Self-Service
Devs do it themselves with tools.

### Vendor
Use managed service.

For: deliberate reduction.

## Self-Service Examples

- Provision DB: Terraform module
- Add monitor: API
- Restart service: button (not page)

Instead of asking SRE.

## Automation Examples

- Auto-scale (HPA, Karpenter)
- Auto-restart (K8s)
- Auto-rotation (cert-manager)
- Auto-deploy (CI/CD)

## Anti-Toil Patterns

### Runbooks → Code
Runbook says: "Run command X then Y."
Better: script that does both.
Better: automatic on alert.

### Tickets → Self-Service
"File ticket to add monitor."
Better: API for monitor creation.

### Pages → Auto-Heal
Page wakes engineer.
Better: K8s auto-restarts pod.

## Investment

Time to build automation:
- Initial: high
- Ongoing: low

vs Toil:
- Ongoing: high

ROI clear in months.

## Toil Inventory

For each toil task:
- Frequency
- Time per occurrence
- Total time/month
- Automation feasibility
- Priority

For: prioritize.

## Top Toils Common

### Deploy
- Manual: bad
- Automated CI/CD: good

### Patching
- Manual SSH: bad
- AMI rotation: good

### Scaling
- Manual: bad
- Auto-scale: good

### Investigations
- Same root cause repeatedly: bad
- Fix root cause: good

## Difficult Toil

Some toil:
- Hard to automate (legal review)
- Low frequency (annual audit)
- High risk (one-off recovery)

Accept these. Document.

## Toil vs Operational Work

Some ops:
- Strategic (capacity planning)
- Learning (incident response)
- Customer-facing (debug user issue)

Not toil; valuable.

## Cultural

Treat toil as enemy.
Celebrate automation.

For: org-wide.

## Toil Reduction Backlog

Each engineer:
- Identifies toil
- Estimates reduction value
- PRs / projects

Like feature backlog.

## Measurement

Per quarter:
- Toil hours: target trending down
- Automation count: trending up
- Recurring incidents: trending down

For: track progress.

## Tooling Investment

50% engineering time:
- Internal tools
- SRE platform
- Self-service

For: investment compounds.

## When Toil Acceptable

- Solving novel
- Learning
- One-time migration
- Critical recovery

Not most cases.

## Burnout Signal

If team complaints:
- Repetitive interrupts
- "Toil all day"
- Low job satisfaction

Then: toil too high.

## Best Practices

- Track toil
- Cap at 50%
- Toil backlog
- Celebrate automation
- Self-service tools
- Cultural shift

## Common Mistakes

- Don't measure (don't know)
- Always firefight
- No automation investment
- Heroics > automation

## Toil Indicators

- Same alert > 1 time/week → fix
- Same manual task > weekly → automate
- > 50% time on tickets → invest

## Quick Refs

```
Toil:
- Manual
- Repetitive
- Automatable
- Tactical
- No enduring value
- Scales with size

Budget: < 50%
Reduce: automate / eliminate / self-service
```

## Interview Prep

**Mid**: "What's toil."

**Senior**: "Reduce toil."

**Staff**: "Toil strategy."

## Next Topic

→ Move to [L19/C02 — Reliability Math](../C02/README.md)
