# L12/C04/T01 — Reducing Image Size

## Learning Objectives

- Shrink images
- Apply techniques systematically

## Why Small

- Faster pull (seconds vs minutes)
- Less storage (registry, nodes)
- Smaller attack surface
- Faster cold start (Lambda, etc.)

For: production essential.

## Techniques

1. Small base image
2. Multi-stage build
3. Remove build deps
4. Clean caches
5. Compress (minimal effect on layers)
6. Squash (rare)

## 1. Small Base

| Base | Size |
|---|---|
| ubuntu:22.04 | ~70 MB |
| debian:slim | ~30 MB |
| alpine | ~5 MB |
| distroless/static | ~2 MB |
| scratch | 0 |

Switch base = massive reduction.

## 2. Multi-Stage

Already covered. Final image = only runtime.

For Go: 800 MB → 10 MB.

## 3. Remove Build Deps

```dockerfile
# BAD
RUN apt-get update && apt-get install -y \
    build-essential gcc make python3-dev
# build deps stay in image
```

```dockerfile
# GOOD
RUN apt-get update && apt-get install -y \
    build-essential && \
    pip install ... && \
    apt-get purge -y --auto-remove build-essential && \
    rm -rf /var/lib/apt/lists/*
```

Install, use, remove in same RUN.

## 4. Clean Caches

### apt
```dockerfile
RUN apt-get update && \
    apt-get install -y package && \
    rm -rf /var/lib/apt/lists/*
```

### pip
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

### npm
```dockerfile
RUN npm ci --only=production && \
    npm cache clean --force
```

### yarn
```dockerfile
RUN yarn install --frozen-lockfile --production && \
    yarn cache clean
```

### apk (alpine)
```dockerfile
RUN apk add --no-cache python3
# --no-cache: don't keep apk cache
```

## 5. Combine RUNs

```dockerfile
# BAD (3 layers)
RUN apt-get update
RUN apt-get install -y x
RUN apt-get clean

# GOOD (1 layer)
RUN apt-get update && \
    apt-get install -y x && \
    rm -rf /var/lib/apt/lists/*
```

## 6. .dockerignore

```
.git
node_modules
*.log
.DS_Store
.env
.vscode
README.md
docs/
tests/
```

Excludes from build context. Smaller layers.

## Static Binaries

Go:
```dockerfile
RUN CGO_ENABLED=0 go build -ldflags='-w -s' -o /app
```

- `-w`: strip DWARF
- `-s`: strip symbol table

Smaller binary.

## Strip Binaries

For C/C++:
```bash
strip ./mybinary
```

Removes debug symbols.

## Compression

Don't gzip files in image (decompression at runtime):
```dockerfile
# Avoid
COPY data.tar.gz /data/
RUN tar -xzf /data/data.tar.gz   # extracts to image; bigger
```

Better: extract during build.

## Use Specific Tags

```dockerfile
FROM python:3.11-slim   # vs python:3.11 (full)
FROM node:20-alpine     # vs node:20 (debian)
```

Variants exist for size.

## Distroless Final

```dockerfile
FROM builder
...

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app /
USER nonroot
ENTRYPOINT ["/app"]
```

Distroless = minimal.

## SOURCE_DATE_EPOCH

For reproducible:
```dockerfile
RUN SOURCE_DATE_EPOCH=0 build-command
```

Reproducible builds; small win.

## Inspect

```bash
# Image size
docker images
docker inspect IMAGE --format '{{.Size}}'

# Layers
docker history IMAGE

# Dive (TUI)
dive IMAGE
```

## Dive

```bash
brew install dive
dive myimage
```

Interactive layer inspection. Identify waste.

## Size Analysis

```bash
docker history myimage --format "table {{.Size}}\t{{.CreatedBy}}"
```

Find big layers.

## Anti-Patterns

- COPY whole repo (use .dockerignore)
- Multiple RUN with related ops
- ADD when COPY ok
- No multi-stage
- Heavy base
- apt-get clean in separate RUN (doesn't help)

## Examples

### Go App
```dockerfile
FROM golang:1.22 AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags='-w -s' -o /app

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app /
USER nonroot
ENTRYPOINT ["/app"]
```

Final: ~10 MB.

### Python App
```dockerfile
FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends gcc

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

COPY . .

FROM gcr.io/distroless/python3-debian12
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app
ENV PATH=/root/.local/bin:$PATH PYTHONPATH=/root/.local/lib/python3.11/site-packages
WORKDIR /app
CMD ["app.py"]
```

Final: ~80 MB.

### Node App
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

FROM node:20-alpine
RUN addgroup -g 1000 app && adduser -D -u 1000 -G app app
WORKDIR /app
COPY --from=builder --chown=app:app /app/node_modules ./node_modules
COPY --chown=app:app . .
USER 1000
EXPOSE 8080
CMD ["node", "index.js"]
```

Or distroless/nodejs.

### Java App
```dockerfile
FROM eclipse-temurin:17-jdk AS builder
WORKDIR /src
COPY pom.xml .
RUN ./mvnw dependency:go-offline
COPY src ./src
RUN ./mvnw clean package -DskipTests

FROM gcr.io/distroless/java17-debian12:nonroot
COPY --from=builder /src/target/*.jar /app.jar
USER nonroot
CMD ["/app.jar"]
```

Final: ~150 MB.

## Tools

- dive: interactive
- skopeo inspect: details
- crane manifest: layers
- container-diff: compare

## Image Slim Tools

- docker-slim: auto-minimize
- distroless: prebuilt minimal
- chisel: chisel-cut UBI

`docker-slim build IMAGE`: produces minimized.

## Multi-Arch

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t myapp .
```

Per-arch images; not bigger total.

## Squash (Rarely)

```bash
docker build --squash -t myapp .
```

Combines layers; loses sharing benefit.

For: one-off small images.

## Lazy Loading

eStargz / zstd:chunked:
- Image format with lazy load
- Start before full pull
- Reduces cold start

Containerd supports.

## Cost

Smaller images:
- Faster CI
- Lower egress costs
- Faster scaling
- Less ECR storage cost

For 1000 services: significant.

## Best Practices

- Multi-stage always
- Distroless / scratch for final
- Single RUN per logical step
- Clean caches in same layer
- .dockerignore aggressive
- Static binaries where possible
- Strip symbols
- Pin base versions

## Common Mistakes

- Heavy base
- Build tools in runtime
- Forgot .dockerignore
- COPY before deps install
- No multi-stage

## Targets

For typical apps:
- Static binary: <50 MB
- Compiled (Java, Python): <300 MB
- Web app + Nginx: <50 MB

Aim for these.

## Quick Refs

```bash
# Inspect
docker images
docker history IMAGE
dive IMAGE

# Minimize
docker-slim build IMAGE
```

## Interview Prep

**Junior**: "Why smaller image."

**Mid**: "Image reduction techniques."

**Senior**: "Distroless for prod."

**Staff**: "Image strategy at org scale."

## Next Topic

→ [T02 — Reproducible Builds](T02-Reproducible-Builds.md)
