# L15/C05/T01 — Artifact Repositories

## Learning Objectives

- Choose artifact repo
- Apply retention

## Artifact

Build output:
- Docker image
- JAR / WAR
- npm package
- Python wheel
- Helm chart
- Terraform module
- Binary
- SBOM, signature, attestation

## Repositories

### Container Registry
- ECR, GCR, ACR, GHCR, Docker Hub, Harbor, Quay

(Covered L12/C09.)

### Generic Artifact
- Artifactory (universal)
- Nexus (open source + paid)
- AWS CodeArtifact
- GitHub Packages
- GitLab Package Registry
- npm registry (and forks)
- PyPI (private mirrors)

## Artifactory

JFrog's universal repo:
- Docker
- Maven, Gradle
- npm, PyPI
- Helm
- Generic
- Replication
- Access control

For: enterprise.

## Nexus

Sonatype:
- Maven (origin)
- npm, Docker, others
- Free + Pro
- Self-host

For: org-wide artifact mgmt.

## Choose

| | Artifactory | Nexus | Cloud-Native |
|---|---|---|---|
| Cost | $$ | $ (OSS) + $ Pro | $ (cloud) |
| Format support | All | Many | Vendor-specific |
| Self-host | Yes | Yes | No |
| Replication | Yes (high tier) | Yes (Pro) | Yes (most) |
| Enterprise | Strong | Strong | Varies |

## CodeArtifact (AWS)

Per-repo:
```bash
aws codeartifact create-repository \
  --domain mycompany \
  --repository my-repo \
  --domain-owner ACCT

aws codeartifact login --tool npm --repository my-repo --domain mycompany
```

For: AWS-native.

## GitHub Packages

```yaml
# In CI
- run: npm publish --registry=https://npm.pkg.github.com
```

```ini
# .npmrc
@myorg:registry=https://npm.pkg.github.com
```

For: GitHub-tied.

## Container Image Tags

```
v1.2.3                  # release
v1.2                    # latest minor
v1                      # latest major
latest                  # avoid in prod
sha-abc123              # commit
sha-abc123-amd64        # arch-specific
```

For prod: pin to digest (sha256:...).

## Immutable Tags

```
ECR: tag mutability = IMMUTABLE
```

Once pushed, tag can't overwrite. Force semver.

For: predictability.

## Promotion

```
dev-images → staging-images → prod-images
   ↑              ↑               ↑
build         passing tests   passing canary
```

Same image, promoted via tag / repo.

## Retention

```json
// ECR lifecycle
{
  "rules": [
    {
      "rulePriority": 1,
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["v"],
        "countType": "imageCountMoreThan",
        "countNumber": 50
      },
      "action": {"type": "expire"}
    }
  ]
}
```

For: cost + clutter.

## Artifact Versioning

### SemVer
```
v1.0.0 (major.minor.patch)
v1.0.1
v2.0.0
```

For: libraries.

### Calendar
```
2026.01.001
2026.01.002
```

For: continuous deploy.

### Commit
```
sha-abc123
```

For: ephemeral.

## Signing

```bash
cosign sign --yes registry/myapp:v1.0.0
```

K8s verifies before pull.

## SBOM

```bash
syft myapp:v1.0.0 -o cyclonedx > sbom.json
cosign attest --predicate sbom.json myapp:v1.0.0
```

Attached to image.

## Auth

### Static Creds (Avoid)
Token in env / file.

### IAM / Workload Identity
Cloud-native; no creds.

### OIDC
CI → cloud → registry.

## Access Control

- Read: developers
- Write: CI only
- Delete: admins / lifecycle

Don't let humans push to prod registries.

## Replication

For multi-region: replicate critical images.

(See L12/C09/T02.)

## Vulnerability Scanning

Auto on push:
- ECR Inspector
- GAR Container Scanning
- ACR Defender
- Harbor + Trivy

Block deploy if CVE.

## Pull-Through Cache

Public registries cached locally:
- ECR pull-through (for Docker Hub etc.)
- GAR remote repository
- Harbor proxy cache

(See L12/C09/T03.)

For: avoid rate limits.

## Multi-Repo Strategy

### Per Team
```
team-a/
  service-1
  service-2
team-b/
  service-3
```

### Per Service
```
service-1
service-2
```

For: ownership clarity.

## Cleanup

```bash
# ECR untagged
aws ecr describe-images --repository-name X | jq '.imageDetails[] | select(.imageTags == null) | .imageDigest'

# Delete
aws ecr batch-delete-image --repository-name X --image-ids imageDigest=sha256:...
```

Lifecycle policies preferred.

## Metrics

- Storage used
- Pulls / pushes per day
- Per-image age
- Vuln count

For: cost + security.

## CI Push

```yaml
- name: Login
  uses: docker/login-action@v3
  with:
    registry: 123.dkr.ecr.us-east-1.amazonaws.com
    username: AWS
    password: ${{ steps.creds.outputs.password }}

- name: Build and push
  uses: docker/build-push-action@v6
  with:
    push: true
    tags: 123.dkr.ecr.us-east-1.amazonaws.com/myapp:${{ github.sha }}
```

## Cross-Repo Copy

```bash
crane copy A B
skopeo copy docker://A docker://B
```

For: replication, mirror.

## Manifest Lists

For multi-arch:
```bash
docker buildx imagetools inspect myapp:v1
```

Single tag → multiple arches.

## Best Practices

- Immutable tags (semver)
- Pin to digest in prod
- Lifecycle policies
- Replication for critical
- Scanning enabled
- Signed images
- SBOMs published
- Per-service repos

## Common Mistakes

- :latest in prod
- No lifecycle (cost)
- Single region
- No scanning
- Public when should be private
- Lost old artifacts (no retention)

## Quick Refs

```bash
# Docker push/pull
docker push REG/REPO:TAG

# Cross-tool copy
crane copy SRC DST
skopeo copy docker://SRC docker://DST

# Inspect
crane manifest REG/REPO:TAG
crane config REG/REPO:TAG
```

## Interview Prep

**Junior**: "What's an artifact repo."

**Mid**: "Lifecycle policies."

**Senior**: "Multi-repo strategy."

**Staff**: "Artifact platform."

## Next Topic

→ [T02 — Immutable Tags & Digests](T02-Immutable-Tags-Digests.md)
