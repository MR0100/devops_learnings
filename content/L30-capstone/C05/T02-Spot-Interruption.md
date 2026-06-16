# L30/C05/T02 — Graceful Spot Interruption Handling

## Learning Objectives

- Handle spot evictions
- Graceful shutdown

## Why This Topic Exists

Spot savings are only real if interruptions are invisible to users. This topic is
where the project earns its "production-grade" claim: AWS gives a **2-minute
warning** before reclaiming a Spot instance, and your job is to use those 2
minutes to drain gracefully so no in-flight request is dropped. Get this wrong
and Spot becomes a reliability liability; get it right and you keep ~70% savings
at ~99.93% availability.

### The Chain of Defenses

Each layer handles a different failure window — together they make interruptions
a non-event:

1. **Detection** (Karpenter interruption queue / node-termination-handler) —
   catches the 2-min notice and the rebalance recommendation, cordons the node.
2. **PDB** — caps how many pods of a service can be unavailable at once, so a
   drain can't take the whole service down (especially when multiple nodes in a
   pool are reclaimed together).
3. **`terminationGracePeriodSeconds` + SIGTERM handler** — the app stops taking
   new work, finishes in-flight requests, closes connections, exits 0 — within
   the grace window (kept under the 2-minute budget).
4. **`preStop` hook** — a short sleep to let the load balancer/endpoints
   deregister the pod *before* it stops accepting traffic (avoids the race where
   traffic still routes to a terminating pod).

## Spot Interruption

AWS:
- 2-min warning
- Via instance metadata
- Or via EventBridge → SQS (what Karpenter consumes)

## Karpenter

Listens to interruption events:
```yaml
spec:
  settings:
    interruptionQueue: my-queue
```

Provisioned SQS receives events. Karpenter:
- Cordons node
- Schedules new node
- Drains old

## Pod Grace

```yaml
spec:
  terminationGracePeriodSeconds: 60
```

For: handle SIGTERM.

## App Handling

```python
import signal

def handle_sigterm(sig, frame):
    # Stop accepting new requests
    server.stop_accepting()
    # Drain
    server.wait_for_inflight()
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)
```

For: clean shutdown.

## PDB

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 2
```

For: maintain availability.

## Stateful

For stateful pods on spot:
- Risk
- Use persistent volumes
- Plan for restart

For: usually avoid.

## Monitor

```promql
karpenter_interruptions_total
```

Track eviction rate:
- < 1%: OK
- > 5%: investigate (instance type pool)

## Spot Diversification

(See T01.)

Diverse types → lower eviction.

## Best Practices

- Karpenter interruption handling
- Graceful shutdown
- PDB
- Diverse types
- Stateless on spot
- Monitor

## Common Mistakes

- No graceful shutdown
- Stateful on spot
- One instance type
- No PDB

## Acceptance Criteria

- Karpenter (or NTH) consumes the interruption notice and cordons/drains the node
- A PDB prevents too many pods of a service draining at once
- The app handles SIGTERM: stops new work, finishes in-flight, exits cleanly
  within the grace period
- A forced interruption (AWS FIS, C05 demo) shows pods rescheduled with **zero**
  customer-facing errors
- Interruption rate is monitored; > ~5% triggers a diversification review

## Quick Refs

```
Detection: Karpenter interruption queue (EventBridge→SQS) / node-termination-handler
PDB: cap simultaneous unavailable pods
App: SIGTERM handler + terminationGracePeriodSeconds (< 2 min)
preStop: short sleep so LB deregisters before traffic stops
Monitor: interruption rate; >5% → diversify
```

## Interview Prep

**Junior**: "What happens when AWS reclaims a Spot instance?" — AWS sends a
2-minute warning before terminating the instance. In that window Kubernetes
cordons the node and drains its pods so they get rescheduled elsewhere before the
node disappears.

**Mid**: "How do you make a Spot interruption not affect users?" — A few layers:
something watches for the interruption notice and starts draining the node; a Pod
Disruption Budget makes sure only a safe number of pods go down at once; and the
app handles SIGTERM by stopping new requests, finishing in-flight ones, and
exiting cleanly within the termination grace period. A `preStop` sleep gives the
load balancer time to stop routing to the pod first. Together, the pod is gone
gracefully and users never see an error.

**Senior**: "Walk me through the 2-minute budget and where it can go wrong." — The
clock starts at the interruption notice. You spend a few seconds on detection and
cordon, then the pod gets SIGTERM and has until `terminationGracePeriodSeconds` to
drain. The classic bug is the **traffic-still-routing race**: the pod gets SIGTERM
and stops serving, but the load balancer/endpoints haven't deregistered it yet, so
in-flight requests hit a dead pod — that's what the `preStop` sleep fixes. The
other failure is a grace period longer than the 2-minute budget, so the node dies
mid-drain. And if multiple nodes in one Spot pool get reclaimed together, a PDB
that's too permissive lets the whole service drain at once. So the design is:
keep grace < 2 min, deregister before stopping, and size PDBs for simultaneous
multi-node loss — not just one pod at a time.

**Staff**: "Your Spot interruption rate spiked to 8% and a few requests are now
erroring during drains. How do you diagnose and fix it?" — First, separate the two
problems: the *rate* (a capacity/diversification issue) and the *errors* (a
graceful-shutdown issue). The 8% rate usually means too few instance pools —
interruptions are clustering because workloads concentrated on one or two
types/AZs, so I'd widen the NodePool's instance diversity and check whether
consolidation re-packed everything onto a narrow set. For the errors, I'd verify
the drain path end to end: is `preStop`/deregistration actually happening before
SIGTERM, is the grace period long enough for real in-flight work but under 2
minutes, and is the PDB actually capping concurrent drains (a `minAvailable` that
math says still allows a full drain is a common silent gap). The staff move is
making this observable as a standing signal — interruption rate and
drain-induced error rate on a dashboard with an alert — so it's caught as a trend,
not discovered when a customer complains. And I'd revisit which workloads are on
Spot at all: if something genuinely can't tolerate this, it shouldn't be there.

## Next Topic

→ [T03 — Cost Dashboards](T03-Cost-Dashboards.md)
