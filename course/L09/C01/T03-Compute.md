# L09/C01/T03 — Compute (VMs, VMSS, AKS, App Service, Functions)

## Learning Objectives

- Choose Azure compute
- Compare to AWS

## VMs

Azure VMs = EC2:
```bash
az vm create \
  --resource-group myrg \
  --name myvm \
  --image Ubuntu2404 \
  --size Standard_D2s_v5 \
  --admin-username azureuser \
  --generate-ssh-keys
```

Pricing: per second; Reserved Instances for discount.

## SKU Families

- **A**: basic
- **B**: burstable
- **D**: general
- **E**: memory-optimized
- **F**: compute-optimized
- **L**: storage-optimized
- **M**: huge memory
- **N**: GPU

For: workload-aligned.

## VM Scale Sets (VMSS)

= Auto Scaling Group:
```bash
az vmss create \
  --resource-group myrg \
  --name myvmss \
  --image Ubuntu2404 \
  --instance-count 3 \
  --upgrade-policy-mode Manual
```

Manages identical VMs. Scale rules tied to metrics.

## Spot VMs

```bash
az vm create --priority Spot --max-price 0.05 ...
```

Cheaper (~80% off); evictable.

For: batch, stateless.

## Availability Sets / Zones

### Set
Fault + Update domains in single region.
- Up to 99.95% SLA

### Zones
Across AZs:
- Up to 99.99% SLA

Zones > Sets.

## AKS

Managed Kubernetes:
```bash
az aks create \
  --resource-group myrg \
  --name myaks \
  --node-count 3 \
  --enable-managed-identity \
  --generate-ssh-keys
```

Control plane: free (limited SLA tier) or paid (Uptime SLA).

Node pools: VMSS underneath.

For: K8s on Azure.

## AKS Features

- Workload Identity
- Azure CNI / Azure CNI Overlay
- Azure Policy
- Defender
- Application Routing (ingress)

## App Service

PaaS web hosting:
```bash
az webapp create \
  --resource-group myrg \
  --plan myasp \
  --name myapp \
  --runtime "PYTHON:3.12"
```

For: web apps without infra.

## App Service Plan

= compute behind App Service:
- F1: free
- B1: basic
- S1: standard
- P1v3: premium

Multiple apps share plan.

## Functions

Serverless = Lambda:
```bash
func init MyFunc --python
func new --name HttpTrigger --template "HTTP trigger"
func azure functionapp publish myfunc
```

Triggers: HTTP, Queue, Blob, Timer, Event Grid.

Plans:
- **Consumption**: pay per execution
- **Premium**: pre-warmed, VNet
- **Dedicated**: App Service Plan

## Container Apps

Serverless containers = Cloud Run / Fargate:
```bash
az containerapp create \
  --name myapp \
  --resource-group myrg \
  --image myacr.azurecr.io/app:v1 \
  --target-port 8080 \
  --ingress external
```

For: containers without K8s.

## Container Instances (ACI)

Single-container; no orchestration:
```bash
az container create --resource-group myrg --name myci --image nginx
```

For: one-off jobs, dev.

## Batch

= AWS Batch:
HPC, parallel batch processing.

## Service Fabric

MS-specific microservices orchestrator.

Mostly legacy; new projects use AKS.

## Choose Compute

```
VM:        full control, lift-and-shift
VMSS:      auto-scaling VMs
AKS:       container orchestration (K8s)
App Svc:   web apps, fast dev
Funcs:     event-driven, short tasks
CntrApp:   serverless containers
ACI:       quick containers
Batch:     HPC / batch jobs
```

## AWS Equivalents

| Azure | AWS |
|---|---|
| VM | EC2 |
| VMSS | ASG |
| AKS | EKS |
| App Service | Elastic Beanstalk |
| Functions | Lambda |
| Container Apps | App Runner / Cloud Run-like |
| ACI | Fargate (sort of) |
| Batch | Batch |

## Networking

VMs in VNet (= VPC).
NSGs (= SGs) at NIC or subnet.

```bash
az network nsg create --resource-group myrg --name mynsg
az network nsg rule create --nsg-name mynsg --resource-group myrg \
  --name allow-ssh --priority 100 \
  --source-address-prefixes Internet \
  --destination-port-ranges 22 \
  --access Allow --protocol Tcp
```

## Identity

VM with managed identity:
```bash
az vm identity assign --resource-group myrg --name myvm
```

Now VM can access Azure resources without creds.

For AKS: Workload Identity.

## Storage

OS disk + data disks:
- Premium SSD
- Standard SSD
- Standard HDD
- Ultra Disk

Encrypted at rest (default).

## SLA

| | SLA |
|---|---|
| Single VM (Premium SSD) | 99.9% |
| Availability Set | 99.95% |
| Availability Zone (2+) | 99.99% |
| AKS (Uptime SLA) | 99.95% |
| App Service (S1+) | 99.95% |

For prod: zones or AS.

## Cost

VMs: pay per second.
RIs / Savings Plans: 30-70% off.
Spot: ~80% off.

For: aggressive optimization.

## Best Practices

- Right-size (don't over-provision)
- RIs / Savings Plans
- Spot for stateless
- Zones for HA
- Managed Identity (no creds)
- Monitor with Azure Monitor

## Common Mistakes

- B-series for prod (CPU credits)
- Single VM (no HA)
- Premium SSD for everything (cost)
- Static creds in VM

## Quick Refs

```bash
# VM
az vm create / start / stop / delete
az vm list

# VMSS
az vmss create / scale / update

# AKS
az aks create / get-credentials / scale

# App Service
az webapp create / restart / delete

# Functions
func init / new / publish
```

## Interview Prep

**Junior**: "Azure compute options."

**Mid**: "AKS vs App Service."

**Senior**: "Cost optimization."

**Staff**: "Compute strategy across services."

## Next Topic

→ [T04 — Storage (Blob, Files, Disks)](T04-Storage.md)
