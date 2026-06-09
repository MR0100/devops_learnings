# L05/C07 — Git Hooks & Automation

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Client-Side-Hooks.md) | Client-Side Hooks (pre-commit, commit-msg, pre-push) | 0.5 hr |
| [T02](T02-Server-Side-Hooks.md) | Server-Side Hooks | 0.5 hr |
| [T03](T03-Pre-Commit-Framework.md) | pre-commit Framework | 1 hr |
| [T04](T04-Conventional-Commits.md) | Conventional Commits | 0.5 hr |

## Hooks Overview

Scripts in `.git/hooks/` (or `core.hooksPath` config) that run at specific Git events.

| Hook | Side | When |
|---|---|---|
| pre-commit | Client | Before commit creates |
| prepare-commit-msg | Client | Before commit message editor |
| commit-msg | Client | After message written |
| post-commit | Client | After commit complete |
| pre-push | Client | Before push |
| post-merge | Client | After merge |
| pre-rebase | Client | Before rebase |
| pre-receive | Server | Before receiving push |
| update | Server | Per ref during receive |
| post-receive | Server | After push received |

## Client Hooks

Per-repo, not committed by default (Git ignores `.git/`). To share, use `core.hooksPath`:

```bash
# .githooks/pre-commit
#!/usr/bin/env bash
set -e

# Fail if any .env files
if git diff --cached --name-only | grep -E '\.env$'; then
  echo "ERROR: Don't commit .env files"
  exit 1
fi

# Run linter
make lint || exit 1
```

Activate:
```bash
git config core.hooksPath .githooks
chmod +x .githooks/*
```

## The pre-commit Framework

The standard way to share hooks across teams. Python-based but supports any language.

```yaml
# .pre-commit-config.yaml
repos:
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
  - id: trailing-whitespace
  - id: end-of-file-fixer
  - id: check-yaml
  - id: check-added-large-files
  - id: check-merge-conflict
  - id: detect-private-key

- repo: https://github.com/koalaman/shellcheck-precommit
  rev: v0.10.0
  hooks:
  - id: shellcheck

- repo: https://github.com/gitleaks/gitleaks
  rev: v8.18.0
  hooks:
  - id: gitleaks

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

```bash
pip install pre-commit
pre-commit install                 # install git hook
pre-commit install --hook-type pre-push
pre-commit run --all-files         # one-off
```

## Common Pre-Commit Use Cases

- Linting (shellcheck, eslint, golangci-lint, ruff)
- Formatting (prettier, black, gofmt, terraform fmt)
- Type checking (mypy, tsc)
- Secret scanning (gitleaks, trufflehog)
- YAML/JSON validation
- Conventional commit message check
- Branch name validation

## commit-msg: Conventional Commits

```yaml
- repo: https://github.com/compilerla/conventional-pre-commit
  rev: v3.0.0
  hooks:
  - id: conventional-pre-commit
    stages: [commit-msg]
```

Enforces:
```
feat(scope): subject

body

footer
```

Enables semantic-release / release-please for automated versioning.

## Server-Side Hooks

Run on the Git server (or GitHub/GitLab via webhooks/Actions).

- **pre-receive**: reject pushes that violate policy (commit signing, branch naming)
- **update**: per ref; can reject just one branch's push
- **post-receive**: trigger downstream (notify, deploy, mirror)

On hosted Git (GitHub):
- Branch protection rules (UI)
- Required workflows (Actions)
- Status checks
- GitHub Apps for custom policies

## CI Replicates Hooks

Always replicate pre-commit checks in CI:

```yaml
# .github/workflows/lint.yml
name: lint
on: [pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: pre-commit/action@v3.0.0
```

Reason: client hooks can be bypassed (`git commit --no-verify`). CI cannot.

## Conventional Commits Tooling

- **semantic-release** — automated version bump + changelog + release based on commit messages
- **release-please** (Google) — same idea
- **commitizen** — interactive commit message builder

```
feat: breaking change → MAJOR bump
feat: new feature      → MINOR
fix:  bug              → PATCH
docs/chore/refactor    → no bump
```

## Interview Themes

- "Why use pre-commit hooks?"
- "Compare client vs server-side hooks"
- "Conventional commits — what do they enable?"
- "How do you enforce policy at the server level?"
- "What gets bypassed with --no-verify?"
