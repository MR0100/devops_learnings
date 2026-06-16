# L01/C01/T03 — DevOps vs Traditional IT Operations

## Learning Objectives

- Articulate the structural differences between traditional IT ops and DevOps
- Map ITIL processes to DevOps practices (where they translate, where they don't)
- Explain "Type 1 vs Type 2" work and why classical IT optimized for the wrong type

## The Traditional IT Operations Model

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│   DEV    │  hand-  │   QA     │  hand-  │   OPS    │
│  (build) │  off →  │  (test)  │  off →  │ (deploy/ │
│          │         │          │         │   run)   │
└──────────┘         └──────────┘         └──────────┘
                                                │
                                                ▼
                                      Tickets, Change Boards,
                                      Maintenance Windows
```

Hallmarks:

- **Functional silos** — devs, QA, ops separated by org and tooling
- **Change as risk** — Change Advisory Boards (CAB) gate every change
- **Documented runbooks** — humans execute steps from documents
- **Tickets as currency** — work moves through ticket queues
- **ITIL framework** — process-heavy, documentation-heavy
- **Quarterly or yearly releases** — batching reduces "change risk"

## The DevOps Model

```
┌────────────────────────────────────────────────┐
│   Cross-Functional Product Team                │
│   • Builds the service                         │
│   • Tests the service                          │
│   • Deploys the service                        │
│   • Operates the service                       │
│   • Owns the on-call rotation                  │
└─────────────────────┬──────────────────────────┘
                      │
                      ▼
            ┌─────────────────────┐
            │  Internal Platform  │
            │  (paved roads)      │
            └─────────────────────┘
```

Hallmarks:

- **Cross-functional teams** — one team owns a service end-to-end
- **Change as routine** — small frequent changes are safer than big rare ones
- **Automated runbooks** — runbooks are code (operators, controllers)
- **Pull requests as currency** — work moves through PRs and pipelines
- **Continuous delivery** — every commit is a release candidate

## Mapping ITIL to DevOps

| ITIL Concept | DevOps Equivalent |
|---|---|
| Change Management | Pull request review + automated CI gates |
| Release Management | Deployment pipeline |
| Incident Management | On-call rotation + runbook automation |
| Problem Management | Blameless postmortem + action items |
| Service Level Agreement | SLI/SLO + error budget policy |
| Configuration Management Database (CMDB) | Infrastructure as Code + Service Catalog (e.g., Backstage) |
| Service Desk | Self-service platform |

ITIL isn't *wrong* — it codifies real operational concerns. DevOps redistributes those concerns into automated systems and shared team ownership.

## Type 1 vs Type 2 Work

This concept from *Team Topologies* / *Phoenix Project*:

- **Type 1 (Business projects)** — features for customers
- **Type 2 (Internal projects)** — platform, tooling, infrastructure
- **Type 3 (Operational changes)** — config, certificates, capacity
- **Type 4 (Unplanned work)** — incidents, firefighting

Traditional IT optimized for **Type 4 efficiency** (be great at firefighting). DevOps optimizes to **eliminate Type 4 sources** through Type 2 investment.

## When Traditional IT Is Still Right

This isn't black and white. Some contexts still need traditional ops models:

- Highly regulated industries with mandatory CABs (some financial trading, FDA-regulated medical devices)
- Legacy systems where the cost of change is genuinely high
- Air-gapped or contractually-frozen environments

A staff engineer recognizes when modernization is and isn't the right call.

## Common Mistakes

- **Relabeling Ops as a "DevOps team"** — moving the same handoff wall one box to the right; the silo survives the rename.
- **Cargo-culting the org chart** — copying cross-functional teams without giving them the ownership, on-call, and platform that make the model work.
- **Treating ITIL as the enemy** — ITIL codifies real concerns (change, incident, problem); the goal is to automate those concerns, not pretend they vanished.
- **Optimizing Type 4 work** — getting excellent at firefighting (faster incident bridges, more runbooks) instead of investing in Type 2 work that removes the fires.
- **Big-bang transformation** — trying to flip a 200-engineer org to CD in one quarter instead of converting low-risk change classes first.

## Best Practices

- **Move risk control left** — replace per-release human approval (CAB) with per-commit automated gates: tests, policy checks, and progressive delivery.
- **Translate, don't discard ITIL** — map each ITIL process to its DevOps equivalent (PR review, pipeline, on-call, postmortem) so compliance stakeholders see continuity.
- **Pre-approve change classes** — define standard/low-risk changes that skip the CAB, reserving manual review for genuinely novel risk.
- **Invest in Type 2 to kill Type 4** — fund platform and tooling work explicitly, and measure the reduction in unplanned work as the return.
- **Generate compliance evidence automatically** — pipelines should emit the audit trail (who, what, tests passed) the CAB used to demand in a meeting.

## Quick Refs

**Traditional IT → DevOps at a glance**

| Dimension | Traditional IT | DevOps |
|---|---|---|
| Team shape | Functional silos (Dev/QA/Ops) | Cross-functional product team |
| Unit of work | Ticket | Pull request |
| Change posture | Risk to be gated (CAB) | Routine, small, frequent |
| Runbooks | Humans execute docs | Code (operators/controllers) |
| Release cadence | Quarterly/yearly batches | Continuous delivery |

**Type-of-work cheat sheet**: Type 1 = business features · Type 2 = platform/tooling · Type 3 = operational changes · Type 4 = unplanned/firefighting. *Spend Type 2 to shrink Type 4.*

## Interview Prep

**Mid**: "What's the difference between a Change Advisory Board and a pull request?"
- Both gate changes; PR is automated and per-commit, CAB is human and per-release. DevOps shifts risk control from approval bottleneck to automated quality gates.

**Senior**: "Our compliance team requires a CAB. How do you reconcile with DevOps?"
- Answer should mention pre-approved change classes, automated evidence for the CAB, and incremental risk reduction rather than head-on conflict.

**Staff**: "Walk me through how you'd transform a 200-engineer org from quarterly releases to continuous delivery."

## Next Topic

→ [T04 — DevOps vs Agile vs SRE vs Platform Engineering](T04-DevOps-vs-Agile-vs-SRE.md)
