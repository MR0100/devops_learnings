# L05/C07/T01 — Client-Side Hooks

## Learning Objectives

- Use pre-commit, commit-msg, pre-push hooks
- Share hooks across team
- Recognize bypass risk

## Hooks Overview

Scripts in `.git/hooks/` triggered at Git events.

```
.git/hooks/
├── pre-commit              # before commit creates
├── prepare-commit-msg      # before message editor
├── commit-msg              # after message written
├── post-commit             # after commit complete
├── pre-push                # before push
├── post-merge              # after merge
├── pre-rebase              # before rebase
└── pre-receive (server-side)
```

Sample hooks (`.sample` extension) included. Rename to enable.

## pre-commit

Most common. Runs before commit creates. Exit non-zero to abort.

```bash
#!/bin/bash
# .git/hooks/pre-commit
set -e

# Block .env files
if git diff --cached --name-only | grep -E '\.env$'; then
    echo "Don't commit .env files"
    exit 1
fi

# Run linter
make lint
```

Make executable: `chmod +x .git/hooks/pre-commit`.

## commit-msg

Validates commit message:

```bash
#!/bin/bash
# .git/hooks/commit-msg
msg_file="$1"
msg=$(cat "$msg_file")

if ! echo "$msg" | grep -qE '^(feat|fix|docs|chore|refactor|test): '; then
    echo "Commit message must start with feat:|fix:|docs:|..."
    exit 1
fi
```

Enforces conventional commits.

## pre-push

Before push to remote:

```bash
#!/bin/bash
# .git/hooks/pre-push
remote="$1"
url="$2"

while read local_ref local_sha remote_ref remote_sha; do
    # Run tests
    if ! make test; then
        echo "Tests failed; push aborted"
        exit 1
    fi
done
```

## Sharing Hooks (Critical)

`.git/` is NOT in the repo. Hooks in `.git/hooks/` aren't shared.

### Solution: core.hooksPath
```bash
git config core.hooksPath .githooks
```

Now Git uses `.githooks/` (committed to repo) instead of `.git/hooks/`.

```
.githooks/
├── pre-commit
├── commit-msg
└── pre-push
```

Make executable:
```bash
chmod +x .githooks/*
```

Each clone needs:
```bash
git config core.hooksPath .githooks
```

Some teams put in setup script.

## pre-commit Framework

Best practice: use the `pre-commit` tool (Python-based) that manages hooks across languages.

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

- repo: https://github.com/koalaman/shellcheck-precommit
  rev: v0.10.0
  hooks:
  - id: shellcheck

- repo: https://github.com/golangci/golangci-lint
  rev: v1.55.0
  hooks:
  - id: golangci-lint
```

```bash
pip install pre-commit
pre-commit install        # installs git hook
pre-commit run --all-files
```

## Common Pre-Commit Hooks

- Linters (golangci-lint, ruff, eslint)
- Formatters (gofmt, black, prettier)
- Secret scanning (gitleaks)
- YAML/JSON validation
- Conventional commits

## Bypass

Hooks can be skipped:
```bash
git commit --no-verify        # skip pre-commit + commit-msg
git push --no-verify          # skip pre-push
```

So hooks aren't security guarantee. Defense in depth: replicate in CI.

## CI Replication

Always have CI also run what hooks check:
```yaml
- name: Pre-commit checks
  run: pre-commit run --all-files
```

Hooks: fast local feedback.
CI: enforcement; cannot be bypassed.

## Lightweight vs Heavy

### Lightweight (run on every commit)
- Linting changed files only
- Format check
- Secret scan

### Heavy (run on push or rarely)
- Full test suite
- Build verification

Keep pre-commit fast (< 5 sec ideal). Slow → engineers bypass.

## Cross-Platform

Hooks must work on:
- Linux
- macOS
- Windows (Git Bash)

Use portable shells. Avoid Linux-specific tools.

## Sample Setup

```bash
# Project setup script
git config core.hooksPath .githooks
pip install pre-commit
pre-commit install
```

Run once after clone.

## Common Issues

- Forgot to make executable (hook ignored)
- Hook expects tools not installed (lint fails confusingly)
- Hook too slow (engineers `--no-verify`)
- Hook doesn't work on Windows (bash assumption)

## Operations

```bash
# Manually run hook
.githooks/pre-commit

# Run pre-commit on all files
pre-commit run --all-files

# Skip a specific hook
SKIP=shellcheck git commit -m "..."
```

## Interview Prep

**Junior**: "What's pre-commit hook?"

**Mid**: "Share hooks across team."

**Senior**: "Hooks bypassed; what's the backstop?"

## Next Topic

→ [T02 — Server-Side Hooks](T02-Server-Side-Hooks.md)
