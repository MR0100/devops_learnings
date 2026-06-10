# L16/C02/T02 — GitHub-Hosted vs Self-Hosted Runners

## Learning Objectives

- Choose runner type
- Operate self-hosted

## GitHub-Hosted

Free / paid; managed:
- Ubuntu, macOS, Windows
- Fresh VM per job
- Pre-installed tools
- No maintenance

```yaml
runs-on: ubuntu-latest
```

## Limits (Free Tier)

- 2000 min/mo (free repos)
- 6 hours per job
- 20 concurrent
- 1 GB cache

Pro: more.

## Costs (Paid)

- Linux: $0.008/min
- macOS: $0.08/min
- Windows: $0.016/min

Free 2000 min then per-minute.

## Larger Runners

```yaml
runs-on: ubuntu-latest-4-cores
runs-on: ubuntu-latest-16-cores
```

More CPU/RAM; cost more.

## Self-Hosted

Your hardware:
```yaml
runs-on: self-hosted
runs-on: [self-hosted, linux, gpu]
```

For:
- Custom hardware
- Pre-installed deps
- VPN access (internal services)
- Cost (own infra)
- Compliance

## Install

```bash
# Download runner
curl -o actions-runner.tar.gz -L https://github.com/actions/runner/releases/...
tar xzf actions-runner.tar.gz

# Register
./config.sh --url REPO_URL --token TOKEN

# Run
./run.sh
```

Or as service.

## Repo / Org / Enterprise

- Repo: scope to one repo
- Org: across repos
- Enterprise: many orgs

For: shared at scale.

## Labels

```yaml
runs-on: [self-hosted, gpu, linux]
```

Tag runners; jobs match.

## Security

Self-hosted security concerns:
- Untrusted PR code → runner
- Persistent state (cache poisoning)
- Network access

Mitigations:
- Ephemeral runners (delete after job)
- Don't allow PRs from forks
- Network-isolated

## Ephemeral Runners

ARC (Actions Runner Controller, K8s):
```yaml
spec:
  template:
    spec:
      containers:
      - name: runner
        image: ghcr.io/actions/actions-runner
```

Per-job pod. Destroyed after.

## ARC

K8s operator:
```bash
helm install arc oci://ghcr.io/actions/actions-runner-controller-charts/gha-runner-scale-set-controller
```

Then per-runner set:
```yaml
apiVersion: actions.github.com/v1alpha1
kind: AutoscalingRunnerSet
spec:
  githubConfigUrl: https://github.com/myorg/myrepo
  minRunners: 1
  maxRunners: 10
```

Scales based on queue.

## Karpenter for Runners

Spot EC2 for runners (cheap):
- Karpenter provisions nodes
- ARC schedules pods
- Auto-scale

For: cost-efficient.

## When Self-Hosted

- Cost (heavy CI usage)
- Hardware (GPU, ARM)
- Network (internal access)
- Compliance
- Custom env

## When GitHub-Hosted

- Small to medium usage
- No special hardware
- Want simplicity
- Public repos (free)

## Hybrid

```yaml
test:
  runs-on: ubuntu-latest  # GitHub-hosted
deploy:
  runs-on: self-hosted    # custom (VPN)
```

Use both per job.

## macOS

macOS only on:
- GitHub-hosted (expensive)
- Self-hosted Mac (Mac mini farm)

For iOS builds: required.

## Windows

GitHub-hosted Windows: more expensive than Linux.

For: .NET Framework, Windows builds.

## Concurrency

Self-hosted:
- More controllable
- Scale with K8s

Hosted:
- Plan-based limits

## Best Practices

- GitHub-hosted default
- Self-hosted for special needs
- ARC for K8s-based
- Ephemeral (don't reuse runners)
- Network isolation
- No PR-from-fork on self-hosted
- Cache cleanup

## Common Mistakes

- Persistent self-hosted (CVEs)
- PR from forks (exfiltration risk)
- No labels (random runner assignment)
- Over-provisioning (cost)

## Cost Compare

GitHub-hosted 10000 min/mo:
- Free 2000 + 8000 × $0.008 = $64/mo

Self-hosted on EC2 c5.large × 5 24/7:
- ~$300/mo

For low usage: GitHub-hosted cheaper.
For high usage: self-hosted with autoscale cheaper.

## Quick Refs

```yaml
# GitHub-hosted
runs-on: ubuntu-latest
runs-on: ubuntu-latest-4-cores

# Self-hosted
runs-on: self-hosted
runs-on: [self-hosted, linux, gpu]

# Label
./config.sh --labels gpu
```

## Interview Prep

**Mid**: "Runner types."

**Senior**: "Self-hosted strategy."

**Staff**: "Runner platform."

## Next Topic

→ [T03 — Reusable Workflows & Composite Actions](T03-Reusable-Workflows.md)
