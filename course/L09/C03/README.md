# L09/C03 — Multi-Cloud Strategy

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Workload-Placement.md) | Choosing Workload Placement | 1 hr |
| [T02](T02-Cross-Cloud-Connectivity.md) | Cross-Cloud Connectivity | 1 hr |
| [T03](T03-Cross-Cloud-IAM.md) | Cross-Cloud IAM Federation | 0.5 hr |
| [T04](T04-Data-Gravity.md) | Data Gravity & Egress Cost Traps | 1 hr |

## Workload Placement Criteria

| Factor | Drives Decision |
|---|---|
| Latency to users | Pick closest cloud + region |
| Data residency | Sovereign clouds, specific regions |
| Compliance | FedRAMP, HIPAA, etc. — varies by cloud/region |
| Service availability | Some services unique (BigQuery, Spanner) |
| Cost | Egress dominates; compute varies |
| Existing investment | M365 → Azure, enterprise license bundles |
| Team expertise | Hire-pool considerations |
| Vendor relationships | Discounts, support |

## Anti-Patterns

- **"Avoid lock-in via abstraction"** — pay for the abstraction; lose cloud-specific features
- **"Use each cloud's best service"** — sounds smart, costs operational overhead
- **"True portability"** — rare in practice; most apps tied to cloud-specific managed services
- **"Multi-cloud DR"** — usually multi-region same-cloud is cheaper and simpler

## When Multi-Cloud Is Right

- **Acquired companies** — inherited multi-cloud
- **Compliance** — data sovereignty requirements
- **Specific unique service** — BigQuery, Spanner, Lambda@Edge
- **Geographic gaps** — provider weak in a region
- **Customer requirement** — buyers demanding their cloud
- **Internal/external split** — internal on private, external on public

## Cross-Cloud Connectivity

### Site-to-Site VPN
- IPSec tunnels between clouds
- Slow, less reliable than dedicated
- Cheapest

### Dedicated Interconnect
- AWS Direct Connect + Azure ExpressRoute + GCP Interconnect meeting in a colocation
- Lower latency, dedicated bandwidth
- Expensive

### MegaPort / Equinix Fabric
- Software-defined fabric connecting clouds
- Provision via API
- Common for production multi-cloud

### Cloud-Native (rare)
- GCP-AWS Confidential Computing connection (rare patterns)
- Cross-cloud K8s clusters (Anthos)

## Cross-Cloud Identity

### Workforce
- **OIDC/SAML federated** — Okta/Auth0/Entra ID issues tokens, all clouds trust
- Most common pattern

### Workloads
- **OIDC federation** between clouds:
  - GCP workload calls AWS API: GCP issues OIDC token → AWS STS AssumeRoleWithWebIdentity
  - Azure workload calls AWS: Entra ID OIDC → AWS
  - GitHub Actions OIDC → any cloud
- No static keys

## Data Gravity

> "Data has gravity; apps gravitate to data."

Moving large datasets is expensive and slow. Once data is in one cloud's storage, moving it across clouds means:
- Egress costs ($0.09/GB AWS → Internet, etc.)
- Network time
- Re-ingest costs (some services)

### Strategies
- Keep data + compute co-located
- Replicate selectively (not entire datasets)
- Aggregate before transfer (compute summaries; ship summaries)
- Use cloud-native data movement tools (AWS DataSync, Azure Data Box, gsutil)

### Egress Cost Examples (per GB, 2025)
- AWS Internet egress: $0.09 (first 10TB)
- Azure Internet egress: $0.087
- GCP Internet egress: $0.12
- AWS to AWS cross-region: $0.02
- Cloudflare R2: $0 egress (intentional disruption play)

A 100TB dataset moving cross-cloud: ~$9,000 just in egress.

## Cost Comparison Across Clouds

For a baseline 8-vCPU 32GB VM (m6i / D8s / n2):
- On-demand: AWS ~$0.40/hr; Azure ~$0.40/hr; GCP ~$0.39/hr
- 3-yr SP/RI: ~$0.14/hr all clouds

For object storage (Standard):
- AWS S3: $0.023/GB-mo
- Azure Blob: $0.018-0.0184
- GCP GCS: $0.020

For egress:
- All similar ~$0.087-0.12/GB
- Cloudflare R2 / Backblaze B2 / Wasabi: low or no egress (disruptors)

Prices vary; the **range is small** across hyperscalers. Differences come from service-specific pricing and FinOps practice.

## Practical Hybrid Architecture

```
Primary cloud: AWS (your main investment)
Specific service: BigQuery on GCP
   ↓
Federated IAM (Okta SSO + OIDC tokens)
Cross-cloud connectivity: MegaPort 1Gbps
Data: aggregate in AWS, ship daily summary to GCP for BigQuery analytics
Monitoring: Datadog (cloud-agnostic SaaS)
Logging: ship from both to S3, query via Athena
```

## Interview Themes

- "When multi-cloud is the right call"
- "Walk me through cross-cloud identity federation"
- "Data gravity — what does it mean?"
- "Hidden costs of multi-cloud"
- "Design a hybrid that uses BigQuery from AWS infra"
