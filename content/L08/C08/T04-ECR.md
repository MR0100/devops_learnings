# L08/C08/T04 — ECR (Image Scanning, Replication)

## Learning Objectives

- Use ECR for images
- Enable scanning

## ECR

Elastic Container Registry. Private container registry per AWS account / region.

## Setup

```bash
aws ecr create-repository --repository-name myapp
```

URI:
```
123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp
```

## Auth

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

Token valid 12 hours.

## Push / Pull

```bash
docker tag myapp:v1 123.dkr.ecr.us-east-1.amazonaws.com/myapp:v1
docker push 123.dkr.ecr.us-east-1.amazonaws.com/myapp:v1
docker pull 123.dkr.ecr.us-east-1.amazonaws.com/myapp:v1
```

## Tags

Multiple tags per image:
```
v1.2.3
v1.2
v1
latest
```

Avoid `latest` (ambiguous); always pin in deployments.

Immutable tags option:
```bash
aws ecr put-image-tag-mutability --repository-name myapp --image-tag-mutability IMMUTABLE
```

Once tag set: can't overwrite. Prevent accidental v1 → bad image.

## Image Scanning

### Basic Scan (free)
On push or on-demand. Reports CVEs.

```bash
aws ecr put-image-scanning-configuration --repository-name myapp --image-scanning-configuration scanOnPush=true
```

```bash
aws ecr describe-image-scan-findings --repository-name myapp --image-id imageTag=v1
```

Output: vulnerabilities with severity.

### Enhanced Scan (Inspector)
Continuous scanning; deeper analysis. Costs per image scanned.

Enable in Inspector.

For: compliance, production images.

## Lifecycle Policies

Auto-delete old images:
```json
{
  "rules": [{
    "rulePriority": 1,
    "description": "Keep last 10 tagged",
    "selection": {
      "tagStatus": "tagged",
      "tagPrefixList": ["v"],
      "countType": "imageCountMoreThan",
      "countNumber": 10
    },
    "action": {"type": "expire"}
  }, {
    "rulePriority": 2,
    "description": "Expire untagged after 7 days",
    "selection": {
      "tagStatus": "untagged",
      "countType": "sinceImagePushed",
      "countUnit": "days",
      "countNumber": 7
    },
    "action": {"type": "expire"}
  }]
}
```

```bash
aws ecr put-lifecycle-policy --repository-name myapp --lifecycle-policy-text file://lc.json
```

Saves cost; reduces clutter.

## Cross-Account

Allow other account to pull:
```bash
aws ecr set-repository-policy --repository-name myapp --policy-text '{
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::OTHER:root"},
    "Action": [
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability"
    ]
  }]
}'
```

## Cross-Region Replication

Copy images to other regions:
```bash
aws ecr put-replication-configuration --replication-configuration '{
  "rules": [{
    "destinations": [{"region": "us-west-2", "registryId": "123"}]
  }]
}'
```

For: multi-region apps; faster pulls from other regions.

Cost: per-GB replicated.

## Cross-Account Replication

Same setup with different registryId. For multi-account organizations.

## Public Registry

ECR Public (gallery.ecr.aws):
- Anonymous read
- For sharing public images
- Free for public

Most teams use private.

## Cost

- Storage: $0.10/GB-month
- Egress to Internet: $0.09/GB
- Cross-region replication: $0.02/GB
- Same-region pull (to ECS / EKS): free

For 10 images × 500 MB = 5 GB = $0.50/mo. Small.

For 100 services × 10 versions × 500 MB = 500 GB = $50/mo.

Lifecycle policies help.

## Pull-Through Cache

ECR can cache from upstream registries:
- Docker Hub (rate-limited)
- Quay
- GitHub Container Registry
- AWS ECR Public

Pull through ECR; first request fetches from upstream; subsequent cached:
```bash
docker pull 123.dkr.ecr.us-east-1.amazonaws.com/myorg/upstream-image:v1
```

For: avoiding Docker Hub rate limits.

## Image Signing (Notary v2)

Sign images cryptographically:
- AWS Signer
- Verify on pull / deploy
- Supply chain security

## Image Tagging Best Practices

- Semantic: v1.2.3
- Git commit SHA: abc123def
- Date: 2024-06-09-1410
- Combination: v1.2.3-abc123

NEVER:
- Mutable `latest` in production
- Untagged in production
- Different things to same tag

## CI/CD Integration

GitHub Actions:
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123:role/GitHubActions
    aws-region: us-east-1

- uses: aws-actions/amazon-ecr-login@v2

- run: |
    docker build -t $IMAGE:$SHA .
    docker push $IMAGE:$SHA
```

## Multi-Arch Images

Build for amd64 + arm64 (Graviton):
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t image:v1 --push .
```

Single tag; manifest list with both arches. Runtime picks right.

## Layer Caching

ECR caches popular layers across pulls in same region (Fargate / EKS).

Multi-stage Dockerfiles + cache from previous build accelerate.

## Vulnerability Management

Workflow:
1. Push image
2. Scan reports CVEs
3. Block deploy if HIGH/CRITICAL (policy)
4. Rebuild with patched base
5. Verify clean

OR: trivy in CI before push.

## Common Mistakes

- `latest` in production
- No lifecycle (storage bloat)
- Public bucket-style sharing (use cross-account)
- Plaintext creds in CI (use OIDC)
- No image scanning
- Mutable tags in prod

## Best Practices

- Immutable tags for production
- Lifecycle policy (keep N; expire untagged)
- Image scanning enabled
- Multi-arch where applicable
- Pull-through cache for upstream
- Cross-region replication for DR
- VPC endpoint for ECR (no NAT cost)

## VPC Endpoints for ECR

ECR API + ECR DKR + S3 (storage backend) endpoints:
- Pull from EKS / ECS in private subnet
- No NAT GW data transfer
- Faster

3 interface endpoints + S3 gateway endpoint.

Cost: ~$66/mo per region (~$22 × 3) but saves NAT for high image traffic.

## Monitoring

CloudWatch metrics:
- RepositoryPullCount
- RepositoryPushCount

CloudTrail: image push / pull events.

For scanning findings: EventBridge rule → Lambda → Slack alert.

## Quick Refs

```bash
# Create
aws ecr create-repository --repository-name myapp

# Auth
aws ecr get-login-password | docker login --username AWS --password-stdin 123.dkr.ecr.us-east-1.amazonaws.com

# Push
docker push 123.dkr.ecr.us-east-1.amazonaws.com/myapp:v1

# Scan
aws ecr start-image-scan --repository-name myapp --image-id imageTag=v1

# Findings
aws ecr describe-image-scan-findings --repository-name myapp --image-id imageTag=v1

# Lifecycle policy
aws ecr put-lifecycle-policy --repository-name myapp --lifecycle-policy-text file://lc.json
```

## Interview Prep

**Mid**: "ECR vs Docker Hub."

**Senior**: "Image scanning in CI/CD."

**Staff**: "Supply chain security for images."

## Next Topic

→ [T05 — App Mesh](T05-App-Mesh.md)
