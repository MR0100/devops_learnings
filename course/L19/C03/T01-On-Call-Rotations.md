# L19/C03/T01 — Designing On-Call Rotations

## Learning Objectives

- Design rotations
- Avoid burnout

## On-Call

Engineer responding to alerts:
- Off-hours coverage
- Primary + secondary
- Rotation

## Rotation Patterns

### Weekly
Most common. Primary 1 week, then off.

For: 6+ person team.

### Daily
Smaller windows.

For: small team or high-load.

### Follow-the-Sun
US team → EU team → APAC team. 8 hours each.

For: global teams; no off-hours.

### Project Team
Whoever built it on-call for it.

For: small services.

## Team Size

### 4-Person
Each on-call 1 week / month. Manageable.

### 6-Person
1 week / 6 weeks. Comfortable.

### 8+
Lighter; specialty rotations.

Smaller: too frequent. Bigger: knowledge dilution.

## Follow-the-Sun

Pros:
- No nights for anyone
- 24/7 coverage

Cons:
- Hand-off overhead
- Knowledge silos
- Time zone challenges

## Primary + Secondary

Primary: takes alerts.
Secondary: backup if primary unavailable.

For: redundancy.

## Coverage

- 24/7
- Business hours only (some services)
- Critical only (sleep through non-critical)

For: match severity.

## Holiday Coverage

- Trade shifts
- Volunteer signups
- Pay premium

For: cover.

## Compensation

- Time off (post-on-call)
- Pay differential
- Comp hours
- Just respect (less common)

For: incentivize, fairness.

## Healthy Targets

- < 2 pages / on-call shift (week)
- < 25% of time on-call
- > 8h sleep undisturbed

If violated: invest in noise reduction.

## Burnout Signs

- Pager volume high
- Same alerts repeating
- Skipped postmortems
- Quitting

For: address before exodus.

## Onboarding

New on-call:
- Shadow first
- Run drills
- Read postmortems
- Know runbooks

For: prepared.

## Pre-Shift Check

Going on shift:
- Test pager
- Check on-call doc
- Review recent incidents

For: ready.

## Hand-Off

End-of-shift:
- Open incidents
- Recent context
- Brief incoming

For: continuity.

## Tools

- PagerDuty
- Opsgenie
- VictorOps
- FireHydrant
- incident.io

For: pager + incident.

## Rotation Software

PagerDuty:
- Schedules
- Escalation
- Override

```
Schedule: my-team
  Layer 1: Primary (weekly)
  Layer 2: Secondary (weekly)
  Overrides for vacation
```

## Coverage Gaps

- Vacation
- Sick
- Out

Plan:
- Cover via swap
- Manager fills
- Document

## Multi-Tier

L1: front line.
L2: subject expert.
L3: escalation.

For: complex teams.

## Domain-Specific

- DB on-call
- Frontend on-call
- Network on-call

Specialty rotations.

## Cross-Team Escalation

If issue spans:
- Primary detects
- Escalate to other team
- Both involved

For: handoff to subject matter expert.

## Severity-Based Page

P0: page immediately.
P1: page within X.
P2: ticket; no page.
P3: log.

(See L19/C04.)

For: noise reduction.

## On-Call Roles

### Primary
Active response.

### IC (Incident Commander)
Coordinates large incidents.

### Comms
External updates.

## Healthy On-Call Practices

(See L19/C03/T04.)

## Best Practices

- 6+ person team
- < 2 pages/shift goal
- Compensation
- Hand-off
- Onboarding
- Vacation coverage
- Continuous improvement

## Common Mistakes

- 2-person rotation (burnout)
- No comp
- Noisy alerts
- No hand-off
- Same person ICs all incidents

## Quick Refs

```
Rotation: weekly typical
Team: 6+
Pages: < 2/shift target
Comp: time / money
Tools: PagerDuty, Opsgenie
```

## Interview Prep

**Mid**: "On-call rotation."

**Senior**: "Healthy on-call."

**Staff**: "On-call strategy."

## Next Topic

→ [T02 — PagerDuty / Opsgenie Patterns](T02-PagerDuty-Opsgenie.md)
