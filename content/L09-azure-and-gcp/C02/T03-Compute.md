# L09/C02/T03 — Compute (GCE, GKE, Cloud Run, Cloud Functions)

## Learning Objectives

- Choose GCP compute
- Compare to AWS / Azure

## GCE (Compute Engine)

= EC2 / Azure VM:
```bash
gcloud compute instances create my-vm \
  --machine-type=e2-medium \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --zone=us-central1-a
```

Per-second billing.

## Machine Families

- **E2**: cost-optimized
- **N2**: general purpose
- **N2D**: AMD general
- **C3**: compute-optimized
- **M3**: memory-optimized
- **A2/A3**: GPU
- **T2D**: ARM
- **C4A**: ARM (Axion)

## Custom Machine Types

```bash
gcloud compute instances create my-vm \
  --custom-cpu=6 --custom-memory=24
```

For: specific needs; not standard SKU.

## Preemptible / Spot

Spot VMs (newer; better):
```bash
gcloud compute instances create my-vm --provisioning-model=SPOT --instance-termination-action=STOP
```

~60-91% off. Evictable in 24h max.

For: stateless, batch.

## MIG (Managed Instance Group)

= ASG:
```bash
gcloud compute instance-templates create my-tmpl \
  --machine-type=e2-medium --image-family=debian-12 --image-project=debian-cloud

gcloud compute instance-groups managed create my-mig \
  --base-instance-name=my-vm \
  --size=3 \
  --template=my-tmpl \
  --zone=us-central1-a
```

Auto-scaling, autohealing, rolling updates.

## Regional vs Zonal MIG

```bash
--zone (single AZ)
--region (multi-AZ; HA)
```

For prod: regional.

## GKE

Managed Kubernetes:
```bash
gcloud container clusters create my-gke \
  --zone=us-central1-a \
  --num-nodes=3
```

Two modes:

### Standard
- You manage node pools
- More control
- Like EKS

### Autopilot
- GKE manages nodes
- Pay per pod
- Like Fargate-on-EKS

```bash
gcloud container clusters create-auto my-gke --region=us-central1
```

For: hands-off.

## Cloud Run

Serverless containers:
```bash
gcloud run deploy my-svc \
  --image=us-central1-docker.pkg.dev/PROJ/repo/myapp:v1 \
  --region=us-central1 \
  --allow-unauthenticated
```

- HTTP request → container start
- Auto-scales to 0
- Pay per request

= AWS App Runner / Azure Container Apps.

## Cloud Run Jobs

Batch:
```bash
gcloud run jobs create my-job \
  --image=... \
  --region=us-central1
```

For: non-HTTP, finite tasks.

## Cloud Functions

= Lambda:
```bash
gcloud functions deploy my-func \
  --gen2 \
  --runtime=python312 \
  --region=us-central1 \
  --source=. \
  --entry-point=handler \
  --trigger-http \
  --allow-unauthenticated
```

Gen 2: built on Cloud Run; better.

Triggers: HTTP, Pub/Sub, Storage, Firestore, etc.

## App Engine

Legacy PaaS:
- Standard (sandboxed)
- Flexible (containers)

Mostly use Cloud Run for new.

## GKE Node Pools

```bash
gcloud container node-pools create gpu-pool \
  --cluster=my-gke \
  --num-nodes=1 \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-t4,count=1
```

Heterogeneous: different machine types in same cluster.

## Image Streaming (GKE)

```bash
gcloud container clusters create --enable-image-streaming ...
```

Container images stream from GAR; pod starts faster.

## GKE Sandboxed

```bash
gcloud container node-pools create sandbox-pool \
  --cluster=my-gke \
  --sandbox=type=gvisor
```

Pods isolated via gVisor.

For: multi-tenant.

## Choose Compute

```
GCE:           full VM control
MIG:           auto-scaling VMs
GKE Standard:  K8s with control
GKE Autopilot: K8s hands-off
Cloud Run:     serverless containers
Cloud Functions: serverless functions
```

Decision:
- Container + scale to 0: Cloud Run
- K8s native: GKE
- VM workload: GCE
- Event-driven small: Functions

## Network

VM in VPC subnet. Firewall rules (project-wide).

```bash
gcloud compute firewall-rules create allow-ssh \
  --network=default \
  --allow=tcp:22 \
  --source-ranges=0.0.0.0/0
```

## SSH

```bash
# IAP tunnel (no public IP needed)
gcloud compute ssh my-vm --tunnel-through-iap
```

For: no public IP; secure.

## OS Login

Centralized SSH via IAM:
```bash
gcloud compute project-info add-metadata --metadata enable-oslogin=TRUE
```

Then SSH access controlled by IAM (no manual sshd config).

For: enterprise.

## Comparison

| GCP | AWS | Azure |
|---|---|---|
| GCE | EC2 | VM |
| MIG | ASG | VMSS |
| GKE | EKS | AKS |
| Cloud Run | App Runner | Container Apps |
| Functions | Lambda | Functions |
| App Engine | Beanstalk | App Service |

## Cost

- Sustained Use Discount (auto)
- Committed Use (1y/3y; 30-70%)
- Spot
- Custom machine types

For: aggressive savings.

## SLA

- Single zone VM: 99.5%
- Multi-zone: 99.99%
- GKE: 99.95% / 99.9%
- Cloud Run: 99.95%

## Best Practices

- Spot for stateless
- Committed Use Discounts
- Regional MIG for HA
- IAP tunnel (no public IPs)
- OS Login
- Workload Identity (no SA keys)

## Common Mistakes

- Single-zone for prod
- e2-micro for prod (CPU credits)
- Default SA (Editor)
- Public IPs everywhere

## Quick Refs

```bash
# GCE
gcloud compute instances create / list / delete
gcloud compute ssh

# MIG
gcloud compute instance-groups managed create / resize

# GKE
gcloud container clusters create / get-credentials

# Cloud Run
gcloud run deploy / services list

# Functions
gcloud functions deploy / list
```

## Interview Prep

**Junior**: "GCP compute options."

**Mid**: "GKE Standard vs Autopilot."

**Senior**: "When Cloud Run vs GKE."

**Staff**: "Compute strategy at scale."

## Next Topic

→ [T04 — Storage (GCS, Persistent Disk, Filestore)](T04-Storage.md)
