# L07/C08/T01 — The IAM Mental Model (Principal, Action, Resource, Condition)

## Learning Objectives

- Reason about IAM permissions
- Design least-privilege

## The Four Elements

Every authorization check:
- **Principal**: who is acting (user, role, service)
- **Action**: what they're trying to do (read, write, delete)
- **Resource**: what they're acting on
- **Condition**: optional limits (time, IP, MFA, tags)

```
Can {Principal} perform {Action} on {Resource} under {Condition}?
```

## AWS IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowReadS3",
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:ListBucket"],
    "Resource": [
      "arn:aws:s3:::my-bucket",
      "arn:aws:s3:::my-bucket/*"
    ],
    "Condition": {
      "StringEquals": {
        "aws:SourceVpce": "vpce-xxx"
      }
    }
  }]
}
```

Effect: Allow or Deny. Deny always wins.

## Policy Types

### Identity-Based
Attached to user, group, or role:
```
User Alice ← Policy "ReadOnlyS3"
```

### Resource-Based
Attached to resource:
```
S3 Bucket ← Policy "Allow Alice"
```

Some resources support: S3, SQS, SNS, Lambda, KMS, IAM roles (trust policy).

### Both
For cross-account: identity policy in source + resource policy in target.

## Effect Evaluation

```
1. Explicit Deny anywhere → DENY
2. Allow in identity + resource policy → ALLOW
3. Allow only in identity → ALLOW (same account)
4. Allow only in resource → ALLOW (cross-account)
5. Neither → DENY (implicit)
```

Deny wins. Explicit Allow needed somewhere.

## Principals

### IAM User
Has access keys / password. For humans or legacy apps.

Avoid: prefer federated (SSO) for humans; roles for apps.

### IAM Role
Assumed temporarily; returns STS temp credentials.

Used for:
- EC2 instance profile
- Lambda execution role
- Cross-account access
- Federated user (after SAML/OIDC exchange)

### Service-Linked Role
AWS-managed role for services (e.g., AutoScaling, ECS). You can't edit; service uses for its operations.

### Federated User
SAML / OIDC: external identity provider; STS assumes role.

## Actions

Service-specific. Format: `service:Action`.
- `s3:GetObject`
- `ec2:RunInstances`
- `iam:CreateUser`

Wildcards: `s3:*`, `s3:Get*`.

## Resources

ARN format: `arn:aws:service:region:account:resource`.

Examples:
- `arn:aws:s3:::my-bucket`
- `arn:aws:s3:::my-bucket/*`
- `arn:aws:ec2:us-east-1:123:instance/i-xxx`
- `arn:aws:iam::123:role/MyRole`

Wildcards in some places (paths in S3; not account).

## Conditions

Refine by context:
- `aws:SourceIp`: from specific IP
- `aws:RequestTime`: time window
- `aws:MultiFactorAuthPresent`: MFA used
- `aws:TagKeys`: required tags
- `s3:prefix`: only certain key prefix
- `kms:EncryptionContext`: KMS context match

Powerful for fine-grained control.

## Permissions Boundary

Max permissions a role / user can have. Attached separately.

Use case: dev creates role; org constrains via boundary.

## SCP (Service Control Policy)

Org-level guardrail. Applies to all in account / OU.
```json
{
  "Effect": "Deny",
  "Action": "*",
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {
      "aws:RequestedRegion": ["us-east-1", "us-west-2"]
    }
  }
}
```

Prevents use of disallowed regions.

## Trust Policy (Roles)

Who can assume the role:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Service": "ec2.amazonaws.com"
    },
    "Action": "sts:AssumeRole"
  }]
}
```

For EC2 instance to use role.

For cross-account:
```json
{
  "Principal": {"AWS": "arn:aws:iam::OTHER:role/SomeRole"},
  "Action": "sts:AssumeRole",
  "Condition": {
    "StringEquals": {"sts:ExternalId": "shared-secret"}
  }
}
```

## STS

Security Token Service. Issues temporary credentials.

```bash
aws sts assume-role --role-arn arn:... --role-session-name me
```

Returns:
- AccessKeyId
- SecretAccessKey
- SessionToken
- Expiration

Use these for API calls.

## EC2 Instance Profile

Role attached to EC2; available via metadata service (`169.254.169.254`). SDKs auto-discover.

Why: no static keys on instance.

## Lambda Execution Role

Role used by Lambda function. Define in role; Lambda picks up automatically.

## IAM Roles for Service Accounts (IRSA)

In EKS: K8s ServiceAccount can assume AWS IAM role (via OIDC):
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123:role/myRole
```

Pod using this SA gets temp AWS creds. Best practice for EKS apps.

## Least Privilege

Grant minimum needed:
- Specific actions (not `*`)
- Specific resources (not `*`)
- Specific conditions

Hard in practice; iterate.

Tools:
- IAM Access Analyzer: suggest tightening
- CloudTrail: what's actually used
- IAM Last Accessed: prune unused

## Common Mistakes

- `*` on all
- AdministratorAccess on humans
- Static keys (rotate or replace with roles)
- Cross-account without ExternalId
- Resource-based + identity-based confusion
- SCPs blocking required actions

## Permission Boundary vs SCP

| | SCP | Boundary | Inline/Managed Policy |
|---|---|---|---|
| Scope | OU/Account | Role/User | Role/User |
| Set by | Org admin | Account admin | IAM admin |
| Effect | Max allowed | Max allowed | Grant |
| Bypass | No | No (within bounds) | n/a |

## Cross-Account

```
Source Account 111:
  Role X with policy allowing sts:AssumeRole on arn:aws:iam::222:role/Y

Target Account 222:
  Role Y with trust policy allowing 111:role/X to assume
  Plus permissions Y has
```

Standard pattern. ExternalId for added security.

## IAM for Humans

Avoid IAM users. Instead:
- Identity provider (Okta, Auth0, Azure AD)
- AWS SSO / Identity Center
- Federated to AWS via SAML / OIDC
- Assumes role per session

Console login: federated.
CLI: `aws sso login`.

## CLI Auth Methods

- Access keys in `~/.aws/credentials` (bad for humans)
- Profile with role assumption
- AWS SSO (`aws sso login`)
- IAM Roles Anywhere (for on-prem)
- ECS/Lambda/EC2 roles (auto)

## Policy Patterns

### Read-only
```json
{
  "Effect": "Allow",
  "Action": ["s3:Get*", "s3:List*"],
  "Resource": "*"
}
```

### Per-team
```json
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": [
    "arn:aws:s3:::team-a-*",
    "arn:aws:s3:::team-a-*/*"
  ]
}
```

### Tagged Resources Only
```json
{
  "Condition": {
    "StringEquals": {"aws:ResourceTag/Team": "${aws:PrincipalTag/Team}"}
  }
}
```

## Audit

- CloudTrail: every API call (who, what, when)
- IAM Access Analyzer: external sharing
- Trusted Advisor: best practices

Review monthly.

## Interview Prep

**Junior**: "User vs role."

**Mid**: "Cross-account access — design."

**Senior**: "Audit IAM policies for org."

**Staff**: "Least-privilege automation."

## Next Topic

→ [T02 — Roles vs Users vs Service Accounts](T02-Roles-Users-SAs.md)
