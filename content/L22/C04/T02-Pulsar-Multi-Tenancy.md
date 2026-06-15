# L22/C04/T02 — Pulsar Multi-Tenancy

## Learning Objectives

- Use Pulsar tenancy
- Isolate per tenant

## Hierarchy

```
Cluster
└─ Tenant
   └─ Namespace
      └─ Topic
```

## Tenant

Per org / team:
```bash
pulsar-admin tenants create acme
pulsar-admin tenants list
```

Permissions / quotas per tenant.

## Namespace

Per project / app:
```bash
pulsar-admin namespaces create acme/finance
pulsar-admin namespaces create acme/marketing
```

Settings per namespace:
- Retention
- TTL
- Backlog quota
- Geo-replication
- Subscription auth

## Topic

```
persistent://acme/finance/orders
non-persistent://acme/marketing/notifications
```

## Permissions

```bash
pulsar-admin namespaces grant-permission acme/finance \
  --actions produce,consume \
  --role finance-app
```

For: per-tenant access.

## Authentication

- TLS
- JWT
- OAuth
- Kerberos

## Quotas

```bash
pulsar-admin namespaces set-backlog-quota acme/finance \
  --limit 100G --policy producer_request_hold
```

## Rate Limit

```bash
pulsar-admin namespaces set-dispatch-rate acme/finance \
  --msg-dispatch-rate 1000 --byte-dispatch-rate 1048576
```

## Retention

```bash
pulsar-admin namespaces set-retention acme/finance \
  --size 100G --time 7d
```

## Compaction

```bash
pulsar-admin namespaces set-compaction-threshold acme/finance \
  --threshold 100M
```

## Geo-Replication

```bash
pulsar-admin namespaces set-clusters acme/finance \
  --clusters us-east,us-west,eu-west
```

Auto-replicate.

## Use Cases

### SaaS Multi-Tenant
Tenant per customer:
- Isolation
- Per-tenant billing
- Quotas

### Org-wide
Tenant per team:
- Self-service
- Cost allocation

## Compared to Kafka

Kafka tenancy:
- Topic naming convention
- ACLs

Pulsar tenancy:
- First-class
- Quotas, retention, replication per

For: stronger isolation.

## Best Practices

- Tenant naming consistent
- Per-tenant quotas
- Authentication strict
- Audit access

## Common Mistakes

- No quotas (one tenant exhausts)
- Shared namespace (mixed concerns)
- Weak auth

## Quick Refs

```bash
pulsar-admin tenants
pulsar-admin namespaces
pulsar-admin topics

pulsar-admin namespaces set-backlog-quota / set-retention / set-clusters / grant-permission
```

## Interview Prep

**Senior**: "Multi-tenancy."

**Staff**: "Pulsar SaaS."

## Next Topic

→ Move to [L22/C05 — NATS & JetStream](../C05/README.md)
