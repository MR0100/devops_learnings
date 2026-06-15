# L20/C02/T01 — IDE Security Plugins

## Learning Objectives

- Catch vulns in IDE
- Shift left

## Why IDE

Earliest catch:
- Before commit
- Before CI
- Free / fast

For: developer feedback.

## Plugins

### Semgrep VSCode
Inline issues:
```bash
code --install-extension semgrep.semgrep
```

Shows: vuln patterns.

### Snyk VSCode
```bash
code --install-extension snyk-security.snyk-vulnerability-scanner
```

Dependencies + code.

### SonarLint
SonarQube IDE companion.

### Checkmarx
Commercial; many languages.

## What They Catch

- SQL injection
- XSS
- Hardcoded secrets
- Insecure crypto
- Dependency CVEs

## Inline Hints

```javascript
const query = `SELECT * FROM users WHERE id = ${userId}`;
// ⚠ SQL injection risk: use parameterized query
```

For: immediate.

## Auto-Fix

Some plugins suggest fixes:
- Apply with click
- Or accept

For: speed.

## Rules

Pre-built rule packs:
- OWASP Top 10
- CWE common
- Language-specific

Custom rules:
```yaml
rules:
  - id: hardcoded-aws-key
    pattern: AKIA[0-9A-Z]{16}
    message: AWS key in code
```

## Org Policy

Enterprise:
- Force install
- Pre-configured rules
- Block commits if violations

## CI Backup

IDE finds most. CI catches rest:
- Pre-commit hooks
- PR checks
- Background scan

For: defense in depth.

## Cost

- Open source: free
- Snyk: free + paid
- SonarQube: free + paid

For: budget.

## Best Practices

- Auto-install for new engineers
- Configured rules
- Auto-fix where safe
- Periodic update

## Common Mistakes

- Optional install (skipped)
- Default rules (irrelevant)
- No CI backup (skipped IDE)

## Quick Refs

```
Semgrep, Snyk, SonarLint, Checkmarx
Catches: SQLi, XSS, secrets, CVE
Inline: yes
Auto-fix: some
```

## Interview Prep

**Junior**: "What do IDE security plugins do?" — They scan code as you type, flagging vulnerabilities, hardcoded secrets, and vulnerable dependencies inline so issues are caught before commit.

**Mid**: "Why catch security issues in the IDE rather than in CI?" — The earlier a flaw is found, the cheaper it is to fix; inline feedback fixes it while context is fresh, before it ever reaches a pipeline, review, or production.

**Senior**: "What are the trade-offs of IDE-based scanning?" — It gives fast, developer-friendly feedback but can't be your enforcement gate (developers can ignore or disable it) and may add noise, so pair it with authoritative CI scans that block merges.

**Staff**: "How do you roll IDE security tooling out at scale without it being ignored?" — Ship it as a managed, low-noise default config, tune rules to high-signal findings, measure adoption and pre-CI catch rate, and treat the IDE as the fast feedback layer backed by CI as the source of truth.

## Next Topic

→ [T02 — Pre-Commit Hooks](T02-Pre-Commit-Hooks.md)
