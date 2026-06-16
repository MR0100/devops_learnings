# L05/C06 — Git at Scale

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Monorepo-vs-Polyrepo.md) | Monorepo vs Polyrepo | 1 hr |
| [T02](T02-Monorepo-Tools.md) | Tools (Bazel, Nx, Turborepo, Pants) | 1 hr |
| [T03](T03-Code-Owners.md) | Code Owners & Branch Protection | 0.5 hr |
| [T04](T04-Commit-Signing.md) | Commit Signing (GPG, Sigstore) | 0.5 hr |

## Monorepo vs Polyrepo

| | Monorepo | Polyrepo |
|---|---|---|
| Repos | One huge | Many smaller |
| Cross-cutting changes | Atomic commit | Multi-PR coordination |
| Code reuse | Direct import | Versioned packages |
| Tooling investment | High | Low |
| CI complexity | Sophisticated (selective builds) | Per-repo simple |
| Onboarding | Heavy initial | Easy per-repo |
| Examples | Google, Meta, Microsoft, Uber | Most startups, many companies |

### Why Monorepo at FAANG
- Atomic refactors across hundreds of services
- One source of truth for shared libs
- Single CI/CD platform investment
- Visibility of all code

### Why Polyrepo
- Team autonomy
- Limited blast radius
- Less tooling investment

### Hybrid
Many companies have ~5–10 large "repo groups": platform repo, frontend repo, ML repo, mobile repo, etc. Not one monorepo but not 1000 either.

## Monorepo Tools

### Bazel
Google's open-source build system. Build a target by deriving its complete dep graph; only rebuild what changed.

- Hermetic builds
- Remote cache + remote execution
- Polyglot (Go, Java, Python, C++, TS, Rust, etc.)
- Steep learning curve

### Buck2 (Meta)
Modern rewrite of Buck. Rust-based. Similar goals to Bazel.

### Pants
Python-friendly Bazel competitor.

### Nx / Turborepo
JS/TS-focused. Faster local DX than Bazel for typical web monorepos.

### Selective CI Triggers

A monorepo CI runs only what's affected:
```yaml
on:
  push:
    paths:
    - 'services/payments/**'
    - 'libs/shared/**'
```

Or use Bazel/Nx target queries:
```bash
bazel query 'rdeps(//..., //libs/shared:lib)'   # what depends on shared:lib
```

## CODEOWNERS

GitHub's mechanism for per-path ownership.

```
# .github/CODEOWNERS
*.md                        @docs-team
/services/payments/**       @payments-team
/services/auth/**           @auth-team @security-team
/.github/workflows/         @platform-team
```

When a PR touches a path, owners are auto-requested as reviewers.

## Branch Protection

In GitHub/GitLab:
- Require PR reviews (N approvals)
- Require CI checks to pass
- Require up-to-date branch
- Restrict force pushes
- Require signed commits
- Require linear history (no merge commits)
- Restrict who can push

```bash
gh api repos/org/repo/branches/main/protection -X PUT --input - <<EOF
{
  "required_status_checks": {"strict": true, "contexts": ["ci/build", "ci/test"]},
  "required_pull_request_reviews": {"required_approving_review_count": 2},
  "enforce_admins": true,
  "restrictions": null
}
EOF
```

## Commit Signing

Verify that a commit was authored by who it claims.

### GPG
```bash
gpg --gen-key
git config --global user.signingkey <KEY-ID>
git config --global commit.gpgsign true
# Upload public key to GitHub/GitLab
```

Commits show "Verified" badge.

### SSH Signing (modern)
```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true
```

### Sigstore (Gitsign)
Keyless signing via OIDC.

```bash
gitsign --version
git config --global commit.gpgsign true
git config --global gpg.format x509
# Sign via OIDC of your identity (GitHub, Google, etc.)
```

No long-lived keys. Verification via Sigstore's Rekor transparency log.

## Cosign / SLSA Tie-In

Commit signing is the first step in supply-chain integrity:
1. Commit signed → who wrote it?
2. Build provenance → what built it?
3. Image signed → did it come from the build?
4. Verify at deploy → only signed images deployed

## Interview Themes

- "Compare monorepo vs polyrepo"
- "How would you organize a 5-team org's repos?"
- "What's CODEOWNERS for?"
- "Why sign commits? What's Sigstore?"
- "How does Bazel scale CI in a monorepo?"
