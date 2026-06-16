# L08/C08/T02 — EKS Architecture & Control Plane

## Learning Objectives

- Understand EKS architecture
- Pick node group strategy

## EKS

Managed Kubernetes. AWS runs control plane (etcd, API server, scheduler, controllers).

You manage: nodes, workloads, networking, IAM, observability.

## Control Plane

- HA across 3 AZs
- Auto-patched (you trigger major upgrades)
- Auto-scaled
- $0.10/hour per cluster ($73/mo)

API endpoint:
- Public (default)
- Private (only from VPC)
- Both

For production: private endpoint or strict CIDR allowlist on public.

## Data Plane (Nodes)

You pick:

### Managed Node Groups
- EC2 instances managed via ASG
- AWS handles AMI updates (you approve)
- Spot supported
- Easy

### Self-Managed Nodes
- You provision EC2; install kubelet manually (or via Cluster Autoscaler)
- More control
- More work

### Fargate Profile
- Serverless pods
- 1 pod = 1 Fargate task
- No node management
- Slower start (~30s); some limitations (no DaemonSet, hostNetwork)

### EKS Auto Mode (2024+)
- AWS manages nodes + many add-ons
- Pay per pod-second
- Simplest

## Networking — VPC CNI

Default CNI:
- Pod gets ENI IP from VPC subnet
- One pod = one IP (or share via secondary IPs)
- Limited by EC2 instance ENI capacity

For high pod density: ENI per pod limitation; use prefix delegation (16 IPs per ENI).

Alternative CNIs:
- Cilium (eBPF; advanced)
- Calico
- ENI Trunking

## IAM Integration

### IRSA (IAM Roles for Service Accounts)

Pod assumes IAM role via OIDC. Each pod can have distinct AWS permissions.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123:role/myRole
```

### EKS Pod Identity (newer)

Simpler than IRSA. Add-on:
```bash
aws eks create-pod-identity-association --cluster-name mycluster --namespace my-ns --service-account my-sa --role-arn arn:...
```

No SA annotation needed; cleaner.

## Storage

EBS CSI driver: PersistentVolumes from EBS.
EFS CSI driver: PV from EFS (ReadWriteMany).
S3 CSI driver: mount S3 (read-only typically).
FSx CSI: high-perf shared FS.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
```

## Load Balancing

### AWS Load Balancer Controller
K8s controller creates ALB / NLB from Service / Ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-svc
            port:
              number: 80
```

Auto-creates ALB; configures target groups.

## Logging

Control plane logs (audit, scheduler, etc.): enable per cluster, sent to CloudWatch.

Workload logs:
- CloudWatch Logs (FluentBit DaemonSet)
- Loki (third-party)
- ELK
- Datadog / NewRelic

## Cluster Versions

EKS supports recent K8s versions. New version each ~year:
- v1.28
- v1.29
- v1.30
- v1.31

Old versions deprecated; force upgrade.

Upgrade path:
1. Upgrade control plane (in-place; ~1 hr)
2. Upgrade node groups (replace with new AMI)
3. Update workloads / API deprecations

## Add-Ons

EKS Add-Ons: managed K8s components installed by AWS:
- VPC CNI
- CoreDNS
- kube-proxy
- EBS CSI driver
- EFS CSI driver
- Pod Identity Agent

```bash
aws eks create-addon --cluster-name mycluster --addon-name vpc-cni
```

Easier than self-installing.

## eksctl

CLI for EKS provisioning:
```bash
eksctl create cluster --name mycluster --region us-east-1 --nodegroup-name workers --node-type m5.large --nodes 3
```

Generates VPC, EKS, node group, IAM in one command. Great for getting started.

For production: Terraform / CDK more common.

## Cluster Autoscaler / Karpenter

Auto-add nodes when pods unschedulable.

### Cluster Autoscaler (CA)
Older; works with ASGs:
- Pod pending → check if ASG can scale
- Add EC2 → kubelet joins → pod scheduled

### Karpenter (recommended 2024+)
AWS's new node provisioner:
- Watches pending pods
- Provisions optimal instance type (not ASG-bound)
- Spot-aware
- Consolidation (move pods to fewer larger instances)

Faster + cheaper than CA.

## Spot in EKS

Managed Node Group with capacityType=SPOT:
```yaml
capacityType: SPOT
instanceTypes: [m5.large, m6i.large, m6a.large]
```

Or Karpenter:
```yaml
spec:
  requirements:
  - key: karpenter.sh/capacity-type
    operator: In
    values: [spot, on-demand]
```

aws-node-termination-handler: handles spot 2-min warning gracefully.

## Networking Modes

### Default (VPC CNI)
- Pod IP = VPC IP
- SG per pod (newer)
- Best AWS integration

### Custom Networking
- Pod IPs from different subnet than node
- For separation

### Secondary CIDR
- Add CIDR to VPC
- Pods use secondary
- For IP exhaustion

## Pod IP Address Per ENI

| Instance | ENIs | IPs/ENI | Max Pods |
|---|---|---|---|
| m5.large | 3 | 9 | 27 |
| m5.xlarge | 4 | 14 | 56 |
| m5.16xlarge | 15 | 49 | 730 |

Prefix delegation: each ENI gets /28 = 16 IPs; 10× more pods.

## Cost

- Cluster: $73/mo
- Nodes: EC2 prices
- Fargate pods: Fargate prices
- LBs, EBS, etc.: standard

For 10 medium nodes + 3 NAT GW + ALB: ~$1500/mo.

## Multi-Cluster

Pros:
- Blast radius (one cluster fail ≠ all down)
- Isolation (per team / env)
- Version variance

Cons:
- Operational overhead
- Cost
- Cross-cluster: complex

For most: one prod cluster, one staging, one dev.
For massive: per-team / per-tenant.

## Cluster Multi-Region

EKS one cluster per region. For multi-region:
- Independent clusters
- Cross-cluster: service mesh (Istio multi-cluster, Cilium ClusterMesh)
- Or LB at Route53 / Global Accelerator

## Security

- Control plane public endpoint: restrict to allowed CIDRs
- Pod Security Standards
- Network Policies (Calico, Cilium)
- IRSA for pod-level IAM
- Image scanning (ECR)
- Runtime scanning (Falco)

## Monitoring

- Control plane: CloudWatch metrics + logs
- Nodes: CloudWatch + Container Insights
- Workloads: Prometheus + Grafana (Managed: AMP + AMG)
- Tracing: X-Ray, OpenTelemetry

## Backups

For etcd: not user-accessible (AWS-managed).
For workload state: Velero (back up K8s objects + PVs).

## Common Mistakes

- Public endpoint without CIDR restriction
- No IAM access for kubectl (manage configmap)
- VPC CIDR too small (run out of pod IPs)
- No autoscaling
- Cluster Autoscaler vs Karpenter (newer better)
- Manual node management

## Best Practices

- Karpenter for nodes
- IRSA / Pod Identity
- Private endpoint (or strict CIDR)
- Multi-AZ
- EBS CSI for stateful
- Network Policy
- Image scanning
- Centralized logs
- Backups (Velero)

## Quick Refs

```bash
# Create cluster (eksctl)
eksctl create cluster --name mycluster --region us-east-1 --node-type m5.large

# Update kubeconfig
aws eks update-kubeconfig --name mycluster

# kubectl
kubectl get nodes
kubectl get pods -A
```

## Interview Prep

**Mid**: "EKS architecture."

**Senior**: "Karpenter vs Cluster Autoscaler."

**Staff**: "Multi-region EKS strategy."

## Next Topic

→ [T03 — Fargate Pricing & Limits](T03-Fargate.md)
