# L07/C04/T02 — Containers (ECS, EKS, GKE, AKS, Fargate, Cloud Run)

## Learning Objectives

- Choose the right container platform
- Understand tradeoffs

## Container Recap

Container: process(es) isolated by namespaces + cgroups. Lighter than VM (no separate OS).

Image: filesystem layers + metadata. Build with Dockerfile. Stored in registry.

Detail covered in L12. Here: cloud-managed orchestration.

## Cloud Container Options

| Option | Cloud | What | When |
|---|---|---|---|
| ECS | AWS | Proprietary orchestrator | AWS-only; simpler than K8s |
| EKS | AWS | Managed K8s | Want K8s; on AWS |
| Fargate | AWS | Serverless containers (ECS/EKS) | Don't manage nodes |
| GKE | GCP | Managed K8s | K8s on GCP; mature |
| Cloud Run | GCP | Serverless containers | HTTP services; scale to 0 |
| AKS | Azure | Managed K8s | K8s on Azure |
| Container Apps | Azure | Serverless containers | Like Cloud Run |
| App Runner | AWS | Serverless web app | Simple web; ECS underneath |

## ECS (AWS)

Proprietary orchestrator. Two flavors:
- **EC2 launch type**: you manage EC2 nodes, ECS schedules
- **Fargate launch type**: AWS manages nodes; you specify CPU/RAM per task

Concepts:
- **Cluster**: logical group
- **Task Definition**: spec (containers, CPU, RAM, IAM, networking)
- **Task**: running instance of task def
- **Service**: keeps N tasks running; integrates with LB

Simpler than K8s; less portable.

## EKS (AWS)

Managed Kubernetes. AWS runs control plane (etcd, API server).

You manage:
- Node groups (EC2 or Fargate)
- Workloads
- RBAC, networking, secrets

Comes with:
- AWS Load Balancer Controller (creates ALBs from Ingress)
- IAM Roles for Service Accounts (IRSA): pods assume AWS IAM roles
- VPC CNI: pod IPs from VPC range
- EBS CSI driver: PersistentVolumes from EBS

EKS Auto Mode (2024+): AWS manages everything including node groups; closer to serverless.

## Fargate

Serverless containers; works with ECS or EKS.

You specify: CPU, RAM, container image, env, IAM, networking.
AWS handles: provisioning, scaling, patching nodes.

Pricing: per vCPU-second + GB-second.

Trade-offs:
- + No node management
- + Easier security (no node access)
- − No DaemonSets, no host network in K8s
- − More expensive per vCPU than EC2
- − Cold start (slow first task)

## GKE (GCP)

Managed K8s on GCP. Often considered most mature K8s service (GCP invented it).

Two modes:
- **Standard**: you manage node pools
- **Autopilot**: GCP manages nodes (pay per pod-second)

Native integrations: GCP IAM via Workload Identity, GCS storage, BigQuery.

## AKS (Azure)

Managed K8s on Azure. Free control plane.

Integration: Azure AD for RBAC, Azure Disks/Files, Application Gateway.

Newer: AKS Automatic mode (similar to GKE Autopilot).

## Cloud Run (GCP)

Serverless containers. HTTP request → container starts → handles request → can scale to 0.

You bring: container image (with HTTP listener on $PORT).
GCP handles: scaling, routing, TLS, scaling to 0 (no traffic = no cost).

Built on Knative; open standard.

Limits:
- Stateless (each request can hit different instance)
- 60-min request timeout (or longer with Jobs)
- HTTP/2 / gRPC supported
- 1 GB RAM default; up to 32 GB

Great for: web apps, APIs, async work (with Pub/Sub).

## Comparison

| | ECS | EKS Fargate | EKS EC2 | Cloud Run | GKE Autopilot |
|---|---|---|---|---|---|
| K8s | No | Yes | Yes | No (Knative) | Yes |
| Nodes | EC2 | Managed | EC2 you | None | Managed |
| Scale to 0 | No | No | No | Yes | No |
| Per-second billing | EC2 | Yes | EC2 | Yes | Pod-second |
| Cold start | No | Yes (slow first) | No | Yes (warm < 1s often) | Pod-second |
| Lock-in | High | Low | Low | Medium | Low |
| Complexity | Medium | Medium | High | Low | Medium |

## When To Pick

**ECS**: AWS-only, simpler than K8s, team prefers AWS-native, microservices growing modestly.

**EKS**: K8s benefits matter (community, portability), team has K8s skills.

**Fargate**: don't want to manage nodes; security-sensitive (no node access).

**Cloud Run / Container Apps / App Runner**: stateless HTTP services; bursty traffic; want scale-to-zero.

**GKE**: GCP shop; K8s expertise; big enterprise.

**AKS**: Azure shop; K8s expertise.

## Multi-Cloud K8s

K8s itself is portable. But each cloud adds:
- Storage CSI (EBS, PD, Azure Disk)
- LB / Ingress
- IAM integration
- Secrets stores

Apps using K8s primitives = portable. Apps using cloud add-ons = portable-ish.

## Service Mesh

For complex networking: Istio, Linkerd, Cilium. Each cloud has integrations.

## Image Registry

Per cloud:
- AWS ECR
- GCP Artifact Registry
- Azure Container Registry

All support OCI; private; IAM-integrated. Pricing per GB stored + transfer.

Public: Docker Hub, GitHub Container Registry, quay.io.

## Common Patterns

### Web App
- HTTP load balancer
- Container with HTTP server
- Scale based on requests/CPU
- Run multiple per AZ for HA

### Worker
- Container reads from queue
- Process work
- Scale based on queue depth

### Cron Job
- Scheduled container run
- K8s CronJob, ECS Scheduled Task, Cloud Run Jobs

### gRPC Service
- Internal LB
- Container with gRPC server
- Header propagation (tracing)

## Cost Comparison

For steady 1 container 24/7:
- EC2 t3.medium: $30/mo
- ECS Fargate: $36/mo (0.5 vCPU + 1 GB)
- Cloud Run (10% utilized): $5/mo (idle no charge)
- Cloud Run (100% utilized): $50/mo

Cloud Run wins for sporadic; EC2/ECS for steady.

## Common Mistakes

- K8s for tiny app (overkill)
- ECS when K8s skills exist
- Self-hosted K8s when managed available
- No autoscaling configured
- Latency-sensitive on Fargate (cold starts)

## Migration

Lift-and-shift VM → container often easy (containerize app, push to ECS Fargate or Cloud Run).

Microservices migration: gradual. Strangler fig.

## Interview Prep

**Mid**: "ECS vs EKS."

**Senior**: "Fargate vs EC2 — cost / control tradeoffs."

**Staff**: "K8s vs Cloud Run for 50 microservices."

## Next Topic

→ [T03 — Serverless (Lambda, Cloud Functions, Azure Functions)](T03-Serverless.md)
