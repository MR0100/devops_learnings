# L12/C09 — Registries

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Registry-Options.md) | Docker Hub, ECR, GCR, Artifact Registry, ACR, Harbor | 1 hr |
| [T02](T02-Image-Replication.md) | Image Replication | 0.5 hr |
| [T03](T03-Pull-Through-Cache.md) | Pull-Through Caches | 0.5 hr |

## Public Registries

| Registry | Owner | Notes |
|---|---|---|
| **Docker Hub** | Docker Inc. | Original; rate limits (100/6h anon, 200/6h authenticated); paid plans for more |
| **GHCR** (ghcr.io) | GitHub | Free for public; integrates with Actions |
| **Quay.io** | Red Hat | Public OSS friendly |
| **gcr.io** / **pkg.dev** | Google | Distroless images here |
| **public.ecr.aws** | AWS | Free public images |

## Private Registries

### AWS ECR
- Per-region
- ECR Public (public images)
- Image scanning (Basic free; Enhanced via Inspector $$$)
- Lifecycle policies (delete old, untagged)
- Cross-region replication
- Pull-through cache (proxy to Docker Hub, Quay, GitHub Container Registry, GitLab, etc.)
- IAM auth

```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123.dkr.ecr.us-east-1.amazonaws.com
```

### GCP Artifact Registry
- Replaces Container Registry (gcr.io)
- Per-region or multi-region
- Supports OCI artifacts (Helm charts, etc.)
- Vulnerability scanning
- IAM-integrated

### Azure Container Registry (ACR)
- Tiers: Basic, Standard, Premium
- Geo-replication (Premium)
- Tasks (built-in build)
- Content trust

### Harbor (CNCF, self-hosted)
- Open source registry
- Vulnerability scanning (Trivy integration)
- Image signing (Notary/Cosign)
- Image replication between Harbors
- Multi-tenant projects, RBAC
- Quotas

### Self-Hosted Docker Distribution
Reference impl (`registry:2`). Simple but lacks features (no UI, scanning, RBAC). Use only for trivial cases or testing.

## Image Tagging Strategy

### Bad: `:latest`
- Ambiguous; non-reproducible
- Can change underneath you
- Don't use in production

### Good
- **Immutable tags**: `:v1.2.3`, `:1.2.3-alpine`, `:abc123def` (commit SHA)
- **Digests**: `image@sha256:abc...` — strongest immutability
- **Branch tags**: `:main` for moving target in dev

```bash
docker pull myimage:v1.2.3
docker pull myimage@sha256:abc...
```

K8s, ArgoCD, Helm — all support digests.

## Lifecycle Policies

ECR example:
```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Keep last 10 prod images",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["v"],
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": {"type": "expire"}
    },
    {
      "rulePriority": 2,
      "description": "Remove untagged after 7 days",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 7
      },
      "action": {"type": "expire"}
    }
  ]
}
```

## Image Replication

For multi-region deploys, replicate images close to workloads.

### Why
- Faster pulls
- Survive regional registry outage
- Reduce cross-region pull costs

### Tools
- ECR cross-region replication (config rule)
- Harbor replication policies
- skopeo for one-off copies:
  ```bash
  skopeo copy docker://src/img:tag docker://dst/img:tag
  ```

## Pull-Through Caches

A pull-through cache proxies upstream registries. First pull goes upstream; subsequent pulls from cache.

### Why
- Dodge Docker Hub rate limits (anonymous pulls per IP)
- Reduce egress
- Reduce build time
- Self-host control over deps

### ECR Pull-Through Cache (AWS)
```bash
aws ecr create-pull-through-cache-rule \
  --ecr-repository-prefix docker-hub \
  --upstream-registry-url registry-1.docker.io
```

Then pull: `123.dkr.ecr.us-east-1.amazonaws.com/docker-hub/library/nginx:1.27`

### Harbor Proxy Project
Configure Harbor project as proxy to Docker Hub, GHCR, etc.

## Authentication

### Docker Login
```bash
docker login           # Docker Hub
docker login ghcr.io   # GitHub
echo $TOKEN | docker login -u user --password-stdin ghcr.io
```

### Credential Helpers
Better than passwords in plaintext:
- `~/.docker/config.json` references helper:
  - `osxkeychain`, `wincred`, `secretservice`
  - Cloud-specific: `docker-credential-ecr-login`, `gcr`, `acr`

### K8s ImagePullSecret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: regcred
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <base64 docker/config.json>
---
# In pod
spec:
  imagePullSecrets:
  - name: regcred
```

### IAM-Based Auth
- ECR: IAM role attached to node / pod (IRSA / Pod Identity)
- GCR / AR: GCP SA with Artifact Registry Reader
- ACR: Azure Managed Identity

No long-lived secrets needed.

## Multi-Arch (Multi-Platform)

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/me/app:v1 \
  --push .

docker manifest inspect ghcr.io/me/app:v1
```

Single tag, registry serves the right arch for the puller.

## Interview Themes

- "Compare registry options"
- "ECR lifecycle policies — what do they solve?"
- "Pull-through cache — when needed?"
- "Image tagging strategy"
- "How do K8s pods authenticate to private registry?"
