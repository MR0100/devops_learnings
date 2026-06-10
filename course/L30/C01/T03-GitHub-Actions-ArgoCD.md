# L30/C01/T03 — GitHub Actions + ArgoCD

## Learning Objectives

- Build CI/CD pipeline
- GitOps deploy

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

## Quick Refs

```
CI:  GitHub Actions
CD:  ArgoCD (GitOps)
Repo: app + deploy-manifests (separate)
Promote: manual via PR
```

## Next Topic

→ [T04 — Observability Stack](T04-CICD-Observability.md)
