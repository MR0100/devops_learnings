# L20/C03/T04 — Software Composition Analysis (SCA)

## Learning Objectives

- Scan dependencies
- Manage vulnerabilities

## SCA

Scan dependencies (libs, packages) for:
- Known CVEs
- License issues
- Outdated versions

For: supply chain.

## Why

Apps use:
- 90%+ third-party code
- One vuln = whole app
- Log4Shell taught everyone

## Tools

- Dependabot (GitHub; free)
- Renovate (open source; rich)
- Snyk (commercial + free)
- Mend (formerly WhiteSource)
- Trivy (open source)
- OWASP Dependency-Check
- Black Duck (Synopsys)
- FOSSA (license)

## Dependabot

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
```

Auto-PRs to update.

## Renovate

```json
// renovate.json
{
  "extends": ["config:base"],
  "automerge": true,
  "automergeType": "pr",
  "platformAutomerge": true,
  "labels": ["dependencies"],
  "schedule": ["before 5am on monday"]
}
```

More flexible than Dependabot.

## Snyk

```bash
snyk test --severity-threshold=high
snyk monitor
```

CI:
```yaml
- uses: snyk/actions/python@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

## Trivy

```bash
# Container
trivy image my-app:v1

# Filesystem
trivy fs .

# Repo
trivy repo .

# SBOM
trivy image --format cyclonedx my-app:v1 > sbom.json
```

For: free, comprehensive.

## OWASP Dependency-Check

```bash
dependency-check --scan . --format HTML
```

For: NIST NVD-based.

## CVE Database

NVD: National Vulnerability Database.
- All public CVEs
- Severity (CVSS)
- Patches

Tools query NVD.

## CVSS

Common Vulnerability Scoring System:
- 0.0-10.0
- Critical: 9.0-10.0
- High: 7.0-8.9
- Medium: 4.0-6.9
- Low: 0.1-3.9

## Severity Policy

Block:
- CRITICAL (CVSS ≥ 9)
- HIGH (≥ 7) for prod

Warn:
- MEDIUM

Track:
- LOW

## Allowlist (Ignore)

```yaml
# .snyk
ignore:
  CVE-2023-12345:
    - '*':
        reason: Not exploitable in our use case
        expires: 2026-12-31
```

Document why; expires.

## License Scanning

Some licenses incompatible:
- GPL: must release source
- AGPL: cloud problematic
- MIT, Apache 2.0: permissive

FOSSA / Snyk License:
- Detect
- Allowlist
- Block

## Update Strategy

- Daily: dependabot PRs
- Auto-merge patches
- Manual review minors
- Major: planned

For: stay current without churn.

## Auto-Merge Risk

Auto-merge:
- Safe for patches (1.2.3 → 1.2.4)
- Risky for minor (1.2 → 1.3)
- Never major (1.x → 2.x)

For: tests must pass.

## SBOM (See L15/C05/T03)

SBOM + SCA:
- Inventory + scan
- Continuous

## Continuous Monitoring

Old artifact still in use? Scan it.

For: drift.

## Container SCA

Image:
- Base image (e.g. nginx)
- Installed packages
- App deps

Scan all layers.

```bash
trivy image my-app:v1
```

## Transitive Deps

`A → B → C`

If C has CVE, A affected.

Scanners follow tree.

## Effective Strategy

```
Daily:
- Dependabot PRs for patch
- Auto-merge if tests pass

Weekly:
- Review minor updates
- Quarterly: major plan

Continuous:
- Trivy in CI (block critical)
- Snyk monitor
- SBOM generated
```

## False Positives

Some CVEs:
- Not exploitable
- Out of scope
- Mitigated elsewhere

Allowlist with reason + expire.

## Best Practices

- Daily updates
- Block critical in CI
- SBOM published
- License compliance
- Allowlist with reason

## Common Mistakes

- Manual update only (stale)
- Auto-merge major (breaks)
- No allowlist (drown)
- Skip transitives

## Cost

- Dependabot: free
- Renovate: free
- Trivy: free
- Snyk: free + paid
- FOSSA: paid

## Quick Refs

```bash
# Trivy
trivy image / fs / repo

# Snyk
snyk test / monitor / code

# Dependabot
.github/dependabot.yml

# Renovate
renovate.json
```

## Interview Prep

**Junior**: "What is SCA?" — Software Composition Analysis inventories your open-source dependencies (direct and transitive) and flags known vulnerabilities and license risks in them.

**Mid**: "Why do transitive dependencies matter so much in SCA?" — Most of your dependency tree is pulled in indirectly, so a CVE in a deep transitive package (like Log4Shell) can be exploitable even though you never imported it directly — SCA has to walk the full graph.

**Senior**: "How do you prioritize SCA findings without drowning teams in CVEs?" — Filter by reachability (is the vulnerable code path actually called) and exploitability/severity, prioritize fixes that have an available non-breaking upgrade, and auto-open dependency-bump PRs so remediation is low-friction.

**Staff**: "How does SCA fit a broader supply-chain security program?" — Pair it with SBOM generation for inventory, lockfile pinning and reproducible builds for integrity, and provenance/signature verification at deploy — SCA tells you what you depend on and what's vulnerable, while SLSA/signing tell you the artifact wasn't tampered with.

## Next Topic

→ Move to [L20/C04 — Container & Image Security](../C04/README.md)
