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

This is the flagship capstone because it touches every layer of the course at
once — IaC, containers, GitOps, supply-chain security, and observability — in a
single coherent system. An interviewer who sees this project can ask about any
of those and you'll have a real answer grounded in something you built.

## What This Project Demonstrates

- You can wire *commit → production* with no human running `kubectl`
- You understand **separation of concerns**: CI builds artifacts, CD (GitOps)
  reconciles desired state — they are different jobs with different blast radii
- You bake security into the pipeline (scan, sign, verify) rather than bolting
  it on
- You ship observability *with* the app, not as an afterthought

## Why These Choices (Rationale & Trade-offs)

- **GitOps (ArgoCD) over `kubectl apply` from CI** — Git is the single source of
  truth and the audit log; rollback is `git revert`; the cluster self-heals to
  the declared state. Trade-off: an extra repo and a reconciliation lag (seconds
  to a minute) versus the imperative speed of pushing straight from CI.
- **EKS over self-managed K8s** — you're showcasing platform skills, not
  etcd-babysitting. Managed control plane lets the project stay buildable in a
  weekend. Trade-off: ~$73/month control-plane cost and less low-level control.
- **GitHub Actions over Jenkins** — zero servers to run, OIDC to AWS (no
  long-lived keys), and the config lives next to the code. Jenkins is still
  common in enterprises; mention you can run either.
- **Separate app repo and manifests repo** — keeps the deploy history clean and
  lets ArgoCD watch manifests without CI write-looping on the app repo.

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

## Prerequisites

- AWS account with billing alerts set (this project costs money while running)
- Terraform, kubectl, helm, the AWS CLI, and a GitHub account
- Comfort with K8s basics (Deployments, Services) and a CI/CD mental model
- Roughly the material from L08 (AWS), L12–L13 (containers/K8s), L20 (supply
  chain), and L17 (observability)

## Build Order

1. **IaC foundation** (T02) — VPC, EKS, ECR via Terraform; remote state first
2. **CI pipeline** (T03) — build, test, scan, sign, push to ECR
3. **GitOps deploy** (T03) — ArgoCD watching the manifests repo
4. **Observability** (T04) — Prometheus/Grafana/Loki/Tempo; app instrumented
5. **Security gates** (T05) — block on CVEs, verify signatures at admission
6. **Polish** — README, architecture diagram, 5-min Loom, blog post

Build it incrementally and keep each layer green before adding the next — a
half-wired pipeline is harder to debug than five small ones.

## Cost & Time Estimate

- **Time**: ~2–3 focused days to first green deploy; ~1 week to portfolio-polished
- **Cost**: ~$100/month if left running continuously (EKS control plane ~$73,
  2× m6i.large ~$140 prorated, NAT/ELB/ECR the rest). **Tear down with
  `terraform destroy` between work sessions** — this is the single biggest way
  to keep the bill near zero.

## Acceptance Criteria

The project is "done" when, from a clean clone, you can demonstrate:

- A code push triggers CI that lints, tests, scans (blocks on HIGH/CRITICAL),
  builds, signs (Cosign), and pushes to ECR
- The manifests repo gets a commit and ArgoCD syncs it automatically
- The pod runs and admission control **rejects** an unsigned image (proves the
  gate works, not just exists)
- Grafana shows metrics, Loki shows the app's logs, Tempo shows a trace
- `git revert` of a deploy commit rolls the app back within a minute

## Document

GitHub:
- README with diagram
- Setup instructions
- Decisions documented (why each tool — the trade-offs above)
- Lessons learned

## Demonstrate

- Live demo (5-min Loom video, recorded so conference Wi-Fi can't kill it)
- Public repo (clean, real scope, working)
- Blog post turning the build into proof of depth

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
Cost: ~$100/mo running; destroy between sessions
```

## Interview Prep

**Junior**: "Walk me through your CI/CD project at a high level." — A push to
GitHub triggers GitHub Actions, which tests, scans, builds, signs, and pushes a
container image. The image tag is written into a separate manifests repo, and
ArgoCD notices the change and deploys it to EKS. Prometheus, Loki, and Tempo
give me metrics, logs, and traces for the running app.

**Mid**: "Why GitOps instead of deploying straight from CI?" — GitOps makes Git
the single source of truth and the audit log of what's running. The cluster
continuously reconciles to the declared state, so it self-heals and drift is
visible. Rollback is just `git revert`. Pushing `kubectl apply` from CI is
faster but loses all of that — no declarative history, no self-heal, and CI
credentials with cluster-admin become a juicy attack target.

**Senior**: "What was the hardest part and how did you reason about it?" — The
trade-offs around blast radius and credentials. I split the app repo from the
manifests repo so CI doesn't loop committing to itself and ArgoCD has a clean
deploy history. I used OIDC from Actions to AWS so there are no long-lived
keys. And I had to decide where security gates live — I block on CVEs in CI for
fast feedback, but I *also* verify signatures at K8s admission, because CI is a
control you own and admission is the control that protects the cluster even if
CI is bypassed.

**Staff**: "How would you scale this from one app to a 100-service estate?" — I'd
stop hand-writing ArgoCD Applications and move to ApplicationSets generated from
the catalog (this is exactly where the Backstage capstone plugs in). CI becomes
a reusable workflow / shared action so every service gets the same scan-sign-SBOM
guarantees for free. I'd push policy (signature verification, Pod Security) to
admission so it's enforced centrally rather than trusting each team's pipeline,
and I'd add progressive delivery (Argo Rollouts) so a bad deploy to one service
can't take the fleet down. The architecture doesn't change — the unit of
management moves from "an app" to "a template," which is the whole point of the
IDP capstone.

## Next Topic

→ [T02 — IaC for Underlying Infra](T02-IaC-CICD.md)
