# L08/C01/T03 — Control Tower & Landing Zones

## Learning Objectives

- Use Control Tower for multi-account
- Build landing zone

## Control Tower

AWS service: automated multi-account governance. Set up Organizations + Identity Center + guardrails + logging.

Replaces manual setup.

## What It Sets Up

1. **Organizations**: with foundational OUs
2. **Identity Center**: SSO directory
3. **Log Archive Account**: centralized CloudTrail / Config logs
4. **Audit Account**: security tooling (GuardDuty, Security Hub)
5. **Guardrails**: preventive (SCP) + detective (Config rules)
6. **Account Factory**: provision new accounts

## Foundational OUs

- Foundational
  - Log Archive
  - Audit
- Sandbox
- Custom (you add)

## Guardrails

### Mandatory
Always on. Can't disable. Like:
- Block public S3 logging bucket
- Enable CloudTrail
- Enable Config

### Strongly Recommended
Best-practice defaults. Recommended on. Can disable.

### Elective
Optional. You enable.

Examples:
- Disallow IAM access keys creation
- Require MFA
- Block region X
- Encrypt EBS

Implemented as SCPs + Config rules.

## Account Factory

Provisioning new accounts:
```
Account Factory → Create new account
- Email
- AccountName
- OU
```

Behind scenes:
- Creates account in Org
- Joins OU (inherits SCPs)
- Joins SSO
- Enables baseline (CloudTrail, Config)
- Email confirmation

Templated: every new account has consistent baseline.

## Customizations for Control Tower (CfCT)

For things Control Tower doesn't do natively (e.g., custom SCP, additional tooling per OU):

Define in CodeCommit; CfCT applies on new accounts.

Or use Account Factory for Terraform (AFT): Terraform-driven account provisioning.

## Landing Zone Concept

Pre-configured multi-account environment ready for workloads:
- Org structure
- Baseline guardrails
- Networking (TGW, shared VPC)
- IAM / SSO
- Logging
- Tooling (security, monitoring)

Workload teams come in; deploy apps; trust baseline.

## Pre-Control Tower Landing Zone

AWS Landing Zone Solution (legacy): CloudFormation StackSet-based. Maintenance heavy.

Control Tower simpler; recommended.

## Beyond Control Tower

Mature orgs need more:
- Custom networking (TGW, custom egress)
- Service catalog (approved services)
- Identity governance
- Cost allocation
- DR / backup policies

Build atop Control Tower foundation.

## Account Strategy

Per Control Tower defaults:
- 1 management account
- 1 log archive account (Foundational OU)
- 1 audit account (Foundational OU)
- N workload accounts (in custom OUs)

## OU Recommendation

```
Root
├── Foundational
│   ├── Log Archive
│   └── Audit
├── Production
│   ├── prod-app1
│   ├── prod-app2
│   └── prod-shared
├── Non-Production
│   ├── dev-app1
│   ├── staging-app1
│   └── sandbox-engineers
├── Suspended
└── Transitional (during M&A etc.)
```

## Cross-Account Resource Sharing

### RAM (Resource Access Manager)
Share resources across accounts:
- VPC subnets (one account owns VPC; others use subnets)
- TGW
- License (specific software)
- Route53 Resolver rules

Reduces duplicated infra. Central networking account.

### Cross-Account S3
Bucket in account A; read/write from B via bucket policy.

### Cross-Account KMS
Key in A; used by B via key policy.

## Centralized Logging

Log Archive account:
- CloudTrail for all accounts (Organization Trail)
- Config snapshots
- VPC Flow Logs (optional centralization)
- App logs (centralize via CloudWatch cross-account or Loki/etc.)

## Centralized Networking

Network account:
- TGW
- Direct Connect
- Egress VPC (single NAT GW serving all)
- DNS (Route53 Resolver)

Workload accounts attach to TGW; route Internet via central egress.

Saves money (one NAT vs many); centralizes inspection.

## Centralized Security

Security account:
- Security Hub
- GuardDuty admin
- Macie
- Inspector
- Audit role to view all accounts

## Cost Allocation

Tags + Cost Explorer + per-account view. AWS Cost & Usage Report (CUR) for deep analysis.

## Anti-Patterns

- Workloads in management account
- Skipping log archive account
- Loose SCPs
- No tag enforcement
- Sandbox accounts without spend caps

## Best Practices

- Workload accounts: app-specific
- Sandbox accounts: per engineer; aggressive cleanup
- Production: locked SCP
- Centralize: network, logs, security, identity

## Common Mistakes

- Control Tower over existing chaotic Org (hard to migrate)
- Disabling mandatory guardrails (you can't; that's the point)
- Per-team customization fragmentation
- No documentation of OU policies

## CfCT vs AFT

- **CfCT**: AWS-native customizations
- **AFT**: Terraform-based; more flexible
- **Custom**: build your own

AFT is most popular for tf-heavy orgs.

## Pricing

Control Tower: free.
But: enables Config (per resource per region; can be expensive at scale).
CloudTrail: free standard trail; extra for advanced features.
GuardDuty / Security Hub: per resource / data.

Multi-account governance: 5-10% bill addition typical.

## Multi-Region Considerations

Each region:
- Has its own Config recorder
- Has its own CloudTrail (per region, or org trail covers all)
- Has its own VPC

Cost adds up; restrict regions where possible.

## Drift Detection

If admin modifies guardrail config manually: drift detected; can re-enroll.

Don't bypass guardrails; raise exception via process.

## Migration from Existing Org

If you have an Org but no Control Tower:
- Set up Control Tower (it adopts existing Org)
- Migrate accounts to managed OUs
- Enroll one at a time

Takes weeks. Plan carefully.

## Quick Refs

```bash
# List Control Tower landing zone / enabled controls
aws controltower list-landing-zones
aws controltower list-enabled-controls --target-identifier arn:aws:organizations::...:ou/o-xxxx/ou-xxxx

# Enable a control (guardrail) on an OU
aws controltower enable-control --control-identifier arn:aws:controltower:...::control/AWS-GR_... --target-identifier arn:...:ou/o-xxxx/ou-xxxx

# Share a resource across accounts via RAM
aws ram create-resource-share --name shared-subnets --resource-arns arn:aws:ec2:...:subnet/subnet-xxxx --principals 111122223333
```

## Interview Prep

**Mid**: "What does Control Tower do?"

**Senior**: "Landing zone design for 100-team org."

**Staff**: "Multi-account governance from scratch."

## Next Topic

→ Move to [L08/C02 — IAM Mastery](../C02/README.md)
