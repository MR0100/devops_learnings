# L09/C01 — Azure Core

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Resource-Groups.md) | Resource Groups, Subscriptions, Management Groups | 1 hr |
| [T02](T02-Entra-ID.md) | Entra ID (formerly Azure AD) | 1.5 hr |
| [T03](T03-Compute.md) | Compute (VMs, VMSS, AKS, App Service, Functions) | 1.5 hr |
| [T04](T04-Storage.md) | Storage (Blob, Files, Disks) | 1 hr |
| [T05](T05-Networking.md) | Networking (VNets, NSGs, Application Gateway, Front Door) | 1.5 hr |
| [T06](T06-Bicep-ARM.md) | Bicep & ARM Templates | 1 hr |

## Hierarchy

```
Management Group
└── Subscription
    └── Resource Group
        └── Resources
```

- **Management Groups**: hierarchical container for governance (RBAC, policy)
- **Subscriptions**: billing + access boundary (similar to AWS account)
- **Resource Groups**: lifecycle container for related resources (required)
- **Resources**: actual things (VMs, storage, etc.)

### Recommended Structure
```
Tenant Root MG
├── Platform MG (shared services)
│   └── Sub: Identity, Connectivity, Management
├── Landing Zones MG
│   ├── MG: Corp
│   │   └── Sub: Prod, NonProd
│   └── MG: Online (internet-facing)
└── Sandbox MG
    └── Sub: Sandbox-Team-X
```

This is the **Cloud Adoption Framework (CAF)** landing zone pattern.

## Entra ID (formerly Azure AD)

Identity and access for Azure + M365 + SaaS apps.

### Concepts
- **Tenant**: an Entra ID instance (your org)
- **Users / Groups**: who
- **App Registrations**: SPNs (Service Principal Names) for workloads
- **Managed Identities**: Azure-native workload identity (no secrets)
- **Conditional Access**: policy-based MFA / blocking
- **PIM (Privileged Identity Management)**: JIT role activation

### RBAC
- Roles (built-in or custom)
- Scopes: MG > Sub > RG > Resource
- Assignments at any scope

```bash
az role assignment create \
  --assignee alice@example.com \
  --role Contributor \
  --scope /subscriptions/<sub-id>/resourceGroups/myrg
```

### Managed Identities
- **System-Assigned**: tied to resource lifecycle
- **User-Assigned**: standalone, can be reused

Pod / app gets Azure AD token via IMDS endpoint; no secrets.

## Compute

| | AWS Equivalent |
|---|---|
| Azure VM | EC2 |
| VM Scale Set (VMSS) | ASG |
| AKS (Azure Kubernetes Service) | EKS |
| App Service | Beanstalk / App Runner |
| Container Apps | Fargate / ECS Fargate / Cloud Run |
| Functions | Lambda |
| Container Instances (ACI) | Fargate (single container) |
| Batch | Batch |
| Service Fabric | (no direct equivalent) |

## Storage

### Storage Accounts
- Container for blob, files, queues, tables, disks
- Performance tiers: Standard (HDD/SSD), Premium (SSD)
- Redundancy: LRS (local 3 copies), ZRS (zone), GRS (geo), RA-GRS (read access geo)
- Account types: General-purpose v2 (GPv2 — default), Premium

### Blob Storage
- Containers contain blobs
- Tiers: Hot, Cool, Cold, Archive
- Lifecycle policies for tier transitions

### Files
- SMB / NFS shares
- Premium for high-perf

### Managed Disks
- For VM OS / data disks
- Ultra Disk, Premium SSD v2, Premium SSD, Standard SSD, Standard HDD

## Networking

### VNet
- Virtual network (like VPC)
- Multiple subnets
- Address space (CIDR)
- NSGs (security groups) per subnet/NIC
- ASGs (Application Security Groups) — tag-like grouping for NSG rules
- Service Endpoints / Private Endpoints (PrivateLink equivalent)
- VNet Peering (hub-spoke common)

### Load Balancers
- **Azure Load Balancer**: L4
- **Application Gateway**: L7 (path-based, WAF integration)
- **Front Door**: Global L7 (Azure's CloudFront + global LB combined)
- **Traffic Manager**: DNS-based routing (like Route 53)

### Connectivity
- **ExpressRoute**: dedicated connection (like DX)
- **VPN Gateway**: site-to-site VPN
- **Virtual WAN (vWAN)**: hub-and-spoke at scale (like TGW)

## Bicep & ARM

### ARM Templates (legacy)
- JSON, verbose, complex
- Native Azure IaC

### Bicep (modern)
- Cleaner DSL that transpiles to ARM
- Modules, looping, conditionals
- IDE support
- Azure's preferred IaC (vs Terraform for Azure-only)

```bicep
param location string = resourceGroup().location
param storageName string

resource sa 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: { supportsHttpsTrafficOnly: true }
}

output saId string = sa.id
```

## Interview Themes

- "Compare Entra ID with AWS IAM"
- "Resource Groups vs Subscriptions vs Management Groups"
- "Bicep vs ARM vs Terraform for Azure"
- "Compare AKS and EKS"
- "What's a Managed Identity?"
