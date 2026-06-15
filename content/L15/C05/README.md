# L15/C05 — Artifact Management

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Artifact-Repositories.md) | Artifact Repositories (Artifactory, Nexus, ECR, GAR) | 1 hr |
| [T02](T02-Immutable-Tags-Digests.md) | Immutable Tags & Digests | 0.5 hr |
| [T03](T03-SBOM-Generation.md) | SBOM Generation | 0.5 hr |

## Artifact Types

- **Container images** (OCI)
- **Language packages** (npm, PyPI, Maven, NuGet, RubyGems, Cargo)
- **Helm charts** (OCI compliant since Helm 3)
- **Terraform modules** (Registry-format)
- **Binary releases** (tarballs, ZIPs)
- **OS packages** (.deb, .rpm)

## Repositories

### Container Registries
- AWS ECR, GCP Artifact Registry, Azure ACR (cloud)
- Harbor, JFrog Artifactory, Sonatype Nexus, GitHub Container Registry (self-hosted/SaaS)

### Universal Repositories
- **JFrog Artifactory** — supports nearly every artifact type
- **Sonatype Nexus** — broad support, OSS option (Nexus 3 OSS)

### Language-Specific
- **npm**: public npm registry; private alternatives (Verdaccio, npm Enterprise)
- **PyPI**: public; private alternatives (devpi, Artifactory)
- **Maven Central / Sonatype OSSRH**: public; private alternatives (Artifactory, Nexus)
- **NuGet**: similar pattern

## Why Centralize Artifacts

- **Security**: vetted images/packages; scanning; signing
- **Speed**: local cache > pulling from Internet
- **Compliance**: SBOM, provenance retention
- **Availability**: survive upstream outage / yank
- **Cost**: avoid egress charges

## Immutable Tags

A tag should always refer to the same artifact. Anti-pattern: re-pushing `:latest` or `:v1.0`.

### Practice
- Tag with commit SHA (`my-app:abc123def`) — guaranteed unique
- Tag with semver (`my-app:1.2.3`) — never overwrite
- `latest` is a moving alias; never use in production

### Enforcement
- **ECR**: enable immutable tags on a repo (rejects re-push of existing tags)
- **GAR / ACR**: similar option
- **Harbor**: per-project setting

## Digests

The strongest form of pinning: SHA256 of the image manifest.

```bash
docker pull ghcr.io/me/app@sha256:abcdef...
```

K8s manifests can reference digests:
```yaml
image: ghcr.io/me/app@sha256:abcdef...
```

ArgoCD / Flux support digest pinning. Use for production-critical pods.

## Tag Strategy

```
my-app:1.2.3                              # semver
my-app:1.2.3-amd64                        # arch-specific
my-app:1.2.3-arm64
my-app:1.2                                # major.minor (moving — careful)
my-app:1                                  # major
my-app:abc123def                          # commit SHA
my-app:abc123def-amd64
my-app:main                               # branch (dev/staging only)
my-app:pr-456                             # PR-scoped
my-app@sha256:...                         # digest (strongest)
```

Production deploys should use SHA or digest, not floating tags.

## SBOMs

### Generating
```bash
# At build time (BuildKit native)
docker buildx build --sbom=true -t myimage --push .

# Standalone
syft myimage:tag -o spdx-json > sbom.spdx.json
syft myimage:tag -o cyclonedx-json > sbom.cdx.json
```

### Storage
- Attached to image as OCI artifact (BuildKit / cosign)
- Or in artifact repo alongside

### Verification on Pull
```bash
cosign download sbom myimage:tag
```

## Lifecycle / Retention

Artifacts grow unbounded without policy:

### ECR Example
- Keep last N tagged images per branch
- Delete untagged after N days
- Delete by tag pattern (dev:* after 7d)

### Implications
- Don't garbage-collect images deployed in prod (they're pulled on pod restart)
- Keep a "minimum N" floor for rollback capability
- Audit log of deletions

## Public vs Private Mirror Strategy

For OSS dependencies:
- Pull-through cache to public registry
- Or scan + republish to internal trusted registry
- Or vendor (commit deps to repo) — rare

### Pull-Through Cache
Most regulated orgs do:
- Internal artifact registry as proxy
- All builds pull from internal
- Internal updates from public (after scanning)
- If public is breached, you have a clean copy

## Signing & Verification

Image signing (Cosign) covered in L12. SBOM signing similar.

```bash
cosign attest --predicate sbom.spdx.json --type spdx myimage:tag
cosign verify-attestation --type spdx myimage:tag
```

## Interview Themes

- "Why immutable tags?"
- "Digest vs tag — when each?"
- "Artifact lifecycle — what should you keep?"
- "How does your CI publish artifacts?"
- "Pull-through cache — why?"
