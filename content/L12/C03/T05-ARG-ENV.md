# L12/C03/T05 — ARG vs ENV

## Learning Objectives

- Distinguish ARG from ENV
- Use each correctly

## ARG

Build-time variable:
```dockerfile
ARG VERSION=1.0
RUN echo "Building version ${VERSION}"
```

Available only during build.

Override:
```bash
docker build --build-arg VERSION=2.0 -t myapp .
```

## ENV

Runtime variable:
```dockerfile
ENV APP_VERSION=1.0
ENV NODE_ENV=production
CMD ["node", "app.js"]
```

Available during build AND in running container.

In running container:
```bash
docker run myapp env
# APP_VERSION=1.0
# NODE_ENV=production
```

## Differences

| | ARG | ENV |
|---|---|---|
| Build-time | Yes | Yes |
| Runtime | No | Yes |
| In image | Metadata only | Yes |
| Override at run | No | Yes (with -e) |

## Use ARG For

- Version selection at build
- Build-time toggles
- Compiler flags
- Build args from CI

```dockerfile
ARG GO_VERSION=1.22
FROM golang:${GO_VERSION} AS builder
```

```bash
docker build --build-arg GO_VERSION=1.21 .
```

## Use ENV For

- App configuration
- Runtime values
- Inherited by child processes

```dockerfile
ENV PORT=8080
ENV LOG_LEVEL=info
```

```bash
docker run -e PORT=9090 myapp
# Override at runtime
```

## ARG Scope

```dockerfile
ARG GLOBAL_ARG       # before FROM: only in FROM line

FROM base
ARG STAGE_ARG        # after FROM: this stage only
RUN echo $STAGE_ARG

FROM small
ARG STAGE_ARG        # re-declare for new stage
RUN echo $STAGE_ARG
```

ARG before FROM: limited.
ARG after FROM: per stage.

## ENV vs ARG Conversion

```dockerfile
ARG VERSION
ENV APP_VERSION=$VERSION
```

ARG → ENV: makes available at runtime.

## Build-Time-Only Values

For values needed only during build, ARG is safer:
- Not in image
- Not in `docker inspect`
- Cleaner

## Secret in ARG (BAD)

```dockerfile
# BAD
ARG SECRET_TOKEN
RUN curl -H "Authorization: token $SECRET_TOKEN" ...
```

ARG visible in `docker history`. Use `--secret`.

## Default Values

```dockerfile
ARG VERSION=latest
ENV PORT=8080
```

If not provided: defaults.

## Multi-Stage Build

```dockerfile
ARG BASE_IMAGE=alpine:3.18

FROM ${BASE_IMAGE} AS builder
...

FROM ${BASE_IMAGE}
...
```

ARG before FROM works for substituting in FROM.

## Predefined ARGs

```dockerfile
FROM --platform=$BUILDPLATFORM golang:1.22 AS builder

ARG BUILDPLATFORM
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

RUN echo "Building on $BUILDPLATFORM for $TARGETPLATFORM"
```

For cross-compilation.

## Docker Compose

```yaml
services:
  app:
    build:
      context: .
      args:
        VERSION: ${VERSION:-1.0}
    environment:
      LOG_LEVEL: info
```

`args`: ARG passed to build.
`environment`: ENV in container.

## K8s

K8s sets ENV for pods:
```yaml
env:
- name: PORT
  value: "8080"
```

Equivalent to `ENV PORT=8080` in Dockerfile but at runtime.

K8s ENV overrides Dockerfile ENV.

## Best Practices

- ARG for build configuration
- ENV for runtime
- Default values
- Don't put secrets in either
- Document purpose

## Common Mistakes

- Secrets in ARG (visible in history)
- ENV for build-only (bloats image)
- Hardcoded vs parameterized (no flexibility)
- Forgot ARG after FROM (out of scope)

## Inspect

```bash
docker history myapp --no-trunc
# Shows ENV / ARG used

docker inspect myapp | jq '.[].Config.Env'
# Shows ENV in final image
```

## ARG in Multi-Stage

Each FROM: new scope. Re-declare ARG:
```dockerfile
ARG VERSION

FROM base AS builder
ARG VERSION
RUN echo $VERSION

FROM small
ARG VERSION
RUN echo $VERSION
```

Or use ENV in stage (persists):
```dockerfile
ARG VERSION
FROM base AS builder
ENV VERSION=$VERSION
```

## Common Patterns

### Version Bump
```dockerfile
ARG APP_VERSION=latest
LABEL version=$APP_VERSION
```

CI passes specific version.

### Build Mode
```dockerfile
ARG BUILD_MODE=production
RUN npm run build:${BUILD_MODE}
```

For dev vs prod builds.

### Conditional Install
```dockerfile
ARG INSTALL_DEV_DEPS=false
RUN if [ "$INSTALL_DEV_DEPS" = "true" ]; then \
      npm install; \
    else \
      npm install --production; \
    fi
```

For dev images.

## ENV in Production

```dockerfile
ENV NODE_ENV=production \
    PORT=8080 \
    LOG_LEVEL=info
```

Single ENV instruction; fewer layers.

## Sensitive ENV

For secrets at runtime:
- Don't bake in image
- Set via `docker run -e` or K8s Secrets

```bash
docker run -e DB_PASSWORD=$DB_PASS myapp
```

Or:
```yaml
# K8s
env:
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-secret
      key: password
```

## Composing

```dockerfile
ARG VERSION
ENV BUILD_VERSION=${VERSION}
ENV APP_HOME=/app
ENV LOG_FILE=${APP_HOME}/log.txt

WORKDIR ${APP_HOME}
COPY . .
```

ENV references other ENV.

## ARG for Conditional FROM

```dockerfile
ARG BASE_IMAGE=alpine:3.18

FROM ${BASE_IMAGE}
```

Switch base image at build.

## Order Matters

```dockerfile
ARG VERSION=1.0
FROM base
ARG VERSION       # need to re-declare after FROM!
RUN echo $VERSION
```

Without re-declare: empty.

## When NOT ENV

For sensitive data: don't ENV.

Better: read at runtime from:
- Mounted file
- Secrets Manager
- Env var passed at run

## When NOT ARG

For values used in many runs: ENV preferred.

For: secrets (use BuildKit secrets).

## Real Example

```dockerfile
# syntax=docker/dockerfile:1.5

ARG BASE_IMAGE=node:20-alpine
ARG APP_VERSION=latest

# Builder
FROM ${BASE_IMAGE} AS builder
ARG APP_VERSION
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build && \
    echo "Version: $APP_VERSION" > /version

# Runtime
FROM gcr.io/distroless/nodejs20-debian12
ARG APP_VERSION
ENV NODE_ENV=production \
    APP_VERSION=$APP_VERSION \
    PORT=8080

COPY --from=builder /app/dist /app
COPY --from=builder /version /version

WORKDIR /app
EXPOSE 8080
CMD ["index.js"]
```

```bash
docker build \
  --build-arg APP_VERSION=$(git rev-parse HEAD) \
  -t myapp .

docker run -e LOG_LEVEL=debug myapp
```

## Quick Refs

```dockerfile
# Build-time
ARG NAME=default
ARG NAME

# Runtime
ENV NAME=value
ENV K1=v1 K2=v2

# Override
docker build --build-arg ARG_NAME=value .
docker run -e ENV_VAR=value IMAGE
```

## Interview Prep

**Junior**: "ARG vs ENV."

**Mid**: "Secrets handling."

**Senior**: "Multi-stage ARG scope."

## Next Topic

→ [T06 — HEALTHCHECK, USER, ENTRYPOINT vs CMD](T06-Healthcheck-User.md)
