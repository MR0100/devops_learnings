# L07/C01/T01 — What Is "The Cloud" (Really)

## Learning Objectives

- Understand cloud beyond marketing
- Know the NIST definition

## NIST Definition

5 essential characteristics, 3 service models, 4 deployment models.

### Essential Characteristics
1. **On-demand self-service**: provision without human interaction
2. **Broad network access**: over standard protocols
3. **Resource pooling**: multi-tenant; abstracted location
4. **Rapid elasticity**: scale out / in fast
5. **Measured service**: pay for what you use

If a service has all 5, it's cloud. If missing any, it's just "hosted."

## Beyond the Marketing

Cloud is:
- **Someone else's computer**: physical servers somewhere
- **APIs over those servers**: provision via REST
- **Massive scale**: economies impossible solo
- **Programmable infrastructure**: code creates infrastructure (IaC)

Cloud is NOT magic. Servers exist. Networks exist. They fail.

## Cloud Layers

```
Application
  ↑
Container / Runtime
  ↑
OS
  ↑
Virtualization
  ↑
Physical hardware
  ↑
Power, cooling, building
```

Cloud abstracts layers below. IaaS exposes from VM up; PaaS exposes from app up.

## Why Cloud Won

- **Speed**: provision in seconds, not weeks
- **Elasticity**: scale to traffic
- **No CapEx**: pay monthly
- **Global**: deploy to 30+ regions instantly
- **Managed services**: outsource DB, queue, ML
- **Programmability**: APIs for everything

What it traded:
- **Cost**: at scale, often cheaper to own; cloud pricier
- **Lock-in**: AWS Lambda doesn't work on GCP
- **Latency**: data in different region = slow
- **Compliance**: must check provider's certs
- **Hidden costs**: egress, IOPS, requests

## When Cloud Loses

- Steady workload, big enough to own hardware
- Strict data residency (some govt / banking)
- Connectivity-sensitive (low-latency trading, factory floor)
- After massive scale (Dropbox famously moved off S3)

## Public Cloud Players

| Provider | 2025 Share | Strength |
|---|---|---|
| AWS | ~31% | Breadth, maturity |
| Azure | ~25% | Enterprise / Microsoft shops |
| GCP | ~11% | Data, AI, K8s |
| Alibaba | ~4% | China |
| Others | ~29% | Cloudflare, IBM, Oracle, smaller |

(Approximate; varies by source.)

For FAANGM interviews: AWS deepest; Azure/GCP also expected; multi-cloud knowledge bonus.

## Cloud-Native vs Cloud-Hosted

**Cloud-Hosted**: traditional app on VMs in cloud. Lift-and-shift.

**Cloud-Native**: built for elasticity, managed services, ephemeral compute. Containers, serverless, queues, etc.

Cloud-native fully exploits cloud benefits.

## Edge Cloud

Compute closer to users:
- CDN edge nodes (CloudFront, Cloudflare)
- Edge functions (Lambda@Edge, Cloudflare Workers)
- 5G MEC

Reduces latency; pushes processing close to data.

## Hybrid Cloud

On-prem + cloud, connected:
- VPN / Direct Connect
- AWS Outposts, Azure Arc, Anthos: cloud APIs on your hardware
- Common scenarios: legacy systems, regulated data on-prem; new workloads in cloud

## Multi-Cloud

Using multiple clouds. Reasons:
- Avoid lock-in
- Use best-of-breed (BigQuery for analytics; Lambda for serverless)
- Compliance (data per region)
- Negotiating leverage

Costs:
- Tooling 3× as complex
- Networking expensive (egress)
- Skills required
- Often not worth it

## The Cloud Stack Mental Model

For any service, ask:
1. What does provider manage?
2. What do I manage?
3. What's the cost model?
4. What's the SLA?
5. What's the lock-in?

## Cloud as API

Everything in cloud is an API call:
- Create VM: `aws ec2 run-instances ...`
- Allocate IP: API call
- Modify firewall: API call

This is why IaC works (Terraform = API calls in deterministic order).

## Quick History

- 2006: AWS S3, EC2 — birth of public cloud
- 2008: Google App Engine (PaaS)
- 2010: Azure
- 2011: GCP, Cloudflare
- 2014: AWS Lambda (serverless)
- 2014: Kubernetes (cloud-portable orchestration)
- 2020s: Edge compute, AI specialized infra

## Common Mistakes

- Equating "cloud" with "someone else's computer" — missing the on-demand, self-service, elastic, API-driven model that actually defines it (NIST).
- Treating cloud as automatically cheaper — at steady, predictable high scale, owned hardware is often cheaper; cloud wins on elasticity and speed, not always on raw cost.
- Lift-and-shift then expecting cloud-native benefits — rehosting a VM gives none of the autoscaling/managed-service upside; you pay cloud prices for on-prem architecture.
- Confusing hybrid and multi-cloud — hybrid = on-prem + cloud; multi-cloud = two or more public clouds. They solve different problems.
- Assuming edge = cloud region — edge is geographically distributed compute close to users; it complements, not replaces, central regions.
- Ignoring egress and inter-AZ data charges — the "infinite scale" story hides per-GB network costs that dominate data-heavy workloads.

## Best Practices

- Adopt cloud for the elasticity, managed services, and speed-to-market — not as a 1:1 datacenter replacement.
- Build cloud-native (managed DBs, autoscaling, IaC) rather than cloud-hosted (VMs you babysit) when you want the real upside.
- Model cost early: small/spiky/uncertain → cloud; large/steady/predictable → revisit owned or reserved capacity.
- Use hybrid deliberately (latency-sensitive or regulated workloads on-prem, burst/elastic in cloud), not as an accident of migration.
- Treat infrastructure as software — everything via API/IaC so it is reproducible, reviewable, and disposable.
- Keep an exit/portability story in mind from day one (data formats, containerized workloads) before lock-in becomes expensive.

## Quick Refs

The 5 NIST essential characteristics (interview gold):

| Characteristic | Meaning |
|---|---|
| On-demand self-service | Provision without human interaction (API/console) |
| Broad network access | Reachable over standard networks/protocols |
| Resource pooling | Multi-tenant; provider abstracts physical location |
| Rapid elasticity | Scale out/in quickly, often automatically |
| Measured service | Metered, pay-per-use billing |

Deployment-model decision rule:

| Need | Model |
|---|---|
| Default, fastest, most managed services | Public cloud |
| Strict data residency / regulatory control | Private or hybrid |
| Burst from datacenter into cloud | Hybrid |
| Avoid single-vendor risk / best-of-breed | Multi-cloud |
| Low latency near end users | Edge |

## Interview Prep

**Junior**: "What is cloud computing?"

**Mid**: "When NOT to use cloud?"

**Senior**: "Hybrid vs multi-cloud — tradeoffs."

**Staff**: "Cloud vendor strategy for $1B company."

## Next Topic

→ [T02 — IaaS vs PaaS vs SaaS vs FaaS](T02-IaaS-PaaS-SaaS.md)
