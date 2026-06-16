# L16/C02/T05 — Secrets, Environments, Approvals

## Learning Objectives

- Manage secrets in Actions
- Use environments + approvals

## Secrets

Encrypted; per repo / org / environment:
```yaml
- run: ./script
  env:
    API_KEY: ${{ secrets.API_KEY }}
```

## Secret Levels

### Repo Secrets
Single repo. Best for repo-specific.

### Org Secrets
All repos in org. Or selected.
For: org-wide creds.

### Environment Secrets
Per environment (production, staging).
For: env-specific.

## Variables (Non-Secret)

```yaml
- run: deploy.sh
  env:
    REGION: ${{ vars.AWS_REGION }}
```

Plain text; visible. For: config.

## Environments

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://prod.example.com
    runs-on: ubuntu-latest
    steps: [...]
```

Config in repo settings:
- Required reviewers
- Wait timer
- Deployment branches
- Environment secrets

## Required Reviewers

Production env:
- 1+ approvers required
- Job pauses until approved
- Cannot be approved by PR author

For: gate prod deploys.

## Wait Timer

```
Environment: production
Wait timer: 5 minutes
```

After approval, 5 min before deploy. For: change announcement.

## Branch Restrictions

```
Environment: production
Deployment branches: main, release/*
```

Only specified branches deploy to env.

## Environment URL

```yaml
environment:
  name: production
  url: https://prod.example.com
```

Shows link in UI.

## Secret Best Practices

- Never echo secrets (masked but careful)
- Limit scope (env-specific)
- Rotate regularly
- Use OIDC where possible
- Audit access

## Mask Detection

```yaml
- run: |
    SECRET=$(some-cmd)
    echo "::add-mask::$SECRET"
```

Mask dynamically-fetched.

## Secret in PR

PRs from same repo: have access.
PRs from forks: NO access.

For security: secrets don't leak via fork PRs.

## Workflow Permissions

Default token (GITHUB_TOKEN):
```yaml
permissions:
  contents: read
  pull-requests: write
  id-token: write
```

Limit scope.

## Default GITHUB_TOKEN

Available to all workflows:
```yaml
- run: gh pr comment ${{ github.event.pull_request.number }} -b "Comment"
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Scoped to repo; auto-rotated.

## Job Token

For complex workflows: different scopes per job.

```yaml
jobs:
  build:
    permissions:
      contents: read
  publish:
    permissions:
      contents: read
      packages: write
```

## Concurrency

```yaml
concurrency:
  group: deploy-${{ github.ref }}-${{ github.event.inputs.environment }}
  cancel-in-progress: false
```

Prevent concurrent deploys.

## Deployment Protection Rules

GitHub:
- Required reviewers
- Wait timer
- Custom rules (custom apps)

For: customize gating.

## Custom Deployment Rules (GitHub Apps)

Build custom logic:
- Check service health
- Validate ticket
- Verify on-call

GitHub Apps query during pending deploy.

## Secrets in Composite Action

Composite actions inherit caller's secrets:
```yaml
# In composite action
- run: echo $MY_SECRET   # access caller's
  env:
    MY_SECRET: ${{ inputs.secret }}
```

But: passing as input is plaintext (less secure). Use `${{ secrets.X }}` in caller.

## Reusable Workflow Secrets

```yaml
# reusable.yml
on:
  workflow_call:
    secrets:
      DEPLOY_KEY:
        required: true
```

```yaml
# Caller
uses: ./.github/workflows/reusable.yml
secrets:
  DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
# Or
secrets: inherit   # pass all
```

## Audit

GitHub:
- Audit log (org level)
- Workflow runs history
- Secret access not directly visible

For: ops review.

## Secret Rotation

```
1. Generate new secret
2. Update in GitHub
3. Old secret no longer used
4. Revoke old
```

Automated: via API + scripts.

## External Secret Stores

For sensitive:
- Vault
- AWS Secrets Manager
- Azure Key Vault

```yaml
- name: Get Vault secret
  uses: hashicorp/vault-action@v3
  with:
    url: https://vault.example.com
    method: jwt
    role: github-actions
    secrets: secret/data/myapp api_key | API_KEY
```

OIDC to Vault; pull secret at runtime.

For: tight control.

## Environments + OIDC

```yaml
jobs:
  deploy-prod:
    environment: production
    permissions:
      id-token: write
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::PROD_ACCT:role/Prod-Deploy
```

Trust policy scoped:
```
"sub": "repo:org/repo:environment:production"
```

For: prod role can only be assumed from production env workflow.

## Audit Trail

```yaml
- run: |
    echo "Deployed by: ${{ github.actor }}"
    echo "Approved by: ${{ github.event.review.user.login }}"
    echo "Commit: ${{ github.sha }}"
```

Log for traceability.

## Notifications

```yaml
- if: success() && contains(github.event_name, 'workflow_dispatch')
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Deployed to ${{ inputs.env }} by ${{ github.actor }}"
      }
```

For: visibility.

## Best Practices

- Environment-scoped secrets
- Required reviewers prod
- OIDC over static
- Vault for sensitive
- Audit regularly
- Rotate keys
- Branch restrictions per env

## Common Mistakes

- Org secrets too broad
- No required reviewers
- Static cloud keys
- Secrets in logs (no masking)
- Wide GITHUB_TOKEN permissions

## Quick Refs

```yaml
# Secret use
${{ secrets.NAME }}

# Variable
${{ vars.NAME }}

# Environment
environment:
  name: production
  url: ...

# Permissions
permissions:
  contents: read
  id-token: write
```

## Interview Prep

**Mid**: "GitHub Actions secrets."

**Senior**: "Environment protection."

**Staff**: "CI secret management."

## Next Topic

→ Move to [L16/C03 — GitLab CI](../C03/README.md)
