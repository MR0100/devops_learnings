# L05/C05/T04 — Git LFS for Large Files

## Learning Objectives

- Configure Git LFS
- Understand pointer files
- Migrate to LFS

## Why LFS

Git stores all history. Large binaries (PSDs, videos, ML models) bloat repos:
- Slow clones
- Slow operations
- Disk usage explodes

LFS (Large File Storage) stores binaries separately; Git tracks pointers.

## How It Works

```
Repo:
file.psd → LFS pointer (small text file with hash)

LFS server (storage):
abc123... → actual 100 MB PSD content
```

On clone: pointer downloaded. On checkout: actual file fetched from LFS server.

## Install

```bash
# Once per system
git lfs install
```

## Track Files

```bash
git lfs track "*.psd"
git lfs track "*.mp4"
git lfs track "models/*.bin"

# This updates .gitattributes:
# *.psd filter=lfs diff=lfs merge=lfs -text
```

Commit `.gitattributes`.

## Add Files

```bash
git add file.psd                # automatically stored as LFS
git commit -m "Add design"
git push
```

LFS server stores binary; Git stores small pointer.

## See What's LFS

```bash
git lfs ls-files                # list LFS-tracked files in HEAD
git lfs status                  # what would be pushed
```

## Pointer File

```
version https://git-lfs.github.com/spec/v1
oid sha256:abc123...
size 12345678
```

Small text. Git operates on pointers; LFS provides the actual content on demand.

## Hosting

- GitHub LFS: included; 1 GB free; paid for more
- GitLab LFS: included; depends on plan
- Self-hosted: gitea, gitlab, git-lfs server
- AWS: lfs-server backed by S3

## Storage Cost

GitHub:
- 1 GB free storage + 1 GB bandwidth/month
- $5/month for 50 GB
- Bandwidth especially: each clone downloads LFS content

For large repos, bandwidth costs add up.

## Migrate Existing Files to LFS

```bash
git lfs migrate import --include="*.psd" --everything
# Rewrites history; --everything = all branches/tags

git push --force --all
git push --force --tags
```

DANGEROUS: rewrites history. Coordinate with team.

## Clone with LFS

```bash
git clone url repo
# Pointers downloaded; LFS content fetched on checkout

# Skip LFS during clone (fast)
GIT_LFS_SKIP_SMUDGE=1 git clone url
# Later fetch on demand:
git lfs pull
```

## Selective Fetch

```bash
git lfs fetch --include="path/*.psd" --exclude="archived/*"
```

Only download specific files.

## When LFS

- Binary assets (images, videos, audio)
- ML models
- Game assets
- Design files

## When NOT

- Source code (Git handles fine)
- Small files
- Sensitive data (LFS storage often less protected than main repo)

## Alternative: Don't Commit Binaries

- Build artifacts: produce in CI, store in artifact registry
- Large assets: external storage (S3, etc.) referenced by URL

For source-only repos: don't need LFS.

## Submodule for Big Repo

Sometimes binaries live in separate repo (with LFS):
- main repo: code
- assets repo: binaries (with LFS)
- main has submodule reference

## CI Considerations

```yaml
- uses: actions/checkout@v4
  with:
    lfs: true                   # download LFS content
```

Default = pointers only.

## Operations

```bash
# Track new pattern
git lfs track "*.zip"
git add .gitattributes
git commit

# Check
git lfs status
git lfs ls-files

# Storage usage
git lfs ls-files --size

# Clean up old LFS
git lfs prune                   # remove unreferenced from local cache
```

## Common Mistakes

- **Forgot `git lfs install`**: pointers committed without LFS upload
- **Forgot to track pattern**: large file in normal Git → bloat
- **CI doesn't fetch LFS**: tests get pointer files, not content
- **Storage costs**: surprise bills

## Alternatives in 2025

For ML / data:
- **DVC** (Data Version Control): like LFS for data science
- **Pachyderm**: data versioning + pipelines
- **Cloudflare R2**: cheap storage, zero egress

For source repos: avoid LFS entirely if possible.

## Best Practices

- Run `git lfs install` once per machine and set up tracking patterns *before* the first commit of any large binary, so content is uploaded as LFS rather than baked into history.
- Commit `.gitattributes` (where the `filter=lfs` rules live) so every collaborator and CI runner treats the same patterns as LFS.
- Configure CI to fetch LFS content (`git lfs pull` / checkout with LFS) and consider `GIT_LFS_SKIP_SMUDGE=1` plus selective fetch for jobs that don't need the binaries.
- Migrate already-committed large files with `git lfs migrate import` (history rewrite) rather than just tracking them going forward, which leaves the bloat in history.
- Watch storage/bandwidth quotas — LFS billing is by storage and egress; prune or use cheaper backends (R2, self-hosted) if costs spike.
- Prefer not committing binaries at all (artifact registry, package manager, DVC for data) when the asset isn't truly part of source.

## Quick Refs

```bash
git lfs install                       # one-time per machine
git lfs track "*.psd"                 # adds rule to .gitattributes
git add .gitattributes                # commit the tracking rules!
git add design.psd && git commit -m "add asset"

# Inspect
git lfs ls-files                      # which files are in LFS
git lfs status
git lfs env                           # config + endpoint

# Migrate existing history into LFS
git lfs migrate import --include="*.psd" --everything

# Clone / fetch behavior
git lfs clone <url>                   # or normal clone (smudge fetches on checkout)
GIT_LFS_SKIP_SMUDGE=1 git clone <url> # pointers only (fast)
git lfs pull                          # fetch actual content later
git lfs fetch --include="assets/*"    # selective fetch
git lfs prune                         # remove old local LFS objects
```

| Symptom | Cause / fix |
|---------|-------------|
| Pointer text instead of file | content not fetched → `git lfs pull` |
| Repo huge despite LFS | files tracked too late → `git lfs migrate import` |
| CI sees pointers | enable LFS fetch in pipeline |

## Interview Prep

**Mid**: "What's Git LFS?"

**Senior**: "Migrate existing repo to LFS."

**Staff**: "LFS alternatives — when each?"

## Next Topic

→ [T05 — Worktrees](T05-Worktrees.md)
