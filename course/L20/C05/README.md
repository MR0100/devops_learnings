# L20/C05 — Secrets Management

## Topics

- **T01 HashiCorp Vault Deep Dive** — Industry leader
- **T02 AWS Secrets Manager, Parameter Store** — Cloud-native
- **T03 Sealed Secrets, External Secrets Operator** — K8s patterns
- **T04 SOPS** — Encrypt for Git

## What Are Secrets

- Database passwords, API keys, certificates
- SSH keys
- Encryption keys
- OAuth tokens
- Bot tokens (Slack, GitHub)

Sensitive: leak = compromise.

## Bad Patterns (avoid)

- Hardcoded in source
- Plain env vars in K8s Secret manifests committed to Git
- Long-lived static credentials in CI
- Shared "service account" credentials
- Credentials in env vars (visible in process listing in some cases)
- Logs containing tokens

## HashiCorp Vault

### Why Vault Wins
- **Dynamic secrets**: generate short-lived DB creds on demand
- **Encryption-as-a-service**: encrypt/decrypt data without holding keys
- **Secret engines** for various backends (AWS, DB, PKI, KV)
- **Strong auth methods**: K8s SA, AWS IAM, OIDC, LDAP, etc.
- **Audit logging** of every access

### Architecture
```
Client → API → Vault Server(s) HA → Storage (Consul / Integrated Raft)
                                  → KMS for auto-unseal
```

### Secrets Engines
- **KV** (v1, v2 with versioning)
- **Database**: dynamic creds for Postgres, MySQL, MongoDB, etc.
- **AWS**: dynamic IAM creds
- **PKI**: issue certificates
- **Transit**: encrypt-as-a-service
- **Cubbyhole**: per-token isolated KV

### Dynamic DB Creds Example
```bash
# Config (once)
vault write database/config/postgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles="webapp" \
  connection_url="postgresql://admin:pass@db:5432/?sslmode=disable"

vault write database/roles/webapp \
  db_name=postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# App requests creds
vault read database/creds/webapp
# Returns: temporary username + password, valid 1h
```

App gets fresh DB creds per hour; auto-revoked. No long-lived password.

### K8s Auth
```bash
# Config (once)
vault auth enable kubernetes
vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc:443" \
  kubernetes_ca_cert=@ca.crt

vault write auth/kubernetes/role/myapp \
  bound_service_account_names=myapp-sa \
  bound_service_account_namespaces=default \
  policies=myapp \
  ttl=1h
```

In pod:
```bash
# Use service account token to login
TOKEN=$(curl -s -H "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
  -d '{"role": "myapp", "jwt": "..."}' \
  $VAULT/v1/auth/kubernetes/login | jq -r .auth.client_token)

# Use to fetch secrets
curl -H "X-Vault-Token: $TOKEN" $VAULT/v1/secret/data/myapp/config
```

### Vault Agent / Sidecar
Vault Agent runs alongside app; templates Vault secrets to files; auto-renews.

```hcl
# vault-agent-config.hcl
auto_auth {
  method "kubernetes" {
    config = { role = "myapp" }
  }
  sink "file" { config = { path = "/var/run/vault-token" } }
}

template {
  source      = "/templates/db-creds.tpl"
  destination = "/secrets/db.json"
}
```

Or Vault CSI Driver / Secrets Store CSI Driver to mount as a volume.

## AWS Secrets Manager

- Native AWS
- Per-secret pricing ($0.40/mo + $0.05 per 10K requests)
- Automatic rotation (Lambda-based, built-in for RDS/DocumentDB/Redshift)
- Replication across regions
- KMS-encrypted at rest

```python
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='prod/myapp/db')
config = json.loads(secret['SecretString'])
```

## AWS Parameter Store

- Free for Standard tier (4 KB params, 10K total, 1000 req/sec)
- Advanced tier paid
- SecureString (KMS-encrypted)
- Hierarchical paths

```python
ssm = boto3.client('ssm')
v = ssm.get_parameter(Name='/myapp/prod/db_password', WithDecryption=True)
```

### When Which
- Parameter Store: free, simple, no rotation
- Secrets Manager: rotation, replication, compliance

## Sealed Secrets (Bitnami)

Commit encrypted secrets to Git. Decrypts in-cluster.

```bash
echo -n "mysecret" | kubectl create secret generic mysecret --dry-run=client --from-file=password=/dev/stdin -o yaml | kubeseal > sealedsecret.yaml
kubectl apply -f sealedsecret.yaml
```

In-cluster controller decrypts using per-cluster private key.

### Trade-Offs
- Per-cluster key (no shared encryption across envs)
- Migration / DR more complex
- Simple to set up

## External Secrets Operator (ESO)

Sync from external store (AWS Secrets Manager, Vault, GCP, Azure) → K8s Secret.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-creds
spec:
  refreshInterval: 1h
  secretStoreRef: { name: aws-secrets, kind: SecretStore }
  target:
    name: db-creds
  data:
    - secretKey: password
      remoteRef:
        key: prod/myapp/db
        property: password
```

ESO creates/updates K8s Secret based on remote store. Apps use K8s Secret normally.

## SOPS (Mozilla)

Encrypt config files with KMS/GPG; commit to Git.

```bash
sops --encrypt --kms <key-arn> values.yaml > values.enc.yaml
git add values.enc.yaml
git commit

# Decrypt at apply
sops --decrypt values.enc.yaml | kubectl apply -f -
```

Helm Secrets / Flux integrations exist.

## Choosing

| Pattern | When |
|---|---|
| Vault | Multi-cloud, dynamic creds, mature secret needs |
| AWS Secrets Manager | AWS-only, rotation needed |
| Parameter Store | AWS-only, simple config |
| ESO + cloud store | K8s + cloud-native ergonomics |
| Sealed Secrets | Simple K8s, single cluster, GitOps |
| SOPS | Config files, not just K8s |

## Rotation

### Automated
- Vault: dynamic creds (always short-lived)
- Secrets Manager: rotation Lambda
- ESO: refreshInterval re-syncs (but doesn't rotate source secret)

### Manual
- API keys for SaaS (you must rotate)
- Document procedure
- Test rotation quarterly (Game Day)

## Best Practices

- No static secrets in repos (ever)
- IAM auth (workload identity) when possible
- Rotation policies in writing
- Audit access (Vault audit log, CloudTrail for Secrets Manager)
- Break-glass procedure (root recovery)
- Backups (Vault snapshot)

## Interview Themes

- "Compare Vault, Secrets Manager, ESO"
- "Dynamic vs static secrets"
- "How does Vault dynamic DB creds work?"
- "Sealed Secrets — security model"
- "When SOPS over a vault?"
