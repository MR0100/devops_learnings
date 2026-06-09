# L19/C03 — On-Call

## Topics

- **T01 Designing On-Call Rotations** — Schedules, sizing
- **T02 PagerDuty / Opsgenie Patterns** — Tooling
- **T03 Runbooks** — What to do when paged
- **T04 Healthy On-Call Practices** — Sustainability

## Rotation Design

### Common Schedules

- **Weekly** — Mon → Mon, common
- **Daily** — Better for short-burst high-pressure roles, worse for sleep
- **Follow-the-sun** — 3 regions cover 24h; each person works business hours

### Sizing
- Need at least **6 on-call rotators** for sustainable weekly rotation
- 1 week on / 5 weeks off
- 4 or fewer = burnout territory; pay extra or change topology

### Primary / Secondary
- Primary pages first
- Secondary escalates after 5-15 min of no ack
- Both compensated

### Multiple Services
- Don't make one rotation cover too many heterogeneous services
- Split by domain (e.g., payments oncall vs catalog oncall)

## PagerDuty / Opsgenie Patterns

```
Alert → Schedule (PagerDuty)
   ↓ paged who's on-call
Primary: gets push, SMS, phone call
   ↓ 5 min no ack
Secondary: paged
   ↓ 10 min no ack
Manager: paged
```

### Schedules
- Layered: weekday + weekend layers
- Holiday coverage planned
- Vacation coverage swap

### Routing
- Alerts tagged by `team` route to that team's schedule
- Severity drives notification urgency (critical = phone call; warning = chat)

## Runbooks

Every alert should link to a runbook. A runbook tells you:
1. What does this alert mean?
2. How does it impact users?
3. How do I check the situation?
4. What are common causes?
5. Step-by-step mitigation
6. Escalation contacts
7. Post-incident steps

### Template
```markdown
# HighErrorRate on /api/checkout

## Summary
5% of checkout requests are returning 5xx for 5+ minutes.

## Impact
Users cannot complete purchases. Revenue impact roughly $X/min.

## Check
1. Open dashboard: https://grafana.../checkout
2. Look at: error rate, latency, downstream calls
3. Recent deploys: https://github.com/.../actions
4. Recent infra changes: terraform PRs

## Common Causes
- Recent deploy with bad config → rollback
- Downstream payment processor (Stripe) outage → check status.stripe.com
- DB connection pool exhausted → check RDS metrics
- High latency cascading → check traces in Tempo

## Mitigation
1. If recent deploy: `argocd rollback checkout v1.2.3`
2. If Stripe down: enable fallback gateway via feature flag
3. If DB pool full: scale RDS Proxy or restart pods

## Escalation
- @platform-team if infra issue
- @payments-team if logic issue
- VP Engineering if customer-impacting > 30 min

## Post-Incident
- Update incident report
- Schedule postmortem within 5 business days
```

### Keep Runbooks Current
- Update after every incident
- Link from alerts
- Search-friendly titles
- Avoid "TODO" sections

## Healthy On-Call

### Page Budget
- Target: < 2 pages per week per person
- If consistently >5/week, system is broken (not engineer)
- Track page count as KPI

### After-Hours Pages
- Track separately
- > 2/month = unhealthy
- Investigate: why did this need urgent response?

### Compensation
- Cash bonus per week on-call
- Or comp time after a busy shift
- Or both

### Boundaries
- Define handoff: when does rotation start/end
- Quiet hours protected (no proactive paging for low-sev)
- Vacation = full disconnect (cover handoff)

### Recovery
- After bad shift, day off
- After major incident, time to decompress
- Manager actively watches for signs of burnout

### Continuous Improvement
- Weekly review: what fired, what was actionable?
- Eliminate noisy pages
- Improve runbooks

## ChatOps

Slack/Teams channel patterns:
- `#alerts` — real-time alert feed
- `#incidents` — per-incident channels (auto-created from PagerDuty)
- `#oncall-handoff` — shift change notes
- `#oncall-roundup` — weekly summary

PagerDuty/Opsgenie integrate with chat for ack, escalate, resolve.

## Anti-Patterns

- **Single point person** — one engineer holds all knowledge
- **Punitive on-call** — used as punishment for bad work
- **No compensation** — burnout factory
- **Engineers fear getting paged** — usually signal of broken systems, not weak engineers
- **Reactive only** — never invest in fixing root causes

## On-Call as Career Growth

Senior+ engineers should embrace on-call:
- Forces broad system knowledge
- Reveals organizational weaknesses
- Demonstrates ownership
- Career narrative ("led on-call modernization")

But not at the cost of health.

## Interview Themes

- "Design an on-call rotation"
- "Healthy on-call signals"
- "Runbook template"
- "Reduce page noise — strategies"
- "When is on-call broken vs engineer overwhelmed?"
