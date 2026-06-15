# L16/C03/T02 — GitLab Runners

## Learning Objectives

- Configure runners
- Choose executor

## Runner

Process that runs CI jobs:
- GitLab.com SaaS: shared runners
- Self-managed: your runners

## Install

```bash
# Linux
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt install gitlab-runner

# Register
sudo gitlab-runner register \
  --url https://gitlab.com \
  --token RUNNER_TOKEN \
  --executor docker \
  --docker-image alpine:latest
```

## Executors

### Shell
Run on host:
```yaml
[[runners]]
  executor = "shell"
```

For: simple; less isolated.

### Docker
Per-job container:
```yaml
[[runners]]
  executor = "docker"
  [runners.docker]
    image = "alpine:latest"
```

For: clean per job.

### Docker Machine
Spin EC2 / GCP VMs (deprecated).

### Kubernetes
Pod per job:
```yaml
[[runners]]
  executor = "kubernetes"
  [runners.kubernetes]
    namespace = "gitlab-runner"
    image = "alpine:latest"
```

For: K8s-native.

### VirtualBox / SSH
Less common.

## K8s Runner Helm

```bash
helm install gitlab-runner gitlab/gitlab-runner \
  --set runnerToken=TOKEN \
  --namespace gitlab-runner --create-namespace
```

Auto-scales pods.

## Concurrency

```yaml
concurrent = 10
```

Max concurrent jobs across all runners.

## Per-Runner

```yaml
[[runners]]
  limit = 5
```

Max for this runner.

## Tags

```yaml
[[runners]]
  tags = ["docker", "gpu"]
```

Jobs select via tag:
```yaml
job:
  tags:
    - gpu
```

## Shared vs Specific

- Shared: across projects in instance
- Group: across projects in group
- Specific: single project

## Cache

```yaml
[runners.cache]
  Type = "s3"
  Shared = true
  [runners.cache.s3]
    BucketName = "gitlab-cache"
    AwsAccessKeyID = "..."
    AwsSecretAccessKey = "..."
```

S3-backed cache; shared across runners.

For: distributed cache.

## Docker-in-Docker (dind)

```yaml
job:
  image: docker:latest
  services:
    - docker:dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  script:
    - docker build .
```

For: image builds.

## Privileged

dind requires privileged. Risk.

Alternatives:
- BuildKit / kaniko
- Buildah
- nerdctl

## GitLab.com Shared Runners

Free tier: limited minutes.

For sensitive: self-host.

## Self-Hosted on K8s

Best for scale:
- Auto-scale
- Spot instances (cheap)
- Isolated

## Auto-Scale

GitLab + K8s + cluster autoscaler:
- Pending pods → new nodes
- Idle nodes → scale down

For: cost.

## Security

- Run in isolated namespace
- No shared cache for sensitive
- Network policies
- No privileged unless needed

For: defense.

## Performance

Image caching:
- Cache base images
- Pre-pull on nodes
- Use local registry

For: fast starts.

## Monitoring

```bash
gitlab-runner --debug run

# Prometheus
[runners]
listen_address = "0.0.0.0:9252"
```

## Best Practices

- Docker / K8s executor (clean isolation)
- Tag for purpose
- S3 cache shared
- Avoid privileged
- Monitor capacity
- Auto-scale

## Common Mistakes

- Shell executor (state leakage)
- No cache (slow)
- Privileged everywhere (security)
- No tags (random assignment)

## Quick Refs

```bash
gitlab-runner register
gitlab-runner list
gitlab-runner verify
gitlab-runner unregister
gitlab-runner run
```

## Interview Prep

**Mid**: "GitLab runner executors."

**Senior**: "Runner architecture."

## Next Topic

→ [T03 — Auto DevOps](T03-Auto-DevOps.md)
