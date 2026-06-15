# L20/C03/T01 — SAST (SonarQube, Semgrep, CodeQL)

## Learning Objectives

- Use SAST tools
- Integrate in CI

## SAST

Static Application Security Testing:
- Analyze source code
- No execution
- Find vulns

## Tools

### Semgrep
Open source; fast; rules in YAML:
```yaml
rules:
  - id: hardcoded-aws-key
    pattern: AKIA[0-9A-Z]{16}
    message: AWS access key found
    languages: [generic]
    severity: ERROR
```

```bash
semgrep --config=p/default .
```

### SonarQube
Comprehensive; rich UI:
- Many languages
- Quality + security
- Server (self-host or cloud)

```bash
sonar-scanner -Dsonar.projectKey=my-app
```

### CodeQL
GitHub-owned; query-based:
- Treat code as data
- Custom queries

```yaml
# .github/workflows/codeql.yml
- uses: github/codeql-action/init@v3
  with:
    languages: javascript, python
- uses: github/codeql-action/analyze@v3
```

### Snyk Code
Snyk's SAST.

### Checkmarx
Commercial; deep analysis.

## Common Findings

- SQL injection
- XSS
- Path traversal
- Hardcoded secrets
- Insecure deserialization
- Weak crypto

## CI Integration

```yaml
- name: SAST
  uses: returntocorp/semgrep-action@v1
  with:
    config: p/default p/security-audit p/secrets

- name: Block merge
  if: steps.semgrep.outputs.findings_count > 0
  run: exit 1
```

## Severity

Block:
- CRITICAL
- HIGH

Warn:
- MEDIUM
- LOW

For: don't drown in low.

## False Positives

Common SAST issue:
- Tool flags safe code

Mitigations:
- Allowlists
- Code annotations:
  ```python
  # nosec  # noqa
  ```

- Suppress with reason

## Allowlist

```yaml
# .semgrepignore
*test*
docs/
```

Skip test code (usually OK).

## Rules

Per language. Common:
- OWASP
- CWE
- Custom

## Custom Rules

```yaml
rules:
  - id: my-org-no-eval
    pattern: eval($X)
    message: Don't use eval
    languages: [javascript]
```

For: org-specific patterns.

## SAST in Pipeline

```
Commit → SAST → block if critical
PR     → SAST → annotate findings
Main   → SAST → trend
```

## Performance

- Semgrep: fast (~minutes)
- CodeQL: slow (~10-30 min, deeper)
- SonarQube: medium

Trade-off: depth vs speed.

## Coverage

SAST language support:
- JS / TS
- Python
- Java
- Go
- Rust
- Ruby
- PHP
- C / C++

For: pick by language.

## Reports

- HTML
- SARIF (standard)
- JSON
- JUnit

For: integrate with dashboards.

## SARIF

```bash
semgrep --config=p/default --sarif > findings.sarif

# Upload to GitHub
gh sarif upload findings.sarif
```

Shown in Security tab.

## Vs DAST

SAST:
- Static
- Source code
- Find in dev

DAST:
- Dynamic
- Running app
- Find in staging

Both useful.

## Vs SCA

SAST: your code.
SCA: dependencies.

Both needed.

## Best Practices

- SAST in CI (every PR)
- Block on critical
- Allowlist false positives
- Custom rules for org
- SARIF to GitHub
- Track trends

## Common Mistakes

- No SAST
- Block on everything (noise)
- No allowlist (drown)
- One-time
- Skip critical fixes

## Cost

- Semgrep: open source
- CodeQL: free for open source
- Snyk: free + paid
- SonarQube: free + paid (Server $)
- Checkmarx: enterprise $$

## Quick Refs

```bash
# Semgrep
semgrep --config=p/default

# CodeQL
codeql database create / analyze

# SonarQube
sonar-scanner

# Snyk
snyk code test
```

## Interview Prep

**Junior**: "What is SAST?" — Static Application Security Testing analyzes source code (or bytecode) without running it, finding vulnerability patterns like injection, XSS, and hardcoded secrets early in development.

**Mid**: "How do you integrate SAST into CI without slowing teams down?" — Run fast incremental scans (diff-only) on PRs as a required check, full scans nightly, and gate the merge only on new high-severity findings so legacy noise doesn't block delivery.

**Senior**: "How do you handle SAST false positives at scale?" — Tune and suppress rules with tracked justifications, baseline existing findings so only net-new issues fail builds, and prefer high-signal tools (e.g. Semgrep/CodeQL with curated rulesets) so developers trust the gate.

**Staff**: "What's your org-wide SAST strategy?" — Standardize a paved-road scanner with central rule management, risk-rank findings (reachability, exploitability) rather than treating all CVEs equally, feed results into a single vuln-management view, and measure mean-time-to-remediate rather than raw finding counts.

## Next Topic

→ [T02 — DAST (OWASP ZAP, Burp)](T02-DAST.md)
