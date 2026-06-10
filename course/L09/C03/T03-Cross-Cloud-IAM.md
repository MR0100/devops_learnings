# L09/C03/T03 — Cross-Cloud IAM Federation

## Learning Objectives

- Federate identities across clouds
- Avoid static credentials

## Goal

App in AWS needs to read from GCS bucket. Or:

GitHub Actions deploys to AWS + GCP + Azure.

Without static keys.

## OIDC Foundation

OIDC tokens prove identity:
- Issuer (e.g. GitHub)
- Subject (e.g. repo)
- Audience (target service)

Each cloud trusts an issuer; exchanges OIDC → cloud credential.

## GitHub Actions → AWS

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::ACCT:role/GitHubActionsRole
    aws-region: us-east-1
```

AWS IAM Role trust policy:
```json
{
  "Effect": "Allow",
  "Principal": {"Federated": "arn:aws:iam::ACCT:oidc-provider/token.actions.githubusercontent.com"},
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:sub": "repo:org/repo:ref:refs/heads/main"
    }
  }
}
```

GitHub → AWS. No keys.

## GitHub Actions → GCP

```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: projects/PROJ_NUM/locations/global/workloadIdentityPools/POOL/providers/PROVIDER
    service_account: my-sa@PROJ.iam.gserviceaccount.com
```

Workload Identity Federation (WIF):
```bash
gcloud iam workload-identity-pools create my-pool
gcloud iam workload-identity-pools providers create-oidc github \
  --workload-identity-pool=my-pool \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor"

# Bind SA
gcloud iam service-accounts add-iam-policy-binding my-sa@PROJ.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/PROJ_NUM/locations/global/workloadIdentityPools/my-pool/attribute.repository/org/repo"
```

## GitHub Actions → Azure

```yaml
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

Federated credential:
```bash
az ad app federated-credential create \
  --id APP_ID \
  --parameters '{"name": "github", "issuer": "https://token.actions.githubusercontent.com", "subject": "repo:org/repo:ref:refs/heads/main", "audiences": ["api://AzureADTokenExchange"]}'
```

## AWS → GCP

EC2 instance (with IRSA-like role) → GCS bucket:

1. EC2 has IAM role
2. AWS STS issues temp creds
3. Use AWS STS GetCallerIdentity as identity (signed)
4. GCP WIF provider trusts AWS

```bash
gcloud iam workload-identity-pools providers create-aws my-aws-provider \
  --workload-identity-pool=my-pool \
  --account-id=AWS_ACCT_ID
```

App on EC2: uses GCP SA token; no static key.

## GCP → AWS

GCP SA → AWS IAM role:

1. SA gets ID token
2. AWS IAM trusts GCP issuer
3. App calls AssumeRoleWithWebIdentity

```bash
# Trust policy
{
  "Principal": {"Federated": "accounts.google.com"},
  "Action": "sts:AssumeRoleWithWebIdentity"
}
```

## Azure → GCP

Similar via Workload Identity Federation:
```bash
gcloud iam workload-identity-pools providers create-oidc azure \
  --workload-identity-pool=my-pool \
  --issuer-uri="https://login.microsoftonline.com/TENANT_ID/v2.0" \
  --allowed-audiences="api://AzureADTokenExchange"
```

## Tenant Identity (Central IdP)

For mature orgs: central IdP federates to all clouds.

```
Okta / Entra / Google → 
   ├─ AWS IAM Identity Center
   ├─ GCP Cloud Identity / SAML
   └─ Azure Entra (native)
```

Users in one IdP; access all clouds via SSO.

## K8s Pods → Cloud

### EKS Pod → AWS (IRSA)
Standard.

### GKE Pod → GCP (Workload Identity)
Standard.

### AKS Pod → Azure (Workload Identity)
Standard.

### Multi-Cloud K8s
Pod in GKE → AWS resource:
- Pod has GCP SA
- AWS WIF trusts GCP
- Token exchange

For: portable apps.

## SPIFFE / SPIRE

Standardized workload identity:
- SPIFFE ID: spiffe://example.com/api/svc
- Identity issued via cryptographic agent
- Cloud-agnostic

For: zero-trust multi-cluster.

## Vault Cross-Cloud

```bash
vault read aws/creds/dev-role  # gets temp AWS creds
vault read gcp/static-account/my-sa/key  # GCP SA key
```

Vault as credential broker. Auth via JWT / OIDC.

For: many clouds via central Vault.

## Audit

Cross-cloud audit:
- AWS CloudTrail
- GCP Cloud Audit Logs
- Azure Activity Log

Aggregate via SIEM (Splunk, Datadog).

## Best Practices

- OIDC federation (no static keys)
- Workload Identity per cloud
- Central IdP for users
- Vault / SPIRE for workload at scale
- Audit cross-cloud
- Conditional scoping (repo, branch, env)

## Common Mistakes

- Static SA / IAM keys in CI
- Cross-cloud secrets (rotation pain)
- No condition scoping (any branch can deploy)
- Trust too broad (whole org access)
- No audit aggregation

## Real Setup

GitHub Actions matrix deploy:
```yaml
strategy:
  matrix:
    cloud: [aws, gcp, azure]
steps:
  - if: matrix.cloud == 'aws'
    uses: aws-actions/configure-aws-credentials@v4
    with: ...
  - if: matrix.cloud == 'gcp'
    uses: google-github-actions/auth@v2
    with: ...
  - if: matrix.cloud == 'azure'
    uses: azure/login@v2
    with: ...
```

Zero keys.

## Quick Refs

```bash
# AWS OIDC for GitHub
aws iam create-open-id-connect-provider ...

# GCP WIF
gcloud iam workload-identity-pools / providers

# Azure federated cred
az ad app federated-credential create
```

## Interview Prep

**Mid**: "OIDC federation."

**Senior**: "Cross-cloud IAM."

**Staff**: "Zero-trust multi-cloud identity."

## Next Topic

→ [T04 — Data Gravity & Egress Cost Traps](T04-Data-Gravity-Egress.md)
