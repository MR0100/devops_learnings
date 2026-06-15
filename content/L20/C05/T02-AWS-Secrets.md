# L20/C05/T02 — AWS Secrets Manager, Parameter Store

## Learning Objectives

- Use AWS secrets options
- Choose between

## Options

- Secrets Manager
- Systems Manager Parameter Store
- KMS (for encryption)

## Secrets Manager

```bash
aws secretsmanager create-secret \
  --name my-app/db \
  --secret-string '{"username":"app","password":"abc123"}'

aws secretsmanager get-secret-value --secret-id my-app/db
```

## Features

- Auto-rotation (built-in for RDS)
- Cross-region replication
- Versioning
- Tags

## Rotation

```bash
aws secretsmanager rotate-secret \
  --secret-id my-app/db \
  --rotation-lambda-arn arn:aws:lambda:... \
  --rotation-rules AutomaticallyAfterDays=30
```

Lambda rotates DB password. Standard templates.

## Cost

- $0.40/secret/month
- $0.05 per 10k API calls

For small: cheap.
For thousands: significant.

## Parameter Store

```bash
aws ssm put-parameter \
  --name /my-app/db/password \
  --value abc123 \
  --type SecureString

aws ssm get-parameter --name /my-app/db/password --with-decryption
```

## Features

- Hierarchical
- Cheap (free tier 10k params)
- Standard or Advanced tier

## Compared

| | Secrets Manager | Parameter Store |
|---|---|---|
| Cost | $0.40/secret | free (up to 10k) |
| Rotation | built-in | manual |
| Size | 64 KB | 4 KB (std), 8 KB (adv) |
| Cross-region | yes | yes (manual) |
| Versioning | yes | yes |

For: secrets manager for auto-rotation; parameter store for config.

## IAM

```json
{
  "Effect": "Allow",
  "Action": ["secretsmanager:GetSecretValue"],
  "Resource": "arn:aws:secretsmanager:*:*:secret:my-app/*"
}
```

Per-service access.

## App Integration

### Lambda
Env var or API call:
```python
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='my-app/db')
```

### ECS
Task definition:
```json
{
  "secrets": [
    {"name": "DB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:...:my-app/db"}
  ]
}
```

Injected at task start.

### EKS
External Secrets Operator:
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-store
  target:
    name: my-app-secrets
  data:
    - secretKey: password
      remoteRef:
        key: my-app/db
        property: password
```

## KMS

Underneath:
- Secrets encrypted with KMS
- Customer-managed (CMK) or AWS-managed

For CMK:
- Audit
- Rotation
- Control

## CloudTrail

Logs:
- Get / put / rotate
- IAM principal
- Time

For: audit.

## Compared to Vault

| | AWS SM | Vault |
|---|---|---|
| Setup | none (managed) | install + HA |
| Dynamic secrets | limited (RDS) | many engines |
| Multi-cloud | no | yes |
| Rotation | RDS only | any DB |
| Cost | per secret | infra |

For AWS-only: Secrets Manager.
For multi-cloud: Vault.

## Hybrid

Vault + Secrets Manager:
- App uses Vault
- Vault back-end stores in Secrets Manager (or AWS-encrypted)

Or independent.

## Rotation

For DB:
- Auto-rotate weekly
- Test connection
- Roll back if fails

For: limit credential lifespan.

## Best Practices

- IRSA for EKS (no static keys)
- Parameter Store for config
- Secrets Manager for sensitive
- Auto-rotation
- CMK for CMK control
- CloudTrail enabled

## Common Mistakes

- All in Parameter Store (no rotation)
- Static keys in code
- No CMK (no control)
- No CloudTrail review

## Migration

From env vars / config:
1. Move to Parameter Store
2. Sensitive → Secrets Manager
3. App reads at startup
4. Cache reasonably

## Quick Refs

```bash
# Secrets Manager
aws secretsmanager create-secret / get-secret-value / rotate-secret

# Parameter Store
aws ssm put-parameter --type SecureString
aws ssm get-parameter --with-decryption

# IAM
secretsmanager:GetSecretValue
ssm:GetParameter
```

## Interview Prep

**Junior**: "How do AWS Secrets Manager and SSM Parameter Store store secrets?" — Both store values encrypted with KMS and control access via IAM; Secrets Manager is purpose-built for secrets with rotation, while Parameter Store is a general config store with a free tier and optional SecureString parameters.

**Mid**: "Secrets Manager vs Parameter Store — when do you pick each?" — Secrets Manager for secrets needing built-in rotation, cross-region replication, and resource policies (it costs per secret); Parameter Store for cheap/free config and simple secrets where you don't need managed rotation.

**Senior**: "How should workloads retrieve these secrets securely?" — Grant a tightly-scoped IAM role (IRSA on EKS, instance profile on EC2) so the app fetches at runtime with no static creds, enable KMS encryption with least-privilege key policies, and cache locally to avoid throttling and per-call cost.

**Staff**: "What's your overall secrets strategy on AWS, and when do you outgrow native services?" — Standardize on IAM-scoped runtime retrieval with rotation and CloudTrail auditing as the paved road; reach for Vault when you need dynamic secrets across many backends, multi-cloud consistency, or fine-grained leasing the native services don't provide.

## Next Topic

→ [T03 — Sealed Secrets, External Secrets Operator](T03-Sealed-Secrets-ESO.md)
