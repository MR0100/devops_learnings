# L15/C04/T05 — Security Tests in CI

## Learning Objectives

- Run security tests
- Avoid common gaps

## Types

### SAST (Static)
Code analysis without running.

### DAST (Dynamic)
Test running app.

### SCA (Software Composition)
Scan dependencies.

### Secret Scanning
Find committed secrets.

### Container Scanning
Scan images for CVEs.

### IaC Scanning
Scan Terraform / K8s manifests.

### IAST (Interactive)
Hybrid; runtime instrumentation.

## SAST Tools

- Semgrep
- CodeQL (GitHub)
- SonarQube
- Snyk Code
- Checkmarx
- Veracode

```yaml
- uses: returntocorp/semgrep-action@v1
  with:
    config: p/default
```

For: code-level vulns.

## DAST Tools

- OWASP ZAP
- Burp Suite
- Acunetix

```bash
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://staging.example.com
```

For: running-app vulns.

## SCA Tools

- Dependabot (GitHub)
- Renovate
- Snyk Open Source
- WhiteSource / Mend
- OWASP Dependency-Check

```yaml
- uses: snyk/actions/python@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

For: vulnerable deps.

## Secret Scanning

- TruffleHog
- GitLeaks
- GitHub Advanced Security
- detect-secrets

```yaml
- uses: gitleaks/gitleaks-action@v2
```

For: AWS keys, tokens, passwords in code.

## Container Scanning

- Trivy
- Grype
- Snyk Container
- Anchore

```bash
trivy image myapp:v1
trivy fs .
```

For: CVEs in image.

## IaC Scanning

- Checkov
- tfsec (now Trivy)
- Terrascan
- KICS

```bash
checkov -d terraform/
checkov -f main.tf
```

For: misconfig in IaC.

## K8s Scanning

- Trivy (image + IaC)
- Polaris
- Kube-bench (CIS)
- Falco (runtime)

```bash
trivy config kubernetes/
kube-bench
```

## Pipeline

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
        with:
          config: p/default

      - name: SCA
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      - name: Container scan
        run: |
          docker build -t myapp:${{ github.sha }} .
          trivy image --exit-code 1 --severity CRITICAL myapp:${{ github.sha }}

      - name: IaC scan
        run: checkov -d terraform/
```

## Severity Levels

```
CRITICAL: block
HIGH:     block (or warn)
MEDIUM:   warn
LOW:      info
```

For: practical gates.

## Trivy

```bash
# Image
trivy image nginx:latest

# Filesystem
trivy fs --severity HIGH,CRITICAL .

# IaC
trivy config kubernetes/

# SBOM
trivy image --format cyclonedx myapp:v1 > sbom.json

# Ignore by ID
trivy image --ignore-id CVE-2023-12345 myapp:v1
```

## Allowlists

```yaml
# .trivyignore
CVE-2023-12345
CVE-2024-67890
```

Document why each ignored.

## SBOM Generation

```yaml
- uses: anchore/sbom-action@v0
  with:
    image: myapp:${{ github.sha }}
    format: cyclonedx-json
```

Attach to release. For: supply chain.

## Signed Images

```bash
cosign sign --yes registry/myapp:${{ github.sha }}
```

K8s verifies before pull.

## Dependency Pinning

```
package.json with package-lock.json (committed)
go.mod with go.sum
requirements.txt (pinned versions)
Pipfile.lock
Cargo.lock
```

Versions deterministic.

## Update Strategy

```yaml
# Dependabot
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

Renovate: more flexible.

For: regular patching.

## OWASP Top 10

Check for:
- Broken access control
- Cryptographic failures
- Injection (SQL, XSS)
- Insecure design
- Misconfiguration
- Vulnerable components
- Auth failures
- Software integrity
- Logging / monitoring
- SSRF

Tools cover some; pen test covers rest.

## Pen Testing

Manual / automated:
- Burp Suite
- Metasploit
- Specialized firms (annually)

For: depth beyond CI scans.

## OWASP ASVS

Application Security Verification Standard:
- L1: opportunistic
- L2: standard
- L3: advanced

Map your testing.

## Threat Modeling

Before CI: think about threats.

Frameworks:
- STRIDE (Spoof, Tamper, Repudiate, Info, DoS, Elevate)
- LINDDUN (privacy)
- PASTA

Find what to test.

## Compliance Scans

- PCI-DSS
- HIPAA
- GDPR
- SOC 2

Tools map to controls.

## Tools Integration

```yaml
# GitHub Code Scanning
- uses: github/codeql-action/init@v3
  with:
    languages: javascript
- uses: github/codeql-action/analyze@v3
```

Results in Security tab.

## Fail Build vs Warn

```yaml
- run: trivy image --exit-code 1 --severity CRITICAL myapp
  # exit 1 if critical
```

For prod: fail.
For dev branches: warn + dashboard.

## Best Practices

- All categories scanned
- Per-PR scans
- Fail on critical
- SBOM published
- Image signed
- Allowlists documented
- Pen test annually
- Threat model new features

## Common Mistakes

- Only SAST (miss runtime, deps)
- No secret scanning (key leaks)
- Allow critical CVEs
- No SBOM
- Out-of-date scanners
- Run only on main (PRs slip)

## Cost

- Open source tools: time
- Commercial (Snyk, Checkmarx): $$
- Pen testing: $$$

For: layered.

## DAST in CI

Often run vs staging:
```yaml
- name: Deploy to staging
  run: ./deploy.sh staging

- name: ZAP scan
  run: docker run owasp/zap2docker-stable zap-baseline.py -t https://staging.example.com
```

## Quick Refs

```bash
# SAST
semgrep --config p/default

# SCA
trivy fs .
snyk test

# Container
trivy image IMAGE

# IaC
checkov -d terraform/

# Secrets
gitleaks detect

# DAST
zap-baseline.py -t URL
```

## Interview Prep

**Mid**: "Security in CI."

**Senior**: "DevSecOps pipeline."

**Staff**: "Security at scale."

## Next Topic

→ [T06 — Flaky Test Management](T06-Flaky-Tests.md)
