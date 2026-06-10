# L30/C02/T03 — Cross-Region Failover

## Learning Objectives

- Implement failover
- Test

## Failover Strategy

```
us-east-1 → unhealthy
  ↓
Detection (CloudWatch / Synthetic)
  ↓
DNS update (Route 53)
  ↓
Traffic to us-west-2
  ↓
DB primary promotion
  ↓
App functions
```

## Components

### Health Check
- Route 53 health check
- Synthetic monitoring
- Multi-source

### DNS
- Failover record
- TTL 60s

### App
- Stateless (easy failover)
- Connection retries

### DB
- Aurora Global (1-sec lag)
- Promote on failure

### Cache
- Cross-region replication or rebuild

## Aurora Global

```bash
aws rds create-global-cluster \
  --global-cluster-identifier global-app \
  --source-db-cluster-identifier primary
```

Promote:
```bash
aws rds failover-global-cluster \
  --global-cluster-identifier global-app \
  --target-db-cluster-identifier secondary
```

## App

Connection string:
```
primary.us-east-1.example.com → fail
secondary.us-west-2.example.com → succeed
```

Or single endpoint with failover.

## Testing

Quarterly drill:
- Block primary
- Verify auto-failover
- Measure RTO

## Best Practices

- Automated detection
- DNS or anycast
- DB replication
- Stateless apps
- Drill quarterly

## Common Mistakes

- Manual failover (slow)
- No DB replication (data loss)
- Sync cross-region (slow writes)
- Never tested

## Quick Refs

```
Detection: health check
DNS: Route 53 failover
DB: Aurora Global
App: stateless
Drill: quarterly
```

## Next Topic

→ Move to [L30/C03 — Project 3: Observability Stack](../C03/README.md)
