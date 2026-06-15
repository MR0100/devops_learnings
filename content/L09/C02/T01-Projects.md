# L09/C02/T01 — Projects, Folders, Organizations

## Learning Objectives

- Understand GCP hierarchy
- Compare to AWS / Azure

## Hierarchy

```
Organization (one per company)
└─ Folders (nested, optional)
   └─ Projects (mandatory; smallest scope)
      └─ Resources
```

Distinct from Azure: Project ≠ Resource Group; Project = AWS Account.

## Organization

= AWS Organization root / Azure Tenant root.
- Bound to Google Workspace or Cloud Identity
- Top-level

For: large companies.

## Folders

Optional grouping of projects:
```
Org
├─ Production folder
│  ├─ proj-prod-api
│  └─ proj-prod-db
├─ Non-Prod folder
│  └─ proj-dev-all
└─ Shared folder
   └─ proj-shared-network
```

Policies apply down.

## Projects

Mandatory; resources live here:
```bash
gcloud projects create myproj-prod-api \
  --folder=FOLDER_ID \
  --name="MyApp Prod API"
```

- Unique ID across all GCP
- Billing target
- Quota
- API enablement per project

For: app-aligned, env-aligned isolation.

## Project ID vs Name vs Number

- **ID**: globally unique; choose at create
- **Name**: human readable; can change
- **Number**: auto-generated numeric

References use ID or number.

## Billing Account

Separate from projects:
```bash
gcloud billing accounts list
gcloud billing projects link myproj --billing-account=BILLING_ACCT_ID
```

Multiple projects → one billing account.

## Why So Many Projects

GCP encourages many projects:
- Isolation
- Quotas
- Distinct billing
- Per-env, per-app, per-team

Common: per-app per-env (3 envs = 3 projects).

Could be 100s.

## Folders for Scale

For many projects: folder hierarchy:
```
Org
├─ Team A
│  ├─ Prod
│  │  ├─ proj-team-a-prod-api
│  │  └─ proj-team-a-prod-db
│  └─ Dev
│     └─ proj-team-a-dev
└─ Team B
   ├─ Prod
   └─ Dev
```

Policy at folder: cascades.

## Constraints (Org Policy)

```bash
gcloud resource-manager org-policies enable-enforce \
  constraints/compute.requireOsLogin \
  --organization=ORG_ID
```

Constraints: deny-list, allow-list, boolean enforcement.

Examples:
- Allowed regions
- Allowed external IPs (none)
- Require OS Login
- Disable SA creation

For: governance at scale.

## Naming

```
proj-<team>-<env>-<workload>
proj-data-prod-warehouse
proj-platform-dev-eks
```

Globally unique. Pick wisely.

## Project Creation Flow

```bash
gcloud projects create proj-id \
  --folder=FOLDER \
  --name="Display Name"

gcloud billing projects link proj-id --billing-account=BILLING_ID

gcloud services enable compute.googleapis.com --project=proj-id
```

3 steps usually:
1. Create project
2. Link billing
3. Enable APIs

## Enable APIs

APIs disabled by default:
```bash
gcloud services enable storage-api.googleapis.com
gcloud services enable cloudkms.googleapis.com
gcloud services list --available --filter=name:compute
```

Each API: independent enable.

## Quotas

Per project, per service.
- vCPUs per region
- Compute Engine instances
- Disk
- Internal IPs

Hit quota → resource creation fails.

```bash
gcloud compute project-info describe --project=PROJ
```

Request quota increase via Console.

## Comparison

| | AWS | Azure | GCP |
|---|---|---|---|
| Top | Organization | Tenant | Organization |
| Grouping | OU | Mgmt Group | Folder |
| Account / Sub / Proj | Account | Subscription | Project |
| Resource grouping | Tags | Resource Group | (no native; via labels) |
| Billing | Per account | Per sub | Per project (multi-project per billing) |

## Labels (vs Tags)

```bash
gcloud projects update myproj --update-labels=env=prod,team=a
```

Labels = AWS tags. K=V.

Used for cost reports, filters.

## Identity Boundaries

Project: most resource access boundary.
Org: identity boundary (via IAM Org Policy).

## Multi-Project Patterns

### Shared VPC
Host project owns VPC; service projects use it:
```bash
gcloud compute shared-vpc enable HOST_PROJ
gcloud compute shared-vpc associated-projects add SERVICE_PROJ --host-project=HOST_PROJ
```

For: centralized network; distributed compute.

### Cross-Project IAM
SA in project A: granted role in project B.

For: shared services.

## Project Lifecycle

```bash
# Create
gcloud projects create ...

# Delete (30 day grace; recoverable)
gcloud projects delete PROJ

# Undelete (within 30 days)
gcloud projects undelete PROJ
```

## Best Practices

- Multi-project (per env / per workload)
- Folders for org structure
- Org Policy for guardrails
- Labels for cost / filter
- Shared VPC for network
- Naming convention strict

## Common Mistakes

- One project for everything (quotas, blast radius)
- No folders (sprawl)
- Wrong billing account
- API not enabled (cryptic errors)
- Project ID reuse (impossible after delete)

## Quick Refs

```bash
# Org
gcloud organizations list

# Folders
gcloud resource-manager folders create / list

# Projects
gcloud projects create / list / describe

# Billing
gcloud billing projects link

# APIs
gcloud services enable / list
```

## Interview Prep

**Junior**: "Project basics."

**Mid**: "GCP vs AWS vs Azure hierarchy."

**Senior**: "Org structure for FAANGM."

**Staff**: "Multi-project governance at scale."

## Next Topic

→ [T02 — IAM (Roles, Service Accounts, Workload Identity)](T02-IAM.md)
