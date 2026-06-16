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
Most common. Primary 1 week, then off. This pattern works best for a team of 6 or more.

### Daily
Smaller windows. This suits a small team or a high-load service where a full week would be too heavy.

### Follow-the-Sun
US team → EU team → APAC team, 8 hours each. This works for global teams and eliminates off-hours paging entirely.

### Project Team
Whoever built the service is on-call for it. This fits small services where the builders have the deepest context.

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

The primary takes alerts and the secondary is the backup if the primary is unavailable, giving the rotation redundancy.

## Coverage

Match the coverage model to the severity the service warrants:
- 24/7
- Business hours only (some services)
- Critical only (sleep through non-critical)

## Holiday Coverage

Cover holidays through a mix of approaches:
- Trade shifts
- Volunteer signups
- Pay premium

## Compensation

Compensate on-call to incentivize participation and keep it fair:
- Time off (post-on-call)
- Pay differential
- Comp hours
- Just respect (less common)

## Healthy Targets

- < 2 pages / on-call shift (week)
- < 25% of time on-call
- > 8h sleep undisturbed

If violated: invest in noise reduction.

## Burnout Signs

Address these burnout signs before they turn into an exodus:
- Pager volume high
- Same alerts repeating
- Skipped postmortems
- Quitting

## Onboarding

Onboard new on-call engineers so they arrive prepared:
- Shadow first
- Run drills
- Read postmortems
- Know runbooks

## Pre-Shift Check

Before going on shift, make sure you're ready:
- Test pager
- Check on-call doc
- Review recent incidents

## Hand-Off

At end of shift, hand off for continuity:
- Open incidents
- Recent context
- Brief incoming

## Tools

These tools handle paging and incident management:
- PagerDuty
- Opsgenie
- VictorOps
- FireHydrant
- incident.io

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

Complex teams use a multi-tier structure:
L1: front line.
L2: subject expert.
L3: escalation.

## Domain-Specific

- DB on-call
- Frontend on-call
- Network on-call

Specialty rotations.

## Cross-Team Escalation

When an issue spans teams, hand off to the subject matter expert:
- Primary detects
- Escalate to other team
- Both involved

## Severity-Based Page

Page by severity to keep noise down:
P0: page immediately.
P1: page within X.
P2: ticket; no page.
P3: log.

(See L19/C04.)

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

**Junior**: "What is an on-call rotation?" — It's a schedule that assigns a designated engineer (often primary plus secondary) to respond to alerts during a window, rotating so no one carries the pager continuously.

**Mid**: "How do you design a sustainable on-call rotation?" — Aim for a team of 6+ so each person is on-call roughly one week in six, use a primary-plus-secondary structure for redundancy, and pick a pattern (weekly, daily, or follow-the-sun) that matches team size and whether you need to avoid night pages.

**Senior**: "What are the healthy-on-call targets and what do you do when they're breached?" — Keep pages under ~2 per shift, on-call to under ~25% of an engineer's time, and protect undisturbed sleep; when those are breached the response isn't more people but investing in noise reduction — tuning alerts, fixing recurring root causes, and enforcing severity-based paging.

**Staff**: "How do you set on-call strategy across many teams?" — Avoid the 2-person death rotation, standardize compensation (time off or differential) and handoff/onboarding practices, use follow-the-sun only where the handoff overhead is worth eliminating night pages, and treat page volume as a tracked metric that gates whether a service is healthy enough to operate.

## Next Topic

→ [T02 — PagerDuty / Opsgenie Patterns](T02-PagerDuty-Opsgenie.md)
