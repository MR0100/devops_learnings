# L20/C05/T03 — Sealed Secrets, External Secrets Operator

## Learning Objectives

- Use Sealed Secrets
- Use External Secrets Operator

## Sealed Secrets

Bitnami project:
- Encrypt secrets for Git
- Controller decrypts in cluster
- Public encryption; private decryption

For: GitOps secrets.

## How

```bash
# Install
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/...

# Encrypt
echo -n 'mypass' | kubectl create secret generic mysecret \
  --dry-run=client --from-file=password=/dev/stdin -o yaml \
| kubeseal -o yaml

# Result: SealedSecret CR
# Commit to Git
```

```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: mysecret
spec:
  encryptedData:
    password: AgB7...
```

Controller decrypts → creates Secret.

## Key Management

Controller:
- Generates keypair
- Public available
- Private in cluster

Lose private = lose secrets.

For: backup controller key.

## External Secrets Operator (ESO)

Sync from external:
- AWS Secrets Manager
- Vault
- Azure Key Vault
- GCP Secret Manager
- 1Password
- Many

## SecretStore

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-store
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
```

## ExternalSecret

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-secret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-store
    kind: SecretStore
  target:
    name: db-secret   # K8s Secret created
  data:
  - secretKey: password
    remoteRef:
      key: my-app/db
      property: password
```

ESO creates K8s Secret from AWS.

## Auth

### AWS IRSA
SA → IAM role → Secrets Manager.

### Vault K8s Auth
SA → Vault role → secrets.

### GCP Workload Identity
SA → GCP SA → Secret Manager.

## Refresh

Periodic sync:
- Default 1 hr
- Configurable

For: rotation propagates.

## ESO vs Sealed Secrets

| | ESO | Sealed Secrets |
|---|---|---|
| Source | external (Vault, AWS) | Git (encrypted) |
| Rotation | automatic (from source) | manual re-seal |
| Multi-cluster | each cluster pulls | re-seal per cluster |
| Setup | provider + operator | controller only |

For: ESO more modern.

## Use Cases

### Sealed Secrets
- Pure GitOps
- No external dependency
- Small teams

### ESO
- Centralized secrets (Vault)
- Rotation
- Multi-cluster

## SealedSecret Limits

- Pinned to cluster (key tied)
- Re-seal on cluster reset
- Lose key = lose secrets

## ESO Limits

- External dependency
- IAM complex
- Auth setup

## Best Practices

### Sealed Secrets
- Backup controller key
- Document re-seal process
- Per-namespace scoping

### ESO
- Per-cluster SecretStore
- Refresh interval matches rotation
- Audit external source

## Examples

### Sealed Secret + ArgoCD

```yaml
# In Git
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: db-secret
  namespace: prod
spec:
  encryptedData:
    password: AgB...
```

ArgoCD applies → controller decrypts → Secret in cluster.

### ESO + Vault

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
spec:
  provider:
    vault:
      server: "https://vault:8200"
      path: "secret"
      auth:
        kubernetes:
          mountPath: kubernetes
          role: my-role
```

App secret synced from Vault.

## ClusterSecretStore

For cross-namespace:
```yaml
kind: ClusterSecretStore
```

Same as SecretStore but cluster-scoped.

## Migration

From Sealed Secrets to ESO:
1. Set up ESO + provider
2. Migrate secret by secret
3. Remove Sealed Secret
4. Update GitOps

## Other Tools

- Vault Agent Injector (Vault native; sidecar)
- Secrets Store CSI Driver (mount as file)
- Banzai Bank Vaults (older)
- Helm Secrets (SOPS-based)

## Best Practices

- ESO for centralized
- Sealed Secrets for pure GitOps
- IRSA / Workload Identity
- Rotation enabled
- Audit access

## Common Mistakes

- Sealed Secrets without backup
- ESO without auth (static keys)
- No rotation
- Mix systems chaotically

## Quick Refs

```bash
# Sealed Secrets
kubeseal -o yaml < secret.yaml > sealed-secret.yaml

# ESO
kubectl get externalsecret
kubectl get secretstore / clustersecretstore
```

## Interview Prep

**Junior**: "What problem do Sealed Secrets and ESO solve?" — Plain Kubernetes Secrets are only base64-encoded, not encrypted, so you can't safely commit them to Git; both tools let you keep secrets out of plaintext in your repo while still using GitOps.

**Mid**: "Sealed Secrets vs External Secrets Operator — how do they differ?" — Sealed Secrets encrypts the secret so the ciphertext lives in Git and the in-cluster controller decrypts it; ESO keeps the real secret in an external store (Vault, AWS Secrets Manager) and syncs it into a K8s Secret, so Git only holds a reference.

**Senior**: "How do you manage secrets in a GitOps workflow?" — Never commit plaintext; commit either a SealedSecret ciphertext or an ExternalSecret reference, let the controller reconcile the actual Secret in-cluster, and rotate at the source so Git stays declarative without becoming a secret store.

**Staff**: "How do you architect K8s secrets across many clusters?" — Prefer ESO pointing at a central secret manager so rotation and access policy live in one place and clusters are stateless consumers; reserve Sealed Secrets for simpler/air-gapped cases, and watch the Sealed Secrets controller key as a single point of trust that must be backed up and rotated carefully.

## Next Topic

→ [T04 — SOPS](T04-SOPS.md)
