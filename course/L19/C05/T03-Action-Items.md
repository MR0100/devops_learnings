# L19/C05/T03 — Action Items That Stick

## Learning Objectives

- Write actionable items
- Follow through

## Why Action Items Fail

- Vague ("improve testing")
- No owner ("the team")
- No deadline ("soon")
- No priority (all important)
- Not tracked (forgotten)
- Too many (overwhelm)

## SMART

- Specific
- Measurable
- Achievable
- Relevant
- Time-bound

```
Bad: "Improve deploy process"
Good: "Add canary stage to deploy pipeline by Jan 15, owned by Alice"
```

## Owner

Single owner:
- Name in doc
- Accountable
- Can delegate but owns outcome

For: clear.

## Due Date

Realistic:
- High-pri: 2 weeks
- Medium: 1 month
- Long-term: quarter

For: time-bound.

## Priority

- P0: incident-blocking
- P1: must do this quarter
- P2: should do this year

For: focus.

## Track

Tools:
- Jira
- GitHub Issues
- Spreadsheet
- Internal tracker

Per item:
- Status
- Owner
- Due
- Updates

## Review

Weekly / bi-weekly:
- Status check
- Blockers
- Re-prioritize if needed

For: follow-through.

## Action Items Per Postmortem

Sweet spot: 3-7.

Too few: incomplete.
Too many: nothing gets done.

## Types

### Prevent
Fix root cause.

### Detect
Monitor + alert.

### Mitigate
Faster recovery.

### Document
Runbook, lesson.

For: balanced.

## Examples

### Specific Code Fix
"Fix BGP regex to avoid backtracking" — clear scope.

### Process Change
"Require canary for all network config deploys" — change in process.

### Tooling
"Add metric: bgp_parse_duration" — instrument.

### Training
"Add BGP module to network team training" — knowledge.

### Documentation
"Update runbook 'network-outage' with new steps" — material.

## Don't Over-Generalize

Bad: "Improve testing across all services."

Good: "Add integration test for payment API with $0 amounts (covers root cause)."

For: tractable.

## Don't Over-Specific

Bad: "Change line 47 of file X to use list instead of tuple."

(Code change is fine but action item should be PR + reviewed, not specific line.)

## Verification

Each action:
- How verify done?
- Test? Metric? Documentation?

For: confirmed.

## Roll-Up

Per service:
- Action items open / closed
- Trend
- Aging

Identify: persistent issues.

## Aging Action Items

> 3 months open:
- Still relevant?
- Re-prioritize?
- Cancel?

For: don't accumulate stale.

## Manager Role

- Push for follow-through
- Allocate time
- Remove blockers

For: support.

## Top-Down Investment

Action items vs feature work:
- 20% reliability budget?
- Explicit allocation?

For: don't compete unfairly.

## Track Org-Wide

Quarterly review:
- All postmortem actions
- % completed
- Repeated themes
- Systemic issues

For: meta-learning.

## Anti-Patterns

### "Look Into This"
Not actionable.

### "All Teams Should..."
No specific owner.

### "Future Work"
Code for "won't happen."

### Mountain of Items
Each postmortem adds 20. Death by paper.

## Cull

Quarterly:
- Old / irrelevant: close
- Done implicitly: close
- Re-prioritize

For: live list.

## Real Example

Cloudflare postmortems publish action items + follow up later showing completion.

For: industry leadership.

## Internal Tracking

```
Postmortem-2026-01-01:
  AI-001 [Closed] Fix regex
  AI-002 [Open] Add canary - due Jan 15 - Alice
  AI-003 [Open] Update runbook - due Jan 10 - Bob
  AI-004 [Closed] Add metric
```

For: visible status.

## Celebrate Closure

When done:
- Mention in team channel
- Reward (lunch?)
- Carry forward learnings

For: positive reinforcement.

## Best Practices

- SMART action items
- Single owner
- Due date
- Tracked
- Reviewed
- Cull aging

## Common Mistakes

- Vague
- No owner
- No due
- No tracking
- Too many
- Never reviewed

## Quick Refs

```
AI:
- Specific
- Measurable
- Owner: 1 person
- Due: realistic
- Tracked: tool
- Reviewed: regularly

Sweet spot: 3-7 per postmortem
```

## Interview Prep

**Mid**: "Action items."

**Senior**: "Follow-through."

**Staff**: "Postmortem effectiveness."

## Next Topic

→ Move to [L19/C06 — Capacity Planning](../C06/README.md)
