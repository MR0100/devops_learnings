# L19/C04 — Incident Management

## Topics

- **T01 Incident Commander Role** — Single accountable person
- **T02 Severity Levels & Escalation** — How serious + who
- **T03 Communication During Incidents** — Cadence, channels
- **T04 ChatOps** — Slack/Teams as IR tooling

## The Roles

### Incident Commander (IC)
- Single accountable person for incident response
- Coordinates; doesn't necessarily fix
- Makes calls (rollback, escalate, declare resolved)
- Owns communication
- Conducts after-incident debriefs

### Tech Lead / Subject-Matter Expert (SME)
- The deep technical expert for affected system
- Investigates root cause
- Implements mitigation
- Reports to IC

### Communications Lead / Scribe
- Sends customer comms (status page, Twitter)
- Updates internal stakeholders
- Maintains incident timeline document
- Frees IC and SME to focus

### Subject-Matter Experts (per dependency)
- "DB SME", "Network SME", "Auth SME"
- Brought in as needed

Separation matters: one person can't simultaneously coordinate AND debug deeply.

## Severity Levels

```
SEV-1 (Critical)
  - All-hands; CTO/VP notified
  - Customer-visible outage of core function
  - Revenue impact > $X/min
  - Update channel every 15 min
  - Status page: Major Outage

SEV-2 (High)
  - On-call + manager involved
  - Degraded function affecting many customers
  - Update channel every 30 min
  - Status page: Partial Outage

SEV-3 (Medium)
  - On-call handles
  - Limited customer impact
  - Update channel every 1h
  - Status page: optional

SEV-4 (Low)
  - Internal impact only
  - Handled in normal hours
  - No status page
```

Document precise criteria for each — don't let "vibes" decide.

## Escalation

Time-based:
- 5 min no ack → secondary on-call
- 10 min → manager
- 15 min → director / VP

Or symptom-based:
- Outage > 30 min → VP Engineering
- Revenue impact > $X → CFO
- Press attention → PR + Legal

## Communication

### Internal (Slack)
```
#incident-2026-06-09-1200-checkout-down
Pinned: "SEV-1: Checkout API returning 5xx since 12:00 UTC. IC: @alice. Status: Investigating."

[every 15 min]
@alice: "Update: Tracing shows DB connection pool saturated. Mitigation: scaling RDS Proxy. ETA 10 min."
```

### External (Status Page)
- Statuspage.io / Atlassian Statuspage
- Better Status / Cachet
- AWS-hosted custom

Customer message template:
> [Investigating] We're aware of issues with checkout and are investigating.
> [Identified] We've identified the issue as database capacity. We're applying a fix.
> [Monitoring] Fix deployed. Monitoring for recovery.
> [Resolved] All systems normal. Postmortem to follow.

### Cadence
- Every 15 min for SEV-1 (even "no change")
- Silence is worse than "still investigating"
- Promise update times, hit them

## Incident Process

```
1. DETECTION (alert fires; user reports)
   ↓
2. ACKNOWLEDGEMENT (on-call ack within X min)
   ↓
3. ASSESSMENT (severity? scope?)
   ↓
4. INCIDENT DECLARED
   - Open incident channel
   - Assign IC
   - Page additional people if needed
   - Update status page
   ↓
5. INVESTIGATE + MITIGATE (parallel; mitigation first if possible)
   - Rollback if recent deploy
   - Failover if service-level
   - Scale up if capacity
   - Disable feature if business-logic
   ↓
6. SERVICE RESTORED
   - Verify with synthetic checks + dashboards
   - Customer confirmation if possible
   - Status page: monitoring
   ↓
7. INCIDENT RESOLVED
   - Status page: resolved
   - Hand off to engineering for root cause
   ↓
8. POSTMORTEM (next 1-5 business days)
```

## Two-Pizza Rule for IR

The smaller the actively-engaged group, the faster decisions are made.
- IC, 2-3 SMEs, 1 comms lead = ~5 people
- "Sidelined" SMEs in channel, called in if needed
- Avoid 20-person bridges (analysis paralysis)

## ChatOps

Modern incident response is conducted via chat (Slack/Teams).

### Tools
- **PagerDuty + Slack**: rich integration; ack from chat
- **incident.io / FireHydrant / Rootly**: dedicated IR platforms
- **Custom bots**: opsbot conventions per company

### Common Commands
```
/inc declare SEV-2 "checkout API 5xx spike"
/inc role assign IC @alice
/inc role assign SME @bob
/inc update "rollback complete; monitoring"
/inc resolve
```

Result: timeline auto-built; channel archived; postmortem template auto-created.

## Pre-Computed Resources

Before incidents happen:
- Pre-built dashboard per service
- Runbooks linked from alerts
- Phone tree (who to call for what)
- Status page accounts + templates
- Decision trees ("when to declare SEV-1")

## Practice

Game days: simulate incidents. Practice IR. Find gaps.

## Common Mistakes

- **No IC** — multiple people trying to direct
- **Debug-first, mitigate-later** — restore service FIRST
- **Don't ack alerts** — alert just sits
- **Status page silent** — customers angry
- **No timeline** — postmortem is guesswork
- **All-hands paged at SEV-3** — burnout

## Interview Themes

- "Walk me through incident response"
- "IC role — what is and isn't it?"
- "Severity definitions"
- "Mitigate or root cause first?"
- "ChatOps — what it provides"
