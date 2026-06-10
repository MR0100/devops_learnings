# L22/C02/T06 — Schema Registry

## Learning Objectives

- Use schema registry
- Manage evolution

## Schema Registry

Confluent component:
- Versioned schemas
- Validates messages
- Enforces evolution

For: typed data; compatibility.

## Why

Without:
- Producer sends; consumer breaks
- Schema drift
- Debug pain

With:
- Producer registers schema
- Consumer gets compatible
- Validated

## Formats

- Avro (most common)
- JSON Schema
- Protobuf

## Setup

```bash
# Confluent Schema Registry
docker run -p 8081:8081 confluentinc/cp-schema-registry
```

## Register Schema

```bash
curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "..."}' \
  http://localhost:8081/subjects/events-value/versions
```

## Producer

```python
from confluent_kafka.avro import AvroProducer

producer = AvroProducer({
    'bootstrap.servers': 'broker:9092',
    'schema.registry.url': 'http://schema-registry:8081'
})

schema = avro.loads('...schema JSON...')

producer.produce(topic='events', value={'user_id': 1}, value_schema=schema)
```

## Consumer

```python
from confluent_kafka.avro import AvroConsumer

consumer = AvroConsumer({
    'bootstrap.servers': 'broker:9092',
    'group.id': 'my-group',
    'schema.registry.url': 'http://schema-registry:8081',
})
```

Auto-deserialize.

## Compatibility

- BACKWARD: new readers can read old data
- FORWARD: old readers can read new data
- FULL: both
- NONE: no check

Per subject.

## BACKWARD (Default)

Allowed:
- Add optional field
- Delete field with default

For: rolling deploy where consumers updated first.

## FORWARD

Allowed:
- Add required field
- Delete optional field

For: where producers updated first.

## Evolution Rules

### Add Field
```json
{"name": "email", "type": "string", "default": ""}
```

Backward compatible.

### Remove Field
Old field has default. OK.

### Rename
Use aliases:
```json
{"name": "email_address", "type": "string", "aliases": ["email"]}
```

### Change Type
- int → long: OK (BACKWARD)
- string → int: not compatible

## Subjects

Naming:
- TopicNameStrategy: topic + "-value"
- RecordNameStrategy: fully qualified record name
- TopicRecordNameStrategy: topic + record name

For: multi-schema per topic.

## Apicurio

Alternative to Confluent Schema Registry:
- Open source
- Multi-format
- Red Hat

## Best Practices

- Use schema registry from day 1
- BACKWARD compatibility
- Subject naming consistent
- Schema in version control too
- Tests for compatibility

## Common Mistakes

- No registry (chaos)
- NONE compatibility (breakage)
- Schema in code (not centralized)
- No tests for evolution

## Quick Refs

```bash
# Subjects
GET /subjects
GET /subjects/X/versions

# Schema
POST /subjects/X/versions
GET /subjects/X/versions/N

# Compat
GET /config/X
PUT /config/X { "compatibility": "BACKWARD" }
```

## Interview Prep

**Mid**: "Schema registry."

**Senior**: "Evolution."

**Staff**: "Schema strategy."

## Next Topic

→ [T07 — Operating Kafka in Production](T07-Operating-Kafka.md)
