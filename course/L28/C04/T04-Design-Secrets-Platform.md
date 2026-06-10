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

## Cost

- Vault cluster
- Storage
- Backup

For: significant; justified.

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

**Senior**: "Secrets platform."

**Staff**: "Cross-cluster."

## Next Topic

→ [T05 — Design a Global Load Balancer](T05-Design-Global-LB.md)
