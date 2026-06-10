# L22/C02/T07 — Operating Kafka in Production

## Learning Objectives

- Operate Kafka safely
- Capacity plan

## Cluster Sizing

For 1 TB/day:
- 3-5 brokers
- 50-100 partitions per topic
- SSD
- 10 Gbps network

For 100 TB/day:
- 20+ brokers
- Tiered storage maybe
- 25 Gbps network

## Hardware

- CPU: 16-32 cores
- RAM: 64-128 GB (most for page cache)
- Disk: NVMe SSD (10+ TB)
- Network: 10-25 Gbps

## Critical Metrics

```promql
# Under-replicated partitions
kafka_server_replicamanager_under_replicated_partitions

# Offline partitions
kafka_controller_kafkacontroller_offlinepartitionscount

# Request latency
kafka_network_requestmetrics_totaltimems

# Disk usage
kafka_log_log_size

# Consumer lag
kafka_consumer_lag_sum
```

## Alerts

- Under-replicated > 0
- Offline > 0
- Lag > threshold
- Disk > 80%
- Request latency p99 > 100ms

## Rebalance

When:
- Broker added
- Broker removed
- Manual

Tools:
- kafka-reassign-partitions.sh
- Cruise Control

Tip: throttle to avoid network saturation.

## Cruise Control

LinkedIn tool:
- Anomaly detection
- Workload balancer
- Auto-rebalance

For: easier ops.

## Upgrade

- Inter-broker protocol version
- Rolling broker by broker
- Producer / consumer compat

Test in staging.

## Monitoring Tools

- Confluent Control Center (paid)
- Kafka Manager (Yahoo; now CMAK)
- Conduktor (paid)
- Provectus UI
- Prometheus + Grafana

## Capacity Planning

Per partition:
- ~10-100 MB/s
- ~10k-100k msg/sec

Plan:
- Total throughput / per partition = partition count
- Plus replicas

## Disk Usage

```
disk = throughput × retention × replication
```

For 100 MB/s × 7 days × 3 = ~180 TB.

## Network

Replication amplifies:
- 100 MB/s in × 2 (replicate to followers) = 200 MB/s network

## Backups

Kafka:
- Mirror Maker 2 to another cluster
- Or just rely on replicas

Topic dump:
- kafkacat / kcat
- Tiered storage (cloud)

## Tiered Storage

Confluent / Apache (3.6+):
- Recent data: local SSD
- Old: S3 / cold

For: lower local disk; cheap retention.

## Multi-Cluster

For:
- DR
- Geo-distribution
- Workload separation

Use Mirror Maker 2.

## Security

- TLS broker-to-client
- TLS broker-to-broker
- SASL auth (SCRAM, OAUTH, Kerberos)
- ACL per topic/group

## ACL

```bash
kafka-acls --add --allow-principal User:alice \
  --operation Read --topic events --group my-group
```

For: least priv.

## Topic Lifecycle

```
Create:  bin/kafka-topics --create
Delete:  bin/kafka-topics --delete (must enable in broker)
Compact: cleanup.policy=compact
Retention: log.retention.hours
```

## Common Issues

- Disk full (alert before)
- Network saturation
- Under-replicated (broker issue)
- ZK unstable (move to KRaft)
- Stuck consumer (lag grows)

## Best Practices

- KRaft mode (modern)
- 3+ brokers
- Rack awareness
- TLS + SASL
- Cruise Control
- Tiered storage
- Monitor + alert

## Common Mistakes

- 1 broker (no HA)
- No monitoring
- Ignore under-replicated
- Skip upgrade testing
- No ACLs

## Quick Refs

```bash
# Cluster
kafka-broker-api-versions --bootstrap-server X

# Topics
kafka-topics --list / --describe

# Consumer groups
kafka-consumer-groups --list / --describe / --reset-offsets

# Reassign
kafka-reassign-partitions

# ACLs
kafka-acls --list
```

## Interview Prep

**Mid**: "Kafka ops."

**Senior**: "Production Kafka."

**Staff**: "Kafka platform."

## Next Topic

→ Move to [L22/C03 — RabbitMQ](../C03/README.md)
