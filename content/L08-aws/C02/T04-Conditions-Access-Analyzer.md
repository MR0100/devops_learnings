# L08/C02/T04 — Conditions, IAM Access Analyzer

## Learning Objectives

- Use conditions for tight policies
- Use Access Analyzer

## Conditions

Refine policy by request context:
```json
"Condition": {
  "StringEquals": {"aws:RequestedRegion": "us-east-1"},
  "Bool": {"aws:MultiFactorAuthPresent": "true"}
}
```

All operators in a Condition block: AND.
Multiple values for same key (in array): OR.

## Condition Operators

- **String**: StringEquals, StringNotEquals, StringLike, StringNotLike
- **Numeric**: NumericEquals, NumericGreaterThan, etc.
- **Date**: DateEquals, DateGreaterThan, etc.
- **Bool**: Bool
- **Binary**: BinaryEquals
- **IP**: IpAddress, NotIpAddress (with CIDR)
- **ARN**: ArnEquals, ArnLike, ArnNotEquals
- **Null**: Null (key present?)

`IfExists` suffix: only checks if key present (`StringEqualsIfExists`).

## Global Condition Keys

Always available:
- `aws:CurrentTime`: ISO 8601 time
- `aws:RequestedRegion`: region of request
- `aws:SecureTransport`: HTTPS?
- `aws:SourceIp`: caller IP
- `aws:SourceVpc`: source VPC
- `aws:SourceVpce`: source VPC endpoint
- `aws:userid`: principal ID
- `aws:username`: name
- `aws:PrincipalArn`: full ARN
- `aws:PrincipalTag/X`: tags on principal
- `aws:ResourceTag/X`: tags on resource
- `aws:MultiFactorAuthPresent`: MFA used?
- `aws:MultiFactorAuthAge`: seconds since MFA
- `aws:ViaAWSService`: through AWS service?
- `aws:CalledVia`: chain of services

## Service-Specific Keys

Each service has more. Examples:
- `s3:prefix`: S3 key prefix
- `s3:RequestObjectTag/X`: tag in request
- `kms:EncryptionContext:X`: KMS context
- `iam:PassedToService`: which service receives passed role

Check service docs.

## Powerful Conditions

### MFA Required
```json
"Condition": {
  "Bool": {"aws:MultiFactorAuthPresent": "true"},
  "NumericLessThan": {"aws:MultiFactorAuthAge": "3600"}    // last hour
}
```

### Specific Source IP
```json
"Condition": {
  "IpAddress": {
    "aws:SourceIp": ["192.168.0.0/16", "10.0.0.0/8"]
  }
}
```

### Time Window
```json
"Condition": {
  "DateGreaterThan": {"aws:CurrentTime": "2024-01-01T00:00:00Z"},
  "DateLessThan": {"aws:CurrentTime": "2024-12-31T23:59:59Z"}
}
```

For temporary access.

### Through VPC Endpoint Only
```json
"Condition": {
  "StringNotEquals": {"aws:SourceVpce": "vpce-xxxxx"}
}
"Effect": "Deny"
```

S3 only accessible via VPC endpoint.

### Tag-Based (ABAC)
```json
"Condition": {
  "StringEquals": {
    "aws:ResourceTag/Team": "${aws:PrincipalTag/Team}"
  }
}
```

User can access resources tagged with their team.

### HTTPS Required
```json
"Condition": {"Bool": {"aws:SecureTransport": "false"}}
"Effect": "Deny"
```

## Chained Service Calls

`aws:CalledVia`: services chain.

Example: User → CloudFormation → Lambda.
`aws:CalledVia` = `["cloudformation.amazonaws.com"]`.

Restrict based on which AWS service is in chain.

## ABAC

Attribute-Based: tag-based access. Scales with org.

Setup:
- Tag principals (Department, Team)
- Tag resources (Department, Team)
- Policies match attributes

One policy serves many:
```json
{
  "Effect": "Allow",
  "Action": "ec2:*",
  "Resource": "*",
  "Condition": {
    "StringEquals": {
      "aws:ResourceTag/Team": "${aws:PrincipalTag/Team}"
    }
  }
}
```

Each team member operates their team's resources.

## IAM Access Analyzer

Service that detects:
- Resources accessible from outside the zone of trust (your account / org)
- Unused IAM permissions

Free.

### Finding External Access
Analyzes S3, KMS, IAM, Lambda, SQS, Secrets Manager for permissions granted to:
- Other AWS accounts
- Anonymous (`*`)
- Federated identities

If unexpected: investigate.

### Unused Permissions
Lists actions never used per role over X days. Tighten policy.

### Validation
Validates policy JSON for:
- Errors (syntax)
- Warnings (overly broad)
- Suggestions (best practices)

```bash
aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document file://policy.json
```

Use in CI before deploy.

### Policy Generation
Reads CloudTrail; generates least-privilege policy for that role's actual usage.

## Policy Simulator

Test policy:
```bash
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123:role/MyRole \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-bucket/file.txt
```

Returns: Allowed / Denied. Useful before deploy.

## CloudTrail for IAM

Every API call logged. Filter for IAM events:
- `iam:CreateUser`
- `iam:AttachUserPolicy`
- `sts:AssumeRole`

Alert on unusual (e.g., AssumeRole at 3 AM from new IP).

## Best Practices

- Add Conditions to tighten broad policies
- Use ABAC for scale
- MFA condition for high-risk actions
- IP / VPC endpoint conditions for sensitive resources
- Run Access Analyzer continuously
- Generate policies from CloudTrail; don't write blind

## Common Mistakes

- Conditions don't apply to wrong action key (each service has specifics)
- IfExists vs strict
- Mixing AND/OR within Condition unclearly
- Forgetting global keys (aws:RequestedRegion etc.)
- ABAC without consistent tagging

## Examples

### Restrict EC2 by Tag
```json
{
  "Effect": "Allow",
  "Action": ["ec2:StartInstances", "ec2:StopInstances"],
  "Resource": "*",
  "Condition": {
    "StringEquals": {"ec2:ResourceTag/Environment": "dev"}
  }
}
```

Can only start/stop dev instances.

### S3 List by Prefix
```json
{
  "Effect": "Allow",
  "Action": "s3:ListBucket",
  "Resource": "arn:aws:s3:::my-bucket",
  "Condition": {
    "StringLike": {
      "s3:prefix": "${aws:username}/*"
    }
  }
}
```

Each user can only list their own prefix.

### Time-Limited Vendor Access
```json
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*",
  "Condition": {
    "DateLessThan": {"aws:CurrentTime": "2024-08-01T00:00:00Z"}
  }
}
```

Access expires Aug 1.

## Quick Refs

```bash
# Validate a policy document (use in CI)
aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document file://policy.json

# Create an account analyzer
aws accessanalyzer create-analyzer --analyzer-name account --type ACCOUNT

# List external-access findings
aws accessanalyzer list-findings --analyzer-arn arn:aws:access-analyzer:...:analyzer/account

# Simulate whether a principal is allowed an action
aws iam simulate-principal-policy --policy-source-arn arn:aws:iam::123:role/MyRole \
  --action-names s3:GetObject --resource-arns arn:aws:s3:::my-bucket/file.txt
```

## Interview Prep

**Mid**: "MFA-required IAM policy."

**Senior**: "ABAC vs RBAC."

**Staff**: "Use Access Analyzer findings."

## Next Topic

→ [T05 — IAM Roles for Service Accounts (IRSA)](T05-IRSA.md)
