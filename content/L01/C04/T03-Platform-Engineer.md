# L01/C04/T03 — Platform Engineer & Internal Developer Platforms

## Learning Objectives

- Define what a Platform Engineer does and how the role differs from DevOps and SRE
- Articulate why Internal Developer Platforms (IDPs) emerged and what problem they solve
- Recognize the difference between a platform *team* and a "tools team"
- Understand the anti-patterns that kill platform investments and the metrics that prove value

## Prerequisites

L01/C04/T01–T02, and the team-topology ideas from *Team Topologies* (referenced in C06).

## What an IDP Actually Is

An **Internal Developer Platform (IDP)** is an internal *product* built by a platform team that gives product engineers self-service access to infrastructure, deployment, observability, security, and the other capabilities they need — **without filing tickets**.

> "An IDP turns the platform team's expertise into a product, not a service desk."

The key word is **product**. A platform team has users (other engineers), a roadmap, adoption metrics, and a feedback loop. It is not a help desk that fields requests; it ships paved roads that make the right thing the easy thing.

The reference architecture from the IDP community (Humanitec et al.) describes five planes:

| Plane | Responsibility | Example tools |
|---|---|---|
| **Developer Control Plane** | How engineers interact with the platform | Backstage, CLI, PR-based config |
| **Integration & Delivery** | Build, test, deploy orchestration | GitHub Actions, ArgoCD, Flux |
| **Resource Plane** | The actual compute, data, networking | Kubernetes, RDS, cloud APIs |
| **Monitoring** | Metrics, logs, traces, dashboards | Prometheus, Grafana, OpenTelemetry |
| **Security** | Secrets, identity, policy enforcement | Vault, OPA/Kyverno, OIDC |

## Why IDPs Emerged

Symptoms in a 50–200 engineer org **without** an IDP:

- Every team writes its own Terraform module library, slightly differently
- Inconsistent monitoring — some services have dashboards, some have nothing
- Repeated, divergent secret-management implementations
- New-service onboarding takes weeks of copy-paste and Slack archaeology
- The ops team is bottlenecked by per-team requests and becomes the new wall

An IDP fixes these by **abstracting them as a product** with sane, opinionated defaults. The economic argument: without it, the cost of operational knowledge scales with the number of teams; with it, that cost is paid once and amortized.

## What a Platform Engineer Builds

- A **service catalog** — Backstage is the common open-source base
- **Golden path templates** for new services (CRUD API, event consumer, ML service, batch job) that ship with CI, observability, and security wired in
- **Self-service environment provisioning** — spin up a namespace/database/queue via PR or portal
- **Standardized observability** — every service auto-emits metrics, logs, and traces with no extra work
- **Paved-road CI/CD** with secure defaults baked in
- **Secret-management abstraction** — engineers don't choose Vault vs. Secrets Manager; they just declare a secret
- **Cost reporting** per team and per service

The golden-path idea: provide an opinionated default that covers 80% of cases beautifully, while leaving an "off-road" escape hatch for the 20% who genuinely need something custom. Mandating the paved road for everyone backfires; making it the easiest path wins voluntarily.

## Platform Engineer Skill Profile

- Strong software engineering (Go, Python, TypeScript) — you build a real product
- Deep Kubernetes — CRDs, operators, the controller pattern, Crossplane
- IaC mastery — Terraform/OpenTofu, Pulumi, and how to expose them safely to non-experts
- **Product mindset** — you act as a PM for internal users: user research, prioritization, adoption
- Strong empathy for developer experience (DX) — you measure and reduce friction

## "Platform Team" vs "Tools Team"

| Tools Team | Platform Team |
|---|---|
| Buys/integrates tools | Builds and runs the platform as a product |
| Reactive (ticket-driven) | Proactive (roadmap-driven) |
| Success = tool installed | Success = adoption + DX metrics |
| Often siloed from users | Embedded with and accountable to users |
| Output measured in completed tickets | Outcome measured in teams enabled |

## Where the Role Sits vs. DevOps and SRE

```
                 reliability focus
                        ▲
                        │   SRE
                        │
   breadth / ops ◄──── DevOps ────► product / DX
                        │
                        │  Platform Engineer
                        ▼
                  product focus
```

DevOps spans the delivery lifecycle for specific teams; SRE owns reliability with a SWE bar; Platform Engineering builds a reusable *product* that the other roles (and product teams) consume. In small orgs these collapse into one person; the distinction sharpens with scale.

## Common Anti-Patterns

- **The Inner Build Empire** — overengineering generic abstractions before knowing user needs; building a platform for problems no one has yet
- **Platform PM Absent** — no one owns user research, so the team builds in a vacuum and ships features nobody asked for
- **Lift-and-Shift Wrapper** — exposing raw AWS console concepts behind a thin UI; not actually abstracting anything
- **No Adoption Strategy** — "build it and they will come" (they won't); adoption must be earned and marketed internally
- **Mandate-by-Decree** — forcing teams onto the platform before it's better than what they have, breeding resentment
- **Premature Platform** — investing in a platform team at 15 engineers, before the duplication pain justifies it

## Platform Team Success Metrics

- **Adoption rate** — % of teams/services using the platform
- **Time to first deploy** for a new service — hours, not weeks
- **Developer NPS / satisfaction** — survey-based, tracked over time
- **Incidents prevented** — guardrails that caught misconfigurations before production
- **Cost saved** through standardization and rightsizing
- **Toil eliminated** — manual requests removed by self-service

If adoption is flat, nothing else matters — a platform no one uses is pure cost.

## Common Mistakes

- **Building before researching** — shipping abstractions for imagined users instead of interviewing real ones
- **Confusing activity with value** — measuring tickets closed or tools installed instead of adoption and DX
- **Forgetting the escape hatch** — making the paved road a cage drives your best engineers off-platform
- **Owning everything centrally** — turning the platform team into the new ops bottleneck you were trying to remove
- **Ignoring documentation and onboarding** — a powerful platform with no docs has the adoption of no platform

## Best Practices

- **Treat developers as customers** — run user interviews, maintain a backlog, ship the most-wanted thing next
- **Ship one strongly-adopted golden path first** — depth on one paved road beats ten half-built ones
- **Make the right way the easy way** — win adoption by being better, not by mandate
- **Measure DX explicitly** — time-to-first-deploy and NPS are your KPIs, not lines of YAML
- **Provide thin, opinionated abstractions** — hide complexity, but always leave an off-ramp for the 20% edge case
- **Dogfood** — your team should deploy its own services through the platform it builds

## Quick Refs

```yaml
# A "golden path" service scaffold (Backstage software template, abridged)
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: crud-service
  title: CRUD Service (Go) — paved road
spec:
  steps:
    - id: fetch        # opinionated repo with CI, Dockerfile, Helm chart
      action: fetch:template
    - id: publish      # creates the repo
      action: publish:github
    - id: register     # auto-registers in the service catalog
      action: catalog:register
```

Mnemonic: **DevOps/SRE *operate* infrastructure; Platform Engineers *productize* it.**

## Interview Prep

**Junior**: "What's an Internal Developer Platform?"
- A self-service internal product that lets product engineers provision infra, deploy, and get observability without filing tickets — the platform team's expertise packaged as a product.

**Mid**: "What's the difference between a platform team and a tools team?"
- A tools team buys and installs tools reactively from tickets; a platform team builds and runs a product proactively against a roadmap, and measures success by adoption and developer experience, not tickets closed.

**Senior**: "We have an IDP that no one uses. How do you fix it?"
- This is almost always a product-market-fit problem: interview engineers to find their real pain, ship one excellent golden path they'll adopt voluntarily, prove it with time-to-deploy and NPS, then expand — never mandate before it's genuinely better.

**Staff**: "Design an IDP from scratch for a fintech startup at 80 engineers, projecting to 300."
- Start from user research and the top duplication pains; sequence golden paths by impact; build on Kubernetes + Backstage + GitOps with a secrets/policy plane for compliance; staff it with a PM mindset; and define adoption, DX, and cost metrics up front so the investment is defensible to leadership.

## Reading

- *Team Topologies* — Skelton & Pais (the chapters on platform teams and team interaction modes)
- Humanitec — Internal Developer Platform reference architecture and blog
- Spotify Engineering — the Backstage origin and golden-path posts

## Next Topic

→ [T04 — Cloud Engineer / Infrastructure Engineer](T04-Cloud-Engineer.md)
