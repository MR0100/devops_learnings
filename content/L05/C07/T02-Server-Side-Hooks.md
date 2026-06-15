# L05/C07/T02 — Server-Side Hooks

## Learning Objectives

- Use server-side hooks for enforcement
- Compare to client-side
- Implement on GitHub via Actions

## Server-Side Hooks

Run on the Git server. Cannot be bypassed by client (unlike client hooks).

```
.git/hooks/  (on server)
├── pre-receive       # before any ref updates
├── update            # per ref during push
└── post-receive      # after push complete
```

## pre-receive

Runs once per push. Can reject the whole push.

```bash
#!/bin/bash
# pre-receive on server
while read old_sha new_sha ref; do
    # Check each commit
    for sha in $(git rev-list "$old_sha..$new_sha"); do
        if git log --format=%s -1 "$sha" | grep -qi "WIP"; then
            echo "Reject: commit message has WIP"
            exit 1
        fi
    done
done
```

## update

Runs per ref. Can reject just one branch's push.

```bash
#!/bin/bash
# update on server
ref="$1" old="$2" new="$3"

if [[ "$ref" == "refs/heads/main" ]]; then
    # Extra checks for main
    if [[ "$old" != "$(git merge-base "$old" "$new")" ]]; then
        echo "Non-fast-forward push to main rejected"
        exit 1
    fi
fi
```

## post-receive

Runs after push complete. Use for notifications, triggering CI/CD.

```bash
#!/bin/bash
# post-receive
while read old new ref; do
    if [[ "$ref" == "refs/heads/main" ]]; then
        curl -X POST https://ci.example.com/trigger -d "ref=$ref&sha=$new"
    fi
done
```

## Self-Hosted Git (Gitea, Gitolite)

Direct access to `.git/hooks/` on server. Configure as desired.

## GitHub / GitLab / Bitbucket

Hosted services don't expose server hooks directly. Use:

### Branch Protection Rules
- Required reviews
- Required status checks
- Restrict who can push
- Require signed commits

### GitHub Apps
- Custom logic via API
- React to webhooks
- Update commit status

### Actions / Workflows
- CI as gate
- Required checks block merge

### Required Workflows (Org-Level)
```yaml
# Organization-required workflow runs on every repo's PR
```

## Custom Policy Enforcement

For GitHub:

```yaml
# .github/workflows/policy.yml
on: pull_request

jobs:
  policy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Check no commits without sign-off
        run: |
          for sha in $(git log --format=%H origin/main..HEAD); do
            if ! git log -1 --format=%B "$sha" | grep -q 'Signed-off-by'; then
              echo "Commit $sha missing Signed-off-by"
              exit 1
            fi
          done
```

PR fails if policy violated → can't merge.

## Common Server-Side Policies

- No force push to main
- Commit message format (conventional)
- File size limits
- No secrets (regex scan)
- Required CODEOWNERS approval
- Signed commits required
- CI must pass

## What Client Hooks Cannot Do

- Enforce on stubborn users (`--no-verify`)
- Enforce on new clones (hooks not shared)
- Block forced pushes
- Gate merges

Server-side is the source of truth.

## What Both Should Do

Best practice: implement same checks on both:
- Client: fast feedback (catch early)
- Server: enforcement

Same tools in both places (pre-commit framework helps).

## Mirroring Hooks Logic

```bash
# Pre-commit (client)
make lint

# CI (server-enforced)
- run: make lint
```

Same command; consistent behavior.

## GitLab CI Equivalent

```yaml
# .gitlab-ci.yml
stages: [lint, test]
lint:
  stage: lint
  script:
    - pre-commit run --all-files
```

Blocks merge if not passing.

## Pre-Push to Distinguish

Client `pre-push` differs from server `pre-receive`:
- Client: prevent bad push from leaving (saves embarrassment)
- Server: refuse if bad push arrives (enforcement)

## Operations on GitHub

```bash
# Branch protection via API
gh api repos/org/repo/branches/main/protection -X PUT --input - <<EOF
{
  "required_status_checks": {"strict": true, "contexts": ["ci/test"]},
  "required_pull_request_reviews": {"required_approving_review_count": 2},
  "enforce_admins": true
}
EOF
```

## Limits

GitHub doesn't let you stop a `git push --force` to a protected branch unless you enable "prevent force pushes" in protection rules.

## Compliance

For SOX / SOC2:
- Approval workflows enforced (branch protection)
- Cannot bypass (admin override tracked)
- Audit log via GitHub audit log

## Common Mistakes

- Confusing the three server hooks: `pre-receive` runs once for the whole push (atomic reject all), `update` runs per ref, `post-receive` runs after the push is accepted (can't reject).
- Trying to reject a push from `post-receive` — by then the refs are already updated; rejection must happen in `pre-receive`/`update`.
- Assuming hosted Git (GitHub/GitLab/Bitbucket) lets you drop in custom server hooks — you generally can't; you enforce via branch protection, required checks, rulesets, or CI instead.
- Reading only `stdin` ref lines in `pre-receive` but forgetting that a single push can update many refs, so partial handling lets bad refs through.
- Putting heavy work (full builds) in `post-receive` synchronously, blocking the pusher; dispatch to a queue/CI instead.
- Treating server hooks as a substitute for CI; they're a gate, but deep validation belongs in pipelines that can report status back.

## Best Practices

- Use `pre-receive`/`update` for hard policy (protected refs, no force-push, required commit format, secret scanning) since they can atomically reject the push.
- On hosted platforms, express policy through branch protection / rulesets and required status checks — that's the supported, auditable enforcement path.
- Keep rejection messages actionable: print exactly which ref/commit failed and how to fix it, so contributors aren't left guessing.
- Make `post-receive` fast and asynchronous — trigger CI, deploys, or notifications by enqueuing work, not by doing it inline.
- Mirror server policy as fast client hooks (pre-commit/pre-push) so developers get feedback before the rejected push, but never rely on the client side for enforcement.
- For compliance (SOC2/SOX), enforce required reviews and disallow admin bypass, and rely on the platform audit log for evidence.

## Quick Refs

```bash
# --- Self-hosted server hooks (in the bare repo's hooks/) ---
# pre-receive: reject the ENTIRE push atomically; reads refs on stdin
#   while read old new ref; do ... exit 1 to reject ...; done
# update:      runs per-ref (args: refname old new); reject a single ref
# post-receive: runs after acceptance; cannot reject (notify/deploy)

# Example pre-receive: block force-push to main
# while read old new ref; do
#   if [ "$ref" = refs/heads/main ] && [ "$old" != 000... ] &&
#      ! git merge-base --is-ancestor "$old" "$new"; then
#        echo "Force-push to main blocked"; exit 1
#   fi
# done

# --- Hosted equivalents (no custom server hooks) ---
# GitHub branch protection / rulesets:
gh api -X PUT repos/:owner/:repo/branches/main/protection \
  -F required_status_checks.strict=true \
  -F enforce_admins=true \
  -F allow_force_pushes=false
# GitLab: Settings → Repository → Protected branches + Push rules
# Bitbucket: Branch permissions + merge checks
```

| Hook | Scope | Can reject? | Use |
|------|-------|-------------|-----|
| `pre-receive` | whole push | yes (all-or-nothing) | global policy, secret scan |
| `update` | per ref | yes (that ref) | per-branch rules |
| `post-receive` | after accept | no | CI trigger, deploy, notify |

## Interview Prep

**Mid**: "Client vs server hooks."

**Senior**: "Enforce policy on GitHub."

**Staff**: "Compliance-driven Git policy."

## Next Topic

→ [T03 — pre-commit Framework](T03-Pre-Commit-Framework.md)
