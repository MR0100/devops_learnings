# L13/C02/T01 — Pods (The Atomic Unit)

## Learning Objectives

- Understand pod semantics
- Use pods correctly

## Pod

Smallest deployable unit. 1+ containers sharing:
- Network namespace (same IP, ports)
- IPC
- Volumes
- Lifecycle

## Why Pods (Not Containers)

Two containers needing tight coupling:
- Web app + log shipper
- Service mesh proxy + app
- Cache + app

Single container: simpler.
Multiple in pod: when ALL co-located + share fate.

## YAML

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  labels:
    app: web
spec:
  containers:
  - name: web
    image: nginx:1.27
    ports:
    - containerPort: 80
    resources:
      requests:
        cpu: "100m"
        memory: 128Mi
      limits:
        cpu: "500m"
        memory: 256Mi
```

## Container Fields

```yaml
containers:
- name: web
  image: nginx:1.27
  imagePullPolicy: IfNotPresent  # or Always, Never
  command: ["/bin/sh"]            # ENTRYPOINT override
  args: ["-c", "echo hello"]      # CMD override
  env:
  - name: MY_VAR
    value: hello
  envFrom:
  - configMapRef:
      name: app-config
  - secretRef:
      name: app-secret
  ports:
  - containerPort: 80
    name: http
    protocol: TCP
  resources:
    requests: {cpu: "100m", memory: 128Mi}
    limits:   {cpu: "500m", memory: 256Mi}
  livenessProbe: {...}
  readinessProbe: {...}
  startupProbe: {...}
  volumeMounts:
  - name: data
    mountPath: /data
  securityContext:
    runAsUser: 1000
    runAsNonRoot: true
    readOnlyRootFilesystem: true
    capabilities:
      drop: [ALL]
```

## Multi-Container Pod

Common patterns:

### Sidecar (Logging)
```yaml
containers:
- name: app
  image: myapp
  volumeMounts:
  - name: logs
    mountPath: /var/log
- name: log-shipper
  image: fluent/fluent-bit
  volumeMounts:
  - name: logs
    mountPath: /var/log
volumes:
- name: logs
  emptyDir: {}
```

App writes logs to shared volume; sidecar ships them.

### Ambassador (Proxy)
- Main app + proxy that abstracts external service

### Adapter (Standardization)
- Convert app output to standard format

## Init Containers

Run before main containers; sequential:
```yaml
spec:
  initContainers:
  - name: wait-for-db
    image: busybox
    command: ['sh', '-c', 'until nc -z db 5432; do sleep 1; done']
  containers:
  - name: app
    image: myapp
```

For: dependency wait, schema migration, file generation.

## Native Sidecars (alpha 1.28, beta 1.29, GA 1.33)

Init container with `restartPolicy: Always` becomes proper sidecar:
- Starts before main
- Persists for pod lifetime
- Pod won't be considered Ready until sidecar ready

```yaml
initContainers:
- name: proxy
  image: istio-proxy
  restartPolicy: Always   # makes it a sidecar
```

For: service mesh sidecars properly.

## Resources

### Requests
Guaranteed minimum:
- Scheduler reserves
- Pod gets at least

### Limits
Maximum allowed:
- CPU throttled at limit
- Memory exceeds → OOM kill

```yaml
resources:
  requests:
    cpu: "500m"        # 0.5 vCPU
    memory: 256Mi
  limits:
    cpu: "1"           # 1 vCPU
    memory: 512Mi
```

## QoS Classes

Determined by resources:
- **Guaranteed**: requests == limits (all containers)
- **Burstable**: at least one request, but != limits
- **BestEffort**: no requests/limits

Eviction priority: BestEffort first, Guaranteed last.

For prod: Guaranteed or Burstable.

## Security Context

Pod-level:
```yaml
securityContext:
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  runAsNonRoot: true
  seccompProfile:
    type: RuntimeDefault
```

Container-level:
```yaml
containers:
- name: app
  securityContext:
    readOnlyRootFilesystem: true
    allowPrivilegeEscalation: false
    capabilities:
      drop: [ALL]
```

## Pod Spec Immutability

Once running: limited fields editable:
- `spec.containers[*].image` (set image)
- `spec.activeDeadlineSeconds`
- `spec.tolerations` (add only)
- `spec.terminationGracePeriodSeconds`

Other changes: delete + recreate.

For changes via Deployment: deployment controller handles.

## Probes Recap

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /readyz
    port: 8080
  initialDelaySeconds: 5

startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
```

For slow start: startup probe.

## Probe Types

```yaml
# HTTP
livenessProbe:
  httpGet:
    path: /
    port: 8080

# TCP
livenessProbe:
  tcpSocket:
    port: 8080

# Exec
livenessProbe:
  exec:
    command: ["/bin/sh", "-c", "curl -f http://localhost"]

# gRPC (newer)
livenessProbe:
  grpc:
    port: 9090
```

## Environment Variables

```yaml
env:
- name: SIMPLE
  value: "hello"

# From ConfigMap
- name: FROM_CM
  valueFrom:
    configMapKeyRef:
      name: my-cm
      key: my-key

# From Secret
- name: FROM_SECRET
  valueFrom:
    secretKeyRef:
      name: my-secret
      key: password

# Downward API
- name: POD_NAME
  valueFrom:
    fieldRef:
      fieldPath: metadata.name
- name: POD_IP
  valueFrom:
    fieldRef:
      fieldPath: status.podIP

# Resource info
- name: CPU_LIMIT
  valueFrom:
    resourceFieldRef:
      containerName: app
      resource: limits.cpu
```

## Volume Mounts

```yaml
volumes:
- name: data
  emptyDir: {}
- name: config
  configMap:
    name: my-config
- name: secret
  secret:
    secretName: my-secret
- name: pvc
  persistentVolumeClaim:
    claimName: my-pvc
- name: hostpath
  hostPath:
    path: /var/lib/foo

containers:
- name: app
  volumeMounts:
  - name: data
    mountPath: /data
  - name: config
    mountPath: /etc/config
    readOnly: true
```

## Restart Policy

```yaml
spec:
  restartPolicy: Always   # default
  # OnFailure | Never
```

- **Always**: Deployment / DaemonSet / StatefulSet
- **OnFailure**: Job
- **Never**: Job
- Pod-level (not per-container)

## Pod Anti-Patterns

- "Pet" pods (named, hand-managed)
- Multiple unrelated containers
- Long-running pods with no restart strategy
- No resources requests
- No probes
- Privileged containers

## Naked Pods

Pods created directly:
```bash
kubectl run my-pod --image=nginx
```

Pros: simple.
Cons:
- Not restarted if deleted
- Not replicated
- No rollout

For prod: Deployment / StatefulSet / Job.

Use bare pods for: debugging, one-shot tasks.

## Pod Topology

```yaml
topologySpreadConstraints:
- maxSkew: 1
  topologyKey: topology.kubernetes.io/zone
  whenUnsatisfiable: DoNotSchedule
  labelSelector:
    matchLabels:
      app: web
```

For: spread replicas across zones.

## kubectl Commands

```bash
kubectl get pods
kubectl get pods -o wide                # IP, node
kubectl describe pod <name>
kubectl logs <name>
kubectl logs <name> -c <container>      # specific container
kubectl logs <name> -f                  # follow
kubectl logs <name> --previous          # last terminated
kubectl exec -it <name> -- /bin/sh
kubectl port-forward <name> 8080:80     # local forward
kubectl cp <name>:/path local-path      # copy file
kubectl delete pod <name>
kubectl debug -it <name> --image=busybox --target=<container>
```

## Pod CIDR

Cluster has pod CIDR; each node gets sub-range.

VPC CNI (AWS): pods use VPC IPs.
Calico / Flannel: overlay; pods in dedicated CIDR.

## Common Mistakes

- No resource requests
- No probes
- One container per pod always (sometimes sidecar useful)
- HostPath volumes (tight coupling)
- Privileged
- Single replica naked Pod for prod

## Best Practices

- Use Deployment (not bare Pod)
- Resource requests + limits
- Probes (all 3 where applicable)
- Security context (non-root)
- ServiceAccount minimal
- Topology spread for HA
- Native sidecars for mesh

## Quick Refs

```bash
# Apply
kubectl apply -f pod.yaml

# Get
kubectl get pod my-pod -o yaml

# Logs / exec
kubectl logs my-pod
kubectl exec -it my-pod -- bash

# Delete
kubectl delete pod my-pod

# Force (stuck)
kubectl delete pod my-pod --force --grace-period=0
```

## Interview Prep

**Junior**: "What's a pod."

**Mid**: "Init vs sidecar."

**Senior**: "QoS class implications."

**Staff**: "Pod design for tier-0 service."

## Next Topic

→ [T02 — ReplicaSets & Deployments](T02-ReplicaSets-Deployments.md)
