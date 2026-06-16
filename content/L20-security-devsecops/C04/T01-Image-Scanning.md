# L20/C04/T01 — Image Scanning Pipelines

## Learning Objectives

- Scan images in CI
- Block bad images

## Why

Container images:
- Base + packages + app
- Vulns anywhere
- Scan all

## Tools

- Trivy (open source)
- Grype (Anchore)
- Snyk Container
- Clair (legacy)
- Twistlock / Prisma
- Aqua Security

## Trivy

```bash
trivy image my-app:v1
trivy image --severity HIGH,CRITICAL --exit-code 1 my-app:v1
```

For: open source standard.

## Grype

```bash
grype my-app:v1
```

Anchore project; fast.

## CI Block

```yaml
- name: Build
  run: docker build -t my-app:${{ github.sha }} .

- name: Scan
  run: |
    trivy image \
      --severity CRITICAL,HIGH \
      --exit-code 1 \
      --ignore-unfixed \
      my-app:${{ github.sha }}
```

`--ignore-unfixed`: skip CVEs without patch.

## Registry Scanning

Cloud registries:
- AWS ECR: Inspector
- Azure ACR: Defender
- GCP GAR: Container Scanning
- Harbor: built-in Trivy

Auto-scan on push.

## Trivy in Harbor

```yaml
# Harbor scans on push
project:
  scanning:
    auto_scan: true
```

## Continuous Scanning

Re-scan old images:
- New CVEs may apply
- Trigger rebuild

For: drift.

## Severity Levels

Trivy:
- UNKNOWN
- LOW
- MEDIUM
- HIGH
- CRITICAL

Filter:
```bash
trivy image --severity HIGH,CRITICAL
```

## Allowlist

```yaml
# .trivyignore
CVE-2023-12345
CVE-2024-67890
```

Document why each.

## SBOM Generation

```bash
trivy image --format cyclonedx > sbom.json
```

Attach to image (cosign).

## Multi-Layer

Image has:
- OS packages (apt, rpm)
- Language packages (npm, pip)
- Custom binaries

Scanner finds all.

## Base Image Choice

Smaller = fewer CVEs:
- distroless
- alpine
- scratch

vs:
- ubuntu (more CVEs surface)
- centos (deprecated)

For: minimize.

## Update Base

```dockerfile
FROM node:20-alpine
```

Periodic refresh:
```bash
docker pull node:20-alpine
docker build --no-cache
```

For: latest patches.

## Vulnerability Lifecycle

CVE published →
- Tool databases update
- Existing images now show vuln
- Re-build needed

For: continuous.

## Multi-Arch

Scan all:
```bash
trivy image --platform linux/amd64 my-app:v1
trivy image --platform linux/arm64 my-app:v1
```

For: ARM + x86.

## Layer-Level

Trivy shows per layer:
- Which layer introduced vuln
- Fix at that layer

For: targeted fix.

## Reports

```bash
trivy image --format json > report.json
trivy image --format table > report.txt
trivy image --format sarif > report.sarif
```

For: integration.

## Best Practices

- Scan in CI (block critical)
- Scan in registry (auto)
- Re-scan periodically
- SBOM generated
- Allowlist with reason
- Minimal base

## Common Mistakes

- One-time scan
- Block on everything (noise)
- No allowlist (drown)
- Large base image
- Skip language packages

## Quick Refs

```bash
# Trivy
trivy image IMAGE
trivy image --severity HIGH,CRITICAL --exit-code 1 IMAGE

# Grype
grype IMAGE

# Snyk
snyk container test IMAGE
```

## Interview Prep

**Junior**: "What does container image scanning find?" — Known CVEs in OS packages and app dependencies inside the image, plus misconfigurations and sometimes embedded secrets, using tools like Trivy or Grype.

**Mid**: "Where in the pipeline should you scan images?" — At build time before push (fail the build on new critical vulns), at registry admission, and continuously on stored images so newly disclosed CVEs against already-built images are caught.

**Senior**: "Why is scanning at build time alone insufficient?" — A vulnerability may be disclosed after the image is built and deployed; without continuous rescanning of the registry and running images, you'd never learn that a passing image is now vulnerable.

**Staff**: "How do you run continuous image scanning at scale without alert fatigue?" — Use minimal/distroless base images to shrink the attack surface, prioritize by fixability and reachability rather than raw CVE count, automate base-image bump PRs, and feed results into a single vuln dashboard with SLAs tied to severity.

## Next Topic

→ [T02 — Image Signing (Cosign / Sigstore)](T02-Image-Signing.md)
