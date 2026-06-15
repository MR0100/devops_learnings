# L09/C02/T02 — IAM (Roles, Service Accounts, Workload Identity)

## Learning Objectives

- Use GCP IAM
- Federate workloads to GCP

## IAM Model

```
Principal → Role → Resource
```

- **Principal**: user, group, SA
- **Role**: bundle of permissions
- **Resource**: project, bucket, instance, etc.

Bindings: principal + role at resource.

## Roles

Three types:

### Basic (legacy)
- Owner
- Editor
- Viewer

Too broad. Avoid for prod.

### Predefined
Service-specific:
- roles/compute.instanceAdmin
- roles/storage.objectViewer
- roles/iam.serviceAccountUser

For: granular access.

### Custom
Define your own:
```bash
gcloud iam roles create myRole \
  --project=PROJ \
  --title="My Role" \
  --permissions=storage.objects.get,storage.objects.list
```

For: precise needs.

## Bind

```bash
gcloud projects add-iam-policy-binding PROJ \
  --member=user:alice@example.com \
  --role=roles/storage.objectViewer
```

## Hierarchy

Roles at:
- Org
- Folder
- Project
- Resource (per type)

Inherited downward.

For: principle of least privilege.

## Service Accounts (SA)

Identities for workloads:
```bash
gcloud iam service-accounts create my-sa \
  --display-name="My SA" \
  --project=PROJ
```

Email: my-sa@PROJ.iam.gserviceaccount.com.

## SA Keys

```bash
gcloud iam service-accounts keys create key.json \
  --iam-account=my-sa@PROJ.iam.gserviceaccount.com
```

**AVOID** in prod. Static key = leak risk.

## Default SAs

- **Compute Engine default SA**: `PROJ_NUM-compute@developer...`
- **App Engine default SA**: `PROJ_ID@appspot.gserviceaccount.com`

Have Editor by default. **DISABLE** in prod (org policy).

## Workload Identity (GKE)

K8s SA → GCP SA:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-sa
  annotations:
    iam.gke.io/gcp-service-account: my-gcp-sa@PROJ.iam.gserviceaccount.com
```

Plus enable on cluster:
```bash
gcloud container clusters update CLUSTER --workload-pool=PROJ.svc.id.goog
```

Pods using my-sa: get GCP SA token. No JSON key.

= IRSA (AWS) / Workload Identity (Azure).

## Workload Identity Federation

For non-GCP workloads (AWS, Azure, GitHub):
```bash
gcloud iam workload-identity-pools create my-pool \
  --location=global \
  --display-name="My Pool"

gcloud iam workload-identity-pools providers create-oidc github \
  --location=global \
  --workload-identity-pool=my-pool \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping=...
```

GitHub Actions:
```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: projects/.../providers/github
    service_account: my-sa@PROJ.iam.gserviceaccount.com
```

For: no SA keys in CI.

## VM SA

```bash
gcloud compute instances create my-vm --service-account=my-sa@PROJ.iam.gserviceaccount.com --scopes=cloud-platform
```

VM impersonates SA via metadata server.

`gcloud` from VM: uses SA auto.

## Impersonation

```bash
gcloud config set auth/impersonate_service_account my-sa@PROJ.iam.gserviceaccount.com

# Now commands act as SA
gcloud storage ls
```

Requires roles/iam.serviceAccountTokenCreator on the SA.

For: humans testing SA permissions; no JSON key needed.

## Conditional IAM

```bash
gcloud projects add-iam-policy-binding PROJ \
  --member=user:alice@example.com \
  --role=roles/compute.admin \
  --condition='expression=resource.name.startsWith("projects/PROJ/zones/us-central1"),title=us-central1-only'
```

Grants role only when condition matches. For: granular.

## Org Policy

Different from IAM:
- IAM: who can do what
- Org Policy: what's allowed (regardless of IAM)

```bash
gcloud org-policies set-policy policy.yaml --organization=ORG
```

Examples:
- Disable SA key creation
- Restrict allowed regions
- Restrict external IPs
- VPC SC

## VPC Service Controls (VPC SC)

Perimeters around resources:
- Even with valid creds, can't access from outside perimeter
- Data exfiltration prevention

For: high security (FedRAMP, regulated).

## Audit Logs

3 types:
- Admin Activity (default on)
- Data Access (off by default; chatty)
- System Event
- Policy Denied

Sent to Cloud Logging.

For: security forensics.

## Comparison

| | AWS | Azure | GCP |
|---|---|---|---|
| Identity | IAM Identity Center | Entra ID | Cloud Identity / Workspace |
| Role | IAM Role | RBAC role | IAM Role |
| Workload | IRSA | Workload Identity | Workload Identity / Federation |
| MFA | Yes | Yes (CA) | Yes |
| Conditional | Conditions | CA Policies | Conditional IAM |

## SA Best Practices

- One SA per app
- Minimal scope
- Workload Identity (no keys)
- Disable default SAs (Editor too broad)
- Audit SA usage
- Rotate any keys (if must use)

## Common Mistakes

- Basic roles (Owner, Editor) — too broad
- Default SA used (Editor)
- SA keys in code/CI (use WIF)
- No org policies (no guardrails)
- Audit logs ignored

## Cloud Identity vs Workspace

- **Workspace**: paid, email + collab
- **Cloud Identity**: free, identity only

For GCP-only orgs: Cloud Identity sufficient.

## Recommender

```bash
gcloud recommender recommendations list \
  --project=PROJ \
  --location=global \
  --recommender=google.iam.policy.Recommender
```

ML-suggested IAM tightening.

For: continuous least-privilege.

## Best Practices

- Predefined / custom roles (not Basic)
- Workload Identity for K8s
- WIF for external CI
- Org Policy for guardrails
- VPC SC for sensitive data
- Conditional bindings
- Recommender insights

## Quick Refs

```bash
# Roles
gcloud iam roles list
gcloud iam roles create

# SA
gcloud iam service-accounts create / list / delete

# Bindings
gcloud projects add-iam-policy-binding

# Workload Identity
gcloud container clusters update --workload-pool=PROJ.svc.id.goog

# WIF
gcloud iam workload-identity-pools / providers
```

## Interview Prep

**Junior**: "GCP IAM."

**Mid**: "Workload Identity."

**Senior**: "WIF for CI."

**Staff**: "Cross-org IAM federation."

## Next Topic

→ [T03 — Compute (GCE, GKE, Cloud Run, Cloud Functions)](T03-Compute.md)
