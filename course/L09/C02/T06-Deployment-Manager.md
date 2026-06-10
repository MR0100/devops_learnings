# L09/C02/T06 — Deployment Manager, Config Connector

## Learning Objectives

- Use GCP native IaC
- Compare to Terraform

## Deployment Manager (DM)

GCP-native IaC. YAML or Python:
```yaml
resources:
- name: my-vm
  type: compute.v1.instance
  properties:
    zone: us-central1-a
    machineType: zones/us-central1-a/machineTypes/e2-medium
    disks:
    - boot: true
      autoDelete: true
      initializeParams:
        sourceImage: projects/debian-cloud/global/images/family/debian-12
    networkInterfaces:
    - network: global/networks/default
```

```bash
gcloud deployment-manager deployments create my-deploy --config config.yaml
```

## Status

DM exists; less actively developed.

Most GCP shops: Terraform or Config Connector.

## Config Connector

K8s-native IaC for GCP:
```yaml
apiVersion: storage.cnrm.cloud.google.com/v1beta1
kind: StorageBucket
metadata:
  name: my-bucket
  annotations:
    cnrm.cloud.google.com/project-id: my-project
spec:
  location: US
```

Apply with kubectl:
```bash
kubectl apply -f bucket.yaml
```

GCP resource created.

For: GitOps + GCP.

## Install

```bash
gcloud container clusters update my-gke --update-addons=ConfigConnector=ENABLED
```

Or self-hosted via Helm.

## Why Config Connector

- K8s native (CRDs)
- GitOps fits
- Per-namespace projects
- Drift reconciliation

For: K8s-first orgs.

## Vs Terraform

| | Terraform | Config Connector | DM |
|---|---|---|---|
| Multi-cloud | yes | GCP-only | GCP-only |
| State | explicit backend | K8s etcd | GCP-managed |
| Drift | plan | reconcile loop | manual |
| Maturity | high | growing | mature but quiet |
| GitOps | possible | native | unusual |

## Pulumi (for GCP)

```typescript
import * as gcp from "@pulumi/gcp";

new gcp.storage.Bucket("my-bucket", {
  location: "US",
});
```

For: GCP via programming language.

## Crossplane

Open-source K8s control plane for cloud:
- Multi-cloud
- K8s-native CRDs
- Compose providers

```yaml
apiVersion: compute.gcp.crossplane.io/v1alpha1
kind: Network
metadata:
  name: my-vpc
spec:
  forProvider:
    autoCreateSubnetworks: false
```

Alternative to CC for multi-cloud.

## Terraform Most Common

For GCP today: Terraform is dominant.

```hcl
resource "google_storage_bucket" "my_bucket" {
  name     = "my-bucket"
  location = "US"
}
```

Reasons:
- Multi-cloud team familiarity
- Mature ecosystem
- Strong state management

## Choosing IaC for GCP

### Multi-Cloud
Terraform.

### GCP-Only, K8s-Native
Config Connector.

### Cloud Run / serverless
Terraform.

### Quick prototype
gcloud CLI.

### Composition / abstractions
Pulumi or Crossplane.

## Config Connector Examples

### IAM
```yaml
apiVersion: iam.cnrm.cloud.google.com/v1beta1
kind: IAMServiceAccount
metadata:
  name: my-sa
spec:
  displayName: "My SA"
```

### Networking
```yaml
apiVersion: compute.cnrm.cloud.google.com/v1beta1
kind: ComputeNetwork
metadata:
  name: my-vpc
spec:
  autoCreateSubnetworks: false
```

### GKE
```yaml
apiVersion: container.cnrm.cloud.google.com/v1beta1
kind: ContainerCluster
metadata:
  name: my-gke
spec:
  location: us-central1
  initialNodeCount: 3
```

## Workload Identity for CC

CC uses GCP SA via Workload Identity:
```bash
gcloud iam service-accounts add-iam-policy-binding cnrm-system@PROJ.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member=...
```

## Per-Namespace Projects

```yaml
apiVersion: core.cnrm.cloud.google.com/v1beta1
kind: ConfigConnectorContext
metadata:
  name: configconnectorcontext.core.cnrm.cloud.google.com
  namespace: team-a
spec:
  googleServiceAccount: team-a-sa@PROJ.iam.gserviceaccount.com
```

Namespace = project. For multi-tenant.

## Compare Bicep / ARM

| | Bicep (Azure) | DM (GCP) |
|---|---|---|
| Maturity | Active | Legacy-feeling |
| Adoption | Growing | Limited |
| Native | Yes | Yes |

GCP didn't push DM like Azure did Bicep.

## State Management

Terraform: state file backend (GCS, etc.).

CC: K8s etcd (where CRDs live).

DM: GCP-internal.

## Best Practices

- Most GCP shops: Terraform
- GitOps + K8s: Config Connector
- Avoid DM for new projects
- Modules / abstractions for reuse
- CI/CD apply (not local)

## Common Mistakes

- Mixing CC + Terraform (drift)
- DM for new (legacy bias)
- No state mgmt
- IAM via UI (drift)

## Terraform for GCP

Provider:
```hcl
provider "google" {
  project = "my-project"
  region  = "us-central1"
}
```

Auth:
- SA key (avoid)
- `gcloud auth application-default login` (dev)
- WIF (CI)

## CI/CD

For CC: Argo CD / Flux.

For Terraform: Atlantis, Spacelift, Terraform Cloud.

## Quick Refs

```bash
# DM
gcloud deployment-manager deployments create / list / delete

# Config Connector
kubectl apply -f resource.yaml
kubectl get StorageBucket

# Terraform
terraform init / plan / apply
```

## Interview Prep

**Junior**: "GCP IaC options."

**Mid**: "Config Connector purpose."

**Senior**: "When CC vs Terraform."

**Staff**: "GCP IaC strategy."

## Next Topic

→ Move to [L09/C03 — Multi-Cloud Strategy](../C03/README.md)
