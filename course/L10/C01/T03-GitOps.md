# L10/C01/T03 — GitOps for Infrastructure

## Learning Objectives

- Apply GitOps for infra
- Use Atlantis / Terraform Cloud / Argo

## GitOps

Git as source of truth. Infrastructure / app config in repo. Continuous reconciliation.

Principles (Weaveworks):
1. Declarative
2. Versioned + immutable
3. Pulled automatically (agent)
4. Continuously reconciled

## For Infrastructure

Code in Git:
```
infra/
├── prod/
│   ├── vpc.tf
│   ├── eks.tf
│   └── rds.tf
├── staging/
└── modules/
```

PR: change → review → merge → apply.

## Workflow

1. Engineer opens PR with change
2. CI runs `terraform plan`
3. Plan output in PR
4. Reviewers see exact change
5. Approve + merge
6. CD runs `terraform apply`
7. State updated

No manual `terraform apply` from laptop.

## Tools

### Atlantis
PR-driven Terraform:
- Commenter on PR: `atlantis plan`
- Plan output back
- `atlantis apply` after approval
- Lockfile prevents concurrent

```yaml
# atlantis.yaml
version: 3
projects:
  - dir: prod/vpc
    workspace: default
    autoplan:
      when_modified: [.tf]
```

### Terraform Cloud / HCP Terraform
HashiCorp's hosted:
- VCS integration
- Run plans
- Apply on approval
- State management
- Variable sets
- Sentinel policies

### Spacelift
Similar; with policy-as-code.

### env0
Hosted Terraform/Pulumi.

### GitHub Actions / GitLab CI
Roll your own:
```yaml
on: [pull_request]
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - terraform plan -out=plan.tfplan
      - upload plan.tfplan
      - comment on PR with plan summary
```

For apply: manual approval + workflow.

## Argo CD / Flux (Kubernetes)

K8s GitOps:
- Watch Git repo
- Sync manifests to cluster
- Reconcile drift
- Health status

For K8s app + config: Argo CD or Flux standard.

## GitOps vs CI/CD

GitOps is CI/CD for infra/K8s.

Traditional CI/CD:
- Code → CI → CD pushes to env

GitOps:
- Code → Git → agent in env pulls → applies

Pull > push:
- Cluster doesn't need outbound creds
- Multi-env easier (cluster watches its branch / dir)

## Benefits

- Audit trail (Git history)
- Rollback (revert PR)
- Review (PR process)
- Multi-environment via branches / dirs
- Drift detection (reconciliation)
- Disaster recovery (Git → cluster)

## Patterns

### Single Repo
All infra in one repo:
- /prod/...
- /staging/...
- /dev/...

Simple. Coupled.

### Repo per Env
- prod-infra
- staging-infra
- dev-infra

More isolation. PR labels which env.

### Repo per Team
Each team owns infra repo.

### Mixed
Shared modules + per-team repos for app-specific.

## Promotion

```
dev → staging → prod
```

PR in dev tested; merged to staging branch; tested; merged to prod.

Or separate dirs same repo:
- Same change applied to dev dir
- Tested
- Applied to staging dir
- Tested
- Applied to prod dir

## Sensitive Data

Don't commit:
- Secrets
- API keys

Use:
- Sealed Secrets / SOPS (encrypted in Git)
- External Secrets Operator (fetch from Vault / Secrets Manager)

## Image Promotion

For K8s app:
- CI builds image; pushes
- Updates manifest in Git (Kustomize / Helm values)
- Argo CD syncs to cluster
- Deploy complete

```yaml
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp:v1.2.3   # bumped by CI
```

## Drift Detection

GitOps agent continuously reconciles:
- Manual cluster change → agent reverts
- True source of truth = Git

Terraform: doesn't continuously reconcile by default. Periodic plan in CI.

For K8s: Argo CD reconciles every few min.

## Trade-offs

Pros:
- Auditable
- Reproducible
- Reversible
- Reviewed

Cons:
- Setup overhead
- Slower for emergencies (Git → review → apply)
- All-or-nothing reverts
- Learning curve

## Emergency Breaks

For tier-0 incident:
- Break glass: manual change (justified, audited)
- Then PR catching up the change to Git

Documented exception process.

## State Visibility

Where's the real state?
- Git: desired
- Cloud: actual
- Agent: reconciling

Dashboard for divergences:
- Argo CD UI: sync status
- Terraform Cloud: drift detect

## Common Mistakes

- Bypassing GitOps for "quick fixes" (creates drift)
- Per-env branches with diverged code (merge nightmare)
- Secrets in plain Git
- No drift alerts

## Best Practices

- One source of truth (Git)
- PR for all changes
- Plan in PR
- Approval gates
- Secrets externalized
- Drift detection
- Documented break-glass
- Branch protection
- CI tests changes before merge

## Plan in PR

Critical: plan output visible in PR:
```
Plan: 2 to add, 1 to change, 0 to destroy.

  + aws_s3_bucket.new
  ~ aws_iam_policy.app
```

Reviewer evaluates before approve.

## Apply Approval

After merge: apply may auto-trigger or require manual approval (especially prod).

For:
- Prod: human approval
- Dev: auto

## Policy as Code

Sentinel (HCP Terraform), OPA (Atlantis), Conftest:
- Block PRs violating policy
- "No 0.0.0.0/0 in SG"
- "Encrypt all volumes"

Codified guardrails.

## Multi-Cluster K8s

Argo CD can manage many clusters from one control plane.

For: dozens of clusters; central policy.

## Cost

Mostly: time + Git infra.

Terraform Cloud: paid tiers for teams.
Atlantis: self-host (free).
Argo CD: free.

## Quick Refs

Terraform GitOps via Atlantis:
```bash
# In PR
atlantis plan
# Review output
atlantis apply
```

Argo CD:
```bash
argocd app create myApp --repo https://... --path manifests/ --dest-server https://kubernetes.default.svc
argocd app sync myApp
```

## Interview Prep

**Mid**: "GitOps benefits."

**Senior**: "Argo CD architecture."

**Staff**: "GitOps for 100 microservices."

## Next Topic

→ Move to [L10/C02 — Terraform Fundamentals](../C02/README.md)
