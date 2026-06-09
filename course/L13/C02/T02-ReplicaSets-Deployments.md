# L13/C02/T02 — ReplicaSets & Deployments

## Learning Objectives

- Use Deployments correctly
- Manage rollouts

## ReplicaSet

Maintains N replicas of pod:
```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: web-rs
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:1.27
```

If pod deleted/crashes: ReplicaSet creates new. Always 3 pods.

Rarely used directly. Use Deployment.

## Deployment

Higher-level: manages ReplicaSets for rollout/rollback.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 25%
      maxSurge: 25%
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:1.27
```

## Hierarchy

```
Deployment
  ↓ creates
ReplicaSet (per version)
  ↓ creates
Pods
```

For each Deployment update: new ReplicaSet; old kept for rollback.

## Rollout Strategies

### RollingUpdate (Default)
- New pods created
- Old terminated gradually
- Zero downtime (if probes pass)

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 25%   # max old removed at once
    maxSurge: 25%         # max above desired during update
```

For 8 replicas, 25%/25%:
- Up to 2 new (above 8 = 10)
- Up to 2 old removed
- Net: 6-10 available during rollout

### Recreate
- Terminate all old
- Then create new
- Downtime!

For: when old and new can't coexist (DB migration).

## Update Triggers

Any change to Pod template triggers rollout:
- Image change
- Env var
- Volume
- Resource

```bash
kubectl set image deployment/web web=nginx:1.28
```

Or edit YAML; apply.

## Rollout Commands

```bash
# Status
kubectl rollout status deployment/web

# History
kubectl rollout history deployment/web

# Specific revision
kubectl rollout history deployment/web --revision=2

# Undo (rollback)
kubectl rollout undo deployment/web                    # last
kubectl rollout undo deployment/web --to-revision=2

# Pause / resume
kubectl rollout pause deployment/web
kubectl rollout resume deployment/web

# Restart (force restart without spec change)
kubectl rollout restart deployment/web
```

## Revision History

`spec.revisionHistoryLimit` (default 10): old ReplicaSets kept.

For rollback. After: garbage collected.

## Selector + Labels

Selector matches pod labels:
- Pod must have all selector labels
- Pod may have additional labels
- Selector immutable

If you change selector: ReplicaSet doesn't know its pods; chaos.

## maxSurge / maxUnavailable

Numeric or percentage:
- `1` or `25%`

For 8 replicas:
- maxSurge=2: up to 10 during rollout
- maxUnavailable=2: at least 6 during rollout
- Combined: 6-10 pods running

For zero-downtime tight: `maxUnavailable: 0`, `maxSurge: 25%`.

## Probes Importance

During rollout:
- New pod created
- Probes determine "Ready"
- If readiness fails: traffic doesn't route there; rollout pauses (won't progress)
- If liveness fails: pod restarted

Without probes: rollout may "succeed" but pods broken (no traffic).

## Failed Rollout

Detection:
```bash
kubectl rollout status deployment/web --timeout=5m
# Exit non-zero if not progressed in time
```

`progressDeadlineSeconds` (default 600s): max time for progress.

After deadline: Deployment Failed condition.

CI catches: undo:
```bash
kubectl rollout undo deployment/web
```

## Scaling

```bash
kubectl scale deployment/web --replicas=10
```

Or HPA (autoscaling; covered C08).

## Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

For: scale on metrics.

## Deployment Strategies

### Blue/Green
- Run both versions
- Cut traffic when new validated
- Quick rollback (cut back)
- Not native K8s; use Argo Rollouts / Flagger

### Canary
- 5% traffic to new
- Monitor
- Gradually 10%, 50%, 100%
- Use Argo Rollouts / Flagger / Istio

### Shadow
- Send copy of traffic to new (don't respond)
- Verify behavior
- Real for testing under load

## Argo Rollouts

CRD for advanced strategies:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
spec:
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 5m}
      - setWeight: 30
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 5m}
      - setWeight: 100
```

For canary, blue/green with analysis (Prometheus metrics).

## PodDisruptionBudget (PDB)

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: web
```

Prevents voluntary disruptions (drain) from violating:
- node drain
- kubectl delete pod

Doesn't apply to involuntary (node crash).

## Sticky Sessions

Pods stateless ideally. For session affinity: at LB level (sticky cookie).

Avoid: state in pod memory (replicas lose state).

## Best Practices

- Deployment (not bare ReplicaSet)
- Always probes
- Resource requests + limits
- Rolling update with surge
- PDB
- Topology spread
- Anti-affinity (replicas on different nodes)
- Rollback tested

## Common Mistakes

- maxUnavailable too high (downtime during rollout)
- No readiness probe (rollout completes but broken)
- progressDeadlineSeconds default too short for slow apps
- Same labels across Deployments (selector matches wrong pods)
- Updating template without changing labels causes confusion

## Restart Pattern

To restart all pods without spec change:
```bash
kubectl rollout restart deployment/web
```

Updates pod template's annotation; triggers rollout.

For: pick up new ConfigMap (mounted files don't auto-restart; env vars don't update).

## ConfigMap / Secret Changes

Mounted as files: app sees update on next read.
Env vars: NO update (pod must restart).

For env var changes: restart deployment.

For automatic: Reloader operator (kube-reloader).

## Image Pull Policy

```yaml
imagePullPolicy: IfNotPresent  # default unless tag is "latest"
imagePullPolicy: Always         # for "latest"
imagePullPolicy: Never          # local only
```

Always: every pod start re-pulls (bandwidth, time).
IfNotPresent: trust tag immutability.

For prod: pin to specific tag; IfNotPresent.

## Deployment Conditions

```bash
kubectl describe deployment web
```

Conditions:
- `Progressing`: rollout in progress / done
- `Available`: enough replicas Ready
- `ReplicaFailure`: can't create pods

## Annotations

`kubectl.kubernetes.io/restartedAt`: track restart.
`deployment.kubernetes.io/revision`: revision tracking.

## kubectl Commands

```bash
kubectl create deployment web --image=nginx
kubectl scale deployment/web --replicas=3
kubectl set image deployment/web web=nginx:1.28
kubectl rollout status deployment/web
kubectl rollout undo deployment/web
kubectl delete deployment/web

# Edit live
kubectl edit deployment/web

# YAML
kubectl get deployment/web -o yaml
```

## Quick Refs

```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0     # zero downtime
      maxSurge: 25%
  template:
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels: {app: web}
            topologyKey: kubernetes.io/hostname
```

## Interview Prep

**Junior**: "Deployment vs ReplicaSet."

**Mid**: "Rolling update mechanics."

**Senior**: "Zero downtime deploy."

**Staff**: "Canary deploy design."

## Next Topic

→ [T03 — StatefulSets](T03-StatefulSets.md)
