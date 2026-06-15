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

Built-in Raft consensus; no ZooKeeper. Easier ops (one system to run, faster metadata, faster controller failover).

Timeline:
- **3.3** — KRaft declared production-ready for new clusters
- **3.5** — ZooKeeper mode deprecated; ZK→KRaft migration tooling matures
- **4.0** — ZooKeeper support fully removed; KRaft is the only mode (a ZK-based cluster cannot run 4.0 — migrate first)

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

**Mid**: "Explain Kafka's core architecture." — Brokers store and serve partitioned, replicated topic logs. Producers append to partitions; consumers read at their own offset. Each partition has a leader (handles writes) and followers that replicate; the in-sync replica (ISR) set plus `acks=all` and `min.insync.replicas` give durability. Consumer groups parallelize reads across partitions.

**Senior**: "ZooKeeper vs KRaft — where are we?" — KRaft replaces ZooKeeper with a built-in Raft metadata quorum, so there's one system to run, faster controller failover, and faster metadata propagation. Timeline: production-ready in 3.3, ZooKeeper deprecated in 3.5, ZooKeeper support fully removed in 4.0 — a ZK-based cluster must migrate before upgrading to 4.0.

**Staff**: "How do you guarantee durability without killing throughput?" — Set `replication.factor=3` and `min.insync.replicas=2` with producer `acks=all`, so a write survives one broker loss while still tolerating one down replica. Avoid `acks=all` + `min.insync.replicas=replication.factor` (a single replica blip stalls writes). Use idempotent producers to prevent duplicate retries, size partitions for parallelism without overloading the JVM (100s/broker fine, 1000s strains heap), and monitor under-replicated partitions and ISR shrink as your early-warning signals.

## Next Topic

→ [T02 — Topics, Partitions, Replicas](T02-Topics-Partitions.md)
