# L15/C03/T03 — Hermetic Builds

## Learning Objectives

- Define hermetic build
- Enforce hermeticity

## Hermetic

Build sees only declared inputs:
- No network during build (after fetching deps)
- No host filesystem
- No host env (mostly)
- Sandboxed

For: reproducibility + cache integrity.

## Why

- Cache hit only if inputs identical
- No "works on my machine"
- No network flakiness during build
- Deterministic

## Bazel

Hermetic by default:
- Sandbox per action
- Only inputs visible
- Outputs declared

```python
go_binary(
    name = "myapp",
    srcs = ["main.go"],
    deps = ["@com_github_foo_bar//:lib"],
)
```

Deps fetched once; cached. Build hermetic.

## Nix

Functional builds:
- Each build = function of inputs
- Pure (no side effects)
- Sandboxed

```nix
{ stdenv, fetchurl }:
stdenv.mkDerivation {
  name = "myapp";
  src = fetchurl {
    url = "...";
    sha256 = "...";
  };
}
```

## Docker (Almost)

Builds can be hermetic if:
- Pinned base
- No network (--network=none) in build
- No host mounts (except cache)

```dockerfile
FROM scratch
COPY app /
```

Easier when minimal.

## Anti-Examples

```dockerfile
RUN curl https://github.com/user/repo/releases/latest/download/app -o /app
```

`latest` = non-deterministic. Build today vs tomorrow: different.

```dockerfile
RUN apt-get install -y nginx
```

Without lock: nginx version varies.

## Hermeticity Tools

### Bazel
Sandboxed actions; explicit deps.

### Nix
Whole derivation hermetic.

### Buck2
Bazel-like.

### Docker BuildKit
With `--network=none`: no network during build.

### Pants
Similar to Bazel.

## Pre-Fetch Deps

```bash
# Fetch all deps offline
go mod download
# OR
go mod vendor

# Build hermetic (no network needed)
go build -mod=vendor
```

## CI Sandboxing

GitHub Actions: less hermetic (can `curl` anywhere during build).

For: hermetic CI: use Bazel / Nix / explicit fetch.

## Network Detection

Block:
```bash
# Use unshare to remove network namespace
unshare -n bash -c "make build"
```

If build needs network: fails. Tighten.

## Filesystem Sandbox

```bash
# Build in chroot
chroot /sandbox bash -c "build"
```

Or Docker with limited mounts.

## Bazel Strict Inputs

```python
go_library(
    srcs = ["lib.go"],
    deps = [":other"],
    # No "data" attribute: nothing else accessible
)
```

Missing dep → build error. No hidden inputs.

## Reproducible vs Hermetic

- Reproducible: same output bytes
- Hermetic: explicit inputs

Hermetic helps reproducible. Not synonymous.

## Cost

- Setup: complex
- Onboarding: steep
- Tooling: Bazel/Nix learning

For: scale justifies.

## When Hermetic

- Monorepo
- Large team
- Reproducible builds required
- Supply chain security

## When Not

- Small project
- Tooling overhead > benefit
- Team unfamiliar
- "good enough" with Docker + lock files

## Real Examples

### Google
Blaze (Bazel internal). Hermetic.

### Facebook
Buck → Buck2. Hermetic.

### NixOS
Whole OS hermetic via Nix.

### Most others
Not strictly hermetic; "best effort."

## Practical Approach

For most:
- Lock all deps (lock files, digest pins)
- Pre-fetch in CI
- Pin base images
- No `latest`
- No `:dev` mid-build
- Audit Dockerfile for fetches

Result: ~hermetic without Bazel.

## Cache Implications

Hermetic = cache works:
- Inputs → output (deterministic)
- Same inputs in CI A and B → same cache key → reuse

Non-hermetic: cache flaky.

## Bazel Remote Cache + Hermetic

```bash
bazel build --remote_cache=... //...
```

Cache hit if inputs match. Hermetic = match works.

For: massive CI speedup.

## Hermeticity Levels

```
L0: anything goes
L1: no internet during build
L2: no internet + pinned deps
L3: sandboxed actions
L4: fully reproducible across machines
```

## Anti-Patterns

### Pulling at Build
```dockerfile
RUN wget ... # bad
```

### Dynamic Tags
```dockerfile
FROM alpine:latest # bad
```

### Host Mounts
```bash
docker build --mount=type=bind,source=/etc/secret,...  # bad
```

### Host Env Leaks
Sensitive HOME paths in artifact.

## Verify Hermetic

```bash
# Clean machine
git clone repo
build > out1

# Different clean machine
git clone repo
build > out2

# Compare
sha256sum out1 out2
```

Match = hermetic + reproducible.

## CI for Hermeticity

```yaml
- name: Build hermetically
  run: |
    docker run --rm --network=none \
      -v $(pwd):/src \
      builder:latest \
      build
```

For: enforce no network.

## Best Practices

- Pin deps, base images
- Pre-fetch in CI
- Bazel / Nix for strict
- Test build with no internet
- Verify reproducibility
- Audit Dockerfile

## Common Mistakes

- `latest` tags
- `apt install` without version
- Network during build
- Host env in build
- Untested reproducibility

## Quick Refs

```bash
# Bazel
bazel build //...

# Nix
nix-build / nix build

# Test hermetic
unshare -n make build
# or
docker run --network=none ...
```

## Interview Prep

**Mid**: "Hermetic build."

**Senior**: "Achieve hermetic."

**Staff**: "Supply chain via hermetic."

## Next Topic

→ Move to [L15/C04 — Testing in Pipelines](../C04/README.md)
