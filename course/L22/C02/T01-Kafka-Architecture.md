# L22/C02/T01 — Kafka Architecture (Broker, ZooKeeper / KRaft)

## Learning Objectives

- Understand Kafka components
- Install cluster

## Components

- Broker (storage + serve)
- Producer (write)
- Consumer (read)
- Coordinator (KRaft or ZooKeeper)

## ZooKeeper (Legacy)

Coordinates:
- Broker membership
- Topic metadata
- Consumer offsets (older)
- Controller election

3-5 ZK servers.

## KRaft (Modern)

Kafka 3.3+:
- Built-in Raft consensus
- No ZooKeeper
- Easier ops

Future: KRaft only.

## Install

```bash
# Download Kafka
wget https://downloads.apache.org/kafka/...

# KRaft mode (modern)
bin/kafka-storage.sh format -t $(bin/kafka-storage.sh random-uuid) -c config/kraft/server.properties
bin/kafka-server-start.sh config/kraft/server.properties
```

## Cluster Setup

3+ brokers typical:
```properties
broker.id=1
process.roles=broker,controller
controller.quorum.voters=1@broker1:9093,2@broker2:9093,3@broker3:9093
listeners=PLAINTEXT://:9092,CONTROLLER://:9093
log.dirs=/var/kafka-data
```

## Topic

```bash
bin/kafka-topics.sh --bootstrap-server localhost:9092 --create \
  --topic events \
  --partitions 12 \
  --replication-factor 3
```

## Partition

Topic split:
- Distribute load
- Parallelism
- Scale

12 partitions × 3 replicas = 36 stores.

## Replicas

- Leader: writes
- Follower: replicate

If leader fails: follower elected.

## ISR (In-Sync Replicas)

Replicas caught up.

Write requires:
- `acks=all`: all ISR ack

For: durability.

## Min ISR

```properties
min.insync.replicas=2
```

If < 2 in ISR: writes fail.

For: prevent silent data loss.

## Log Storage

Per partition:
- Files (segments)
- Append-only
- Sequential write fast

## Retention

```properties
log.retention.hours=168   # 7 days
log.retention.bytes=1073741824   # 1 GB per partition
```

Older segments deleted.

## Compaction

```properties
log.cleanup.policy=compact
```

Keep only latest per key.

For: state stores.

## Producer

```python
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['broker:9092'],
    acks='all',
    enable_idempotence=True,
)

producer.send('events', key=b'user-1', value=b'hello')
producer.flush()
```

## Consumer

```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'events',
    bootstrap_servers=['broker:9092'],
    group_id='my-group',
    auto_offset_reset='earliest',
)

for msg in consumer:
    process(msg)
```

## Consumer Group

Multiple consumers in group:
- Partitions distributed
- Each partition: one consumer
- Parallel processing

## Throughput

Per partition:
- 100k-1M msg/sec
- 100 MB/s+

For: scale via partitions.

## Latency

End-to-end:
- < 10 ms typical
- < 1 ms possible (tight)

## Disk

Sequential write:
- SSD or HDD OK
- Fast even on HDD (sequential)

## Network

Crucial:
- 10 Gbps for high throughput
- Replication 3× = 3× bandwidth

## Best Practices

- 3-5 brokers HA
- 3 replicas per topic
- min.insync.replicas=2
- KRaft (no ZK)
- Monitor under-replicated partitions
- SSD for hot
- Network 10 Gbps+

## Common Mistakes

- 1 broker (no HA)
- replication.factor=1 (no replicas)
- No min ISR (silent loss)
- ZK without good HA

## Quick Refs

```bash
# Topic
kafka-topics.sh --create / --list / --describe / --delete

# Console producer/consumer
kafka-console-producer.sh
kafka-console-consumer.sh

# Group
kafka-consumer-groups.sh --describe --group X

# Performance
kafka-producer-perf-test.sh
kafka-consumer-perf-test.sh
```

## Interview Prep

**Mid**: "Kafka basics."

**Senior**: "Broker / ZK / KRaft."

**Staff**: "Kafka architecture."

## Next Topic

→ [T02 — Topics, Partitions, Replicas](T02-Topics-Partitions.md)
