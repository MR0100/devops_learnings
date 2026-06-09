# L22/C02 — Kafka Deep Dive

## Topics

- **T01 Architecture** — Brokers, ZooKeeper / KRaft
- **T02 Topics, Partitions, Replicas** — Core model
- **T03 Producers & Idempotence** — Reliability
- **T04 Consumers & Consumer Groups** — Parallelism
- **T05 Kafka Connect & Mirror Maker** — Integration
- **T06 Schema Registry** — Type safety
- **T07 Operating Kafka in Production** — Day-2

## Architecture

```
[Producers] → push messages → [Kafka Brokers (cluster)] ← pull → [Consumers]
                                       │
                                       ↓
                          [ZooKeeper or KRaft for cluster metadata]
```

### Broker
- Stores topic partitions on disk
- Replicates with other brokers
- Serves reads/writes

### ZooKeeper (legacy)
- Cluster coordination
- Controller election
- Topic/partition metadata

### KRaft (Kafka Raft, modern)
- Replaces ZooKeeper (deprecated as of Kafka 3.5, removed 4.0)
- Built-in Raft consensus
- Simpler ops

## Topics, Partitions, Replicas

### Topic
- Named log of messages
- Partitioned for parallelism

### Partition
- Ordered, append-only log
- Parallelism unit (more partitions = more consumers can read in parallel)
- 100s ok per broker; 1000s strains
- Once set, increasing partitions breaks key→partition mapping

### Replica
- Each partition replicated across brokers
- One leader; rest are followers
- Producers write to leader; followers replicate
- Consumers read from leader (or followers in newer Kafka)

### ISR (In-Sync Replicas)
- Replicas caught up to leader
- Min ISR = quorum for writes
- Reduce min ISR for availability; increase for durability

### Replication Factor
- 3 is standard (tolerate 1 broker loss)
- 5 for extra safety (tolerate 2 broker loss)

## Producers

```java
Properties props = new Properties();
props.put("bootstrap.servers", "broker1:9092,broker2:9092");
props.put("acks", "all");                    // wait for all ISR
props.put("enable.idempotence", "true");     // no duplicates from retries
props.put("max.in.flight.requests.per.connection", "5");
props.put("retries", Integer.MAX_VALUE);     // retry forever
props.put("delivery.timeout.ms", 120000);
props.put("compression.type", "lz4");        // or zstd
props.put("linger.ms", "20");                // batch up
props.put("batch.size", 65536);

Producer<String, String> producer = new KafkaProducer<>(props);
producer.send(new ProducerRecord<>("orders", key, value));
```

### Key
- Determines partition: `hash(key) % numPartitions`
- Same key → same partition → ordered for that key
- Null key → round-robin (no ordering)

### Acks
- `0`: don't wait for ack (fast, lossy)
- `1`: leader ack (default; lose if leader fails)
- `all` / `-1`: ISR ack (most durable)

### Idempotent Producer
- Each producer has a unique ID + sequence per partition
- Broker dedupes
- No duplicates from retries
- Almost always enable

### Transactions
- Multi-partition atomic writes
- Producer sends + commits all-or-nothing
- Used for exactly-once semantics

## Consumers

### Consumer Group
- A group of consumers cooperating
- Each partition assigned to ONE consumer in the group
- More consumers than partitions = idle ones
- Different groups: each gets all messages (fanout)

```java
Properties props = new Properties();
props.put("bootstrap.servers", "...");
props.put("group.id", "my-consumer-group");
props.put("enable.auto.commit", "false");      // manual commit (preferred)
props.put("auto.offset.reset", "earliest");
props.put("isolation.level", "read_committed"); // skip aborted tx

Consumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));

while (true) {
  ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
  for (ConsumerRecord<String, String> record : records) {
    process(record);
  }
  consumer.commitSync();
}
```

### Offsets
- Each consumer group tracks position per partition
- Stored in internal Kafka topic `__consumer_offsets`
- Commit after processing (at-least-once)
- Auto-commit possible but risky (can ack before process)

### Rebalancing
- When group membership changes (consumer joins/leaves)
- Old: stop-the-world rebalance (all consumers pause)
- New: cooperative incremental rebalance (only affected partitions move)

### Consumer Lag
The gap between latest message and consumer's position.
- Important metric (monitor!)
- High lag = falling behind

## Kafka Connect

Standalone or distributed framework for moving data in/out of Kafka.

### Source Connectors
- Read from DB/file/system → write to Kafka
- Debezium (DB CDC)
- JDBC source

### Sink Connectors
- Read from Kafka → write to DB/S3/etc.
- S3 sink
- Elasticsearch sink
- JDBC sink

```json
{
  "name": "postgres-source",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.user": "...",
    "database.dbname": "mydb",
    "topic.prefix": "myapp"
  }
}
```

## MirrorMaker 2

Replicate topics from one Kafka cluster to another.
- DR
- Multi-region
- Migration between clusters

## Schema Registry

Typed messages via Avro / Protobuf / JSON Schema.

### Why
- Without: every consumer parses raw bytes; schema drift breaks
- With: producer validates against registered schema; consumer verifies

```python
from confluent_kafka.avro import AvroProducer

schema = avro.loads(open("order.avsc").read())
producer = AvroProducer(config, default_value_schema=schema)
producer.produce(topic='orders', value=order_dict)
```

### Compatibility Modes
- BACKWARD: new schema can read data written by old
- FORWARD: old schema can read data written by new
- FULL: both ways

Use BACKWARD for evolving message formats safely.

## Operating Kafka in Production

### Sizing
- Disk: 7-14 days retention × throughput × RF
- Memory: ~1 GB for OS cache per active partition
- Network: ~10 Gbps NICs for high throughput

### Replication Factor 3 + min.insync.replicas 2 + acks=all
Standard durable setup. Tolerate 1 broker loss; ensure 2 ISR ack before producer success.

### Partition Count Strategy
- Plan for parallelism (consumers)
- Plan for distribution (more partitions = better balance across brokers)
- Don't over-partition (each is overhead)
- Common: 10-100 partitions per topic

### Monitoring
- Under-replicated partitions
- ISR shrink rate
- Request latency (p99)
- Disk usage
- Consumer lag per group/topic/partition

### Operational Tools
- **Cruise Control** — auto-balance partition placement
- **Burrow** — consumer lag monitoring
- **AKHQ / Kafka UI** — web UIs
- **kcat (kafkacat)** — CLI

### Common Issues
- Under-replicated partitions during broker restart
- Disk full (insufficient retention tuning)
- Consumer lag building (consumer too slow)
- Hot partition (bad keys)
- Rebalance storms (frequent consumer group changes)

## Cloud Kafka

- **AWS MSK** — managed Kafka
- **Confluent Cloud** — premium, more features
- **Aiven Kafka** — multi-cloud managed
- **Redpanda Cloud** — Kafka-compatible, written in C++ (no JVM)

## Interview Themes

- "Kafka architecture"
- "Partition design — for a use case"
- "Producer idempotence"
- "Consumer group rebalancing"
- "Schema Registry — why?"
- "How to scale Kafka cluster"
- "Compare Kafka and Kinesis"
