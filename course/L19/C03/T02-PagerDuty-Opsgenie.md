# L19/C03/T02 — PagerDuty / Opsgenie Patterns

## Learning Objectives

- Configure pager systems
- Apply escalation

## Pager Systems

- PagerDuty (most popular)
- Opsgenie (Atlassian)
- VictorOps (Splunk)
- xMatters
- Custom

## Concepts

- Service
- Escalation Policy
- Schedule
- Team
- Incident
- Override

## Service

In PagerDuty:
- Per microservice
- Or per category

Each service has:
- Integration (incoming alerts)
- Escalation policy
- Acknowledgment timeouts

## Integration

Inbound alerts:
- Webhook (e.g. from Alertmanager)
- Email
- Prometheus
- Datadog
- Many

```yaml
# Alertmanager
receivers:
  - name: pagerduty
    pagerduty_configs:
      - service_key: INTEGRATION_KEY
```

## Escalation Policy

```
Level 1: Primary (5 min ack)
Level 2: Secondary (10 min)
Level 3: Manager (15 min)
Level 4: Director (30 min)
```

If not acked, escalate.

For: ensure response.

## Schedules

```
Schedule: my-team
  Layer 1: weekly rotation [A, B, C, D]
  Overrides:
    - Alice: 2026-01-01 to 2026-01-07 (Bob covers)
```

## Override

For: vacation, sick, swap.

```
PagerDuty UI / API
```

## Stakeholders

Non-on-call subscribed:
- Email on incident
- Read-only

For: visibility without page.

## Audit

PagerDuty:
- Incident timeline
- Who paged
- Ack time
- Resolution time

For: postmortem data.

## Mobile App

Critical for response.
- Push notifications
- Acknowledge
- Comment

## Slack Integration

Bot in channel:
- Alert posted
- React to ack
- Comment to incident

For: ChatOps.

## Severity-Based

```
P1 (critical): page
P2 (warning): email + ticket
P3 (info): email only
```

Different channels.

## Auto-Resolution

If alert resolves before ack:
- Auto-close incident
- No-page after window

For: short transient.

## Snooze

For: low-severity if can wait.

```bash
pd incident snooze ID --duration 1h
```

## Maintenance Windows

```
Sun 02:00-04:00: weekly maintenance
```

Suppress alerts during.

## Routing

Alert content → which team:
```yaml
service: payments → payments team
service: search → search team
```

In Alertmanager:
```yaml
routes:
  - matchers: [team=payments]
    receiver: payments-pagerduty
```

## Auto-Triage

Some platforms (FireHydrant):
- Group related alerts
- Suggest cause
- Pull context

For: faster diagnosis.

## Cost

PagerDuty:
- Per-user/month
- Tiers (basic, pro, enterprise)

Opsgenie:
- Similar
- Atlassian ecosystem

For: budget consider users count.

## Alternatives

Free:
- Telegram bot (DIY)
- Discord webhook
- SMS gateway

For: small teams.

## PagerDuty API

```bash
curl -X POST -H "Authorization: Token..." \
  https://api.pagerduty.com/incidents \
  -d '...'
```

For: automation.

## Webhook Out

Send incident events to:
- Slack
- Custom systems
- BI tools

For: integration.

## Incident Templates

Pre-defined incident types:
- Quick create
- Routing
- Owner

## Postmortem Integration

PagerDuty → postmortem doc auto-generated.

For: streamline.

## Best Practices

- Service per microservice
- Escalation policy strict
- Schedule clarity
- Audit logs reviewed
- Mobile app required
- Stakeholders subscribed

## Common Mistakes

- One service for all
- No escalation
- Schedule gaps
- No audit (postmortem suffers)
- Static creds

## Quick Refs

```
Service:        what to page
Escalation:     who to page next
Schedule:       when each engineer
Override:       exceptions
Integration:    inbound alert source
Auto-resolve:   close if alert clears
```

## Interview Prep

**Mid**: "Pager system."

**Senior**: "Escalation design."

**Staff**: "Incident routing."

## Next Topic

→ [T03 — Runbooks](T03-Runbooks.md)
