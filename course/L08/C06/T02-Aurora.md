# L08/C06/T02 — Aurora Architecture (Storage Layer, Global DB)

## Learning Objectives

- Understand Aurora's unique architecture
- Use Aurora features

## Aurora

AWS's cloud-native RDBMS. MySQL or Postgres compatible.

Looks like RDS but architected differently underneath.

## Key Differences from RDS

| | RDS | Aurora |
|---|---|---|
| Storage | EBS per instance | Shared distributed |
| Replicas | Async copy | Read from shared storage |
| Replica lag | Seconds | Milliseconds |
| Max read replicas | 5 | 15 |
| Failover | ~60s | ~30s |
| Backup | Snapshots | Continuous to S3 |
| Multi-region | Read replica | Global Database |
| Serverless | No | Yes (v2) |

## Storage Architecture

Aurora storage:
- Cluster volume (logical), 6 copies across 3 AZs
- Quorum: 4/6 for write, 3/6 for read
- Self-healing (lost segments rebuild)
- Up to 128 TB

Compute (DB instances) is decoupled. Multiple instances share single storage.

## Cluster

Aurora "cluster":
- 1 writer instance (primary)
- 0-15 reader instances (replicas)
- All share storage

Replica != copy. Reader sees same data as writer immediately (sub-ms).

## Cluster Endpoints

- **Cluster endpoint (writer)**: always points to writer
- **Reader endpoint**: load-balanced across readers
- **Custom endpoints**: subset of readers (e.g., analytics-only)
- **Instance endpoints**: specific instance

App typically: cluster endpoint for writes; reader endpoint for reads.

## Failover

Writer fails:
1. Aurora promotes a reader to writer (~30s)
2. Cluster endpoint DNS updates
3. App reconnects

Faster than RDS Multi-AZ because storage is already shared.

## Backtrack

Rewind DB to point in past (up to 72 hours):
```bash
aws rds backtrack-db-cluster --db-cluster-identifier mycluster --backtrack-to 2026-06-09T10:00:00Z
```

No restore-to-new-instance; same cluster reverted. Use for accidental data corruption.

MySQL-compatible only.

## Aurora Global Database

Multi-region:
- Primary region: writer + readers
- Secondary region(s): read-only replicas
- Cross-region replication: <1s typically; dedicated infrastructure
- Promote secondary to primary on disaster (~1 min)

For: low-latency global reads + DR.

```bash
aws rds create-global-cluster --global-cluster-identifier myglobal --source-db-cluster-identifier mycluster
```

Up to 5 secondary regions.

## Aurora Serverless v2

Auto-scale ACUs (Aurora Capacity Units; mix CPU+RAM):
- Scale up in seconds
- Scale down when idle
- Min ACU: 0.5 (always-on)
- Max ACU: 256 (huge)

For: variable workloads, dev/test, microservices with sporadic load.

```bash
aws rds create-db-cluster --engine aurora-postgresql --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=16 ...
```

## Aurora Serverless v1 (Legacy)

Older; cold start; pause when idle. Mostly superseded by v2.

## Aurora I/O Optimized

For high-I/O workloads:
- No per-I/O charges
- Higher instance / storage cost
- Break-even ~25% I/O cost

For OLTP: usually I/O Optimized makes sense.

## Aurora vs RDS Cost

Aurora:
- More expensive per instance hour
- No I/O charges (with I/O Optimized) vs RDS pays per I/O
- More features

For typical OLTP: similar total cost.

## Aurora Limitless Database

Newer (2024+): horizontal scaling beyond single writer:
- Shard automatically
- For massive write throughput
- Postgres compatible

For very high write QPS.

## Aurora Zero-ETL

Direct integration with Redshift / Athena / OpenSearch:
- No ETL pipeline
- Real-time data replication
- For analytics on operational data

## Aurora Performance

vs same-spec MySQL/Postgres:
- 3-5× read perf
- 5× throughput
- Better failover
- More replicas

Storage IOPS not your concern; handled internally.

## Aurora Storage Pricing

Per GB-month + per million I/O requests (without I/O Optimized).

I/O Optimized: 25% more storage + larger instance class but no I/O charge.

## Limits

- 128 TB storage
- 15 read replicas
- Up to 96 vCPU per instance

For more: shard at app level OR Limitless.

## Aurora Reader Auto Scaling

Auto-add/remove readers based on CPU / connections:
```yaml
PolicyType: TargetTrackingScaling
TargetValue: 70
PredefinedMetricSpecification:
  PredefinedMetricType: RDSReaderAverageCPUUtilization
```

## Connection Pooling

RDS Proxy works with Aurora. Mandatory for Lambda + Aurora at scale.

## Aurora vs DynamoDB

| | Aurora | DynamoDB |
|---|---|---|
| Model | Relational | Key-value / Document |
| Schema | Strict | Flexible |
| Queries | SQL, joins | PK lookup, indexed |
| Scale | Up to 96 vCPU; 128 TB | Unlimited |
| Latency | ms (cached: sub-ms) | sub-ms predictable |
| Cost (small) | Cheap | Cheap |
| Cost (huge) | Expensive | Predictable |
| Operations | Some (failover) | None |

For new relational: Aurora.
For high-scale KV: DynamoDB.

## Aurora Compatibility

Aurora MySQL:
- 95%+ MySQL compatible
- Most apps work without changes

Aurora Postgres:
- 100% Postgres compatible

Aurora-specific features beyond engine.

## When NOT Aurora

- Massive scale (>96 vCPU writer) → consider DynamoDB / Limitless / sharding
- Specific Oracle/SQL Server features → RDS Oracle/SQL Server
- Tiny budget app → smaller RDS

## Failover Test

```bash
aws rds failover-db-cluster --db-cluster-identifier mycluster
```

Test regularly. App handles reconnect gracefully?

## DR Strategies (Aurora)

1. **In-region HA**: Multi-AZ (built-in)
2. **Cross-region read**: Global Database (~1s RPO)
3. **Backup-restore**: snapshot to S3; restore in another region
4. **DMS replication**: to non-Aurora target

Global DB best for tight RPO/RTO.

## Backup

Continuous backup to S3:
- Always running; no perf impact
- PITR to any second within retention
- Retention 1-35 days

Snapshots: extra; persist beyond retention.

## Monitoring

CloudWatch:
- DatabaseConnections
- CPU
- ReadIOPS / WriteIOPS
- ReplicaLag (sub-ms typically)
- AuroraReplicaLag (specific Aurora)
- ServerlessDatabaseCapacity (v2)

Performance Insights: built-in.

## Common Mistakes

- Using regular RDS for high-traffic when Aurora better
- Aurora without I/O Optimized for I/O-heavy
- No connection pooling
- Treating reader endpoint as strong-consistent (it's milliseconds behind)
- Single-region without Global DB for tier-0

## Best Practices

- Aurora over RDS for new high-traffic apps
- Global DB for tier-0 multi-region
- I/O Optimized for OLTP
- Serverless v2 for variable
- RDS Proxy for many connections
- Reader auto-scaling
- Monitor replication lag

## Cost

For 1 vCPU 8 GB equivalent:
- RDS Postgres: ~$200/mo
- Aurora Postgres: ~$300/mo
- Aurora Serverless v2 (0.5 ACU): ~$45/mo idle; scales up

Burst workload: Serverless wins.
Steady: Aurora provisioned.

## Quick Refs

```bash
# Create cluster
aws rds create-db-cluster --db-cluster-identifier mycluster --engine aurora-postgresql --engine-version 16 ...

# Add instance to cluster
aws rds create-db-instance --db-instance-identifier mywriter --db-cluster-identifier mycluster --engine aurora-postgresql --db-instance-class db.r6g.large

# Global database
aws rds create-global-cluster --global-cluster-identifier myglobal --source-db-cluster-identifier mycluster
```

## Interview Prep

**Mid**: "Aurora vs RDS."

**Senior**: "Aurora storage architecture."

**Staff**: "Multi-region tier-0 DB design."

## Next Topic

→ [T03 — DynamoDB Deep Dive](T03-DynamoDB.md)
