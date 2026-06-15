# L20/C03 — Application Security Testing

## Topics

- **T01 SAST** — Static analysis
- **T02 DAST** — Dynamic / running app testing
- **T03 IAST & RASP** — Hybrid runtime
- **T04 SCA** — Software composition analysis

## SAST (Static Application Security Testing)

Analyze source code without running it.

### Tools
- **Semgrep** (OSS + commercial) — pattern-based; fast; multi-language
- **CodeQL** (GitHub) — semantic analysis; deep
- **SonarQube** — quality + security
- **Checkmarx**, **Veracode** — enterprise
- **Bandit** (Python), **gosec** (Go) — language-specific

### Strengths
- Fast (CI-friendly)
- Catches known patterns early
- Language-aware (variable flow, taint analysis)

### Limitations
- False positives
- Misses runtime issues (config, dependencies)
- Can be noisy without tuning

### Semgrep Example
```yaml
rules:
  - id: hardcoded-jwt-secret
    pattern: |
      jwt.encode($DATA, "$SECRET", ...)
    message: Hardcoded JWT secret
    languages: [python]
    severity: ERROR
```

Run:
```bash
semgrep --config auto .
semgrep --config rules/ .
```

## DAST (Dynamic Application Security Testing)

Run against a deployed app; probe for vulnerabilities.

### Tools
- **OWASP ZAP** (OSS) — proxy + scanner
- **Burp Suite** (commercial) — pen-test workbench
- **Nessus** (commercial) — infrastructure scanner
- **Nuclei** (OSS) — template-driven

### When
- Pre-prod environments
- Nightly against staging
- Pre-release gates

### Limitations
- Slower than SAST
- Needs a runnable app
- Coverage limited to what scanner probes
- Risk of impact if pointed at prod

## IAST (Interactive Application Security Testing)

Agent inside running app; tracks data flow at runtime.

### Tools
- **Contrast Security**
- **Hdiv**

### Strengths
- Real-time analysis
- Low false positives (sees actual data flow)
- Catches things SAST can't (config-dependent)

### Limitations
- Performance overhead (~5-15%)
- Per-language agents
- Cost

## RASP (Runtime Application Self-Protection)

Like IAST but blocks attacks at runtime (not just detection).

### Tools
- **Contrast Protect**
- **Sqreen** (Datadog)
- **Imperva Cloud WAF + RASP**

### Trade-Offs
- Performance cost
- Vendor lock-in
- WAF often covers similar ground at lower cost

## SCA (Software Composition Analysis)

Find known vulnerabilities in dependencies.

### Tools
- **Trivy** (free) — containers + IaC + deps
- **Grype** (free)
- **Snyk** (commercial; great UX)
- **OWASP Dependency-Check**
- **Dependabot** (GitHub built-in) — auto-PRs with fixes
- **Renovate** (OSS) — same idea, more flexible
- **OSV-Scanner** (Google) — backed by OSV database

### Coverage
- npm, pip, Maven, Cargo, Go, RubyGems, NuGet
- Container images (OS packages)
- IaC (Terraform, K8s)

### Integration
```yaml
# GitHub Actions
- uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    severity: 'HIGH,CRITICAL'
    exit-code: '1'

- uses: snyk/actions/python@master
  with:
    args: --severity-threshold=high
```

### Triage
Not every CVE is exploitable in your context:
- Is the vulnerable code path actually used?
- Is the vulnerable function called?
- Is the input attacker-controlled?

Tools like Snyk and Endor Labs do reachability analysis (newer, better).

## SBOM (Software Bill of Materials)

Inventory of all components in an artifact. Standards: SPDX, CycloneDX.

Generate at build:
```bash
syft myimage:tag -o cyclonedx-json > sbom.json
```

Use cases:
- Vulnerability matching (CVE → which artifacts have this)
- Supply chain compliance (executive order in US, EU CRA)
- Incident response ("we use log4j; where?")

## Secret Scanning

Find leaked credentials.

### Tools
- **gitleaks** — OSS; in CI + pre-commit
- **trufflehog** — OSS; verifies findings against APIs
- **GitGuardian** — SaaS; org-wide repository scan
- **GitHub Secret Scanning** — built-in for OSS, paid for private

Run on every PR + nightly on full history.

## Integrating in CI

```yaml
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Secret scan
        uses: gitleaks/gitleaks-action@v2
      - name: SAST
        uses: returntocorp/semgrep-action@v1
      - name: SCA
        uses: aquasecurity/trivy-action@master
        with: { scan-type: 'fs', severity: 'HIGH,CRITICAL', exit-code: '1' }
      - name: IaC
        uses: bridgecrewio/checkov-action@v12
```

## Findings Triage

| Severity | Action |
|---|---|
| Critical | Block merge; patch ASAP |
| High | Block merge; remediate within sprint |
| Medium | Track; patch this quarter |
| Low | Track; review quarterly |

Avoid: drowning in findings with no action.

## Interview Themes

- "SAST vs DAST vs IAST"
- "SCA — what's special about it?"
- "Why might a 'critical' CVE not be critical for you?"
- "Secret scanning — strategies"
- "Integrate security in CI — how"
