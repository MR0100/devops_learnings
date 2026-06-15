# L08/C02/T03 — Resource-Based Policies

## Learning Objectives

- Apply resource-based policies
- Understand when needed

## What

Policy attached TO the resource (not to a user/role).

Resources supporting:
- S3 (bucket policies)
- SQS, SNS
- Lambda
- KMS (key policies — MANDATORY)
- IAM (trust policies on roles)
- Secrets Manager
- ECR repositories
- API Gateway
- VPC endpoints

NOT supported by: EC2, RDS, DynamoDB (use identity policy instead).

## S3 Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowRead",
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::123:role/MyRole"},
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::my-bucket/*"
  }]
}
```

Anyone matching principal can perform action.

### Public Access
```json
{"Principal": "*"}
```

DANGEROUS. Combined with Public Access Block (often: blocked).

### Force HTTPS
```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:*",
  "Resource": ["arn:aws:s3:::my-bucket", "arn:aws:s3:::my-bucket/*"],
  "Condition": {"Bool": {"aws:SecureTransport": "false"}}
}
```

### Cross-Account
```json
{
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::OTHER:root"},
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::my-bucket/*"
}
```

Plus OTHER account's user/role needs identity policy allowing it.

## SQS Queue Policy

```json
{
  "Effect": "Allow",
  "Principal": {"Service": "sns.amazonaws.com"},
  "Action": "sqs:SendMessage",
  "Resource": "arn:aws:sqs:us-east-1:123:my-queue",
  "Condition": {
    "ArnEquals": {"aws:SourceArn": "arn:aws:sns:us-east-1:123:my-topic"}
  }
}
```

Let SNS topic publish to queue. Source ARN restricts to specific topic.

## SNS Topic Policy

```json
{
  "Effect": "Allow",
  "Principal": "*",
  "Action": "SNS:Subscribe",
  "Resource": "arn:aws:sns:us-east-1:123:my-topic",
  "Condition": {
    "StringEquals": {"aws:SourceAccount": "456"}
  }
}
```

## KMS Key Policy

REQUIRED on every CMK. Without it, key unusable.

```json
{
  "Statement": [
    {
      "Sid": "RootAccess",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123:root"},
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "AppUse",
      "Effect": "Allow",
      "Principal": {"AWS": "arn:aws:iam::123:role/AppRole"},
      "Action": ["kms:Encrypt", "kms:Decrypt", "kms:GenerateDataKey"],
      "Resource": "*"
    }
  ]
}
```

Root statement: keeps account admin access (don't remove; lockout).

## Lambda Resource Policy

For who can invoke:
```json
{
  "Effect": "Allow",
  "Principal": {"Service": "events.amazonaws.com"},
  "Action": "lambda:InvokeFunction",
  "Resource": "arn:aws:lambda:us-east-1:123:function:MyFn",
  "Condition": {
    "ArnEquals": {"AWS:SourceArn": "arn:aws:events:us-east-1:123:rule/MyRule"}
  }
}
```

Auto-added when you wire EventBridge → Lambda via console.

## ECR Repository Policy

```json
{
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::OTHER:root"},
  "Action": [
    "ecr:GetDownloadUrlForLayer",
    "ecr:BatchGetImage",
    "ecr:BatchCheckLayerAvailability"
  ]
}
```

Cross-account image pulls.

## Cross-Account: Two Policies Needed

For account A's role to access account B's S3 bucket:
- B's bucket policy: Allow A's role
- A's identity policy: Allow s3:GetObject on B's bucket

Both. Either missing = no access.

## When Identity Policy Sufficient

Same account, resource doesn't support resource policy (RDS, DynamoDB):
- Only identity policy needed
- Resource accepts what identity allows

For S3 same-account: usually identity policy is enough (bucket policy not needed unless extra).

## When Resource Policy Needed

- Cross-account (B's policy needed)
- Anonymous (no identity to give policy)
- Specific service principal access
- Conditions specific to resource

## Evaluation Order

```
1. SCP applies → if Deny: DENY
2. Identity policy + Resource policy combined
3. If either explicitly Deny: DENY
4. If either Allow: ALLOW (in some cases need both)
5. Else: DENY (implicit)
```

Cross-account: BOTH must Allow. Same-account: EITHER Allow enough.

## Access Analyzer

Detects:
- Resources with policies granting external access
- Unintended public exposure
- Cross-account leak

Run continuously.

## Common Mistakes

### Bucket Public by Mistake
Removing Public Access Block; bucket policy allows `*`.

Solution: Public Access Block at account level too.

### Resource Policy without Identity
Cross-account: identity policy in source account missing.

### Removing Root Statement from KMS
Lockout. Root needed for emergency recovery.

### Forgetting SourceArn
Allow service principal without SourceArn → confused deputy.

```json
"Principal": {"Service": "s3.amazonaws.com"}    // ALL S3 from anyone
"Condition": {"ArnEquals": {"aws:SourceArn": "..."}}    // specific
```

## Block Public Access (S3)

Account or bucket-level:
- BlockPublicAcls
- IgnorePublicAcls
- BlockPublicPolicy
- RestrictPublicBuckets

Enable all by default. Override only if absolutely needed.

## Cross-Account Replication Role

S3 cross-region replication:
- Role in source account
- Role assumes role in target account (or same trust)
- Replicates objects

Specific bucket policy in target allows replication writes.

## Vault Policy Pattern

Strict resource policy:
```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "secretsmanager:*",
  "Resource": "arn:aws:secretsmanager:us-east-1:123:secret:prod/*",
  "Condition": {
    "Bool": {"aws:MultiFactorAuthPresent": "false"}
  }
}
```

Force MFA for production secrets.

## Best Practices

- Use SourceArn / SourceAccount with service principals
- Audit resource policies (Access Analyzer)
- Combine with SCP for defense in depth
- Document each policy's purpose
- Version (commit to Git)
- Test before applying widely

## Common Mistakes Recap

- Forgetting BOTH policies for cross-account
- Public bucket
- KMS lockout (removing root)
- Wide resource pattern
- Missing condition for service trigger

## Quick Refs

```bash
# Get bucket policy
aws s3api get-bucket-policy --bucket my-bucket

# Put
aws s3api put-bucket-policy --bucket my-bucket --policy file://policy.json

# Delete
aws s3api delete-bucket-policy --bucket my-bucket
```

## Interview Prep

**Mid**: "When use bucket policy?"

**Senior**: "Cross-account S3 access — design."

**Staff**: "Confused deputy — explain and mitigate."

## Next Topic

→ [T04 — Conditions, IAM Access Analyzer](T04-Conditions-Access-Analyzer.md)
