# L25/C04/T03 — Capturing Findings

## Learning Objectives

- Document findings
- Act on them

## Findings Per Game Day

```markdown
## Game Day: DB Failover Drill - 2026-01-15

### Hypothesis
"DB primary failure recovered < 5 min."

### Result
Recovered in 12 min. Hypothesis falsified.

### Timeline
14:00 - Inject failure
14:02 - Alert
14:05 - Investigation begins
14:08 - Detected failover trigger missing
14:10 - Manual promotion
14:12 - Recovery complete

### Issues
1. Auto-failover script broken
2. Runbook outdated
3. No alert on promotion failure
4. Replica lag delayed promote

### Action Items
| Action | Owner | Due |
|---|---|---|
| Fix auto-failover script | Alice | Jan 25 |
| Update runbook | Bob | Jan 20 |
| Add alert on promotion fail | Carol | Jan 22 |
| Monitor replica lag tighter | Dave | Jan 30 |

### Lessons
- Test auto-failover before relying
- Runbook drift between drills
- Alerting incomplete

### Next Drill
Re-run after fixes (March)
```

## Track

Tools:
- Jira / GitHub Issues
- Spreadsheet
- Wiki

Per action:
- Status (open / done)
- Owner
- Updates

## Review

Weekly: action items.
Quarterly: trend analysis.

## Org Roll-Up

For multiple teams:
- Common issues?
- Systemic patterns?
- Investment areas?

## Communication

- Engineering channel
- Leadership summary
- Customer-facing if relevant

## Best Practices

- Capture immediately (memory fresh)
- Action items SMART
- Track to closure
- Next drill validates

## Common Mistakes

- Forget action items
- No owner
- No follow-up
- Same issue every quarter

## Quick Refs

```
Capture:
- Timeline
- Issues found
- Action items (owner + due)
- Lessons

Track:
- Status
- Closure
- Re-validate
```

## Interview Prep

**Junior**: "What do you capture from a Game Day?" — A timestamped timeline, the issues found, action items with an owner and due date each, and the lessons learned — written down immediately while memory is fresh.

**Mid**: "The hypothesis was falsified — is the Game Day a failure?" — No, that's the best outcome: a falsified hypothesis (e.g. recovery took 12 min, not the predicted 5) is exactly the signal you ran the drill to get. Failure is finding nothing or not converting findings into owned action items.

**Senior**: "How do you make sure findings actually get fixed?" — Every action item is SMART with a named owner and due date, tracked to closure in the same tracker as normal work (Jira/GitHub), reviewed weekly, and validated by re-running the same drill (+90 days). If the same issue recurs every quarter, the tracking process is broken.

**Staff**: "How do findings drive org-level investment?" — Roll findings up across teams to spot systemic patterns — recurring runbook drift, alerting gaps, repeated failover problems — and turn those into platform-level investments rather than per-team patches. Summarize trends for leadership so resilience gets funded, and use the +90-day re-test as the closure proof, not just a closed ticket.

## Next Topic

→ Move to [L25/C05 — Patterns](../C05/README.md)
