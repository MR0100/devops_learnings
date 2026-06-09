# L01/C06/T03 — The NoOps Myth

## Learning Objectives

- Define what "NoOps" claims and why it's a myth
- Recognize where it sounds plausible (serverless, PaaS)
- Articulate the real shift behind the term

## The Claim

> With enough automation, serverless, and PaaS, you can eliminate Ops entirely.

## Why It's a Myth

Operations work doesn't disappear; it *moves*. Examples:

- **Lambda needs cold-start tuning, concurrency limits, and IAM trust** — that's ops
- **Heroku PaaS still needs scaling decisions, observability, security review** — that's ops
- **Managed Kubernetes needs node autoscaling tuning, version upgrades, addons management** — that's ops
- **Cloud DBs need backup verification, performance tuning, IAM auth** — that's ops

What gets eliminated is the *manual provisioning of low-level infrastructure*. What stays:

- Capacity planning
- Cost management
- Security configuration
- Incident response
- Performance tuning
- Reliability engineering

## Where NoOps Sounds Plausible

| Tech | Reduces | Doesn't Eliminate |
|---|---|---|
| Serverless | Server patching | Memory/timeout/concurrency tuning |
| PaaS | Infra setup | App-level observability, scaling rules |
| Managed K8s | Control plane mgmt | Workload reliability, costs |
| Vendor APIs | Integration | API rate limits, retries, monitoring |

## The Real Shift the Term Captures

The amount of operational work *per service* decreases dramatically. So:

- Smaller teams can operate more services
- Operations becomes more "engineering" (in code) than "administration"
- Specialists shift to platform engineering

But: **total ops work in the org goes UP** because product surface area grows. The visible ops shrinks per service; the total grows.

## The Realistic Posture

- "NoOps" = "less-Ops-per-service" + "more-Engineering-in-Ops"
- Companies that bought the NoOps myth and fired ops teams ended up rebuilding them as SRE or Platform
- Use serverless and PaaS strategically, but staff for operational expertise anyway

## Famous Cautionary Tales

- Companies that "went all-in on serverless" hit bill shock from concurrent invocations
- Companies on PaaS hit scaling cliffs at 100K users and discover they need infra engineering
- Companies on managed DBs hit performance issues they can't tune from the console

In every case, the operational work was *deferred*, not eliminated.

## Interview Prep

**Mid**: "What's wrong with NoOps?"

**Senior**: "A CFO says 'we should be all-serverless because then we don't need Ops engineers.' Respond."

**Staff**: "Design a serverless-heavy platform where ops cost is minimized. What ops capacity do you still need?"
- Capacity for: cost monitoring, IAM stewardship, observability platform, incident response, vendor escalation, security/compliance, platform engineering.

## Next Topic

→ [T04 — Cargo-Culting Practices](T04-Cargo-Culting.md)
