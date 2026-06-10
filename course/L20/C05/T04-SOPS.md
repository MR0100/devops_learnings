# L20/C05/T04 — SOPS

## Learning Objectives

- Use SOPS for files
- Encrypt YAML/JSON

## SOPS

Mozilla / CNCF; encrypts values in files:
- YAML, JSON, ENV, INI
- Keys: KMS, GCP KMS, Azure Key Vault, age, GPG
- Per-value encryption (structure visible)

## Install

```bash
# Linux / Mac
brew install sops
```

## Usage

```bash
# Create / edit (decrypts, opens editor, re-encrypts)
sops secrets.yaml

# Encrypt
sops -e -i secrets.yaml

# Decrypt
sops -d secrets.yaml
```

## Config

```yaml
# .sops.yaml
creation_rules:
  - path_regex: secrets/.*\.yaml$
    kms: 'arn:aws:kms:us-east-1:ACCT:key/KEY_ID'
    aws_profile: my-profile
  - path_regex: dev/.*\.yaml$
    age: 'age1ABC...'
```

Per-path: different keys.

## Encrypted YAML

```yaml
db:
  password: ENC[AES256_GCM,data:abc,iv:def,tag:ghi]
```

Structure (keys) visible; values encrypted.

For: diff-friendly.

## Multiple Keys

```yaml
creation_rules:
  - kms: 'arn:aws:kms:...'
    pgp: 'ABC123...'
    age: 'age1...'
```

OR logic; any key can decrypt.

## age

```bash
# Generate
age-keygen -o key.txt

# Use
sops --age $(cat key.txt | grep public) secrets.yaml
```

Lightweight; no PKI.

## In CI

```yaml
- name: Decrypt
  run: |
    sops -d secrets.enc.yaml > secrets.yaml
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_KEY }}
```

Or OIDC to KMS.

## ArgoCD + SOPS

Helm Secrets plugin or operator decrypts at sync.

## Flux + SOPS

Native support:
```yaml
spec:
  decryption:
    provider: sops
    secretRef:
      name: sops-keys
```

Flux decrypts before apply.

## Compared to Sealed Secrets

| | SOPS | Sealed Secrets |
|---|---|---|
| Type | files | K8s Secrets |
| Format | YAML, JSON, ENV | K8s SealedSecret CRD |
| Storage | git | git |
| Multi-cluster | re-encrypt or share key | per-cluster re-seal |
| Tool | sops CLI | kubeseal |

For: SOPS more flexible (files); Sealed Secrets K8s-specific.

## Use Cases

### Terraform Secrets
```yaml
# secrets.enc.yaml
db_password: ENC[...]
api_key: ENC[...]
```

```bash
sops -d secrets.enc.yaml > secrets.yaml
terraform apply -var-file=secrets.yaml
```

### K8s Secrets
```yaml
# secret.enc.yaml
apiVersion: v1
kind: Secret
data:
  password: ENC[...]
```

Decrypt → apply.

### Config Files
Any file format.

## Best Practices

- KMS / age in prod
- Per-env keys
- Audit access (KMS CloudTrail)
- Don't decrypt to disk in CI (use stdin)
- Backup keys

## Common Mistakes

- GPG in CI (PGP complexity)
- Plain decrypt to file (leaves on disk)
- Single key (lose = lose all)
- No audit

## Quick Refs

```bash
# Edit
sops secrets.yaml

# Encrypt
sops -e -i FILE

# Decrypt
sops -d FILE > out

# Rotate key
sops -r FILE
```

```yaml
# .sops.yaml
creation_rules:
  - path_regex: ...
    kms: ...
    age: ...
```

## Interview Prep

**Mid**: "What's SOPS."

**Senior**: "SOPS use cases."

**Staff**: "Secrets in IaC."

## Next Topic

→ Move to [L20/C06 — Supply Chain Security](../C06/README.md)
