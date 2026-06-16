# L20/C05/T01 — HashiCorp Vault Deep Dive

## Learning Objectives

- Operate Vault
- Use secret engines

## Vault

Secrets management:
- Centralized
- Dynamic secrets
- Auto-rotation
- Audit
- Encryption

## Components

- Storage (HA): Consul, integrated raft
- Cluster (HA)
- API + CLI + UI
- Authentication: many methods
- Secret engines: many types

## Install

```bash
helm install vault hashicorp/vault \
  --set 'server.dev.enabled=false' \
  --set 'server.ha.enabled=true' \
  --set 'server.ha.raft.enabled=true'
```

K8s: 3-replica HA.

## Unseal

After start:
- Sealed (encryption key not loaded)
- Unseal with shards (Shamir):
  ```bash
  vault operator unseal SHARD_1
  vault operator unseal SHARD_2
  vault operator unseal SHARD_3
  ```

Or auto-unseal: KMS (AWS / GCP / Azure).

## Auto-Unseal AWS

```hcl
seal "awskms" {
  region = "us-east-1"
  kms_key_id = "alias/vault-unseal"
}
```

Vault uses KMS to unseal automatically.

## Auth Methods

- userpass
- LDAP
- AWS IAM
- GCP IAM
- Azure
- K8s
- OIDC
- JWT
- AppRole

For: many sources.

## Secret Engines

### KV (Key-Value)
```bash
vault kv put secret/myapp password=abc123
vault kv get secret/myapp
```

Static secrets.

### Database
Dynamic creds:
```bash
vault read database/creds/readonly
# Returns user+password; expires in 1 hr
```

DB:
- Postgres
- MySQL
- Mongo
- Redis

App gets temp creds.

### AWS
Dynamic IAM creds:
```bash
vault read aws/creds/my-role
```

### PKI
Issue certs:
```bash
vault write pki/issue/my-role common_name=app.example.com
```

### Transit
Encryption as a service:
```bash
vault write transit/encrypt/my-key plaintext=$(base64 <<< "secret")
```

App doesn't have key; calls Vault.

### SSH
Sign SSH certs.

### TOTP
Generate TOTP codes.

## K8s Auth

```bash
vault auth enable kubernetes

vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc"

vault write auth/kubernetes/role/myapp \
  bound_service_account_names=myapp-sa \
  bound_service_account_namespaces=prod \
  policies=myapp-policy \
  ttl=1h
```

K8s SA → Vault token → secrets.

## Vault Agent Injector

```yaml
metadata:
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: myapp
    vault.hashicorp.com/agent-inject-secret-db: "database/creds/readonly"
```

Sidecar injects secrets to file.

## Policies

```hcl
path "secret/data/myapp/*" {
  capabilities = ["read"]
}

path "database/creds/readonly" {
  capabilities = ["read"]
}
```

Per-team / per-app.

## Audit Log

```bash
vault audit enable file file_path=/var/log/vault/audit.log
```

Every operation logged.

## High Availability

```hcl
storage "raft" {
  path = "/vault/data"
  node_id = "node1"
  retry_join {
    leader_api_addr = "https://vault-1:8200"
  }
}
```

3+ nodes; Raft consensus.

## Disaster Recovery

```bash
vault operator raft snapshot save backup.snap
vault operator raft snapshot restore backup.snap
```

Backup + restore.

## Performance

For 10k ops/sec:
- 3 nodes
- Solid network
- Storage SSD

## Lease Mgmt

Dynamic creds:
```bash
vault lease list aws/creds/my-role
vault lease revoke -prefix aws/creds/my-role
```

Revoke if leaked.

## Token TTL

Short-lived:
- Token created with TTL
- Renew while valid
- Expires automatically

For: minimize leak window.

## OIDC for Humans

```bash
vault auth enable oidc

vault write auth/oidc/config \
  oidc_discovery_url="https://accounts.google.com" \
  oidc_client_id=$ID \
  oidc_client_secret=$SECRET
```

SSO into Vault.

## Best Practices

- HA cluster (3+ nodes)
- Auto-unseal (KMS)
- K8s auth for apps
- Vault Agent for injection
- Dynamic secrets where possible
- Audit logs on
- Backup snapshots

## Common Mistakes

- Single node (no HA)
- Long-lived tokens
- Static secrets when dynamic available
- No audit
- No backup

## Quick Refs

```bash
# Auth
vault login
vault auth enable METHOD
vault token create

# Secrets
vault secrets enable -path=secret kv-v2
vault kv put / get / delete

# Policies
vault policy write NAME policy.hcl

# Audit
vault audit enable file file_path=...

# HA / Raft
vault operator raft join URL
vault operator raft list-peers
```

## Interview Prep

**Junior**: "What is HashiCorp Vault?" — A centralized secrets manager that stores, encrypts, and controls access to secrets, and can also issue short-lived dynamic credentials and act as an encryption-as-a-service backend.

**Mid**: "What are dynamic secrets and why are they better than static ones?" — Vault generates credentials on demand (e.g. a DB user) scoped to a lease and revokes them when the lease expires, so there's no long-lived shared secret to leak and every consumer gets unique, auditable, automatically-rotated creds.

**Senior**: "How does a workload authenticate to Vault without a bootstrapping secret?" — Via an auth method that trusts an existing identity — e.g. the Kubernetes auth method validates the pod's ServiceAccount token, or AWS auth validates instance identity — so the workload trades a platform-issued identity for a Vault token rather than holding a static Vault credential.

**Staff**: "What does running Vault at scale and HA involve?" — Integrated Raft storage with multiple nodes, auto-unseal via a cloud KMS, namespaces and policy-as-code for multi-tenant isolation, performance/DR replication across regions, and a clear seal/recovery key custody plan — plus monitoring lease/token counts since unbounded leases are a common scaling failure.

## Next Topic

→ [T02 — AWS Secrets Manager, Parameter Store](T02-AWS-Secrets.md)
