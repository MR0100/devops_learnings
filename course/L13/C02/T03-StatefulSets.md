# L13/C02/T03 — StatefulSets

## Learning Objectives

- Run stateful workloads
- Use ordered pods, stable identity

## StatefulSet

For pods that need:
- Stable, unique network identity
- Stable persistent storage
- Ordered, graceful deployment / scaling
- Ordered, automated rolling update

E.g., databases, message queues, distributed systems.

## YAML

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: db
spec:
  serviceName: db-headless
  replicas: 3
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
      - name: postgres
        image: postgres:15
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ReadWriteOnce]
      storageClassName: gp3
      resources:
        requests:
          storage: 50Gi
```

## Key Differences From Deployment

| | Deployment | StatefulSet |
|---|---|---|
| Pod names | Random suffix | Ordinal (web-0, web-1, web-2) |
| Order | Parallel | Ordered (0 first, N last) |
| Storage | Shared / none | Per-pod PVC |
| Identity | Ephemeral | Stable (DNS, hostname) |
| Update | Random | Reverse order (N first) |

## Pod Identity

Pods named `<set>-0`, `<set>-1`, `<set>-2`.

Stable across:
- Rescheduling
- Restart
- Rolling update

Pod IP changes; hostname stable.

## Headless Service

Required for stable DNS:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: db-headless
spec:
  clusterIP: None
  selector:
    app: db
  ports:
  - port: 5432
```

DNS:
- `db-0.db-headless.namespace.svc.cluster.local`
- `db-1.db-headless.namespace.svc.cluster.local`
- ...

Stable; resolvable.

## Persistent Volumes

`volumeClaimTemplates`: each pod gets own PVC:
- `data-db-0`: PVC for db-0
- `data-db-1`: for db-1
- ...

Stable across pod restart (same PVC reattached to same pod ordinal).

## Ordered Operations

### Deploy
Pod 0 created. Wait Ready. Then 1. Then 2.

For: leader-follower (0 = leader; 1, 2 follow).

### Scale Up
Add pod 3. Wait Ready. Then 4.

### Scale Down
Remove highest ordinal first. Wait gone. Then next.

### Rolling Update
Update highest first; wait; next lower; ...

Reverse of deploy order.

## podManagementPolicy

```yaml
spec:
  podManagementPolicy: OrderedReady  # default
  # Parallel
```

`Parallel`: don't wait between pods. Faster but no ordering guarantee.

For: when order doesn't matter (e.g., independent shards).

## Update Strategies

### RollingUpdate (Default)
Reverse order; one at a time.

```yaml
updateStrategy:
  type: RollingUpdate
  rollingUpdate:
    partition: 0
    maxUnavailable: 1   # 1.27+
```

`partition`: update only ordinals >= N. For staged updates.

### OnDelete
Don't auto-update. User deletes; new pod is updated.

For manual control.

## Use Cases

### Distributed DB
Cassandra, Cockroach, etcd, Consul:
- Stable names
- Discover peers via DNS
- Persistent storage

### Stateful Apps
Kafka brokers, Zookeeper:
- Identity per broker (broker.id matches ordinal)

### Single-Instance with State
Redis primary:
- replicas: 1
- Stable storage

## Persistent Volume Lifecycle

PVCs not deleted when pod / StatefulSet deleted (default).

```yaml
spec:
  persistentVolumeClaimRetentionPolicy:
    whenDeleted: Retain    # or Delete
    whenScaled: Retain     # or Delete
```

For: data preserved across operations.

To actually delete: manual `kubectl delete pvc`.

## DNS Records

For headless Service `db-headless`:
- `db-0.db-headless` → pod 0 IP
- `db-1.db-headless` → pod 1 IP
- ...

App configures with these names; auto-resolves.

For peer discovery in distributed systems.

## Application Patterns

### Leader Election
Pod 0 = leader; others = followers.

Or use Raft (etcd) / Paxos / Bully for election; identity from ordinal.

### Shard Per Pod
Each pod owns a shard. Data partitioned by ordinal.

### Anti-Affinity
Each pod on different node:
```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchLabels:
          app: db
      topologyKey: kubernetes.io/hostname
```

## Operations

```bash
# Get
kubectl get statefulset
kubectl get pods -l app=db

# Scale
kubectl scale statefulset/db --replicas=5

# Update image
kubectl set image statefulset/db postgres=postgres:16

# Status
kubectl rollout status statefulset/db
```

## Delete

```bash
kubectl delete statefulset db
# Pods deleted; PVCs remain
```

To cascade-delete PVCs: use `persistentVolumeClaimRetentionPolicy: Delete`.

## Operators

For complex stateful: use operators:
- postgres-operator (Zalando, Crunchy, etc.)
- mysql-operator
- mongodb-community-operator
- cassandra-operator
- redis-operator

Operators add intelligence:
- Backups
- Failover
- Schema migrations
- Replication setup

Building on StatefulSet primitive.

## Failure Modes

### Pod Restart
- Same name; same PVC reattached
- Container restarts; data preserved

### Node Failure
- Pod stuck Terminating (kubelet unreachable)
- New pod NOT created until old GONE (avoids two pods writing same volume)
- Manual intervention: `kubectl delete pod --force --grace-period=0` (DANGEROUS)

### PVC Stuck
- Volume can't detach (node gone)
- New pod waits forever
- Force delete (risk data loss)

For: cluster-aware operators handle.

## Single-Pod Patterns

Sometimes single replica (DB primary):
```yaml
replicas: 1
```

Use StatefulSet (not Deployment) for stable storage + identity.

## Storage Considerations

- Use SSD for DB
- Local disk for performance (sacrifice mobility)
- Network attached for portability

Trade-offs covered in C05.

## Backup

StatefulSet doesn't back up. You implement:
- Sidecar with backup tool
- CronJob with kubectl exec into pod
- Volume snapshots (CSI)

Or operator.

## Common Mistakes

- Use Deployment for stateful (PVC shared = race)
- Forget headless Service (no stable DNS)
- No PV retention policy (lose data on scale down)
- Updating image without testing (data corruption)
- Anti-affinity missing (replicas on same node)

## Best Practices

- StatefulSet for stateful
- Headless Service for DNS
- Anti-affinity
- PV retention policy
- Backup strategy
- Operator for complex apps
- Resource requests/limits
- Probes designed for state

## DB on K8s vs Managed

Managed (RDS, Aurora): operator overhead avoided.
K8s DB: portability, cost, multi-cloud.

For most: managed if available.
K8s DB: when constraints force (on-prem, multi-cloud, vendor-locked).

## Quick Refs

```yaml
spec:
  serviceName: db-headless    # REQUIRED
  replicas: 3
  podManagementPolicy: OrderedReady  # or Parallel
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 0
  volumeClaimTemplates:
  - metadata: {name: data}
    spec:
      accessModes: [ReadWriteOnce]
      resources: {requests: {storage: 50Gi}}
```

## Interview Prep

**Mid**: "StatefulSet vs Deployment."

**Senior**: "DB on K8s — operate."

**Staff**: "Distributed DB design with StatefulSet."

## Next Topic

→ [T04 — DaemonSets](T04-DaemonSets.md)
