# L25/C04/T02 — Running the Exercise

## Learning Objectives

- Run game day
- Stay calm

## Day-Of

```
T-30 min: Kickoff call
T-15:     Roles assigned
T-0:      Inject failure
T-X:      Team responds
T-Y:      Recover
T+30:     Debrief
```

## Roles

### Chaos Master
Inject; observes.

### IC
Coordinates response.

### Responders
Real on-call experience.

### Observers
Notes; learn.

## Observe Don't Help

Chaos master:
- Inject
- Watch
- Don't suggest

Team learns by doing.

## Stop Conditions

- Real customer impact
- 1 hr unresolved
- Cascading failure

Predetermined.

## Recording

Slack channel:
- Timeline
- Decisions
- Notes

For: postmortem.

## Comms

External:
- Status page if needed
- Customers if production

Internal:
- Engineering channel
- War room

## Debrief

After:
- What went well
- What didn't
- Action items
- Lessons

For: improve.

## Best Practices

- Calm energy
- Realistic
- Learn-focused
- Document everything

## Common Mistakes

- Chaos master helps (defeats purpose)
- No stop conditions
- Skip debrief

## Quick Refs

```
Inject → Observe → Recover → Debrief
```

## Interview Prep

**Junior**: "Walk me through the day of a Game Day." — Kickoff and assign roles (T-30), inject the failure (T-0), let the on-call team respond while the facilitator only observes, recover, then debrief (T+30) and capture findings.

**Mid**: "Why does the facilitator observe and not help?" — The Game Day exists to surface the team's real gaps — missing runbooks, slow detection, unclear ownership. If the facilitator jumps in, those gaps stay hidden and the exercise becomes theater that teaches nothing.

**Senior**: "How do you keep a Game Day from turning into a real incident?" — Pre-agreed written stop conditions (real customer impact, an unrelated incident opening, cascading failure, or a time cap), a tested abort/kill switch, a deploy freeze, and a scribe recording the timeline so the facilitator can abort instantly without debate the moment a condition trips.

**Staff**: "How do you run Game Days that produce durable improvement, not just a fun afternoon?" — Treat the run as data collection: a scribe captures a timestamped timeline, observers note confusion and tooling gaps, and the debrief converts those into owned, due-dated action items that gate a +90-day re-run. Standardize the facilitator discipline and comms ("DRILL" labeling) so results are comparable across teams and the org can spot systemic patterns.

## Next Topic

→ [T03 — Capturing Findings](T03-Findings.md)
