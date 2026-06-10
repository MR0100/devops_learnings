# L15/C03/T02 — Reproducible Builds

## Learning Objectives

- Achieve reproducibility
- Verify

## Reproducible Build

Same inputs → bit-identical output, anywhere, anytime.

## Why

- Verify: rebuild from source; match published.
- Supply chain: detect tampering.
- Cache: hashes match.
- Compliance: prove build provenance.

## Common Non-Determinism

- Timestamps
- Random IDs / GUIDs
- File order (filesystem dependent)
- Build dir paths
- Locale
- Network state
- Hostname / build machine info

## Mitigations

### SOURCE_DATE_EPOCH
```bash
SOURCE_DATE_EPOCH=$(git log -1 --format=%ct) go build
```

Build tools respect this for timestamps.

### Stable Sort
```bash
ls | sort
find . -print0 | sort -z
```

Avoid filesystem order.

### Strip Build Paths
```bash
go build -trimpath
```

Replace /home/me/build with `_`.

### Strip Random
```bash
# Disable per-build IDs
```

### Reproducible Containers
```dockerfile
FROM debian:bullseye-slim@sha256:...   # pin
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends ...
```

## Tools

### diffoscope
Compare two builds:
```bash
diffoscope build1.tar.gz build2.tar.gz
```

Shows differences.

### Nix
Functional package manager. Builds derived from inputs; reproducible by design.

### Bazel
Hermetic if rules done right.

### Docker buildx with provenance
SLSA-level provenance.

## SLSA Levels

Supply-chain Levels for Software Artifacts:
- L1: documented
- L2: hosted build
- L3: hermetic, provenance
- L4: two-person review

For: supply chain security.

## Go Specific

Go ~deterministic out-of-box:
- No timestamps in binaries (mostly)
- `-trimpath`: remove paths
- `-buildvcs=false`: skip git info

Result: same bytes.

## Rust

```bash
RUSTFLAGS="--remap-path-prefix=$(pwd)=." cargo build
```

For: build paths replaced.

## Java

`reproducible` Maven plugin:
- Strip timestamps in JARs
- Sort entries

## JavaScript

Harder:
- npm: deterministic with lockfile (mostly)
- Webpack: deterministic mode

## Containers

Tools:
- BuildKit: built-in features
- Kaniko: deterministic
- buildah: similar

Pin everything:
- Base image digest (sha256)
- Package versions
- Build args

```dockerfile
FROM debian@sha256:abc123...
RUN apt-get install -y nginx=1.27.0-1~bullseye
```

## Verify

```bash
# Build twice, compare
sha256sum build1.tar.gz build2.tar.gz
```

Same hash = reproducible.

For: regression test.

## In CI

```yaml
- name: Reproducible build check
  run: |
    build > out1.bin
    sleep 60
    build > out2.bin
    diff out1.bin out2.bin
```

For: CI gate.

## Supply Chain Attacks

Reproducibility helps detect:
- Compromised build server (output differs)
- Tampered dependencies (hash mismatch)
- Insider attacks

## Reproducible Container vs Reproducible App

Container reproducibility: layers + tar consistency.
App reproducibility: binary bytes.

Both desirable.

## Image Pinning by Digest

```yaml
image: nginx@sha256:abc123def456...
```

Tag can change; digest can't.

For: prod manifests.

## Lock Files

```
Go: go.sum
JS: package-lock.json
Python: pip-tools, poetry.lock
Rust: Cargo.lock
Ruby: Gemfile.lock
```

Commit. Required for reproducibility.

## Vendoring

```
go mod vendor
npm pack-and-vendor (not standard; tools exist)
```

Build offline; no network for deps.

For: reproducibility without registry access.

## Reproducibility Tier

```
T1: Same machine, same time = same bytes
T2: Same machine, anytime = same bytes
T3: Any machine, anytime = same bytes (true reproducible)
```

T3: ideal.

## Achievability

- Go: T3 achievable
- Rust: T3 with effort
- JS: hard (npm, transitive)
- Containers: hard (base images change)

For: get close, not perfect, often fine.

## Provenance

Record what was built, how, by who:
```yaml
provenance:
  builder: github-actions
  workflow: .github/workflows/build.yml
  run-id: 12345
  source-commit: abc123
  inputs:
    - go-mod-hash: ...
```

For: traceability.

## SLSA Provenance

```bash
docker buildx build --attest type=provenance ...
```

Image signed with build metadata.

## Best Practices

- Pin deps (lock files, digest)
- SOURCE_DATE_EPOCH
- Strip build paths
- Use Bazel / Nix for hermetic
- Verify via diff
- SLSA provenance

## Common Mistakes

- :latest tags
- No lock files
- Build machine timestamps leak
- Random salts in code
- No verification

## Quick Refs

```bash
# Go
go build -trimpath -ldflags="-s -w"

# Docker
docker buildx build --no-cache --pull --attest provenance

# Diff
diffoscope build1 build2

# Verify
sha256sum *.bin
```

## Interview Prep

**Mid**: "Reproducible build."

**Senior**: "How to achieve."

**Staff**: "Supply chain + reproducibility."

## Next Topic

→ [T03 — Hermetic Builds](T03-Hermetic-Builds.md)
