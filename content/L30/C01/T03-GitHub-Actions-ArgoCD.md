# L30/C01/T03 — GitHub Actions + ArgoCD

## Learning Objectives

- Build CI/CD pipeline
- GitOps deploy

## Why This Split (CI Pushes Artifacts, CD Pulls State)

The core idea: **CI produces an immutable, signed artifact; CD reconciles the
cluster to a Git-declared desired state.** CI ends at "image pushed + manifest
updated." ArgoCD takes over from Git. Keeping them separate means CI never holds
cluster credentials (smaller blast radius), the deploy history lives in Git, and
a rollback is a `git revert` rather than a frantic re-run.

- **Separate app repo and deploy repo** — the app repo builds; the deploy repo
  declares what's running. CI commits a new image tag to the deploy repo, ArgoCD
  notices. One repo for both would have CI committing to itself in a loop and
  muddy the deploy history.
- **Manual gate to prod** — staging syncs automatically for fast feedback; prod
  requires a human (or a promotion PR) so a bad commit can't auto-roll to
  customers. Trade-off: a few minutes of latency for a lot of safety.

## Workflow

```
1. Push to feature branch
2. GitHub Actions:
   - Lint
   - Test
   - Build image
   - Scan
   - Push to registry
3. PR opened
4. Reviewed + merged
5. Merge to main triggers:
   - Build image (with main tag)
   - Update manifest in deploy repo
6. ArgoCD detects change
7. Syncs to staging
8. Smoke test
9. Manual promote to prod
```

## GitHub Actions

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
      - run: go test ./...

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_ROLE }}
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: REGISTRY/app:${{ github.sha }}
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: REGISTRY/app:${{ github.sha }}
          severity: CRITICAL,HIGH
          exit-code: 1
      - uses: sigstore/cosign-installer@v3
      - run: cosign sign --yes REGISTRY/app:${{ github.sha }}

  update-manifest:
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
        with:
          repository: org/deploy-repo
          token: ${{ secrets.DEPLOY_TOKEN }}
      - run: |
          yq -i ".image.tag = \"${{ github.sha }}\"" staging/values.yaml
          git commit -am "Deploy ${{ github.sha }}"
          git push
```

## ArgoCD App

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp-staging
spec:
  project: default
  source:
    repoURL: https://github.com/org/deploy-repo.git
    targetRevision: main
    path: staging/
  destination:
    server: https://staging-cluster.example.com
    namespace: app
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Prod Promotion

```yaml
# Manual via UI
# Or GitHub Actions step
- name: Promote to prod
  if: github.event.inputs.promote == 'true'
  run: |
    yq -i ".image.tag = \"${{ github.sha }}\"" prod/values.yaml
    git commit -am "Promote ${{ github.sha }} to prod"
    git push
```

## Rollback

```bash
# Revert commit; ArgoCD redeploys old
git revert HEAD
git push
```

## Best Practices

- GitOps
- Image scanning
- Signing
- Multi-env
- Manual prod gate

## Common Mistakes

- Direct kubectl from CI
- No signing
- No manual gate
- One repo (app + manifests)

## Acceptance Criteria

- A merge to `main` builds + scans + signs an image and commits the new tag to
  the deploy repo automatically
- ArgoCD syncs staging within ~1 minute and the new pod rolls out healthy
- Promotion to prod requires an explicit action (PR or workflow input)
- `git revert` of a deploy commit returns the app to the previous image, with
  ArgoCD doing the rollout — no `kubectl` involved

## Quick Refs

```
CI:  GitHub Actions  (test → scan → build → sign → push → bump tag)
CD:  ArgoCD (GitOps; pulls desired state from Git)
Repo: app + deploy-manifests (separate)
Promote: staging auto, prod manual
Rollback: git revert (ArgoCD reconciles)
```

## Interview Prep

**Junior**: "What's the difference between CI and CD in this design?" — CI
(GitHub Actions) tests and builds the image and pushes it to a registry. CD
(ArgoCD) takes the manifests from Git and makes the cluster match them. CI
produces the artifact; CD deploys it.

**Mid**: "Why does ArgoCD watch a separate repo instead of CI running `kubectl
apply`?" — So Git is the source of truth for what's deployed. ArgoCD
continuously reconciles, so it self-heals drift and the deploy history is just
the Git log. If CI ran `kubectl apply`, CI would need cluster-admin
credentials, there'd be no declarative record, and rollback would mean
re-running an old pipeline instead of reverting a commit.

**Senior**: "How do you do safe promotion and rollback across environments?" —
Staging auto-syncs for fast feedback; prod is gated behind a human-approved
promotion (a PR that bumps the prod image tag, or a manual workflow). Because
every deploy is a commit, rollback is `git revert` and ArgoCD reconciles to the
previous image — deterministic and fast. For higher-risk services I'd layer
Argo Rollouts for canary/blue-green so prod promotion is progressive rather than
all-at-once.

**Staff**: "A team wants to bypass the manual prod gate for velocity. How do you
respond?" — I'd reframe it as risk, not bureaucracy: the gate exists so a bad
commit can't auto-reach customers. The right answer to "we want speed" is
usually *better automated confidence*, not removing the gate — add canary
analysis (Argo Rollouts + metric checks) so prod promotion can be automatic
*because* it's automatically verified and auto-rolled-back on SLO regression.
That gives the velocity they want while keeping the safety the gate provided.
Removing the gate with nothing in its place trades a rare manual step for a
recurring outage class.

## Next Topic

→ [T04 — Observability Stack](T04-CICD-Observability.md)
