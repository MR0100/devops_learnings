# L16/C10/T03 — Self-Hosted Runner Security

## Learning Objectives

- Secure self-hosted runners
- Avoid common attacks

## Threats

### Persistent State
Runners reused: previous job artifacts visible.
Mitigation: ephemeral.

### Fork PRs
Untrusted code from fork PRs.
Mitigation: don't run on self-hosted, or sandbox.

### Network Access
Runner reaches internal services.
Mitigation: network policies.

### Privileged Escalation
Privileged container → host compromise.
Mitigation: avoid privileged.

### Secret Exfiltration
Malicious workflow steals secrets.
Mitigation: scoped secrets, ephemeral.

## Best Practices

### Ephemeral
Per-job pod. Destroyed after.

```yaml
runnerSpec:
  ...
# ARC: ephemeral by default
```

### Don't Allow Fork PRs

```yaml
# Workflow
on:
  pull_request:
    branches: [main]

jobs:
  test:
    if: github.event.pull_request.head.repo.full_name == github.repository
    runs-on: self-hosted
```

Or use GitHub-hosted for forks.

### Use GitHub App, Not PAT

PAT: long-lived; broad.
App: per-org, fine-grained, rotatable.

### Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ci-runners
spec:
  podSelector:
    matchLabels:
      app: runner
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
            except:
              - 10.0.0.0/8   # block internal
```

For: limit blast radius.

### Pod Security Standards

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: arc-runners
  labels:
    pod-security.kubernetes.io/enforce: restricted
```

For: enforce safe defaults.

### Don't Use Privileged

For Docker build:
- Buildah / Kaniko (rootless)
- Not DinD privileged

### Image Hygiene

Custom runner image:
- Minimal base
- No build tools not needed
- Scanned for CVEs
- Pinned versions

### Scoped Secrets

Per-env / per-job:
```yaml
jobs:
  deploy:
    environment: production
    # Only prod secrets accessible
```

### OIDC for Cloud

No static cloud keys.

### Audit Logs

GitHub: workflow run logs.
K8s: audit log.
Cloud: CloudTrail / equivalent.

Correlate.

### Runner Image Updates

Regular: weekly.
CVEs: immediate.

### No Cross-Tenant Sharing

Per-team runner sets:
- Team A's runners isolated from Team B
- Different namespaces

For: tenant separation.

## Common Attacks

### Crypto Mining
Compromised workflow mines crypto on your runners.

Mitigation:
- Monitor CPU
- Network egress alerts
- Image scanning

### Lateral Movement
Workflow uses runner to access internal services.

Mitigation:
- NetworkPolicy
- Minimal RBAC

### Secret Leak
echo $SECRET in log; visible.

Mitigation:
- GitHub masks; but careful
- Don't print sensitive

### Build Tampering
Modify code mid-build (cache poisoning).

Mitigation:
- Ephemeral cache
- Signed artifacts

## Hardening Checklist

- [ ] Ephemeral runners
- [ ] GitHub App auth
- [ ] No fork PR on self-hosted
- [ ] NetworkPolicy
- [ ] Pod Security Standards
- [ ] No privileged (use Buildah)
- [ ] Image scanning
- [ ] OIDC for cloud
- [ ] Scoped secrets
- [ ] Audit logs aggregated
- [ ] Regular updates

## Auditing

```bash
# K8s
kubectl logs -n arc-runners -l app=runner | grep CRITICAL

# GitHub
GET /repos/owner/repo/actions/runs/RUN/logs

# Aggregate to SIEM
```

## Compliance

For PCI / HIPAA:
- Isolated runners
- Audit trail
- Encrypted storage
- Annual review

## Incident Response

Compromised runner:
- Revoke tokens
- Rotate secrets
- Audit recent runs
- Investigate

## Real Incidents

- 2022: Crypto mining via GitHub Actions self-hosted
- 2023: Multiple supply chain attacks
- 2024: Continued vigilance required

## Best Practices Recap

```
Ephemeral
Authenticated (GitHub App)
Isolated (network)
Restricted (PSS)
Scoped (secrets)
Audited (logs)
Updated (images)
Monitored (metrics)
```

## Common Mistakes

- Persistent runners
- PAT for auth
- Privileged DinD
- Wide network egress
- No PSS
- Stale images
- No monitoring

## Cost vs Security

Self-hosted:
- Cheaper at scale
- More security ops
- Trade-off

For: justify with risk analysis.

## Alternative: GitHub-Hosted

For untrusted (fork PRs): GitHub-hosted.
For trusted (main): self-hosted.

Hybrid.

## Quick Refs

```yaml
# Ephemeral
runnerSpec:
  # ARC default

# Network policy
kind: NetworkPolicy

# PSS
namespace labels:
  pod-security.kubernetes.io/enforce: restricted

# GitHub App
githubConfigSecret:
  github_app_id: ...
```

## Interview Prep

**Mid**: "Runner security risks."

**Senior**: "Hardening runners."

**Staff**: "Secure CI platform."

## Next Topic

→ Move to [L17 — Monitoring & Observability](../../L17/README.md)
