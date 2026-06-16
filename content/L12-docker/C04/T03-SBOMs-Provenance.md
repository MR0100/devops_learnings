# L12/C04/T03 — SBOMs & Provenance

## Learning Objectives

- Generate SBOMs
- Attach provenance

## SBOM

Software Bill of Materials. Inventory of components in image.

For:
- Vulnerability tracking
- License compliance
- Supply chain transparency
- Regulatory (US Executive Order 14028)

## Formats

- **SPDX**: ISO standard
- **CycloneDX**: OWASP
- **Syft JSON**: native

Tooling supports multiple.

## Generate SBOM

### Syft (Anchore)
```bash
brew install syft
syft myimage -o spdx-json > sbom.json
syft myimage -o cyclonedx-json > sbom.cyclonedx.json
syft myimage -o table
```

### Trivy
```bash
trivy image --format spdx-json -o sbom.json myimage
```

### Docker
```bash
docker buildx build --sbom=true -t myimage --push .
```

Attaches SBOM during build.

## Inspect SBOM

```bash
syft myimage
# Shows packages, versions, licenses

cat sbom.json | jq '.packages[] | {name, versionInfo, licenseConcluded}'
```

## Vulnerability Scan with SBOM

```bash
# Grype
grype sbom:sbom.json

# Trivy
trivy sbom sbom.json
```

For: scan without re-fetching image.

## SBOM Components

For each package:
- Name
- Version
- License
- Origin (PyPI, npm, OS)
- Hash
- File paths
- Relationships

## Provenance

Where + how was image built?
- Builder identity
- Source repo + commit
- Build script
- Materials used
- Build timestamp

For: audit + verification.

## SLSA Provenance

Format for build provenance:
```json
{
  "buildType": "https://github.com/Attestations/GitHubActionsWorkflow@v1",
  "builder": {
    "id": "https://github.com/actions/runner"
  },
  "invocation": {
    "configSource": {
      "uri": "git+https://github.com/me/repo@refs/heads/main",
      "digest": {"sha1": "abc..."}
    }
  },
  "materials": [
    {
      "uri": "git+https://github.com/me/repo",
      "digest": {"sha1": "abc..."}
    }
  ]
}
```

For: verify provenance.

## Generate Provenance

### BuildKit
```bash
docker buildx build --provenance=mode=max -t myapp --push .
```

mode=min: minimal info.
mode=max: full info (source, materials, etc.).

### GitHub Actions
```yaml
- uses: docker/build-push-action@v5
  with:
    provenance: mode=max
    sbom: true
```

Auto-attaches.

## Cosign Attestations

```bash
# Sign + attest SBOM
cosign attest --predicate sbom.json --type spdx myimage

# Sign + attest provenance
cosign attest --predicate provenance.json --type slsaprovenance myimage
```

## Verify Attestations

```bash
cosign verify-attestation \
  --type spdx \
  --certificate-identity-regexp '.*github.com/me/.*' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  myimage
```

For: CI / admission controller.

## Sigstore

Keyless signing infrastructure:
- Fulcio: short-lived certs
- Rekor: transparency log
- Cosign: client

For: signing without key management.

## Image Signing

```bash
# Sign
cosign sign myimage

# Keyless (uses OIDC)
COSIGN_EXPERIMENTAL=1 cosign sign myimage

# Verify
cosign verify --certificate-identity-regexp '.*' --certificate-oidc-issuer URL myimage
```

## In-Cluster Verification

For K8s:
- Sigstore Policy Controller
- Kyverno verifyImages

```yaml
# Kyverno
- name: verify-images
  match: ...
  verifyImages:
  - imageReferences: ["myregistry/*"]
    attestors:
    - entries:
      - keyless:
          subject: 'https://github.com/me/.*'
          issuer: 'https://token.actions.githubusercontent.com'
```

Block unsigned.

## Vulnerability Management

Workflow:
1. Build image
2. Generate SBOM (attach)
3. Scan SBOM for CVEs
4. Block if HIGH/CRITICAL
5. Deploy
6. Continuous scan (new CVEs against existing SBOM)

For: stay ahead of disclosures.

## SBOM Diff

```bash
syft diff sbom-old.json sbom-new.json
```

What changed between builds. Audit.

## License Compliance

```bash
syft myimage -o spdx-json | jq '[.packages[].licenseConcluded] | unique'
```

List all licenses. Check against policy.

## Tools

- **Syft**: SBOM generation
- **Grype**: vuln scan
- **Trivy**: scan + SBOM
- **Cosign**: signing + attest
- **Rekor**: transparency log
- **Kyverno**: policy
- **Sigstore Policy Controller**: K8s admission

## SLSA Levels

| Level | What |
|---|---|
| 0 | Nothing |
| 1 | Build script + provenance |
| 2 | Hosted build + signed provenance |
| 3 | Hardened build + isolated |
| 4 | Hermetic + reproducible |

For: most prod aim L2-L3.

## L3 Setup

- Hosted build (GitHub Actions / GitLab CI)
- OIDC for signing (no static keys)
- Provenance generated
- Signed with Sigstore
- Verified at deploy

## Continuous Monitoring

SBOM stored in:
- Registry (as attestation)
- Database (for queries)
- SIEM (for monitoring)

For: when new CVE disclosed, find affected images.

## Trivy DB

Scans against:
- NVD
- Distro security advisories
- Language ecosystem advisories
- GHSA

Updated continuously.

## CycloneDX vs SPDX

| | CycloneDX | SPDX |
|---|---|---|
| Origin | OWASP | Linux Foundation |
| Focus | Supply chain | Licensing |
| Maturity | Rising | Mature |

Both work; tooling supports.

## Image Updates

For ongoing CVE management:
- Periodic rebuild (catch base CVEs)
- Auto-PR on CVE (Dependabot)
- Block on findings (CI policy)

For: stay current.

## Real-World Pipeline

```yaml
# .github/workflows/build.yml
- uses: docker/build-push-action@v5
  with:
    push: true
    tags: myimage:${{ github.sha }}
    provenance: mode=max
    sbom: true

- uses: aquasecurity/trivy-action@master
  with:
    image-ref: myimage:${{ github.sha }}
    format: sarif
    output: trivy.sarif
    severity: HIGH,CRITICAL
    exit-code: '1'

- uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: trivy.sarif

- name: Sign
  run: cosign sign --yes myimage:${{ github.sha }}

- name: Attest SBOM
  run: |
    docker buildx imagetools inspect myimage:${{ github.sha }} --format '{{json .SBOM}}' > sbom.json
    cosign attest --predicate sbom.json --type spdx myimage:${{ github.sha }}
```

Build + scan + sign + attest. Production-grade.

## Best Practices

- SBOM for every image
- Sign every image
- Provenance attached
- Verify at deploy (K8s policy)
- Continuous scan
- License compliance checks
- Audit log of signers

## Common Mistakes

- SBOM not generated
- Signing optional (not enforced)
- No verification at deploy
- Stale SBOMs (new CVEs missed)
- License violations

## Audit

For audit:
- All prod images signed
- SBOMs available
- Provenance verifiable
- Vuln scans regular
- Reports retained

## SBOM Standards (US)

Executive Order 14028:
- Federal vendors must provide SBOM
- For: critical software
- Format: SPDX, CycloneDX, SWID

For sales to US fed: SBOM required.

## Quick Refs

```bash
# SBOM
syft myimage -o spdx-json > sbom.json
trivy image --format spdx-json myimage

# Vuln scan
grype sbom:sbom.json
trivy sbom sbom.json

# Sign
cosign sign myimage

# Attest
cosign attest --predicate file.json --type X myimage

# Verify
cosign verify-attestation --type X myimage
```

## Interview Prep

**Mid**: "What is SBOM."

**Senior**: "SLSA levels."

**Staff**: "Supply chain security program."

## Next Topic

→ Move to [L12/C05 — Container Networking](../C05/README.md)
