# L17/C08/T04 — Error Budget Policies

## Learning Objectives

- Define EBP
- Enforce it

## Error Budget Policy

What happens when budget exhausted:
- Releases?
- Reliability work?
- Postmortems?

Pre-agreed; explicit.

## Why

Without policy:
- Budget metric exists but ignored
- No accountability
- Toy

With policy:
- Forces conversation
- Reliability prioritized
- Trust mechanism between dev + SRE

## Sample Policy

```
When error budget < 0%:
  - Freeze releases (except security)
  - Senior eng review for hotfix
  - Reliability work prioritized
  - Postmortem within 5 days

When budget 0-50%:
  - Increased scrutiny on changes
  - Risk register reviewed

When budget > 50%:
  - Normal pace
  - Risk taking OK
```

For: graduated response.

## Stakeholders

- Engineering (devs)
- SRE
- Product
- Leadership

Agree together. Document.

## Release Freeze

Hard rule:
- Budget exhausted → no new feature releases
- Only: bug fixes, reliability, security

For: focus on reliability.

## Exceptions

```
Critical security: always allowed
Customer-blocking bug: allowed with VP approval
```

Document carefully.

## Reliability Work

When budget low:
- Pause feature work (some %)
- Address top reliability issues
- Run game days
- Fix top alerts

For: pay debt.

## Reviewing SLO

If always under budget:
- SLO too lenient
- Tighten

If always exhausted:
- SLO too strict
- Engineering can't meet
- Loosen OR invest

For: realistic targets.

## Cross-Service

Service A's SLO depends on Service B.

If B exhausts: A consumes budget through no fault.

Policy: B owner accountable; A informed.

For: dependency awareness.

## Per-Customer SLO

For SaaS:
- Per-tenant SLO
- Budget per tenant

For: enterprise contracts.

## SLA vs SLO

| | SLA | SLO | SLI |
|---|---|---|---|
| External | yes | no | no |
| Contractual | yes | aspirational | metric |
| Penalty | refund / discount | internal | none |

SLO < SLA (buffer).

## Sample Policy Text

```
This document establishes Error Budget Policy for myapp.

SLO: 99.9% availability over 28 days
Error budget: 0.1% = 43 min/month

Budget Status:
- > 50% remaining: green
- 0-50% remaining: yellow
- < 0%: red

Actions:
- Green: normal velocity; risk taking encouraged
- Yellow: increased scrutiny; risk register reviewed weekly
- Red: 
  * Feature releases frozen (except policy exceptions)
  * Reliability work prioritized (>50% engineering time)
  * Postmortems for top contributors
  * Weekly SLO review meeting

Exceptions:
- Critical security: always allowed (VP approval logged)
- Customer-blocking bug: allowed with VP approval

Review:
- Quarterly: SLO target validation
- Quarterly: policy effectiveness

Owners:
- SRE: track + report
- Eng Manager: enforce
- VP: exception approval
```

## Burn Rate Triggers

Beyond exhausted:
- Fast burn (14x for 1h): pause new releases briefly
- Slow burn (3x for 1 day): increase monitoring

For: proactive.

## Game Days

When budget high:
- Inject failure
- Verify SLO maintained
- Build confidence

For: practice resilience.

## Tooling

- DORA metrics
- SLO dashboards (Pyrra, Sloth, Nobl9)
- Release management (lock when red)
- Postmortem template

## Cultural

EBP requires:
- Trust between dev + SRE
- Leadership backing
- Clear communication
- Iteration

For: works only if respected.

## Common Mistakes

- Policy not enforced (lip service)
- SLO too strict (always red)
- No exceptions (rigid)
- No review (stale)
- Punishment culture (blame)

## Successful Adoption

```
1. Baseline: measure current SLO
2. Set realistic target (slightly stretch)
3. Track for 1 quarter
4. Add EBP gradually
5. Iterate
```

For: not big-bang.

## Reporting

Monthly:
- SLO compliance per service
- Top contributors to budget burn
- Reliability work done
- Trends

For: visibility.

## Tied to Promotions

Some orgs: SLO compliance affects performance review.

Risk: gaming.

For: cautious tie.

## Real Examples

### Google
SRE book defines EBP origin.

### Spotify
EBP across services.

### Many fintech
SLO-driven; EBP enforced.

## Drawbacks

- Process overhead
- Politics (release freezes unpopular)
- Hard for shared infra
- Doesn't help if alerts wrong

## Best Practices

- **Agree the policy *before* you need it.** Write down what happens at each
  budget level, get dev + SRE + product + leadership to sign off, and store
  it as a versioned document — a policy invented mid-incident has no
  authority.
- **Use graduated responses, not a single cliff.** Green (>50%) = full
  velocity, yellow (0–50%) = added scrutiny, red (<0%) = freeze + reliability
  focus. A binary "freeze/no-freeze" rule gets ignored or fought.
- **Automate the trigger.** Wire the burn-rate/budget signal into release
  tooling so "red" actually locks deploys, and surface budget status on a
  dashboard — manual enforcement decays into lip service.
- **Always define exceptions** (security fixes, customer-blocking bugs) with a
  named approver and an audit log. A policy with no escape valve gets
  bypassed and discredited.
- **Treat the SLO as tunable.** Perpetually red means the target is too strict
  (loosen or invest); perpetually green means it's too loose (tighten). Review
  the target quarterly using real data.
- **Pair with burn-rate alerts, not just end-of-window exhaustion** so you act
  before the budget is gone (fast burn → pause; slow burn → investigate).
- **Keep it blameless.** Budgets fund a conversation about reliability vs
  velocity; the moment they become a stick for performance reviews, teams game
  the SLI instead of improving the service.

## Quick Refs

```
Budget status → action

> 50%:   normal
0-50%:   scrutiny
< 0%:    freeze + reliability focus
```

## Interview Prep

**Mid**: "What's error budget policy."

**Senior**: "Enforce EBP."

**Staff**: "SLO + EBP at scale."

## Next Topic

→ Move to [L18 — Logging & Distributed Tracing](../../L18/README.md)
