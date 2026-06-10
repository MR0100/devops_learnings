# L15/C05/T02 — Immutable Tags & Digests

## Learning Objectives

- Pin to digests
- Enforce immutable tags

## Tag vs Digest

### Tag
Mutable label:
```
myapp:v1.0.0
myapp:latest
```

Can point to different images over time.

### Digest
Immutable content hash:
```
myapp@sha256:abc123def456...
```

Always same image.

## Why Pin to Digest

- Reproducibility
- Supply chain (no swap)
- Predictable rollbacks

## Pin Example

```dockerfile
FROM nginx@sha256:abc123def456789...
```

vs:
```dockerfile
FROM nginx:1.27
```

Tag could be updated; digest can't.

## K8s Deployments

```yaml
spec:
  containers:
  - image: registry/myapp@sha256:abc123...
```

Production: pin.
Dev: tags OK.

## Find Digest

```bash
docker pull nginx:1.27
docker inspect nginx:1.27 | jq '.[0].RepoDigests'
# Or
crane digest nginx:1.27
# Or
docker manifest inspect nginx:1.27
```

## Immutable Tags

Prevent overwrite:

### ECR
```bash
aws ecr put-image-tag-mutability \
  --repository-name my-app \
  --image-tag-mutability IMMUTABLE
```

Push to existing tag: fails.

### GAR
```bash
gcloud artifacts repositories update REPO --immutable-tags
```

### ACR
```bash
az acr config retention update \
  --registry NAME \
  --status enabled
```

### Harbor
UI / API: enable.

## Why Immutable Tags

Without:
- Push v1.0.0 again with bug fix
- Old deploys reference v1.0.0
- They now have different content (after re-pull)
- Inconsistency

With:
- v1.0.0 forever same
- Bug fix = v1.0.1
- Force versioning discipline

## Convention

```
Push:    v1.2.3 (immutable)
Tag also: latest (mutable)
```

`latest` for convenience; never for prod.

## Promotion via Digest

```
Build → tag v1.0.0, get digest sha256:abc
Test  → use digest
Stage → use digest
Prod  → use digest
```

Same artifact through all stages.

## Multi-Arch

Digest of manifest list:
```bash
crane digest --platform linux/amd64 nginx:1.27
sha256:amd64-specific
```

Or:
```bash
crane digest nginx:1.27   # manifest list digest
sha256:multi-arch
```

## CI Pin Update

```yaml
- name: Get digest
  id: digest
  run: |
    docker pull nginx:1.27
    DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' nginx:1.27 | cut -d@ -f2)
    echo "digest=$DIGEST" >> $GITHUB_OUTPUT

- name: Update manifest
  run: |
    yq -i ".spec.containers[0].image = \"nginx@${{ steps.digest.outputs.digest }}\"" deploy.yaml
```

For: auto-pin.

## Renovate / Dependabot

Auto-PRs to update pinned digests:
```yaml
# renovate.json
{
  "extends": ["config:base"],
  "docker": {
    "pinDigests": true
  }
}
```

For: keep current.

## Helm Charts

```yaml
image:
  repository: nginx
  digest: sha256:abc123def...
```

Or tag + verify checksum.

## Argo CD

Reconciles to manifest exact match.

For digest-pinned: redeploy only on digest change.

## Drift Detection

Periodic check: prod images match manifests.

```bash
kubectl get pods -o json | jq '.items[].status.containerStatuses[].imageID'
# Compare to expected
```

For: spot manual changes.

## Tools

### crane
```bash
crane copy SRC DST            # copy
crane digest TAG               # get digest
crane manifest TAG             # raw manifest
crane config TAG               # config
```

### regctl
```bash
regctl image inspect REPO:TAG
regctl image digest REPO:TAG
```

### docker
```bash
docker manifest inspect REPO:TAG
```

## When to Use Tags

### Acceptable
- Dev / personal envs
- Latest dev
- Sticky env (mutating)

### Not Acceptable
- Prod
- Versioned releases
- Audited environments

## Migration to Digests

1. Tooling: emit digests in CI
2. K8s manifests: digest-only
3. Helm values: digest
4. Pin tooling (Renovate)

For: stricter supply chain.

## Inspect Image

```bash
crane manifest IMAGE@sha256:abc
# Layers, config

crane config IMAGE@sha256:abc
# Env, entrypoint, etc.
```

For: verify.

## Cosign Verify by Digest

```bash
cosign verify registry/myapp@sha256:abc \
  --certificate-identity ...
```

Digest = content; signature = trust.

## Best Practices

- Immutable tags enabled
- Prod manifests: digest
- Dev: tag OK
- Renovate / Dependabot for updates
- Multi-arch: manifest list digest
- Audit untagged / dangling

## Common Mistakes

- :latest in prod
- Mutable tags (overwrite bugs)
- Forget to update digests (stale)
- Mix tag + digest randomly
- No tooling for digest pin

## Quick Refs

```bash
# Digest of tag
crane digest REG/REPO:TAG
docker manifest inspect REG/REPO:TAG | jq

# Immutable tag config
aws ecr put-image-tag-mutability --image-tag-mutability IMMUTABLE
gcloud artifacts repositories update REPO --immutable-tags

# Pin in K8s
image: registry/app@sha256:abc...
```

## Interview Prep

**Mid**: "Tag vs digest."

**Senior**: "Why immutable."

**Staff**: "Supply chain via digests."

## Next Topic

→ [T03 — SBOM Generation](T03-SBOM-Generation.md)
