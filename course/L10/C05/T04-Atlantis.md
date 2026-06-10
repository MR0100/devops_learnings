# L10/C05/T04 — Atlantis for PR-Driven Workflows

## Learning Objectives

- Use Atlantis for GitOps Terraform
- Configure for team workflow

## Atlantis

PR-driven Terraform automation:
- PR opened → atlantis plan
- Comments in PR show plan
- Approve → atlantis apply
- Merge

For: team collaboration with safety.

## Install

```bash
# Standalone
docker run runatlantis/atlantis:latest

# Helm in K8s
helm install atlantis runatlantis/atlantis \
  --set github.token=$GH_TOKEN \
  --set github.user=atlantis-bot \
  --set github.webhook.secret=$WEBHOOK
```

## Webhook

GitHub webhook → Atlantis:
- PR events
- Comment events

Atlantis processes.

## Workflow

1. Engineer opens PR
2. Atlantis auto-runs `terraform plan`
3. Plan output posted to PR
4. Reviewers see exact changes
5. Approve PR
6. Comment `atlantis apply`
7. Atlantis runs `terraform apply`
8. PR merged

For: review before apply.

## Configuration

`atlantis.yaml` in repo:
```yaml
version: 3
projects:
- name: prod-vpc
  dir: live/prod/us-east-1/vpc
  workspace: default
  autoplan:
    when_modified: ["*.tf", "*.tfvars"]
    enabled: true
  workflow: prod

- name: dev-vpc
  dir: live/dev/vpc
  workflow: dev

workflows:
  prod:
    plan:
      steps:
      - init
      - plan
    apply:
      steps:
      - apply
  dev:
    plan:
      steps:
      - init
      - plan
```

Per-project config.

## Auto-Plan

```yaml
autoplan:
  when_modified: ["*.tf"]
  enabled: true
```

PR change to .tf → plan auto-runs.

## Apply Approval

```yaml
apply_requirements: [approved, mergeable]
```

Plan must be:
- Approved (PR review)
- Mergeable (no conflicts)

Before apply.

## Commands

In PR comment:
- `atlantis plan` — re-plan
- `atlantis apply` — apply specific project
- `atlantis apply -p prod-vpc` — specific
- `atlantis unlock` — release lock
- `atlantis help`

## Locks

Per-project locks:
- One PR planning → others wait
- Prevents concurrent applies to same state

Released on:
- Apply
- PR close
- Manual unlock

## Multi-Repo / Single-Repo

Single repo: one atlantis.yaml; many projects.
Multi-repo: per-repo config.

## Workflows

Customize:
```yaml
workflows:
  prod:
    plan:
      steps:
      - run: terraform-docs markdown table . > README.md
      - init
      - plan
    apply:
      steps:
      - run: ./pre-apply-check.sh
      - apply
      - run: ./notify-slack.sh
```

Custom commands; hooks.

## Webhook Secret

```bash
WEBHOOK_SECRET=$(openssl rand -hex 32)
```

In GitHub webhook + Atlantis env. Validates events.

## Auth

Atlantis as GitHub App:
- Install on repos
- Restricted permissions
- Per-org

Or PAT (less secure).

## Per-Environment

```yaml
- name: prod
  dir: live/prod
  workflow: prod
  apply_requirements: [approved, mergeable]

- name: dev
  dir: live/dev
  workflow: dev
  apply_requirements: []   # auto-apply OK
```

Different requirements per env.

## Slack Integration

```yaml
workflows:
  prod:
    apply:
      steps:
      - apply
      - run: |
          curl -X POST $SLACK_WEBHOOK -d "{
            \"text\": \"Applied $PROJECT_NAME\"
          }"
```

For: notifications.

## Plan Cache

Atlantis caches plans per PR. Apply uses saved plan.

For: ensure apply matches reviewed plan.

## Terraform Cloud Alternative

TFC built-in PR-driven workflow:
- VCS integration
- Auto-plan on PR
- Manual / auto-apply on merge

For TFC users: less Atlantis.

For: open source: Atlantis.

## Spacelift / Env0

Hosted alternatives:
- Spacelift
- env0
- Scalr

Paid; more features.

## When Atlantis

- Self-hosted preferred
- Open source
- Standard PR workflow

## When NOT

- Single developer
- Simple infrastructure
- TFC available

## Best Practices

- atlantis.yaml in repo (version-controlled)
- apply_requirements for prod
- Separate workflows per env
- Webhooks secret
- Restrict who can apply (GitHub team)
- Document commands in repo README
- Logs / metrics

## Common Mistakes

- No apply_requirements (anyone applies)
- Wide GitHub permissions
- Forgot lock cleanup
- Plan / apply mismatch (config changed)

## Security

- Atlantis pod has Terraform's permissions (provider creds)
- Restrict cluster access
- Audit logs
- Use OIDC for cloud access

For: principle of least privilege.

## Scaling

For huge orgs:
- Multiple Atlantis instances
- Per-team
- Or HA Atlantis

Default: single pod.

## Multi-User

Multiple PRs same time:
- Different projects: parallel
- Same project: locked; sequential

For: avoid conflicts.

## Reporting

Slack / Datadog metrics:
- Plans per day
- Apply success rate
- Common failures

For: improvement.

## PR Stack

For multi-module changes:
- Per-project plans
- Per-project applies
- Or stack-apply (newer feature)

For: coordinated changes.

## Anti-Patterns

- Bypass Atlantis (direct apply)
- All workflows same
- No backup state (manual apply if issue)
- Atlantis is single point

## Quick Refs

```bash
# Setup
docker run -p 4141:4141 \
  -e ATLANTIS_GH_USER=bot \
  -e ATLANTIS_GH_TOKEN=$TOKEN \
  -e ATLANTIS_REPO_ALLOWLIST=github.com/myorg/* \
  runatlantis/atlantis server

# In PR
# atlantis plan
# atlantis apply
# atlantis apply -p PROJECT
# atlantis unlock
```

## Interview Prep

**Mid**: "Atlantis purpose."

**Senior**: "PR-driven Terraform."

**Staff**: "Self-service Terraform for 50 teams."

## Next Topic

→ Move to [L10/C06 — Writing Custom Providers](../C06/README.md)
