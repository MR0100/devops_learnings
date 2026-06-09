# L13/C03/T03 — Downward API

## Learning Objectives

- Use Downward API
- Inject pod metadata

## Downward API

Expose pod's own metadata to the container:
- Name, namespace
- IP
- Node name
- Labels, annotations
- Resource requests/limits
- ServiceAccount

Without making external API calls.

## Env Vars

```yaml
env:
- name: POD_NAME
  valueFrom:
    fieldRef:
      fieldPath: metadata.name

- name: POD_NAMESPACE
  valueFrom:
    fieldRef:
      fieldPath: metadata.namespace

- name: POD_IP
  valueFrom:
    fieldRef:
      fieldPath: status.podIP

- name: NODE_NAME
  valueFrom:
    fieldRef:
      fieldPath: spec.nodeName

- name: SERVICE_ACCOUNT
  valueFrom:
    fieldRef:
      fieldPath: spec.serviceAccountName

- name: HOST_IP
  valueFrom:
    fieldRef:
      fieldPath: status.hostIP
```

## Resource Fields

```yaml
- name: CPU_REQUEST
  valueFrom:
    resourceFieldRef:
      containerName: app
      resource: requests.cpu
      divisor: "1m"   # millicores

- name: MEM_LIMIT
  valueFrom:
    resourceFieldRef:
      containerName: app
      resource: limits.memory
      divisor: "1Mi"
```

Useful for: tuning app (JVM -Xmx based on limit).

## Volume Mount

```yaml
volumes:
- name: podinfo
  downwardAPI:
    items:
    - path: "name"
      fieldRef:
        fieldPath: metadata.name
    - path: "labels"
      fieldRef:
        fieldPath: metadata.labels
    - path: "annotations"
      fieldRef:
        fieldPath: metadata.annotations

volumeMounts:
- name: podinfo
  mountPath: /etc/podinfo
```

Files:
- /etc/podinfo/name
- /etc/podinfo/labels (key=value lines)
- /etc/podinfo/annotations

## Auto-Update

Labels / annotations mounted as files: auto-update when changed.

Useful for: feature flags via annotations.

## Use Cases

### Java JVM Sizing
```yaml
env:
- name: MAX_HEAP
  valueFrom:
    resourceFieldRef:
      resource: limits.memory
      divisor: "1Mi"

# Then in app:
# java -Xmx${MAX_HEAP}m
```

JVM uses 75% of pod's RAM.

### Logging Context
Include pod name in logs:
```yaml
env:
- name: POD_NAME
  valueFrom: {fieldRef: {fieldPath: metadata.name}}

# Log:
log.info({"pod": os.environ["POD_NAME"], "msg": "..."})
```

For: correlate logs across instances.

### Metric Labels
```python
metric = Counter("requests", "Requests", ["pod"])
metric.labels(pod=os.environ["POD_NAME"]).inc()
```

Distinguish by pod.

### Self-Aware
Discover own IP for clustering:
```python
my_ip = os.environ["POD_IP"]
peers = get_peers()  # from headless Service DNS
cluster.join(my_ip, peers)
```

### Sidecar Configuration
Sidecar reads pod's labels to configure itself.

## What Can Be Exposed

```
metadata.name
metadata.namespace
metadata.uid
metadata.labels[*]
metadata.annotations[*]
metadata.labels (all as file)
metadata.annotations (all as file)

spec.nodeName
spec.serviceAccountName

status.hostIP
status.podIP
status.podIPs

resource fields per container
```

NOT spec fields (resource requests etc. except via resourceFieldRef).

## Examples

### Region Detection
```yaml
env:
- name: NODE_REGION
  valueFrom:
    fieldRef:
      fieldPath: metadata.labels['topology.kubernetes.io/region']
```

Pod's node region (if node labeled).

### Cluster Identity
Annotation:
```yaml
metadata:
  annotations:
    cluster-name: prod-us-east
```

In env:
```yaml
env:
- name: CLUSTER_NAME
  valueFrom:
    fieldRef:
      fieldPath: metadata.annotations['cluster-name']
```

Useful for multi-cluster apps.

## Limits

- Env vars: limited fields (resourceFieldRef + fieldRef)
- Volume: more flexible (labels, annotations as maps)
- Some fields immutable post-start; values frozen

## Common Patterns

### App Self-Aware
```python
import os

POD_NAME = os.environ.get("POD_NAME")
NAMESPACE = os.environ.get("POD_NAMESPACE")
NODE = os.environ.get("NODE_NAME")
POD_IP = os.environ.get("POD_IP")

print(f"Starting {POD_NAME} on {NODE} ({POD_IP})")
```

### Sidecar Configuration
```yaml
# Sidecar reads labels at /etc/podinfo/labels
volumeMounts:
- name: podinfo
  mountPath: /etc/podinfo
```

Sidecar config based on pod's labels (e.g., team, env).

## Not Magic

Just K8s exposing existing fields. Same data available via API:
```bash
kubectl get pod <self> -o jsonpath='{.metadata.name}'
```

Downward API: in-pod access without API call.

## Common Mistakes

- Trying to expose other resources (only own pod)
- Expecting writes (read-only)
- Volume not getting label updates (subPath has issue; use root path)

## Best Practices

- Use for self-aware apps
- Include POD_NAME in logs
- Resource-based sizing for JVM, etc.
- Annotations for cluster identity
- Volume mount when fields can change

## ServiceAccount

Mounted automatically at `/var/run/secrets/kubernetes.io/serviceaccount/`:
- token
- ca.crt
- namespace

Used by SDK to talk to API Server (kube-rs, kubernetes-client).

For external (AWS): IRSA / Pod Identity uses this.

## Inspection

```bash
# Look at what's mounted
kubectl exec my-pod -- ls /etc/podinfo

# Read
kubectl exec my-pod -- cat /etc/podinfo/labels
```

## Quick Refs

```yaml
# Env
env:
- name: POD_NAME
  valueFrom:
    fieldRef:
      fieldPath: metadata.name

# Volume
volumes:
- name: podinfo
  downwardAPI:
    items:
    - path: name
      fieldRef: {fieldPath: metadata.name}

# Resource
env:
- name: MEM_LIMIT
  valueFrom:
    resourceFieldRef:
      resource: limits.memory
      divisor: "1Mi"
```

## Interview Prep

**Mid**: "Downward API use case."

**Senior**: "JVM sizing in K8s."

**Staff**: "Self-aware sidecar pattern."

## Next Topic

→ [T04 — Environment Variables vs Files](T04-EnvVars-vs-Files.md)
