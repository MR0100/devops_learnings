# L19/C04/T01 — Incident Commander Role

## Learning Objectives

- Run as IC
- Coordinate large incident

## Incident Commander (IC)

- Coordinates response
- Makes decisions
- Doesn't fix (others do)
- Source of truth

For: large or sustained incidents.

## ICS Origins

Incident Command System (NASA/FEMA).
Google adapted for tech.

## Roles

### IC
Coordinator.

### Ops / Subject Matter Expert
Fixes.

### Comms Lead
External updates.

### Scribe
Notes timeline.

## Small Incidents

One person all roles. OK.

## Large Incidents

Spawn IC + Ops + Comms.

## Activate IC

When:
- Multi-team needed
- > 30 min duration likely
- Customer impact
- Multiple unknowns

IC steps in; clarifies roles.

## IC Responsibilities

- Establish call
- Assign roles
- Track status
- Decide priorities
- Escalate
- Hand off if shift ends

NOT:
- Fix bugs
- Type commands
- Investigate (delegate)

## Call

- Slack channel + voice
- Single source of truth
- Updates posted

## Status Tracking

```
Time: 14:30 - Incident detected
Time: 14:33 - IC assigned (Alice)
Time: 14:40 - Identified cause: bad deploy
Time: 14:45 - Rollback initiated
Time: 14:50 - Service recovered
Time: 15:00 - Postmortem assigned
```

Live updates.

## Roles Assignment

```
IC: Alice
Ops: Bob (backend), Carol (DB)
Comms: Dave
Scribe: Eve
```

Posted in channel.

## Decisions

IC decides:
- Rollback vs forward
- Page more help
- Customer comm timing
- Severity escalation

## Escalation

If IC needs help:
- Page additional engineers
- Notify management
- Engage vendor

## Hand-Off

If shift ends:
- New IC briefed
- Documented status
- Continuity

## Comms

To stakeholders:
- Slack #incidents channel
- Email
- Status page

Frequency:
- Every 30 min initial
- On material change

## Customer Comm

Comms Lead:
- Status page update
- Customer email
- Twitter / blog
- Account managers

Templates ready.

## Tool

FireHydrant, incident.io:
- Auto-channel
- Roles
- Timeline
- Stakeholder updates

For: streamline.

## Drills

Practice:
- Game day
- Tabletop
- Simulated incident

For: prepared.

## Anti-Patterns

### IC Types
IC fixing instead of coordinating.

Bad: gets lost.

### No IC
Chaos; people talk over each other.

### Too Many Cooks
Multiple "deciders."

### Skip Comms
Customers in dark.

## When to Stand Down

After:
- Mitigation
- Verified stable
- Customer informed
- Postmortem assigned

## Pre-IC Skills

- Calm under pressure
- Communication
- Decision-making
- Authority
- Familiarity with systems

For: training.

## Becoming IC

Volunteer:
- Shadow ICs
- Run tabletops
- Take small incidents
- Step up gradually

## Training

- IC course
- Role-play
- Reviews

For: certify.

## On-Call ≠ IC

On-call: respond to page.
IC: coordinate response.

Different role; sometimes same person, sometimes not.

## Best Practices

- Clear IC criteria
- Trained IC pool
- Tooling
- Templates
- Drills
- Post-incident review

## Common Mistakes

- IC also fixing
- No IC (chaos)
- IC overload (escalate)
- Skip comms
- Forget hand-off

## Quick Refs

```
IC: coordinate
Ops: fix
Comms: external
Scribe: notes

Activate when:
- Multi-team
- > 30 min likely
- Customer impact
```

## Interview Prep

**Junior**: "What does an Incident Commander do?" — The IC coordinates the incident response, assigns roles, tracks status, and makes decisions; crucially they don't fix anything themselves — they delegate the hands-on work to Ops/subject experts.

**Mid**: "When do you activate an IC and what roles do you spin up?" — Activate an IC when an incident needs multiple teams, is likely to run beyond ~30 minutes, or has customer impact; the standard roles are IC (coordinate), Ops/SME (fix), Comms (external updates), and Scribe (timeline).

**Senior**: "Walk me through running an incident as IC." — Establish a single source of truth (channel plus voice bridge), assign and post roles, keep a live timeline, drive decisions like rollback-vs-forward, push regular stakeholder updates (~every 30 min), and stand down only after mitigation is verified stable, customers are informed, and a postmortem is assigned.

**Staff**: "How do you scale incident command across an org?" — Borrow the ICS model, maintain a trained IC pool with clear activation criteria so anyone can step in, standardize tooling (auto-channels, timelines, templates) and hand-off procedures for long incidents, and rehearse with game days so the structure holds under real pressure rather than collapsing into chaos.

## Next Topic

→ [T02 — Severity Levels & Escalation](T02-Severity-Escalation.md)
