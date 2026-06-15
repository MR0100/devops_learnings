# L07/C01 — Cloud Concepts

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-What-Is-Cloud.md) | What Is "The Cloud" (Really) | 0.5 hr |
| [T02](T02-IaaS-PaaS-SaaS.md) | IaaS vs PaaS vs SaaS vs FaaS | 1 hr |
| [T03](T03-Deployment-Models.md) | Public, Private, Hybrid, Multi-Cloud, Edge | 0.5 hr |
| [T04](T04-Regions-AZs.md) | Regions, Availability Zones, Edge Locations | 1 hr |

## What "The Cloud" Really Is

"The cloud" = someone else's computer, but with:
- Self-service provisioning (API/console)
- Pay-as-you-go
- Elastic scaling
- Managed services
- Global presence

NIST definition: on-demand network access to a shared pool of configurable computing resources.

## Service Models

```
Application       │  You manage   │ SaaS  PaaS  IaaS
Data              │  You manage   │ ----  You   You
Runtime           │  You manage   │ ----  ----  You
Middleware        │  You manage   │ ----  ----  You
OS                │  You manage   │ ----  ----  You
Virtualization    │  Provider     │ Prov  Prov  Prov
Servers           │  Provider     │ Prov  Prov  Prov
Storage           │  Provider     │ Prov  Prov  Prov
Networking        │  Provider     │ Prov  Prov  Prov
```

- **IaaS**: VMs, networks, storage (EC2, GCE, Azure VM)
- **PaaS**: managed runtime (App Engine, Heroku, Cloud Run, Beanstalk)
- **SaaS**: turnkey app (Gmail, Salesforce)
- **FaaS**: event-driven functions (Lambda, Cloud Functions)
- **CaaS**: containers as a service (ECS, GKE, AKS, Cloud Run)

## Deployment Models

| Model | Example | Use |
|---|---|---|
| Public | AWS, Azure, GCP | Default for most |
| Private | OpenStack, VMware on-prem | Compliance, sensitive |
| Hybrid | On-prem + cloud | Migration, burst |
| Multi-cloud | AWS + GCP | Cherry-pick services, avoid lock-in |
| Edge | CloudFront, Cloudflare | Low-latency users worldwide |
| Sovereign | EU-only, Gov | Compliance / data residency |

## Regions, AZs, Edge

```
Region (us-east-1)
├── AZ a (us-east-1a)  — one or more datacenters, independent power/network
│   ├── DC1
│   └── DC2
├── AZ b (us-east-1b)
└── AZ c (us-east-1c)
```

**AZs within a region**:
- ~1-2ms RTT between
- Independent power, cooling, network
- ≥100km between (typically)
- Used for high availability

**Across regions**:
- Tens to hundreds of ms RTT
- Independent failure domain
- Used for disaster recovery, geo-routing, compliance

**Edge / PoP**:
- Hundreds worldwide (CDN providers)
- Tens of ms from users typically
- Cache, edge compute, DDoS absorption

## Choosing Regions

Considerations:
- **Latency to users** — pick closest region
- **Compliance** — GDPR (EU), data sovereignty
- **Service availability** — some services don't exist everywhere
- **Cost** — varies by region (e.g., us-east-1 cheapest, sa-east-1 expensive)
- **Carbon** — Azure/GCP report grid carbon intensity per region

## Region Pair Concept

Azure: each region has a paired region (same continent typically) for DR.
AWS: customer chooses, no enforced pairing.
GCP: regions have multiple zones; global services span automatically.

## Why "Cloud" Was a Step Change

Before cloud:
- Months to provision a server
- CapEx for capacity for peak
- Geographic expansion = building a DC
- HA via specialized hardware

With cloud:
- Minutes to provision
- OpEx, pay for what you use
- Geographic expansion = API call
- HA via design (multi-AZ, multi-region)

## Interview Themes

- "Define IaaS, PaaS, SaaS, FaaS"
- "Difference between Region and AZ"
- "When multi-region?"
- "Why is sa-east-1 (São Paulo) more expensive?"
- "Hybrid cloud — when?"
