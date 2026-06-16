# L16/C10 — Self-Hosted Runners at Scale

## Topics

- **T01 Karpenter-Backed Runners** — Spot + Karpenter for cost.
- **T02 ARC (Actions Runner Controller)** — Ephemeral GH Actions runners on K8s.
- **T03 Security Considerations** — Isolation, OIDC, secrets.

## Why Self-Hosted

- **Cost**: hosted minutes get expensive (~$0.008/min on GitHub Actions; spot k8s ~$0.0005/min)
- **Access**: private network resources without VPN tunnels
- **Performance**: bigger machines, NVMe, dedicated cores
- **Compliance**: data never leaves your network

## Actions Runner Controller (ARC)

K8s operator that manages ephemeral GitHub Actions runners.

```yaml
apiVersion: actions.github.com/v1alpha1
kind: AutoscalingRunnerSet
metadata:
  name: my-runners
  namespace: arc-runners
spec:
  githubConfigUrl: https://github.com/myorg
  githubConfigSecret: github-app-secret  # GitHub App auth
  minRunners: 0
  maxRunners: 50
  template:
    spec:
      containers:
        - name: runner
          image: ghcr.io/actions/actions-runner:latest
          resources:
            requests:
              cpu: 1
              memory: 4Gi
            limits:
              cpu: 4
              memory: 16Gi
```

Each workflow job → fresh pod → run → terminate. Ephemeral = secure.

## Karpenter for Runners

Karpenter provisions K8s nodes per runner demand:
- Spot instances (cheap)
- Right-sized per workload
- Auto-scale to zero when no jobs

```yaml
apiVersion: karpenter.k8s.aws/v1
kind: NodePool
metadata:
  name: runners
spec:
  template:
    metadata:
      labels:
        purpose: ci-runners
    spec:
      taints:
        - key: ci
          effect: NoSchedule
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]
        - key: node.kubernetes.io/instance-type
          operator: In
          values: ["c6i.2xlarge", "c6i.4xlarge"]
  disruption:
    consolidationPolicy: WhenEmpty
    consolidateAfter: 1m
```

Result: idle = 0 nodes; busy = up to 50 large nodes, mostly spot.

## GitLab Runner on K8s

```yaml
runners:
  config: |
    [[runners]]
      [runners.kubernetes]
        namespace = "gitlab-runners"
        cpu_limit = "4"
        memory_limit = "8Gi"
        privileged = true   # only for DinD; avoid otherwise
```

Auto-scales pods per job.

## Security Considerations

### Isolation
- Ephemeral runners (fresh per job — KEY)
- Per-team namespaces (RBAC isolates)
- Pod Security Standards: restricted
- Network policies (runners can talk to needed deps only)

### Avoid Privilege
- Don't run as root in runner image
- Don't use `privileged: true` (avoid DinD; use Kaniko/BuildKit instead)
- Drop capabilities; seccomp default

### Secrets
- GitHub Actions secrets injected per job (ephemeral)
- For cloud auth: OIDC to assume role, not static creds
- Vault sidecar for app-level secrets

### Repo Access
- Limit runner sets to specific repos/orgs
- Don't share runners across security boundaries (e.g., open-source repos shouldn't share runners with private)

## Cost Model

```
GitHub-hosted (small): free 2000 min/mo private; then $0.008/min
GitHub-hosted (large): $0.064/min for 16-core
Self-hosted on EKS Spot c6i.2xlarge: ~$0.00067/min per core, includes machine
```

Math for ~30K min/month of large builds:
- Hosted: $30K/year+ for "premium" runners
- Self-hosted on K8s + Spot: ~$2-5K/year

## DinD Alternative for Image Builds

Don't mount `/var/run/docker.sock`. Use:
- **Kaniko**: builds in userland (no daemon)
- **BuildKit** rootless
- **Buildah** (Podman ecosystem)

## ARC + Spot = The Modern Setup

End-to-end:
1. PR opened
2. GitHub Actions workflow triggers
3. ARC controller sees pending job
4. ARC creates ephemeral runner pod
5. K8s scheduler can't fit it
6. Karpenter provisions spot node in seconds
7. Runner pod schedules, runs job
8. Runner pod completes, deleted
9. Karpenter consolidates (kills empty node)

Result: scale to zero idle, scale to N parallel jobs in minutes.

## Interview Themes

- "Self-hosted runners — why and how?"
- "ARC + Karpenter design"
- "Runner security at scale"
- "Cost comparison hosted vs self-hosted"
- "DinD risks — how to avoid?"
