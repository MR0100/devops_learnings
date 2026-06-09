# L12/C03 — Dockerfile Mastery

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Base-Images.md) | Base Images (distroless, alpine, scratch, ubi) | 1 hr |
| [T02](T02-Layer-Caching.md) | Layer Caching Strategy | 1 hr |
| [T03](T03-Multi-Stage.md) | Multi-Stage Builds | 1 hr |
| [T04](T04-BuildKit.md) | BuildKit & Build Secrets | 1 hr |
| [T05](T05-ARG-ENV.md) | ARG vs ENV | 0.5 hr |
| [T06](T06-HEALTHCHECK-USER.md) | HEALTHCHECK, USER, ENTRYPOINT vs CMD | 0.5 hr |

## Base Image Tour

| Base | Size | Pros | Cons |
|---|---|---|---|
| `scratch` | 0 | Smallest possible; only your binary | No shell, no libc; statically-linked only |
| `gcr.io/distroless/static` | ~2 MB | Statically-linked; no shell; secure | Hard to debug |
| `gcr.io/distroless/base` | ~17 MB | glibc + a few libs; no shell | Hard to debug |
| `alpine:3` | ~7 MB | Has shell, busybox; tiny | musl libc (occasional issues with Go DNS, Python wheels) |
| `debian:bookworm-slim` | ~75 MB | Familiar glibc + apt | Larger |
| `ubuntu:24.04` | ~80 MB | Familiar; long support | Larger |
| `redhat/ubi9-minimal` | ~110 MB | Red Hat support; compliance | Largest among "minimal" |

### Picking
- **Go / Rust**: distroless static or scratch
- **Java**: distroless java or alpine + JRE (or stripped JRE)
- **Python**: python:3-slim → switch to distroless if you can
- **Node**: node:20-alpine
- **Anything needing shell debugging**: alpine or debian-slim

## Layer Caching

Each Dockerfile instruction creates a layer. Docker caches if inputs match.

### Order Matters

```dockerfile
# BAD — copying everything invalidates dep cache on every code change
COPY . /app
RUN cd /app && pip install -r requirements.txt

# GOOD — deps cached separately
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
COPY . /app/
```

Put the things that change LEAST at the top.

### .dockerignore
Critical:
```
.git/
__pycache__/
*.pyc
node_modules/
.env
*.log
.terraform/
.venv/
```

Skipped files don't go into build context (faster builds, smaller images).

## Multi-Stage Builds

Stage 1 builds; Stage 2 runs. Drops build tools from runtime.

### Go
```dockerfile
# syntax=docker/dockerfile:1.6
FROM golang:1.22-bookworm AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download
COPY . .
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -ldflags='-s -w' -o /out/app ./cmd/app

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /out/app /usr/local/bin/app
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/app"]
```

### Node
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build && npm prune --production

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/node_modules /app/node_modules
COPY package*.json ./
USER node
CMD ["node", "dist/index.js"]
```

### Python
```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM python:3.12-slim
COPY --from=builder /install /usr/local
COPY . /app
WORKDIR /app
USER 1000
CMD ["python", "main.py"]
```

## BuildKit

Modern Docker builder (default since 23.0). Features:

- **Parallel** stage build (DAG)
- **Cache mounts** (persistent across builds): `--mount=type=cache`
- **Bind mounts** during build: `--mount=type=bind`
- **Secrets**: `--mount=type=secret` (no leak in layers)
- **SSH agent forwarding**: `--mount=type=ssh`
- **Multi-platform**: `--platform=linux/amd64,linux/arm64`

### Cache Mounts
```dockerfile
RUN --mount=type=cache,target=/root/.cache/go-build \
    --mount=type=cache,target=/go/pkg/mod \
    go build -o /out/app
```
Cache persists across builds; not in the resulting image.

### Build Secrets
```dockerfile
# Dockerfile
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) npm install
```

```bash
docker build --secret id=npm_token,env=NPM_TOKEN -t app .
```
Secret doesn't end up in the image.

### Multi-Platform Builds
```bash
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t myimage --push .
```

Builds for both archs in parallel; pushes single manifest list (multi-arch).

## ARG vs ENV

### ARG
- Build-time variable only
- Not in final image
- `--build-arg KEY=VALUE`

```dockerfile
ARG VERSION=1.0
RUN echo "Building v$VERSION"   # available
# At runtime, VERSION is NOT available
```

### ENV
- Build and runtime
- Persists in image and container

```dockerfile
ENV PORT=8080
EXPOSE $PORT
CMD ["./app", "--port", "8080"]
```

> Secrets must not be in ARG or ENV — both can leak.

## HEALTHCHECK

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/healthz || exit 1
```

- Docker tracks container health
- K8s ignores this; uses its own probes
- Useful for Docker Compose, Docker Swarm

## USER

Avoid running as root.

```dockerfile
RUN groupadd -r app && useradd -r -g app -s /sbin/nologin app
USER app:app
```

Or use a numeric UID (better for K8s `runAsNonRoot`):
```dockerfile
USER 10001:10001
```

## ENTRYPOINT vs CMD

| | ENTRYPOINT | CMD |
|---|---|---|
| Purpose | The command (immutable) | Default args (override on docker run) |
| Form | exec (preferred) or shell | exec or shell |

```dockerfile
ENTRYPOINT ["/app"]
CMD ["--port", "8080"]

# docker run myimage              → /app --port 8080
# docker run myimage --port 9090  → /app --port 9090
```

### Exec form vs Shell form
```dockerfile
CMD ["./app"]            # exec form (no shell; PID 1 = app)
CMD ./app                # shell form (sh -c ./app; PID 1 = sh)
```

Use exec form. Shell form breaks signal propagation.

## Other Useful Instructions

- `WORKDIR /app` — set working dir
- `EXPOSE 8080` — documentation (doesn't publish)
- `LABEL maintainer="ops@example.com"` — metadata
- `ONBUILD ...` — triggered when used as base
- `VOLUME ["/data"]` — declare volume mount point
- `STOPSIGNAL SIGINT` — signal to stop (default SIGTERM)

## Interview Themes

- "Optimize this Dockerfile"
- "Multi-stage build — what does it solve?"
- "Build secrets — how do you handle them safely?"
- "ARG vs ENV"
- "ENTRYPOINT vs CMD"
- "Compare base image choices"
