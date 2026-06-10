# L12/C08/T02 — Image Scanning (Trivy, Grype, Snyk)

## Learning Objectives

- Scan images for vulnerabilities
- Integrate in CI

## Why

- Identify CVEs
- License compliance
- Misconfiguration detection
- Supply chain
- Regulatory

## Trivy

Most popular OSS scanner:
```bash
brew install trivy
trivy image nginx:1.27
```

Output:
```
nginx:1.27
========
Total: 12 (HIGH: 5, MEDIUM: 7)

CVE-2024-XXXX: Package: libssl, ...
```

## Grype (Anchore)

```bash
brew install grype
grype nginx:1.27
```

Similar; alternative.

## Trivy Features

- Vulnerabilities (CVE)
- Misconfigurations (IaC)
- Secrets (in image)
- License scanning
- SBOM generation

## Severity Filtering

```bash
trivy image --severity HIGH,CRITICAL nginx:1.27
trivy image --ignore-unfixed nginx:1.27
```

For CI: focus on actionable.

## Output Formats

```bash
trivy image -f json nginx:1.27 > scan.json
trivy image -f sarif nginx:1.27 > scan.sarif
trivy image -f cyclonedx nginx:1.27 > sbom.xml
```

For: tooling integration.

## CI Integration

```yaml
- uses: aquasecurity/trivy-action@master
  with:
    image-ref: myapp:${{ github.sha }}
    format: sarif
    output: trivy.sarif
    severity: HIGH,CRITICAL
    exit-code: '1'
    ignore-unfixed: true

- uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: trivy.sarif
```

Failed PR if HIGH/CRITICAL.

## Trivy Server / Database

Trivy downloads CVE DB on first run. Cache for CI:
```bash
trivy --cache-dir /cache image nginx
```

For: faster CI runs.

## Snyk

Commercial; SaaS + CLI:
```bash
brew install snyk
snyk auth
snyk container test myimage
```

Pros:
- Friendly UI
- Vuln database curated
- Fix suggestions

Cons:
- Paid for org
- Vendor lock

## Anchore

Enterprise platform:
- Image scanning
- Policy
- Compliance
- Reporting

For: large orgs.

## Clair

Quay's scanner (CoreOS originally):
- Used by Quay registry
- API-driven

## Built-In Registry Scanning

### ECR
```bash
aws ecr put-image-scanning-configuration --repository-name myapp \
  --image-scanning-configuration scanOnPush=true
```

Auto-scan on push.

### GHCR
GitHub built-in vulnerability scanning.

### Docker Hub
Scout (paid).

## Scanning Stages

1. Local dev (pre-commit)
2. CI build
3. Registry (on push)
4. Runtime (in cluster; periodic)

Multiple layers.

## Misconfigurations

Trivy scans Dockerfiles:
```bash
trivy config Dockerfile
# Or
trivy fs .
```

Catches:
- USER not set
- HEALTHCHECK missing
- Latest tags
- etc.

## Secrets

```bash
trivy image --scanners secret myimage
```

Detects:
- AWS keys
- API tokens
- Private keys

For: leaked secrets in layers.

## SBOM

```bash
trivy image --format spdx-json myimage > sbom.json
```

Generate SBOM during scan.

## Skip / Ignore

```bash
trivy image --skip-update myimage      # don't download DB
trivy image --skip-files Dockerfile myimage
```

For: speed.

## .trivyignore

```
# Ignore specific CVE
CVE-2024-1234
```

For: known false positives or accepted risk.

## Vulnerability Lifecycle

CVE found:
1. Disclosed (public)
2. Score (CVSS)
3. Affected products
4. Patch released
5. Update images
6. Redeploy

For: stay current.

## Continuous Monitoring

New CVEs disclosed daily. Periodic re-scan:
```yaml
schedule:
- cron: "0 6 * * *"
jobs:
  scan:
    - run: trivy image --severity HIGH,CRITICAL myapp:latest
```

For: catch CVEs that landed since build.

## Policy

For block:
- HIGH/CRITICAL in PR → fail
- Trend over time (increasing = bad)
- Accept known with justification

## Whitelisting

For false positives:
```yaml
# .trivyignore
CVE-2024-XXXX
```

Document why.

## Distroless Advantage

```bash
trivy image gcr.io/distroless/static-debian12
# Very few CVEs (minimal packages)

trivy image ubuntu:22.04
# Many CVEs (lots of packages)
```

Smaller base = fewer CVEs.

## Java Specific

```bash
trivy image --severity HIGH,CRITICAL --vuln-type library myapp
```

Library-specific (Maven, npm, etc.) vulnerabilities.

## Python Specific

```bash
trivy fs requirements.txt
# Or
trivy image --scanners vuln myapp
```

Scans installed pip packages.

## Comparison

| | Trivy | Grype | Snyk | Anchore |
|---|---|---|---|---|
| OSS | Yes | Yes | No | Has OSS |
| Speed | Fast | Fast | API call | Faster (DB) |
| Coverage | Broad | Broad | Strong | Broad |
| Cost | Free | Free | Paid | Paid/free |

For: Trivy default.

## SCAP / Compliance

Trivy supports:
```bash
trivy image --compliance docker-cis myapp
```

Maps findings to compliance frameworks.

For: audit.

## Performance

```bash
trivy image --scanners vuln --quiet --no-progress myapp
```

Just vulns; faster.

## Cluster Scanning

```bash
trivy k8s --report summary cluster
```

Scan all workloads in cluster.

## Best Practices

- Scan in CI (fail on HIGH/CRITICAL)
- Scan in registry (continuous)
- Trivy operator in K8s (cluster)
- Update base images regularly
- Patch policy documented
- Whitelist with justification
- SBOM in artifact

## Common Mistakes

- Skip scan to "save time"
- All severities (noise)
- No re-scan after fix
- No tracking over time
- Whitelist without reason

## Visualization

For findings over time:
- Dashboards (Grafana)
- Defect Dojo
- Bridgecrew Cloud

For: trend analysis.

## Quick Refs

```bash
# Trivy
trivy image IMAGE
trivy image --severity HIGH,CRITICAL --ignore-unfixed IMAGE
trivy image -f json IMAGE
trivy fs DIR
trivy config Dockerfile

# Grype
grype IMAGE

# Snyk
snyk container test IMAGE

# K8s
trivy k8s cluster
```

## Interview Prep

**Junior**: "Why scan."

**Mid**: "Trivy in CI."

**Senior**: "Vuln management."

**Staff**: "Supply chain security."

## Next Topic

→ [T03 — Signed Images (Cosign, Notary v2)](T03-Signed-Images.md)
