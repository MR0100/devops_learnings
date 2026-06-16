# L25/C04 — Game Days

## Topics

- **T01 Planning a Game Day** — Scope, scenarios, participants
- **T02 Running the Exercise** — IC structure
- **T03 Capturing Findings** — Document, act

## What Game Day Is

A scheduled, full-team chaos exercise. 2-4 hours. Simulate realistic outage and respond.

### Purposes
- Validate runbooks
- Train on-call rotation
- Find unknown gaps
- Build "muscle memory" for incidents
- Foster blameless learning

## Planning

### Choose Scope
- Top-priority service
- A specific failure scenario
- Or end-to-end stack

### Examples
- "Primary DB fails; failover to replica"
- "Entire AZ goes dark"
- "Payment processor returns 500s"
- "Cache cluster unavailable"
- "Config push of bad value"

### Participants
- IC (Incident Commander)
- On-call engineers
- SMEs (DB, Network, App)
- Observer / Scribe
- Optional: PM, product

### Pre-Game
- Brief participants (general scope; not specifics)
- Confirm steady state baseline
- Test abort capability
- Open Slack channel
- Brief broader team (this is a drill; no real incident)
- Notify customer-facing teams (so they don't escalate)

### Hypothesis Document
```
Scenario: Primary RDS in us-east-1 fails

Hypothesis: Multi-AZ failover completes within 60 seconds.
            Error rate stays below 5% for less than 90 seconds.
            On-call is paged; can verify recovery without intervention.

Steady state: error rate 0.05%, p99 200ms, throughput 5K rps

Method:
1. Verify steady state (5 min)
2. Reboot RDS primary with failover (FIS)
3. Observe for 5 min
4. Resolve; verify steady state restored

Abort: error rate > 20% sustained, customer escalations, OR active prod incident
```

## Running

### Roles
- **Facilitator**: triggers chaos; doesn't help with response
- **IC**: leads the team
- **SMEs**: technical investigation
- **Observers**: note timeline, blockers, missed steps
- **Scribe**: timeline, decisions

### Timeline
- 0:00 — Brief, verify steady state
- 0:30 — Facilitator triggers chaos
- 0:30+ — Team responds (no facilitator intervention)
- 1:30 — Resolve OR explicit abort
- 1:30 — Verify recovery
- 2:00 — Initial debrief

### Communicate
- Slack channel labeled "GAME DAY (drill)"
- All updates clearly marked as drill
- No customer comms (it's not real)

### Don't Help
Facilitator must resist helping. The team must figure it out (with their existing knowledge + runbooks).

## Debrief

Within 24 hours.

### What Went Well
- Specific actions that worked
- Tooling that helped
- Communication that was clear

### What Went Wrong
- Confusion moments
- Missing information
- Tooling gaps
- Process gaps

### Lucky / Unlucky
- What worked accidentally
- What didn't go as planned

### Action Items
- Owner + deadline
- Update runbook
- Add observability
- Fix bug discovered
- Improve tool

## Capturing Findings

Document:
- Hypothesis (predicted) vs reality
- Timeline with key decisions
- What was tested
- Gaps identified
- AIs with owners

Share widely: engineering org should learn.

## Sample Game Day Schedule

| Week | Activity |
|---|---|
| -2 | Pick scope, hypothesis, get approvals |
| -1 | Brief participants; verify tooling; prep abort |
| Day 0 | Execute (2-4 hours) |
| +1 | Debrief; document |
| +1 to +30 | Address AIs |
| +90 | Re-test (does the fix work?) |

## Frequency

- Quarterly for high-priority services
- Monthly small-scope exercises
- Yearly massive exercise (full multi-region failure)

## What Makes Game Day Successful

- Realistic but bounded scope
- Clear hypothesis and abort criteria
- Strong facilitator who doesn't help
- Honest debrief without blame
- AIs actually completed
- Follow-up to verify fixes

## Common Mistakes

- Too easy ("we know exactly what will happen")
- Too realistic (real customer impact)
- No abort plan (escalates beyond intent)
- No debrief (no learning captured)
- AIs never completed (Same gap next time)
- Skipping the drill ("too busy") — biggest mistake of all

## Comparing to Real Incidents

Game days simulate. Real incidents teach. Both:
- Use IC structure
- Run blameless
- Generate AIs
- Build skill

Difference: game day is controlled.

## Cultural Notes

Game days reveal that:
- Runbooks are outdated
- Some folks panic; others lead
- Tooling has gaps
- Senior engineers' knowledge isn't shared

All learnable + fixable.

## Interview Themes

- "Plan a Game Day for X"
- "Game Day vs real incident"
- "How do you ensure psychological safety?"
- "Debrief structure"
- "Game Day frequency + cadence"
