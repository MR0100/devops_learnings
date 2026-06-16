# L01/C04/T01 — The DevOps Engineer Role

## Learning Objectives

- Define the day-to-day work of a DevOps Engineer and how it shifts by company size and maturity
- Identify what genuinely differentiates this role from SRE, Platform, Cloud, and SysAdmin roles
- Build a target skill profile and read job descriptions critically
- Understand the compensation and growth landscape so you can negotiate and plan

## Prerequisites

A working mental model of DevOps as a culture (L01/C01) and the value stream (L01/C03).

## What "DevOps Engineer" Actually Means

There is a famous objection — *"DevOps is a culture, not a job title"* — and it's correct in principle. DevOps is a way of working that ideally every team owns. But the **labor market disagrees with the purists**: tens of thousands of open requisitions say "DevOps Engineer", and they describe a real, hireable scope of work. The honest reconciliation:

> A DevOps Engineer is the person who builds and operates the **paved road** — the automation, pipelines, and infrastructure abstractions — that lets product engineers ship and run their own software safely.

The danger is a company that hires a "DevOps team" and recreates the old Dev↔Ops wall (covered as an anti-pattern in L01/C06). A *good* DevOps Engineer reduces the amount of ops work product teams must do; a *bad* DevOps org becomes the new ticket queue.

## Typical Day-to-Day

- Building and maintaining CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins, ArgoCD)
- Writing Infrastructure as Code (Terraform, OpenTofu, CloudFormation, Pulumi)
- Operating Kubernetes clusters — upgrades, autoscaling, ingress, RBAC
- Configuring monitoring, dashboards, and alerting (Prometheus, Grafana, Datadog)
- Responding to incidents and production issues, often on a rotation
- Supporting product teams in deploying and debugging their services
- Capacity planning, rightsizing, and cost optimization (FinOps)
- Day-2 ops: security patching, certificate rotation, dependency upgrades, DR drills

How this mix shifts with context:

| Context | What the role looks like |
|---|---|
| Seed/Series A startup | You ARE the ops org. Cloud account, CI, on-call, security — all you. Breadth over depth. |
| Scale-up (50–300 eng) | You build shared tooling and golden paths; start specializing (CI, K8s, observability). |
| Enterprise | Narrow, deep ownership of one platform (e.g., the Terraform module library, the Jenkins fleet). |
| FAANGM | The title is usually SRE/Production Engineer; "DevOps" maps to internal tools/infra SWE. |

## Required Core Skills

- **Linux**: deep familiarity — `strace`, `/proc`, systemd, cgroups, comfortable troubleshooting blind
- **Networking**: VPCs, subnets, routing, DNS, load balancers, TLS, the OSI layers in practice
- **Cloud provider**: expert depth on at least one (AWS most common), conversant on a second
- **Containers**: Docker image hygiene, Kubernetes objects, the scheduler, networking (CNI)
- **IaC**: Terraform/OpenTofu — modules, state, drift, plan review discipline
- **CI/CD**: at least one pipeline tool end-to-end, plus GitOps (ArgoCD/Flux)
- **Programming**: Bash for glue, plus Python **or** Go for real tooling
- **Observability**: metrics (Prometheus), logs (Loki/ELK), traces (OpenTelemetry)
- **Security basics**: IAM least-privilege, secrets management, image/dependency scanning

A useful self-assessment: you should be able to take a service you've never seen, find its logs, identify why it's failing, and ship a fix through the pipeline — without asking anyone where things live.

## Differentiation from Adjacent Roles

| vs. | The honest distinction |
|---|---|
| **SRE** | DevOps leans pipeline/tooling/breadth; SRE leans reliability, SLOs, error budgets, and a SWE-level coding bar. |
| **Platform Engineer** | Platform builds an internal *product* with a roadmap; DevOps often embeds with and serves specific teams. |
| **Cloud Engineer** | Cloud goes deep on cloud architecture (networking, landing zones); DevOps spans the whole delivery lifecycle. |
| **SysAdmin** | SysAdmins maintain existing systems by hand/ticket; DevOps automates so the system maintains itself. |

These are tendencies, not walls. At most companies under 200 engineers, one person does pieces of all five.

## Reading a Job Description Critically

| Phrase | Likely Reality |
|---|---|
| "End-to-end ownership" | You'll be on-call |
| "Self-starter" | Limited mentorship and onboarding |
| "Wear many hats" | Broad work, little specialization |
| "Greenfield environment" | Either exciting, or "we have nothing yet and no standards" |
| "Modernize legacy systems" | A migration project, possibly painful and political |
| "Build a platform team" | An IDP investment — exciting but slow; ask about budget and headcount |
| "Fast-paced environment" | Frequent context-switching, possibly weak prioritization |
| "Rockstar / ninja" | Immature engineering culture; proceed with caution |

Questions that reveal the real role: *What's the on-call rotation and how often does it page? Who owns production reliability today? What's the deploy frequency? How many people will do what I do?*

## A Mental Model of the Role

```
   PRODUCT ENGINEERS
   (write & run their services)
          │  self-service
          ▼
   ┌─────────────────────────┐
   │   THE PAVED ROAD        │  ← DevOps Engineer builds & operates this
   │  CI/CD · IaC · K8s ·    │
   │  observability · secrets│
   └───────────┬─────────────┘
               ▼
   CLOUD / INFRASTRUCTURE
```

If product engineers can't move without you, you're a bottleneck. If they can move *because of* you, you're doing the job right.

## Salary & Growth Outlook (2026, US)

| Level | Total Comp (approx) |
|---|---|
| Mid DevOps Engineer | $130K–$180K |
| Senior | $180K–$280K |
| Staff at FAANGM | $350K–$600K+ |

Growth paths branch by what energizes you: DevOps → Senior SRE → Staff SRE → Principal; or DevOps → Platform Engineer → Platform Architect; or DevOps → Cloud/Infra specialist. Comp varies enormously by geography and equity; treat these as US-market anchors, not guarantees.

## Common Mistakes

- **Collecting tools, not outcomes** — knowing 30 CLIs but unable to reduce a team's lead time
- **Becoming the ticket queue** — owning deploys *for* teams instead of enabling teams to deploy themselves
- **No coding depth** — stuck stitching YAML; the ceiling is low without Python/Go to build real tooling
- **Hero on-call** — fixing the same incident manually every week instead of automating it away
- **Ignoring cost** — building elegant infra that quietly burns six figures a month
- **Snowflake servers** — manual changes that drift from IaC, making the system unreproducible

## Best Practices

- **Automate the thing you did twice** — the second manual repetition is the signal to script it
- **Treat infrastructure as a product** — even before there's a platform team, build for self-service
- **Default to least privilege** — IAM, secrets, and network rules start closed and open only as needed
- **Instrument before you optimize** — measure lead time, MTTR, and cost before claiming an improvement
- **Write runbooks** — if you're the only one who can do it, you've created a single point of failure (you)
- **Push ownership left** — your goal is to make yourself less necessary to each individual deploy

## Quick Refs

```bash
# Inspect what a node is actually running
kubectl get pods -A --field-selector spec.nodeName=$NODE -o wide

# Find the most expensive AWS services this month
aws ce get-cost-and-usage --time-period Start=2026-06-01,End=2026-06-15 \
  --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Detect Terraform drift without applying
terraform plan -detailed-exitcode   # exit 2 = drift exists

# Who can assume this IAM role? (least-privilege audit starting point)
aws iam get-role --role-name my-role --query 'Role.AssumeRolePolicyDocument'
```

Role-defining metrics to own: **Deployment Frequency, Lead Time, MTTR, Change Failure Rate** (the DORA four), plus **cloud spend per environment**.

## Interview Prep

**Junior**: "What does a DevOps engineer do day-to-day?"
- Building/maintaining CI/CD, writing IaC, running containers, setting up monitoring, and helping teams deploy — automating the path from commit to production.

**Mid**: "Walk me through how you'd take a service from a Dockerfile to production safely."
- Containerize, push to a registry on CI, deploy via IaC/GitOps to a staging env, run automated tests and a canary, gate on health metrics, then progressive rollout with an automated rollback trigger.

**Senior**: "How is your role different from an SRE at your previous job?"
- Frame it on axes: coding bar, SLO/error-budget ownership, and breadth vs. reliability focus — then give a concrete example of work you owned that an SRE org would have structured differently.

**Staff**: "If I told you we had no DevOps engineers, what would you build first and why?"
- Start from the biggest constraint (usually a reproducible deploy path and an on-call/observability baseline), justify with DORA and risk, and sequence toward a self-service paved road rather than centralizing ops in yourself.

## Next Topic

→ [T02 — SRE vs DevOps Engineer](T02-SRE-vs-DevOps.md)
