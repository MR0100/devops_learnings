# L15/C05/T03 — SBOM Generation

## Learning Objectives

- Generate SBOMs
- Use for supply chain

## SBOM

Software Bill of Materials:
- Components in artifact
- Versions
- Licenses
- Sources

For: supply chain security, vulnerability management.

## Formats

### SPDX
ISO standard:
```json
{
  "spdxVersion": "SPDX-2.3",
  "packages": [
    {
      "name": "nginx",
      "version": "1.27.0",
      "downloadLocation": "https://nginx.org/...",
      "licenseConcluded": "BSD-2-Clause"
    }
  ]
}
```

### CycloneDX
OWASP:
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "components": [
    {
      "name": "nginx",
      "version": "1.27.0",
      "licenses": [{ "license": { "id": "BSD-2-Clause" } }]
    }
  ]
}
```

Both: tooling rich.

## Tools

### Syft
```bash
syft myapp:v1 -o cyclonedx-json
syft myapp:v1 -o spdx-json
```

Scans:
- Files (filesystem)
- Containers
- Archives

Detects:
- OS packages (apt, rpm, apk)
- Language packages (npm, pip, go, etc.)

### Trivy
```bash
trivy image --format cyclonedx myapp:v1 > sbom.json
```

Multi-purpose.

### Anchore
Enterprise; commercial.

### CycloneDX CLI
```bash
cyclonedx-py -o bom.json
```

Per-language tools.

## Generate in CI

```yaml
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    image: registry/myapp:${{ github.sha }}
    format: cyclonedx-json
    output-file: sbom.json
    upload-artifact: true
```

## Attach to Image

```bash
cosign attest --predicate sbom.json myapp:v1
```

SBOM signed + attached as attestation.

Retrieve:
```bash
cosign verify-attestation myapp:v1 > attestation.json
```

## Why SBOM

### Vulnerability Management
Log4Shell, etc.:
- Search SBOMs for `log4j-core` < 2.17.1
- Find all affected
- Patch / mitigate fast

### License Compliance
GPL in artifact? Audit.

### Supply Chain
Know what's in artifact.

### Regulatory
EU Cyber Resilience Act, US Executive Order: require SBOMs.

## Storage

- In artifact registry (alongside image)
- Dedicated SBOM repo (Dependency-Track)
- Internal DB

## Dependency-Track

Open-source SBOM platform:
```bash
docker run -p 8080:8080 dependencytrack/apiserver
```

Upload SBOMs; tracks vulnerabilities.

For: continuous CVE monitoring.

## Grype + SBOM

```bash
grype sbom:sbom.json
```

Scan SBOM for vulns; no need to re-scan image.

For: fast vulnerability checks.

## SBOM at Each Stage

```
Source → SBOM (deps)
Build → SBOM (deps + buildtime)
Image → SBOM (full)
```

Track through pipeline.

## SCA Difference

SCA: scan deps for vulns.
SBOM: list deps.

SBOM is a deliverable; SCA is a process.

## OSS Compliance

License obligations:
- MIT: include notice
- Apache 2.0: include notice
- GPL: source if distributed
- ...

SBOM helps audit.

Tools:
- FOSSA
- Snyk License
- ScanCode

## SLSA Provenance

SBOM + provenance = supply chain attestation:
- What's in artifact
- How built
- By whom

```bash
# GitHub-managed
- uses: actions/attest-build-provenance@v1
  with:
    subject-path: 'dist/*.tar.gz'
```

## Container SBOM Best Practice

```yaml
- name: Build image
  run: docker build -t myapp:${{ github.sha }} .

- name: SBOM
  run: syft myapp:${{ github.sha }} -o spdx-json > sbom.spdx.json

- name: Sign SBOM
  run: cosign attest --predicate sbom.spdx.json myapp:${{ github.sha }}

- name: Scan SBOM
  run: grype sbom:sbom.spdx.json --fail-on critical
```

## Per-Lang SBOMs

### Go
```bash
cyclonedx-gomod app -output bom.json
```

### npm
```bash
npm sbom --sbom-format=cyclonedx
```

### Python
```bash
cyclonedx-py -o bom.json
```

### Maven
```bash
mvn org.cyclonedx:cyclonedx-maven-plugin:makeBom
```

## Aggregate

Multiple SBOMs → combined:
- Service A SBOM
- Service B SBOM
- Aggregate per release

For: org-wide view.

## Dependency Graph

GitHub Insights:
- Detects deps
- Vulnerability alerts
- Graph view

For: visualization.

## Limitations

SBOM:
- Static (build-time)
- Doesn't cover runtime
- Doesn't cover internal libs (unless declared)

For: complement with SCA + runtime tools.

## SBOM Verification

```bash
# Cosign attestation
cosign verify-attestation \
  --type cyclonedx \
  myapp:v1
```

For: integrity check.

## Cost

Free tools:
- Syft, Trivy, Grype: open
- Generate in CI: cheap

Commercial:
- Dependency-Track: free
- Snyk, Mend: paid
- Anchore Enterprise: paid

## Real Examples

### Linux Foundation
SPDX standard.

### CISA
SBOM mandate for federal.

### Many companies
SBOM-required by customers (security questionnaires).

## Best Practices

- SBOM per build
- CycloneDX or SPDX
- Signed (cosign attest)
- Stored centrally
- Scanned continuously
- Updated on rebuild

## Common Mistakes

- One-time SBOM (stale)
- No signing (tamper)
- No scanning (passive)
- Manual generation (drift)
- Incomplete (skip OS packages)

## Quick Refs

```bash
# Generate
syft IMAGE -o cyclonedx-json
trivy image --format cyclonedx IMAGE

# Attest
cosign attest --predicate sbom.json IMAGE

# Verify
cosign verify-attestation IMAGE

# Scan SBOM
grype sbom:sbom.json
```

## Interview Prep

**Mid**: "What's SBOM."

**Senior**: "SBOM workflow."

**Staff**: "Supply chain at scale."

## Next Topic

→ Move to [L15/C06 — Deployment Strategies](../C06/README.md)
