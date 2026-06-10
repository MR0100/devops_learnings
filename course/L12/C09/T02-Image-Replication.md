# L12/C09/T02 — Image Replication

## Learning Objectives

- Replicate images cross-region/cloud
- Apply patterns

## Why Replicate

- Latency: pull from nearest region
- DR: regional failure resilience
- Compliance: per-region data
- Cost: minimize cross-region pull

## ECR Cross-Region

```bash
aws ecr put-replication-configuration \
  --replication-configuration '{
    "rules": [{
      "destinations": [
        {"region": "us-west-2", "registryId": "123"},
        {"region": "eu-west-1", "registryId": "123"}
      ]
    }]
  }'
```

Pushes to us-east-1 auto-replicate to us-west-2 + eu-west-1.

## ACR Geo-Replication

```bash
az acr replication create --registry myreg --location eastus2
```

Multi-region; managed.

## GAR Multi-Region

Configure repository per region; same name.

Or single multi-region: `us-multi-region-docker.pkg.dev/...`.

## Harbor Replication

```yaml
# Harbor UI
Replication Rule:
  Source: Harbor instance A
  Destination: Harbor instance B
  Trigger: On push
  Filters: ...
```

For self-hosted multi-region.

## Cross-Cloud

For: avoid lock-in or hybrid.

Tools:
- crane copy
- skopeo
- Harbor

```bash
crane copy us-east-1-ecr-image gcr.io/project/image
```

For: backup or migration.

## Pull-Through Cache

Alternative: cache upstream:
```bash
# ECR pull-through
aws ecr create-pull-through-cache-rule \
  --upstream-registry-url public.ecr.aws \
  --ecr-repository-prefix ecr-public
```

For: deps from public registries; cached locally.

## Use Cases

### Multi-Region Deploy
- Push to primary region
- Auto-replicate
- Pods pull from local region
- Faster start

### DR
- Primary region down
- Workloads shift
- Replicated images available

### Compliance
- EU data in EU registry
- US data in US registry

## Replication Costs

- Storage: in each region
- Replication traffic: cross-region (one-time per image)
- Pull from local: free / cheap

For: cost optimization (cross-region pull avoided).

## Image Pull Throughput

Cross-region pull:
- Slower (network)
- Egress charges

Local pull:
- Fast
- Free (same-region typically)

Difference for 1 GB image: seconds vs minutes; $0 vs $$.

## Strategy

For multi-region apps:
- Build in central region
- Replicate to deploy regions
- Pods pull locally
- Fastest start + cheapest

## Filters

Only certain images:
```bash
# ECR
"replicationFilter": {
  "filter": "production",
  "filterType": "PREFIX_MATCH"
}
```

For: production tags only; not all builds.

## Sync via CI

Manual replication via CI:
```yaml
- name: Replicate
  run: |
    crane copy myregistry.com/app:v1 backup-registry.com/app:v1
```

For: custom workflows.

## Air-Gapped

For air-gapped:
- Mirror upstream to internal
- Pull from internal only
- Periodic sync (manually transfer or via DMZ)

Tools: orca, distribution.

## Best Practices

- Replicate prod images
- Per-region for HA
- Filter (not all images)
- Monitor replication lag
- Test failover

## Common Mistakes

- All regions for all images (cost)
- No filter (replicates dev too)
- No monitoring (replication broke; pull from wrong region)
- Stale replicas

## Monitoring

```bash
# Lag
aws ecr describe-image-replication-status --repository-name myrepo --image-id imageTag=v1
```

Alert if not replicated within X minutes.

## Eventual Consistency

Replication: not instant; usually <1 min.

For: image must exist before pod schedules to other region.

Add delay or pre-warm.

## Disaster Recovery

For: primary registry down:
- Replicas accessible
- DNS / config redirects pulls
- Pre-tested

## Image Sync Tools

- crane
- skopeo
- regctl
- Harbor scheduler
- Docker registry tools

## crane Examples

```bash
# Copy
crane copy A B

# Mirror tag
crane copy --all-tags REPO_A REPO_B

# Verify
crane manifest A
crane manifest B
# Compare
```

## skopeo Examples

```bash
# Copy
skopeo copy docker://src docker://dst

# Sync
skopeo sync --src docker --dest docker SRC_REG DST_REG
```

## Quick Refs

```bash
# ECR replication
aws ecr put-replication-configuration ...

# ACR geo-replication
az acr replication create --registry NAME --location REGION

# Cross-cloud
crane copy SRC DST
skopeo copy docker://SRC docker://DST
```

## Interview Prep

**Mid**: "Why replicate."

**Senior**: "Replication strategy."

**Staff**: "Multi-region container deployment."

## Next Topic

→ [T03 — Pull-Through Caches](T03-Pull-Through.md)
