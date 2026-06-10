# L19/C05/T01 — Blameless Postmortem Template

## Learning Objectives

- Run blameless postmortem
- Use template

## Postmortem

Document after incident:
- What happened
- Why
- Impact
- Timeline
- Action items

For: learning.

## Blameless

Focus on:
- Systems
- Processes
- Knowledge gaps

Not:
- Individual fault
- "Alice broke it"

For: psychological safety; learning.

## Template

```markdown
# Postmortem: [Incident Title]

## Summary
1-2 paragraphs. Non-technical.

## Impact
- Users affected: X
- Duration: Y minutes
- Revenue loss: $Z (if applicable)
- SLO impact

## Timeline
- 14:30 - First alert
- 14:33 - On-call paged
- 14:35 - Investigation begins
- 14:40 - Cause identified (bad deploy)
- 14:45 - Rollback initiated
- 14:50 - Service recovered
- 14:55 - Verified stable
- 15:00 - Incident closed

## Root Cause
Detailed technical explanation.

## Contributing Factors
- Deploy validation missing
- Monitoring lag
- Runbook outdated

## What Went Well
- Quick detection (3 min from start)
- Smooth rollback
- Good comms

## What Went Wrong
- Validation step missing
- Customer comm late
- Runbook hard to find

## Action Items
| Item | Owner | Priority | Due |
|---|---|---|---|
| Add canary validation | Alice | P0 | Jan 15 |
| Update runbook | Bob | P1 | Jan 10 |
| Faster status page | Carol | P1 | Feb 1 |

## Lessons Learned
- Tech: ...
- Process: ...
- Communication: ...
```

## Writing

### Lead with Impact
What customers saw.

### Detail Timeline
Minute by minute.

### Honest
What broke; what didn't.

### Action Items Concrete
Not "improve testing." Be: "Add canary to deploy pipeline by Jan 15."

## When

For all P0/P1.

For P2: optional, valuable if novel.

Within 5 days.

## Who

- IC writes draft
- Subject experts contribute
- Team reviews
- Org-wide share (eventually)

## Review Meeting

- Walk through
- Identify additional context
- Validate action items
- Closure

## Publish

- Internal wiki
- Per-service
- Org-wide repo

For: learn from each other.

## Blameless Language

Bad: "Alice deployed bad code."
Good: "The deploy process did not catch the bug."

Bad: "Bob took too long to respond."
Good: "The alert lacked context, delaying response."

For: focus on systems.

## Heroes

Don't:
- Celebrate one engineer "saving the day"
- Imply others failed

For: team success.

## Real Failures

Sometimes blameless feels uncomfortable when:
- Someone clearly made bad call
- Process was clear

Still blameless:
- Why was process so easy to bypass?
- Better safeguards?

For: improve system.

## Externalize

Public postmortems:
- Show customers seriousness
- Build trust
- Set industry standard

Examples: Cloudflare, AWS, GitLab.

## Action Item Ownership

Each action:
- Single owner
- Due date
- Reviewable

Track:
- Open
- In progress
- Done

For: follow through.

## Track Action Items

If not done:
- Re-discuss
- Postpone? Risky.
- Insufficient?

For: don't accumulate stale.

## Avoid Blame

Even if engineer made error:
- Why was the system designed so a single mistake caused outage?
- Better testing? Validation? Process?

For: systemic improvement.

## Postmortem Anti-Patterns

### Cover-Up
Skip; pretend didn't happen.

### Punish
Engineer who caused: fired / disciplined.

Result: future incidents hidden.

### No Action
Doc filed; nothing done.

### Long Lists
20 action items; none done.

For: prioritize top 3-5.

## Cultural

Blameless is hard. Requires:
- Trust
- Leadership backing
- No retaliation
- Examples

## Best Practices

- Within 5 days
- Blameless tone
- Action items concrete + owned
- Review meeting
- Publish org-wide
- Track follow-through

## Common Mistakes

- Blame individuals
- Vague action items
- No follow-through
- Skip postmortem
- Buried doc

## Tools

- FireHydrant (templates)
- incident.io (postmortem)
- Confluence (template)
- Google Docs (simple)

## Real Example

Cloudflare BGP incident postmortems:
- Detailed
- Honest
- Public
- Trust-building

## Quick Refs

```
Template:
- Summary
- Impact
- Timeline
- Root Cause
- Contributing Factors
- What Went Well
- What Went Wrong
- Action Items (owned, due)
- Lessons

Blameless:
- Focus on systems
- Avoid individual blame
```

## Interview Prep

**Mid**: "What's blameless postmortem."

**Senior**: "Postmortem template."

**Staff**: "Postmortem culture."

## Next Topic

→ [T02 — Root Cause vs Contributing Factors](T02-Root-Cause.md)
