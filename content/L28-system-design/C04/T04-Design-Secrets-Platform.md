# L28/C04/T04 — Design a Secrets Management Platform

## Learning Objectives

- Design secrets platform
- Cross-cluster

## Requirements

### Functional
- Store secrets
- Auto-rotate
- Audit
- Per-app access
- Cross-cluster

### Non-Functional
- HA
- 99.99%
- Sub-second access
- Audit retention 1+ year

## Estimation (derived)

Vault is on the critical path of every pod start, so derive request load from app churn, not steady reads:
```
pods              = 50,000   (across the fleet)
restarts/pod/day  = 5        (deploys, scaling, evictions)
fetches/restart   = 4        (DB creds, API keys, TLS, config)
daily_fetches     = 50,000 × 5 × 4 = 1,000,000/day
avg_qps           = 1,000,000 / 86,400 ≈ 12/s
```
12/s sounds trivial — but secret fetches **spike on mass restarts** (a region failover or fleet-wide rollout restarts everything at once):
```
peak_qps ≈ thousands/s during a stampede
```
That's the sizing case. A 3-node Vault HA cluster handles ~10k req/s, but the real defense is **client-side caching of leases** so a rolling restart doesn't thunder the cluster. **Derived: 3–5 node HA cluster + agent-side lease caching to flatten the restart spike.**

## Components

### Vault (Central)
- HA cluster (3-5 nodes)
- Auto-unseal KMS
- Cross-region replicas

### Auth Methods
- K8s SA
- OIDC
- AWS IAM
- App-specific

### Secret Engines
- KV
- Dynamic DB
- Dynamic cloud creds
- PKI

### Audit
- Centralized log
- Long retention

### Integration
- ExternalSecrets Operator (K8s)
- Vault Agent (sidecar)
- App SDK

## Architecture

```
App → Vault Agent (sidecar) → Vault HA Cluster
                              ↓
                          KMS auto-unseal
                          Audit logs (SIEM)
                          Replication (DR region)
```

## Multi-Cluster

ExternalSecrets:
- Per cluster
- Sync from central Vault
- K8s Secrets created

## Dynamic Secrets

DB:
```
Vault → generate temp creds → app uses → expires
```

For: short-lived; minimize leak.

## Rotation

- Static: scheduled rotation
- Dynamic: continuous
- Workflow: notify on rotation

## Audit

Every operation logged:
- Read / write
- Auth
- Lease

For: compliance.

## DR

Vault replication:
- Performance Replica (read scaling)
- DR Replica (failover)

## HA

3-5 nodes:
- Raft consensus
- KMS auto-unseal

## Self-Service

Devs:
- Register service
- Auto-bind to secrets
- No tickets

## Access Patterns

- Per-app policy
- Per-env (prod vs dev)
- Per-team

## Deep Dive: The Trust Chain (unseal & auth)

The whole platform's security reduces to two questions — *how does Vault decrypt its own data, and how does an app prove who it is?*
- **Unseal**: Vault's storage is encrypted; the decryption key is itself encrypted by a master key that's split (Shamir) or wrapped by a KMS. **Auto-unseal via cloud KMS** removes the manual "5 humans with key shares" ceremony at every restart — but now KMS is a hard dependency, so it lives in a **separate account/region** so a blast in the app account can't also lock you out of secrets.
- **Auth without static keys**: a pod presents its **Kubernetes ServiceAccount JWT**; Vault validates it against the cluster's OIDC issuer and maps it to a policy. No shared secret is ever baked into an image — the identity *is* the workload. This is the single most important property: compromising an image yields no usable credential.
- **Dynamic secrets close the loop**: instead of a long-lived DB password, Vault generates a short-TTL credential on demand and revokes it on lease expiry — so a leaked credential is useless within minutes.

## Cost

- Vault cluster compute (3–5 nodes) + KMS API calls (per-unseal/decrypt)
- Audit log storage with Object Lock (compliance retention)
- DR/perf replica clusters

Significant but justified: the alternative — static credentials sprawled across configs — is a breach waiting to happen. Cost scales with replicas and audit volume, not request rate.

## Real Examples

### HashiCorp Vault
Standard.

### AWS Secrets Manager + Parameter Store
AWS-native.

### CyberArk
Enterprise.

## Trade-Offs

- Self-host Vault: control; ops
- AWS Secrets Manager: managed; AWS-only

## Best Practices

- Workload Identity (no static keys)
- Dynamic secrets
- Audit logs centralized
- DR replica
- Test failover

## Common Mistakes

- Static keys in apps
- No rotation
- No audit
- Single Vault (SPOF)

## Quick Refs

```
Vault (central)
ExternalSecrets (K8s)
Vault Agent (sidecar)
Dynamic secrets
Audit + DR
```

## Interview Prep

**Mid**: "Why are dynamic secrets better than a stored password?" — Vault generates a short-TTL credential on demand and revokes it when the lease expires, so a leaked credential is useless within minutes instead of forever. There's also no long-lived secret sitting in a config file to steal in the first place.

**Senior**: "How does an app authenticate to Vault without any stored credential?" — Workload identity: the pod presents its Kubernetes ServiceAccount JWT, Vault validates it against the cluster's OIDC issuer and maps it to a policy. The identity *is* the workload, so there's no shared secret baked into the image — compromising the image yields nothing usable. ExternalSecrets or a Vault Agent sidecar handles the fetch and renewal.

**Staff**: "Design secrets for a multi-cluster fleet, and what's the worst failure mode?" — Central Vault HA cluster (3–5 nodes, Raft), KMS auto-unseal in a separate account, ExternalSecrets per cluster syncing from the center, dynamic secrets for databases. The scary failure is a **restart stampede** — a region failover restarts thousands of pods that all hammer Vault for credentials at once. I defend with agent-side lease caching to flatten the spike, and a DR replica so a Vault region loss doesn't block every deploy. The second scary one is losing KMS access, which is why it lives in an isolated account.

**Principal**: "How do you make this auditable and compliant end to end?" — Every read/write/auth/lease event goes to a tamper-evident audit log shipped to S3 with Object Lock so it can't be altered or deleted within the retention window. Access is least-privilege per-app, per-env policies, dynamic secrets give per-lease attribution (you know exactly which workload held which credential when), and rotation is automated so there are no stale long-lived keys. The audit trail plus dynamic attribution is what turns "we use Vault" into "we can prove who accessed what" for an auditor.

## Next Topic

→ [T05 — Design a Global Load Balancer](T05-Design-Global-LB.md)
