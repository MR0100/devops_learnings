# L25/C02/T02 — Chaos Mesh

## Learning Objectives

- Install Chaos Mesh and understand its CRD-based execution model
- Pick the right fault CRD for a given experiment
- Chain faults into workflows and abort them safely

(Introduced in L19/C07/T02 — this is the chaos-specific deep dive.)

## Chaos Mesh

Chaos Mesh is a CNCF, Kubernetes-native chaos platform. Everything is a
**Custom Resource** — you `kubectl apply` a fault manifest and a controller
reconciles it onto the targeted pods, then automatically reverts when the
`duration` elapses or you delete the object. That declarative model is the
whole appeal: experiments are versioned YAML in Git, and the abort path is
`kubectl delete`.

- Broad fault catalog spanning pod, network, IO, kernel, time, and DNS
- CRD-based — GitOps-friendly, reviewable, reproducible
- Dashboard UI for authoring and observing experiments
- Faults injected per-pod via a privileged DaemonSet (`chaos-daemon`)

## Architecture

```
┌───────────────────┐   reconciles    ┌──────────────────────┐
│ chaos-controller  │ ──────────────▶ │ chaos-daemon         │
│ -manager (Deploy) │   CRD intent    │ (DaemonSet, per node)│
└───────────────────┘                 └─────────┬────────────┘
        ▲                                        │ enters target
        │ kubectl apply <chaos>.yaml             ▼ pod's netns/cgroup
   you / GitOps                            target container
```

The controller watches the CRDs; the daemon does the dirty work inside the
target's namespaces (tc for network, a sidecar for IO, etc.). No app changes
needed.

## Install

```bash
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm install chaos-mesh chaos-mesh/chaos-mesh \
  --namespace chaos-mesh --create-namespace \
  --set chaosDaemon.runtime=containerd \
  --set chaosDaemon.socketPath=/run/containerd/containerd.sock
```

The `runtime`/`socketPath` must match your nodes' container runtime or the
daemon can't enter target containers — the single most common install failure.

## Fault Types

| CRD            | Models                                                  |
|----------------|---------------------------------------------------------|
| PodChaos       | `pod-kill`, `pod-failure`, `container-kill`             |
| NetworkChaos   | delay, loss, duplicate, corrupt, partition, bandwidth   |
| StressChaos    | CPU and memory pressure                                 |
| IOChaos        | disk latency, errno faults, attr override, corruption   |
| TimeChaos      | clock skew (forward/back) — TLS, TOTP, scheduler tests  |
| DNSChaos       | DNS errors / wrong answers                              |
| HTTPChaos      | abort, delay, replace, patch HTTP requests/responses    |
| KernelChaos    | inject kernel-level failures (eBPF)                     |
| AWS/GCP/Azure  | cloud-resource faults (e.g. detach volume, stop node)   |

## PodChaos Example

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-kill-test
  namespace: chaos-mesh
spec:
  action: pod-kill          # pod-kill | pod-failure | container-kill
  mode: one                 # one | all | fixed | fixed-percent | random-max-percent
  selector:
    namespaces: [prod]
    labelSelectors:
      app: my-app
  duration: '30s'
```

`mode` is the blast-radius control: start at `one` (a single pod) and only widen
to `fixed-percent`/`all` once the experiment is boring. `pod-failure` makes a
pod unschedulable/unavailable without deleting it — useful to test how the
service behaves while a replica is *stuck* rather than cleanly gone.

## NetworkChaos

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: db-latency
spec:
  action: delay             # delay | loss | duplicate | corrupt | partition | bandwidth
  mode: all
  selector:
    namespaces: [prod]
    labelSelectors: { app: api }
  delay:
    latency: '100ms'
    jitter: '20ms'
    correlation: '50'       # % correlation between successive packets
  direction: to             # to | from | both
  target:                   # scope the fault to traffic toward postgres only
    mode: all
    selector:
      labelSelectors: { app: postgres }
  duration: '5m'
```

The `target` block is what makes NetworkChaos precise: this injects latency
*only* on the api→postgres path, not all of api's traffic. Without it you'd
degrade health checks and unrelated calls and muddy the signal.

## Workflow (chaining faults)

A `Workflow` orchestrates multiple faults — serial, parallel, or conditional —
to model a realistic incident rather than one isolated fault.

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: Workflow
metadata:
  name: cache-then-db
spec:
  entry: the-entry
  templates:
    - name: the-entry
      templateType: Serial
      children: [kill-cache, then-db-latency]
    - name: kill-cache
      templateType: PodChaos
      podChaos: { action: pod-kill, mode: all, selector: {labelSelectors: {app: redis}} }
    - name: then-db-latency
      templateType: NetworkChaos
      deadline: '5m'
      networkChaos: { action: delay, ... }
```

This models "cache dies, then the DB it now hammers gets slow" — the kind of
compound failure single faults miss.

## Dashboard

```bash
kubectl port-forward -n chaos-mesh svc/chaos-dashboard 2333:2333
```

The web UI authors experiments visually, shows live status, and exposes the
event log. In production, gate it behind RBAC and the token-based auth — a
Chaos Mesh dashboard is, by design, a button that breaks production.

## Abort

```bash
kubectl delete podchaos pod-kill-test       # revert this fault now
kubectl delete -f experiment.yaml            # revert everything in the file
```

Deleting the CRD triggers the controller to undo the fault. This is the
universal kill switch — verify it works before any prod experiment.

## Common Mistakes

- Wrong `chaosDaemon.runtime`/`socketPath` → daemon can't inject; faults silently no-op
- Omitting the `target` selector on NetworkChaos → degrading far more traffic than intended
- Starting at `mode: all` instead of `mode: one` → blast radius too wide on the first run
- Leaving the dashboard unauthenticated/exposed → anyone can break prod
- Setting no `duration` and forgetting the experiment is still running
- Reading results without a steady-state baseline, so the outcome is uninterpretable

## Best Practices

- Test every new fault in dev/staging first; confirm the revert path works
- Always scope with `selector` + (for network) `target`; default to `mode: one`
- Keep experiments as Git-versioned YAML; review them like any other change
- Pair the fault window with dashboards/alerts so you capture the signal
- Use `Workflow` to model compound failures, not just single isolated faults
- RBAC-gate the controller and dashboard; chaos is a privileged capability

## Quick Refs

```bash
helm install chaos-mesh chaos-mesh/chaos-mesh -n chaos-mesh --create-namespace
kubectl apply -f chaos.yaml                  # run an experiment
kubectl get podchaos|networkchaos|iochaos    # list running faults
kubectl delete -f chaos.yaml                 # abort / revert
kubectl port-forward -n chaos-mesh svc/chaos-dashboard 2333:2333
# CRDs: PodChaos NetworkChaos StressChaos IOChaos TimeChaos DNSChaos HTTPChaos KernelChaos
```

## Interview Prep

**Junior**: "What is Chaos Mesh?" — A CNCF, Kubernetes-native chaos tool where every fault is a Custom Resource you `kubectl apply`; it injects pod, network, IO, time, and DNS faults and reverts automatically.

**Mid**: "How do you run and safely abort an experiment?" — Apply a fault CRD (e.g. `PodChaos action: pod-kill, mode: one`) scoped by a label selector with a `duration`; abort by `kubectl delete` of the CRD, which makes the controller revert the fault.

**Senior**: "How do you keep a NetworkChaos experiment from being too broad?" — Set `mode: one` for blast radius and use the `target` selector so the fault only applies to one path (e.g. api→postgres) instead of all of the source's traffic, plus a `direction` to model the realistic flow.

**Staff**: "Design a compound-failure experiment in Chaos Mesh." — Use a `Workflow` to chain faults serially — kill the cache, then inject DB latency — to reproduce the cache-miss-storm-then-slow-DB cascade, gate it behind RBAC, run it in staging first with steady-state dashboards, and keep the manifests in Git so the experiment is reviewable and repeatable.

## Next Topic

→ [T03 — Litmus](T03-Litmus.md)
