# L25/C02/T02 — Chaos Mesh

## Learning Objectives

- Install Chaos Mesh
- Run experiments

(Covered L19/C07/T02 — referencing here.)

## Chaos Mesh

CNCF; K8s-native:
- Many fault types
- CRD-based
- UI (Dashboard)

## Install

```bash
helm install chaos-mesh chaos-mesh/chaos-mesh \
  --namespace chaos-mesh --create-namespace
```

## Fault Types

- PodChaos (kill, fail)
- NetworkChaos (delay, loss, partition)
- StressChaos (CPU, memory)
- IOChaos (disk)
- TimeChaos (clock skew)
- DNSChaos (DNS errors)
- HTTPChaos (request manipulation)
- KernelChaos
- AWSChaos / GCPChaos / AzureChaos

## PodChaos Example

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-kill-test
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces: [prod]
    labelSelectors:
      app: my-app
  scheduler:
    cron: '@every 10m'
```

## NetworkChaos

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
spec:
  action: delay
  mode: all
  selector: ...
  delay:
    latency: '100ms'
    jitter: '20ms'
  duration: '5m'
```

## Workflow

Multi-step:
```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: Workflow
spec:
  entry: the-entry
  templates:
    - name: the-entry
      templateType: Serial
      children: [step1, step2]
```

## Dashboard

```bash
kubectl port-forward -n chaos-mesh svc/chaos-dashboard 2333:2333
```

Web UI for experiments.

## Best Practices

- Test in dev first
- Limit blast
- Monitor during
- Schedule (cron)

## Quick Refs

```bash
kubectl apply -f chaos.yaml
kubectl get podchaos / networkchaos / etc.
```

## Interview Prep

**Mid**: "Chaos Mesh."

**Senior**: "Run experiments."

## Next Topic

→ [T03 — Litmus](T03-Litmus.md)
