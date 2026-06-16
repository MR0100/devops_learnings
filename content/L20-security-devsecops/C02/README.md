# L20/C02 — Shift Left Security

## Topics

- **T01 IDE Security Plugins** — Catch in editor
- **T02 Pre-Commit Hooks** — Catch before commit
- **T03 Developer Security Training** — The human layer

## The Spectrum

```
DEV               COMMIT          PR              CI              CD              PROD
 ↓                  ↓                ↓               ↓               ↓               ↓
IDE plugins      Pre-commit       PR checks      CI scans       Image policy   Runtime
Linting          Secret scan      SAST           SCA           Admission      detection
Type checks      Format check     Test           Container     OPA            Falco
                                                  scan           Gatekeeper
```

The earlier you catch, the cheaper to fix.

## IDE Plugins

### Semgrep
Pattern-matching SAST. IDE plugin shows findings inline.

### Snyk
Inline vuln warnings on imported deps.

### SonarLint
Quality + security warnings, linked to SonarQube rules.

### Built-in
- VS Code: Microsoft DevSkim, GitHub Codespaces security tab
- IntelliJ: built-in inspections + Qodana

## Pre-Commit Hooks

Stop bad things from entering the repo. Examples:

```yaml
# .pre-commit-config.yaml
repos:
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.18.0
  hooks:
  - id: gitleaks                  # Detect secrets

- repo: https://github.com/Yelp/detect-secrets
  rev: v1.4.0
  hooks:
  - id: detect-secrets

- repo: https://github.com/antonbabenko/pre-commit-terraform
  rev: v1.83.0
  hooks:
  - id: terraform_fmt
  - id: terraform_validate
  - id: terraform_tflint
  - id: tfsec

- repo: https://github.com/bridgecrewio/checkov
  rev: 3.0.0
  hooks:
  - id: checkov

- repo: https://github.com/koalaman/shellcheck-precommit
  rev: v0.10.0
  hooks:
  - id: shellcheck
```

```bash
pre-commit install                 # in repo, sets up git hook
pre-commit run --all-files         # one-off
```

### Critical Note
Pre-commit hooks can be bypassed (`git commit --no-verify`). Always replicate checks in CI; pre-commit is a faster local feedback loop, not the gate.

## Developer Security Training

Even the best tools don't catch novel bugs. Training the developers does.

### Topics
- OWASP Top 10 (web; updated every few years)
- Secure coding patterns per language
- Threat modeling basics
- Recognizing phishing / social engineering
- Cloud-specific risks (IAM, S3 leaks, etc.)
- Container security
- Incident response basics

### Formats
- Annual mandatory module
- Hands-on workshops (Capture the Flag)
- "Tech talks" deep dives
- Onboarding bootcamp

### Effectiveness Indicators
- Reduced security findings per PR
- Developers asking better questions
- Self-reported security incidents (not hidden)

## Capture the Flag (CTF)

Internal CTF events where engineers attack purposely vulnerable apps. Best way to instill security mindset.

Tools:
- **GitGuardian** for secret-scan training
- **OWASP Juice Shop** (vulnerable web app)
- **TryHackMe / HackTheBox** (commercial)
- Internal "red day" — eng/security team builds a vulnerable env

## Security Champions

A program where one engineer per team is the "security champion":
- Takes deep training
- First line of security questions on the team
- Bridges to security team
- Doesn't replace security team; multiplies them

Effective at scale.

## Secrets Discovery Tools

For finding leaks in existing repos:
- **GitGuardian** — SaaS, organization-wide
- **Gitleaks** — OSS, CLI + pre-commit + CI
- **TruffleHog** — OSS, deeper scan (verifies API keys against live services)

Run quarterly across all repos; remediate findings (rotate the leaked secret, then clean Git history).

## Code Review for Security

Every PR review should ask:
- Does this handle user input safely?
- Where does external data come from?
- Are secrets exposed?
- Is logging redacting sensitive data?
- Does this expand IAM permissions? Necessarily?
- Does this open a new network path?

Security questions in code review become habit.

## Shift-Left Doesn't Mean Skip-Right

Shift-left catches many issues. But runtime threats (zero-days, misconfig, lateral movement) still need:
- Runtime detection (Falco)
- Network anomaly detection
- Audit log review
- Incident response

Layers.

## Interview Themes

- "Shift left security — what does it mean?"
- "Pre-commit hooks — what's caught, what's missed?"
- "Security champions program"
- "Why developer training matters"
- "Tool chain for catching issues early"
