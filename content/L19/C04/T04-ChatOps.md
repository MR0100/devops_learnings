# L19/C04/T04 — ChatOps (Slack, Teams)

## Learning Objectives

- Use ChatOps for incidents
- Build bots

## ChatOps

Operations via chat:
- Commands in Slack
- Bot responds
- Audit trail
- Shared context

## Why

- Single source of truth
- Asynchronous coordination
- Audit log
- Tool integration

For: incident management.

## Slack as Hub

```
#incident-2026-01-01
  Bot: Incident opened (P0)
  Alice: I'll IC
  Bot: IC = Alice
  Bob: Pulling logs
  Bob: !runbook payment-down
  Bot: [posts runbook]
  ...
```

For: live coordination.

## Tools

- PagerDuty Operations Console
- FireHydrant
- incident.io
- Stack Overflow Incident Manager
- Custom (Slack bot)

## Commands

```
/incident open severity=P0 description="Payments down"
/incident resolve
/incident assign IC @alice
/incident status investigating
/incident postmortem
```

Bot orchestrates.

## Channel Per Incident

Auto-create:
- #incident-YYYY-MM-DD-short-desc

Topic: status, IC.

For: focused; archive.

## Threading

Sub-discussions in threads:
- Main: status updates
- Thread: investigation chatter

For: organization.

## Status Updates

```
/update status="Engineering investigating; mitigation pending"
```

Bot posts to status page + #incidents-internal.

## Roles

```
/role ic @alice
/role ops @bob
/role comms @carol
```

Bot tracks.

## Page from Chat

```
/page payments-team P0
```

PagerDuty integration.

## Integrations

- Grafana (dashboard links)
- Datadog (metric snapshots)
- Kubernetes (kubectl in chat?)
- GitHub (PR / issue)

Bot brings context.

## Timeline

Auto:
- Bot logs key events
- Reactions create timeline entries
- Postmortem doc auto-generated

```
14:30: Incident opened
14:32: IC assigned (Alice)
14:35: DB issue identified
14:40: Rollback initiated
14:50: Recovery confirmed
15:00: Incident resolved
```

## Voice Bridge

Slack Huddle or Zoom:
- Voice for fast discussion
- Slack for record

For: complex incidents.

## Privacy

Sensitive info (CVE, customer data):
- Don't post in public channels
- Use private channels
- Or DM

## Audit

Slack archives.

For: postmortem.

## Best Practices

- Bot for repeatable
- Roles posted
- Cadence enforced
- Thread for sub-topics
- Auto-page integration
- Postmortem from log

## Common Mistakes

- Private chats (lose history)
- Voice only (no record)
- Manual everything (slow)
- No channel structure

## Bot Maintenance

Like any service:
- Tested
- Monitored
- Updated

## Custom Bot

```python
from slack_sdk import WebClient
import os

client = WebClient(token=os.environ['SLACK_TOKEN'])

@app.command("/incident")
def handle_incident(ack, command, client):
    ack()
    text = command['text']
    # Parse, create channel, page, etc.
```

For: tailored automation.

## Teams Equivalent

Microsoft Teams:
- Adaptive cards
- Bots (Botkit, etc.)
- Similar workflows

## Discord

For some orgs (smaller, gaming):
- Voice + text
- Bots
- Less mature for ops

## Real Examples

Many tech companies:
- Atlassian uses Slack heavily for incidents
- GitHub built their own ChatOps (Hubot origin)
- Spotify: similar

## Cost

Slack:
- Per user/month (paid)
- Free has message limits

For: enterprise.

## Quick Refs

```
/incident open
/incident assign
/incident update
/incident resolve
/runbook NAME
/page TEAM
/role IC @user
```

## Interview Prep

**Junior**: "What is ChatOps?" — ChatOps means running operations through chat commands — a bot in Slack or Teams responds to commands, gives everyone shared context, and produces an automatic audit trail of what happened.

**Mid**: "Why is ChatOps well suited to incident response?" — It creates a single source of truth where the timeline, roles, and decisions are all captured in one searchable channel, supports asynchronous coordination across teams, and integrates the tools (paging, dashboards, runbooks) the responders need in one place.

**Senior**: "What chat patterns make an incident channel effective?" — Auto-create a per-incident channel, keep the main thread for status updates while investigation chatter goes in threads, post roles explicitly, pull in context via integrations (Grafana, Datadog, PagerDuty), and have the bot log key events so the postmortem timeline is generated automatically.

**Staff**: "How do you build or choose a ChatOps platform?" — Decide between buying (incident.io, FireHydrant, PagerDuty) or building a custom Slack bot, standardize a command grammar (/incident open/assign/update/resolve, /page, /runbook), treat the bot like any production service that's tested and monitored, and enforce privacy rules so sensitive data (CVEs, customer info) never lands in public channels.

## Next Topic

→ Move to [L19/C05 — Postmortems](../C05/README.md)
