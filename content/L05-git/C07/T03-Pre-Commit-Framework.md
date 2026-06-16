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

## Common Mistakes

- Installing the config but forgetting `pre-commit install`, so hooks never actually run on commit — the YAML alone does nothing.
- Leaving `rev:` unpinned or stale; without periodic `pre-commit autoupdate` the team runs different hook versions and gets inconsistent results.
- Expecting the framework to enforce policy — like all client hooks it's bypassable with `--no-verify`; the CI mirror is the real gate.
- Forgetting `pre-commit run --all-files` when first adopting it on an existing repo, so a backlog of violations only surfaces commit-by-commit later.
- Not specifying the right `default_language_version`/stages, causing hooks to fail or run at unexpected points (e.g. a commit-msg hook never wired up).
- Putting slow hooks in the commit stage instead of `pre-push`/CI, training developers to bypass.

## Best Practices

- Commit `.pre-commit-config.yaml` and run `pre-commit install` (and `--hook-type commit-msg` / `pre-push` as needed) so the whole team gets identical checks.
- Pin every hook `rev:` to a tag and bump deliberately with `pre-commit autoupdate`, reviewing the diff like any dependency update.
- Run `pre-commit run --all-files` in CI as the enforcement layer; local hooks are for fast feedback, CI is the gate.
- When onboarding it to an existing repo, fix the whole backlog first with one `--all-files` pass so future commits stay clean.
- Keep the commit-stage hooks fast (format/lint staged files) and move heavier checks to `pre-push` or CI.
- Document setup in the README and provide a bootstrap script so new contributors are protected from their first commit.

## Quick Refs

```bash
# Setup
pipx install pre-commit                       # or pip install
pre-commit install                            # wire pre-commit hook
pre-commit install --hook-type commit-msg     # also wire commit-msg
pre-commit install --hook-type pre-push

# Run
pre-commit run                                # on staged files
pre-commit run --all-files                    # whole repo (adoption / CI)
pre-commit run black --all-files              # one hook only

# Maintain
pre-commit autoupdate                         # bump pinned rev: tags
pre-commit clean                              # clear cache
pre-commit gc                                 # drop unused hook envs

# Bypass (escape hatch)
git commit --no-verify
SKIP=flake8 git commit -m "..."
```

```yaml
# .pre-commit-config.yaml (minimal)
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks: [ {id: trailing-whitespace}, {id: end-of-file-fixer}, {id: check-yaml} ]
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks: [ {id: ruff}, {id: ruff-format} ]
```

## Interview Prep

**Mid**: "What's the pre-commit framework?"

**Senior**: "Why both client hooks and CI?"

**Staff**: "Org-wide pre-commit policy."

## Next Topic

→ [T04 — Conventional Commits](T04-Conventional-Commits.md)
