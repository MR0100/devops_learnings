# L28 — System Design for DevOps & Platform Engineers

## Overview

System design interviews decide the level you get hired at. This lecture covers the framework and walks through canonical platform/DevOps systems.

**6 chapters, 27 topics.**

## Chapter Map

### [C01](C01/) — System Design Framework
- T01 Functional vs Non-Functional Requirements
- T02 Capacity Estimation Math
- T03 The 4 Boxes (Client, App, Data, Infra)

### [C02](C02/) — Scalability Patterns
- T01 Horizontal vs Vertical
- T02 Sharding & Partitioning
- T03 Replication Patterns
- T04 CAP & PACELC

### [C03](C03/) — Reliability Patterns
- T01 Idempotency
- T02 Backpressure
- T03 Graceful Degradation

### [C04](C04/) — Real-World System Designs
- T01 Design a CI/CD Platform
- T02 Design a Multi-Region Kubernetes Platform
- T03 Design a Metrics / Logging Pipeline at Scale
- T04 Design a Secrets Management Platform
- T05 Design a Global Load Balancer
- T06 Design Netflix's Deployment Platform
- T07 Design an Internal Developer Platform
- T08 Design a Rate Limiter
- T09 Design a Distributed Queue / Job Scheduler
- T10 Design a Key-Value / Cache Store

### [C05](C05/) — Platform Engineering
- T01 What an IDP Actually Is
- T02 Golden Paths
- T03 Backstage for Service Catalog
- T04 Crossplane & Compositions

### [C06](C06/) — Tradeoff Discussions
- T01 Build vs Buy vs Open Source
- T02 Centralized vs Federated Platforms
- T03 Tool Sprawl Management

## The System Design Framework (35 min)

```
Min 0-5    Clarify requirements & scope
           - Functional (what)
           - Non-functional (scale, latency, availability)
           - Constraints (cost, compliance, team)

Min 5-10   Capacity estimation
           - DAU, QPS (peak), data growth, storage
           - Read:write ratio
           - Bandwidth

Min 10-15  High-level design (4 boxes)
           - Client → App → Data → Infra

Min 15-30  Deep dive on 2-3 components
           - Pick risky/interesting parts
           - Tradeoffs explicit (CAP, latency vs cost)

Min 30-35  Reliability, monitoring, scaling
           - SLOs, alerts
           - Failure modes
           - Multi-region if needed
```

## Latency Numbers Every Engineer Should Know

```
L1 cache reference            0.5 ns
Branch mispredict             5   ns
L2 cache reference            7   ns
Mutex lock/unlock            25   ns
Main memory reference       100   ns
Send 1KB over 1Gbps        10,000 ns =  10 μs
SSD random read            150,000 ns = 150 μs
Read 1 MB sequential SSD 1,000,000 ns =   1 ms
Round trip same DC         500,000 ns =  0.5 ms
HDD seek                10,000,000 ns =  10 ms
Read 1 MB sequential HDD 20,000,000 ns =  20 ms
Round trip CA → Netherlands  150 ms
```

## CAP and PACELC

**CAP**: under network partition, choose Consistency or Availability.
- CP: refuse writes when can't replicate (Zookeeper, etcd)
- AP: serve, reconcile later (DynamoDB eventual, Cassandra)
- CA: only without partition (single node)

**PACELC**: Even without partition, choose Latency vs Consistency.
- Postgres synchronous replication: PC/EC (consistent always, slow when partition)
- DynamoDB eventual: PA/EL (available always, eventual reads)

## Sample Design: Internal Developer Platform

### Requirements
- 1000 engineers, 50 product teams
- New service to production in < 1 day
- Self-service for: env provisioning, deploy, observability
- Standardized security, compliance

### Components
```
[Developer Portal (Backstage)]
        │
        ├─► [Service Catalog & Templates]
        ├─► [Provisioning API (Crossplane)]
        │       └─► AWS/K8s resources
        ├─► [CI/CD (GitHub Actions + ArgoCD)]
        ├─► [Observability stack (Prom + Grafana + OTel)]
        ├─► [Secrets (Vault + External Secrets)]
        └─► [Cost dashboards (Kubecost)]
```

### Golden Paths
- "Create a CRUD service" template scaffolds: repo, CI, manifests, dashboards, alerts, runbook
- All standard concerns pre-wired
- Engineers focus on business logic

## Sample Design: Global Metrics Pipeline

### Requirements
- 50K services × ~100 metrics × 10s scrape → 5M samples/sec
- Retention: 7d hot, 2y cold
- Multi-region, low query latency

### Architecture
```
Apps + Exporters
     │ Prometheus per cluster (scrape locally)
     │
     │ remote_write
     ▼
Receiver layer (Thanos Receive or Mimir)
     │
     ├──► Hot storage (S3 + in-memory cache)
     ├──► Cold storage (S3 Glacier)
     │
     └──► Querier (Grafana frontend)
```

### Tradeoffs
- Push (remote_write) vs Pull (federate) — push is more reliable at scale
- Compaction strategy
- Cardinality limits per team
- Multi-tenancy (Mimir supports natively)

## Recommended Reading

- *System Design Interview* — Alex Xu (Vol 1 & 2)
- *Designing Data-Intensive Applications* — Kleppmann (mandatory)
- "System Design Primer" GitHub repo
- *Software Engineering at Google* — Winters et al.

## Interview Themes

- "Design a CI/CD platform that handles 10K builds/day"
- "Design a metrics pipeline at Datadog scale"
- "Design a secrets management platform"
- "Design Netflix's deployment system"
- "Design Backstage from scratch"

## Next

→ [L29 — FAANGM Interview Mastery](../L29-interview-mastery/README.md)
