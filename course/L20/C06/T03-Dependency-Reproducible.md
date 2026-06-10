# L20/C06/T03 — Dependency Pinning & Reproducible Builds

## Learning Objectives

- Pin dependencies
- Achieve reproducible builds

## Why Pin

Without:
- npm install pulls latest
- "Works on my machine"
- Supply chain attack risk

With:
- Same deps every build
- Predictable
- Auditable

## Lock Files

- `package-lock.json` (npm)
- `yarn.lock` (yarn)
- `pnpm-lock.yaml`
- `go.sum` (Go)
- `Pipfile.lock` (Python)
- `Cargo.lock` (Rust)
- `Gemfile.lock` (Ruby)
- `composer.lock` (PHP)

Commit. Required.

## Hash Pinning

Even better:
```
nginx@sha256:abc123...
```

Tag can change; digest can't.

For: containers, image base.

## Dependency Audit

```bash
npm audit
go mod verify
pip-audit
cargo audit
```

Check for known issues.

## Reproducible Builds

Same inputs → same output bytes.

For: verify integrity.

(See L15/C03/T02.)

## Hermetic

Builds:
- No network during build (after fetch)
- No host env
- Sandboxed

(See L15/C03/T03.)

## Verifying Reproducibility

```bash
# Build twice
docker build -t v1 .
docker build -t v2 .

# Compare
docker image inspect v1 --format='{{.Id}}'
docker image inspect v2 --format='{{.Id}}'
```

Same hash = reproducible.

## SBOM at Build

Generate; verify dependencies:
```bash
syft my-image -o cyclonedx > sbom.json
```

(See L15/C05/T03.)

## Bazel / Nix

Hermetic builds:
- Sandbox each action
- Cache deterministic
- Reproducible by design

For: highest assurance.

## Anti-Patterns

### Floating Versions
```json
"react": "^18.0.0"
```

Pulls 18.x.y. Variable.

```json
"react": "18.2.0"
```

Pin specific.

### :latest Tags
```dockerfile
FROM nginx:latest
```

Different each build.

```dockerfile
FROM nginx@sha256:abc...
```

Pin digest.

### Curl from Web in Dockerfile
```dockerfile
RUN curl https://example.com/install.sh | bash
```

Unverified. Avoid.

## Renovate

Auto-update lock files:
```json
{
  "extends": ["config:base"],
  "rangeStrategy": "pin"
}
```

For: managed updates.

## Dependabot

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    versioning-strategy: "increase"  # exact pinning
```

## In CI

```yaml
- run: npm ci   # uses lockfile exactly
# NOT: npm install (may modify lockfile)
```

For: reproducibility.

## Workspaces / Monorepo

Lockfile at root:
```
my-monorepo/
  package-lock.json
  service-a/
  service-b/
```

Shared deps.

## Private Registry

```
.npmrc:
@myorg:registry=https://my-registry/
```

Org-controlled.

Prevent:
- Typosquatting
- Malicious updates

## Mirror

Mirror public to private:
- npm
- PyPI
- Docker Hub

Audit + cache.

## Vendoring

```bash
go mod vendor
```

Copies deps into repo. Build offline.

For: reproducibility.

## Best Practices

- Lock files committed
- Pin to digest where possible
- Hermetic builds (Bazel/Nix)
- Verify with diff
- SBOM at each build
- Mirror critical deps

## Common Mistakes

- ^ or ~ in package.json
- :latest tags
- No lockfile
- npm install vs npm ci
- Curl from web

## Quick Refs

```bash
# Verify
md5sum binary
sha256sum binary

# Tools
nix-build
bazel build
diffoscope build1 build2

# SBOM
syft / trivy --format cyclonedx
```

## Interview Prep

**Mid**: "Pin deps."

**Senior**: "Reproducible builds."

**Staff**: "Supply chain integrity."

## Next Topic

→ [T04 — Lessons from SolarWinds, Codecov, xz Utils](T04-Supply-Chain-Lessons.md)
