# L01/C04/T02 — SRE vs DevOps Engineer

## Learning Objectives

- Distinguish SRE and DevOps Engineer on technical, cultural, and organizational axes
- Recognize which companies use which model and why their history produced it
- Understand error budgets — the single mechanic that most sharply separates the two
- Choose between the roles based on your strengths and what energizes you

## Prerequisites

L01/C04/T01 (the DevOps Engineer role) and a basic grasp of SLI/SLO concepts.

## Origin & Identity

- **SRE**: born at Google in 2003 under **Ben Treynor Sloss**, who described it as *"what happens when you ask a software engineer to design an operations team."* It is the discipline of running production using software-engineering practices, with reliability as an explicit, measured product feature.
- **DevOps Engineer**: emerged from the broader industry after the 2009 DevOpsDays movement (Patrick Debois). It crystallized as a hybrid title covering automation, pipelines, and infrastructure, with scope that varies widely by employer.

A useful framing from Google: **"class SRE implements DevOps."** DevOps is the philosophy (shared ownership, automation, measurement, blameless culture); SRE is one prescriptive, opinionated *implementation* of it with concrete rules.

## The Bar to Hire

- **SRE** at Google (and most FAANGM) requires the **same coding bar as a SWE**: data structures, algorithms, and system design at full depth. You will write production code — controllers, automation, control planes.
- **DevOps Engineer** roles often weight infrastructure, cloud, and tooling fluency over algorithmic depth. Coding matters, but the interview is rarely a LeetCode-hard gauntlet.

This single difference filters who applies and predicts the comp band.

## Error Budgets — The Defining Mechanic

This is the concept that, more than any other, separates the disciplines.

```
Availability target (SLO) = 99.9%
Error budget             = 100% - 99.9% = 0.1%
Over 30 days             ≈ 43.2 minutes of allowed downtime

  budget remaining ──► ship freely, take risks
  budget exhausted ──► deploys freeze, focus on reliability
```

In a mature SRE org, the error budget is a **shared currency** between product and SRE. Burn it too fast and feature releases pause until reliability recovers. This aligns incentives: developers can't ship recklessly, and SRE can't demand infinite stability. Most DevOps-titled roles **do not** operate a formal error budget; reliability is "important" but not a hard gate on releases.

## What They Optimize For

| Dimension | SRE | DevOps Engineer |
|---|---|---|
| Reliability of services | Primary, measured objective | One of many concerns |
| Coding contributions | High (production code, controllers) | Moderate (tools, IaC, glue) |
| On-call | Mandatory rotation, strict policies (e.g., ≤2 incidents/shift) | Common but varied |
| SLI / SLO ownership | Explicit and owned | Sometimes, often informal |
| Error budgets | Used to gate deploys | Rare |
| Toil reduction | Tracked (Google caps toil at ~50%) | Encouraged, rarely measured |
| Tooling building | Yes, with software rigor and tests | Yes, broader and more varied |
| Capacity planning | First-class responsibility | Common |

## A Concrete Task Comparison

| Task | SRE | DevOps Engineer |
|---|---|---|
| Write a Kubernetes operator | Yes, in Go, with unit + integration tests | Maybe; often configures existing operators |
| Define an SLO and burn-rate alert | Yes, routinely | Sometimes |
| Tune a Postgres query plan | Often, especially if owning data infra | Sometimes |
| Build a Terraform module library | Yes | Yes |
| Run a postmortem | Leads it | Often participates |
| Refactor production code for reliability | Yes — opens PRs against the service | Less commonly |
| Set up a GitHub Actions pipeline | Yes | Yes, frequently the owner |

## Toil — The Other SRE Discipline

Google formalized **toil**: manual, repetitive, automatable work that scales linearly with service size and carries no enduring value. SRE teams are expected to keep toil **under ~50%** of their time, spending the rest on engineering that reduces future toil. If an SRE team drifts past that threshold, work is shed back to the product team — a structural pressure valve that DevOps roles usually lack.

## When Companies Pick One Over the Other

- **Google, Meta, Microsoft**: formal SRE and/or Production Engineer orgs
- **Amazon**: "you build it, you run it" — SDEs run their own services; no central SRE org; Sysops/TPM/Support Engineer roles exist
- **Netflix**: senior SWEs own reliability; few formal SREs; strong platform/tooling teams
- **Stripe, Shopify**: Reliability Engineers / Production Engineering
- **Most startups**: DevOps Engineers — frequently the *only* ops staff

The pattern: companies large enough to fund a dedicated reliability discipline with a SWE hiring bar adopt SRE; everyone else hires DevOps Engineers for breadth.

## Which Should You Choose

| You Are... | Probably Pick |
|---|---|
| Strong coder, love systems, want to write production code | SRE |
| Broad infrastructure interest, less coding-focused | DevOps Engineer |
| Want depth in a specific domain (networking, databases, control planes) | SRE or specialist |
| Want to influence many teams' practices and DX | Platform Engineer or DevOps |
| Want clear OKRs tied to reliability and error budgets | SRE |
| Thrive on variety and being the "fix anything" person | DevOps Engineer |

## Common Mistakes

- **Treating the titles as identical** — they overlap ~70%, but the 30% (coding bar, error budgets, SLO ownership) decides comp and fit
- **Calling yourself SRE without the coding depth** — you'll fail the interview loop and underperform in the role
- **Assuming DevOps means less rigor** — strong DevOps engineers build tooling with the same software discipline as SREs
- **Ignoring org context** — "SRE" at one company is "DevOps" at another; read the JD, not the title
- **Promising 100% uptime** — the absence of an error budget is itself an anti-pattern; some failure must be acceptable

## Best Practices

- **Make reliability measurable** regardless of title — define SLIs/SLOs even if your org doesn't mandate them
- **Cap and track toil** — borrow the 50% rule; if you're drowning in manual work, that's a planning input, not a personality trait
- **Use error budgets to mediate conflict** — they convert "dev vs ops" arguments into a shared, data-driven decision
- **Invest in coding** if you want the SRE/Staff ceiling — Go or Python at production quality is the unlock
- **Lead blameless postmortems** — the artifact that turns incidents into systemic fixes (see L01/C02)

## Quick Refs

```promql
# Multi-window burn-rate alert (fast burn): paging when you'll
# exhaust a 30-day error budget in ~2 days
(
  sum(rate(http_requests_total{status=~"5.."}[1h]))
  / sum(rate(http_requests_total[1h]))
) > (14.4 * 0.001)   # 14.4x burn rate against a 99.9% SLO
```

Mnemonic: **DevOps is the *what* (philosophy); SRE is a prescriptive *how* (error budgets, toil caps, SLOs, a SWE bar).**

## Interview Prep

**Junior**: "What's the difference between SRE and DevOps Engineer?"
- DevOps is a culture of shared ownership and automation; SRE is Google's specific implementation of it, with a software-engineering hiring bar and explicit reliability targets.

**Mid**: "What is an error budget and how does it change a team's behavior?"
- It's the inverse of the SLO — the allowed amount of unreliability. When it's healthy, teams ship fast; when it's burned, deploys freeze and focus shifts to reliability, aligning dev and ops incentives.

**Senior**: "Why does Google have SRE and Amazon doesn't?"
- Google centralized reliability as a discipline with a SWE bar and error budgets; Amazon pushed reliability into product teams via 'you build it, you run it.' Both implement DevOps — different org topologies for the same goal.

**Staff**: "Argue for or against creating a separate SRE org in a company that currently has only DevOps engineers."
- Weigh the benefits (consistent reliability practice, error budgets, a coding bar) against the risk of recreating a Dev↔Ops silo; tie the decision to org size, service criticality, and whether you can fund SWE-level hires without starving product teams.

## Next Topic

→ [T03 — Platform Engineer & Internal Developer Platforms](T03-Platform-Engineer.md)
