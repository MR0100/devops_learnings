# L19/C07 — Chaos Engineering

## Topics

- **T01 Principles** — Hypothesis-driven experiments
- **T02 Tools** — Chaos Mesh, Litmus, Gremlin, AWS FIS
- **T03 Game Days** — Coordinated practice

(Covered deeper in L25; this chapter focuses on SRE-specific framing)

## Principles of Chaos Engineering

From principlesofchaos.org:
1. Build a hypothesis around steady-state behavior
2. Vary real-world events
3. Run experiments in production
4. Automate experiments to run continuously
5. Minimize blast radius

## Why Chaos for SRE

- Prove system handles failures (don't assume)
- Find weaknesses before customers do
- Train on-call (recovery muscle)
- Build confidence to deploy faster

## Maturity Levels

```
Level 1: Manual experiments in staging
Level 2: Manual experiments in production
Level 3: Scheduled experiments in production
Level 4: Continuous random chaos in production
```

Most companies stop at Level 2-3. Netflix runs at Level 4 (Chaos Monkey randomly kills instances 24/7).

## Tools

### Chaos Mesh (CNCF)
- Kubernetes-native; CRDs for chaos resources
- Network delay/loss, pod kill, CPU/memory stress, IO delay

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: api-delay
spec:
  action: delay
  mode: all
  selector:
    namespaces: [api]
    labelSelectors:
      app: my-app
  delay:
    latency: "500ms"
    jitter: "50ms"
  duration: "5m"
```

### Litmus (CNCF)
- Similar; with marketplace of experiments
- ChaosCenter UI

### Gremlin (commercial)
- Strong UI; pre-built experiment library
- Heavily used in regulated industries

### AWS Fault Injection Simulator (FIS)
- AWS-native; affects EC2, RDS, EKS, etc.
- Templates: zone failure, instance termination, latency injection
- IAM-controlled

## Game Days

Coordinated chaos exercises.

### Plan
- Scope: one service or full system
- Scenarios: AZ failure, DB outage, cache failure, etc.
- Participants: on-call + IC + observers
- Schedule: 2-3 hours, business hours

### Run
- Pre-brief: review hypothesis + abort criteria
- IC kicks off chaos
- Team responds as if real
- Observers take notes
- Abort if real customer harm risk

### Debrief
- What worked, what didn't
- Where did we struggle?
- What's missing (monitoring, runbooks)?
- Action items

### Cadence
- Quarterly for top-priority services
- Monthly chaos exercises (smaller scope)
- Yearly large-scale exercise

## Sample Hypothesis

```
Hypothesis: If our primary DB fails, replica failover completes
            within 60 seconds, with < 1% request error rate.

Steady state: 0.05% error rate; p99 latency 80 ms.

Experiment:
1. Verify steady state.
2. Simulate primary DB failure (via FIS).
3. Observe for 5 minutes.
4. Resolve simulation; observe recovery.

Abort criteria: error rate > 5% for > 30s OR customer-visible alert
                fires that team can't dismiss within 10s.

Expected result: 60s of elevated errors; recovery to baseline within 90s.

Actual result: ___ (filled in after experiment)

Action items: ___ (if differences from expected)
```

## What Not To Chaos

- During known peak periods (Black Friday)
- During known organizational stress (mid-deploy, customer launch)
- Without informed consent of on-call team
- Without abort capability
- When customer harm is foreseeable

## Combined with SLOs

Each chaos experiment is also an SLO test:
- During DB failover, did error rate exceed SLO?
- If yes, system needs more reliability investment.

This is reliability engineering in action: not asserting reliability, **proving** it.

## Interview Themes

- "Chaos engineering — principles"
- "Game day — what would you do?"
- "Chaos in prod — how to do safely?"
- "Sample hypothesis"
- "When NOT to chaos"
