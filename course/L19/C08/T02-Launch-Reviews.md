# L19/C08/T02 — Launch Reviews

## Learning Objectives

- Run launch review
- Coordinate launches

## Launch Review

Meeting before launch:
- Review PRR
- Risks discussed
- Sign-off

## Attendees

- Service owner
- SRE
- Security
- Product
- Possibly leadership

## Agenda

1. Service overview
2. Architecture
3. PRR walkthrough
4. Risks + mitigations
5. Launch plan
6. Rollback plan
7. On-call plan
8. Sign-offs

## Pre-Review

Materials provided:
- PRR checklist
- Architecture doc
- Runbook
- Load test results
- Security review

For: efficient meeting.

## Risk Register

```
Risk: DB might OOM at peak
Mitigation: vertical scale before launch + monitor
Owner: Alice
```

For: explicit.

## Launch Plan

```
Day 0: Deploy to staging
Day 1: Internal testing
Day 7: 1% canary
Day 14: 10% canary
Day 21: 50%
Day 28: 100%
```

Phased.

## Rollback Plan

```
If error rate > 1%:
  - Auto-rollback (Argo Rollouts)
  - Investigate
  - Postmortem

If unable to rollback:
  - Forward fix
  - Feature flag off
```

Tested in non-prod.

## Capacity Sign-Off

- Forecast vs provisioned
- Headroom verified
- Load test passed

## Security Sign-Off

- Pen test passed
- IAM least priv
- Data classification
- Compliance check

## On-Call Sign-Off

- Team assigned
- Trained on service
- Runbooks ready
- Pager configured

## Soft Launch

Internal users:
- Find bugs
- Test under realistic load
- Feedback

Before external.

## Gradual Rollout

- Per-region
- Per-tenant
- Per-cohort

For: limit blast.

## Communication

Pre-launch:
- Stakeholders informed
- Status page note
- Customer success briefed

## Post-Launch

Day 1-7:
- Daily metrics review
- Bug bash
- Performance tuning

Day 8-30:
- Weekly reviews
- SLO tracking
- Postmortem if issue

## Outcomes

Launch review:
- Go (proceed)
- Conditional go (with action items)
- No-go (postpone)

For: gate.

## Conditional Go

```
Approved with conditions:
- Pen test before public launch
- Multi-AZ before traffic spike
- Runbook updated by Day 10
```

Track.

## No-Go

Reasons:
- Critical PRR gap
- Architecture concern
- Capacity unconfirmed

For: better delay than outage.

## Anti-Patterns

### Skip Review
"Just launch."

Result: incident.

### Rubber Stamp
Review without verifying.

### One Person Approves
No cross-functional perspective.

### No Documentation
Decisions lost.

## Templates

```markdown
## Launch Review: [Service]

### Date
### Attendees

### Service
- Description
- Owner
- Architecture

### PRR Status
- All required items: yes/no
- Gaps: ...

### Risks
- Risk 1: mitigation
- Risk 2: mitigation

### Launch Plan
- Phase 1
- Phase 2

### Rollback Plan

### On-Call Plan

### Sign-Offs
- Owner: ___
- SRE: ___
- Security: ___
- Product: ___

### Decision
- Go / Conditional / No-Go

### Action Items
- ...
```

## Real Examples

### Big Launch (Public)
Full review; weeks ahead; comms.

### Internal Tool
Light review; smaller impact.

### Feature Flag Launch
Maybe lighter; flag = safety.

## Best Practices

- Mandatory for risky
- Cross-functional
- Documented
- Conditional OK
- Post-launch review
- Iterate process

## Common Mistakes

- Skip
- Last minute (no fix time)
- Ignore concerns
- No follow-up

## Post-Launch Review

After 30 days:
- Did it go well?
- Issues?
- Lessons?

For: improve process.

## Quick Refs

```
Pre-review: materials ready
Agenda:
  - Overview
  - PRR walk
  - Risks
  - Launch plan
  - Rollback
  - On-call
  - Sign-offs

Decision: Go / Conditional / No-Go
```

## Interview Prep

**Mid**: "Launch review."

**Senior**: "Launch coordination."

**Staff**: "Org-wide launch process."

## Next Topic

→ Move to [L19/C09](../C09/README.md) or next major topic
