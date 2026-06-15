# L15/C07/T02 — Flagger, Argo Rollouts

## Learning Objectives

- Use Flagger or Argo Rollouts
- Auto-promote / rollback

## Progressive Delivery

Combines:
- Canary
- Feature flags
- Metric analysis
- Auto rollback

## Argo Rollouts

K8s controller; CRD replaces Deployment:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: { duration: 5m }
      - setWeight: 50
      - pause: { duration: 5m }
      - setWeight: 100
      analysis:
        templates:
        - templateName: success-rate
  selector:
    matchLabels:
      app: myapp
  template: ...   # like Deployment
```

## Install

```bash
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f \
  https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
```

CLI:
```bash
curl -LO https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-amd64
chmod +x kubectl-argo-rollouts-linux-amd64
sudo mv kubectl-argo-rollouts-linux-amd64 /usr/local/bin/kubectl-argo-rollouts
```

## Analysis

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  args:
  - name: service-name
  metrics:
  - name: success-rate
    interval: 30s
    successCondition: result[0] >= 0.99
    failureLimit: 3
    provider:
      prometheus:
        address: http://prometheus:9090
        query: |
          sum(rate(istio_requests_total{destination_workload="{{args.service-name}}",response_code!~"5.."}[1m]))
          /
          sum(rate(istio_requests_total{destination_workload="{{args.service-name}}"}[1m]))
```

## Step Types

```yaml
steps:
- setWeight: 20
- pause: { duration: 5m }
- pause: {}  # indefinite; manual promote
- setCanaryScale:
    replicas: 1   # scale canary independently
- analysis:
    templates:
    - templateName: ...
```

## Promotion

```bash
# Manual
kubectl argo rollouts promote myapp

# Skip analysis
kubectl argo rollouts promote myapp --skip-current-step

# Abort
kubectl argo rollouts abort myapp

# Pause
kubectl argo rollouts pause myapp

# Resume
kubectl argo rollouts resume myapp

# Restart
kubectl argo rollouts restart myapp
```

## Traffic Management

### Without mesh
Argo Rollouts uses Deployment + ReplicaSet to control weight via pod count.

5 stable + 1 canary = ~17% canary traffic (via Service round-robin).

### With Istio
Argo Rollouts updates VirtualService:
```yaml
strategy:
  canary:
    trafficRouting:
      istio:
        virtualService:
          name: myapp
        destinationRule:
          name: myapp
          canarySubsetName: canary
          stableSubsetName: stable
```

Precise traffic %.

### With ALB / NGINX
ALB target group weights.

## Flagger

Similar; Flux-aligned.

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: myapp
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  service:
    port: 80
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 5
    metrics:
    - name: success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: latency
      thresholdRange:
        max: 500
      interval: 1m
```

## Flagger Auto

- Increase weight
- Check metrics
- If pass: continue
- If fail: rollback

For: hands-off.

## Metric Providers

- Prometheus
- Datadog
- CloudWatch
- New Relic
- Stackdriver
- Web

For: data-driven.

## Choosing

| | Argo Rollouts | Flagger |
|---|---|---|
| Maintainer | Intuit / Argo | Weaveworks (now CNCF) |
| Integration | Argo CD | Flux |
| K8s Native | CRD | CRD |
| Auto-promote | Yes | Yes |
| Mesh integration | Istio, Linkerd, etc. | Istio, Linkerd, Contour, etc. |
| UI | argo-rollouts dashboard | Custom |

For: pick based on ecosystem.

## Web Analysis

```yaml
provider:
  web:
    url: https://my-analysis-svc/api/check
    timeoutSeconds: 30
    jsonPath: "{$.healthy}"
```

Custom endpoint.

## Job Analysis

```yaml
provider:
  job:
    spec:
      ...
```

K8s Job runs check.

## Argo Rollouts Dashboard

```bash
kubectl argo rollouts dashboard
```

Visualize rollouts.

## Notifications

```yaml
spec:
  notifications:
    triggers:
    - on-rollout-step-completed
    services:
    - slack
```

For: visibility.

## Best Practices

- Use mesh for precise traffic
- AnalysisTemplate reusable
- Pre-promotion analysis
- Multiple metric checks
- Failure threshold > 1 (avoid flake)
- Notifications

## Common Mistakes

- Single metric (one fail metric ≠ rollback)
- failureLimit too low (rollback on transient)
- No analysis (just timer)
- Manual when should be auto

## ConfigMap / Secrets

Rollouts know about:
- ConfigMap
- Secret

```yaml
spec:
  template:
    spec:
      containers:
      - env:
        - valueFrom:
            configMapKeyRef:
              name: myconfig
```

Auto-restart on ConfigMap change (with annotation).

## ProgressDeadline

```yaml
spec:
  progressDeadlineSeconds: 600
```

If not progressed: failed.

## Antiaffinity

Spread pods:
```yaml
spec:
  template:
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: myapp
            topologyKey: kubernetes.io/hostname
```

Even during rollout.

## Quick Refs

```yaml
# Argo Rollouts
kind: Rollout
strategy:
  canary:
    steps: [ ... ]
    analysis: { templates: [...] }

# Flagger
kind: Canary
spec:
  analysis:
    metrics: [...]
    stepWeight: 5
    maxWeight: 50
```

```bash
# Argo
kubectl argo rollouts get rollout NAME
kubectl argo rollouts promote / abort / pause / resume NAME

# Flagger
kubectl get canary
kubectl describe canary NAME
```

## Interview Prep

**Mid**: "Argo Rollouts vs Flagger."

**Senior**: "Analysis templates."

**Staff**: "Progressive delivery platform."

## Next Topic

→ [T03 — Automated Rollback Triggers](T03-Automated-Rollback.md)
