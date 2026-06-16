# L08/C10/T05 — MSK (Managed Kafka)

## Learning Objectives

- Use MSK for Kafka
- Pick MSK vs alternatives

## MSK

Amazon Managed Streaming for Apache Kafka.

AWS manages: brokers, ZooKeeper (legacy), KRaft (newer), patches, monitoring.

You: topics, partitions, producers, consumers.

## Kafka Concepts

- **Cluster**: set of brokers
- **Topic**: named stream
- **Partition**: ordered shard of a topic
- **Producer**: writes
- **Consumer**: reads (group-based)
- **Offset**: per-partition position

## MSK Setup

```bash
aws kafka create-cluster \
  --cluster-name myCluster \
  --kafka-version 3.7.0 \
  --number-of-broker-nodes 3 \
  --broker-node-group-info '{
    "InstanceType": "kafka.m5.large",
    "ClientSubnets": ["subnet-a","subnet-b","subnet-c"],
    "SecurityGroups": ["sg-..."]
  }'
```

Returns cluster ARN; brokers boot.

## MSK Serverless

Newer: auto-scale; pay per usage:
- No instance management
- Capacity scales with throughput

For: variable workloads; lower ops.

Limits:
- Max 24 MB/s sustained per partition
- Max 200 partitions per cluster (recently raised)

## Authentication

- IAM: AWS-native (recommended)
- TLS mutual auth
- SASL/SCRAM (username/password)
- No auth (plaintext)

For production: IAM (simplest, integrates with AWS).

## Authorization

ACLs: per-topic, per-operation.

```bash
kafka-acls.sh --add --producer --topic my-topic --allow-principal User:CN=my-user
```

For IAM: IAM policy controls actions.

## Topics

Create:
```bash
kafka-topics.sh --create --topic my-topic --partitions 12 --replication-factor 3
```

Partitions: ordering scope; parallelism.
Replication: copies (default 3 for durability).

## Producer

```python
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=["b-1.cluster:9092"],
    security_protocol="SASL_SSL",
    sasl_mechanism="AWS_MSK_IAM",
    sasl_oauth_token_provider=...,
)

producer.send("my-topic", key=b"key", value=b"value")
producer.flush()
```

## Consumer

```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    "my-topic",
    group_id="my-group",
    bootstrap_servers=...,
    ...
)

for message in consumer:
    process(message)
    consumer.commit()
```

## Consumer Groups

Multiple consumers in group share partitions:
- 12 partitions; 4 consumers → 3 partitions each
- Adding consumer rebalances
- Each partition processed by one consumer (per group)

For: parallelism + ordered per-key.

## Replication

- replication-factor: copies on different brokers (3 typical)
- Leader: handles writes
- Followers: replicate
- ISR (in-sync replicas): caught up

Producer acks:
- 0: fire-forget (fastest, unsafe)
- 1: leader ack (default)
- all: all ISR ack (safest)

## Retention

Default 7 days; configurable per topic.

Log compaction: keep latest per key (vs delete by age).

For: long retention with key updates.

## Schema Registry

AWS Glue Schema Registry:
- Avro, JSON, Protobuf schemas
- Validate at producer / consumer
- Evolution rules

For typed events.

## Connectors

Managed Connectors (MSK Connect):
- Source: pull from DB, etc.
- Sink: push to S3, Redshift, etc.

Built on Kafka Connect framework.

## Mirror Maker

Replicate between clusters:
- Cross-region DR
- Multi-cluster aggregation

MSK supports.

## Pricing

Provisioned:
- Per broker hour ($0.21 for kafka.m5.large)
- Storage per GB-mo
- Data transfer

3 broker × $0.21 × 24 × 30 = $454/mo minimum.

Serverless:
- $0.75 per cluster-hour ($540/mo base)
- Plus throughput

For small: Serverless higher base; for medium+: provisioned.

## MSK vs Kinesis

| | MSK | Kinesis |
|---|---|---|
| Standard | Kafka | AWS-proprietary |
| Throughput | High; tunable | Per-shard limit |
| Latency | Sub-ms | Sub-second |
| Ecosystem | Huge | AWS |
| Operations | More | Less |
| Cost | Higher base | Per shard |

For Kafka ecosystem / cross-cloud: MSK.
For AWS-only / simpler: Kinesis.

## When MSK

- Existing Kafka infrastructure
- Kafka Streams / KSQL workloads
- Cross-cloud / portability
- High throughput
- Specific Kafka features (compaction, exactly-once, transactions)

## When NOT MSK

- AWS-only and Kinesis sufficient
- Small workload (overhead)
- No Kafka expertise

## Patterns

### Event Streaming Platform
```
Microservices → MSK → consumers (services, analytics, ML)
```

### Change Data Capture
```
Database → Debezium connector → MSK → consumers
```

### Log Aggregation
```
Apps → MSK → consumers → ES / S3 / etc.
```

### Real-Time Analytics
```
MSK → Spark Streaming / Flink → results
```

## Performance Tuning

- Partitions: more = more parallelism
- Brokers: more = more throughput
- Instance type: m5.4xlarge for high throughput
- Acks: tradeoff durability vs latency
- Batch size on producer
- Compression (gzip, snappy, lz4)

## Operations

- Monitor metrics (CloudWatch + Open Monitoring)
- Patch (managed; you approve)
- Scale brokers (online)
- Scale storage (online)
- Rebalance partitions

## Open Monitoring

Prometheus / JMX exporters:
- Detailed Kafka metrics
- For self-managed dashboards

## Security

- IAM auth (recommended)
- TLS in transit (default)
- KMS encryption at rest
- VPC private
- SG controlling access

## Monitoring Metrics

CloudWatch + Open:
- BytesInPerSec, BytesOutPerSec
- MessagesInPerSec
- UnderReplicatedPartitions (problem)
- ActiveControllerCount (should be 1)
- OfflinePartitionsCount (should be 0)
- ConsumerLag per consumer group

Alert on:
- Lag growing
- Under-replicated
- Offline partitions

## Common Mistakes

- Too few partitions (no parallelism)
- Too many (overhead)
- Single AZ
- No monitoring of consumer lag
- Replication factor 1 (data loss on broker fail)

## Best Practices

- Replication factor 3
- Multi-AZ
- IAM auth
- Monitor consumer lag
- Right-size brokers
- Schema Registry
- Compression

## Migration

From self-hosted Kafka to MSK:
1. Set up MSK cluster
2. Mirror Maker replicates topics
3. Move consumers
4. Move producers
5. Decommission old

## MSK Connect

Managed Kafka Connect:
- Connectors as workers
- AWS handles scaling, monitoring
- Less ops than self-hosted Kafka Connect

## Quick Refs

```bash
# Create cluster
aws kafka create-cluster --cluster-name myCluster --kafka-version 3.7.0 --number-of-broker-nodes 3 --broker-node-group-info ...

# Get bootstrap brokers
aws kafka get-bootstrap-brokers --cluster-arn ...

# Topics (run on Kafka client; not AWS CLI)
kafka-topics.sh --create --topic my-topic --partitions 12 --replication-factor 3
```

## Interview Prep

**Mid**: "MSK vs Kinesis."

**Senior**: "Kafka cluster design at MSK."

**Staff**: "Event platform for 100 microservices."

## Next Topic

→ Move to [L08/C11 — Observability on AWS](../C11/README.md)
