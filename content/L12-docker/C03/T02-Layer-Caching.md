# L12/C03/T02 — Layer Caching Strategy

## Learning Objectives

- Order Dockerfile for cache hits
- Speed up builds

## Cache Mechanics

Each Dockerfile instruction → layer.
Build:
- Check cache for matching layer
- Hit: reuse
- Miss: rebuild from this layer down

For: fast builds when little changes.

## Cache Key

Per instruction:
- Instruction text
- Files referenced (for COPY/ADD)
- Parent layer

If any change → cache miss.

## Order Matters

```dockerfile
# BAD
COPY . /app                  # changes often
RUN apt-get install -y ...   # invalidated by COPY

# GOOD
RUN apt-get install -y ...   # rarely changes; cached
COPY . /app                  # last (changes most)
```

Put rarely-changed before often-changed.

## Dependency First

```dockerfile
# BAD
COPY . /app
RUN pip install -r requirements.txt   # invalidated by code change

# GOOD
COPY requirements.txt /app/
RUN pip install -r requirements.txt   # cached if requirements.txt unchanged
COPY . /app                            # last
```

Install deps from copied dep file; then copy code.

## Multi-Stage

Builder stage: cache install
Runtime: minimal copy

```dockerfile
FROM python:3.11 AS builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
```

## Caching Specific Commands

### apt-get
```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        package1 \
        package2 && \
    rm -rf /var/lib/apt/lists/*
```

Single RUN; clean up cache; smaller layer.

### npm
```dockerfile
COPY package.json package-lock.json ./
RUN npm ci --production
COPY . .
```

### Go modules
```dockerfile
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN go build
```

Modules cached separately from code.

### Pip
```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```

`--no-cache-dir`: pip's cache; don't store in layer.

## BuildKit Cache

Modern; persistent across builds:
```dockerfile
# syntax=docker/dockerfile:1.4

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

Pip's cache persisted between builds. Faster.

```dockerfile
# Go module cache
RUN --mount=type=cache,target=/root/.cache/go-build \
    --mount=type=cache,target=/go/pkg/mod \
    go build
```

## Cache From

For CI:
```bash
docker build --cache-from myapp:latest -t myapp:new .
```

Pull previous; use as cache base.

Or BuildKit:
```bash
docker buildx build \
  --cache-from type=registry,ref=myapp:cache \
  --cache-to type=registry,ref=myapp:cache,mode=max \
  -t myapp .
```

Distributed cache.

## ARG vs Cache

```dockerfile
ARG VERSION=1.0
RUN curl -O https://example.com/app-${VERSION}.tar.gz
```

Build arg change → cache miss.

For stable: hardcode.

## .dockerignore

```
.git
node_modules
*.log
.DS_Store
.env
```

Excluded from build context; avoids cache miss.

For: stop unnecessary files invalidating cache.

## Inspect Cache Usage

```bash
docker history IMAGE
# Shows layers + cache info

docker build --progress=plain .
# Shows what's cached vs not
```

## Common Anti-Patterns

### Copy All First
```dockerfile
# BAD
COPY . .
RUN npm install
```

Every code change → re-install.

### Separate apt-get update + install
```dockerfile
# BAD
RUN apt-get update
RUN apt-get install -y package
# Possible stale apt cache
```

Combine:
```dockerfile
RUN apt-get update && apt-get install -y package
```

### --no-cache-dir not used
Pip / npm cache in image: bloat + cache contamination.

## Useful Patterns

### Common Deps Layer
```dockerfile
FROM base
RUN apt-get install -y curl jq vim
# Used by many apps; cached
COPY . .
```

### Builder Cache
```dockerfile
FROM golang:1.22 AS builder

# Cache: just modules
COPY go.mod go.sum ./
RUN go mod download

# Code (changes often)
COPY . .
RUN go build
```

## BuildKit Features

### Mount Cache
```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
```

### Mount Secret
```dockerfile
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc \
    npm install
```

```bash
docker build --secret id=npmrc,src=~/.npmrc -t myapp .
```

For private packages without baking secret.

### Mount SSH
```dockerfile
RUN --mount=type=ssh \
    git clone git@github.com:org/private.git
```

```bash
docker build --ssh default -t myapp .
```

## Parallel Build (Multi-Stage)

BuildKit builds multi-stage in parallel:
```dockerfile
FROM A AS a
...

FROM B AS b
...

FROM C
COPY --from=a / /
COPY --from=b / /
```

a + b: parallel.

For: faster builds.

## Frontend Specific

For npm/yarn:
```dockerfile
# Cache deps
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile

# Code
COPY . .
RUN yarn build

# Runtime
FROM nginx
COPY --from=builder /app/dist /usr/share/nginx/html
```

## Backend Specific

Java (Maven):
```dockerfile
FROM maven:3.9 AS builder

# Cache deps
COPY pom.xml .
RUN mvn dependency:go-offline

# Code
COPY src ./src
RUN mvn package

FROM eclipse-temurin:17-jre
COPY --from=builder /target/app.jar /app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

## Cache Size

Layers add up. Optimize:
- Combine RUNs (single layer)
- Clean up in same RUN
- Use multi-stage to exclude build artifacts

## Buildx

Modern Docker build:
```bash
docker buildx build ...
```

BuildKit features; multi-arch; distributed cache.

## Best Practices

- Order: rarely-changed first
- Multi-stage builds
- BuildKit mount cache
- .dockerignore aggressive
- Pin versions
- Clean up apt / pip / npm cache
- Cache from registry in CI

## Common Mistakes

- COPY . . at top (invalidates everything)
- Separate apt-get update + install (stale cache)
- No .dockerignore (unnecessary cache busts)
- ARG changes ignoring cache implications
- Forgetting --no-cache-dir for pip

## CI Optimization

For multi-job builds:
```yaml
- run: docker buildx build \
    --cache-from type=gha \
    --cache-to type=gha,mode=max \
    -t myapp .
```

GitHub Actions cache for Docker. Significant speedup.

## Image Bloat

Heavy layers from caches:
```dockerfile
# BAD
RUN apt-get update
RUN apt-get install -y x y z
RUN apt-get clean

# GOOD (single layer)
RUN apt-get update && \
    apt-get install -y x y z && \
    rm -rf /var/lib/apt/lists/*
```

Separate cleans: cleanup in different layer; original layer still bloated.

## When Cache Hurts

For security-critical:
- Rebuilds important (CVE updates)
- Cache may serve stale

Mitigation:
- Periodic rebuild
- `docker build --no-cache`
- Update base image often

## Verify

```bash
docker build .
# Real: 30s

docker build .
# Cached: 2s
```

If second build slow: cache misses.

`docker build --progress=plain` to see.

## Quick Refs

```bash
# Build
docker build .
docker build --no-cache .

# Buildx
docker buildx build --cache-from=... --cache-to=...

# Inspect
docker history IMAGE
docker build --progress=plain .

# Dockerfile
COPY package.json .
RUN install
COPY . .

# BuildKit
RUN --mount=type=cache,target=/root/.cache/X ...
RUN --mount=type=secret,id=X ...
```

## Interview Prep

**Junior**: "Layer cache."

**Mid**: "Dockerfile order."

**Senior**: "BuildKit cache mounts."

**Staff**: "Build time optimization for 50 services."

## Next Topic

→ [T03 — Multi-Stage Builds](T03-Multi-Stage.md)
