# L30 — Capstone Projects & Portfolio

## Overview

A portfolio that proves your skills survives any interview. This lecture walks through 5 capstone projects that exercise the entire course. Build them. Publish them. Talk about them.

**6 chapters, 24 topics.**

## Chapter Map

### [C01](C01/) — Project 1: End-to-End CI/CD Platform
- T01 Architecture
- T02 IaC for Underlying Infra
- T03 Jenkins/GitHub Actions + ArgoCD
- T04 Observability Stack
- T05 Security Gates

### [C02](C02/) — Project 2: Multi-Region Kubernetes Platform
- T01 Cluster Topology
- T02 Federation / Multi-Cluster Service Mesh
- T03 Cross-Region Failover

### [C03](C03/) — Project 3: Production-Grade Observability Stack
- T01 Prometheus + Thanos
- T02 Loki + Grafana
- T03 OTel Collector Fleet

### [C04](C04/) — Project 4: Internal Developer Platform (Backstage)
- T01 Service Catalog
- T02 Golden Path Templates
- T03 Self-Service Provisioning

### [C05](C05/) — Project 5: Cost-Optimized Spot-Heavy Workload Platform
- T01 Karpenter + Spot
- T02 Graceful Spot Interruption Handling
- T03 Cost Dashboards

### [C06](C06/) — Portfolio Presentation
- T01 Public Repos & READMEs
- T02 Blog Posts as Proof of Depth
- T03 Conference Talks / Lightning Talks
- T04 Open Source Contributions That Matter

## Project 1: CI/CD Platform

**Outcome**: A working pipeline that builds, tests, scans, signs, deploys, and observes a sample app on a real cloud.

### Stack
- AWS account ($30/month budget)
- EKS cluster (Karpenter-managed)
- ArgoCD for GitOps
- GitHub Actions for CI
- Trivy + Cosign for image scan + sign
- Prometheus + Grafana
- Sample app (Go service with /healthz, /metrics)

### Demo Artifacts
- Repo with code + manifests + IaC
- Public dashboard screenshots
- One-page README explaining design
- 5-min Loom walkthrough

## Project 2: Multi-Region K8s Platform

**Outcome**: Two EKS clusters in two regions, with Argo CD managing both, service mesh (Istio multi-cluster), failover via Route 53.

### Demo
- Live failover demo (kill a region, traffic shifts)
- Cross-region service-to-service mTLS
- Observability federated

## Project 3: Observability Stack

**Outcome**: A Prometheus + Thanos + Loki + Tempo stack with sample apps generating metrics, logs, traces. Correlation working via OTel.

### Demo
- A Grafana dashboard showing all three pillars correlated via exemplars
- Burn-rate alerts firing on injected SLO failures

## Project 4: Internal Developer Platform

**Outcome**: A Backstage instance with golden-path template that scaffolds a new service (repo, CI, manifests, dashboards) in < 10 min.

### Demo
- "Create a new service" recording from click to running
- Service catalog with multiple services tracked

## Project 5: Spot + Karpenter Cost-Optimized

**Outcome**: K8s workloads running mostly on spot, with graceful interruption handling, cost dashboards via OpenCost.

### Demo
- Cost dashboard before/after Karpenter
- Disruption test (kill instances) showing graceful drain
- Mix of spot + on-demand fallback

## Portfolio Format

### GitHub READMEs Should Have
- Architecture diagram
- Outcome statement
- Tech stack
- How to run it
- What you learned
- What you'd do next

### Blog Posts
Topics that demonstrate depth:
- "What I learned operating Prometheus at 5M samples/sec"
- "Decoupling Kubernetes cluster lifecycle from workloads"
- "A FinOps program at 50 engineers"
- "Migrating a 100-service estate from EC2 to EKS"

### Conference Talks
Start with internal brown bags or local meetups (DevOps Day, CNCF). Build to KubeCon, SREcon, AWS re:Invent.

### Open Source Contributions That Matter

- Fix bugs in tools you use (Prometheus, K8s, Terraform providers)
- Improve docs (high-impact, lower bar)
- Maintain a small tool that other engineers use
- Avoid: drive-by typo fixes that don't show depth

## Course Closing

You've finished the entire course. The next steps:

1. Pick weak areas, deepen them
2. Build at least one capstone
3. Mock interview at least 5 times
4. Apply to roles where you'd want to work
5. Negotiate
6. Continue learning — this field never stops

## What Excellent Looks Like at Each Level

| Level | Demonstration |
|---|---|
| L5 (Senior) | You ship a working capstone; you can answer hard interview questions confidently. |
| L6 (Staff) | You influence multiple teams; you've published artifacts; you can architect across domains. |
| L7 (Principal) | You define technical strategy for a BU; you're a known person in your domain; you mentor staff engineers. |

## Final Reading List

- *Site Reliability Engineering* — Google (re-read)
- *Designing Data-Intensive Applications* — Kleppmann (re-read)
- *Staff Engineer* — Larson
- *The Staff Engineer's Path* — Reilly
- *Software Engineering at Google* — Winters et al.
- *An Elegant Puzzle: Systems of Engineering Management* — Larson (for the next career step)

## End

Good luck. Build well. Operate kindly.
