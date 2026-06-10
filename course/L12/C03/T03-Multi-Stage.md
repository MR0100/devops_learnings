# L12/C03/T03 — Multi-Stage Builds

## Learning Objectives

- Build small production images
- Multiple FROM stages

## Multi-Stage

Multiple FROM statements; last is the final image.

```dockerfile
# Stage 1: Build
FROM golang:1.22 AS builder
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /app

# Stage 2: Runtime
FROM gcr.io/distroless/static
COPY --from=builder /app /
ENTRYPOINT ["/app"]
```

Final image: just runtime + binary.

## Why

Final image needs only runtime, not build tools.

Without multi-stage:
- 800 MB Java app (full JDK + Maven cache)

With multi-stage:
- 200 MB (just JRE + jar)
- Or 100 MB (Go static binary)

## Pattern

```dockerfile
FROM <builder> AS builder
# Install build tools
# Compile
# Output: /app or similar

FROM <runtime>
COPY --from=builder /app /
ENTRYPOINT ...
```

## Multiple Stages

```dockerfile
FROM node:20 AS frontend-builder
COPY frontend/ .
RUN npm install && npm run build

FROM golang:1.22 AS backend-builder
COPY backend/ .
RUN go build -o /app

FROM alpine
COPY --from=frontend-builder /dist /static
COPY --from=backend-builder /app /
ENTRYPOINT ["/app"]
```

For: monorepo with frontend + backend.

## Named Stages

```dockerfile
FROM x AS deps
FROM y AS test
FROM z AS prod
```

```bash
# Build specific stage
docker build --target test -t myapp:test .
docker build --target prod -t myapp:prod .
```

## Real Examples

### Go Static
```dockerfile
FROM golang:1.22 AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags='-w -s' \
    -o /app

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /app /
USER nonroot
ENTRYPOINT ["/app"]
```

Final: ~10 MB.

### Java Spring Boot
```dockerfile
FROM eclipse-temurin:17-jdk AS builder
WORKDIR /src
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn -B clean package -DskipTests

FROM eclipse-temurin:17-jre
COPY --from=builder /src/target/*.jar /app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

Or distroless:
```dockerfile
FROM gcr.io/distroless/java17
COPY --from=builder /src/target/*.jar /app.jar
CMD ["/app.jar"]
```

### Node React
```dockerfile
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
```

### Python
```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
COPY . .

FROM gcr.io/distroless/python3-debian12
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app
ENV PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/root/.local/lib/python3.11/site-packages
WORKDIR /app
CMD ["app.py"]
```

### Rust
```dockerfile
FROM rust:1.75 AS builder
WORKDIR /src
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
COPY src ./src
RUN touch src/main.rs && cargo build --release

FROM gcr.io/distroless/cc
COPY --from=builder /src/target/release/myapp /
ENTRYPOINT ["/myapp"]
```

## Cross-Stage Copy

```dockerfile
COPY --from=builder /app /app
COPY --from=other-image /etc/ssl /etc/ssl
COPY --from=alpine:3.18 /etc/passwd /etc/passwd
```

Copy from named stage or external image.

## Parallel Build (BuildKit)

```dockerfile
FROM A AS a
RUN slow-thing

FROM B AS b
RUN another-slow-thing

FROM scratch
COPY --from=a / /
COPY --from=b / /
```

`a` and `b`: parallel.

For: faster builds.

## Common Stages

```dockerfile
FROM base AS deps
# Deps install

FROM deps AS dev
# Dev tools

FROM deps AS test
# Test run

FROM deps AS builder
# Build for prod

FROM small AS prod
# Runtime
```

```bash
docker build --target dev -t myapp:dev .
docker build --target prod -t myapp:prod .
```

## Cache Optimization

```dockerfile
FROM golang:1.22 AS builder

# Cache deps
COPY go.mod go.sum ./
RUN go mod download

# Code
COPY . .
RUN go build -o /app
```

Code change ≠ re-download modules.

## BuildKit + Multi-Stage

```bash
DOCKER_BUILDKIT=1 docker build .
# or
docker buildx build .
```

Default in modern Docker. Parallel builds.

## Build Args Per Stage

```dockerfile
ARG VERSION
FROM base AS builder
RUN echo "Building ${VERSION}"

FROM final
ARG VERSION
LABEL version=${VERSION}
```

Args scoped per FROM.

## Cross-Compile

Build for multiple architectures:
```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.22 AS builder
ARG TARGETOS TARGETARCH
WORKDIR /src
COPY . .
RUN GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o /app

FROM gcr.io/distroless/static
COPY --from=builder /app /
ENTRYPOINT ["/app"]
```

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t myapp --push .
```

## Test Stage

```dockerfile
FROM builder AS test
RUN go test ./...

FROM builder AS prod
RUN go build -o /app
```

```bash
docker build --target test .   # runs tests
```

For: build-time tests.

## Lint Stage

```dockerfile
FROM golangci/golangci-lint AS lint
COPY . /src
WORKDIR /src
RUN golangci-lint run
```

```bash
docker build --target lint .
```

## Production Image

Minimal:
- Runtime
- App binary / jar / dist
- Required configs
- No build tools
- No package manager (if distroless)
- No shell (security)

## Inspect Layers

```bash
docker history myapp
# Shows final image layers
# Most from final FROM; not builder
```

## When NOT Multi-Stage

- Simple single-stage works
- Build cache reuse important (single stage caches differently)
- Tooling doesn't support

For most: multi-stage.

## .dockerignore Affects All

```
node_modules
.git
*.log
```

Applies to all build context.

## BuildKit Required for Some Features

```dockerfile
# syntax=docker/dockerfile:1.4
```

Top of file. Enables BuildKit features (cache mounts, secrets).

## Image Size Comparison

| | Without Multi-Stage | With Multi-Stage |
|---|---|---|
| Go app | 800 MB (golang:1.22) | 10 MB (scratch) |
| Java app | 700 MB (eclipse-temurin) | 200 MB (jre) |
| Node app | 1.2 GB (node:20) | 50 MB (nginx) |
| Python app | 1 GB (python:3.11) | 100 MB (slim) |

## Build Time

Multi-stage with cache: build time similar to single stage (most cached).

Without cache: slightly longer (builds multiple stages).

## CI Use

```yaml
- run: docker build --target prod -t myapp:${SHA} .
- run: docker push myapp:${SHA}
```

Per-target builds.

## Security

Smaller image = fewer CVEs = less attack surface.

For: production.

## Anti-Patterns

- Build tools in final image
- All in one stage
- Copy from many stages without cleanup
- Stages too granular (overhead)

## Best Practices

- Multi-stage always for prod
- Builder + runtime split
- Parallel stages where independent
- Use BuildKit
- Targeted builds in CI
- Minimal runtime base
- Multi-arch via buildx

## Common Mistakes

- Forgot --from
- Copy whole src to runtime (defeat purpose)
- Build deps in runtime
- Heavy runtime base

## Quick Refs

```dockerfile
# Pattern
FROM builder_base AS builder
# Build steps

FROM runtime_base
COPY --from=builder /built /

# Build
docker build --target STAGE -t TAG .
docker build .   # builds final
```

## Interview Prep

**Junior**: "What is multi-stage."

**Mid**: "Reduce image size."

**Senior**: "Multi-stage with parallel."

**Staff**: "Build pipeline for monorepo."

## Next Topic

→ [T04 — BuildKit & Build Secrets](T04-BuildKit.md)
