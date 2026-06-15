# L12/C09/T03 — Pull-Through Caches

## Learning Objectives

- Configure pull-through cache
- Avoid rate limits

## Pull-Through Cache

Registry that caches upstream:
- Pulls from upstream on first request
- Subsequent: cached
- Pulls feel local

For:
- Avoid rate limits (Docker Hub)
- Faster pulls (cached locally)
- Reduce external traffic
- Air-gapped reliability

## ECR Pull-Through

```bash
aws ecr create-pull-through-cache-rule \
  --ecr-repository-prefix dockerhub \
  --upstream-registry-url registry-1.docker.io
```

Now:
```bash
docker pull 123.dkr.ecr.us-east-1.amazonaws.com/dockerhub/library/nginx:1.27
# First time: ECR pulls from Docker Hub, caches
# Subsequent: from cache
```

## Supported Upstreams (ECR)

- Docker Hub
- AWS ECR Public
- Quay
- Microsoft Container Registry
- GitHub Container Registry (limited)

## Auth

For private upstream:
```bash
aws ecr put-pull-through-cache-rule \
  --upstream-registry-url quay.io \
  --upstream-credentials-arn arn:aws:secretsmanager:...
```

Secret in Secrets Manager.

## GAR Remote Repository

```bash
gcloud artifacts repositories create dockerhub-remote \
  --repository-format=docker \
  --location=us-central1 \
  --mode=remote-repository \
  --remote-docker-repo=DOCKER-HUB
```

Similar concept; GCP-native.

## ACR

Connected Registries / cache:
```bash
az acr scope-map create ...
az acr token create ...
```

For Azure.

## Harbor Proxy Cache

```yaml
# Harbor UI / API
Project: dockerhub-proxy
Type: Proxy Cache
Registry: Docker Hub
```

Pulls and caches.

For self-hosted.

## Use in Image References

```dockerfile
# Was
FROM nginx:1.27

# Now
FROM 123.dkr.ecr.us-east-1.amazonaws.com/dockerhub/library/nginx:1.27
```

App image references cache.

## Lifecycle

Cached images:
- Stored like normal images
- Subject to lifecycle policies
- Storage cost in your registry

For: clean up periodically.

## Cost vs Benefit

For:
- Rate limit avoidance (essential for Docker Hub free)
- Latency (faster pulls)
- Reliability (upstream down)

Cost:
- Storage (cached images)
- First pull (proxied through)

For high-traffic: massive benefit.

## Multi-Cluster

Pull-through cache visible across clusters in same region.

For: shared cache.

## Multi-Region

Per-region cache:
- Pulls go to nearest
- Cross-region replication for popular images

## Docker Hub Rate Limits

Free tier:
- 100 pulls / 6 hr (anonymous)
- 200 (authenticated)

Authenticated higher; still limited.

Mitigations:
- Pull-through cache
- Replicate critical images to private
- Paid plan

## CI Optimization

For CI runners:
- Pull from local cache (pull-through or replica)
- Faster builds
- No rate limit issues

## Disabling

To stop caching:
```bash
aws ecr delete-pull-through-cache-rule --ecr-repository-prefix dockerhub
```

Cached images remain (manually delete).

## Air-Gapped

For no Internet:
- Mirror upstream periodically (manual)
- Use cached images
- Don't try pull-through (no upstream)

## Common Patterns

### Org-Wide Cache
Central registry caches Docker Hub:
```
ecr/dockerhub/library/nginx:1.27
ecr/dockerhub/library/postgres:15
```

All teams pull from here.

### Specific Images
Only mirror what's used:
```bash
crane copy docker.io/nginx:1.27 myregistry/nginx:1.27
```

## Performance

Pull-through cache:
- First pull: same as upstream
- Subsequent: as fast as local

For: amortize cost.

## Best Practices

- Use pull-through for public registries
- Document image references (point to cache)
- Monitor cache usage
- Periodic cleanup
- Combine with replication

## Common Mistakes

- Not using cache (rate-limit hits)
- Cache without lifecycle (bloat)
- Wrong upstream URL
- Missing auth for private upstream

## Quick Refs

```bash
# ECR
aws ecr create-pull-through-cache-rule --ecr-repository-prefix PREFIX --upstream-registry-url URL

# GAR
gcloud artifacts repositories create REPO --mode=remote-repository --remote-docker-repo=...

# Harbor (UI)
```

## Interview Prep

**Mid**: "Pull-through cache."

**Senior**: "Rate limit mitigation."

**Staff**: "Image distribution strategy."

## Next Topic

→ Move to [L12/C10 — Container Best Practices](../C10/README.md)
