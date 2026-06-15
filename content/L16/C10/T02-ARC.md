# L16/C10/T02 — ARC (Actions Runner Controller)

## Learning Objectives

- Install ARC
- Operate at scale

## ARC

GitHub-official:
- K8s operator
- Auto-scales runners
- Per-job pods (ephemeral)

## Install

```bash
helm install arc \
  --namespace arc-systems \
  --create-namespace \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller
```

## Runner Scale Set

```bash
helm install arc-runner-set \
  --namespace arc-runners \
  --create-namespace \
  --set githubConfigUrl=https://github.com/myorg/myrepo \
  --set githubConfigSecret.github_token=$GH_TOKEN \
  --set maxRunners=10 \
  oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set
```

## Use

```yaml
# In workflow
jobs:
  test:
    runs-on: arc-runner-set
    steps:
      - uses: actions/checkout@v4
      - run: make test
```

GitHub queues → ARC sees → spawns pod.

## Per-Job Pods

Pod started for each job:
- Ephemeral
- Isolated
- Destroyed after

For: clean state.

## Resource Limits

```yaml
runnerSpec:
  resources:
    requests: { cpu: 1, memory: 2Gi }
    limits: { cpu: 4, memory: 8Gi }
```

Per-job. Right-size.

## Custom Image

```yaml
runnerSpec:
  containers:
    - name: runner
      image: ghcr.io/myorg/custom-runner:latest
```

Pre-install:
- Build tools
- Common deps
- Languages

For: fast job starts.

## Network Access

Inside cluster:
- Internal services accessible
- Private registries
- VPN

For: tests against internal.

## Secrets

```yaml
runnerSpec:
  containers:
    - name: runner
      env:
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: ci-secrets
              key: api-key
```

K8s secrets to runner.

## DinD (Docker in Docker)

```yaml
runnerSpec:
  containers:
    - name: dind
      image: docker:dind
      securityContext:
        privileged: true
```

For: docker build inside.

Risk: privileged.

## Buildah / Kaniko (Rootless)

Better than DinD:
```yaml
- name: build
  image: quay.io/buildah/stable
  command: [buildah, bud, -t, IMAGE]
```

No privileged.

## Multi-Repo / Org

One scale set per org:
```yaml
githubConfigUrl: https://github.com/myorg
```

Or per repo. Per-org cheaper at scale.

## Scaling

```yaml
minRunners: 0
maxRunners: 50
```

ARC scales based on:
- Queued jobs
- Min/max limits

## Karpenter Integration

ARC creates pods → unschedulable → Karpenter provisions node.

For: end-to-end auto-scale.

## Auth

### PAT (Personal Access Token)
Quick start. Avoid in prod.

### GitHub App
Recommended:
- Per-repo / per-org permissions
- Rotatable
- Auditable

```bash
# Install GitHub App for org
# Get app-id, install-id, private-key
helm install arc-runner-set \
  --set githubConfigSecret.github_app_id=ID \
  --set githubConfigSecret.github_app_installation_id=INST \
  --set-file githubConfigSecret.github_app_private_key=key.pem
```

## RBAC

```yaml
# ServiceAccount for runners
spec:
  template:
    spec:
      serviceAccountName: ci-runner-sa
```

Limit access.

## Best Practices

- GitHub App (not PAT)
- Per-org scale set
- Ephemeral pods
- Image pre-warm
- Karpenter for nodes
- Resource limits
- Network isolation

## Common Mistakes

- PAT in prod
- Persistent runners (CVE risk)
- Wide RBAC
- No resource limits (DoS)
- Privileged everywhere

## Security

- No fork PR jobs (or sandboxed)
- Network policies
- Pod Security Standards
- Audit logs

## Cost

For active org:
- Self-hosted (spot + Karpenter): often 50%+ cheaper
- But: more ops time

For: justify with usage data.

## Quick Refs

```bash
# Install
helm install arc oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller

# Scale set
helm install RUNNER_SET oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set --set githubConfigUrl=URL --set ...

# Use
runs-on: RUNNER_SET
```

## Interview Prep

**Mid**: "What's ARC."

**Senior**: "Self-hosted at scale."

**Staff**: "Runner architecture."

## Next Topic

→ [T03 — Security Considerations](T03-Runner-Security.md)
