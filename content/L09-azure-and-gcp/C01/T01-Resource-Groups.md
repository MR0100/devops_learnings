# L09/C01/T01 — Resource Groups, Subscriptions, Management Groups

## Learning Objectives

- Understand Azure org hierarchy
- Compare to AWS

## Hierarchy

```
Tenant (Entra ID)
└─ Management Group (optional)
   └─ Subscription (billing + access boundary)
      └─ Resource Group (mandatory container)
         └─ Resources (VMs, storage, etc.)
```

## Tenant

= Entra ID directory. One per organization (typically).

For: identity boundary.

## Management Groups

Hierarchical groups of subscriptions:
- Apply policies across many subs
- Hierarchical (4 levels max)

For: large orgs.

```
Root MG
├─ Production MG
│  ├─ Prod-Sub-A
│  └─ Prod-Sub-B
└─ Dev MG
   └─ Dev-Sub
```

Policy at "Production MG": applies to A and B.

## Subscription

Billing + access boundary:
- One bill per sub
- Quota per sub
- Like an AWS account

Multiple subs per tenant common:
- Prod / Dev / Test
- Per team
- Per cost center

## Resource Group (RG)

Mandatory container; logical grouping:
- Lifecycle (delete RG = delete contained)
- Region (RG has region; resources can be elsewhere)
- Tags (inherited optionally)
- RBAC scope

```bash
az group create --name myapp-prod --location eastus
```

For: app-aligned grouping.

## RG Strategies

### Per-App per-Env
```
myapp-prod-eastus
myapp-staging-eastus
myapp-dev-eastus
```

Clean separation.

### Per-Tier
```
myapp-prod-web
myapp-prod-db
```

Lifecycle distinct.

### Per-Lifecycle
Stable infra (network) separate from app churn:
```
myorg-network
myapp-prod-eastus
```

## Comparison to AWS

| | AWS | Azure |
|---|---|---|
| Identity | IAM (per account) | Entra ID (per tenant) |
| Account/Sub | Account | Subscription |
| Multi-account | Organizations | Management Groups |
| Grouping | Tags / no native | Resource Group (mandatory) |
| Region | Per-resource | Per-RG (and per-resource) |

## Naming

Azure recommends:
```
<workload>-<env>-<region>-<instance>
myapp-prod-eus2-001
```

For consistent identification.

## Subscriptions Strategy

### Single Sub
Small orgs. Less overhead.

### Multi-Sub
- Prod / Dev / Test
- Per team
- Per cost center
- Compliance boundary

For FAANGM scale: hundreds.

## Quotas

Per subscription:
- Cores
- IPs
- Resources
- API calls

Hit quota → resource creation fails.

```bash
az vm list-usage --location eastus
```

## Cross-Sub

Resources can reference across subs (with permission).

For: shared services in one sub; consumed by others.

## Policy

```bash
az policy assignment create \
  --name require-tags \
  --policy /providers/Microsoft.Authorization/policyDefinitions/... \
  --scope /providers/Microsoft.Management/managementGroups/Production
```

Policy at MG: cascades.

## RBAC Scope

Hierarchy:
```
MG → Sub → RG → Resource
```

Permission at higher: inherited.

```bash
az role assignment create \
  --assignee user@example.com \
  --role Contributor \
  --scope /subscriptions/SUB_ID/resourceGroups/myapp-prod
```

## Locks

```bash
az lock create --name dont-delete \
  --lock-type CanNotDelete \
  --resource-group myapp-prod
```

Prevent accidental deletion. Better than relying on humans.

For: prod RGs.

## Cost

Cost reported per:
- Sub (primary)
- RG (allocations)
- Tags (chargeback)

For: chargeback.

## Tagging

```bash
az group update --name myapp-prod --tags env=prod owner=team-a
```

Tags don't cascade by default; use Policy to enforce inheritance.

## Move Resources

```bash
az resource move --destination-group new-rg --ids /subscriptions/.../resourceGroups/old-rg/...
```

For: reorganization.

## Limitations

- Some resources can't move
- Some moves have downtime
- Subscription quotas

For: plan moves carefully.

## EA / CSP / PAYG

- Enterprise Agreement (EA): negotiated discount
- CSP: through reseller
- Pay-As-You-Go: standard

For enterprise: EA.

## Best Practices

- Mandatory tags (Policy)
- Per-app RG (lifecycle)
- Multi-sub for isolation
- MG hierarchy for policy
- Locks on prod
- Clear naming

## Common Mistakes

- Everything in one RG (chaos)
- No tags
- Sub sprawl (un-managed)
- Cross-region in single RG (consistency)

## Quick Refs

```bash
# Account / sub
az account list
az account show
az account set --subscription NAME

# RG
az group list
az group create --name NAME --location REGION
az group delete --name NAME

# Resources in RG
az resource list --resource-group NAME
```

## Interview Prep

**Junior**: "What's a Resource Group."

**Mid**: "Azure hierarchy."

**Senior**: "Multi-subscription strategy."

**Staff**: "Tenant + MG architecture for FAANGM."

## Next Topic

→ [T02 — Entra ID (formerly Azure AD)](T02-Entra-ID.md)
