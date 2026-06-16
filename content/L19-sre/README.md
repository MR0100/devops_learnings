# L19 — Site Reliability Engineering

## Overview

SRE is the discipline that defines senior+ DevOps roles. This lecture goes deep on the Google SRE methodology, customized for any company.

**9 chapters, 29 topics.**

## Chapter Map

### [C01](C01/) — SRE Origins & Philosophy
- T01 The Google SRE Book in 90 Minutes
- T02 Embracing Risk
- T03 Eliminating Toil

### [C02](C02/) — Reliability Math
- T01 Availability (the Nines)
- T02 Failure Modes & MTTR/MTBF
- T03 Composing SLOs Across Services

### [C03](C03/) — On-Call
- T01 Designing On-Call Rotations
- T02 PagerDuty / Opsgenie Patterns
- T03 Runbooks
- T04 Healthy On-Call Practices

### [C04](C04/) — Incident Management
- T01 Incident Commander Role
- T02 Severity Levels & Escalation
- T03 Communication During Incidents
- T04 ChatOps (Slack, Teams)

### [C05](C05/) — Postmortems
- T01 Blameless Postmortem Template
- T02 Root Cause vs Contributing Factors
- T03 Action Items That Stick

### [C06](C06/) — Capacity Planning
- T01 Forecasting Demand
- T02 Load Testing in Anger
- T03 Headroom Management

### [C07](C07/) — Chaos Engineering
- T01 Principles
- T02 Tools (Chaos Mesh, Litmus, Gremlin, AWS FIS)
- T03 Game Days

### [C08](C08/) — Production Readiness
- T01 PRR Checklist
- T02 Launch Reviews
- T03 Quarterly Service Reviews

### [C09](C09/) — SRE Leadership at FAANGM
- T01 SRE Org Structures (Embedded vs Central)
- T02 Influence Without Authority
- T03 The Staff SRE Role

## Availability Math

| Nines | Downtime / year | Downtime / month | Downtime / week |
|---|---|---|---|
| 99% (2 nines) | 3.65 days | 7.2 hours | 1.68 hours |
| 99.9% (3 nines) | 8.76 hours | 43.8 min | 10.1 min |
| 99.95% | 4.38 hours | 21.9 min | 5.0 min |
| 99.99% (4 nines) | 52.6 min | 4.38 min | 1.0 min |
| 99.999% (5 nines) | 5.26 min | 26.3 sec | 6.05 sec |

> Each additional "nine" is exponentially more expensive. Pick targets that match business value.

## SLO Composition

If service A depends on services B (SLO 99.9%) and C (SLO 99.99%):

```
A's max possible availability = 99.9% × 99.99% = 99.89%
```

If A also wants 99.9%, the math doesn't allow it without:
- Caching / circuit breakers
- Failover paths
- Or lowering A's SLO

## On-Call Design

| Rotation | Pros | Cons |
|---|---|---|
| 24/7 single team | Knowledge | Burnout |
| Follow-the-sun (3 regions) | Sleep | Coordination cost |
| Primary + secondary | Backup | More people on-call |
| Weekly | Predictable | Long burnout if active |
| Daily | Shorter | More handoff cost |

**Healthy on-call rules:**
- Cap at 1 week per 5–6 weeks per engineer
- Pages should be < 5/week; > 10 indicates broken systems
- Page only on customer impact (use SLO burn alerts)
- Compensate (cash or time off)
- Track signal/noise ratio

## Incident Response

```
Detect → Page → Acknowledge → Assemble (IC, comms, scribe)
   ↓
Triage (assess scope)
   ↓
Investigate + Mitigate (don't search root cause during fire)
   ↓
Restore service
   ↓
Postmortem (next day or two)
   ↓
Action items
```

### Severity Levels (Sample)
- **SEV-1**: customer-impacting outage, all hands
- **SEV-2**: degraded service, on-call + manager
- **SEV-3**: internal impact, on-call
- **SEV-4**: minor, handled in normal hours

## Blameless Postmortem Template

```
## Summary
One paragraph, no jargon, business-impact framing.

## Impact
• Users affected: 200K (10%)
• Duration: 25 min
• Revenue impact: ~$50K

## Timeline (UTC)
14:00 Deploy of v2.4
14:05 Error rate begins climbing
14:08 Alert fires
14:09 On-call paged
...

## Root Causes & Contributing Factors
1. New config schema not validated in CI
2. Canary signal missed because canary sampled wrong cohort
3. Rollback delayed by lack of automation

## What Went Well
• PagerDuty fired correctly
• ChatOps channel auto-created

## What Went Wrong
• 10 min between alert and mitigation
• No automated rollback

## Where We Got Lucky
• Rollback worked first try

## Action Items
| AI | Owner | Due | Priority |
|---|---|---|---|
| Add CI config schema validation | @alice | June 30 | High |
| Improve canary cohort assignment | @bob | July 15 | High |
| Automate rollback on burn | @carol | Aug 1 | Medium |
```

## Capacity Planning

- Project growth quarterly (with margins for events, marketing)
- Load test at 2× projected peak
- Maintain 30% headroom
- Plan for AZ failure: surviving AZs must hold full traffic
- Plan for region failure if multi-region

## Recommended Reading

- *Site Reliability Engineering* — Google (FREE online; mandatory)
- *The SRE Workbook* — Google (FREE online)
- *Seeking SRE* — David Blank-Edelman
- *Implementing Service Level Objectives* — Alex Hidalgo

## Interview Themes

- "What's the difference between SLI, SLO, and SLA?"
- "Compose SLOs across dependent services"
- "Design an on-call rotation"
- "Walk me through an incident you led"
- "What's an error budget policy?"
- "Toil — define, measure, eliminate"

## Next

→ [L20 — Security & DevSecOps](../L20-security-devsecops/README.md)
