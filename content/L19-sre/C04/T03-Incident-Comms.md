# L19/C04/T03 — Communication During Incidents

## Learning Objectives

- Communicate well in incidents
- Manage stakeholders

## Why

Bad comms:
- Trust erodes
- Customers angry
- Internal confusion
- Worse decisions

Good comms:
- Trust maintained
- Coordination effective
- Customers informed

## Channels

### Internal
- Slack #incidents channel
- Email
- Status meetings
- IC bridge (call)

### External
- Status page
- Customer email
- Social media
- Account managers

## Slack Channel

Per-incident:
```
#incident-2026-01-01-payments-outage
```

For: focused; archive.

Or single #incidents channel:
- Topic
- Threading
- Bots

## Bot Integration

```
/incident open severity=P0 description="Payments outage"
```

Bot:
- Creates channel
- Pages IC
- Updates status page

For: speed.

## Cadence

### P0
Updates every 30 min.

### P1
Every hour.

### P2
Daily.

## Audience

- Engineering: technical
- Product / leadership: business impact
- Customers: simplified

Tailor.

## Template

```
Subject: [INCIDENT] Service X experiencing issues

Status: Investigating
Time: 14:30 UTC
Impact: Some users unable to checkout

Engineering team is investigating. 
Next update at 15:00 UTC.

[link to status page]
```

## Status Page

Tools:
- Statuspage.io (Atlassian)
- StatusGator
- Better Stack
- Self-hosted (Cachet)

Update during.

States:
- Investigating
- Identified
- Monitoring
- Resolved

## Wording

Avoid:
- "Issue" (vague)
- "Outage" (loaded)
- "Working on it" (no detail)

Better:
- "Experiencing degraded performance"
- "Some users unable to..."
- "Investigating; expect update by..."

## Empathy

```
"We understand this is impacting your work. 
We are working as fast as we can. 
Updates: [link]"
```

Acknowledge user pain.

## Detail Level

Internal: full detail.
External: high-level + impact.

Not:
- Vulnerability details
- Internal architecture
- Specific engineers

## Customer Comm

Account managers:
- Notified
- Have script
- Can answer questions

For: relationship preservation.

## Press / Social

For widely visible:
- PR team involved
- Twitter / blog
- Single source of truth

## Avoid Speculation

Don't:
- "It's probably the database"
- "Will be 5 minutes"

Until confirmed.

Better:
- "Investigating"
- "Working on mitigation"

## Update Cadence

Even if no news:
"Still investigating; next update in 30 min."

For: keep stakeholders informed.

## Post-Incident

After resolution:
- Final update
- Postmortem link (when ready)
- Apology
- Action items summary

For: closure.

## Internal Comms

```
- Engineering channel: technical
- Leadership: business impact + ETA
- Customer success: customer-facing summary
- Legal: if data
```

## Multi-Region

Comms across teams:
- IC bridge
- Slack
- Live status doc

For: coordination.

## Tooling

- FireHydrant
- incident.io
- PagerDuty Operations Console
- Atlassian Jira Ops

For: orchestrate comms.

## Live Doc

Google Doc / Confluence:
- Timeline
- Decisions
- Action items
- Status

Updated live.

For: single source.

## Best Practices

- Channels clear
- Cadence respected
- Tailored to audience
- Empathic
- Honest
- Updates even if no news
- Post-incident closure

## Common Mistakes

- Speculation (wrong)
- No empathy
- Silence
- Same message to all
- No status page
- No postmortem link

## Drills

Practice comms:
- Mock outage
- Practice updates
- Review wording

For: ready.

## Customer Trust

After incident:
- Show what changed
- Postmortem (public if appropriate)
- Demonstrate learning

For: rebuild trust.

## Quick Refs

```
Channels: Slack, status page, email, account managers
Cadence: every 30 min (P0)
Template: Time + Status + Impact + Next update
Tailored: per audience
```

## Interview Prep

**Junior**: "Why does communication matter during an incident?" — Good comms maintain trust and coordinate the response, while silence or confusion erodes customer trust and leads to worse decisions; the goal is to keep both internal teams and customers informed.

**Mid**: "What's a good update cadence and template?" — For a P0, send updates roughly every 30 minutes even when there's no news ("still investigating, next update in 30 min"), and use a template covering time, status, impact, and the next update time so people aren't left guessing.

**Senior**: "How should a status page be worded and run?" — Move it through clear states (Investigating → Identified → Monitoring → Resolved), use precise non-loaded language like "experiencing degraded performance" rather than vague "issue" or alarming "outage," show empathy, and never speculate on cause or ETA before it's confirmed.

**Staff**: "How do you design a customer-comms strategy across audiences?" — Tailor detail by audience — full technical depth internally, business impact for leadership, simplified high-level messaging externally without exposing vulnerabilities or architecture — equip account managers and PR with scripts, and close the loop after resolution with a final update, apology, and (when appropriate) a public postmortem to rebuild trust.

## Next Topic

→ [T04 — ChatOps (Slack, Teams)](T04-ChatOps.md)
