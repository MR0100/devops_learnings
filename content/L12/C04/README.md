# L12/C04 — Image Optimization

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Reducing-Image-Size.md) | Reducing Image Size | 1 hr |
| [T02](T02-Reproducible-Builds.md) | Reproducible Builds | 0.5 hr |
| [T03](T03-SBOMs-Provenance.md) | SBOMs & Provenance | 1 hr |

## Image Size Reduction

### Why It Matters
- Smaller = faster pull = faster startup
- Smaller = less attack surface
- Smaller = lower storage / bandwidth cost
- Smaller = easier to reason about (less unknown software)

### Techniques

#### 1. Multi-Stage Builds
(See C03)

#### 2. Smaller Base
- scratch / distroless for compiled languages
- -slim / -alpine variants
- Native ARM (Graviton) for ~10-20% smaller in some cases

#### 3. Minimize Layers
Combine RUN commands when there's no caching benefit to splitting:

```dockerfile
# Bad — adds layer + leaves cache
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get clean

# Good — single layer + cleanup
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
```

#### 4. Clean Up in Same Layer
Files deleted in a LATER layer don't reduce image size (the layer still has them). Clean up in the SAME RUN:

```dockerfile
RUN curl -O https://example.com/big.tar.gz && \
    tar xf big.tar.gz && \
    rm big.tar.gz                   # cleaned in same layer
```

#### 5. Use --no-install-recommends, --no-cache
```dockerfile
RUN apt-get install -y --no-install-recommends nginx
RUN pip install --no-cache-dir -r requirements.txt
RUN apk add --no-cache curl
```

#### 6. Strip Binaries
```dockerfile
RUN strip /usr/local/bin/app
```

For Go: `-ldflags="-s -w"` strips symbol tables.

#### 7. Avoid Build Tools in Final Image
Use multi-stage; final stage has only runtime needs.

#### 8. Static Binaries
For Go/Rust: build statically; use `scratch` or distroless static.

```dockerfile
# Go
RUN CGO_ENABLED=0 go build -ldflags='-s -w' -o /out/app
FROM scratch
COPY --from=builder /out/app /app
ENTRYPOINT ["/app"]
```

#### 9. Dive Tool
Analyze image layers and find waste:
```bash
dive myimage:tag
```

Shows file system per layer and identifies space wasted.

## Reproducible Builds

Goal: building the same source produces a byte-identical image. Important for security verification.

### Challenges
- Timestamps (file mtimes, build time)
- Random order of installed files
- Package metadata that varies
- Build host info (kernel, hostname)
- Non-deterministic compilers

### Tools
- **Buildkit** with `SOURCE_DATE_EPOCH` for timestamps
- **ko** for Go: builds Go images reproducibly
- **kaniko** (Google): runs in-cluster, deterministic
- **nixpkgs / Nix**: most reproducible

### Practical Approximation
For most purposes, "same image content + same dependencies → same image" is enough. Pin everything:
- Base image SHA (not `:latest`)
- Package versions (e.g., `apt install nginx=1.24.0-2`)
- Language deps (lockfiles)

```dockerfile
FROM debian:bookworm-slim@sha256:abc...
```

## SBOM (Software Bill of Materials)

What's in your image? Lists every package, language dep, and version.

### Standards
- **SPDX**: OSS-friendly, widely supported
- **CycloneDX**: vendor-friendly, security-focused

### Generating
```bash
syft myimage -o cyclonedx-json > sbom.json
syft myimage -o spdx-json > sbom.spdx.json

# Docker BuildKit can attach during build
docker buildx build --sbom=true -t myimage --push .
```

### Why It Matters
- Vulnerability scanning (match SBOM to CVE database)
- Compliance (SBOM is often required for fed/regulated)
- Supply-chain incident response (Log4Shell — "where is log4j?")

## Provenance

Who built it, where, when, how? In-toto attestations.

```bash
docker buildx build --provenance=true -t myimage --push .
```

Attestations attached to image; verifiable later.

### SLSA Levels
- **SLSA 1**: provenance generated
- **SLSA 2**: hosted build; signed provenance
- **SLSA 3**: hardened build; non-falsifiable
- **SLSA 4**: two-person review; hermetic

GitHub Actions + Buildx → SLSA 3 capable.

## Vulnerability Scanning

```bash
# Trivy (free, fast, comprehensive)
trivy image myimage:tag
trivy image --severity HIGH,CRITICAL myimage:tag

# Grype
grype myimage:tag

# Snyk
snyk container test myimage:tag

# AWS ECR Enhanced Scanning (Inspector)
# GCP Artifact Registry scanning
# Azure Container Registry scanning
```

Use in CI: fail PR if HIGH/CRITICAL count grows.

## Image Signing

Cosign (Sigstore) — keyless OIDC signing:

```bash
# Sign
COSIGN_EXPERIMENTAL=1 cosign sign --yes ghcr.io/me/app:v1

# Verify
cosign verify --certificate-identity-regexp '.+@example.com' \
              --certificate-oidc-issuer https://accounts.google.com \
              ghcr.io/me/app:v1
```

K8s admission policy verifies signatures at deploy.

## Putting It All Together (Production Image)

```dockerfile
# syntax=docker/dockerfile:1.6
FROM golang:1.22-bookworm AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download
COPY . .
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -trimpath -ldflags='-s -w' -o /out/app ./cmd/app

FROM gcr.io/distroless/static-debian12:nonroot
LABEL org.opencontainers.image.source="https://github.com/me/app"
COPY --from=builder /out/app /usr/local/bin/app
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/app"]
```

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --sbom=true \
  --provenance=true \
  --push \
  -t ghcr.io/me/app:v1 .

cosign sign --yes ghcr.io/me/app:v1
```

## Interview Themes

- "Optimize this image"
- "Reproducible builds — what's hard?"
- "SBOM — why?"
- "How does Cosign keyless signing work?"
- "Vulnerability scanning — what to do with results"
