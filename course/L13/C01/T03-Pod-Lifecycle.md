# L13/C01/T03 — The Pod Lifecycle (End-to-End)

## Learning Objectives

- Trace pod from apply to running
- Handle pod phases

## Pod Phases

- **Pending**: accepted; not yet running (image pull, scheduling)
- **Running**: bound to node; at least one container started
- **Succeeded**: all containers exited 0; won't restart
- **Failed**: at least one container exited non-zero (terminal for Job)
- **Unknown**: state unknown (node communication lost)

## Container States

Per container:
- **Waiting**: starting up (pulling image, etc.)
- **Running**: process running
- **Terminated**: exited

```yaml
containerStatuses:
- state:
    waiting:
      reason: ContainerCreating
- state:
    running:
      startedAt: ...
- state:
    terminated:
      exitCode: 0
      reason: Completed
```

## End-to-End Flow

1. **kubectl apply**: client sends YAML
2. **API Server**:
   - Auth (cert / token)
   - RBAC check
   - Mutating webhooks (e.g., inject sidecar, set defaults)
   - Validating webhooks (PSA, custom)
   - Persist to etcd
3. **Watchers notified**: scheduler, kubelet, controllers
4. **Scheduler**:
   - Filter nodes (resources, taints, affinity)
   - Score (spread, locality)
   - Bind to node (writes spec.nodeName)
5. **kubelet on node**:
   - Sees pod assigned
   - Pulls image (via runtime)
   - CNI sets up network (IP, route)
   - CSI mounts volumes
   - Runtime starts pause container (holds namespaces)
   - Runtime starts init containers (sequentially)
   - Runtime starts app containers
   - Probes begin
6. **Probes**:
   - StartupProbe (if defined): wait until success
   - LivenessProbe: ongoing health
   - ReadinessProbe: when ready, mark Ready
7. **Ready**:
   - kubelet sets Pod Ready=True
   - kube-proxy adds to Service endpoints
   - Traffic flows
8. **Running**

## Init Containers

Run before app containers; sequential; must succeed.

```yaml
spec:
  initContainers:
  - name: init-db
    image: busybox
    command: ['sh', '-c', 'until nslookup db; do sleep 1; done']
  containers:
  - name: app
    image: myapp
```

For: dependency wait, config generation, permissions setup.

## Sidecar Containers

Auxiliary containers in same pod:
- Logging agent
- Service mesh proxy (Istio sidecar)
- Cache

Run for pod's lifetime.

K8s 1.28+: native sidecars (init containers with `restartPolicy: Always`).

## Probes

### Liveness
"Is container alive?"
- Failure → restart container
- Use: detect deadlock, infinite loop

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3
```

### Readiness
"Can container serve traffic?"
- Failure → removed from Service endpoints
- Use: warming up, in-flight migration

```yaml
readinessProbe:
  httpGet:
    path: /readyz
    port: 8080
```

### Startup
"Has container started?"
- Disables liveness/readiness until passes
- Use: slow-starting apps (Java)

## Restart Policy

- **Always**: Pod restarts on container exit (default)
- **OnFailure**: restart on non-zero exit
- **Never**: no restart

Pod-level. For Deployments / StatefulSets: typically Always.

## Termination Flow

When pod deleted:
1. API Server marks deletion timestamp
2. kubelet receives event
3. **PreStop hook** runs (if defined)
4. SIGTERM sent to containers
5. **terminationGracePeriodSeconds** countdown (default 30s)
6. If still running: SIGKILL
7. Containers stopped
8. Volumes unmounted
9. Pod removed from etcd

Pod removed from Service endpoints immediately at step 1 (or shortly after).

## Graceful Termination

For your app:
```python
import signal

def handler(sig, frame):
    # Stop accepting new requests
    # Wait for in-flight to finish
    # Exit cleanly
    sys.exit(0)

signal.signal(signal.SIGTERM, handler)
```

Without: SIGTERM ignored; SIGKILL after grace period; in-flight dropped.

## PreStop Hook

```yaml
lifecycle:
  preStop:
    exec:
      command: ["sh", "-c", "sleep 15"]
```

Useful: drain time before SIGTERM.

Or:
```yaml
preStop:
  httpGet:
    path: /shutdown
    port: 8080
```

## Pod Disruption Budget (PDB)

Limits voluntary disruptions:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: web
```

Voluntary: node drain, kubectl delete.
Involuntary: node crash (PDB doesn't apply).

## Pod IP

Assigned by CNI on pod creation. Lost on pod deletion.

If pod restarted (same name, new instance): new IP (typically).

For stable IP / DNS: Service.

## Pod DNS

Pods resolve via CoreDNS (cluster DNS):
- `service.namespace.svc.cluster.local`
- `pod-ip.namespace.pod.cluster.local`

/etc/resolv.conf in pod:
```
nameserver 10.96.0.10
search namespace.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

## Common Failures

### Pending
- No node fits (resource, affinity)
- Image pull error
- Volume not provisioned
- `kubectl describe pod` shows events

### CrashLoopBackOff
Container starts, exits, restarted, exits, repeats:
- App bug
- Missing config
- Wrong command
- Misconfigured probes

Check logs:
```bash
kubectl logs <pod>
kubectl logs <pod> --previous   # last terminated
```

### ImagePullBackOff
- Wrong image name
- Private registry; no pull secret
- Network can't reach registry

### CreateContainerConfigError
- ConfigMap / Secret referenced doesn't exist
- Wrong key

## Pod Lifecycle Annotations

Some fields manage lifecycle:
- `terminationGracePeriodSeconds`: default 30
- `restartPolicy`: Always/OnFailure/Never
- `activeDeadlineSeconds`: max runtime (Job)
- `dnsPolicy`: cluster DNS or custom
- `nodeName`: forces specific node
- `priorityClassName`: scheduling priority

## Pod Spec Mutations

Once running: spec is mostly immutable.

Mutable:
- `spec.containers[*].image` (kubectl set image)
- `spec.activeDeadlineSeconds`
- `spec.tolerations` (add only)
- `spec.terminationGracePeriodSeconds`

Other changes: delete + recreate (or update via Deployment).

## Pod Conditions

```yaml
conditions:
- type: PodScheduled
  status: "True"
- type: Initialized
  status: "True"
- type: ContainersReady
  status: "True"
- type: Ready
  status: "True"
```

Each transition has reason + message.

## Debug Container (Ephemeral)

For debugging:
```bash
kubectl debug -it <pod> --image=busybox --target=<container>
```

Adds container to running pod (shares process namespace).

For: when prod pod has bug; can't include debug tools in image.

## Logs

```bash
kubectl logs <pod>
kubectl logs <pod> -c <container>   # multi-container
kubectl logs <pod> --previous       # previous instance
kubectl logs <pod> -f               # follow
kubectl logs <pod> --since=1h
kubectl logs -l app=web --tail=100 -f   # all pods with label
```

## Events

```bash
kubectl get events --sort-by='.lastTimestamp'
kubectl describe pod <pod>   # shows events
```

For: troubleshooting Pending, Failed, restarts.

## Best Practices

- Probes (liveness, readiness)
- PreStop for graceful shutdown
- Handle SIGTERM in app
- Resource requests (scheduling sanity)
- Termination grace appropriate
- PDB for HA
- Init containers for deps

## Common Mistakes

- No probes → traffic to dying / starting
- Wrong probe params (too aggressive → flapping)
- SIGTERM ignored → connection drops
- No graceful drain → in-flight lost
- Heavy init containers (slow startup)

## Interview Prep

**Junior**: "Pod phases."

**Mid**: "What happens on kubectl delete pod."

**Senior**: "Graceful shutdown design."

**Staff**: "Diagnose CrashLoopBackOff."

## Next Topic

→ [T04 — The Scheduler Internals](T04-Scheduler-Internals.md)
