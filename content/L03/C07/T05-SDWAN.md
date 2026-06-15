# L03/C07/T05 — SD-WAN

## Learning Objectives

- Understand what SD-WAN solves
- Recognize vendor landscape
- Know cloud-native alternatives

## What SD-WAN Is

Software-Defined Wide Area Network. Orchestrates branch-to-cloud connectivity with software policies.

Traditional WAN:
- MPLS circuits (expensive, slow to provision)
- Each branch a private link to HQ/cloud
- Manual config per device

SD-WAN:
- Overlay over various underlay (MPLS, Internet, LTE, 5G)
- Centralized policy control plane
- Application-aware routing
- Provisioning via API

## Components

- **Edge devices**: at each branch
- **Controller**: central policy + orchestration
- **Analytics**: visibility into traffic patterns

## Why Adopt

- **Cost**: cheaper Internet links instead of expensive MPLS
- **Agility**: provision new branches in days, not months
- **Performance**: app-aware routing (Office365 over best path)
- **Resilience**: dynamically switch underlay on failure
- **Security**: integrated NGFW, ZTNA

## Vendor Landscape

| Vendor | Strengths |
|---|---|
| Cisco (Viptela, Meraki) | Enterprise; well-integrated |
| Aruba (Silver Peak) | Strong WAN optimization |
| Versa | Best-of-breed independent |
| VMware VeloCloud | Cloud-native; Broadcom now |
| Fortinet | Security + SD-WAN |
| Palo Alto Prisma | SASE focus |
| Cato Networks | SASE single-vendor |

## Cloud-Native Equivalents

- **AWS Cloud WAN**: AWS-managed global WAN
- **Azure Virtual WAN**: Microsoft's
- **GCP NCC (Network Connectivity Center)**: Google's

These offload SD-WAN responsibilities to cloud provider.

## SASE (Secure Access Service Edge)

SD-WAN + cloud-delivered security:
- ZTNA (zero trust network access)
- CASB (cloud access security broker)
- SWG (secure web gateway)
- FWaaS

Replaces traditional perimeter:
- User connects to SASE provider (Zscaler, Cato, etc.)
- All security applied in cloud
- Then to destination

## Why It Matters for DevOps

For branch-heavy companies:
- Cloud connectivity from each branch
- App performance from anywhere
- Backup paths for outages

For cloud-only companies: not directly relevant; you're already on Internet + cloud.

## Hub-and-Spoke vs Mesh

### Hub-and-Spoke
- Each branch connects to HQ/cloud
- Simpler config
- Traffic between branches goes through hub

### Mesh
- Branches connect directly
- Better latency
- More complex (n^2 connections)

SD-WAN can be either, dynamically.

## Application Identification

SD-WAN identifies apps by signature/DPI:
- Office365, Salesforce, Zoom
- Routes based on app SLA needs
- E.g., voice over private MPLS, bulk over Internet

## Failover Modes

- **Active/passive**: primary link; switch on fail
- **Active/active**: load balance across links
- **App-aware**: each app picks best link

## Common Architectures

### Branch
```
Branch
├── Internet (broadband)
├── LTE (backup)
└── (sometimes) MPLS

→ SD-WAN edge device
→ Encrypted tunnel to nearest cloud PoP
→ Centralized security
→ Apps (cloud or internal)
```

## SD-WAN vs VPN

| | SD-WAN | VPN |
|---|---|---|
| Setup | Vendor managed | DIY |
| App awareness | Yes | No |
| Multi-link | Native | DIY |
| Cost | Subscription | Per-tunnel |
| Visibility | Excellent | Basic |

For small offices: site-to-site VPN. For enterprises: SD-WAN.

## When You Care About SD-WAN

- Enterprise with 10+ branches
- Hybrid cloud + on-prem
- Office365 / Salesforce / SaaS-heavy
- Cost-conscious replacing MPLS
- Need centralized security

For cloud-native DevOps: indirectly. Your apps in cloud; users' SD-WAN affects user experience.

## Cloud WAN (AWS)

AWS Cloud WAN manages multi-region + multi-account network as code:
- Core network (managed by AWS)
- Attached: VPCs, DX, Site-to-Site VPN, SD-WAN connect
- Policy as JSON

```hcl
resource "aws_networkmanager_core_network" "main" {
  global_network_id = aws_networkmanager_global_network.main.id
  policy_document   = data.aws_networkmanager_core_network_policy_document.main.json
}
```

## Future

SASE is the convergence: SD-WAN + Zero Trust + cloud security. Single vendor delivering networking + security.

## Common Mistakes

- **Buying SD-WAN for a cloud-only shop** — if you have no branches, your apps already sit in the cloud on the Internet; SD-WAN solves a branch/WAN problem you don't have.
- **Ripping out MPLS overnight** — Internet underlays are best-effort; keep MPLS or a second carrier for latency-sensitive traffic until you've validated SLAs.
- **Skipping the security layer** — moving branch egress straight to the Internet without ZTNA/SWG/FWaaS (SASE) trades a hardened perimeter for an open one.
- **Single underlay "for simplicity"** — the whole point is multi-link resilience; one broadband link with no LTE/secondary defeats it.
- **Treating it as set-and-forget** — app-aware policies need tuning as SaaS endpoints and DPI signatures change; stale policies route traffic badly.

## Best Practices

- **Run at least two diverse underlays** per branch (broadband + LTE/5G, optionally MPLS) and let the SD-WAN steer per-application by SLA.
- Use **app-aware routing**: latency-sensitive (voice/Zoom) over the best/private path, bulk/backup over commodity Internet.
- Adopt **SASE** so branch security (ZTNA, SWG, CASB, FWaaS) is delivered in the cloud near the user rather than backhauled to a central firewall.
- For AWS-centric estates, evaluate **Cloud WAN / Virtual WAN / NCC** to manage the cloud side as policy-as-code instead of stitching tunnels by hand.
- **Centralize policy and monitoring** in the controller; the visibility/analytics is a primary reason to choose SD-WAN over DIY VPN.

## Quick Refs

| | SD-WAN | Site-to-Site VPN | MPLS |
|---|---|---|---|
| App awareness | yes (DPI) | no | no |
| Multi-link steering | native | DIY | n/a |
| Provisioning | API / days | per-tunnel | weeks–months |
| Cost | subscription + cheap links | per-tunnel | expensive circuits |
| Visibility | excellent | basic | carrier-dependent |
| Best for | 10+ branches, SaaS-heavy | a few small sites | legacy low-jitter needs |

Pick by scale: **few small offices → site-to-site VPN · enterprise with many branches → SD-WAN · branch-to-AWS specifically → Cloud WAN / DX / VPN depending on bandwidth and SLA.**

Topology: **hub-and-spoke** (simple, branch↔hub, inter-branch via hub) vs **mesh** (direct branch↔branch, lower latency, n² complexity) — SD-WAN can do either dynamically.

## Interview Prep

**Mid**: "What's SD-WAN?"

**Senior**: "Compare SD-WAN vs MPLS."

**Staff**: "Branch connecting to AWS — SD-WAN vs DX vs VPN?"

## Next Topic

→ [T06 — Load Balancing (L4 vs L7)](T06-Load-Balancing-L4-L7.md)
