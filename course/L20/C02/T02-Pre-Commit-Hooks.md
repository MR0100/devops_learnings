# L20/C02/T02 — Pre-Commit Hooks

## Learning Objectives

- Set up pre-commit
- Catch issues early

## Pre-Commit

Run before commit:
- Lint
- Security scan
- Format
- Test

For: catch before code lands.

## pre-commit Framework

```bash
pip install pre-commit
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/returntocorp/semgrep
    rev: v1.0.0
    hooks:
      - id: semgrep
        args: ['--config=p/default', '--error']

  - repo: https://github.com/aquasecurity/trivy
    rev: v0.50.0
    hooks:
      - id: trivy
```

## Install

```bash
pre-commit install
```

Sets up git hook.

## Run

Auto on commit. Or manually:
```bash
pre-commit run --all-files
```

## Common Hooks

- trailing-whitespace
- check-yaml / json / toml
- check-merge-conflict
- check-added-large-files
- detect-private-key
- gitleaks
- semgrep
- prettier / black / gofmt

## Security Hooks

- gitleaks (secrets)
- detect-secrets
- semgrep (SAST)
- trivy (deps + IaC)
- checkov (Terraform)

## Bypass (Sometimes)

```bash
git commit --no-verify
```

For: real emergency. Audit.

## Org-Wide

```yaml
# .pre-commit-config.yaml (shared template)
default_install_hook_types: [pre-commit, commit-msg]
default_stages: [commit]
```

Distribute via:
- Cookiecutter / yeoman
- Org template
- Internal docs

## CI Backup

CI also runs:
- Same checks
- For PRs from forks
- For force-push past

For: redundancy.

## Performance

Hooks should be fast:
- < 5 sec ideal
- Lint per-file (only changed)
- Cached

Slow hooks: disable for now; CI catches.

## CI Pre-Commit

```yaml
- name: Pre-commit
  uses: pre-commit/action@v3.0.0
```

Runs all hooks; reports.

## Examples

### Detect Secrets
```yaml
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.5.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
```

Baseline file: known + ignored.

### Conventional Commits
```yaml
- repo: https://github.com/compilerla/conventional-pre-commit
  rev: v3.0.0
  hooks:
    - id: conventional-pre-commit
      stages: [commit-msg]
```

For: semantic-release.

## Update

```bash
pre-commit autoupdate
```

Bumps versions.

## Best Practices

- Required in repo
- Documented
- Run before push
- CI backup
- Periodic update

## Common Mistakes

- Optional (skipped)
- Slow hooks (devs disable)
- No CI backup
- Outdated hooks

## Quick Refs

```bash
# Install
pip install pre-commit
pre-commit install

# Run
pre-commit run --all-files

# Update
pre-commit autoupdate

# Bypass
git commit --no-verify
```

## Interview Prep

**Mid**: "Pre-commit hooks."

**Senior**: "Security in pre-commit."

## Next Topic

→ [T03 — Developer Security Training](T03-Dev-Training.md)
