# L25/C02/T03 — Litmus

## Learning Objectives

- Run Kubernetes chaos with LitmusChaos and its ChaosCenter control plane
- Use ChaosHub experiments and probes for safe, validated runs
- Decide when Litmus fits versus Chaos Mesh

## Litmus

LitmusChaos is a CNCF, Kubernetes-native chaos framework. Where Chaos Mesh is
fault-CRD-first, Litmus is organized around a **control plane** (ChaosCenter)
and a **library of packaged experiments** (ChaosHub) that you compose into
ChaosEngines and workflows. Its differentiator is the **probe** system —
SLO-style validation baked into the experiment so a run produces a pass/fail
verdict, not just an injected fault.

- **ChaosCenter** — web control plane: schedule, observe, multi-cluster
- **ChaosHub** — curated, shareable experiments (the "GitHub of chaos faults")
- **Probes** — automated pre/during/post health checks that gate the verdict
- GitOps and Argo Workflows / Argo CD integration

## Architecture

```
┌──────────────┐  installs/schedules  ┌────────────────────────┐
│ ChaosCenter  │ ───────────────────▶ │ Chaos delegate (agent) │
│ (control     │                      │ in each target cluster │
│  plane + UI) │ ◀─────────────────── │  runs experiments,     │
└──────────────┘   results / verdict  │  evaluates probes      │
                                       └────────────────────────┘
```

ChaosCenter is the single pane; a lightweight delegate runs in each target
cluster and executes the ChaosEngine, reporting the ChaosResult and verdict
back.

## Install

```bash
# Litmus 3.x via Helm (ChaosCenter control plane)
helm repo add litmuschaos https://litmuschaos.github.io/litmus-helm/
helm install chaos litmuschaos/litmus \
  --namespace litmus --create-namespace
```

After install, log into ChaosCenter, create a chaos environment, and connect a
delegate to the cluster you want to target.

## ChaosCenter

The web control plane lets you:

- Schedule experiments and recurring workflows
- View ChaosResults, probe outcomes, and the resilience score per run
- Manage multiple clusters/environments from one place
- Enforce RBAC over who can launch chaos where

## ChaosEngine (running a fault)

A `ChaosEngine` binds a packaged experiment to a target application:

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: nginx-chaos
  namespace: default
spec:
  appinfo:
    appns: 'default'
    applabel: 'app=nginx'
    appkind: 'deployment'
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: '60'        # seconds of chaos
            - name: CHAOS_INTERVAL
              value: '10'        # seconds between kills
            - name: PODS_AFFECTED_PERC
              value: '50'        # blast radius
```

`PODS_AFFECTED_PERC` is the blast-radius knob; `appinfo` scopes the target. The
experiment body (`pod-delete`) comes from ChaosHub, so the manifest stays small.

## Probes (the safety/validation layer)

Probes are what make a Litmus run a *test* rather than just a fault. They run
at defined points and decide the verdict:

```yaml
spec:
  experiments:
    - name: pod-delete
      spec:
        probe:
          - name: app-health
            type: httpProbe
            mode: Continuous        # SOT | EOT | Edge | Continuous | OnChaos
            httpProbe/inputs:
              url: http://my-app/health
              method: { get: { criteria: '==', responseCode: '200' } }
            runProperties:
              probeTimeout: 2s
              interval: 1s
              retry: 3
```

Probe modes — `SOT` (start), `EOT` (end), `Edge`, `Continuous`, `OnChaos` —
let you assert steady state before, hold a continuous SLO during, and confirm
recovery after. If a probe fails, the ChaosResult verdict is **Fail**, which is
the signal you actually want.

## Workflow

Litmus chaos workflows (Argo-based) chain experiments and probes into a
scenario, schedulable from ChaosCenter:

```yaml
spec:
  templates:
    - name: install-experiment   # pull the fault definition
    - name: pod-delete           # run it
    - name: revert               # cleanup
```

## ChaosHub

```bash
# Experiments are sourced from a hub (public or a private Git-backed hub)
litmusctl ...   # CLI to manage projects, environments, and delegates
```

ChaosHub is the curated, community-shared catalog of experiments. Teams
typically fork it into a **private Git-backed hub** so experiments are reviewed
and versioned like code.

## Litmus vs Chaos Mesh

| Dimension       | Litmus                          | Chaos Mesh                     |
|-----------------|---------------------------------|--------------------------------|
| Model           | Control plane + packaged experiments | Fault CRDs you apply directly |
| Validation      | First-class **probes** → verdict | Roll-your-own observation      |
| Catalog         | ChaosHub (shareable)            | Built-in CRDs                  |
| Multi-cluster   | ChaosCenter native              | Per-cluster install            |
| Best when       | You want governed, validated, multi-team chaos | You want lean GitOps fault CRDs |

## Common Mistakes

- Running without **probes** — you inject a fault but get no pass/fail signal
- Wrong `appinfo` label/namespace → experiment finds no target and silently passes
- Missing/over-broad `chaosServiceAccount` RBAC → experiment fails to run or runs too privileged
- Setting `PODS_AFFECTED_PERC: 100` on the first run instead of a small slice
- Using the public ChaosHub directly in prod instead of a reviewed private hub
- Treating the resilience score as truth without checking which experiments/probes ran

## Best Practices

- Always attach probes (httpProbe/k8sProbe/promProbe/cmdProbe) so runs have a verdict
- Scope tightly with `appinfo` + a low `PODS_AFFECTED_PERC`; widen across runs
- Use a private Git-backed ChaosHub; review experiments like any other code
- Run a least-privilege `chaosServiceAccount`; RBAC-gate ChaosCenter
- Validate in a non-prod environment first; confirm the revert step works
- Schedule recurring workflows so resilience regressions surface over time

## Quick Refs

```bash
helm install chaos litmuschaos/litmus -n litmus --create-namespace
kubectl get chaosengine                 # running experiments
kubectl get chaosresult                 # verdicts (Pass/Fail) + probe status
litmusctl                               # projects, environments, delegates
# Probe modes: SOT · EOT · Edge · Continuous · OnChaos
```

## Interview Prep

**Junior**: "What is Litmus?" — A CNCF Kubernetes chaos framework with a control plane (ChaosCenter), a shareable experiment catalog (ChaosHub), and probes that validate whether the system stayed healthy during the fault.

**Mid**: "What do probes do?" — Probes are automated health checks that run before/during/after chaos (httpProbe, promProbe, k8sProbe, cmdProbe). They turn an experiment into a pass/fail test: if the continuous probe trips, the ChaosResult verdict is Fail.

**Senior**: "Litmus vs Chaos Mesh — when each?" — Litmus is control-plane-centric with first-class probes and a shareable hub, good for governed multi-team/multi-cluster chaos with built-in validation; Chaos Mesh is leaner, fault-CRD-first, and fits teams who want GitOps-versioned fault manifests and will build their own observation.

**Staff**: "How would you operate Litmus across many teams safely?" — Run ChaosCenter as a governed control plane with RBAC and least-privilege chaos service accounts, source experiments from a reviewed private Git-backed hub, mandate probes so every run yields a verdict, start every team at a small blast radius, and schedule recurring workflows so resilience is trended rather than tested once.

## Next Topic

→ [T04 — Gremlin](T04-Gremlin.md)
