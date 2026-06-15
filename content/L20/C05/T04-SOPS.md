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

**Junior**: "What is SOPS?" — Mozilla's Secrets OPerationS encrypts the values in a YAML/JSON/env file (keys stay readable) using a KMS, age, or PGP key, so you can commit the encrypted file to Git.

**Mid**: "Why encrypt only values, not the whole file?" — Encrypting values per-key keeps the file diff-able and reviewable in Git — you can see which keys changed in a PR without exposing the secret contents.

**Senior**: "When would you choose SOPS over a secrets manager?" — When you want secrets versioned alongside config in Git with no extra running infrastructure (just a KMS for the data key); the trade-off is no dynamic secrets or central rotation, so it fits IaC/config secrets more than high-churn credentials.

**Staff**: "How does SOPS fit a secrets strategy in IaC?" — Use it to keep encrypted config in the same repo as Terraform/manifests with KMS-based access control and audit, integrate it via Terraform/Helm providers so decryption happens at apply time, and reserve a dynamic-secrets system (Vault/ESO) for credentials that need rotation SOPS can't provide.

## Next Topic

→ Move to [L20/C06 — Supply Chain Security](../C06/README.md)
