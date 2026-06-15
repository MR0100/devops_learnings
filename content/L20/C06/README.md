# L20/C06 — Supply Chain Security

## Topics

- **T01 SLSA Framework** — Supply-chain Levels for Software Artifacts
- **T02 in-toto Attestations** — Verifiable build metadata
- **T03 Dependency Pinning & Reproducible Builds**
- **T04 Lessons from SolarWinds, Codecov, xz Utils** — Real incidents

## Why Supply Chain Now

High-profile incidents made supply chain a board-level concern:
- **SolarWinds (2020)**: build system compromised; signed malware distributed to 18K customers
- **Codecov (2021)**: bash uploader script altered; credentials of thousands exfiltrated
- **Log4Shell (2021)**: vulnerability in popular Java lib; affected enormous footprint
- **xz Utils (2024)**: multi-year social engineering of a sole maintainer; near-miss SSH backdoor

The pattern: trust at one layer (vendor, package, build) abused to compromise many downstream.

## SLSA (Supply-chain Levels for Software Artifacts)

Google-led framework with levels:

### SLSA 1
- Build process scripted (no manual builds)
- Provenance generated (basic)

### SLSA 2
- Hosted build service (no developer laptop builds)
- Signed provenance (link build to source)

### SLSA 3
- Hardened build platform
- Non-falsifiable provenance (signed in trusted context)
- Source-version controlled

### SLSA 4
- Two-party review of changes
- Hermetic builds (no network during build)
- Reproducible builds

Most companies aim for SLSA 2-3.

### GitHub Actions → SLSA 3
GitHub Actions with OIDC + signing reaches SLSA 3 capable. Recipe:
```yaml
permissions:
  id-token: write    # OIDC
  contents: read
  packages: write

steps:
  - uses: actions/checkout@v4
  - run: ./build.sh
  - uses: actions/attest-build-provenance@v1
    with:
      subject-path: 'dist/*'
```

GitHub generates provenance and signs it via Sigstore.

## in-toto

Framework for verifiable build metadata. Each step in pipeline creates an attestation; downstream verifies.

```
Source → [code-review] → [build] → [test] → [publish]
            attest        attest    attest    attest
```

Verifiable at deploy: did all steps run, in order, by authorized parties?

Cosign supports in-toto attestations:
```bash
cosign attest --predicate provenance.json --type slsaprovenance myimage
cosign verify-attestation --type slsaprovenance myimage
```

## Dependency Pinning

### Pin to Versions
```
# Don't
dep@latest
dep@1.x

# Do
dep@1.2.3
dep@1.2.3+sha256:abc...
```

### Pin to Digests
For container images:
```
FROM debian:bookworm-slim@sha256:abc123...
```

For Go modules: `go.sum` does this.

For npm: lockfile (`package-lock.json`) does this.

For Terraform: `.terraform.lock.hcl`.

### Update Mechanism
- Renovate / Dependabot — auto-PRs with version bumps
- Combined with CI tests, safe enough
- Review the PR before merging

### Vendoring
Commit deps into your repo. Extreme but eliminates supply chain risk for committed code.

Trade-off: large repos, slow updates.

## Reproducible Builds

Same source → byte-identical output.

### Why
- Independent rebuild verifies binary matches source
- "Two people built it; bytes match" = high confidence no tamper

### Challenges
- Timestamps embedded
- File ordering
- Build host info

### Tools
- **ko** (Go) — reproducible images
- **kaniko** — in-cluster reproducible builds
- **Nixpkgs** — most reproducible OS ecosystem
- **Buildkit** + `SOURCE_DATE_EPOCH` — best effort

### Verifying
- Build twice (different host, same commit)
- Compare digests
- If different, investigate non-determinism

## Lessons from Real Incidents

### SolarWinds
- Attackers compromised build environment
- Malicious code injected into build at compile time
- Signed by SolarWinds (trusted CA)
- Distributed via routine updates to 18K customers

Lessons:
- Sign artifacts; verify signers
- Multi-party review of build infra changes
- Detect anomalous build behavior
- Network egress monitoring from build machines

### Codecov
- Codecov's bash uploader was altered to exfiltrate env vars
- Anyone who used the uploader uploaded their secrets

Lessons:
- Verify third-party scripts (checksum, signature)
- Limit env exposed to CI scripts (use OIDC, scoped tokens)
- Rotate keys after a vendor compromise notification

### Log4Shell
- Log4j (popular Java logging lib) had RCE via crafted log message
- Affected basically everyone using log4j
- Months of remediation

Lessons:
- SBOM ("where is log4j?")
- Fast patch path for dependencies
- Defense in depth (egress controls would have helped)

### xz Utils
- A maintainer was social-engineered over years
- New maintainer added backdoor to compressed test files
- Caught by accident (microsecond timing anomaly)

Lessons:
- Single maintainer = risk
- OSS maintainer health matters
- Defense in depth (the backdoor still required specific conditions)
- Sponsor critical OSS

## Security Posture Hardening

### Build System
- Ephemeral runners (no persistent state)
- OIDC for cloud auth (no long-lived keys)
- Audit log all builds
- Restrict who can modify CI config

### Repository
- Branch protection (required reviews, status checks)
- Signed commits (Sigstore gitsign)
- CODEOWNERS for sensitive paths
- Audit log

### Dependencies
- Pin everything
- Scan with SCA in CI
- Reachability analysis (don't sweat unused vulns)
- Patch fast (Renovate PRs auto-merged on green)

### Artifacts
- SBOM generated + signed
- Image scanned
- Image signed (Cosign)
- Provenance attached
- Admission policy verifies at deploy

### Runtime
- Falco/Tetragon for anomaly detection
- Network policy (limit lateral movement)
- Egress controls (limit data exfil)

## Interview Themes

- "What is SLSA?"
- "Walk through SLSA 3 for GitHub Actions"
- "Lessons from SolarWinds / xz Utils"
- "Dependency pinning strategy"
- "Defend a build pipeline against supply chain attack"
