# L30/C01/T01 — End-to-End CI/CD Platform: Architecture

## Learning Objectives

- Build CI/CD portfolio project
- Cover full lifecycle

## Goal

Production-grade CI/CD:
- Build / test / deploy
- Multi-env
- Security gates
- Observability

For: showcase senior+ skills.

## Architecture

```
GitHub → GitHub Actions (CI)
              ↓ build image
          ECR / GHCR
              ↓
          Update manifest (Git)
              ↓
          ArgoCD → K8s (staging, prod)
              ↓
          Prometheus + Grafana
```

## Components

### CI
- GitHub Actions
- Linting / tests / SAST
- Build image
- Push to registry
- SBOM, signature

### CD
- ArgoCD
- GitOps
- Multi-cluster (staging, prod)

### Infra
- AWS EKS
- Terraform / Crossplane
- Multi-AZ

### Observability
- Prometheus
- Grafana
- Loki
- Tempo (traces)

### Security
- Trivy (image scan)
- Cosign signing
- OIDC for auth

## Tech Stack

- GitHub Actions
- ArgoCD
- AWS EKS
- Terraform
- Helm
- Prometheus / Grafana / Loki
- Trivy / Cosign
- OPA Gatekeeper / Kyverno

## Document

GitHub:
- README with diagram
- Setup instructions
- Decisions documented
- Lessons learned

## Demonstrate

- Live demo (video)
- Public repo (clean)
- Blog post

For: portfolio piece.

## Best Practices

- Production patterns
- Documented decisions
- Tests
- Observability built-in

## Common Mistakes

- Toy project (small)
- Skipping prod patterns
- No docs
- No demo

## Quick Refs

```
Stack: GitHub Actions + ArgoCD + AWS EKS + Observability
Patterns: GitOps + multi-env + security + observability
Output: GitHub repo + blog + demo video
```

## Next Topic

→ [T02 — IaC for Underlying Infra](T02-IaC-CICD.md)
