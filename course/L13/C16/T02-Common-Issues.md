# L13/C16/T02 — ImagePullBackOff, CrashLoopBackOff, OOMKilled

## Learning Objectives

- Diagnose common pod failures
- Apply fixes

## ImagePullBackOff

Can't pull image:
```bash
kubectl get pod
# NAME    READY   STATUS              RESTARTS
# my-pod  0/1     ImagePullBackOff    0

kubectl describe pod my-pod
# Events:
#   Failed to pull image "myregistry/app:v1":
#     manifest unknown
#   OR
#     unauthorized: authentication required
```

## Causes & Fixes

### Wrong Image Name / Tag
```yaml
image: myapp:v1.2.4   # typo
```

Fix: correct image / tag.

```bash
# Verify image exists
docker pull myregistry/app:v1
crane manifest myregistry/app:v1
```

### Private Registry; No Pull Secret
```yaml
imagePullSecrets:
- name: regcred
```

Create secret:
```bash
kubectl create secret docker-registry regcred \
  --docker-server=... --docker-username=... --docker-password=...
```

Attach to ServiceAccount (better):
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: default
imagePullSecrets:
- name: regcred
```

### ECR Auth Expired
For non-IRSA: token expires ~12 hr.

Fix: IRSA (recommended) or refresh via CronJob.

### Network Issue
Node can't reach registry. Check:
- Egress
- DNS
- Firewall

### Rate Limit
Docker Hub: 100 pulls/6hr anonymous, 200 authenticated.

Fix: ECR Pull-Through cache.

## CrashLoopBackOff

Container starts, crashes, restarts, crashes:
```bash
kubectl get pod
# my-pod   0/1   CrashLoopBackOff   5

kubectl describe pod my-pod
# State: Waiting
# Reason: CrashLoopBackOff
# Last State: Terminated
#   Exit Code: 1
```

## Causes & Fixes

### App Crashes Immediately
```bash
kubectl logs my-pod --previous
# Error: missing env var DATABASE_URL
```

Fix: set required env vars.

### Wrong Command
```yaml
command: ["wronng-command"]   # typo
```

Fix: correct command.

### Missing Config
```bash
kubectl logs my-pod --previous
# Error: config file not found
```

ConfigMap not mounted; check volumeMounts.

### Probe Failure
Liveness probe fails → kubelet kills container → restart loop.

```bash
kubectl describe pod my-pod
# Events: Liveness probe failed
```

Fix:
- Increase initialDelaySeconds (slow start)
- Use startupProbe
- Fix probe path / port

### Dependency Down
App can't connect to DB / other service:
```bash
kubectl logs my-pod --previous
# Error: connection refused to db:5432
```

Fix: ensure dependencies ready (init container wait).

### Permission Denied
Container can't read file / bind port:
```bash
kubectl logs my-pod --previous
# Error: permission denied opening /data/file
```

Fix:
- runAsUser
- fsGroup for volume ownership
- chown in initContainer

## Backoff Time

Restart delay: exponential.
- 10s → 20s → 40s → 80s → ...
- Caps at 5 minutes.

Pod state alternates Waiting / CrashLoopBackOff / Running briefly.

## OOMKilled

Memory exceeded limit:
```bash
kubectl describe pod my-pod
# Last State: Terminated
#   Reason: OOMKilled
#   Exit Code: 137
```

## Causes & Fixes

### Memory Limit Too Low
```yaml
limits:
  memory: 128Mi   # app needs 256Mi
```

Fix: increase limit.

```bash
# Check usage
kubectl top pod my-pod --containers
```

### Memory Leak
App grows over time → eventually OOM.

```bash
# Track over time
kubectl top pod my-pod --containers   # rising
```

Fix: app code (leak).

### Java -Xmx Too High
Java sees node memory, not pod limit:
```yaml
limits:
  memory: 1Gi
```

JVM with -Xmx=8g exceeds. Fix:
```yaml
env:
- name: MAX_HEAP
  valueFrom:
    resourceFieldRef:
      resource: limits.memory
      divisor: "1Mi"

command:
- java
- -Xmx${MAX_HEAP}m
- ...
```

Or modern JVMs honor cgroup limits.

### Working Set vs RSS
`container_memory_working_set_bytes` is what kubelet uses for eviction.

```bash
kubectl top pod   # working set
```

If close to limit: OOM imminent.

## Exit Codes

- 0: success
- 1: general error
- 130: SIGINT (Ctrl+C)
- 137: SIGKILL (OOM or terminated)
- 143: SIGTERM

For 137 + OOMKilled reason: memory.
For 137 + other: forcibly killed (often grace period exceeded).

## Pending

Pod can't be scheduled:
```bash
kubectl describe pod my-pod
# Events: "0/3 nodes are available: 3 Insufficient cpu"
```

## Causes & Fixes

### Insufficient Resources
- Cluster too small
- Pod request too high
- Other pods consuming

Fix:
- Scale cluster (Cluster Autoscaler / Karpenter)
- Right-size requests
- Set Priority Class

### Volume Issue
```bash
# Events: "FailedScheduling: 0/3 nodes available; volume not bound"
```

PVC pending; check:
```bash
kubectl describe pvc my-pvc
```

### Taints Without Tolerations
```bash
# Events: "0/3 nodes: 3 had taint that the pod didn't tolerate"
```

Fix: tolerations or untaint.

### Affinity Mismatch
```bash
# Events: "0/3 nodes: 3 didn't match node selector"
```

Fix: label nodes or relax affinity.

## Container Creating (Stuck)

```bash
kubectl describe pod my-pod
# Status: ContainerCreating
# Events: 
```

## Causes

### CNI Issue
Pod can't get IP. CNI failure.

```bash
kubectl logs -n kube-system <cni-pod>
```

### Volume Mount Failed
PVC not attached:
```bash
# Events: FailedAttachVolume: ...
```

Check:
- PV bound?
- Cloud provider attached?
- Multi-AZ mismatch?

### Image Pull
Same as ImagePullBackOff but earlier phase.

## Init Container Stuck

```bash
kubectl get pod
# NAME    READY   STATUS      
# my-pod  0/1     Init:0/2    
# my-pod  0/1     Init:CrashLoopBackOff   1
```

Init container failing:
```bash
kubectl logs my-pod -c init-container-name --previous
```

Fix init logic.

## Completed (Pod Shouldn't Be)

```bash
kubectl get pod
# my-pod   0/1   Completed   0
```

Container exited 0; pod-spec.restartPolicy=Never.

For DaemonSet / Deployment: should be Always.

## Specific Container Issues

Multi-container pod:
```bash
kubectl logs my-pod -c app           # app container
kubectl logs my-pod -c sidecar       # sidecar
kubectl exec my-pod -c app -- sh     # specific container
```

## Get Pod History

```bash
kubectl describe pod my-pod | head -30
# Shows recent state transitions
```

For history beyond pod's life: events:
```bash
kubectl get events --field-selector involvedObject.name=my-pod
```

## Best Practices

- Probes configured (catch issues early)
- Resource requests + limits set
- Test failure modes
- Monitor restart counts
- Alert on CrashLoopBackOff
- Logs to external system

## Common Mistakes

- No requests (scheduling chaos)
- No limits (OOM risk)
- Probe too aggressive (false positives)
- Wrong image tag (typo)
- No private registry pull secret

## Investigation Workflow

For broken pod:
1. `kubectl describe pod <pod>` → see status + events
2. `kubectl logs <pod> --previous` if crashed
3. Identify root cause
4. Check Spec mistake or env / dep issue
5. Apply fix; redeploy

## Quick Refs

```bash
# Status
kubectl get pod
kubectl describe pod NAME

# Logs
kubectl logs NAME --previous
kubectl logs NAME -c CONTAINER

# Common queries
kubectl get pods -A | grep -v Running   # non-running
kubectl get events --sort-by=.lastTimestamp | tail -20

# Exit code
kubectl get pod NAME -o jsonpath='{.status.containerStatuses[*].lastState.terminated.exitCode}'
```

## Interview Prep

**Junior**: "ImagePullBackOff causes."

**Mid**: "CrashLoopBackOff workflow."

**Senior**: "OOMKilled in Java app."

**Staff**: "Pod failure runbook."

## Next Topic

→ [T03 — DNS, Service, Ingress Issues](T03-DNS-Service-Issues.md)
