# L12/C03/T01 — Base Images (distroless, alpine, scratch, ubi)

## Learning Objectives

- Pick right base image
- Trade-offs per choice

## Common Bases

| Base | Size | Use |
|---|---|---|
| scratch | 0 | Static binary |
| distroless/static | ~2 MB | Static Go/Rust |
| distroless/base | ~20 MB | Dynamic apps |
| alpine | ~5 MB | Small + apk |
| busybox | ~1 MB | Shell + tools |
| ubuntu/debian-slim | ~30 MB | Full distro |
| ubi (Red Hat) | ~80 MB | Enterprise |

## scratch

```dockerfile
FROM scratch
COPY ./mybinary /
ENTRYPOINT ["/mybinary"]
```

No OS. Just binary + dependencies.

For: static binaries (Go with CGO=0, Rust musl).

Smallest possible.

## Distroless

Google's minimal images:
- gcr.io/distroless/static
- gcr.io/distroless/base
- gcr.io/distroless/python3
- gcr.io/distroless/java
- gcr.io/distroless/nodejs

No package manager, no shell. Just runtime.

```dockerfile
FROM gcr.io/distroless/python3
COPY app.py /
CMD ["app.py"]
```

For: production minimal + secure.

## Alpine

```dockerfile
FROM alpine:3.18
RUN apk add --no-cache python3
COPY app.py /
CMD ["python3", "/app.py"]
```

Small (~5 MB); package manager (apk).

Pros:
- Tiny
- Well-maintained
- Shell available

Cons:
- musl libc (not glibc) — compatibility issues for some apps
- DNS resolution differences
- Some libraries don't work

## Ubuntu / Debian

```dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3
COPY app.py /
CMD ["python3", "/app.py"]
```

Familiar; larger.

For: when alpine compatibility issues.

## Slim Variants

```dockerfile
FROM python:3.11-slim
# Smaller than python:3.11
```

Slim = minimal packages of distro.

For: balance familiarity + size.

## UBI (Universal Base Image)

Red Hat's:
```dockerfile
FROM registry.access.redhat.com/ubi9/ubi
```

Pros:
- RHEL-based (compatible)
- Security patches
- No subscription needed
- Enterprise-grade

For: RHEL ecosystem.

## Comparison

For Python app:

| Base | Size with app |
|---|---|
| python:3.11 (full) | ~1 GB |
| python:3.11-slim | ~150 MB |
| python:3.11-alpine | ~60 MB |
| distroless/python3 | ~50 MB |

Smaller = faster pull + less attack surface.

## Multi-Stage Build

Build in big; runtime in small:
```dockerfile
# Builder
FROM golang:1.22 AS builder
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /app

# Runtime
FROM gcr.io/distroless/static
COPY --from=builder /app /
ENTRYPOINT ["/app"]
```

Final image: just binary.

Covered T03 in detail.

## When scratch

- Static binary
- No dynamic deps
- No /etc/ssl, /etc/hosts (need)
- Bare minimum

Need CA certs:
```dockerfile
FROM alpine AS certs
RUN apk --update add ca-certificates

FROM scratch
COPY --from=certs /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY ./mybinary /
```

## When Distroless

- No shell needed (security)
- Dynamic libs needed (use base)
- Production
- Compliance-sensitive

Bonus: distroless has `:debug` variants with shell for troubleshooting.

```dockerfile
FROM gcr.io/distroless/base-debian12:debug
```

## When Alpine

- Need package manager
- Want small
- App works with musl

Test thoroughly; musl ≠ glibc.

## When Ubuntu/Debian

- Glibc required
- Familiar to team
- Specific packages
- Compat issues with alpine

## Image Selection Process

1. Identify language runtime (Python, Java, Go, Node)
2. Static or dynamic linking?
3. Need package manager at runtime?
4. Security stance?
5. Pick base

## Static (Go) → scratch / distroless/static

```dockerfile
FROM golang:1.22 AS builder
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags='-w -s' -o /app .

FROM gcr.io/distroless/static
COPY --from=builder /app /
ENTRYPOINT ["/app"]
```

## Java → distroless/java

```dockerfile
FROM eclipse-temurin:17 AS builder
COPY . .
RUN ./gradlew build

FROM gcr.io/distroless/java17
COPY --from=builder /app/build/libs/app.jar /app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

## Python → distroless/python3

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
COPY . .

FROM gcr.io/distroless/python3
COPY --from=builder /root/.local /root/.local
COPY . /app
ENV PATH=/root/.local/bin:$PATH PYTHONPATH=/root/.local/lib/python3.11/site-packages
WORKDIR /app
CMD ["app.py"]
```

## Node → distroless/nodejs

```dockerfile
FROM node:20 AS builder
COPY . .
RUN npm ci --production

FROM gcr.io/distroless/nodejs20
COPY --from=builder /app /app
WORKDIR /app
CMD ["index.js"]
```

## Tags / Versioning

```
ubuntu:22.04       # specific version
ubuntu:latest      # avoid in prod
alpine:3.18.4       # specific
alpine             # avoid

ubuntu@sha256:...  # immutable digest
```

For prod: pin to digest.

## Security Scanning

```bash
trivy image myapp
grype myapp
snyk container test myapp
```

Per-base CVE count varies:
- distroless: minimal CVEs
- alpine: small base; fewer
- ubuntu: more packages = more potential CVEs

## Update Cadence

Update base regularly:
- Distroless: rolling
- Alpine: per release
- Ubuntu: regular patches
- UBI: with Red Hat

Auto-rebuild + redeploy when base updates.

## Multi-Arch

Most bases support amd64 + arm64:
```dockerfile
FROM --platform=$BUILDPLATFORM alpine
```

For: Apple Silicon, Graviton.

## Rootless

Some bases default to root. Override:
```dockerfile
FROM alpine
RUN adduser -D -u 1000 appuser
USER appuser
```

Or distroless `:nonroot` variants:
```dockerfile
FROM gcr.io/distroless/static:nonroot
```

UID 65532 by default.

## Anti-Patterns

- Latest tags in prod
- Heavy bases (ubuntu) when slim works
- No security scans
- Don't update bases (CVE accumulation)

## Best Practices

- Distroless for prod (security + size)
- Multi-stage build
- Pin versions / digests
- Non-root user
- Scan in CI
- Re-build periodically (CVE fixes)
- Smallest viable base

## Test Compatibility

For alpine: test app works with musl.

```dockerfile
FROM alpine
# Test
RUN python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"
```

If errors: switch base.

## Common Issues

### Alpine Glibc
Some Python packages need glibc:
```
Error: libc.so.6: cannot open shared object file
```

Switch to slim Debian or use `alpine:edge` with packages.

### Time Zones
Distroless lacks tzdata sometimes. Set TZ env or include.

### CA Certs
scratch needs explicit CA certs.

## Size Comparison Real

Common app sizes:
- Java app on full JDK: 800 MB
- Same on distroless/java: 200 MB
- Go on ubuntu: 100 MB
- Go on scratch: 10 MB

## Quick Refs

```dockerfile
# Multi-stage (best for prod)
FROM BASE AS builder
...

FROM SMALL_BASE
COPY --from=builder /app /
ENTRYPOINT ["/app"]
```

Build:
```bash
docker build -t myapp .
docker images myapp   # check size
```

## Interview Prep

**Junior**: "Why small image."

**Mid**: "scratch vs alpine vs distroless."

**Senior**: "Image base for Java app."

**Staff**: "Org-wide base image strategy."

## Next Topic

→ [T02 — Layer Caching Strategy](T02-Layer-Caching.md)
