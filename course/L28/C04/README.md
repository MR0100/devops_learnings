# L28/C04 — Real-World System Designs

## Topics

- **T01 Design a CI/CD Platform** — Build, test, deploy
- **T02 Design a Multi-Region Kubernetes Platform** — Cross-region K8s
- **T03 Design a Metrics / Logging Pipeline at Scale** — Observability at scale
- **T04 Design a Secrets Management Platform** — Vault-like
- **T05 Design a Global Load Balancer** — Anycast + L4/L7
- **T06 Design Netflix's Deployment Platform** — Spinnaker-style
- **T07 Design an Internal Developer Platform** — Backstage-style

## Design 1: CI/CD Platform

### Requirements
- 1000+ engineers, ~10K builds/day
- Multi-language (Go, Python, Node, Java, Rust)
- Multi-cloud (AWS primary; some GCP)
- Sub-30-min commit → prod for SLA
- Audit trail (compliance)

### Architecture
```
[GitHub] ──webhook──→ [Webhook receiver]
                              ↓
                       [Pipeline scheduler]
                              ↓
              ┌──────────────┴──────────────┐
              ↓                              ↓
       [Ephemeral runners on K8s]    [Build cache (S3 / OCI)]
              ↓
       [Image registry]
              ↓
       [Deploy: ArgoCD]
              ↓
       [Multi-region K8s]
       [Observability: built-in]
```

### Key Decisions
- Self-hosted runners (cost + speed)
- Karpenter + spot for runner cost
- Image build cache (BuildKit cache mounts)
- ArgoCD for GitOps deploy
- Pipeline definition: YAML in repos

### Reliability
- Multi-AZ scheduler
- DLQ for failed builds
- Auto-retry transient failures
- Audit: webhook events + run logs to S3

### Scale Math
- 10K builds/day → ~7/min average; peak 30/min
- Each build 5 min avg = 50 builds parallel needed
- Buffer for spikes: ~200 concurrent capacity
- Karpenter scales 0 → 200 spot nodes in 60s

## Design 2: Multi-Region K8s Platform

### Requirements
- 3 regions (us-east-1, eu-west-1, ap-south-1)
- Tier-1 services in all 3 active
- Failover within minutes on region loss
- Centralized auth + observability

### Architecture
```
[Route 53 latency policy] → routes to nearest region

Per region:
[ALB] → [EKS] → [Aurora Regional]
                   ↑ writes
                   ↓ reads
       [Aurora Global Database — cross-region replica]

Cross-region:
[Global service mesh: Cilium ClusterMesh / Istio multi-cluster]
[Backstage service catalog: central]
[Observability: Mimir + Loki + Tempo, cross-region]
```

### Key Decisions
- Each region full stack (active-active)
- Aurora Global for primary write region; failover with promotion
- mTLS via service mesh
- Centralized observability fed from regions
- Configuration via GitOps (ArgoCD per cluster)

### Failover
- Route 53 health check fails → traffic shifts
- Aurora regional promotion if write region lost (manual)

### Scale Math
- Each region: 50% of peak (so loss of one = remaining absorb 1.5×)
- 30% headroom at steady state per region
- 100K req/s total → ~35K/region

## Design 3: Metrics Pipeline at Scale

### Requirements
- 50K services × ~100 metrics × 10s scrape = 5M samples/sec
- 7-day hot retention; 2-year cold
- Multi-region (low query latency)

### Architecture
```
Apps + exporters
   ↓ scrape (per-cluster)
[Prometheus per cluster]
   ↓ remote_write
[Mimir Receiver tier (multi-tenant)]
   ↓
[Mimir Ingester]
   ↓ flush
[S3 hot tier]
   ↓
[Compactor]
   ↓
[S3 cold tier]

Query path:
[Grafana] → [Mimir Querier] → ingesters + S3
```

### Key Decisions
- Push (remote_write) not pull at this scale
- Mimir for multi-tenancy + horizontal scale
- S3 for cheap retention
- Cardinality limits per tenant (prevent blast)

### Scale
- 5M samples/sec → ~50 ingesters
- Each ingester ~100K samples/sec capacity
- S3 storage: ~5 TB/day raw → 50 TB compressed after compaction
- 2-year retention: ~10 PB cold

### Failure Modes
- Ingester crash → write redundancy (replication factor 3)
- S3 outage → queue writes
- Cardinality explosion → reject + alert tenant

## Design 4: Secrets Management Platform

### Requirements
- 1000+ apps need secrets
- Rotation (DB creds, API keys)
- Audit log (compliance)
- Workload identity (no static keys)

### Architecture
```
[Apps/Pods]
   ↓ workload identity (K8s SA + OIDC)
[Vault Server (3-node HA)]
   - Auth (K8s, OIDC, AWS IAM)
   - Secrets engines (KV, DB, AWS, PKI)
   - Audit (to S3)
   ↓
[Storage backend (Consul / Integrated Raft)]
[Auto-unseal via KMS]
```

### Key Decisions
- Vault for dynamic secrets (DB creds on demand)
- Workload identity (no shared service accounts)
- Audit log mandatory + tamper-evident
- KMS for auto-unseal (no manual unseal at startup)

### Reliability
- 3 Vault nodes (Raft quorum)
- KMS in different account / region
- DR cluster (Vault DR replication)
- Audit log to S3 with Object Lock

### Scale
- ~10K req/s capacity per Vault node
- Cache lease info at app side
- Replica for read scaling (Vault Enterprise)

## Design 5: Global Load Balancer

### Requirements
- Global users
- Sub-50ms RTT
- Failover within seconds
- DDoS protection

### Architecture
```
[Client]
   ↓ Anycast IP
[Edge PoP (one of 300+ globally)]
   - L4 LB
   - L7 LB (HTTPS termination, WAF, rate limit)
   - Cache for static
   ↓ backbone
[Regional origin (3 regions)]
   ↓
[App + DB per region]
```

### Key Decisions
- Anycast for fast failover
- L7 at edge (WAF, auth, routing)
- Cache aggressively at edge
- Origin shield reduces origin load

### Scale
- Each PoP: ~10K req/s
- Total across PoPs: 3M req/s
- Bandwidth: 30 Gbps+ per PoP

### Failover
- PoP failure: BGP withdraws prefix; routes elsewhere
- Region failure: edge routes to surviving region

## Design 6: Internal Developer Platform (Backstage)

### Requirements
- 500 services across 50 teams
- Self-service: create new service, deploy, observe
- Golden paths for common service types
- Standardized observability, security, cost

### Architecture
```
[Backstage UI]
   ├── Service Catalog
   ├── Templates (golden paths)
   ├── Plugins (cost, observability, alerts)
   └── User mgmt

   ↓ creates resources
[Templates] generate:
   - Git repo
   - CI/CD pipeline
   - K8s manifests
   - Observability dashboards
   - Runbook

   ↓ APIs
[Crossplane / Terraform Cloud]
   - Provision AWS resources from K8s API

[ArgoCD / Flux] for deploy

[Observability stack] auto-instrumented
```

### Key Decisions
- Backstage as portal
- Templates encode standards
- Crossplane for cloud resource provisioning
- ArgoCD for deploy
- All paved-road; opt out requires justification

### Scale
- 500 services in catalog
- 50 teams use platform
- Time to first deploy for new service: < 1 day

## Interview Approach

Use this framework for any prompt:
1. Clarify requirements (5 min)
2. Estimate capacity (5 min)
3. High-level design (10 min)
4. Deep dive on 2-3 risky components (15 min)
5. Reliability + monitoring + scale (5 min)

Drive. Make decisions. Defend with tradeoffs.

## Interview Themes

- "Design X" (pick one from above)
- "How would you scale Y?"
- "What if traffic 10x?"
- "Failure mode of Z?"
- "Trade off A vs B"
