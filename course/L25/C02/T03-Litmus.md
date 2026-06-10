# L25/C02/T03 — Litmus

## Learning Objectives

- Use Litmus
- Chaos hub

## Litmus

CNCF; chaos for K8s:
- ChaosCenter (UI)
- ChaosHub (shared experiments)
- ArgoCD integration

## Install

```bash
kubectl apply -f https://litmuschaos.github.io/litmus/2.14.0/litmus-2.14.0.yaml
```

## ChaosCenter

Web UI:
- Schedule experiments
- View results
- Multi-cluster

## Experiment

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: nginx-chaos
spec:
  appinfo:
    appns: 'default'
    applabel: 'app=nginx'
    appkind: 'deployment'
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: '60'
            - name: CHAOS_INTERVAL
              value: '10'
```

## Probes

```yaml
litmus.io/check-pre: |
  url: http://my-app/health
  expected: 200
```

Pre / during / post conditions.

## Workflow

Argo Workflows-style:
```yaml
spec:
  steps:
    - - name: install-experiment
        ...
    - - name: pod-delete
        ...
```

## ChaosHub

```bash
# Pull from hub
litmusctl pull experiment pod-delete
```

Community-shared.

## Best Practices

- ChaosCenter for ops
- Probes for safety
- Test in non-prod
- Audit results

## Quick Refs

```bash
kubectl get chaosengine / chaosresult
litmusctl
```

## Interview Prep

**Mid**: "What's Litmus."

**Senior**: "Litmus vs Chaos Mesh."

## Next Topic

→ [T04 — Gremlin](T04-Gremlin.md)
