# L07/C04 — Compute Family

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-VMs.md) | VMs (EC2, Compute Engine, Azure VMs) | 1 hr |
| [T02](T02-Containers.md) | Containers (ECS, EKS, GKE, AKS, Fargate, Cloud Run) | 1 hr |
| [T03](T03-Serverless.md) | Serverless (Lambda, Cloud Functions, Azure Functions) | 1 hr |

## VMs Across Clouds

| | AWS EC2 | Azure VM | GCP GCE |
|---|---|---|---|
| Instance metadata | IMDSv2 (token-protected) | IMDS (token-protected) | metadata server |
| AMI / Image | AMI | Managed image / VHD | GCE image |
| Auto-scaling | ASG | VMSS | MIG |
| Spot | Spot Instances | Spot VMs | Spot VMs / Preemptible |
| Boot | EBS-backed | Managed disk | Persistent disk |
| Local disk | Instance store (ephemeral) | Temporary disk | Local SSD |

### Choosing an Instance Type (general)

| Need | Pick |
|---|---|
| Burstable, dev | T-series (AWS), B-series (Azure), E2 (GCP) |
| General | M-series, D-series, N1 |
| Compute-optimized | C-series, F-series, C2 |
| Memory-optimized | R/X-series, E-series, N2-HighMem |
| Storage I/O | I-series (NVMe local), D-series, M-series w/ local SSD |
| GPU | P/G-series, NC-series, A-series with accelerator |
| ARM (cheaper) | Graviton (m7g, c7g), Ampere Altra | T2A |

## Containers as a Service

```
                 Self-managed         Managed CP, your nodes      Fully serverless
                 ────────────         ─────────────────────       ────────────────
AWS              EC2 + Docker         ECS / EKS                    Fargate, App Runner
Azure            AKS self-managed     AKS                          Container Apps, ACI
GCP              GKE Standard         GKE                          GKE Autopilot, Cloud Run
```

### When to Choose Each

- **VMs only**: lift-and-shift, no orchestration needed
- **ECS/EKS/GKE/AKS with your nodes**: full control, cost-optimized at scale
- **Fargate / Autopilot / Cloud Run**: no node mgmt, simpler ops, pay per use, premium price

### Cloud Run / Container Apps / App Runner

Containers as functions:
- Source: container image
- Scale to zero
- Per-request billing
- HTTP-only (usually)
- Great for: HTTP services with variable traffic

## Serverless (FaaS)

### AWS Lambda
- 10 GB max memory; up to 6 vCPU (proportional)
- 15 min max duration
- Cold start: ~100ms (Python/Node) to seconds (Java without SnapStart)
- Triggers: API GW, S3, SQS, EventBridge, DynamoDB, Kinesis, etc.

### GCP Cloud Functions
- 8 GB max
- 9 min max (1st gen) / 1 hour (2nd gen on Cloud Run)
- Triggers: HTTP, Pub/Sub, Storage, Firestore, more

### Azure Functions
- Premium / Consumption plans
- Triggers: HTTP, Queue, Blob, Event Hub, Service Bus, Cosmos

### Cold Start Mitigation
- Provisioned Concurrency (Lambda) — keep warmers warm
- SnapStart (Lambda for Java)
- Smaller deployment package
- Avoid lazy initialization at first request

### When Serverless Wins
- Unpredictable / bursty traffic
- Event-driven workflows
- Small services where ops cost dominates
- Scheduled jobs (Lambda + EventBridge schedule)
- Glue between AWS services

### When Serverless Loses
- Steady high traffic (Fargate/EC2 cheaper)
- Long-running (> 15 min)
- Heavy CPU/GPU (no GPU on Lambda)
- Stateful workloads (use DynamoDB, etc., not Lambda state)

## Pricing Snapshot

| Service | Pricing |
|---|---|
| EC2 m6i.large On-Demand | ~$0.10/hr (~$70/mo) |
| EC2 with 3-yr SP | ~$0.04/hr |
| Spot m6i.large | ~$0.03/hr |
| Fargate 1 vCPU + 2GB | ~$0.05/hr |
| Cloud Run 1 vCPU + 512MB | ~$0.024 + per-request |
| Lambda 1GB, 1 sec | $0.0000167 |

(Approximate, US East, 2024-2025; check current pricing.)

## Interview Themes

- "Compare EC2, Fargate, Lambda"
- "When would you choose Lambda over Fargate?"
- "Cold starts — what are they, how to mitigate?"
- "When are containers cheaper than serverless?"
- "Walk through choosing compute for a new service"
