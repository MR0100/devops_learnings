# L05/C07/T03 — pre-commit Framework

## Learning Objectives

- Install and configure pre-commit framework
- Use community hooks
- Integrate into CI

## What pre-commit Is

Python tool (`pip install pre-commit`) that manages Git hooks across languages.

Not to be confused with the `pre-commit` Git hook (different thing).

## Install

```bash
pip install pre-commit
# or
brew install pre-commit
```

## Configure

```yaml
# .pre-commit-config.yaml
repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
  - id: trailing-whitespace
  - id: end-of-file-fixer
  - id: check-yaml
  - id: check-json
  - id: check-added-large-files
    args: ['--maxkb=500']
  - id: check-merge-conflict
  - id: detect-private-key

- repo: https://github.com/gitleaks/gitleaks
  rev: v8.18.0
  hooks:
  - id: gitleaks

- repo: https://github.com/koalaman/shellcheck-precommit
  rev: v0.10.0
  hooks:
  - id: shellcheck

- repo: https://github.com/golangci/golangci-lint
  rev: v1.55.0
  hooks:
  - id: golangci-lint

- repo: https://github.com/charliermarsh/ruff-pre-commit
  rev: v0.1.0
  hooks:
  - id: ruff
  - id: ruff-format

- repo: https://github.com/antonbabenko/pre-commit-terraform
  rev: v1.83.0
  hooks:
  - id: terraform_fmt
  - id: terraform_validate
  - id: tflint
```

## Install Hook

```bash
pre-commit install
# Adds pre-commit hook to .git/hooks/pre-commit
```

Now `git commit` runs configured hooks.

## Run Manually

```bash
pre-commit run --all-files    # against all files
pre-commit run                 # against staged
pre-commit run gitleaks        # specific hook
```

Useful for adding to an existing repo (first time, run on all files).

## Skip

```bash
SKIP=gitleaks git commit -m "..."   # skip specific
git commit --no-verify              # skip all
```

## Update

```bash
pre-commit autoupdate
# Updates rev: tags in config
```

Periodically.

## CI Integration

```yaml
# GitHub Actions
- uses: actions/setup-python@v5
- uses: pre-commit/action@v3.0.0
```

Or:
```yaml
- run: |
    pip install pre-commit
    pre-commit run --all-files
```

CI runs same hooks. Catches what user bypassed.

## Other Hook Types

Default = pre-commit. Configure for other types:

```yaml
- repo: https://github.com/compilerla/conventional-pre-commit
  rev: v3.0.0
  hooks:
  - id: conventional-pre-commit
    stages: [commit-msg]
    args: [--strict]
```

Install:
```bash
pre-commit install --hook-type commit-msg
pre-commit install --hook-type pre-push
```

## Custom Hooks

Local hooks:
```yaml
repos:
- repo: local
  hooks:
  - id: custom-check
    name: My custom check
    entry: ./scripts/check.sh
    language: script
    files: \.py$
```

Or:
```yaml
- id: lint
  name: Lint
  entry: golangci-lint run
  language: system
  pass_filenames: false
```

## Performance

Hooks run on changed files only (default). Most are fast.

For slow checks: move to CI only:
```yaml
- id: slow-test
  stages: [pre-push]    # only on push, not every commit
```

## Common Hook Suite

For a multi-language repo:
```
- trailing-whitespace
- end-of-file-fixer
- check-yaml
- detect-secrets
- shellcheck
- golangci-lint  
- ruff
- terraform_fmt
- conventional-pre-commit (msg)
```

## Sharing Across Org

Some companies share base config:
```yaml
repos:
- repo: git@github.com:org/precommit-shared.git
  rev: v1.0
  hooks:
  - id: company-policy
```

Update version when policy changes.

## When NOT pre-commit Framework

- Tiny solo project (overkill)
- Non-Python users find it weird (rare)
- Need extreme speed (Go-native tools faster)

For most teams: use it.

## Operations

```bash
pre-commit clean                # clear cache
pre-commit gc                   # garbage collect old hook versions
pre-commit migrate-config       # upgrade config format
```

## Tips

- Run `pre-commit run --all-files` once when adding to existing repo (fix existing issues)
- Update versions periodically
- Document in README for new team members

## Integration with CI Flow

```
Developer commits → pre-commit hooks run locally → fast feedback
↓
Push to remote → CI runs pre-commit run --all-files → enforcement
↓
PR merge gated on CI status
```

## Interview Prep

**Mid**: "What's the pre-commit framework?"

**Senior**: "Why both client hooks and CI?"

**Staff**: "Org-wide pre-commit policy."

## Next Topic

→ [T04 — Conventional Commits](T04-Conventional-Commits.md)
