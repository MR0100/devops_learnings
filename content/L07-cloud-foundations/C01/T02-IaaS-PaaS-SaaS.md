# L07/C01/T02 — IaaS vs PaaS vs SaaS vs FaaS

## Learning Objectives

- Place services on the abstraction spectrum
- Pick the right model

## The Stack

```
SaaS    Gmail, Slack, Workday
↑
FaaS    Lambda, Cloud Functions
↑
PaaS    Heroku, App Engine, Cloud Run
↑
CaaS    ECS, EKS, GKE
↑
IaaS    EC2, GCE, Azure VM
↑
On-Prem Bare metal
```

Higher = more managed by provider; less control; less work for you.

## IaaS — Infrastructure as a Service

You get: VMs, virtual networks, storage volumes.

You manage: OS, runtime, app.

Examples: EC2, GCE, Azure VM.

When: legacy lift-and-shift, custom OS/kernel, low-level control needed.

Pros:
- Maximum flexibility
- Familiar (same as on-prem)
- Run anything

Cons:
- You patch OS
- You scale manually (or via ASG)
- You handle HA

## PaaS — Platform as a Service

You get: runtime (Java, Node, Python), deploy code.

You manage: code.

Examples: Heroku, Google App Engine, AWS Elastic Beanstalk, Azure App Service.

When: standard web apps; don't want to manage OS.

Pros:
- Just push code
- Auto-scale
- Built-in monitoring

Cons:
- Limited customization
- Specific runtime / lang versions
- Often opinionated (12-factor)
- Lock-in

## CaaS — Containers as a Service

Mid-tier: ECS, EKS, GKE, AKS, Fargate, Cloud Run.

You get: container runtime, orchestration.

You manage: container images, configs.

Sometimes considered PaaS; depends on definition.

## FaaS — Functions as a Service (Serverless)

You get: event triggers; compute runs your function.

You manage: function code.

Examples: AWS Lambda, GCP Cloud Functions, Azure Functions, Cloudflare Workers.

When: event-driven, sporadic, glue, webhooks.

Pros:
- True pay-per-execution
- Auto-scale to 0
- No infra mgmt at all

Cons:
- Cold starts (100ms-10s)
- Function size limits
- Execution time limit (15 min AWS)
- Stateless (need DB/cache)
- Lock-in (event triggers)
- Debugging harder

## SaaS — Software as a Service

You get: working application.

You manage: data, users, config.

Examples: Gmail, Salesforce, Slack, Datadog.

When: commodity functionality; don't build it.

Pros:
- Zero ops
- Often best-of-class
- Subscription

Cons:
- Expensive at scale
- Limited customization
- Data lives in vendor

## Visualizing What You Manage

| | App | Runtime | OS | VM | HW | Net |
|---|---|---|---|---|---|---|
| On-Prem | You | You | You | You | You | You |
| IaaS | You | You | You | Provider | Provider | Provider |
| CaaS | You | You | Provider | Provider | Provider | Provider |
| PaaS | You | Provider | Provider | Provider | Provider | Provider |
| FaaS | You (function) | Provider | Provider | Provider | Provider | Provider |
| SaaS | Provider | Provider | Provider | Provider | Provider | Provider |

## Pricing Sensitivity

| | Cost Model |
|---|---|
| IaaS | Per VM-hour |
| CaaS | Per pod-hour or vCPU/RAM |
| PaaS | Per instance-hour |
| FaaS | Per execution + ms (granular) |
| SaaS | Per seat, per month |

FaaS is cheapest for sporadic; expensive for steady high traffic. Math matters.

## Choosing

**IaaS** when:
- Legacy app
- Custom kernel
- Maximum control
- Already have OS expertise

**PaaS** when:
- Standard web app
- Small team
- Move fast
- Don't need custom OS

**FaaS** when:
- Event-driven
- Bursty traffic
- Glue code
- Webhooks

**SaaS** when:
- Commodity tool
- "Build vs buy" → buy
- Internal tooling

## Hybrid

Most apps mix:
- VMs for stateful (databases)
- K8s for stateless web tier
- Lambda for cron / event
- SaaS for monitoring / log

## Trends

Toward higher abstraction:
- 2006-2014: IaaS dominant
- 2014-2020: PaaS / containers rise
- 2020s: serverless mainstream
- Future: more managed; less plumbing

## Common Mistakes

- Picking IaaS by default and rebuilding what PaaS/managed services give for free — you end up maintaining OS patching, runtimes, and scaling yourself.
- Treating serverless (FaaS) as "always cheapest" — for steady high-throughput traffic the per-invocation price beats a constantly-running container/VM.
- Forgetting that "less to manage" means "less control" — FaaS/PaaS limit runtime versions, execution time, and tuning; some workloads simply don't fit.
- Ignoring cold starts and execution limits on FaaS (timeout caps, memory-linked CPU) when porting a long-running or latency-sensitive job.
- Conflating CaaS with PaaS — containers (CaaS) still leave you owning the image/runtime; PaaS abstracts the runtime away entirely.
- "Build vs buy" misjudged — writing a commodity tool in-house (IaaS/PaaS) when a SaaS exists wastes engineering time on undifferentiated work.

## Best Practices

- Choose the highest level of abstraction that still meets control/compliance needs — managed beats self-run unless you have a concrete reason.
- Mix models per workload: VMs for stateful legacy, containers for stateless web tiers, FaaS for event/cron glue, SaaS for commodity tooling.
- Do the cost math at expected scale before committing — FaaS for spiky/low volume, containers/VMs (with reserved/committed-use discounts) for steady high volume.
- Prefer managed databases/queues/caches over self-hosting on IaaS — operational toil and reliability favor the provider.
- Keep portability where it's cheap (containers, open data formats) and accept deeper lock-in only for high-leverage managed services.

## Quick Refs

Key distinctions — what *you* manage at each layer:

| Model | You manage | Provider manages | Bills by |
|---|---|---|---|
| On-prem | Everything | Nothing | CapEx |
| IaaS | OS, runtime, app | Hardware, network, virtualization | VM-hour |
| CaaS | Container image, app | OS, orchestration plumbing | vCPU/RAM or pod-hour |
| PaaS | App code + config | Runtime, OS, scaling | Instance-hour |
| FaaS | Function code only | Everything else, scaling to zero | Per-invocation + ms |
| SaaS | Just your data/usage | The whole stack | Per seat/month |

Decision rule:

- Legacy app / custom kernel / max control → **IaaS**
- Standard web app, small team, move fast → **PaaS**
- Event-driven, bursty, glue/webhooks → **FaaS**
- Commodity capability you shouldn't build → **SaaS**

## Interview Prep

**Junior**: "PaaS vs IaaS."

**Mid**: "When use Lambda vs ECS?"

**Senior**: "Migrate VM app to serverless — approach."

**Staff**: "Cost model for 1M/day app: Lambda vs ECS."

## Next Topic

→ [T03 — Public, Private, Hybrid, Multi-Cloud, Edge](T03-Deployment-Models.md)
