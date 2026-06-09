# L08/C02/T01 — Users, Groups, Roles, Policies

## Learning Objectives

- Use IAM building blocks
- Apply correctly per use case

## Building Blocks

| | Purpose |
|---|---|
| User | Long-lived identity (human or app legacy) |
| Group | Collection of users (for policy attach) |
| Role | Temporary identity (assumed) |
| Policy | JSON document with permissions |

## Users

Avoid creating new ones; prefer SSO.

When you must:
- Service accounts (rare; prefer roles)
- Legacy apps (rare; prefer roles via instance profile)

Has: access keys (long-lived; bad), console password (rare).

```bash
aws iam create-user --user-name alice
aws iam create-access-key --user-name alice    # returns AccessKeyId + SecretAccessKey
```

Stored in `~/.aws/credentials`.

Rotate keys: 90 days max.

## Groups

Collection of users; policy attached once; affects all members.

```bash
aws iam create-group --group-name Developers
aws iam attach-group-policy --group-name Developers --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
aws iam add-user-to-group --user-name alice --group-name Developers
```

Group ≠ role; group can't be assumed.

## Roles

The right abstraction for most things.

```bash
aws iam create-role --role-name MyAppRole --assume-role-policy-document file://trust.json
aws iam attach-role-policy --role-name MyAppRole --policy-arn ...
```

### Trust Policy
Who can assume:
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

Service principals:
- ec2.amazonaws.com
- lambda.amazonaws.com
- ecs-tasks.amazonaws.com
- glue.amazonaws.com
- ...

Or AWS account:
```json
{"Principal": {"AWS": "arn:aws:iam::OTHER_ACCT:root"}}
```

Or federated:
```json
{"Principal": {"Federated": "arn:aws:iam::ACCT:saml-provider/Okta"}}
```

### Permissions Policy
What the role can do (attached separately).

## Policies

Identity-based:
- Managed (AWS or customer-managed; reusable)
- Inline (embedded in one user/role/group; one-off)

Use managed when possible (reuse, single source).

### Anatomy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadS3",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:SourceVpc": "vpc-xxx"
        }
      }
    }
  ]
}
```

## AWS Managed Policies

Pre-built:
- `AdministratorAccess`
- `PowerUserAccess` (everything except IAM)
- `ReadOnlyAccess`
- Service-specific: `AmazonS3FullAccess`, etc.

Use for testing; avoid for production (often too broad).

## Customer-Managed Policies

You write; tighter scoped.

```bash
aws iam create-policy --policy-name S3ReadOnlyMyBucket --policy-document file://policy.json
```

Attach to multiple users/roles.

Version controlled (Git!). Apply via CI.

## Policy Limits

- 6144 chars inline
- 6144 chars per managed policy version
- 10 managed policies per user / role
- 5 versions per managed policy

Hit limits at scale; restructure.

## Wildcards

```json
"Action": "s3:*"
"Action": "s3:Get*"
"Action": ["s3:GetObject", "s3:PutObject"]
```

```json
"Resource": "arn:aws:s3:::my-bucket/*"
"Resource": "*"
```

Avoid `*` on Action AND Resource unless intended.

## Variables

```json
"Resource": "arn:aws:s3:::my-bucket/${aws:username}/*"
```

Per-user prefix.

## Conditions

```json
"Condition": {
  "StringEquals": {"aws:RequestedRegion": "us-east-1"},
  "Bool": {"aws:MultiFactorAuthPresent": "true"},
  "DateGreaterThan": {"aws:CurrentTime": "2024-01-01T00:00:00Z"}
}
```

All conditions must be true. Within same operator type, OR. Across types, AND.

## NotAction, NotResource, NotPrincipal

Inverse:
```json
"Effect": "Allow",
"NotAction": ["iam:*"],
"Resource": "*"
```

Tricky; usually clearer to list specifically.

## Effect: Deny

Use sparingly. Common cases:
- Block specific dangerous action
- Defend against accidental over-grant
- Org-wide guardrails (SCP)

```json
{
  "Effect": "Deny",
  "Action": "iam:DeleteUser",
  "Resource": "*",
  "Condition": {
    "StringEquals": {"aws:userid": "important-user"}
  }
}
```

## Evaluation

Per request:
1. Default DENY
2. Apply SCP (if any) → if denied, DENY
3. Apply identity policy → if denied explicitly, DENY
4. Apply resource policy → if denied explicitly, DENY
5. If any Allow: ALLOW
6. Else: DENY

Explicit Deny anywhere wins.

## Common Use Cases

### EC2 Role
```
Trust: ec2.amazonaws.com
Permissions: read specific S3, write CloudWatch
```

Attach as instance profile.

### Lambda Role
```
Trust: lambda.amazonaws.com
Permissions: read SQS, write DynamoDB, write logs
```

### Cross-Account Role
```
Trust: other AWS account (with ExternalId)
Permissions: limited to required actions
```

### CI/CD Role
```
Trust: GitHub OIDC
Permissions: specific deploy actions
```

## IAM Access Analyzer

Free service. Flags:
- Resources accessible from outside org
- Unused IAM permissions
- Potential issues

Run regularly.

## Last Accessed

```bash
aws iam generate-service-last-accessed-details --arn arn:aws:iam::123:role/MyRole
```

Shows services not accessed; candidates for permission removal.

## Best Practices

- No `*` on Action AND Resource
- Managed > inline
- Reuse via groups (for users)
- Roles > users for apps
- MFA for sensitive ops (condition)
- Rotate keys
- Use AWS IAM Identity Center / SSO

## Common Mistakes

- AdministratorAccess on humans
- Hardcoded keys in code
- IAM user for app on EC2 (use instance profile)
- Inline policy proliferation
- Forgetting Resource (defaults to `*`)
- Conditions on wrong attribute

## Quick Refs

```bash
# Whoami
aws sts get-caller-identity

# List users
aws iam list-users

# Get policy
aws iam get-policy-version --policy-arn ... --version-id v1

# Simulate
aws iam simulate-principal-policy --policy-source-arn ... --action-names s3:GetObject --resource-arns ...
```

## Interview Prep

**Junior**: "User vs role."

**Mid**: "Cross-account access setup."

**Senior**: "Audit IAM for over-privileged roles."

**Staff**: "IAM for 100-team org."

## Next Topic

→ [T02 — Trust Policies vs Permission Policies](T02-Trust-Policy.md)
