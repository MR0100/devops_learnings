# L20/C06/T04 — Lessons from SolarWinds, Codecov, xz Utils

## Learning Objectives

- Learn from breaches
- Apply lessons

## SolarWinds (2020)

Attack:
- Threat actor (Russian state)
- Compromised SolarWinds build system
- Injected backdoor into Orion update
- 18,000+ orgs received malicious update
- Federal agencies + Fortune 500

## Lessons

### Build System
Critical. Protect.

### Update Path
Trust everything from vendor. Verify.

### Detection
Signed update; not detected for months.

For:
- Audit build infra
- Multiple signers
- Verify provenance

## SLSA Response

SLSA framework largely response:
- L3: hardened builds
- Provenance + verification

## Codecov (2021)

Attack:
- Codecov bash uploader compromised
- Months of malicious code in installer
- Stole env vars (incl. tokens) from CI runs

## Lessons

### Bash Pipe Install
```bash
curl https://codecov.io/bash | bash
```

No verification. Trust.

For:
- Pin to specific commit
- Verify signature
- Don't pipe untrusted

### CI Secrets Exposure
Compromised tool steals secrets.

For:
- OIDC over static keys
- Limit secret scope
- Audit CI tool changes

## xz Utils (2024)

Attack:
- Threat actor (sophisticated; ~years)
- Became maintainer of xz
- Inserted backdoor into liblzma
- Targeted OpenSSH via systemd
- Almost shipped in Debian / Fedora unstable
- Caught by performance regression

## Lessons

### Open Source Burden
Maintainer alone; vulnerable.

For:
- Fund critical infra
- Multiple maintainers
- Suspicious PRs review

### Backdoor in Build
Injected via test files; subtle.

For:
- Review build process
- Reproducible builds
- Audit test infra

### Detection
Caught by:
- Performance regression
- Bigger comm.

For:
- Continuous monitoring
- Performance baselines
- Community vigilance

## Log4Shell (2021)

Vuln in log4j:
- Wildly used
- RCE via log message
- Months of patching

## Lessons

### Transitive Deps
Few use log4j directly; many transitively.

For:
- SBOM
- Continuous SCA
- Patching automation

### Speed of Response
Hours mattered.

For:
- Inventory ready
- Patch process automated
- Communication

## Common Themes

- Build infra critical
- Trust verification weak
- Maintainer burden
- Transitive deps invisible
- Detection slow

## Defenses

### Build
- Hermetic
- Provenance
- Multi-party signing

### Verify
- Cosign
- SLSA verify
- SBOM

### Inventory
- SBOM per artifact
- Dependency-Track
- Continuous

### Update
- Renovate / Dependabot
- Auto-merge patches
- Quick response

### Maintain
- Fund OSS
- Multiple maintainers
- Review suspicious

## Industry Response

- SLSA
- Sigstore
- OpenSSF
- US EO
- EU CRA

For: regulation + tooling.

## Specific Tools

### Sigstore
Free signing for OSS.

### OpenSSF Scorecard
Score repos by security.

### OSV.dev
Open source vulnerabilities.

### Allstar
Auto-enforce best practices.

## Application

For your projects:
- SBOM
- Sign artifacts
- Verify
- Pin deps
- Monitor SCA
- Hermetic builds where possible

## Real Cost

SolarWinds:
- Direct: $40M cleanup
- Plus customer impact
- Reputation damage

For: justify investment.

## Threat Modeling

Per project:
- Where does code come from?
- Where build?
- Where deploy?
- Who can change?

Map; harden.

## Open Source Funding

GitHub Sponsors, Tidelift:
- Fund maintainers
- Reduce burden
- Reduce burn-out

For: ecosystem health.

## Best Practices

- SLSA L2+
- Sigstore everywhere
- Continuous SCA
- SBOM per build
- Audit build infra
- Fund OSS

## Common Mistakes

- Trust signed = trust signer (no verify)
- Skip transitive scan
- One-time SBOM
- Manual patching
- No incident response plan

## Quick Refs

```
Lessons:
- SolarWinds: harden builds
- Codecov: verify installers
- xz: review maintainership
- Log4Shell: SBOM + SCA

Tools:
- Sigstore
- SLSA
- OpenSSF
- OSV
```

## Interview Prep

**Junior**: "Name a major supply-chain attack and what happened." — SolarWinds (2020): attackers compromised the build system and injected a backdoor into signed updates, which then shipped to thousands of customers as legitimately-signed software.

**Mid**: "What was different about the xz Utils incident?" — It was a multi-year social-engineering attack where a malicious actor gained maintainer trust on a low-staffed but widely-depended-on library and slipped a backdoor into release tarballs — highlighting human/maintainer risk, not just technical compromise.

**Senior**: "What concrete lessons come out of SolarWinds, Codecov, and xz?" — Protect and monitor the build system itself (a signature on a compromised build is worthless), verify what's actually in release artifacts vs source (xz's backdoor was only in the tarball), and reduce trust in single maintainers and unreviewed CI uploaders (Codecov's bash uploader exfiltrated creds).

**Staff**: "How do you design an org-wide supply-chain security strategy from these lessons?" — Treat build infrastructure as production: ephemeral isolated builders (SLSA L3), signed provenance and SBOMs verified at admission, pinned/hash-locked dependencies with reproducible builds, transparency logging, and least-privilege CI with no long-lived secrets — so no single compromise (maintainer, CI step, or signing key) silently reaches production.

## Next Topic

→ Move to [L20/C07 — Cloud Security Posture](../C07/README.md)
