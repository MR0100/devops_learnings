# L06/C02/T02 — Virtual Environments, Poetry, uv

## Learning Objectives

- Manage Python deps isolated per project
- Choose tool

## Why venv

System Python: shared deps; conflicts. Per-project venv: isolated.

## Plain venv + pip

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests
pip install -r requirements.txt
deactivate
```

`requirements.txt`:
```
requests>=2.31
boto3>=1.28
```

Lock for reproducibility:
```bash
pip install pip-tools
pip-compile requirements.in       # → requirements.txt with pinned versions
```

## Poetry

Modern Python dep + project manager.

```bash
poetry init                  # interactive
poetry add requests
poetry add --dev pytest
poetry install
poetry run python main.py
poetry shell                 # activate
poetry build                 # build wheel
poetry publish               # to PyPI
```

`pyproject.toml`:
```toml
[tool.poetry]
name = "myapp"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.31"

[tool.poetry.dev-dependencies]
pytest = "^7.4"
```

Lock file: `poetry.lock` (commit it).

## uv (Astral, Rust-based, RECOMMENDED 2025+)

Drop-in pip replacement; 10-100× faster.

```bash
uv venv                      # creates .venv
source .venv/bin/activate

uv pip install requests      # like pip install
uv pip sync requirements.txt  # like pip-sync

# Project management (uv 0.3+)
uv init
uv add requests
uv run python main.py
uv sync                      # install lockfile

# Tools (like pipx)
uv tool install ruff
uv tool run black .
```

`uv.lock` is the lockfile.

### Why uv
- 10-100× faster than pip/poetry
- One tool (replaces pip, pip-tools, pipx, poetry, virtualenv)
- Rust-built
- Active development (Astral)

## Comparison

| | pip | Poetry | uv |
|---|---|---|---|
| Speed | Slow | Slow | Very fast |
| Project mgmt | Basic | Full | Full |
| Lockfile | requirements.txt (with pip-tools) | poetry.lock | uv.lock |
| Tool install | pipx | poetry tool | uv tool |
| Resolution | Basic | Good | Excellent |
| Newer | 1995 | 2018 | 2024 |

## Recommendation 2025+

**uv** for new projects. **Poetry** if already invested. **pip** for one-offs.

## Dependency Pinning

Three levels:
- **Loose**: `requests>=2.0` (any 2.x)
- **Compatible**: `requests~=2.31` (any 2.31.x)
- **Exact**: `requests==2.31.0` (only that)

Lockfile pins exact. Manifest can be looser.

## Updating Deps

```bash
# Poetry
poetry update                 # all
poetry update requests        # specific

# uv
uv lock --upgrade
```

Then test; commit lockfile.

## Renovate / Dependabot

Auto-PRs to update deps. Integrate with CI; merge on green.

## Production Distribution

For CLIs:
- pipx install
- uv tool install
- standalone bin via shiv / pyinstaller

For services:
- Docker (image with deps)
- Lambda Layer

For libraries:
- Publish to PyPI

## Common Issues

- venv not activated → pip installs to system
- requirements.txt without lock → versions drift
- Editing site-packages directly → loss on reinstall
- Mixing system + venv pip → confused state

## Operations

```bash
# Show installed
pip list
uv pip list

# Frozen lockfile output
pip freeze > requirements.txt
uv pip freeze > requirements.txt

# Remove venv
rm -rf .venv
```

## Tooling Choice for Org

For team consistency:
- Pick one (uv recommended new; Poetry stable)
- Document in README
- Set up CI with same tool
- Enforce via pre-commit

## Common Mistakes

- Committing `requirements.txt` from `pip freeze` but no real lockfile, so transitive deps drift between machines and CI.
- Mixing tools in one repo (Poetry for some, raw pip for others) so the lockfile and the installed env disagree.
- Installing into the system interpreter because the venv was never activated (`pip` silently writes to system site-packages).
- Running `uv pip install` ad hoc instead of `uv add` + `uv sync`, leaving `uv.lock` and `pyproject.toml` out of sync.
- Baking dev/test dependencies into the production image instead of installing only the locked runtime group.

## Best Practices

- Standardize on one tool org-wide (uv for new projects, Poetry where already stable), document it in the README, and enforce via pre-commit.
- Commit the lockfile (`uv.lock` / `poetry.lock`) and make CI install from it (`uv sync --frozen` / `poetry install`) for reproducible builds.
- Use dependency groups to separate dev/test from runtime, and install only runtime deps in production images.
- Pin `requires-python` in `pyproject.toml` so an incompatible interpreter fails fast instead of mid-deploy.
- Recreate (`rm -rf .venv && uv sync`) rather than hand-patch a broken environment; never edit `site-packages` directly.
- Automate dependency updates with Renovate/Dependabot so lockfile bumps land as reviewable PRs.

## Quick Refs

| Task | venv + pip | Poetry | uv |
|---|---|---|---|
| Create env | `python -m venv .venv` | (auto) | `uv venv` |
| Add a dep | `pip install X` | `poetry add X` | `uv add X` |
| Add a dev dep | — | `poetry add --dev X` | `uv add --dev X` |
| Install from lock | `pip install -r requirements.txt` | `poetry install` | `uv sync` |
| Run in env | `python main.py` (activated) | `poetry run python main.py` | `uv run python main.py` |
| Lockfile | `requirements.txt` (manual/pip-tools) | `poetry.lock` | `uv.lock` |

Reproducibility rule: commit the **lockfile**, not just the loose dependency list — CI must install from the lock.

## Interview Prep

**Junior**: "Why venv?"

**Mid**: "Lock file purpose."

**Senior**: "uv vs Poetry — when each?"

## Next Topic

→ [T03 — Standard Library Highlights](T03-Standard-Library.md)
