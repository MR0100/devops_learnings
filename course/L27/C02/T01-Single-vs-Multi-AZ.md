# L27/C02/T01 — Single AZ vs Multi-AZ

## Learning Objectives

- Choose AZ strategy
- HA fundamentals

## Single AZ

Everything in one AZ:
- Simpler
- Cheaper (no cross-AZ data transfer)
- AZ failure = outage

For: dev, non-critical.

## Multi-AZ

Across 2+ AZs:
- HA
- More cost (cross-AZ, redundancy)
- Standard for prod

## AWS AZ

Independent data center:
- Power, network
- Failures: rare but real
- 3+ per region typically

## Multi-AZ Setup

### LB
- ALB / NLB spans AZs

### EC2 / ASG
```yaml
AvailabilityZones: [us-east-1a, us-east-1b, us-east-1c]
```

### RDS
```bash
aws rds create-db-instance --multi-az
```

Sync replica in another AZ.

### EBS
Per-AZ. For multi: snapshot to S3.

### S3
Multi-AZ default.

## K8s

- 3+ nodes
- 1+ per AZ
- pod anti-affinity

```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchLabels:
            app: my-app
        topologyKey: topology.kubernetes.io/zone
```

## Topology Spread

```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: DoNotSchedule
```

## Cost

Multi-AZ:
- 2-3x infra (redundancy)
- Cross-AZ transfer ($0.01-0.02/GB)

For: justified for prod.

## Failures

AZ failure:
- Power outage
- Network partition
- Cooling failure

Rare; happens.

For: plan.

## Test

- AZ down drill
- Verify failover
- Document recovery

## SLA

AWS SLA:
- Single AZ EC2: 99.5%
- Multi-AZ ASG: 99.99%

For: significant.

## Best Practices

- Prod multi-AZ
- Test failover
- Cross-AZ data transfer accounted
- Per-AZ monitoring

## Common Mistakes

- Single AZ prod
- All replicas same AZ (defeats purpose)
- No failover test
- Ignore cross-AZ cost

## Quick Refs

```yaml
# K8s
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: zone

# AWS
ASG: AZ-spanning
RDS: --multi-az
```

## Interview Prep

**Junior**: "Multi-AZ."

**Mid**: "Setup."

**Senior**: "HA design."

## Next Topic

→ [T02 — Multi-Region Architecture](T02-Multi-Region.md)
