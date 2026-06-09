# L13/C05/T04 — Stateful Workloads & Data Gravity

## Learning Objectives

- Handle stateful in K8s
- Understand data gravity

## Data Gravity

Data is heavy; hard to move. Application moves to data, not vice versa.

Implications:
- DB on-prem? Apps near it.
- Multi-region: replication, not move.
- Cross-cloud: $$$ and slow.

## K8s + Stateful Tension

K8s designed for stateless:
- Cattle (kill, replace)
- Ephemeral
- Replicated

Stateful:
- Pets (named, important)
- Persistent
- Unique state

Solutions:
- StatefulSet
- Operators
- External managed services

## When K8s for Stateful

Pros:
- Portable
- Cost (vs managed at scale)
- Operator-managed automation
- Same tooling as stateless

Cons:
- Complexity
- Risk on PVC mistakes
- Operator maturity varies
- Disaster recovery harder

## Managed Service Often Better

For most:
- RDS / Aurora for SQL
- DynamoDB / Cosmos for NoSQL
- ElastiCache / Memorystore for cache
- MSK / Kafka cloud for streaming

Saves ops. Pays premium.

## Operators for K8s Stateful

For postgres:
- Zalando postgres-operator
- Crunchy Data PG Operator
- Cloud Native PG (CNPG)

For Cassandra: cass-operator.
For Kafka: Strimzi.
For MongoDB: community / enterprise.

Operators provide:
- Initial deployment
- Backups
- Failover
- Schema migration
- Scaling
- Monitoring

For: K8s stateful that's manageable.

## Storage Options

| | Pros | Cons |
|---|---|---|
| EBS / cloud block | Performant; familiar | Per-AZ; portability |
| EFS / cloud file | RWX; multi-pod | Slower; not for DB |
| Local NVMe | Fastest | Tied to node; lost on terminate |
| External SAN | Reliable; shared | Setup; cost |

For DB: EBS gp3/io2.
For shared: EFS.
For perf: local NVMe (rebuild on failure).

## High Performance: Local NVMe

```yaml
storageClassName: local-storage
```

Pros: 100k+ IOPS; sub-ms latency.
Cons: data lost on node terminate; pod tied to specific node.

For Cassandra, Elasticsearch: data replicated across nodes; can rebuild.

## Pod Disruption Budget

PDB protects stateful:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: db
```

Voluntary disruptions (drain) respect PDB. Involuntary (node crash): doesn't apply.

## Cluster Identity per Pod

StatefulSet provides ordinal:
- db-0, db-1, db-2

DB software (Cassandra, Kafka) uses to identify members.

For peer discovery: headless Service.

## Initialization

First pod: bootstrap cluster.
Subsequent: join.

```yaml
initContainers:
- name: bootstrap
  command: ["sh", "-c", "if [ $HOSTNAME = db-0 ]; then bootstrap; else join; fi"]
```

Or operator handles.

## Backup

Approaches:
- Snapshot via CSI (storage-level)
- App-level dump (pg_dump, mongodump)
- Streaming replication to backup cluster
- Velero (K8s-aware)

For prod: multi-layered.

## Velero

K8s backup tool:
- Backs up resources (Deployment, StatefulSet, etc.)
- Backs up PV data (via CSI snapshot or restic)
- Stores in S3
- Restore to same / different cluster

```bash
velero install --provider aws --plugins velero/velero-plugin-for-aws:v1.7.0 --bucket my-backups --backup-location-config region=us-east-1
velero backup create my-backup --include-namespaces production
velero restore create --from-backup my-backup
```

For DR.

## Disaster Recovery

For stateful:
1. Backup regularly (snapshot + ship)
2. Replicate cross-region (streaming)
3. Test restore quarterly
4. RTO / RPO defined

Without test: assume DR doesn't work.

## Resource Limits

For stateful: be careful with limits.

CPU throttling can corrupt some DBs.

Memory limit hit → OOM kill → restart → potential corruption.

Set generously. Monitor.

## QoS Class Guaranteed

```yaml
resources:
  requests:
    cpu: 2
    memory: 8Gi
  limits:
    cpu: 2
    memory: 8Gi
```

Guaranteed: not evicted under node pressure.

For stateful: use Guaranteed.

## Anti-Affinity

Replicas on different nodes:
```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchLabels:
          app: db
      topologyKey: kubernetes.io/hostname
```

Across zones:
```yaml
topologyKey: topology.kubernetes.io/zone
```

## Single-AZ vs Multi-AZ

EBS is AZ-bound. StatefulSet with PVC: pods stuck in original AZ.

For multi-AZ stateful: replicas in different AZs, each with own PVC in their AZ.

Topology spread + storage topology align.

## When Stateful Right in K8s

- Standard databases with mature operators
- Caching / session stores
- Message queues (Kafka, RabbitMQ)
- Internal apps (Redis as primary store)

When Stateful Wrong in K8s

- Multi-master DBs requiring complex consensus
- Latency-critical specific hardware
- High-IOPS budget-constrained (cloud RAID complex)
- Massive scale (>10 TB; manageability)

For: use managed service.

## Multi-Cluster Stateful

Each cluster has own stateful set:
- Cross-cluster replication (DB-level)
- Application routes to local

For: regional latency + DR.

## Patterns

### Primary-Replica (Postgres)
- StatefulSet with replicas: 3
- Pod 0: primary; 1, 2: replicas
- Operator handles failover

### Sharded (Cassandra)
- StatefulSet with replicas: N (where N = shard count)
- Each pod owns slice
- Data redistributed on add/remove

### Single Instance (Redis Cache)
- StatefulSet replicas: 1
- Stable PVC for persistence (optional)
- LB in front (Service)

For HA: Redis Sentinel / Cluster mode.

## Operations

```bash
# Status
kubectl get sts
kubectl rollout status sts/db

# Scale
kubectl scale sts/db --replicas=5

# Delete (preserves PVCs)
kubectl delete sts/db

# PVC retain after delete
spec:
  persistentVolumeClaimRetentionPolicy:
    whenDeleted: Retain
```

## Common Mistakes

- Stateful without backup
- No anti-affinity (single node failure → cluster down)
- PVC delete policy (lose data)
- Memory limit too low (OOM)
- Single-AZ
- No DR testing

## Best Practices

- Operator if available
- Backup + DR tested
- Anti-affinity
- Multi-AZ
- Guaranteed QoS
- Generous resources
- Monitor: replication lag, disk usage, slow queries
- PV expansion enabled
- Documented runbook

## Real Operators

### CNPG (CloudNativePG)
```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
spec:
  instances: 3
  storage:
    size: 50Gi
    storageClass: gp3
  backup:
    barmanObjectStore:
      destinationPath: s3://my-backups
```

Handles HA, backups, point-in-time recovery.

### Strimzi (Kafka)
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
spec:
  kafka:
    replicas: 3
    storage:
      type: persistent-claim
      size: 100Gi
```

## Decision Tree

For new stateful workload:
1. Is managed service available? → Use it.
2. Tight compliance forces self-host? → K8s with operator.
3. Strong reason to be on K8s? → K8s with operator.
4. Otherwise → managed.

## Quick Refs

```bash
# Backups
velero backup create daily --include-namespaces prod --ttl 720h

# Snapshots
kubectl apply -f volume-snapshot.yaml

# Operator install
helm install postgres-operator postgres-operator/postgres-operator
```

## Interview Prep

**Mid**: "Stateful in K8s — challenges."

**Senior**: "Postgres on K8s vs RDS."

**Staff**: "Multi-region stateful platform design."

## Next Topic

→ [T05 — Snapshots](T05-Snapshots.md)
