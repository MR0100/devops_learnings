# L08/C08 — Container Services

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-ECS.md) | ECS (EC2 vs Fargate) | 1 hr |
| [T02](T02-EKS.md) | EKS Architecture & Control Plane | 1.5 hr |
| [T03](T03-Fargate.md) | Fargate Pricing & Limits | 0.5 hr |
| [T04](T04-ECR.md) | ECR (Image Scanning, Replication) | 0.5 hr |
| [T05](T05-App-Mesh.md) | App Mesh | 0.5 hr |

## ECS (Elastic Container Service)

AWS's container orchestrator. Simpler than K8s.

### Concepts
- **Task Definition**: container(s) spec (image, ports, env, resources)
- **Task**: instantiation of task definition
- **Service**: maintains N tasks running
- **Cluster**: logical grouping of tasks
- **Capacity Provider**: how tasks get capacity (EC2 ASG, Fargate, Fargate Spot)

### ECS on EC2
- You manage the EC2 fleet (or ASG with capacity provider)
- Lower per-vCPU cost
- More control (placement, daemon containers via DaemonSet-equivalent)

### ECS on Fargate
- AWS manages the compute
- No EC2 fleet
- Per-second billing
- Pay for vCPU and memory provisioned
- Premium price

### Fargate Spot
- Spot pricing on Fargate (~70% off)
- 2-min interruption
- Stateless workloads

## EKS Architecture

```
[AWS-Managed Control Plane]
   ├── 3 apiserver instances (multi-AZ)
   ├── etcd (multi-AZ, AWS-managed)
   ├── scheduler, controller-manager
   └── Cloud Controller Manager

[Your Worker Nodes]
   ├── EC2 (self-managed or Managed Node Groups)
   ├── Fargate (per-pod billed)
   └── Karpenter (recommended for autoscaling)

[Add-ons]
   ├── VPC CNI (default)
   ├── kube-proxy
   ├── CoreDNS
   ├── EBS CSI driver
   └── Pod Identity Agent
```

### Cost
- $0.10/hr per cluster control plane (~$73/mo)
- Plus EC2/Fargate for nodes
- Plus Cloud LB, EBS, etc.

### Networking
- **AWS VPC CNI**: pods get real VPC IPs (one ENI/IP per pod)
- ENI limits per instance type can constrain pod density
- Alternative CNIs: Calico, Cilium (lose some integration; gain features)
- **Custom Networking**: pods in different subnet than nodes (for IP exhaustion)

### Auth
- IAM Identity Center → kubectl via aws-iam-authenticator (or `aws eks get-token`)
- aws-auth ConfigMap maps IAM principals to K8s users/groups (legacy)
- EKS API Access entries (newer, 2023+) — manage access through EKS API

### Upgrades
- Manual control plane upgrade (one minor at a time)
- AWS handles patch updates automatically
- Node groups upgrade separately

## ECR (Elastic Container Registry)

- OCI-compliant private registry
- IAM-based auth
- Image scanning: Basic (free, Trivy-equivalent) or Enhanced (Inspector, paid, OS+language vulns)
- Cross-region replication
- Pull through cache (proxy to upstream registries like Docker Hub, Quay)
- Lifecycle policies (delete untagged > 30 days, etc.)

```bash
aws ecr get-login-password | docker login --username AWS --password-stdin 123.dkr.ecr.us-east-1.amazonaws.com
docker tag myimage:v1 123.dkr.ecr.us-east-1.amazonaws.com/myimage:v1
docker push 123.dkr.ecr.us-east-1.amazonaws.com/myimage:v1
```

### ECR Public
For sharing public images (like Docker Hub).

## App Mesh

AWS-managed service mesh built on Envoy.

- Sidecar Envoy injected into ECS/EKS pods
- Virtual nodes, services, routers, gateways
- mTLS via ACM
- Integrates with X-Ray, CloudWatch

Adoption is lower than Istio/Linkerd; most teams use those on EKS.

## Choosing Compute for Containers

| Decision factor | ECS | EKS |
|---|---|---|
| K8s ecosystem (Helm, operators) | ❌ | ✅ |
| Simplicity | ✅ | ❌ |
| Cost (control plane) | Free | $73/mo |
| Multi-cloud portability | ❌ | ✅ |
| Hiring market | smaller | larger |

| Decision factor | Fargate | EC2 |
|---|---|---|
| No node mgmt | ✅ | ❌ |
| Per-pod isolation | ✅ | ❌ (shared kernel) |
| Cost at scale | ❌ | ✅ |
| Daemon Sets (host monitoring) | ❌ | ✅ |
| GPU | ❌ | ✅ |
| Spot | Fargate Spot | EC2 Spot |

## Recommendations

- Start with EKS + Karpenter + Spot for new platforms
- Use Fargate for low-volume / steady-state simple workloads
- ECS for legacy AWS-native and teams without K8s expertise
- Fargate for ECS where node mgmt isn't justified

## Interview Themes

- "Compare ECS and EKS"
- "EKS control plane — what does AWS manage?"
- "Fargate vs EC2 for containers — when each?"
- "ECR image scanning — Basic vs Enhanced"
- "Design a multi-account EKS platform"
