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

Give each item a single, clearly accountable owner:
- Name in doc
- Accountable
- Can delegate but owns outcome

## Due Date

Set a realistic, time-bound due date:
- High-pri: 2 weeks
- Medium: 1 month
- Long-term: quarter

## Priority

Assign a priority so effort stays focused on what matters most:
- P0: incident-blocking
- P1: must do this quarter
- P2: should do this year

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

Review weekly or bi-weekly to drive follow-through:
- Status check
- Blockers
- Re-prioritize if needed

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

A good postmortem produces a balanced mix of prevent, detect, mitigate, and document items.

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

Keep items tractable rather than sweeping:

Bad: "Improve testing across all services."

Good: "Add integration test for payment API with $0 amounts (covers root cause)."

## Don't Over-Specific

Bad: "Change line 47 of file X to use list instead of tuple."

(Code change is fine but action item should be PR + reviewed, not specific line.)

## Verification

For each action, define how you'll confirm it's actually done:
- How verify done?
- Test? Metric? Documentation?

## Roll-Up

Per service:
- Action items open / closed
- Trend
- Aging

Identify: persistent issues.

## Aging Action Items

When an item has been open over 3 months, revisit it so the list doesn't accumulate stale work:
- Still relevant?
- Re-prioritize?
- Cancel?

## Manager Role

The manager's role is to support delivery:
- Push for follow-through
- Allocate time
- Remove blockers

## Top-Down Investment

Carve out an explicit reliability allocation so action items don't compete unfairly with feature work:
- 20% reliability budget?
- Explicit allocation?

## Track Org-Wide

Track action items org-wide each quarter for meta-learning:
- All postmortem actions
- % completed
- Repeated themes
- Systemic issues

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

Cull quarterly to keep the list live:
- Old / irrelevant: close
- Done implicitly: close
- Re-prioritize

## Real Example

Cloudflare publishes its postmortem action items and follows up later showing completion — a strong example of industry leadership in transparency.

## Internal Tracking

```
Postmortem-2026-01-01:
  AI-001 [Closed] Fix regex
  AI-002 [Open] Add canary - due Jan 15 - Alice
  AI-003 [Open] Update runbook - due Jan 10 - Bob
  AI-004 [Closed] Add metric
```

Tracking each item this way keeps its status visible to everyone.

## Celebrate Closure

Celebrate closure as positive reinforcement when an item is done:
- Mention in team channel
- Reward (lunch?)
- Carry forward learnings

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

**Junior**: "What makes a good postmortem action item?" — It should be SMART — specific, measurable, achievable, relevant, and time-bound — like "Add a canary stage to the deploy pipeline by Jan 15, owned by Alice," not vague guidance like "improve the deploy process."

**Mid**: "Why do action items fail to get done?" — They fail when they're vague, have no single owner or deadline, aren't tracked in a tool, or there are simply too many; the sweet spot is 3–7 well-defined items per postmortem with an owner and due date each.

**Senior**: "How do you ensure follow-through?" — Track every item in a real tracker with status and owner, review weekly or bi-weekly, balance the mix across prevent/detect/mitigate/document, define a verification step for each (test, metric, or doc), and cull aging items so the list stays live rather than accumulating stale work.

**Staff**: "How do you make postmortems actually effective org-wide?" — Carve out an explicit reliability allocation (e.g. ~20%) so action items don't lose to feature work, roll up completion rates and recurring themes quarterly to catch systemic issues, and follow the industry-leadership pattern of publicly committing to and reporting on action items the way Cloudflare does.

## Next Topic

→ Move to [L19/C06 — Capacity Planning](../C06/README.md)
