# L12/C03/T06 — HEALTHCHECK, USER, ENTRYPOINT vs CMD

## Learning Objectives

- Write robust Dockerfiles
- Apply security defaults

## ENTRYPOINT vs CMD

Both: what to run when container starts.

### ENTRYPOINT
```dockerfile
ENTRYPOINT ["/app"]
```

Always runs; args appended.

### CMD
```dockerfile
CMD ["--port", "8080"]
```

Default args; overridable.

### Combined
```dockerfile
ENTRYPOINT ["/app"]
CMD ["--port", "8080"]
```

`docker run myimage`: runs `/app --port 8080`.
`docker run myimage --debug`: runs `/app --debug` (CMD replaced).

## Exec vs Shell Form

### Exec (preferred)
```dockerfile
ENTRYPOINT ["/app"]
CMD ["--port", "8080"]
```

Direct execve. No shell.

### Shell
```dockerfile
ENTRYPOINT /app
CMD --port 8080
```

`/bin/sh -c "/app"`. Shell intermediary.

Issues:
- PID 1 is sh; signals not forwarded
- Shell expansion / interpolation possible

For containers: use exec form.

## Signal Handling

Exec form:
- App is PID 1
- Receives SIGTERM directly
- Can handle graceful shutdown

Shell form:
- Shell is PID 1
- May not forward signals
- App killed abruptly (SIGKILL after grace)

For graceful: exec.

## tini (init)

```dockerfile
ENTRYPOINT ["tini", "--", "/app"]
```

tini = lightweight init:
- Reaps zombies
- Forwards signals
- For PID 1 best practices

`docker run --init` adds tini implicitly.

## USER

Set user for subsequent commands + runtime.

```dockerfile
RUN useradd -u 1000 -m appuser
USER 1000
COPY --chown=1000:1000 . /app
WORKDIR /app
CMD ["./run.sh"]
```

For: non-root container.

## Why Non-Root

- Defense in depth
- Compromise = limited
- Pod Security Standards require
- Compliance

## Default User

Many images default root:
- alpine
- ubuntu
- Most language images

Distroless `:nonroot` variants use UID 65532:
```dockerfile
FROM gcr.io/distroless/static:nonroot
```

## Non-Root Pattern

```dockerfile
FROM alpine
RUN addgroup -g 1000 appgroup && \
    adduser -D -u 1000 -G appgroup appuser

WORKDIR /app
COPY --chown=appuser:appgroup . .

USER 1000

CMD ["./app"]
```

## Bind to Low Ports

Ports <1024 require root or CAP_NET_BIND_SERVICE.

Solutions:
- Use port >1024 (e.g., 8080)
- Add capability
- Run as root (avoid)

```dockerfile
USER 1000
EXPOSE 8080
CMD ["./app", "--port", "8080"]
```

Map at runtime: `docker run -p 80:8080`.

## HEALTHCHECK

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

Periodic check; Docker marks healthy/unhealthy.

K8s usually overrides via liveness/readiness probes. Don't bother for K8s pods.

For Docker standalone / Swarm: use HEALTHCHECK.

## HEALTHCHECK Options

- `--interval`: between checks (30s default)
- `--timeout`: per check
- `--start-period`: grace before first
- `--retries`: failures before unhealthy

## WORKDIR

```dockerfile
WORKDIR /app
COPY . .
RUN make
```

Sets cwd for subsequent.

Creates dir if missing.

For: cleaner than `cd && command`.

## EXPOSE

```dockerfile
EXPOSE 8080
```

Documentation only. Doesn't actually expose.

Need `-p` at runtime to map.

## LABEL

```dockerfile
LABEL maintainer="me@example.com" \
      version="1.0" \
      org.opencontainers.image.source="https://github.com/me/repo"
```

Metadata; useful for tooling.

OCI standard labels:
- org.opencontainers.image.source
- org.opencontainers.image.version
- org.opencontainers.image.title

## STOPSIGNAL

```dockerfile
STOPSIGNAL SIGTERM
```

Signal sent on `docker stop`. Default SIGTERM.

For: app expects different signal.

## ONBUILD

```dockerfile
ONBUILD COPY . /app
ONBUILD RUN make
```

Triggers on child image build. Rarely useful.

## SHELL

```dockerfile
SHELL ["/bin/bash", "-c"]
RUN echo "hello"
```

Change shell for RUN.

For: bash features in alpine (need install bash).

## VOLUME

```dockerfile
VOLUME ["/data"]
```

Anonymous volume created at that path.

Issues:
- Anonymous; hard to find
- Forces volume; not always wanted

Prefer: mount at runtime.

## COPY vs ADD

### COPY (preferred)
```dockerfile
COPY src/ /app/
```

Just copies files.

### ADD
```dockerfile
ADD https://example.com/file.tar.gz /tmp/
ADD file.tar.gz /tmp/   # auto-extracts
```

URL fetch + auto-extract. Rarely needed; use RUN curl.

For: use COPY 99% of time.

## COPY --chown

```dockerfile
COPY --chown=1000:1000 . /app
```

Set ownership at copy.

For: non-root user.

## --chmod

```dockerfile
COPY --chmod=755 scripts/ /scripts/
```

Set perms at copy.

## RUN Optimization

### Single RUN
```dockerfile
RUN apt-get update && \
    apt-get install -y package && \
    rm -rf /var/lib/apt/lists/*
```

Single layer; cleanup in same.

### Multiple RUNs
```dockerfile
RUN apt-get update
RUN apt-get install -y package
```

Many layers; bigger image.

## Comments

```dockerfile
# This is a comment
FROM alpine

# Comments before instruction
RUN apk add nginx
```

## ENV Multiple

```dockerfile
ENV PORT=8080 \
    LOG_LEVEL=info \
    NODE_ENV=production
```

Single ENV; one layer.

## Best Practices Summary

```dockerfile
# syntax=docker/dockerfile:1.5

FROM alpine:3.18 AS builder
WORKDIR /src
RUN apk add --no-cache build-base
COPY . .
RUN make

FROM alpine:3.18
RUN addgroup -g 1000 app && \
    adduser -D -u 1000 -G app app && \
    apk add --no-cache ca-certificates && \
    rm -rf /var/cache/apk/*

WORKDIR /app
COPY --from=builder --chown=app:app /src/myapp .

USER 1000
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/healthz || exit 1

ENTRYPOINT ["./myapp"]
CMD ["--port", "8080"]
```

## Common Mistakes

- ENTRYPOINT shell form (no signal forwarding)
- Run as root
- No HEALTHCHECK (Docker only)
- Missing USER
- COPY whole dir (no .dockerignore)
- ADD when COPY suffices

## Anti-Patterns

```dockerfile
# BAD
FROM ubuntu
RUN apt-get update
RUN apt-get install -y nginx
ADD . /app
RUN cd /app && make
ENTRYPOINT /app/run.sh
```

Issues:
- Multiple RUN (bigger image)
- Latest base
- ADD when COPY ok
- Shell form ENTRYPOINT
- No USER

## Good Version

```dockerfile
# syntax=docker/dockerfile:1.5
FROM ubuntu:22.04 AS builder
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY . .
RUN make

FROM ubuntu:22.04
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -u 1000 -m app

WORKDIR /app
COPY --from=builder --chown=app:app /src/myapp .

USER 1000
EXPOSE 8080
ENTRYPOINT ["./myapp"]
CMD ["--port", "8080"]
```

## Verify

```bash
# Check user
docker run myapp id
# uid=1000 gid=1000

# Check shell vs exec
docker inspect myapp --format='{{.Config.Cmd}}'

# Check healthcheck
docker inspect myapp --format='{{.Config.Healthcheck}}'

# Test signal
docker run -d --name app myapp
docker stop app   # should be quick + graceful
```

## Quick Refs

```dockerfile
# Identity
USER 1000
WORKDIR /app

# Defaults
ENTRYPOINT ["/app"]
CMD ["--port", "8080"]

# Metadata
LABEL key=value
EXPOSE PORT

# Health (Docker only)
HEALTHCHECK CMD curl ... || exit 1

# Copy with attrs
COPY --chown=USER:GROUP --chmod=MODE src dst

# Signals
STOPSIGNAL SIGTERM
```

## Interview Prep

**Junior**: "ENTRYPOINT vs CMD."

**Mid**: "Non-root container."

**Senior**: "Production Dockerfile pattern."

**Staff**: "Docker security baseline."

## Next Topic

→ Move to [L12/C04 — Image Optimization](../C04/README.md)
