# L08/C01/T02 — AWS Organizations, SCPs, OUs

## Learning Objectives

- Manage many accounts
- Use SCPs to enforce policy

## AWS Organizations

Multi-account container. Free.

Hierarchy:
- Management account (root payer)
- OUs (Organizational Units): tree
- Accounts: leaves

Pattern:
```
Management Account (payer; minimal resources)
├── Security OU
│   ├── log-archive
│   ├── audit (security tools)
│   └── identity (SSO)
├── Production OU
│   ├── prod-team-a
│   ├── prod-team-b
│   └── prod-shared-services
├── Non-Prod OU
│   ├── dev-team-a
│   ├── staging-team-a
│   └── sandbox-engineer-1
└── Suspended OU (for deletion)
```

Many accounts because: blast radius, billing separation, governance.

## Consolidated Billing

All accounts pay through management account. Volume discounts apply across accounts.

Reserved Instance / Savings Plan sharing across org.

## SCPs (Service Control Policies)

Org-wide guardrails. Restrict what IAM can grant in member accounts.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyOutsideRegions",
    "Effect": "Deny",
    "Action": "*",
    "Resource": "*",
    "Condition": {
      "StringNotEquals": {
        "aws:RequestedRegion": ["us-east-1", "us-west-2"]
      }
    }
  }]
}
```

Attached to OU / account. Apply to ALL principals in that scope (except root).

### Important: SCPs DON'T grant

They cap permissions. Identity / resource policies grant; SCPs limit.

If SCP denies, no policy can override (except for root).

### Useful SCPs

#### Region Restriction
Block resources outside approved regions.

#### Service Restriction
Block use of disallowed services.
```json
{
  "Effect": "Deny",
  "Action": ["sagemaker:*", "iot:*"],
  "Resource": "*"
}
```

#### No Public S3
```json
{
  "Effect": "Deny",
  "Action": "s3:PutBucketPublicAccessBlock",
  "Resource": "*",
  "Condition": {
    "StringEqualsIgnoreCase": {"aws:ResourceTag/Public": "false"}
  }
}
```

#### Force Encryption
Block creating unencrypted EBS, S3:
```json
{
  "Effect": "Deny",
  "Action": "ec2:RunInstances",
  "Resource": "arn:aws:ec2:*:*:volume/*",
  "Condition": {
    "Bool": {"ec2:Encrypted": "false"}
  }
}
```

#### Protect CloudTrail
Prevent disabling:
```json
{
  "Effect": "Deny",
  "Action": [
    "cloudtrail:StopLogging",
    "cloudtrail:DeleteTrail"
  ],
  "Resource": "*"
}
```

#### Protect IAM
```json
{
  "Effect": "Deny",
  "Action": ["iam:DeleteRole"],
  "Resource": ["arn:aws:iam::*:role/OrganizationAccountAccessRole"]
}
```

## OU Strategy

By environment + team + function. Common patterns:

### By Environment
```
Production OU
Non-Production OU
Sandbox OU
```

Different SCPs per env. Prod: locked. Dev: permissive.

### By Business Unit
```
Finance OU
Engineering OU
Marketing OU
```

For multi-BU companies.

### Workload
```
Workloads OU
  └── Per-app OUs / accounts
Infrastructure OU
  └── Per-shared-service accounts
```

## Account Per Workload

Modern best practice. Each major workload / team gets own AWS account.

Pros:
- Blast radius limited
- IAM cleaner
- Billing per workload
- Different SCPs

Cons:
- More accounts to manage
- Cross-account complexity (VPC peering, IAM)
- DNS, networking shared via central accounts

## Cross-Account Access

App in Account A needs S3 in Account B:
- Account B's S3 bucket policy allows Account A
- Account A's role has S3 permissions

Or assume role:
- Account A's role assumes Account B's role
- Use Account B's role to access B's resources

## Cross-Account Logging

Central log-archive account:
- Receives CloudTrail from all
- S3 / Athena for analysis
- Tighter access

Send via Organization Trail (one trail covers all accounts).

## SSO / Identity Center

Set up SSO at org level:
- Users in Identity Center (or external IdP)
- Permission Sets (templates)
- Assign permission sets to user × account

User logs in once; sees all their accounts; assumes role per account.

## Service-Linked Roles

Some SCPs would block AWS itself. Exception: service-linked roles for AWS services (named by AWS).

## Testing SCPs

DON'T deploy untested SCPs widely. They can lock you out.

Process:
1. Test in sandbox OU
2. Apply to specific test account
3. Validate (try operations that should work / fail)
4. Roll out to wider

## Removing Account

```bash
aws organizations leave-organization      # member leaves
aws organizations remove-account --account-id ...   # management removes
```

Account becomes standalone. Pays own bill from then on.

## Tagging Policies

Enforce tagging consistency:
```json
{
  "tags": {
    "Environment": {
      "tag_value": {"@@assign": ["prod", "staging", "dev"]}
    }
  }
}
```

Apply at org / OU. Reports non-compliant resources.

## Backup Policies

Org-wide AWS Backup plans. Apply to OU; backs up tagged resources across accounts.

## Service Quotas

Org-level requests propagate. One request raises limit across accounts.

## Common Patterns

### Sandbox Account
- Each engineer's own AWS account
- Spending cap; auto-shutdown nightly
- Wide SCP allowing most services
- Auto-cleanup of resources weekly

### Per-Team Production
- Team owns prod account
- SCP restricts non-prod-grade services
- Centralized logging + monitoring

### Shared Services
- Networking (TGW hub) in shared account
- DNS (Route53) in shared
- Container registry (ECR) in shared

## Account Creation

```bash
aws organizations create-account \
  --email aws+team-a-prod@company.com \
  --account-name "Team A Production"
```

Automatically:
- Account joins org
- Role "OrganizationAccountAccessRole" created (management can assume)

## Anti-Patterns

- One huge account (no blast radius)
- SCPs that lock out admins
- No tagging
- Default VPC kept
- Org without SSO

## Common Mistakes

- SCP on management account (different behavior)
- Forgetting service-linked role exceptions
- Region SCP missing IAM (IAM is global)
- Deny without thinking about side effects

## Best Practices

- Start with strict; loosen as needed
- Test SCPs in sandbox
- Document each SCP's purpose
- Review OUs quarterly
- Set service quotas org-wide
- Backup policies org-wide
- One IdP for org

## Interview Prep

**Mid**: "Why multi-account."

**Senior**: "SCP for region restriction."

**Staff**: "Org design for 200 microservices."

## Next Topic

→ [T03 — Control Tower & Landing Zones](T03-Control-Tower.md)
