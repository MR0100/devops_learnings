# L08/C03/T03 — Placement Groups (Cluster, Spread, Partition)

## Learning Objectives

- Pick placement group type
- Apply to right workload

## Three Types

| | Goal | Topology |
|---|---|---|
| Cluster | Low latency | Same rack |
| Spread | Independent failure | Different hardware |
| Partition | Balanced isolation | Groups of racks |

## Cluster

Instances physically close: low-latency, high-throughput network.

Use:
- HPC (tightly-coupled compute, MPI)
- High-frequency trading
- Big data (intra-cluster shuffle)

```bash
aws ec2 create-placement-group --group-name my-cluster --strategy cluster
aws ec2 run-instances --placement GroupName=my-cluster ...
```

Constraints:
- Same AZ
- Specific instance types (mostly all modern)
- Max instances = capacity available in that rack

Performance: up to ~10 Gbps full-duplex between instances.

## Spread

Instances on different hardware. Each on distinct rack.

Use:
- Critical apps where instance failure should not affect others
- Master nodes (e.g., HA DBs)

Limits:
- 7 instances per AZ
- Can span multiple AZs

For 7+ critical: use Partition.

## Partition

Logically split into partitions; each on distinct rack.

Use:
- HDFS, Cassandra, Kafka — distributed systems with replica awareness

Up to 7 partitions per AZ; up to hundreds of instances per partition.

Each partition independent failure domain.

App can be aware (Cassandra's rack-awareness uses partition info).

## When Each

| Workload | Group |
|---|---|
| MPI compute | Cluster |
| Active-passive DB | Spread (primary + standby) |
| Distributed DB (Cassandra) | Partition |
| Stateless web tier | Maybe Spread for critical mass; usually none |
| Latency-critical < 10us | Cluster |

For most apps: no placement group needed (AWS spreads adequately).

## Cluster Performance

Within cluster group:
- Up to 100 Gbps between EFA-enabled instances
- Low latency (microseconds)
- Use EFA + cluster for HPC

## Mixed With ASG

ASG can be in placement group:
```yaml
LaunchTemplate:
  PlacementGroupId: pg-xxx
```

For ASGs needing topology guarantees.

## Migration

Can launch into existing PG. Move existing? Stop, change placement, start (for Spread/Partition; Cluster more complex).

## Cost

PG itself free. Spread / Partition can save by reducing failure domain overlap.

## Limits

- Cluster: AZ has limited capacity; large clusters may fail
- Spread: 7 per AZ
- Partition: 7 partitions per AZ; up to 100s per partition

## Cross-AZ

- Cluster: same AZ only
- Spread: multi-AZ
- Partition: multi-AZ

## Tags

Tag PG; appear in cost / inventory reports.

## Best Practices

- Cluster: HPC + EFA
- Spread: <7 critical instances
- Partition: distributed DB on AWS
- Otherwise: don't use; AWS placement is fine

## Common Mistakes

- Cluster for non-HPC (overhead with no benefit)
- Spread > 7 instances (fails)
- Forgetting to specify in launch
- Cluster across AZs (impossible)

## Quick Refs

```bash
aws ec2 create-placement-group --group-name pg-x --strategy cluster
aws ec2 describe-placement-groups
aws ec2 delete-placement-group --group-name pg-x
```

## Interview Prep

**Mid**: "Cluster vs Spread vs Partition."

**Senior**: "Cassandra deployment with placement groups."

**Staff**: "Capacity planning across AZs with cluster groups."

## Next Topic

→ [T04 — EBS Types and Performance](T04-EBS-Performance.md)
