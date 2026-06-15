# L19/C07/T03 — Game Days

## Learning Objectives

- Run game days
- Build muscle

## Game Day

Scheduled chaos exercise:
- Team responds
- Inject failure
- Validate runbooks
- Build skill

For: real-world prep.

## Format

```
1. Pre-brief (1 hr)
   - Hypothesis
   - Scope
   - Roles
2. Inject failure
3. Team responds (observe; don't help)
4. Recover
5. Debrief (1 hr)
   - What went well
   - What missing
   - Action items
```

Total: 3-4 hours.

## Hypothesis Examples

- "Team can detect DB outage in < 5 min."
- "Customer impact stays < SLO during AZ failure."
- "Recovery from full region down < 30 min."

## Scope

- One service
- Multi-service
- Cross-team
- Full infra

For: incremental.

## Roles

### Chaos Master
Injects + observes.

### Responders
Real on-call experience.

### Observers
Take notes; learn.

## Prep

- Schedule weeks in advance
- Pre-brief
- Tools ready
- Customer comms drafted

## Live Chaos

```
Time 0: Inject DB latency
Time 1: Alert fires (3 min later)
Time 4: On-call paged
Time 6: Investigates
Time 10: Identifies + acts
Time 15: Mitigation
Time 20: Recovery
```

Track timeline.

## Don't Help

Chaos master observes; doesn't suggest fixes.

Team gets real practice.

## Stop Conditions

- Real customer impact
- Cascading failure
- 1 hr+ unresolved

For: bound damage.

## Debrief

```
What went well?
- Detection time
- Comms

What didn't?
- Runbook outdated
- No recent training
- Tool gap

Action items:
- Update runbook by X (Alice)
- Quarterly training (Bob)
```

For: postmortem-style.

## Examples

### DB Failover
"Promote replica when primary dies."

Inject: kill primary.
Observe: failover time, lag.

### Region Failure
"Multi-region serves traffic if one down."

Inject: drop region traffic.
Observe: traffic shift, SLO held.

### Deploy Bug
"Rollback works on a bug deploy."

Inject: deploy buggy version.
Observe: detection, rollback.

### Slow Service
"Circuit breaker prevents cascade."

Inject: slow upstream.
Observe: circuit breaker triggers.

## Frequency

- Quarterly per service
- Monthly for org-wide
- More for new

For: keep skill sharp.

## Hierarchy

### Tabletop
Discussion only; no real chaos.

### Walkthrough
Verify steps; minor chaos.

### Live
Real injection.

For: maturity progression.

## Communication

Pre:
- Calendar invite
- Customer success aware
- Status page note (sometimes)

During:
- War room
- Slack channel

Post:
- Debrief
- Doc

## Common Outcomes

### Runbook Outdated
Doc says X; reality Y.

Fix doc.

### Missing Alert
Issue not detected.

Add alert.

### Tool Gap
Couldn't query.

Build tool.

### Knowledge Gap
Team unfamiliar.

Training.

## Customer Comm

For some chaos:
- Maintenance window
- Status note

For most:
- Internal only
- Customers don't notice

## Real Examples

### AWS GameDay
Public training: solve unknown system.

### Netflix
Continuous chaos (Chaos Monkey).
Plus periodic large game days.

### Google DiRT
Disaster Recovery Testing; org-wide.

## Resistance

Team:
- "We're too busy"
- "Tests are enough"

Counter:
- Tests don't find unknowns
- Real practice = confidence

## Investment

Game day:
- Hours of team time
- Prep + run + debrief

ROI:
- Find issues before real outage
- Build muscle
- Lower MTTR

For: pays off.

## Org Maturity

### Beginner
Tabletop. No chaos.

### Intermediate
Lower env chaos.

### Advanced
Prod chaos.

### Mastery
Continuous + scheduled.

## Best Practices

- Quarterly
- Hypothesis-driven
- Real on-call responds
- Debrief seriously
- Track action items

## Common Mistakes

- One-off (no muscle)
- Skip debrief
- Help instead of observe
- No follow-up

## Quick Refs

```
Pre-brief → Inject → Respond → Recover → Debrief
Hypothesis-driven
Quarterly minimum
Track action items
```

## Interview Prep

**Junior**: "What is a game day?" — A scheduled exercise where the team responds to an injected failure to validate runbooks and build real incident-response skill, with a pre-brief, the injection, the response, recovery, and a debrief.

**Mid**: "How do you structure a game day?" — Pre-brief the hypothesis, scope, and roles (chaos master, responders, observers); inject the failure while the chaos master observes without helping so responders get real practice; then debrief postmortem-style on what went well, what was missing, and owned action items.

**Senior**: "What makes a game day actually valuable, and why not just rely on tests?" — Set a concrete hypothesis (e.g. "team detects a DB outage in under 5 minutes"), define stop conditions to bound damage, and let real on-call respond — because tests only cover known scenarios while game days surface unknown unknowns like outdated runbooks, missing alerts, and tooling or knowledge gaps.

**Staff**: "How do game days fit into org chaos maturity?" — Progress from tabletop discussions to walkthroughs to live injections, run them at least quarterly per service (monthly org-wide) so muscle memory stays sharp, follow real-world models like Google DiRT and AWS GameDay, and counter "we're too busy" resistance by showing the ROI: issues found before a real outage and a lower MTTR.

## Next Topic

→ Move to [L19/C08 — Production Readiness](../C08/README.md)
