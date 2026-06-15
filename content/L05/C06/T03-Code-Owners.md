# L05/C06/T03 — Code Owners & Branch Protection

## Learning Objectives

- Use CODEOWNERS for review routing
- Configure branch protection

## CODEOWNERS

GitHub/GitLab feature: route PR reviews based on paths.

```
# .github/CODEOWNERS
*.md                            @docs-team
/services/payments/**            @payments-team
/services/auth/**                @auth-team @security-team
/.github/workflows/              @platform-team
/terraform/**                    @infra-team
```

When PR touches a path, listed owners auto-requested as reviewers.

## Patterns

```
*                               @everyone-default
*.js                            @js-team
/docs/                          @writers
/docs/api/                      @api-team       # more specific overrides above
```

Last matching rule wins (specific paths override broader).

## File Location

- `.github/CODEOWNERS` (root or .github/)
- `docs/CODEOWNERS`
- `CODEOWNERS` (root)

GitHub checks all; last wins for path.

## Required for Merge?

Configure branch protection to REQUIRE codeowner approval:
```
Settings → Branches → Protection rules
✓ Require review from Code Owners
```

Without this: CODEOWNERS just suggests reviewers.

## Branch Protection Rules

GitHub Settings → Branches → main:

```
✓ Require a pull request before merging
  ✓ Require approvals (2)
  ✓ Dismiss stale reviews
  ✓ Require review from Code Owners
✓ Require status checks (CI must pass)
  ✓ Require branches to be up to date
✓ Require conversation resolution
✓ Require signed commits
✓ Require linear history
✓ Do not allow bypassing the above
✗ Allow force pushes (NO)
✗ Allow deletions (NO)
```

## Status Checks

Define which CI jobs must pass:
```
✓ ci/build
✓ ci/test
✓ ci/lint
✓ security/scan
```

Without all green: can't merge.

## Required Up to Date

PR branch must be current with main before merge. Forces rebase/merge from main first.

Avoids: "tests passed when stale, broke main after merge."

## Linear History

Prohibits merge commits. PRs must squash or rebase.

```bash
git push --force-with-lease   # rewrite local branch after rebase
```

## Signed Commits

```bash
git config commit.gpgsign true
git config user.signingkey KEYID
```

Verifies author identity via GPG (or SSH signing, or Sigstore).

## Permission Granularity

Settings → Repositories → Roles:
- Read: clone, file issues
- Triage: manage issues + PRs
- Write: push to non-protected branches
- Maintain: most things
- Admin: everything

For sensitive repos: be restrictive.

## Team-Based Access

```
@org/team-name
```

Members of team have access. Manage at team level.

## Sample CODEOWNERS

```
# Default
*                                       @org/all-engineers

# Frontend
/apps/web/**                            @org/frontend-team
/apps/mobile/**                         @org/mobile-team

# Backend services
/services/*/                            @org/backend-team
/services/payments/**                   @org/payments-team
/services/auth/**                       @org/auth-team

# Infrastructure
/infrastructure/**                      @org/platform-team
/terraform/**                           @org/platform-team
/.github/workflows/**                   @org/platform-team

# Docs
/docs/**                                @org/docs-team

# Security-sensitive
/services/auth/passwords/**             @org/security-team @org/auth-team
```

Order matters; later overrides.

## Common Mistakes

- Too many codeowners per path (PRs blocked)
- One mega-team for everything (bottleneck)
- No codeowners (no automatic review routing)
- Codeowners but no required (just suggestions)

## Force Push Protection

```
✗ Allow force pushes
```

Critical for main branch. Once enabled: no rewrites.

## Branch Naming Convention

Some teams enforce via Action / hook:
```
feature/...  bugfix/...  hotfix/...  chore/...
```

Or per-user prefixes: `<author>/<description>`.

## Bypass

For emergencies: admin can override (but should be rare; tracked).

Settings → Branches → "Do not allow bypassing" prevents even admins.

## CI Required Checks Configuration

GitHub Actions auto-registers as status checks. To require:
- Add to required status checks list
- Branch protection enforces

## Operations

```bash
gh api repos/org/repo/branches/main/protection
```

Shows current protection config.

## Best Practices

- Keep CODEOWNERS entries minimal per path — assign the smallest team that can actually review, so PRs aren't blocked waiting on the wrong people.
- Pair CODEOWNERS with "Require review from Code Owners" in branch protection; otherwise the file only suggests reviewers and enforces nothing.
- Protect `main`/release branches with required status checks, required up-to-date branches, linear history (if you want it), and force-push + deletion disabled.
- Use teams (not individuals) in CODEOWNERS so ownership survives people changing roles, and order rules so the most specific path wins (last match applies).
- Require signed commits and dismiss stale approvals on new pushes for security-sensitive paths.
- Audit protection settings via the API/IaC (Terraform GitHub provider) so rules are version-controlled and consistent across repos.

## Quick Refs

```text
# .github/CODEOWNERS  (last matching pattern wins)
*                       @org/core
/frontend/              @org/web
/services/payments/**   @org/payments @org/security
*.tf                    @org/infra
/docs/                  @org/docs
```

```bash
# Inspect / set branch protection (gh CLI + API)
gh api repos/:owner/:repo/branches/main/protection      # view config

gh api -X PUT repos/:owner/:repo/branches/main/protection \
  -F required_pull_request_reviews.require_code_owner_reviews=true \
  -F required_pull_request_reviews.required_approving_review_count=2 \
  -F required_pull_request_reviews.dismiss_stale_reviews=true \
  -F required_status_checks.strict=true \
  -f required_status_checks.contexts[]='ci/build' \
  -F enforce_admins=true \
  -F required_linear_history=true \
  -F allow_force_pushes=false \
  -F allow_deletions=false \
  -F required_signatures=true
```

| Protection setting | Effect |
|--------------------|--------|
| Require CODEOWNERS review | routes + blocks on owning team |
| Strict status checks | branch must be up to date before merge |
| Linear history | no merge commits (rebase/squash only) |
| Block force push | history on protected branch is immutable |
| Require signatures | only verified commits merge |

## Interview Prep

**Mid**: "What's CODEOWNERS?"

**Senior**: "Branch protection — what to enable?"

**Staff**: "Compliance-driven access control."

## Next Topic

→ [T04 — Commit Signing (GPG, Sigstore)](T04-Commit-Signing.md)
