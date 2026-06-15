# L08/C01 — Account Setup & Organizations

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Root-MFA-Billing.md) | Root Account, MFA, Billing Alarms | 0.5 hr |
| [T02](T02-Organizations-SCPs.md) | AWS Organizations, SCPs, OUs | 1.5 hr |
| [T03](T03-Control-Tower.md) | Control Tower & Landing Zones | 1 hr |

## Account Hygiene

### Root Account
- One root per AWS account
- Hardware MFA mandatory
- Don't use root for daily tasks
- Lock away credentials
- Audit root use in CloudTrail
- Remove root access keys (if any)

### Billing Alarms
First thing in any new account:
```
Billing → Budgets → Create budget
- Type: Cost budget
- Period: Monthly
- Threshold: $50, $100, $500 (graduated)
- Action: SNS to email/Slack
```

### Account Aliasing
- Make login URLs friendly: `<alias>.signin.aws.amazon.com`
- Aliases are organization-unique

## AWS Organizations

The multi-account control plane.

```
Organization (Management account)
├── OU: Security
│   ├── Account: Audit
│   └── Account: Log Archive
├── OU: Production
│   ├── Account: prod-payments
│   └── Account: prod-data
├── OU: Non-Production
│   ├── Account: dev
│   └── Account: staging
└── OU: Sandbox
    └── Account: sandbox-*
```

Why multiple accounts:
- **Blast radius** — limit damage from one breach/error
- **Cost tracking** — per-account billing
- **Compliance** — separate prod from non-prod
- **IAM simplification** — per-account least privilege
- **Service limits** — quotas are per-account
- **Team autonomy** — teams own their accounts

## SCPs (Service Control Policies)

Org-level deny/allow rules applied to OUs/accounts.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyRegions",
      "Effect": "Deny",
      "NotAction": [
        "iam:*", "support:*", "organizations:*", "cloudfront:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": ["us-east-1", "us-east-2"]
        }
      }
    }
  ]
}
```

SCPs are **deny boundaries**. They limit what permissions identity policies can grant.

### Common SCPs
- Deny outside approved regions
- Deny S3 bucket public access settings
- Require encryption (deny `s3:PutObject` without SSE)
- Deny disabling CloudTrail / Config / GuardDuty
- Deny root user actions
- Deny IAM user creation (force SSO + roles)
- Deny removing required tags

## Control Tower

Managed multi-account setup. Provisions:
- Management account
- Log archive account
- Audit account
- Guardrails (preventive SCPs + detective Config rules)
- Account Factory for vending new accounts

Use case: greenfield or org transformation; gives you a "best-practice" baseline fast.

Alternatives: build it yourself (more flexible, more work) using:
- Organizations + SCPs
- IAM Identity Center (formerly SSO)
- Centralized logging (org-level CloudTrail, Config aggregator)
- AFT (Account Factory for Terraform) for IaC-driven account vending

## Landing Zone

A "ready-for-prod" account framework:
- Org structure (OUs, accounts)
- SCPs by OU
- VPCs with standard CIDR scheme
- Centralized logging (CloudTrail org trail → log archive bucket)
- Centralized monitoring (CloudWatch, Config aggregator)
- IAM Identity Center for SSO
- Network hub (Transit Gateway in network account)
- Standard tagging policy
- Default GuardDuty + Security Hub

## CIDR Planning

For multi-account VPCs, plan CIDR space up front:
```
10.0.0.0/8  → org space
10.0.0.0/16 → shared services
10.1.0.0/16 → prod
10.2.0.0/16 → staging
10.3.0.0/16 → dev
10.10.0.0/16 → tenant 1
...
```

Avoid CIDR collisions for peering / TGW.

## Multi-Account Cost Tracking

- Cost allocation tags (must enable; cost takes 24h to appear)
- Consolidated billing (org-level)
- CUR (Cost & Usage Reports) → Athena queries
- Cost Categories (custom rollups)

## Interview Themes

- "Walk me through account organization for a 100-engineer company"
- "What are SCPs and how do they work?"
- "Why Control Tower vs roll-your-own?"
- "Design CIDR for a multi-account environment"
- "Common landing zone components"
