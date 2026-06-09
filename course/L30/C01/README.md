# L30/C01 — Project 1: End-to-End CI/CD Platform

## Topics

- **T01 Architecture** — Components
- **T02 IaC for Underlying Infra** — Terraform foundation
- **T03 Jenkins/GitHub Actions + ArgoCD** — Pipeline + deploy
- **T04 Observability Stack** — Metrics, logs, traces
- **T05 Security Gates** — Quality + signing

## Goal

Build a working CI/CD platform you can demo. Shows you can integrate everything taught in the course.

## Outcomes
- Public GitHub repo
- README with architecture
- Working deploy in a sample app
- Observability dashboards
- 5-min Loom walkthrough
- Blog post about lessons learned

## Architecture

```
[GitHub repo]
   ↓ webhook
[GitHub Actions]
   - Lint, test, build
   - SBOM gen, vulnerability scan
   - Push to ECR (signed via Cosign)
   ↓
[ArgoCD]
   - Watch manifests repo
   - Deploy to EKS (dev → staging → prod)
   - Verify via probes
   ↓
[EKS cluster]
   - Karpenter for scaling
   - Istio for mesh + mTLS
   - Sample app deployed
   ↓
[Observability]
   - Prometheus / Grafana
   - Loki for logs
   - Tempo for traces
```

## Infrastructure as Code

```
infrastructure/
├── modules/
│   ├── vpc/
│   ├── eks/
│   ├── ecr/
│   └── monitoring/
├── live/
│   └── prod/
│       ├── network/
│       │   ├── main.tf  # uses vpc module
│       │   └── ...
│       ├── cluster/
│       │   ├── main.tf  # uses eks module
│       │   └── ...
│       └── observability/
└── README.md
```

### Sample EKS Module
```hcl
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"
  
  cluster_name = "platform"
  cluster_version = "1.30"
  
  vpc_id = data.aws_vpc.this.id
  subnet_ids = data.aws_subnets.private.ids
  
  eks_managed_node_groups = {
    default = {
      instance_types = ["m6i.large"]
      min_size = 1
      max_size = 5
      desired_size = 2
    }
  }
  
  cluster_addons = {
    coredns = {}
    kube-proxy = {}
    vpc-cni = {}
    eks-pod-identity-agent = {}
  }
}
```

## CI/CD with GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  id-token: write
  contents: read
  packages: write

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with: { go-version: '1.22', cache: true }
      - run: go test ./...

  scan:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@master
        with: { scan-type: 'fs', severity: 'HIGH,CRITICAL', exit-code: '1' }
      - uses: gitleaks/gitleaks-action@v2

  build:
    needs: scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123:role/gha-deployer
          aws-region: us-east-1
      - uses: aws-actions/amazon-ecr-login@v2
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: 123.dkr.ecr.us-east-1.amazonaws.com/app:${{ github.sha }}
          sbom: true
          provenance: true
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - run: cosign sign --yes 123.dkr.ecr.us-east-1.amazonaws.com/app:${{ github.sha }}

  update-manifest:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { repository: org/manifests }
      - run: |
          yq -i '.spec.template.spec.containers[0].image = "123.dkr.ecr.us-east-1.amazonaws.com/app:${{ github.sha }}"' \
            apps/app/deployment.yaml
          git config user.email "ci@example.com"
          git add . && git commit -m "Update app to ${{ github.sha }}"
          git push
```

## ArgoCD Deploy

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/manifests
    targetRevision: HEAD
    path: apps/app
  destination:
    server: https://kubernetes.default.svc
    namespace: app
  syncPolicy:
    automated: { prune: true, selfHeal: true }
    syncOptions: [CreateNamespace=true]
```

## Observability Stack

```bash
# Install kube-prometheus-stack (Prom + Grafana)
helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  -f monitoring-values.yaml

# Install Loki
helm install loki grafana/loki \
  -n logging --create-namespace \
  -f loki-values.yaml

# Install Tempo  
helm install tempo grafana/tempo \
  -n tracing --create-namespace

# Install OTel Collector
helm install otel open-telemetry/opentelemetry-collector \
  -n observability --create-namespace \
  -f otel-values.yaml
```

Configure Grafana datasources pointing to all three.

## Security Gates

In CI:
- Trivy image scan (block HIGH+ CVEs)
- Gitleaks secret scan
- Semgrep SAST
- Cosign sign every image
- SBOM generation + attach

In K8s (admission control):
- Sigstore Policy Controller — verify image signatures
- Pod Security Standards — restricted

## Verification

Build a sample Go app with:
- `/healthz` endpoint
- `/metrics` (Prometheus)
- OTel traces emitted
- Structured logs to stdout

Deploy via the pipeline. Verify:
- Image signed + signed
- ArgoCD synced
- Pod running
- Logs in Loki
- Traces in Tempo
- Metrics in Prometheus
- Grafana dashboards show data

## Demo Script

5-min Loom:
1. Architecture diagram (30s)
2. Make a code change in repo (30s)
3. Show GHA build (1 min)
4. Show ArgoCD sync (30s)
5. Verify pod running, logs/metrics flowing (1 min)
6. Show dashboards (1 min)
7. Lessons learned (30s)

## What to Highlight

- Full automation from commit to production
- Security at every step
- Observability everywhere
- IaC for infrastructure
- GitOps for application

## README Template

```markdown
# End-to-End CI/CD Platform

## What This Demonstrates
- Modern CI/CD with security and observability
- IaC-driven AWS infrastructure
- GitOps deploy via ArgoCD
- Multi-pillar observability

## Architecture
[diagram]

## How to Run
1. Bootstrap with `terraform apply` in `infrastructure/live/prod/`
2. Install observability stack: `make observability`
3. Deploy app: GitHub Actions auto-deploys on push to main
4. Verify: see Grafana dashboards

## Key Files
- `infrastructure/` — Terraform
- `.github/workflows/` — CI
- `manifests/` — K8s + ArgoCD
- `app/` — sample Go app

## Cost
- ~$100/month to run continuously
- Tear down with `terraform destroy`

## Lessons Learned
- [Specific things you discovered]
```

## Interview Themes

- "Walk me through your CI/CD project"
- "Why these tools?"
- "What was hardest?"
- "How would you scale this?"
- "Security tradeoffs you made"
