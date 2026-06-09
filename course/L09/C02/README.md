# L09/C02 — GCP Core

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Projects-Folders-Orgs.md) | Projects, Folders, Organizations | 1 hr |
| [T02](T02-IAM-SA-WorkloadID.md) | IAM (Roles, Service Accounts, Workload Identity) | 1.5 hr |
| [T03](T03-Compute.md) | Compute (GCE, GKE, Cloud Run, Cloud Functions) | 1.5 hr |
| [T04](T04-Storage.md) | Storage (GCS, Persistent Disk, Filestore) | 1 hr |
| [T05](T05-Networking.md) | Networking (VPC, Cloud Load Balancing, Cloud Armor) | 1.5 hr |
| [T06](T06-IaC.md) | Deployment Manager, Config Connector | 1 hr |

## Hierarchy

```
Organization
├── Folder: Production
│   ├── Project: prod-app
│   └── Project: prod-data
├── Folder: Development
│   └── Project: dev
└── Project: shared
```

- **Organization**: tenant root (tied to Workspace/Cloud Identity)
- **Folder**: optional grouping (multi-level)
- **Project**: billing + access + API enablement boundary (smaller scope than AWS account)

Common pattern: **one project per team or per workload**, not per cloud.

## IAM

### Principal Types
- Google Account (user)
- Service Account (workload)
- Google Group
- Workspace domain
- Workforce Identity (federated)

### Role Types
- **Basic** (legacy): Owner, Editor, Viewer (too broad, avoid for prod)
- **Predefined**: per-service, well-scoped (`roles/storage.objectViewer`)
- **Custom**: your own permission sets

### Granting
```
Resource (Project/Folder/Org) → Role → Principal
```

```bash
gcloud projects add-iam-policy-binding my-project \
  --member="user:alice@example.com" \
  --role="roles/storage.objectViewer"
```

### Service Accounts (SAs)
- Project-scoped identity for workloads
- Key types: JSON keys (avoid), short-lived via impersonation (preferred)
- Default SA per project (compute SA, App Engine SA) — restrict permissions

### Workload Identity (GKE)
GKE pods auth to Google APIs as a GCP SA:
1. K8s SA in namespace
2. IAM binding: K8s SA → GCP SA (`roles/iam.workloadIdentityUser`)
3. Annotate K8s SA with GCP SA email
4. Pod gets metadata-server-provided token automatically

No JSON keys to manage.

## Compute

| | AWS Equivalent |
|---|---|
| Compute Engine (GCE) | EC2 |
| Instance Group | ASG |
| GKE (Standard) | EKS |
| GKE Autopilot | EKS Auto Mode |
| Cloud Run | Lambda/Fargate hybrid |
| Cloud Functions | Lambda |
| App Engine | Beanstalk |
| Cloud Run Jobs | Batch / Lambda async |

### GKE Autopilot
- Fully managed nodes
- Per-pod billing
- No node management
- Slightly higher per-vCPU
- Great for teams without K8s ops expertise

### Cloud Run
- Containers as a service
- Scale to zero
- Per-request billing (sub-second granularity)
- HTTP only
- Best for: HTTP services with variable traffic

## Storage

### GCS (Cloud Storage)
- Object storage (S3 equivalent)
- Buckets are global namespace
- Location: regional, dual-region, multi-region
- Classes: Standard, Nearline, Coldline, Archive
- Object versioning, lifecycle, retention policies
- Uniform bucket-level access (recommended) vs fine-grained (legacy ACLs)

### Persistent Disk
- Zonal or regional (replicated across 2 zones — unique!)
- Types: Standard, Balanced, SSD, Extreme

### Filestore
- NFS-managed service

## Networking

### VPC
- **Global** by default (vs AWS regional)
- Subnets are regional
- One VPC can span all regions
- Custom mode (you create subnets) vs Auto mode (auto subnets)

### Firewall Rules
- VPC-level (not per-subnet)
- Applied via network tags or service accounts
- Stateful

### Cloud Load Balancing
- **Global**: single anycast IP, routes to nearest healthy backend
- L4 and L7 variants
- HTTPS LB has built-in CDN and Cloud Armor integration

### Cloud CDN
- Edge cache backed by Cloud Storage or Cloud LB origins

### Cloud Armor
- WAF + DDoS protection
- Adaptive Protection (ML-based)

### Cross-region by default
GCP networking elegance: many things work cross-region without explicit peering.

## IaC

### Deployment Manager (legacy)
- YAML/Python templates
- GCP-native; not widely used today

### Config Connector
- K8s controller that creates GCP resources via CRDs
- Manage GCP infra declaratively in K8s
- Powerful for GitOps-driven infra

### Modern Choice
Most teams use **Terraform** for GCP IaC. The Google Cloud Provider is mature.

## Cloud-Specific Strengths

- **Spanner**: globally distributed strongly-consistent SQL (unique to GCP)
- **BigQuery**: serverless data warehouse at any scale
- **Bigtable**: petabyte-scale wide-column
- **Pub/Sub**: durable global messaging
- **Vertex AI**: managed ML platform
- **TPUs**: ML accelerators (10× faster than GPU for some workloads)
- **Live Migration**: VMs migrate during hypervisor maintenance without reboot

## Interview Themes

- "Compare Project hierarchy vs AWS accounts"
- "How does Workload Identity work in GKE?"
- "Global VPC vs regional VPC — what's different?"
- "Cloud Run vs Lambda"
- "When GCP over AWS?"
