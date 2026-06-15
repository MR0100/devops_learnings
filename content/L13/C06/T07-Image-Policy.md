# L13/C06/T07 — Image Pull Secrets, Image Policy

## Learning Objectives

- Use private registries
- Sign + verify images

## Image Pull Secrets

For private registries:
```bash
kubectl create secret docker-registry my-registry \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=pass \
  --docker-email=me@example.com
```

Creates Secret of type `kubernetes.io/dockerconfigjson`.

## Pod Reference

```yaml
spec:
  imagePullSecrets:
  - name: my-registry
  containers:
  - name: app
    image: registry.example.com/myapp:v1
```

## Service Account Reference

Set on SA → all pods inherit:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: default
imagePullSecrets:
- name: my-registry
```

Simpler than per-pod.

## ECR (AWS)

Token expires ~12 hours. Refresh:

### IRSA / Pod Identity (Recommended)
EKS pulls ECR images using IRSA role:
- No imagePullSecret needed
- Permission attached to node group's IAM role
- Or use Pod Identity for granular

EKS nodes auto-authenticate to ECR for image pulls if node IAM allows.

### CronJob Refresh (Manual)
```yaml
apiVersion: batch/v1
kind: CronJob
spec:
  schedule: "0 */6 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: refresh
            image: amazon/aws-cli
            command:
            - sh
            - -c
            - |
              TOKEN=$(aws ecr get-login-password --region us-east-1)
              kubectl delete secret ecr-secret --ignore-not-found
              kubectl create secret docker-registry ecr-secret \
                --docker-server=123.dkr.ecr.us-east-1.amazonaws.com \
                --docker-username=AWS \
                --docker-password=$TOKEN
```

For non-EKS or non-IAM scenarios.

## GCR / Artifact Registry

Workload Identity for GKE: auto-auth.
Or use SA JSON key:
```bash
kubectl create secret docker-registry gcr-secret \
  --docker-server=gcr.io \
  --docker-username=_json_key \
  --docker-password="$(cat sa-key.json)"
```

## ACR (Azure)

Workload Identity or service principal:
```bash
kubectl create secret docker-registry acr-secret \
  --docker-server=myregistry.azurecr.io \
  --docker-username=<sp-app-id> \
  --docker-password=<sp-password>
```

## Image Pull Policy

```yaml
imagePullPolicy: IfNotPresent   # default for non-latest tags
imagePullPolicy: Always          # default for :latest
imagePullPolicy: Never           # local images only
```

`Always`: every pod start fetches image manifest (slow + bandwidth).

For production: pin specific tag (not latest) + IfNotPresent.

## Image Signing

Beyond pulling: verify image authenticity.

### Cosign (Sigstore)
```bash
# Sign
cosign sign --key cosign.key registry.example.com/myapp:v1

# Verify
cosign verify --key cosign.pub registry.example.com/myapp:v1
```

Public key in cluster verifies.

### Keyless (OIDC)
```bash
# Sign using GitHub Actions OIDC
cosign sign registry.example.com/myapp:v1
# Records identity in transparency log

# Verify
cosign verify --certificate-identity-regexp '.*' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  registry.example.com/myapp:v1
```

No key management; identity proves provenance.

## Policy Verification

Enforce signed images on cluster.

### Sigstore Policy Controller
```yaml
apiVersion: policy.sigstore.dev/v1beta1
kind: ClusterImagePolicy
metadata:
  name: must-be-signed
spec:
  images:
  - glob: "registry.example.com/**"
  authorities:
  - keyless:
      url: https://fulcio.sigstore.dev
      identities:
      - issuer: https://token.actions.githubusercontent.com
        subjectRegExp: ".*github.com/myorg/.*"
```

Pods with unsigned images blocked.

### Connaisseur (Sap)
Alternative; broader signing standards (Notary, etc.).

### Kyverno Image Verification
```yaml
rules:
- name: verify-images
  match: ...
  verifyImages:
  - imageReferences:
    - "registry.example.com/*"
    attestors:
    - entries:
      - keyless:
          subject: "https://github.com/myorg/.*"
          issuer: "https://token.actions.githubusercontent.com"
```

Integrated with broader policy.

## Image Vulnerability Scanning

### Pre-Deploy
- Trivy in CI
- Snyk
- Clair
- Anchore

Block deploy if critical CVE.

### Cluster-Side
- Inspector (AWS)
- Trivy operator
- Falco (runtime)

Periodic scanning.

## Image Mutability

`latest` tag: mutable; can point to different content.

For prod:
- Pin to specific tag (`v1.2.3`)
- Or digest (`@sha256:...`)

```yaml
image: myapp@sha256:abc...
```

Immutable; guaranteed exact content.

## Registry Mirroring

For air-gapped / network-restricted:
- Mirror approved images to internal registry
- Block external registries (via policy or network)

Or use pull-through cache (ECR Pull-Through, Harbor, etc.).

## Private Registry CI

GitHub Actions example:
```yaml
- uses: docker/login-action@v3
  with:
    registry: ${{ secrets.REGISTRY }}
    username: ${{ secrets.USERNAME }}
    password: ${{ secrets.PASSWORD }}

- run: |
    docker build -t $IMAGE:$SHA .
    docker push $IMAGE:$SHA
```

Plus sign:
```yaml
- uses: sigstore/cosign-installer@v3
- run: cosign sign --yes $IMAGE:$SHA
```

## SBOM (Software Bill of Materials)

Inventory of image components:
```bash
syft registry.example.com/myapp:v1 -o spdx-json > sbom.json
```

Attach to image:
```bash
cosign attach sbom --sbom sbom.json registry.example.com/myapp:v1
```

For supply chain.

## SLSA

Supply chain Levels for Software Artifacts:
- L0: nothing
- L1: build script
- L2: hosted build, signed provenance
- L3: hardened build platform
- L4: hermetic, reproducible

For high security: SLSA L3+.

## Image Registry Allowlist

Kyverno policy:
```yaml
rules:
- name: allowed-registries
  match: any:
    - resources: {kinds: [Pod]}
  validate:
    message: "Image from approved registry only"
    pattern:
      spec:
        containers:
        - image: "registry.example.com/* | ghcr.io/myorg/*"
```

Block any other registry.

## Distroless

Minimal images:
```dockerfile
FROM gcr.io/distroless/static:nonroot
COPY app /app
ENTRYPOINT ["/app"]
```

No shell, no package manager. Reduces attack surface.

## Multi-Arch

Build for amd64 + arm64:
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t $IMAGE --push .
```

K8s pulls right arch automatically.

## Image Lifecycle

Per registry:
- ECR lifecycle policy: keep last N
- GHCR: manual / GH Actions
- Custom registries: tooling needed

For: cost + clean state.

## Quick Refs

```bash
# Pull secret
kubectl create secret docker-registry mysec \
  --docker-server=... --docker-username=... --docker-password=...

# Cosign
cosign sign --key cosign.key $IMAGE
cosign verify --key cosign.pub $IMAGE

# Trivy scan
trivy image $IMAGE

# Check signed
cosign verify --certificate-identity-regexp ... $IMAGE
```

## Common Mistakes

- `latest` tag in production
- Pull secret per pod (use SA)
- No signature verification
- Allow any registry
- Big images (slow start; more surface)
- Root-running containers

## Best Practices

- Pin to digest or specific tag
- Distroless / nonroot base
- Multi-stage build (smaller)
- Sign images (Cosign)
- Verify signatures in cluster
- Vulnerability scan in CI
- Allowlist registries
- Pull secrets via SA
- Workload Identity / IRSA for cloud registries

## Anti-Patterns

- Single registry for everything (blast)
- Long-lived registry credentials
- No scan, no verify
- Same SA for many apps

## Cluster Security

Image policy = one of many controls. Combined:
- Signed images (provenance)
- Vulnerability scan (CVE)
- Distroless (minimal)
- Pod Security Standards (runtime)
- NetworkPolicy (lateral)
- RBAC (API access)

Defense in depth.

## Interview Prep

**Junior**: "Pull secret purpose."

**Mid**: "Image signing — why."

**Senior**: "Supply chain security in K8s."

**Staff**: "SLSA L3 for org."

## Next Topic

→ [T08 — Admission Control (Webhooks & ValidatingAdmissionPolicy / CEL)](T08-Admission-Control.md)
