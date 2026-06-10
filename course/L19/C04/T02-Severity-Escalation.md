# L19/C04/T02 — Severity Levels & Escalation

## Learning Objectives

- Define severities
- Set escalation paths

## Severity

How impactful:
- P0 / SEV1: critical
- P1 / SEV2: high
- P2 / SEV3: medium
- P3 / SEV4: low

## P0 / SEV1

Examples:
- Complete outage
- Data loss
- Security breach
- Customer trust impact

Response:
- Page immediately
- IC assigned
- All hands
- Comms updated

## P1 / SEV2

Examples:
- Significant degradation
- Some customers affected
- Important feature broken

Response:
- Page (maybe)
- Address ASAP
- Comms internal

## P2 / SEV3

Examples:
- Limited impact
- Workaround exists
- Quality issue

Response:
- Ticket
- Address within day
- No urgency

## P3 / SEV4

Examples:
- Cosmetic
- Edge case
- Future improvement

Response:
- Backlog
- Triage

## Definition Per Org

Customize:
- "Affects > 50% users → P0"
- "Affects single tenant → P2"

For: clarity.

## Escalation Time

```
P0: ack < 5 min; recover < 1 hr
P1: ack < 15 min; recover < 8 hr
P2: < 24 hr
P3: < 1 week
```

## Auto-Escalate

If not acked:
```
Primary: 5 min
Secondary: 10 min
Manager: 15 min
VP: 30 min
CEO: 1 hr (for P0)
```

## Roles by Severity

### P0
- IC
- Multiple subject experts
- Comms lead
- Executive sponsor

### P1
- IC (maybe)
- Subject expert
- Manager aware

### P2/P3
- Engineer
- Possibly informal

## Decision Tree

```
Outage of critical service?
  YES → P0
Significant degradation?
  YES → P1
Workaround exists?
  YES → P2
```

For: rapid triage.

## Severity Drift

After initial:
- Upgrade if worse
- Downgrade if mitigation works

For: dynamic.

## Misclassification

P0 declared too easily:
- Burnout
- Compromised trust

P0 declared too late:
- Late response
- Customer harm

For: balanced criteria.

## Comm Cadence

### P0
- Initial: 5 min
- Updates: every 30 min
- Resolution: + final

### P1
- Initial: 30 min
- Hourly updates

### P2
- Daily

## Stakeholders

### Internal
- Engineering
- Product
- Customer success
- Leadership

### External
- Customers
- Public (Twitter, status page)
- Press (if major)

## Status Page

Tools:
- Statuspage.io
- StatusGator
- BetterStack

Update reflecting severity.

## Communication Templates

```
Subject: [P0] Service X experiencing degradation

We are aware of an issue affecting Service X. 
Engineers are investigating.

Affected: [details]
Workaround: [if any]
Next update: [time]
```

For: speed under pressure.

## Postmortem Required

P0/P1: postmortem mandatory.
P2: maybe.
P3: optional.

## Severity Examples

### P0
- Payment processing down
- All users locked out
- Data corruption
- Public CVE exploit

### P1
- Slow checkout (5x latency)
- Login broken for some users
- Major feature broken

### P2
- Sporadic 500s
- Slow analytics dashboard
- Minor UI issue

### P3
- Typo
- Cosmetic glitch
- Edge case rare

## Best Practices

- Document severities
- Train on triage
- Auto-escalation
- Multiple comms channels
- Postmortem mandates
- Quarterly review of incidents by severity

## Common Mistakes

- Inflate severity (cry wolf)
- Slow escalation
- No clear criteria
- Skip P0 comms
- No drill

## Escalation Outside Engineering

For P0:
- Legal (data breach)
- PR (public outage)
- Sales (contract impact)
- Finance (cost)

Notify.

## Quick Refs

```
P0: outage; page; all hands
P1: significant; page; sub
P2: limited; ticket
P3: backlog
```

## Interview Prep

**Mid**: "Severity levels."

**Senior**: "Escalation paths."

**Staff**: "Incident triage."

## Next Topic

→ [T03 — Communication During Incidents](T03-Incident-Comms.md)
