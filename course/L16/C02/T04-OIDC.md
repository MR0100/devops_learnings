# L16/C02/T04 — OIDC for Cloud Deploys

## Learning Objectives

- Configure OIDC
- Stop using static cloud keys

## Why OIDC

Without OIDC:
- Store cloud secrets in GitHub
- Rotate manually
- Leak risk

With OIDC:
- Short-lived tokens
- No static secrets
- Per-workflow scope

## How

```
GitHub Actions
   ↓ requests OIDC token
   ↓ token has claims (repo, branch, etc.)
Cloud
   ↓ verifies token
   ↓ issues temp credentials
GitHub uses temp creds
```

## Setup AWS

```bash
# Create OIDC provider in AWS IAM
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

Create role with trust policy:
```json
{
  "Effect": "Allow",
  "Principal": {
    "Federated": "arn:aws:iam::ACCT:oidc-provider/token.actions.githubusercontent.com"
  },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
    },
    "StringLike": {
      "token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:ref:refs/heads/main"
    }
  }
}
```

## Use in Workflow

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::ACCT:role/GitHubActionsRole
          aws-region: us-east-1
      - run: aws s3 ls
```

`id-token: write`: enables OIDC token.

## GCP

```bash
gcloud iam workload-identity-pools create my-pool --location=global
gcloud iam workload-identity-pools providers create-oidc github \
  --workload-identity-pool=my-pool \
  --location=global \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository"
```

Bind SA:
```bash
gcloud iam service-accounts add-iam-policy-binding \
  my-sa@PROJ.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/PROJ_NUM/locations/global/workloadIdentityPools/my-pool/attribute.repository/myorg/myrepo"
```

Workflow:
```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: projects/PROJ_NUM/locations/global/workloadIdentityPools/my-pool/providers/github
    service_account: my-sa@PROJ.iam.gserviceaccount.com
```

## Azure

Configure federated credential:
```bash
az ad app federated-credential create \
  --id APP_ID \
  --parameters '{
    "name": "github",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:myorg/myrepo:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

Workflow:
```yaml
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

(IDs are public; not secrets technically.)

## Subject Claims

GitHub subject format:
```
repo:OWNER/REPO:ref:refs/heads/BRANCH
repo:OWNER/REPO:ref:refs/tags/TAG
repo:OWNER/REPO:environment:ENVIRONMENT
repo:OWNER/REPO:pull_request
```

Scope to specific.

## Environment-Based

```yaml
jobs:
  deploy:
    environment: production
    permissions:
      id-token: write
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::ACCT:role/Prod-Deploy
```

Trust policy:
```json
"sub": "repo:myorg/myrepo:environment:production"
```

For: env-scoped roles.

## Multiple Environments

Per environment, separate role:
```
GitHub-Dev-Role: trust dev environment
GitHub-Staging-Role: trust staging
GitHub-Prod-Role: trust production
```

Workflow picks based on env.

## Token Inspection

```yaml
- run: |
    curl -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
      "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=test" | jq
```

For: debug.

## Audience

For specific audience:
```bash
"$ACTIONS_ID_TOKEN_REQUEST_URL&audience=https://my-app.example.com"
```

Cloud verifies audience matches expected.

## Pros

- No static secrets
- Auto-rotated (per workflow)
- Scope per repo/branch/env
- Audit (CloudTrail / Logs)

## Limitations

- Setup more complex
- Per-cloud different
- Public repos: fork PRs need extra care

## Fork PRs

By default, forks can't access secrets / OIDC.

Mitigation:
- Use pull_request_target carefully
- Or limit workflows on forks

## Multi-Cloud Workflow

```yaml
jobs:
  deploy:
    permissions:
      id-token: write
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.AWS_ROLE }}

      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ vars.GCP_WIF }}
          service_account: ${{ vars.GCP_SA }}

      - uses: azure/login@v2
        with: ...
```

Sequential or parallel.

## Best Practices

- OIDC over static keys
- Scope tightly (repo + branch + env)
- Per-env roles
- Audit cloud logs
- Document trust policies
- Test before removing static keys

## Common Mistakes

- Wildcard `sub` (any branch)
- One role for all envs (lateral movement)
- Forget `id-token: write` (token won't be issued)
- Don't audit (lose trail)

## Migrate

1. Set up OIDC + role
2. Test in non-prod
3. Workflow uses OIDC
4. Remove static keys
5. Audit cloud for unused IAM users

## Quick Refs

```yaml
permissions:
  id-token: write
  contents: read

# AWS
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::ACCT:role/ROLE

# GCP
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ...
    service_account: ...

# Azure
- uses: azure/login@v2
  with:
    client-id: ...
    tenant-id: ...
```

## Interview Prep

**Mid**: "What's OIDC."

**Senior**: "OIDC for CI."

**Staff**: "Multi-cloud CI auth."

## Next Topic

→ [T05 — Secrets, Environments, Approvals](T05-Secrets-Environments-Approvals.md)
