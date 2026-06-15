# L22/C02/T05 — Kafka Connect & Mirror Maker

## Learning Objectives

- Use Kafka Connect
- Replicate via Mirror Maker

## Kafka Connect

Framework for connectors:
- Source: external → Kafka
- Sink: Kafka → external

## Run

```bash
# Distributed mode
connect-distributed.sh config/connect-distributed.properties
```

## Connectors

- Debezium (CDC; covered L21/C08/T03)
- JDBC source/sink
- S3 sink
- Elasticsearch sink
- BigQuery sink
- 100+ community

## Install

```bash
confluent-hub install confluentinc/kafka-connect-s3:latest
```

## Config

```json
POST /connectors
{
  "name": "s3-sink",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "topics": "events",
    "s3.bucket.name": "my-bucket",
    "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
    "flush.size": "1000"
  }
}
```

## Mirror Maker 2

Replicate between Kafka clusters:
```properties
clusters = primary, replica
primary.bootstrap.servers = primary:9092
replica.bootstrap.servers = replica:9092

primary->replica.enabled = true
primary->replica.topics = .*
```

For: DR, multi-region.

## Use Cases

### Multi-Region
Primary US → replica EU.

### Disaster Recovery
Primary down → consumers go to replica.

### Data Lake
Topics → S3 (sink).

### CDC
Postgres → Kafka (source).

## Distributed Mode

Multiple Connect workers:
- HA
- Scale
- Auto-rebalance tasks

## Schema

For typed data:
- Avro (Schema Registry)
- JSON Schema
- Protobuf

## Best Practices

- Distributed mode prod
- Monitor lag
- Tune flush size for batches
- Schema registry
- Idempotent sinks

## Common Mistakes

- Standalone in prod (SPOF)
- No monitoring
- Wrong batch size
- Schema drift

## Quick Refs

```bash
# Status
curl http://connect:8083/connectors

# Restart
curl -X POST http://connect:8083/connectors/X/restart

# Mirror Maker 2
connect-mirror-maker.sh mirror-maker.properties
```

## Interview Prep

**Mid**: "Kafka Connect."

**Senior**: "Multi-region replication."

**Staff**: "Connect at scale."

## Next Topic

→ [T06 — Schema Registry](T06-Schema-Registry.md)
