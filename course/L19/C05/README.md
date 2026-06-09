# L19/C05 — Postmortems

## Topics

- **T01 Blameless Postmortem Template** — Standard structure
- **T02 Root Cause vs Contributing Factors** — Multiple causes
- **T03 Action Items That Stick** — Make them happen

## Why Postmortems

After an incident, capture learning. Without postmortems, the same incident repeats.

## Blameless

> Assume operators acted with good intent given the information they had. Look at systems, not individuals.

The reason: psychological safety enables truth. If people fear blame, they hide info → you can't learn → it happens again.

Blameless ≠ accountability-free. Action items still have owners. But we don't blame individuals for system failures.

## Template

```markdown
# Incident: Checkout API 5xx spike — 2026-06-09

## Summary
One paragraph, no jargon, business-impact framing.

Example: At 12:00 UTC, the checkout API began returning 5xx errors at 30%
rate for 25 minutes. 12,000 customer orders failed. Estimated revenue impact
$45,000. Root cause: DB connection pool exhaustion triggered by a config
change deployed at 11:55 UTC. Mitigated by reverting the config at 12:23 UTC.

## Impact
- Users affected: 12,000 checkout attempts (~20% of period)
- Duration: 25 min (12:00 – 12:25 UTC)
- Revenue impact: ~$45,000
- Reputation: 3 customer support tickets, 1 Twitter complaint

## Timeline (UTC)
- 11:55 — Deploy of config v2.4 (PR #1234)
- 12:00 — Error rate begins climbing on /api/checkout
- 12:03 — Alert fires (HighErrorRate)
- 12:04 — On-call @alice acked
- 12:06 — Incident channel opened; @alice IC
- 12:08 — Hypothesis: recent deploy; @bob investigates
- 12:15 — Root cause identified: config v2.4 set max_db_connections=10
         (was 100); pool exhausted under load
- 12:20 — Rollback via ArgoCD initiated
- 12:23 — Rollback complete; error rate drops to baseline
- 12:25 — All metrics back to normal; incident resolved
- 12:30 — Status page updated to "resolved"

## Root Cause
The deploy of config v2.4 reduced `max_db_connections` from 100 to 10 due to
a typo (intended to change a different setting). Under normal load, the pool
saturated within minutes.

## Contributing Factors
1. CI didn't validate max_db_connections is sensible (no range check)
2. Deploy went straight to prod (no staging exposure)
3. Canary stage doesn't include this specific config path
4. Rollback took 8 min (could be < 2 min)
5. Alert fired 3 min after onset (could detect faster)

## What Went Well
- Alert fired (it did, eventually)
- On-call acked quickly (1 min)
- IC structure worked; clear roles
- Rollback succeeded first try
- Status page updated within 30 min

## What Went Wrong
- Bad config reached prod
- 8 min from "rollback decision" to "rollback complete" (target < 2 min)
- 3 min detection latency
- No staging validation of config-only changes

## Where We Got Lucky
- Issue manifested at low-traffic time of day
- Rollback worked first try; sometimes Argo gets stuck
- @alice was at her desk

## Action Items

| # | Action | Owner | Due | Priority |
|---|--------|-------|-----|----------|
| 1 | Add CI validation for config values (range checks) | @alice | June 30 | High |
| 2 | Route config-only deploys through staging first | @bob | July 15 | High |
| 3 | Reduce ArgoCD rollback time to <2 min (pre-warm new manifests) | @carol | Aug 1 | Medium |
| 4 | Tighten alert: detect at p99 latency anomaly | @dan | July 10 | Medium |
| 5 | Add runbook section for "bad config deploy" | @alice | June 20 | Low |

## Follow-Up
- Postmortem doc shared in #eng-all
- AIs tracked in JIRA project INFRA
- Review at next reliability review (June 25)
```

## Run the Postmortem Meeting

Within 5 business days. ~1 hour.

Agenda:
1. (5 min) Read the doc together
2. (10 min) Walk through timeline; correct facts
3. (15 min) Discuss root cause + contributing factors
4. (15 min) Identify action items; assign owners
5. (5 min) Confirm next steps + close

## Root Cause vs Contributing Factors

> Single root cause is usually a fiction. Complex incidents have multiple contributing factors.

Use Five Whys but stop when "we'd have needed to change a system." Multiple Whys often → multiple paths → multiple AIs.

### Examples
- "DB pool exhausted" — why?
- "Config set max_connections=10" — why?
- "Typo in deploy" — why?
- "No CI validation" — root cause for AI #1
- "Bypassed staging" — root cause for AI #2

Each contributing factor gets its own AI.

## Action Items That Stick

### Make Them Concrete
- "Improve testing" → vague, won't happen
- "Add a unit test verifying max_db_connections is in [10, 1000]" → concrete

### Assign Owners
- One person, not a team
- They commit; their manager tracks

### Deadlines
- Within 30 days for high-priority
- Tracked in your normal issue tracker

### Track Until Done
- Stalled AIs are common
- Quarterly review: which AIs from postmortems are still open?

## Anti-Patterns

- **Naming names** in cause section (use blameless framing)
- **Action item is "be more careful"** (not actionable)
- **All AIs assigned to one engineer** (won't get done)
- **No AIs** (incident repeats)
- **Privately discussed; not shared** (others can't learn)
- **Skipping the meeting** (writing the doc isn't the value)

## Templates & Tools

- **Google's SRE template** (free)
- **incident.io / Rootly / FireHydrant** auto-generate templates from incidents
- **Confluence / Notion / Markdown in Git** as storage

## Inviting Broader Audience

Postmortems are learning artifacts. Share:
- Engineering all-hands recap
- Wiki searchable
- Tagged by service / failure mode
- "Hall of fame" of educational incidents

## Interview Themes

- "Walk me through a postmortem you ran"
- "Root cause vs contributing factor"
- "Action items that stick — how?"
- "Blameless — what does it really mean?"
- "Postmortem meeting structure"
