# L18/C02/T02 — Logstash & Beats

## Learning Objectives

- Pipeline logs into ES
- Choose right tool

## Logstash

Heavy-weight log processor:
- Input → Filter → Output
- Many plugins
- JVM-based (memory hungry)

## Config

```ruby
input {
  beats {
    port => 5044
  }
  kafka {
    bootstrap_servers => "kafka:9092"
    topics => ["logs"]
  }
}

filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:ts} %{LOGLEVEL:level} %{GREEDYDATA:msg}" }
  }
  date {
    match => [ "ts", "ISO8601" ]
  }
  json {
    source => "msg"
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
}
```

## Grok

Pattern matching:
```
%{IP:client} %{WORD:method} %{URIPATH:request}
```

For: unstructured → fields.

## Filters

- grok (parse)
- mutate (rename, add, remove)
- date (parse timestamp)
- geoip
- json
- kv

## Outputs

- Elasticsearch
- Kafka
- S3
- stdout
- many

## Beats

Lightweight shippers (Go):
- Filebeat (logs)
- Metricbeat (metrics)
- Packetbeat (network)
- Auditbeat (audit)
- Heartbeat (uptime)
- Winlogbeat (Windows)

## Filebeat

```yaml
filebeat.inputs:
  - type: container
    paths:
      - /var/log/containers/*.log
    processors:
      - add_kubernetes_metadata: ~

output.elasticsearch:
  hosts: ["elasticsearch:9200"]

# Or via Logstash
# output.logstash:
#   hosts: ["logstash:5044"]
```

## Filebeat vs Fluent Bit

| | Filebeat | Fluent Bit |
|---|---|---|
| Lang | Go | C |
| Memory | medium | low |
| Plugins | Elastic-focused | multi-cloud |
| Beats family | yes | no |
| OTel | partial | yes |

For: ELK stack: Filebeat.
For: multi-output: Fluent Bit.

## Logstash vs Beats

| | Logstash | Beats |
|---|---|---|
| Resource | heavy | light |
| Place | central | edge |
| Processing | rich | basic |

Typical:
- Beats: edge (sidecars / DaemonSets)
- Logstash: central (heavy processing)

## Architecture Pattern

```
App → Filebeat → Logstash → ES
                       ↓
                       Kafka (buffer)
                       ↓
                       Logstash → ES
```

For: durability buffer.

## Modules

Pre-built:
- nginx
- apache
- system
- k8s

```bash
filebeat modules enable nginx
filebeat setup
```

For: common log formats.

## Kibana Integration

Beats ship to ES; Kibana dashboards prebuilt.

## Container Logs

Filebeat in K8s:
```yaml
filebeat.autodiscover:
  providers:
    - type: kubernetes
      hints.enabled: true
```

Reads container logs; adds K8s metadata.

## Resources

Filebeat:
- 50-100 MB RAM
- ~1% CPU

Logstash:
- 512 MB - 2 GB RAM
- 1 vCPU+

For: scale Logstash horizontally.

## Best Practices

- Beats at edge
- Logstash central (or skip if Filebeat can ship direct)
- Kafka for durability
- Multiline (stack traces)
- Backpressure tested

## Common Mistakes

- Logstash on every host (heavy)
- No buffer (loss on outage)
- Grok complex (slow)
- No tests for grok patterns

## Multiline

```yaml
multiline.pattern: '^\['
multiline.negate: true
multiline.match: after
```

Combine stack trace lines.

## Filtering Beats

```yaml
processors:
  - drop_event:
      when:
        equals:
          message: "DEBUG"
  - drop_fields:
      fields: [agent.ephemeral_id]
```

Reduce ingest.

## Alternatives

- Fluent Bit / Fluentd
- Vector (Rust)
- Promtail (Loki-specific)
- OTel Collector

## Logstash Pipelines

Multiple in one process:
```yaml
- pipeline.id: main
  path.config: "/etc/logstash/conf.d/*.conf"
- pipeline.id: events
  path.config: "/etc/logstash/events.conf"
```

For: separate workflows.

## Persistent Queue

```ini
queue.type: persisted
queue.max_bytes: 4gb
```

Disk-backed; survives restart.

## Quick Refs

```ruby
input { beats { port => 5044 } }
filter { grok { ... } }
output { elasticsearch { ... } }
```

```bash
# Filebeat
filebeat modules enable nginx
filebeat -e -c filebeat.yml

# Logstash
bin/logstash -f config.conf
```

## Interview Prep

**Mid**: "Logstash vs Beats."

**Senior**: "ELK pipeline design."

**Staff**: "Log shipping at scale."

## Next Topic

→ [T03 — Kibana](T03-Kibana.md)
