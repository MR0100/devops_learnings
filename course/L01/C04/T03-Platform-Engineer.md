# L01/C04/T03 — Platform Engineer & Internal Developer Platforms

## Learning Objectives

- Define what a Platform Engineer does
- Articulate why "Internal Developer Platforms" (IDPs) emerged
- Recognize the difference between a platform team and a "tools team"

## What an IDP Actually Is

An IDP is an **internal product** built by a platform team that gives product engineers self-service access to infrastructure, deployment, observability, security, and the other capabilities they need — without filing tickets.

> "An IDP turns the platform team's expertise into a product, not a service desk."

## Why IDPs Emerged

Symptoms in a 50–200 engineer org without an IDP:

- Every team writes their own Terraform module library
- Inconsistent monitoring across services
- Repeated secret-management implementations
- New service onboarding takes weeks
- Ops bottlenecked by per-team requests

IDP fixes by abstracting these as a product.

## What a Platform Engineer Builds

- A **service catalog** (Backstage being the common base)
- **Golden path** templates for new services (CRUD service, ML service, batch job)
- **Self-service portals** for environment provisioning
- **Standardized observability** (every service auto-emits metrics/logs/traces)
- **Paved-road CI/CD** with sane defaults
- **Secret management abstraction** (engineers don't choose Vault vs Secrets Manager)
- **Cost reporting** per team

## Platform Engineer Skill Profile

- Strong software engineering (Go, Python, TypeScript)
- Deep Kubernetes (CRDs, operators, Crossplane)
- IaC mastery (Terraform, Pulumi)
- Product mindset (PMs for internal users)
- Strong empathy for engineer developer experience (DX)

## "Platform Team" vs "Tools Team"

| Tools Team | Platform Team |
|---|---|
| Buys/integrates tools | Builds and runs the platform as a product |
| Reactive (ticket-driven) | Proactive (roadmap-driven) |
| Success = tool installed | Success = adoption + DX metrics |
| Often siloed | Embedded with users |

## Common Anti-Patterns

- **The Inner Build Empire** — overengineering generic abstractions before knowing user needs
- **Platform PM Absent** — no one owns the user research; team builds in a vacuum
- **Lift-and-Shift Wrapper** — exposing AWS console concepts; not actually abstracting
- **No Adoption Strategy** — build it and they will come (they won't)

## Platform Team Success Metrics

- Adoption rate (% teams using the platform)
- Time to first deploy for a new service (hours, not weeks)
- Developer NPS / satisfaction
- Number of incidents the platform prevented
- Cost saved through standardization

## Interview Prep

**Mid**: "What's an Internal Developer Platform?"

**Senior**: "We have an IDP that no one uses. How do you fix it?"
- Diagnose: usually product-market fit issue. Interview engineers, find their actual pain, ship one strongly-adopted golden path, expand.

**Staff**: "Design an IDP from scratch for a fintech startup at 80 engineers, projecting to 300."

## Reading

- *Team Topologies* — Chapters on platform teams
- *Internal Developer Platforms* — Various blogs (Humanitec)
- Spotify's Backstage blog

## Next Topic

→ [T04 — Cloud Engineer / Infrastructure Engineer](T04-Cloud-Engineer.md)
