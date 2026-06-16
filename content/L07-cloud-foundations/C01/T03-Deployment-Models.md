# L07/C01/T03 — Public, Private, Hybrid, Multi-Cloud, Edge

## Learning Objectives

- Place deployment models on the spectrum
- Pick for context

## Public Cloud

Shared infrastructure; pay-as-you-go; APIs.

Examples: AWS, Azure, GCP, Oracle Cloud, IBM Cloud.

Used by: startups, modern enterprises, most workloads.

## Private Cloud

Cloud APIs and elasticity but in YOUR data center (or rented hardware).

Tools: OpenStack, VMware vSphere, Nutanix.

Used by: regulated (banks, govt), high-perf computing, large enterprises with existing DCs.

Pros: data residency, compliance, sometimes cheaper at scale.
Cons: you build/maintain everything. Most "private cloud" is just virtualization.

## Hybrid

Mix of private + public, connected:
- Critical/regulated data on-prem
- Burst capacity to public cloud
- New workloads in cloud; legacy on-prem

Tools: AWS Outposts, Azure Arc, Anthos. Bring cloud APIs to your DC.

Connectivity: VPN, Direct Connect, ExpressRoute.

## Multi-Cloud

Multiple public clouds.

Reasons:
- Avoid lock-in
- Best-of-breed per workload
- Compliance / regional
- M&A inheritance

Reality:
- Tooling 3× harder
- Skill 3× expensive
- Networking pricey (egress)
- Most "multi-cloud" is 1 primary + 1 backup

## Sky / Cross-Cloud

Idea: abstract cloud below your apps. Apps run on any cloud transparently.

Examples: K8s (run on EKS, GKE, AKS), Crossplane, OpenStack.

Reality: hardest in data, easiest in compute.

## Edge

Compute close to end users.

Layers:
- CDN edge POPs (CloudFront, Cloudflare, Fastly)
- Edge functions (CF Workers, Lambda@Edge)
- Telco edge (5G MEC: AWS Wavelength, Azure Edge Zones)
- IoT gateways

Use cases:
- Low-latency (gaming, video)
- Privacy (process before sending up)
- Bandwidth (filter at source)
- Resilience (works if cloud down)

## Cloud Models Compared

| Model | Cost | Speed | Compliance | Lock-In |
|---|---|---|---|---|
| Public | Variable | Fastest | Easy with shared resp | Per service |
| Private | High CapEx | Slow | Full control | Internal |
| Hybrid | Mixed | Medium | Granular | Mixed |
| Multi-Cloud | Highest mgmt | Slow | Cherry-pick | Less per service |
| Edge | Premium | Lowest latency | Distributed | Per provider |

## When Each

**Public alone**: startups, web/mobile apps, modern enterprises (default).

**Private alone**: HFT, secret data (defense), uniquely massive scale (FB, Google have their own).

**Hybrid**: large enterprises with existing on-prem, regulated industries (banks, healthcare).

**Multi-cloud**: lock-in averse, M&A combined orgs, compliance per region.

**Edge**: real-time apps, content delivery, IoT.

## Common Mistakes

### "Multi-cloud for resilience"
If app must run on both: doubles your code paths. Often, single-cloud with multi-region is cheaper and easier.

### "We need our own cloud"
Building > using. Usually a few years and tens of millions wasted; eventually move to AWS anyway.

### "Hybrid for slow migration"
Gets stuck. Two systems forever. Plan exit.

## Sovereignty

Govts increasingly require:
- Data in country
- Decryption keys with local entity
- No US legal access (GDPR, China Cybersecurity Law)

Drives:
- Sovereign clouds (Bleu in France, OVH)
- Region-locked services
- Customer-managed keys

## Carbon

Cloud vs on-prem footprint debate:
- Cloud usually cleaner (better PUE, renewable PPA)
- But variable (consumption tracking)

Tools: Cloud Carbon Footprint, AWS Customer Carbon Footprint Tool.

## Sovereign K8s

Run K8s wherever:
- On-prem (OpenShift, Rancher)
- Edge (K3s)
- Multi-cloud (EKS Anywhere, GKE Enterprise)

K8s as the abstraction → portability.

## Practical: My App

For a typical FAANGM-scale app:
- Primary cloud (AWS/Azure/GCP)
- Multi-region within
- CDN at edge
- Maybe failover DR cloud
- Specialized workloads on best-fit cloud (BigQuery for analytics; etc.)

NOT: spread evenly across 3 clouds.

## Best Practices

- Default to a single primary public cloud with multi-region for HA; reach for multi-cloud only when a concrete driver (compliance, M&A, best-of-breed) justifies the tooling and cost overhead.
- Treat hybrid as a deliberate end-state or a time-boxed migration with a defined exit — never an open-ended "we'll finish someday."
- Use Kubernetes/containers and open data formats as the portability layer so workloads can move without rewrites.
- Put latency-sensitive and bandwidth-heavy logic at the edge (CDN, edge functions) and keep the source of truth central.
- For sovereignty/residency, design with customer-managed keys and region-locked services from the start rather than retrofitting.
- Model egress and inter-cloud networking costs explicitly before adopting multi-cloud — they often dominate.

## Quick Refs

Deployment-model decision rule:

| Situation | Pick |
|---|---|
| Startup / modern web/mobile app (default) | Public, single cloud, multi-region |
| Strict data residency / regulated data | Private or hybrid with CMK |
| Existing on-prem to leverage during migration | Hybrid (time-boxed) |
| Avoid lock-in / best-of-breed per workload | Multi-cloud (1 primary + 1 secondary in practice) |
| Sub-50ms latency to global users / IoT | Edge |

Connectivity cheat sheet:

- On-prem ↔ AWS: **Direct Connect** (private) or Site-to-Site **VPN**
- On-prem ↔ Azure: **ExpressRoute** or VPN
- Cloud APIs in your DC: **AWS Outposts**, **Azure Arc/Stack**, **Anthos**

## Interview Prep

**Mid**: "Hybrid use case."

**Senior**: "Multi-cloud strategy — when justified."

**Staff**: "Cloud sovereignty for EU customers."

## Next Topic

→ [T04 — Regions, AZs, Edge Locations](T04-Regions-AZs.md)
