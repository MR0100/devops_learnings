# L12/C03/T04 — BuildKit & Build Secrets

## Learning Objectives

- Enable BuildKit
- Use secrets safely

## BuildKit

Modern Docker build engine:
- Faster (parallel)
- Cache mounts
- Build secrets
- SSH agent forwarding
- Better caching
- Frontends (different DSLs)

## Enable

```bash
# Set env
export DOCKER_BUILDKIT=1
docker build .

# Or use buildx (default)
docker buildx build .
```

Or `/etc/docker/daemon.json`:
```json
{ "features": { "buildkit": true } }
```

Modern Docker: BuildKit default.

## Dockerfile Frontend

```dockerfile
# syntax=docker/dockerfile:1.5
```

First line. Enables specific frontend version with features.

## Build Secrets

NEVER bake secrets in image:
```dockerfile
# BAD
ARG GITHUB_TOKEN
RUN curl -H "Authorization: token $GITHUB_TOKEN" ...
```

Token in layer; visible in image.

## Secret Mount

```dockerfile
# syntax=docker/dockerfile:1.5
RUN --mount=type=secret,id=github_token \
    GITHUB_TOKEN=$(cat /run/secrets/github_token) && \
    curl -H "Authorization: token $GITHUB_TOKEN" ...
```

```bash
docker build --secret id=github_token,src=$HOME/.github_token -t myapp .
```

Secret available during build; NOT in image.

## Multiple Secrets

```bash
docker build \
  --secret id=npmrc,src=$HOME/.npmrc \
  --secret id=gemrc,src=$HOME/.gemrc \
  -t myapp .
```

```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    --mount=type=secret,id=gemrc,target=/root/.gemrc \
    npm install && bundle install
```

## SSH Forward

For private Git:
```dockerfile
# syntax=docker/dockerfile:1.5
RUN --mount=type=ssh \
    git clone git@github.com:org/private-repo.git
```

```bash
ssh-add ~/.ssh/id_rsa
docker build --ssh default -t myapp .
```

SSH key not in image; agent forwarded during build.

## Cache Mounts

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

Cache persisted between builds; not in image.

For:
- pip / npm / cargo / go module caches
- Faster builds
- Cleaner images

## tmpfs Mount

```dockerfile
RUN --mount=type=tmpfs,target=/tmp \
    do-something-with-tmp
```

RAM-backed; not in image.

## Bind Mount

```dockerfile
RUN --mount=type=bind,source=./scripts,target=/scripts \
    /scripts/build.sh
```

Read from host during build.

## Inline Cache

```bash
docker buildx build \
  --cache-from type=registry,ref=myapp:cache \
  --cache-to type=registry,ref=myapp:cache,mode=max \
  -t myapp .
```

Cache pushed to registry; pulled in next build (different host).

For: CI runners (each is fresh).

## GitHub Actions Cache

```yaml
- uses: docker/setup-buildx-action@v3
- uses: docker/build-push-action@v5
  with:
    push: true
    tags: myapp:${{ github.sha }}
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

GitHub Actions cache for Docker layers.

## Multi-Platform

```bash
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t myapp --push .
```

Cross-arch builds. QEMU for non-native arch.

For: ARM Macs + Graviton.

## Parallel Stages

BuildKit builds independent stages in parallel:
```dockerfile
FROM A AS stage_a
RUN slow-thing

FROM B AS stage_b
RUN another-slow

FROM small
COPY --from=stage_a / /a
COPY --from=stage_b / /b
```

stage_a + stage_b: parallel.

## Provenance

```bash
docker buildx build --provenance=true -t myapp --push .
```

Image includes build attestation.

For: SLSA L3.

## SBOM

```bash
docker buildx build --sbom=true -t myapp --push .
```

Attaches SBOM.

## Output Formats

```bash
docker buildx build --output type=local,dest=./out .
# Build to local dir, not image
```

For: producing build artifacts.

## Frontend Variants

```dockerfile
# Buildpacks frontend
# syntax=docker/dockerfile:1
# Or different DSL
```

Future: BuildKit supports multiple input formats.

## Build Args

Differ from ENV:
- ARG: build-time
- ENV: build + runtime

```dockerfile
ARG VERSION=1.0
ENV APP_VERSION=$VERSION

RUN echo "Building ${VERSION}"
```

```bash
docker build --build-arg VERSION=2.0 -t myapp .
```

## Don't Pass Secrets via ARG

```dockerfile
# BAD
ARG SECRET
RUN echo $SECRET > /etc/secret
```

ARG visible in `docker history`. Use `--secret`.

## Image History (Inspect)

```bash
docker history myapp
# Shows commands; may leak ARGs if used incorrectly
```

## Builders

```bash
docker buildx ls
# Shows builder instances

docker buildx create --name mybuilder
docker buildx use mybuilder

docker buildx inspect --bootstrap
```

Multiple builders for different purposes.

## Remote Builder

Build on remote machine:
```bash
docker buildx create --name remote ssh://user@build-server
docker buildx use remote
docker buildx build .   # builds on server
```

For: powerful build machines.

## Build Outputs

```bash
docker buildx build --output type=image,push=true ...
docker buildx build --output type=oci,dest=image.tar ...
docker buildx build --output type=local,dest=./bin ...
```

Various.

## Cache Types

| Type | Use |
|---|---|
| inline | Cache in image (legacy) |
| registry | Separate registry tag |
| gha | GitHub Actions |
| s3 | AWS S3 |
| azblob | Azure Blob |

For CI: gha or registry.

## Cache Pruning

```bash
docker buildx prune --all
docker builder prune
```

For: free space.

## BuildKit vs Legacy

| | Legacy | BuildKit |
|---|---|---|
| Parallel | No | Yes |
| Cache mounts | No | Yes |
| Secrets | No | Yes |
| SSH | No | Yes |
| Multi-platform | Hard | Easy |
| Output formats | Image | Many |

BuildKit: default modern; recommended.

## Migration

If `DOCKER_BUILDKIT=0`: legacy.
Modern Docker: BuildKit default.

For old Dockerfiles: usually work; faster.

## Best Practices

- BuildKit always
- Secrets via --secret
- SSH forwarded for private repos
- Cache mounts for deps
- Multi-platform
- Cache pushed to registry / GHA
- Provenance + SBOM in production

## Common Mistakes

- ARG for secrets (leak in image)
- COPY private key into image
- Not using cache mounts (re-download)
- Forgot `# syntax=` directive

## Real-World Example

```dockerfile
# syntax=docker/dockerfile:1.5
FROM golang:1.22 AS builder
WORKDIR /src

# Cache modules
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/root/.cache/go-build \
    --mount=type=cache,target=/go/pkg/mod \
    go mod download

# Cache build
COPY . .
RUN --mount=type=cache,target=/root/.cache/go-build \
    --mount=type=cache,target=/go/pkg/mod \
    CGO_ENABLED=0 go build -o /app

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app /
USER nonroot
ENTRYPOINT ["/app"]
```

Fast + minimal.

## CI Example

```yaml
- uses: docker/setup-buildx-action@v3

- uses: docker/login-action@v3
  with:
    registry: ${{ env.REGISTRY }}
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}

- uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    platforms: linux/amd64,linux/arm64
    tags: |
      ${{ env.IMAGE }}:${{ github.sha }}
      ${{ env.IMAGE }}:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
    secrets: |
      GITHUB_TOKEN=${{ secrets.GH_PAT }}
    provenance: true
    sbom: true
```

Modern CI.

## Quick Refs

```bash
# Enable
export DOCKER_BUILDKIT=1

# Build
docker buildx build .

# Multi-platform
docker buildx build --platform linux/amd64,linux/arm64 ...

# Secret
docker build --secret id=NAME,src=PATH ...

# SSH
docker build --ssh default ...

# Cache
docker buildx build --cache-from=... --cache-to=...
```

## Interview Prep

**Mid**: "BuildKit benefits."

**Senior**: "Secrets in build."

**Staff**: "Build pipeline at scale."

## Next Topic

→ [T05 — ARG vs ENV](T05-ARG-vs-ENV.md)
