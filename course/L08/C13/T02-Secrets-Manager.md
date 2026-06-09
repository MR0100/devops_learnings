# L08/C13/T02 — Secrets Manager vs Parameter Store

## Learning Objectives

- Store secrets correctly
- Use rotation

## Two Services

### Secrets Manager
- Built for secrets
- Auto-rotation (DB passwords)
- Cross-region replication
- Resource policies
- $0.40/secret/mo + $0.05/10000 calls

### Parameter Store (SSM)
- Hierarchical key-value
- Free (standard tier)
- 4 KB max (standard) / 8 KB (advanced)
- Supports SecureString (KMS encrypted)

## Secrets Manager

Create:
```bash
aws secretsmanager create-secret --name prod/db/password --secret-string "..."
```

Get:
```bash
aws secretsmanager get-secret-value --secret-id prod/db/password
```

JSON:
```bash
aws secretsmanager create-secret --name prod/db --secret-string '{"username":"admin","password":"..."}'
```

## Rotation

Automatic rotation for RDS, Aurora, DocumentDB, Redshift:
```bash
aws secretsmanager rotate-secret --secret-id prod/db --rotation-rules AutomaticallyAfterDays=30
```

Lambda function rotates:
- Generates new password
- Updates DB
- Updates secret
- Tests
- Switches

Custom rotation: write your own Lambda.

## Versions

Versioned. Default `AWSCURRENT`.

For staged rotation: `AWSPENDING` (testing) → switch to `AWSCURRENT`.

## Cross-Region Replication

```bash
aws secretsmanager replicate-secret-to-regions --secret-id ... --add-replica-regions Region=us-west-2
```

Same secret in multiple regions. Manage in primary.

## Cross-Account

Resource policy on secret:
```json
{
  "Statement": [{
    "Principal": {"AWS": "arn:aws:iam::OTHER:role/X"},
    "Action": "secretsmanager:GetSecretValue",
    "Resource": "*"
  }]
}
```

Plus KMS key policy (since encrypted).

## Parameter Store

Create:
```bash
aws ssm put-parameter --name "/myapp/db/host" --value "db.example.com" --type String
aws ssm put-parameter --name "/myapp/db/password" --value "..." --type SecureString --key-id alias/myKey
```

Get:
```bash
aws ssm get-parameter --name /myapp/db/host
aws ssm get-parameter --name /myapp/db/password --with-decryption
```

## Hierarchy

`/myapp/db/host`
`/myapp/db/password`
`/myapp/api/key`

Get all under path:
```bash
aws ssm get-parameters-by-path --path /myapp/db --recursive --with-decryption
```

## SecureString

Encrypted with KMS:
- Default AWS-managed key
- Or custom CMK

`--with-decryption` flag returns plaintext.

## Tiers

Standard:
- 4 KB max
- Free
- No history retention beyond 100 versions

Advanced:
- 8 KB max
- $0.05/mo per param
- Policy expiration
- Notifications

## Parameter Hierarchy / Policies

```bash
aws ssm put-parameter --name /myapp/api/key --value "..." --type SecureString \
  --policies '[{"Type":"Expiration","Version":"1.0","Attributes":{"Timestamp":"2025-12-31T00:00:00Z"}}]'
```

Auto-expire.

## When Secrets Manager

- Need rotation (DB passwords)
- Cross-region replication
- Resource policies
- Versioned with stages

## When Parameter Store

- Configuration (not strict secrets)
- Hierarchy
- Free
- Smaller secrets

For DB passwords needing rotation: Secrets Manager.
For app config: Parameter Store.

Many use both.

## In Lambda

```python
import boto3
import os

def get_secret():
    sm = boto3.client("secretsmanager")
    resp = sm.get_secret_value(SecretId=os.environ["SECRET_NAME"])
    return json.loads(resp["SecretString"])

# At module level (cached):
SECRET = None

def handler(event, context):
    global SECRET
    if SECRET is None:
        SECRET = get_secret()
    # use SECRET
```

Cache to avoid per-invoke KMS cost.

## Lambda Extension for Secrets

AWS provides Lambda extension to cache locally:
- Add layer
- Read via `localhost` endpoint
- Caches in-memory

No app code changes; cheaper.

## In ECS / EKS

ECS task definition:
```json
"secrets": [
  {"name": "DB_PASSWORD", "valueFrom": "arn:aws:secretsmanager:..."}
]
```

ECS injects as env var on task start.

EKS / K8s:
- External Secrets Operator: syncs to K8s Secrets
- Secrets Store CSI Driver: mount as volume
- IRSA: pod accesses Secrets Manager API directly

## Pricing Comparison

Secret Manager: $0.40/secret/mo + $0.05/10000 API calls.
Parameter Store SecureString: free + KMS API calls.

For 100 secrets accessed 10M times/mo:
- SM: 100 × $0.40 + 10M / 10000 × $0.05 = $40 + $50 = $90
- PS: KMS calls only = $30

PS cheaper for high-volume access.

## Best Practices

- Secrets Manager for rotation-required
- Parameter Store for config + simple secrets
- KMS CMK for sensitive
- Cache in Lambda
- Encryption context (audit)
- IAM policy minimal
- Cross-region for DR

## Don't Do

- Hardcode in code
- Env vars without rotation
- Config files in Git
- Same secret across many apps (blast radius)
- Long-lived (rotate)

## Migration

App → Secrets Manager:
1. Add secret
2. Update app to fetch (cache locally)
3. Remove env var / hardcoded
4. Enable rotation

## Container Apps

For containers, env vars common but:
- Visible to anyone with container access
- Logged sometimes
- Need rotation = restart

Better: fetch from Secrets Manager / Parameter Store at startup; refresh periodically.

## App Patterns

```python
class Config:
    def __init__(self):
        self._secrets = None
        self._last_refresh = 0
    
    def get(self, key):
        if time.time() - self._last_refresh > 3600:
            self._refresh()
        return self._secrets[key]
    
    def _refresh(self):
        sm = boto3.client("secretsmanager")
        resp = sm.get_secret_value(SecretId="my-secret")
        self._secrets = json.loads(resp["SecretString"])
        self._last_refresh = time.time()

config = Config()
```

Cache + periodic refresh.

## Vault

HashiCorp Vault: alternative; multi-cloud; rich features (dynamic credentials, PKI).

AWS-specific simpler with Secrets Manager.

## Common Mistakes

- Hardcoded secrets
- Plaintext in env
- Reading every request (cost / latency)
- No rotation
- Cross-account without resource policy
- KMS key policy missing

## Quick Refs

```bash
# Secrets Manager
aws secretsmanager create-secret --name myapp/db --secret-string '...'
aws secretsmanager get-secret-value --secret-id myapp/db
aws secretsmanager rotate-secret --secret-id myapp/db

# Parameter Store
aws ssm put-parameter --name /myapp/db --value "..." --type SecureString
aws ssm get-parameter --name /myapp/db --with-decryption
```

## Interview Prep

**Mid**: "Secrets Manager vs Parameter Store."

**Senior**: "Rotation strategy."

**Staff**: "Secrets architecture for 100 services."

## Next Topic

→ [T03 — GuardDuty, Security Hub, Inspector, Macie](T03-GuardDuty-SecHub.md)
