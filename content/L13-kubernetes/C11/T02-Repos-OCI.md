# L13/C11/T02 — Helm Repos & OCI Registries

## Learning Objectives

- Use Helm repos
- Push charts to OCI

## Traditional Helm Repo

HTTP server with `index.yaml`:
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm search repo redis
```

`index.yaml` is auto-generated catalog.

## Add + Install

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack
```

## Create Repo

Host charts on:
- GitHub Pages
- S3
- GCS
- Chart Museum
- JFrog Artifactory

Build:
```bash
helm package ./mychart   # creates mychart-0.1.0.tgz
helm repo index .         # creates index.yaml
```

Upload .tgz + index.yaml to HTTP server.

## OCI Registries

Modern: store charts in OCI registries (Docker Hub, ECR, GHCR, etc.).

```bash
helm push mychart-0.1.0.tgz oci://myregistry.io/charts
helm pull oci://myregistry.io/charts/mychart --version 0.1.0
helm install my-release oci://myregistry.io/charts/mychart --version 0.1.0
```

No index.yaml; OCI registry handles.

## Why OCI

- Reuse registry infra
- IAM-controlled access
- Image-like distribution
- Multi-platform support
- No separate repo server

For modern: prefer OCI.

## Login to OCI

```bash
# Docker Hub
helm registry login docker.io
# ECR
aws ecr get-login-password | helm registry login --username AWS --password-stdin 123.dkr.ecr.us-east-1.amazonaws.com
# GHCR
echo $GH_TOKEN | helm registry login ghcr.io -u USERNAME --password-stdin
```

## Push

```bash
helm package mychart
helm push mychart-0.1.0.tgz oci://myregistry.io/charts
# stored as oci://myregistry.io/charts/mychart:0.1.0
```

Tag = chart version.

## Pull / Install

```bash
helm pull oci://myregistry.io/charts/mychart --version 0.1.0
# downloads mychart-0.1.0.tgz

helm install my-release oci://myregistry.io/charts/mychart --version 0.1.0
```

## Use in CI

```yaml
- name: Login
  run: |
    aws ecr get-login-password | helm registry login --username AWS --password-stdin $REGISTRY
- name: Package + Push
  run: |
    helm package ./mychart
    helm push mychart-$(yq .version Chart.yaml).tgz oci://$REGISTRY/charts
```

## Private Charts

Authentication via:
- helm registry login
- Registry-specific creds in CI

For: internal charts.

## Versioning

Semver per chart:
- `0.1.0`: initial
- `0.2.0`: minor (backward compat)
- `1.0.0`: stable
- `2.0.0`: breaking

In Chart.yaml:
```yaml
version: 0.1.0
appVersion: 1.16.0
```

`version` = chart version.
`appVersion` = embedded app version.

## Chart Releases

Each install:
- Render templates
- Apply manifests
- Track release in Secret in namespace

```bash
helm history my-release
# REVISION  UPDATED                   STATUS    CHART
# 1         Mon Jun 9 10:00 2025      deployed  mychart-0.1.0
# 2         Mon Jun 9 11:00 2025      deployed  mychart-0.2.0
```

## Multi-Repo Strategy

Org might have:
- Public charts (Bitnami, official)
- Internal mirror (consolidated)
- Custom charts

Tools:
- Chart Museum (legacy repo)
- Harbor (multi-arch + OCI)
- ECR / GAR / ACR (OCI)

## Dependency Management

In Chart.yaml:
```yaml
dependencies:
- name: redis
  version: 17.x.x
  repository: https://charts.bitnami.com/bitnami
- name: postgres
  version: 12.x.x
  repository: oci://myregistry.io/charts
  alias: pgdb
```

```bash
helm dependency update
```

Pulls subcharts to charts/.

## Hardened Dependencies

For supply chain:
- Pin specific version
- Mirror to internal registry
- Sign charts (cosign)

## Signing Charts

```bash
# Sign
cosign sign $REGISTRY/charts/mychart:0.1.0

# Verify (in cluster via policy controller)
```

For supply chain security.

## ArtifactHub

Public catalog of charts (artifacthub.io). Search + discover.

For: finding community charts.

## Helmfile

For managing many releases:
```yaml
# helmfile.yaml
releases:
- name: prometheus
  namespace: monitoring
  chart: prometheus-community/kube-prometheus-stack
  values:
  - prometheus.yaml

- name: ingress
  namespace: ingress
  chart: ingress-nginx/ingress-nginx
  values:
  - ingress.yaml

- name: my-app
  namespace: default
  chart: ./charts/my-app
  values:
  - my-app.yaml
```

```bash
helmfile apply
```

Manages many releases as code. Like Terraform for Helm.

## Chart Repositories Search

```bash
helm search repo nginx       # in added repos
helm search hub nginx        # ArtifactHub
```

## Repo Updates

```bash
helm repo update             # update all
helm repo remove bitnami
helm repo list
```

## OCI Discovery

For OCI repos: no listing API yet (registry-specific).

Use registry UI / API.

## Air-Gapped

For air-gapped:
- Download chart .tgz
- Transfer offline
- helm install ./mychart-0.1.0.tgz

For: secure environments.

## Mirroring

For supply chain:
- Daily sync public → internal OCI
- Apps reference internal
- Audited

Tools: orca, distribution.

## Patterns

### Per-Environment Repo
```bash
helm install -f dev.yaml ./mychart
helm install -f prod.yaml ./mychart
```

Same chart; different values.

### Per-Team Repo
Each team publishes own charts. Shared via OCI.

### Umbrella Chart
Big chart with many subcharts:
```yaml
dependencies:
- name: frontend
- name: backend
- name: db
```

Install whole app at once.

## Best Practices

- OCI for new
- Pin chart versions
- Schema validation in chart
- CI publishes charts
- Internal mirror of public
- helmfile for multi-release
- Sign charts (Cosign)

## Common Mistakes

- Mixing latest tags (mutability)
- No internal mirror (supply chain risk)
- Untrustworthy public charts
- No version control on values files

## Migration HTTP → OCI

```bash
# Pull from HTTP repo
helm pull oldrepo/mychart --version 0.1.0
# Push to OCI
helm registry login oci.example.com
helm push mychart-0.1.0.tgz oci://oci.example.com/charts
```

Existing repos still work; migrate over time.

## Tooling

- helm: CLI
- helmfile: multi-release
- helm-secrets: SOPS integration
- helm-diff: diff before apply
- helm-git: install from Git

## Quick Refs

```bash
# Repo
helm repo add NAME URL
helm repo update
helm repo list

# OCI
helm registry login URL
helm push CHART.tgz oci://URL/path
helm pull oci://URL/path/CHART --version V
helm install NAME oci://URL/path/CHART --version V

# Package
helm package ./mychart

# Dependencies
helm dependency update
helm dependency build

# helmfile
helmfile apply
helmfile diff
```

## Interview Prep

**Mid**: "Helm repo vs OCI."

**Senior**: "Internal chart distribution."

**Staff**: "Chart supply chain security."

## Next Topic

→ [T03 — Helm 3 Architecture (No Tiller)](T03-Helm-Architecture.md)
