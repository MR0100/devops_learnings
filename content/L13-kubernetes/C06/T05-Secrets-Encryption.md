# L13/C06/T05 — Secrets Encryption at Rest

## Learning Objectives

- Encrypt Secrets in etcd
- Use KMS providers

## Why Encrypt

By default: Secrets stored base64-encoded in etcd. NOT encrypted.

Threats:
- etcd backup leaked → all secrets readable
- etcd disk stolen
- Read access to etcd data

Encryption at rest: API Server encrypts before write to etcd.

## EncryptionConfiguration

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <base64-encoded-32-byte-key>
  - identity: {}
```

`aescbc`: AES-256-CBC.
`identity`: no encryption (fallback for reading old data).

## Providers

| Provider | Strength | Performance |
|---|---|---|
| identity | None | Fastest |
| aescbc | AES-256 | Good |
| aesgcm | AES-GCM | Good (preferred) |
| secretbox | XSalsa20-Poly1305 | Fast |
| kms | External KMS | Variable |

aesgcm preferred (modern crypto).

For production: KMS provider (covered below).

## Setup

1. Generate key:
```bash
head -c 32 /dev/urandom | base64
```

2. Create EncryptionConfiguration file at `/etc/kubernetes/enc/enc.yaml`.

3. API Server flag:
```
--encryption-provider-config=/etc/kubernetes/enc/enc.yaml
```

4. Restart API Server.

5. Re-encrypt existing Secrets:
```bash
kubectl get secrets --all-namespaces -o json | kubectl replace -f -
```

## Re-Encryption

Just enabling doesn't encrypt existing data. Must read + write each Secret.

```bash
kubectl get secrets -A -o json | kubectl replace -f -
```

Each Secret rewritten; now encrypted.

## Key Rotation

To rotate:
1. Add new key at TOP of providers list:
```yaml
providers:
- aescbc:
    keys:
    - name: key2
      secret: <new-key>
    - name: key1
      secret: <old-key>
- identity: {}
```

2. Restart API Server (decrypts with key1 or key2; encrypts with key2).

3. Re-encrypt all Secrets (now uses key2).

4. Remove key1 from config.

5. Restart API Server.

## KMS Provider

For production: use cloud KMS:
```yaml
providers:
- kms:
    name: aws-kms
    endpoint: unix:///opt/kmsplugin.sock
    cachesize: 1000
    timeout: 3s
```

Plugin runs as DaemonSet / process; integrates with AWS KMS / GCP KMS / Azure Key Vault.

## KMS V2

Newer; better:
```yaml
providers:
- kms:
    apiVersion: v2
    name: aws-kms
    endpoint: ...
```

Improvements:
- Better key management
- Per-resource encryption
- Faster rotation

## EKS Encryption

EKS provides native KMS encryption:
```bash
aws eks create-cluster ... --encryption-config '[{
  "resources": ["secrets"],
  "provider": {"keyArn": "arn:aws:kms:..."}
}]'
```

AWS-managed; no plugin to deploy.

## GKE / AKS

GKE: Cloud KMS integration built-in.
AKS: Azure Key Vault integration.

For managed K8s: use provider-native.

## What to Encrypt

Resources block specifies:
```yaml
resources:
- resources:
  - secrets        # mandatory
  - configmaps     # optional (if sensitive data)
```

For ConfigMaps with sensitive content: include.

Custom resources can also be encrypted.

## Verification

```bash
# Get raw etcd data
ETCDCTL_API=3 etcdctl get /registry/secrets/default/my-secret \
  --endpoints=... --cacert=... --cert=... --key=... \
  --print-value-only | hexdump -C | head
```

If encrypted: starts with `k8s:enc:aescbc:v1:key1:`...
If plain: base64 readable.

## Performance

Each Secret operation: encrypt/decrypt.

For small clusters: negligible.

For 100k+ Secrets: cache helps; KMS latency matters.

KMS API calls: cached by provider.

## Backup Implications

etcd backups now contain encrypted data:
- Backup itself can be in less-secure storage
- Key still needed for restore
- Lost key = lost Secrets

For: protect key separately from etcd backups.

## Defense in Depth

Encryption + RBAC + audit:
- Encryption: data at rest
- RBAC: API access
- Audit: who accessed when
- Sealed Secrets / SOPS: Git-stored

Each layer.

## External Secret Managers

Alternative: don't store in K8s at all:
- AWS Secrets Manager / Vault / etc.
- External Secrets Operator syncs (or app fetches direct)

Covered L13/C03/T02.

## Audit

API Server audit log records:
- Secret reads
- Secret writes
- Token grants

For: detect anomalous access.

```yaml
# audit policy
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets"]
```

## Encryption + GitOps

Storing Secret in Git: bad (plaintext readable).

Options:
- Sealed Secrets (Bitnami): encrypted at rest in Git; controller decrypts
- SOPS: file-level encryption with KMS
- External Secrets: reference external

Encryption at rest in K8s + external secret mgmt: full coverage.

## Common Mistakes

- Enable encryption; forget re-encrypt (old Secrets plain)
- Local keys in EncryptionConfiguration committed to Git
- No key rotation
- No KMS provider for production
- etcd backups in unencrypted location

## Best Practices

- Encryption at rest enabled (always)
- KMS provider for production
- Re-encrypt after enabling
- Rotate keys annually
- Audit Secret access
- External secret manager for sensitive
- Encrypt etcd backups separately

## Limitations

- API Server holds encryption keys in memory
- API Server compromise = key compromise
- Encryption is "at rest in etcd"; in-memory Secrets in pods unprotected

For higher security: external KMS + per-namespace + audit.

## Disaster Recovery

Lost key:
- Secrets unrecoverable
- Apps fail
- Restore from external secret manager (if used)
- Or rotate all secrets manually

For: key backup is critical.

KMS handles this; manage keys carefully.

## Implementation Steps Summary

1. Plan: which provider, which keys
2. Generate keys
3. Create EncryptionConfiguration
4. Configure API Server flag
5. Restart API Server (HA: rolling)
6. Re-encrypt existing data
7. Verify with etcd query
8. Document key rotation procedure

## Quick Refs

```bash
# Generate key
head -c 32 /dev/urandom | base64

# Check if encrypted
ETCDCTL_API=3 etcdctl get /registry/secrets/ns/name --print-value-only | head -c 30

# Re-encrypt all
kubectl get secrets -A -o json | kubectl replace -f -

# EKS native
aws eks create-cluster --encryption-config '[...]'
```

## Interview Prep

**Junior**: "Why encrypt secrets in K8s."

**Mid**: "EncryptionConfiguration setup."

**Senior**: "KMS provider vs local key."

**Staff**: "End-to-end secret protection."

## Next Topic

→ [T06 — OPA Gatekeeper & Kyverno](T06-OPA-Kyverno.md)
