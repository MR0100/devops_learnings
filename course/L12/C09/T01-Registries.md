# L12/C09/T01 — Docker Hub, ECR, GCR, Artifact Registry, ACR, Harbor

## Learning Objectives

- Choose registry
- Operate per provider

## Registries

Where images live:
- Public: Docker Hub, ghcr.io, quay.io
- Cloud: ECR (AWS), GAR (GCP), ACR (Azure)
- Self-hosted: Harbor, distribution, Nexus, Artifactory

## Docker Hub

Public default; most popular.

```bash
docker push username/image:tag
docker pull library/nginx:1.27
```

Tiers:
- Free: 200 pulls/6hr (anonymous)
- Paid: more

Rate limits: pain point.

## ECR (AWS)

Per-account, per-region:
```bash
aws ecr get-login-password | docker login --username AWS --password-stdin 123.dkr.ecr.us-east-1.amazonaws.com
docker push 123.dkr.ecr.us-east-1.amazonaws.com/myapp:v1
```

Features:
- IAM-integrated
- Lifecycle policies
- Scanning
- Replication

## ECR Public

```bash
docker pull public.ecr.aws/nginx/nginx
```

Public images; AWS-managed; no rate limits for AWS users.

## GAR (Google Artifact Registry)

```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
docker push us-central1-docker.pkg.dev/project/repo/image:tag
```

Replaces GCR (deprecated).

Features:
- IAM
- Vulnerability scanning
- Multi-region
- Format support (Docker, Maven, npm, etc.)

## ACR (Azure)

```bash
az acr login --name myregistry
docker push myregistry.azurecr.io/myapp:v1
```

Features:
- RBAC
- Replication
- Scanning (Defender)
- Tasks (CI built-in)

## Harbor

Open-source enterprise:
- Self-host
- Helm chart
- Vulnerability scanning (Trivy)
- Content trust
- Replication
- RBAC
- Robot accounts

For: on-prem / multi-cloud.

## GHCR (GitHub Container Registry)

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
docker push ghcr.io/myorg/myapp:v1
```

Free for public + private (with limits).

Tied to GitHub repo permissions.

## quay.io

Red Hat's registry:
- Public + private
- Scanning (Clair)
- Robot accounts
- Free tier

## JFrog Artifactory

Enterprise universal repo:
- All formats
- Replication
- HA
- Paid

## Nexus

Open-source artifact repo:
- Docker support
- Other formats
- Free + paid

## Pull-Through Cache

```bash
# ECR pull-through cache for Docker Hub
aws ecr create-pull-through-cache-rule \
  --ecr-repository-prefix dockerhub \
  --upstream-registry-url registry-1.docker.io

# Pull through ECR
docker pull 123.dkr.ecr.us-east-1.amazonaws.com/dockerhub/nginx:1.27
```

For: cache; avoid rate limits.

## Replication

Multi-region:
- ECR: cross-region replication
- ACR: geo-replication
- GAR: multi-region

For: latency + DR.

```bash
aws ecr put-replication-configuration --replication-configuration '...'
```

## Image Lifecycle

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 10 tagged",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["v"],
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": {"type": "expire"}
    }
  ]
}
```

ECR lifecycle policy. Similar for other.

For: cost + clutter.

## Authentication

### Static Credentials
Username/password or token.

### IRSA / Workload Identity
K8s SA → cloud IAM. No static creds.

For ECR: IRSA, EC2 instance role.

### OIDC
GitHub Actions → cloud:
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::ACCT:role/GitHubActions
```

For: no AWS keys in CI.

## Multi-Arch Push

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -t REGISTRY/IMAGE:v1 --push .
```

Single tag; manifest list.

## Costs

### ECR
- $0.10/GB/mo storage
- Egress to Internet
- Same-region pull free

### GAR
- $0.10/GB/mo
- Similar egress

### Docker Hub
- Free public
- Paid private

### Harbor
- Self-host (HW cost + ops)

## Security

- Private repos
- IAM / RBAC
- Image signing
- Scanning
- Audit logs

## Scanning Integration

Most cloud registries integrate scanning:
- ECR: basic + Inspector
- GAR: Container Scanning
- ACR: Microsoft Defender
- Harbor: Trivy

For: continuous CVE detection.

## Repository Strategy

### Per-Workload Repo
```
myapp-api
myapp-worker
myapp-frontend
```

Clear ownership.

### Per-Team
```
team-a/api
team-a/worker
team-b/service
```

Tenant isolation.

### Per-Env
Usually not; same image across envs.

## Tagging Strategy

```
v1.2.3              # release
v1.2                # latest minor
v1                  # latest major
latest              # latest (avoid in prod)
sha-abc123def       # commit
sha-abc123def-amd64 # arch-specific
```

For prod: pin to digest.

## Best Practices

- Private registry for prod
- Lifecycle policies
- Scanning enabled
- Replication for DR
- IAM/RBAC
- Pull-through for upstream
- Signed images
- Pinned tags / digests in deploy

## Common Mistakes

- :latest in prod
- No lifecycle (storage bloat)
- Public when should be private
- Static creds in CI (use OIDC)
- No replication for DR

## Cross-Registry

```bash
# Copy
crane copy registry-a/image:tag registry-b/image:tag
skopeo copy docker://A docker://B
```

For: mirror, backup.

## OCI Artifacts

Beyond images:
- Helm charts
- WASM
- SBOMs
- Anything

```bash
oras push REGISTRY/REPO:TAG file.bin
```

For: unified artifact storage.

## Quick Refs

```bash
# Push
docker push REGISTRY/REPO:TAG

# Pull
docker pull REGISTRY/REPO:TAG

# Inspect
docker manifest inspect REGISTRY/REPO:TAG

# Cross-tool
crane copy SRC DST
skopeo copy docker://SRC docker://DST
```

## Interview Prep

**Mid**: "Registry choice."

**Senior**: "Pull-through cache."

**Staff**: "Multi-region registry strategy."

## Next Topic

→ [T02 — Image Replication](T02-Image-Replication.md)
