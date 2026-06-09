# L19/C01 — SRE Origins & Philosophy

## Topics

- **T01 The Google SRE Book in 90 Minutes** — Core ideas distilled
- **T02 Embracing Risk** — Why 100% reliability is wrong
- **T03 Eliminating Toil** — The 50% rule

## Origin

Ben Treynor Sloss at Google, ~2003. The question: "How do we run our services reliably at planet scale?"

Insight: Operations is a software engineering problem. Hire software engineers; let them solve ops with code.

## The SRE Book (2016)

Free online. Key chapters every SRE should read:
- Ch 1 — Introduction
- Ch 3 — Embracing Risk
- Ch 4 — Service Level Objectives
- Ch 5 — Eliminating Toil
- Ch 8 — Release Engineering
- Ch 12 — Effective Troubleshooting
- Ch 13 — Emergency Response
- Ch 14 — Incident Management
- Ch 15 — Postmortem Culture

## SRE in 5 Principles

### 1. Embrace Risk
> 100% reliability is the wrong target.

- Users can't tell 99.99% from 100%
- Each "nine" is exponentially more expensive
- Accept controlled risk in exchange for velocity

This leads to SLOs (target reliability) + Error Budgets (allowable badness).

### 2. SLOs are the Contract
SRE doesn't care about uptime — they care about SLOs. SLO defines what "reliable enough" means.

### 3. Error Budget Drives Decisions
When budget healthy → ship more features.
When budget exhausted → freeze features, fix reliability.

This is the engineering organizational lever. Reliability isn't "we'll do it later" — it's gated by a measurable budget.

### 4. Eliminate Toil
Toil = manual, repetitive, automatable work. The 50% rule: SREs spend at most 50% of time on toil; the rest on software engineering to eliminate toil.

If toil exceeds 50%, escalate: hire more SREs or kill the toil-generating workload.

### 5. Monitoring & Alerting Should Be Quiet
- Pages should be infrequent (per-person, < 2/week)
- Alert on symptoms (customer-visible) not causes (CPU)
- Use SLO burn rate
- Runbooks for every alert

## Embracing Risk in Practice

Risk = (probability) × (impact).

Each change to production has risk. Mitigations:
- Canary deployments (small blast radius)
- Feature flags (instant rollback)
- Tests (reduce probability)
- Observability (detect fast)
- Automated rollback (limit duration)

Conscious risk: accept calculated chance of incident in exchange for shipping.

## Toil Examples

| Activity | Toil? | Fix |
|---|---|---|
| Restarting a stuck pod | Yes | K8s auto-restart |
| Manually scaling for known peak | Yes | HPA |
| Rotating certificates | Yes | cert-manager |
| Promoting deploys through envs | Yes | GitOps + Argo |
| Investigating novel incidents | No (engineering) | — |
| Code review | No | — |
| Capacity planning analysis | No (engineering) | — |

If you can write code to eliminate a recurring task → do it.

## Toil Quantification

Track in your team:
- Hours per week on toil per engineer
- Top sources of toil
- Reduce quarter-over-quarter

If a team's toil exceeds 50%, it's burnout territory. Either:
- Add headcount
- Stop accepting the workload
- Invest hard in toil reduction

## SRE vs DevOps Engineer

| | SRE | DevOps Engineer |
|---|---|---|
| Origin | Google (2003) | Industry (~2010) |
| Coding bar | Same as SWE | Variable |
| Day-to-day | Reliability eng | Tooling + ops |
| Authority | Can refuse to operate | Less |
| SLO/Error Budget | First-class | Variable |
| Org structure | Centralized or embedded | Often embedded |

> "Class SRE implements interface DevOps." — DevOps is principles; SRE is one opinionated implementation.

## Class SRE

In Google, SRE has the authority to:
- Set SLO
- Enforce Error Budget Policy (freeze deploys)
- Refuse to operate a service that doesn't meet PRR (Production Readiness Review) criteria
- Hand a service back to dev when it's too unreliable

This last point is unique. Without that authority, "SRE" is just renamed Ops.

## Hiring SREs

- Strong coding (full SWE bar at Google)
- Systems thinking
- Calm under pressure
- Comfortable saying "no" with data
- Bias to automation

You can't make an SRE team by retitling sysadmins.

## When NOT to Adopt SRE

- Small team (< 30 engineers) — SRE roles aren't justified; do DevOps
- Pre-product-market-fit — reliability isn't yet the constraint
- No exec support for Error Budget enforcement — SRE becomes hollow

## Interview Themes

- "What is SRE?"
- "Why embrace risk?"
- "Toil — define, measure, eliminate"
- "SRE vs DevOps Engineer"
- "Error Budget Policy — what's in it?"
- "Why can SRE refuse to operate a service?"
