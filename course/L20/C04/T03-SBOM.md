# L20/C04/T03 — SBOM (CycloneDX, SPDX)

## Learning Objectives

- Generate SBOMs
- Use for tracking

(See also L15/C05/T03 — comprehensive SBOM coverage.)

## SBOM Recap

Software Bill of Materials:
- Components
- Versions
- Licenses

## Formats

### CycloneDX (OWASP)
JSON:
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "components": [...]
}
```

### SPDX (ISO)
JSON or text:
```json
{
  "spdxVersion": "SPDX-2.3",
  "packages": [...]
}
```

Both: standard.

## Tools

- Syft (Anchore): generate
- Trivy: generate + scan
- CycloneDX CLI: language-specific
- SPDX tools

## Generate

```bash
syft my-app:v1 -o cyclonedx-json
trivy image my-app:v1 --format cyclonedx > sbom.json
```

## In CI

```yaml
- uses: anchore/sbom-action@v0
  with:
    image: registry/my-app:${{ github.sha }}
    format: cyclonedx-json
    output-file: sbom.json

- uses: actions/upload-artifact@v4
  with:
    name: sbom
    path: sbom.json
```

## Attach to Image

```bash
cosign attest --predicate sbom.json --type cyclonedx my-app:v1
```

## Vulnerability Lookup

```bash
grype sbom:sbom.json
```

Scan SBOM offline.

## Dependency-Track

Platform:
```bash
docker run -p 8080:8080 dependencytrack/apiserver
```

Upload SBOMs; track CVEs over time.

## EU CRA / US EO

Regulation:
- SBOMs required
- Vulnerability disclosure
- Patch obligations

For: compliance.

## License Tracking

CycloneDX includes:
```json
"licenses": [{ "license": { "id": "Apache-2.0" } }]
```

Audit:
- GPL: review
- MIT: allowed
- AGPL: caution

## SBOM at Each Stage

```
Source SBOM (deps)
Build SBOM (deps + tools)
Image SBOM (full)
Runtime SBOM (loaded libs)
```

For: track through.

## Consumer Use

Customer asks:
"Are you affected by Log4Shell?"

Search SBOMs:
```bash
grep "log4j-core" sboms/*.json
```

Quick answer.

## SBOM Storage

- Per image (attestation)
- Dependency-Track
- Internal DB
- Customer-facing portal

## Compose Org-Wide

Aggregate:
- All services
- Composite SBOM
- Single dependency view

For: org-wide.

## Update on Rebuild

Every build → new SBOM.
Versioned.

For: track changes.

## Best Practices

- SBOM per build
- Format: CycloneDX or SPDX
- Signed (cosign attest)
- Stored centrally
- Continuous scan
- License audit

## Common Mistakes

- One-time SBOM
- No scanning of SBOM
- Manual generation
- Skip language packages

## Quick Refs

```bash
# Generate
syft IMAGE -o cyclonedx-json
trivy image --format cyclonedx IMAGE

# Attest
cosign attest --predicate sbom.json IMAGE

# Scan
grype sbom:sbom.json

# Platform
Dependency-Track
```

## Interview Prep

**Mid**: "SBOM."

**Senior**: "SBOM workflow."

**Staff**: "Supply chain inventory."

## Next Topic

→ [T04 — Admission Controllers](T04-Admission-Controllers.md)
