# L12/C04/T02 — Reproducible Builds

## Learning Objectives

- Build reproducibly
- Apply to security

## Reproducibility

Same source + same build → same binary (byte-for-byte).

For:
- Verify build wasn't tampered
- Cache hits more reliable
- SLSA compliance
- Trust supply chain

## Sources of Non-Determinism

- Timestamps
- File order
- Compiler versions
- Random IDs
- Network fetches
- Build env vars

## Mitigations

### Pin Everything
- Base image @ digest
- Package versions explicit
- Build tool version

```dockerfile
FROM ubuntu@sha256:abc... AS builder
```

### Timestamps
Set SOURCE_DATE_EPOCH:
```dockerfile
ARG SOURCE_DATE_EPOCH
RUN find /app -exec touch -d @$SOURCE_DATE_EPOCH {} \;
```

Files mtime set deterministically.

### File Order
Tar with sorted entries:
```bash
find . -type f -print0 | sort -z | tar --null -T - -czf out.tar.gz
```

## Buildah Reproducible

```bash
buildah build --timestamp 0 ...
```

Sets layer timestamps to epoch.

## Docker

Docker buildkit:
```bash
SOURCE_DATE_EPOCH=$(git log -1 --format=%ct) \
docker buildx build --output type=image .
```

## Identical Layers

For reproducibility:
- Same Dockerfile
- Same context
- Same SOURCE_DATE_EPOCH
- Same buildkit version

Result: same digest.

## Verify

```bash
# Build twice
SOURCE_DATE_EPOCH=1234567890 docker build -t img1 .
SOURCE_DATE_EPOCH=1234567890 docker build -t img2 .

# Compare
docker inspect img1 --format '{{.Id}}'
docker inspect img2 --format '{{.Id}}'

# Same digest = reproducible
```

## Go Reproducible

```bash
go build -trimpath -ldflags="-buildid="
```

- `-trimpath`: remove paths
- `-buildid=""`: no build ID

For reproducible Go binaries.

## Rust Reproducible

```bash
cargo build --frozen --locked
```

With:
- Locked deps
- Cargo.lock committed
- Pinned rust version

## Java Reproducible

Set timestamps in jar:
```bash
zip -X archive.jar
# -X: no extra fields (no timestamps)
```

Or Reproducible Maven plugin.

## Node Reproducible

```bash
npm ci --frozen-lockfile
```

With package-lock.json committed.

Result close to reproducible (not byte-perfect).

## File Permissions

Set deterministically:
```dockerfile
COPY --chmod=644 . /app/
```

Permissions consistent.

## Cleanup

Remove non-deterministic files:
- /var/cache/
- /tmp/
- /var/log/
- Build temp

In same RUN.

## Build Provenance

Attach metadata:
```bash
docker buildx build --provenance=true -t myapp --push .
```

Includes:
- Source commit
- Builder identity
- Materials (base images)
- Build script

## SLSA Levels

- L1: build script
- L2: hosted + signed provenance
- L3: hardened build platform
- L4: hermetic, reproducible

For L4: full reproducibility.

## Hermetic Build

Build doesn't access network or unpinned resources:
- All deps pinned by hash
- No network during build (or proxied)
- Build environment captured

For: Bazel, Nix.

## Bazel

```python
# BUILD.bazel
load("@io_bazel_rules_docker//container:container.bzl", "container_image")

container_image(
    name = "myapp",
    base = "@distroless_static//image",
    entrypoint = ["/app"],
    files = [":app"],
)
```

Bazel: hermetic by design. Reproducible.

## Nix

```nix
# default.nix
pkgs.dockerTools.buildLayeredImage {
  name = "myapp";
  tag = "latest";
  contents = [ pkgs.python3 ];
  config = {
    Cmd = [ "${pkgs.python3}/bin/python3" "/app/main.py" ];
  };
}
```

Nix: highly reproducible. Hash-pinned deps.

## SOURCE_DATE_EPOCH

Standard for reproducible builds:
```bash
SOURCE_DATE_EPOCH=$(git log -1 --format=%ct)
```

Tools (gcc, tar, etc.) honor.

## Image Digest

Same source + same build → same digest.

Push by digest:
```bash
docker push myapp@sha256:abc...
```

Pull by digest:
```bash
docker pull myapp@sha256:abc...
```

Immutable.

## Diff Two Builds

```bash
container-diff diff img1 img2
```

Shows differences. For reproducibility: should be empty.

## Build Cache Invalidation

For reproducible:
- Same cache state required
- Or: build fresh (no cache)

Sometimes: cached layers differ across runs slightly.

For exact: `--no-cache`.

## Cosign Attestations

```bash
cosign attest --predicate provenance.json --type slsaprovenance myimage
```

Attaches signed attestation.

For: verify build details.

## Verification

```bash
cosign verify-attestation --type slsaprovenance \
  --certificate-identity-regexp '.*github.com/myorg/.*' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  myimage
```

Validates provenance.

## CI Setup

```yaml
- uses: docker/setup-buildx-action@v3

- name: Build with provenance
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: myimage:${{ github.sha }}
    provenance: mode=max
    sbom: true
```

GitHub Actions: automated provenance.

## Image as Code

Treat image build as deterministic function:
- Input: source + deps
- Output: same digest always

For: trust, verification, caching.

## When NOT Reproducible

- Quick dev builds
- Local testing
- Pre-prod experimentation

Reproducibility costs time. Worth for prod.

## Best Practices

- Pin base by digest
- Pinned deps (lock files)
- SOURCE_DATE_EPOCH
- BuildKit provenance
- Sign images (cosign)
- SBOM attached
- Verify in deploy

## Common Mistakes

- :latest tags (mutable)
- Unpinned deps
- Network during build (varies)
- Timestamps from build time
- No verification at deploy

## Tools

- BuildKit (provenance + SBOM)
- Cosign (signing)
- Syft (SBOM)
- Bazel / Nix (hermetic)
- container-diff (compare)

## Real-World

Production:
- Pin to digest in K8s manifests
- Sign all production images
- Verify signatures via policy
- Attest provenance

```yaml
image: myregistry.com/myapp@sha256:abc...
```

## Quick Refs

```bash
# Pin digest
docker pull myapp@sha256:...
docker inspect myapp --format '{{.Id}}'

# Provenance
docker buildx build --provenance=mode=max --sbom=true ...

# Sign
cosign sign myimage

# Attest
cosign attest --predicate file.json --type X myimage

# Verify
cosign verify ...
```

## Interview Prep

**Mid**: "Reproducible build."

**Senior**: "SLSA L3 setup."

**Staff**: "Supply chain security org-wide."

## Next Topic

→ [T03 — SBOMs & Provenance](T03-SBOMs-Provenance.md)
