# L19/C08/T03 — Quarterly Service Reviews

## Learning Objectives

- Understand why production readiness is ongoing, not a one-time launch gate
- Run a quarterly service review that surfaces reliability, toil, cost, and capacity risks
- Turn review findings into tracked action items with owners

## Why Quarterly Reviews Exist

A Production Readiness Review (PRR) checks a service *before* launch. But services drift: traffic grows, dependencies change, alerts accumulate, toil creeps in. A **quarterly service review** is the recurring health check that catches drift before it becomes an incident.

PRR as a one-time gate is an anti-pattern. Readiness is a property you re-verify on a cadence.

## The Quarterly Questions

Every quarter, for each service, ask:

| Dimension | Question |
|---|---|
| **SLO** | Did we meet our SLO over the quarter? Error budget burn? |
| **Alerts** | What were the top 5 alerts that fired? Were they actionable? |
| **Toil** | How much time went to toil vs engineering? Trend? |
| **Action items** | What's still outstanding from last quarter? |
| **Capacity** | How much headroom is left? When do we hit a wall? |
| **Cost** | What's the cost trend? Any surprises? |
| **Tech debt** | What debt items are now blocking reliability or velocity? |

**Output**: a one-page summary per service. Every gap becomes a tracked action item with an owner and a date.

## What Each Dimension Surfaces

### SLO Compliance

Pull the last quarter's SLO attainment. If you burned the entire error budget, the error-budget policy should already have triggered (e.g. freeze features, prioritize reliability). The review confirms the policy is actually being followed.

### Top 5 Alerts

The alerts that fired most often reveal:

- **Noisy / non-actionable alerts** → tune or delete (alert fatigue kills on-call)
- **Recurring real issues** → a systemic fix is overdue
- **Missing alerts** → an incident happened with no page

### Toil vs Engineering

Google SRE's guidance: cap toil at ~50%. If a service's on-call is spending 70% of their time on manual, repetitive, automatable work, the review makes that visible and forces an investment decision.

### Capacity Headroom

Project current growth forward. "At this rate we exhaust the DB connection pool / node group / quota in 8 weeks" is exactly the finding a quarterly review should produce — while there's still time to act.

### Cost Trend

Tie into FinOps. A service whose cost-per-request is climbing is either inefficient or scaling poorly; both deserve attention before the bill forces it.

## How It Connects to PRR

```
PRR (pre-launch)         → minimum bar to go live
Launch Review (event)    → sign-off for a specific launch
Quarterly Review (ongoing) → re-verify the bar still holds as the service evolves
```

The quarterly review is also where a service that has *degraded* below the PRR bar gets flagged — and where SRE can invoke "can refuse to operate" if a team has let reliability rot.

## Sample Cadence

1. Service owner fills the one-page template a week ahead (data, not prose)
2. 30-minute review with SRE + service team
3. Walk the seven dimensions; identify gaps
4. Each gap → action item (owner + due date) in the tracker
5. Next quarter opens by checking last quarter's action items

## Common Mistakes

- Treating the review as a status meeting with no action items (rubber stamp)
- Reviewing without the dev team in the room (no buy-in, no follow-through)
- Letting action items roll over forever with no accountability
- Only reviewing at launch and never again (the original anti-pattern)
- Filling the page with prose instead of numbers (SLO %, toil hours, cost delta)

## Best Practices

- Keep it to one page and 30 minutes — make it sustainable so it actually recurs
- Lead with data: SLO attainment, alert counts, toil hours, cost trend
- Every gap gets an owner and a date; start each review by auditing the last one's items
- Track toil explicitly so the 50% cap is enforceable, not aspirational
- Use the review to re-confirm the service still meets its PRR bar

## Quick Refs

```
Quarterly review checklist (per service):
[ ] SLO compliance + error-budget burn
[ ] Top 5 alerts (actionable?)
[ ] Toil % vs engineering %
[ ] Outstanding action items from last quarter
[ ] Capacity headroom + runway
[ ] Cost trend
[ ] Tech debt blocking reliability/velocity
→ Output: 1-page summary; gaps → tracked action items
```

## Interview Prep

**Junior**: "What is a quarterly service review?" — A recurring health check of a production service across SLOs, alerts, toil, capacity, and cost.

**Mid**: "Why review quarterly if you already did a PRR?" — PRR is a launch gate; services drift afterward, and the quarterly review catches that drift before it becomes an incident.

**Senior**: "What does a quarterly review surface that day-to-day on-call misses?" — Trends: rising toil, shrinking capacity headroom, climbing cost-per-request, and recurring alerts that signal an overdue systemic fix.

**Staff**: "How do you make quarterly reviews drive real reliability investment instead of becoming a rubber stamp?" — Tie findings to the error-budget policy and a toil cap, require data not prose, give every gap an owner and date, audit last quarter's items first, and back it with SRE's authority to refuse to operate a degraded service.

## Next Topic

→ Move to [L19/C09](../C09/README.md) or next major topic
