# L13/C16/T01 — kubectl describe, logs, exec, debug

## Learning Objectives

- Master core debug tools
- Use ephemeral debug containers

## The Four Tools

```bash
kubectl describe   # what's happening
kubectl logs       # what app says
kubectl exec       # interact with pod
kubectl debug      # ephemeral debugger
```

Use in order; build context.

## kubectl describe

Shows resource details + events:
```bash
kubectl describe pod my-pod
```

Output:
```
Name:          my-pod
Status:        Running (or Pending, Failed, etc.)
IP:            10.0.1.5
Containers:
  app:
    State:     Waiting
    Reason:    CrashLoopBackOff
    Last State: Terminated
      Reason:    Error
      Exit Code: 1
Events:
  Warning  Failed       30s    kubelet  Error: ...
  Normal   Pulled       1m     kubelet  Container image pulled
```

Events crucial: tell you WHY.

## describe Other Resources

```bash
kubectl describe deployment my-app
kubectl describe service my-svc
kubectl describe node my-node
kubectl describe pvc my-pvc
kubectl describe ingress my-ing
```

For each: relevant fields + events.

## kubectl logs

```bash
# Current logs
kubectl logs my-pod

# Specific container (multi-container)
kubectl logs my-pod -c app

# Previous (last terminated)
kubectl logs my-pod --previous

# Follow
kubectl logs my-pod -f

# Tail N
kubectl logs my-pod --tail=100

# Since
kubectl logs my-pod --since=1h
kubectl logs my-pod --since-time=2024-06-09T10:00:00Z

# All pods with label
kubectl logs -l app=web --tail=50 -f
```

## --previous Key

If container crashes + restarts: current logs are new container. `--previous` shows crashed one.

For CrashLoopBackOff: usually need `--previous`.

## kubectl exec

Run command in container:
```bash
# Run command
kubectl exec my-pod -- ls /

# Interactive shell
kubectl exec -it my-pod -- bash
kubectl exec -it my-pod -- sh   # if no bash

# Specific container
kubectl exec -it my-pod -c app -- sh

# As different user (if supported)
kubectl exec my-pod -- whoami
```

For: interactive debugging, check files, test network.

## Inside Pod

```bash
# In pod
ls /
ps aux
env | grep MY_VAR
cat /etc/resolv.conf
nslookup other-service
curl http://other-service:8080/health
```

Test connectivity, config, env.

## kubectl debug

Ephemeral debug container in running pod:
```bash
kubectl debug -it my-pod --image=nicolaka/netshoot --target=app
```

Adds container to pod:
- Shares process namespace with `--target`
- Has debug tools (curl, dig, netcat, etc.)
- No need to rebuild image with debug tools

## Use Cases

### Network Issues
```bash
kubectl debug -it my-pod --image=nicolaka/netshoot --target=app
# In debug container:
nslookup target-service
curl -v target-service:8080
traceroute target-service
```

### Process Inspection
```bash
kubectl debug -it my-pod --image=nicolaka/netshoot --target=app
# Process namespace shared
ps aux
strace -p <pid>
```

### File System
```bash
kubectl debug -it my-pod --image=busybox --target=app
ls /proc/<pid>/cwd
cat /proc/<pid>/environ
```

## Debug Node

```bash
kubectl debug node/my-node -it --image=ubuntu
```

Pod scheduled on node; chroot to host:
```bash
chroot /host
# Now in host context
systemctl status kubelet
journalctl -u kubelet
```

For: node-level debugging.

## Copy Files

```bash
# From pod
kubectl cp my-pod:/path/file ./file

# To pod
kubectl cp ./file my-pod:/path/file

# Container
kubectl cp my-pod:/path/file ./file -c app
```

For: extract logs, configs, dumps.

## Events

```bash
kubectl get events -A
kubectl get events -A --sort-by=.lastTimestamp
kubectl get events -n my-ns --field-selector type=Warning
```

Cluster-wide events. Show recent issues.

## Watch Resources

```bash
kubectl get pods -w
```

Live updates. For: see state transitions.

## Get Specific

```bash
# Yaml
kubectl get pod my-pod -o yaml

# JSON
kubectl get pod my-pod -o json

# JSONPath
kubectl get pod my-pod -o jsonpath='{.spec.containers[*].image}'

# Custom columns
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName
```

## Top

```bash
kubectl top pod
kubectl top node
kubectl top pod --containers
kubectl top pod --sort-by=cpu
```

Current resource usage. Requires Metrics Server.

## Diagnostic Flow

For Pending pod:
```bash
1. kubectl describe pod my-pod | grep -A 10 Events
   # Why not scheduled?
2. kubectl describe node | grep -A 5 "Allocated resources"
   # Resources available?
3. Check taints, affinity, etc.
```

For CrashLoopBackOff:
```bash
1. kubectl logs my-pod --previous
   # Why crashed?
2. kubectl describe pod my-pod
   # Image issues? Probe failures?
3. kubectl exec my-pod -- sh  (if running)
   # Inspect inside
```

For Service not working:
```bash
1. kubectl get endpoints my-svc
   # Backend pods registered?
2. kubectl exec my-pod -- nslookup my-svc
   # DNS works?
3. kubectl exec my-pod -- curl http://my-svc/
   # Connect works?
```

## Aliases (Save Time)

```bash
alias k=kubectl
alias kgp='kubectl get pods'
alias kdp='kubectl describe pod'
alias kl='kubectl logs'
alias ke='kubectl exec -it'
```

For frequent commands.

## Useful Plugins

```bash
# Install krew
(set -x; cd "$(mktemp -d)" && curl -fsSLO "..." && tar zxvf krew-linux_amd64.tar.gz && ./krew-linux_amd64 install krew)

# Useful plugins
kubectl krew install neat       # cleaner output
kubectl krew install tree        # resource tree
kubectl krew install ctx         # switch contexts
kubectl krew install ns          # switch namespaces
kubectl krew install who-can     # RBAC inspection
kubectl krew install ksniff      # tcpdump
```

## Common Commands

```bash
# Most pending pods
kubectl get pods -A --field-selector=status.phase!=Running

# Pod events recent
kubectl get events -n my-ns --sort-by=.lastTimestamp | tail -20

# Find pod's node
kubectl get pod my-pod -o jsonpath='{.spec.nodeName}'

# Pod's IP
kubectl get pod my-pod -o jsonpath='{.status.podIP}'

# Containers in pod
kubectl get pod my-pod -o jsonpath='{.spec.containers[*].name}'
```

## Best Practices

- Always check events
- --previous for crashloops
- Use debug for missing tools in image
- Verify endpoint registration
- Network test from pod context
- Save common queries as aliases

## Common Mistakes

- Forgot --previous (looking at wrong instance)
- Wrong container in multi-container pod
- Skipping events
- Trusting "Running" without checking probes

## Tools to Add to Image

For dev/test:
- curl, wget
- dig, nslookup
- tcpdump
- strace
- vim/nano

For prod: minimal image; use `kubectl debug` with netshoot.

## Pre-Stop Investigation

If pod stuck terminating:
```bash
kubectl describe pod my-pod | grep -A 3 Status
kubectl get pod my-pod -o yaml | grep deletionTimestamp
```

If finalizer stuck:
```bash
kubectl get pod my-pod -o yaml | grep -A 3 finalizers
kubectl patch pod my-pod -p '{"metadata":{"finalizers":[]}}' --type=merge
```

DANGEROUS; only when sure.

## Investigation Examples

### Pod Stuck Pending
```bash
kubectl describe pod my-pod
# Events: "0/3 nodes are available: 3 Insufficient cpu"
# → not enough capacity; scale cluster or reduce request
```

### Pod CrashLoopBackOff
```bash
kubectl logs my-pod --previous
# Error: connection refused to db
# → DB not reachable; check Service / network
```

### Service Returns 503
```bash
kubectl get endpoints my-svc
# (empty)
# → no backend pods; check labels / pod status
```

### Pod Can't Resolve DNS
```bash
kubectl exec my-pod -- cat /etc/resolv.conf
# nameserver 10.96.0.10
kubectl exec my-pod -- nslookup kubernetes.default
# Fails → CoreDNS issue or NetworkPolicy
```

## Quick Refs

```bash
# Describe + logs + exec
kubectl describe pod NAME
kubectl logs NAME --previous
kubectl exec -it NAME -- sh

# Debug
kubectl debug -it POD --image=nicolaka/netshoot --target=app
kubectl debug node/NODE -it --image=ubuntu

# Events
kubectl get events --sort-by=.lastTimestamp

# Monitor
kubectl top pod
watch kubectl get pods
```

## Interview Prep

**Junior**: "Pod not running — investigate."

**Mid**: "kubectl debug use case."

**Senior**: "Distributed app + network issue — workflow."

**Staff**: "Production K8s troubleshooting playbook."

## Next Topic

→ [T02 — ImagePullBackOff, CrashLoopBackOff, OOMKilled](T02-Common-Issues.md)
