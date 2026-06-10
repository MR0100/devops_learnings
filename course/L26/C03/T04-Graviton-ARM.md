# L26/C03/T04 — Graviton & ARM Migration

## Learning Objectives

- Migrate to ARM
- Save cost

## Graviton

AWS ARM CPUs:
- Graviton 2 / 3 / 4
- 20-40% cheaper than x86
- Often equal or better perf

## ARM Benefits

- Lower cost
- Lower power
- Often higher perf-per-dollar

## Compatibility

Most code:
- Interpreted (Python, Ruby, Node): just works
- Compiled (Go, Rust): rebuild for ARM
- Java / .NET: JVM/CLR handles

## Containers

Multi-arch images:
```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -t myapp:v1 --push .
```

Manifest list; runs on either.

## Test First

Some incompatibility:
- C/C++ binary deps
- Older libraries
- Native extensions

For: test before prod migration.

## Migration

1. Build multi-arch images
2. Test functional + perf
3. Roll out to dev
4. Staging
5. Prod

## K8s

Mix:
```yaml
# Karpenter
requirements:
  - key: kubernetes.io/arch
    operator: In
    values: [amd64, arm64]
```

Or per-deployment:
```yaml
nodeSelector:
  kubernetes.io/arch: arm64
```

## Lambda ARM

```bash
aws lambda update-function-configuration \
  --function-name myfn \
  --architectures arm64
```

20% cheaper.

## RDS Graviton

Switch instance:
```bash
aws rds modify-db-instance --db-instance-identifier X --db-instance-class db.m6g.large
```

Brief downtime; cheaper.

## ElastiCache Graviton

Similar.

## OpenSearch Graviton

Similar.

## Savings

Typical:
- 20-40% on instance hour
- Plus better perf often = effectively more

For: significant.

## Azure Cobalt 100

Azure ARM:
- Dpsv6 series
- Similar gains

## GCP Tau T2A / Axion C4A

GCP ARM:
- Tau T2A
- Axion C4A (newer)

## Real Examples

### Snap
Migrated heavily to Graviton.

### Twitter / X
Big ARM adoption.

### Many SaaS
Standard now.

## Best Practices

- Multi-arch images
- Test thoroughly
- Gradual rollout
- Track cost saving

## Common Mistakes

- Skip testing (subtle bugs)
- All-at-once
- No multi-arch image
- Native extension breaks

## Quick Refs

```bash
# Build multi-arch
docker buildx build --platform linux/amd64,linux/arm64

# Check arch
uname -m   # x86_64 or aarch64

# AWS instance families ARM
m6g / m7g / c6g / c7g / r6g / r7g / t4g
```

## Interview Prep

**Mid**: "Graviton."

**Senior**: "ARM migration."

**Staff**: "ARM strategy."

## Next Topic

→ Move to [L26/C04 — Storage Optimization](../C04/README.md)
