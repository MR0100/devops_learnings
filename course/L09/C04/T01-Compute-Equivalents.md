# L09/C04/T01 — Compute Equivalents

## Learning Objectives

- Map compute services across clouds
- Choose equivalents quickly

## VM

| Service | AWS | GCP | Azure |
|---|---|---|---|
| VM | EC2 | Compute Engine (GCE) | Virtual Machine |
| ASG | Auto Scaling Group | Managed Instance Group (MIG) | VM Scale Set (VMSS) |
| Spot | EC2 Spot | Spot VM | Spot VM |
| Reserved | RI / Savings Plan | Committed Use | Reserved Instance |

## Container

| Service | AWS | GCP | Azure |
|---|---|---|---|
| K8s | EKS | GKE | AKS |
| K8s + serverless | Fargate-on-EKS | GKE Autopilot | AKS Virtual Node |
| Container service | ECS | (none direct) | Container Apps |
| Serverless container | Fargate / App Runner | Cloud Run | Container Apps |
| One-off container | ECS task | Cloud Run jobs | Container Instance (ACI) |

## Functions / FaaS

| Service | AWS | GCP | Azure |
|---|---|---|---|
| Functions | Lambda | Cloud Functions (Gen 2) | Functions |
| Edge | Lambda@Edge | (Cloudflare Workers) | (Front Door rules) |
| Workflows | Step Functions | Workflows | Logic Apps / Durable Funcs |

## PaaS

| Service | AWS | GCP | Azure |
|---|---|---|---|
| PaaS web | Elastic Beanstalk | App Engine | App Service |
| Lift containers | App Runner | Cloud Run | Container Apps |

## HPC / Batch

| Service | AWS | GCP | Azure |
|---|---|---|---|
| Batch | AWS Batch | Cloud Batch | Azure Batch |
| HPC | ParallelCluster | (custom) | CycleCloud |

## VM Sizes

### Burstable
- AWS: t3, t4g
- GCP: e2 (with some burst)
- Azure: B-series

### General Purpose
- AWS: m6i, m7i
- GCP: n2, n2d
- Azure: D-series

### Compute Optimized
- AWS: c6i, c7i, c7g
- GCP: c3, c3d
- Azure: F-series

### Memory Optimized
- AWS: r6i, x2, u-instances (huge)
- GCP: m1, m3, m4
- Azure: E, M-series

### GPU
- AWS: p4, p5, g5
- GCP: a2, a3
- Azure: NC, ND

### ARM
- AWS: m7g, c7g (Graviton)
- GCP: t2a, c4a (Axion)
- Azure: Dpls v5 (Ampere), Cobalt 100

## Spot Discounts

| | Discount | Eviction |
|---|---|---|
| AWS Spot | 70-90% | 2-min warning |
| GCP Spot | 60-91% | 30s warning |
| Azure Spot | varies | 30s warning |

For: stateless, batch.

## Commit Discounts

| | Term | Discount |
|---|---|---|
| AWS RI | 1y, 3y | 30-60% |
| AWS Savings Plan | 1y, 3y | 30-72% |
| GCP Committed Use | 1y, 3y | 30-70% |
| Azure Reserved | 1y, 3y | 30-72% |
| Azure Savings Plan | similar | similar |

For: stable workloads.

## K8s Comparison

### Control Plane
| | Free | Paid SLA |
|---|---|---|
| EKS | $0.10/hr | (always paid) |
| GKE | first zonal free | $0.10/hr Standard |
| AKS | free | $0.10/hr Uptime SLA |

### Autoscaler
- EKS: Karpenter (recommended) or Cluster Autoscaler
- GKE: Cluster Autoscaler (native); Autopilot (no node mgmt)
- AKS: Cluster Autoscaler

### Workload Identity
- EKS: IRSA
- GKE: Workload Identity
- AKS: Workload Identity

### Networking
- EKS: VPC CNI (Pod = IP in VPC); other CNIs supported
- GKE: GKE CNI or Alias IP
- AKS: Azure CNI / Kubenet (legacy) / Azure CNI Overlay

## Serverless Containers

### Cloud Run (GCP)
- Scale to 0
- Per-request billing
- Most mature

### App Runner (AWS)
- Simpler
- Similar concept
- Less mature

### Container Apps (Azure)
- Built on KEDA
- Dapr integration
- Strong DX

For: greenfield serverless: Cloud Run mature; AWS / Azure catching up.

## Functions Maturity

- Lambda: most languages, most features
- Cloud Functions Gen 2: built on Cloud Run; good
- Azure Functions: many bindings, durable functions

All viable.

## Comparison Quirks

### EC2 Storage
- Instance store: ephemeral, fast
- EBS: persistent, mounted

### GCE Storage
- Local SSD: ephemeral, fast
- PD: persistent

### Azure VM Storage
- Temp disk: ephemeral, fast
- Managed disk: persistent

Concept similar; names different.

## Boot Time

| | Boot | Notes |
|---|---|---|
| EC2 (Linux) | 30-60s | Fast |
| GCE (Linux) | 30-60s | Fast |
| Azure VM | 60-120s | Slower historically |
| AWS Fargate | 30-60s | |
| Cloud Run | 1-3s | Cold start ~100ms warm |
| Lambda | 100ms-2s | Cold start matters |
| Functions (Az) | 100ms-2s | |

## Pricing Comparison

For small workload (1 vCPU, 4 GB RAM):
- AWS t3.medium: ~$30/mo on-demand, $11/mo 3y RI
- GCP e2-medium: ~$25/mo, $8/mo 3y commit
- Azure B2s: ~$30/mo, $11/mo 3y RI

Roughly similar; check current.

## When Each Compute

### GKE Autopilot
- Don't want to manage nodes
- Per-pod billing fine
- K8s-comfortable team

### Cloud Run
- HTTP service
- Scale to 0 desired
- Stateless

### Lambda
- Event-driven
- Many triggers
- Short tasks

### Fargate
- ECS or EKS without nodes
- Per-task billing

### App Service
- Web app
- Azure ecosystem
- Quick setup

## Best Practices

- Match VM size to actual usage (right-size)
- Commit for steady-state
- Spot for batch / stateless
- Autoscaler tuned
- ARM where compatible (cost savings)
- Pick managed service over self-host

## Common Mistakes

- Over-provisioning (cost)
- Burstable for sustained CPU (slow)
- No commits (paying on-demand for stable)
- Wrong abstraction layer (Lambda for long-running)

## Quick Refs

```
VM: EC2 / GCE / Azure VM
K8s: EKS / GKE / AKS
Serverless container: App Runner / Cloud Run / Container Apps
Functions: Lambda / Cloud Functions / Functions
```

## Interview Prep

**Junior**: "Map compute services."

**Mid**: "When each compute model."

**Senior**: "K8s flavor differences."

**Staff**: "Compute strategy across clouds."

## Next Topic

→ [T02 — Storage Equivalents](T02-Storage-Equivalents.md)
