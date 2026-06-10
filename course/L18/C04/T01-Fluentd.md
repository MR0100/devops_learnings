# L18/C04/T01 — Fluentd

## Learning Objectives

- Use Fluentd
- Pipeline logs

## Fluentd

CNCF; Ruby-based log collector:
- Plugin-rich (700+)
- Tag-based routing
- Pluggable inputs/outputs

## Install

```bash
helm install fluentd fluent/fluentd
```

Or:
```bash
gem install fluentd
fluentd -c fluent.conf
```

## Config

```
<source>
  @type tail
  path /var/log/app/*.log
  pos_file /var/log/fluentd.pos
  tag app.*
  <parse>
    @type json
  </parse>
</source>

<filter app.**>
  @type record_transformer
  <record>
    hostname "#{Socket.gethostname}"
  </record>
</filter>

<match app.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name app-%Y%m%d
  <buffer>
    @type file
    path /var/log/fluentd-buffers
    flush_interval 5s
    retry_forever
  </buffer>
</match>
```

## Tags

Hierarchical routing:
```
app.access
app.error
system.kernel
```

`<match app.**>`: matches app and children.

## Sources

- tail (file)
- forward (network)
- http
- syslog
- tcp/udp

## Filters

- grep
- record_transformer
- parser
- record_modifier
- geoip

## Outputs

- Elasticsearch
- Loki
- S3
- Kafka
- file
- stdout
- many more

## Buffer

```
<buffer>
  @type file
  path /var/log/fluentd-buffers
  chunk_limit_size 10MB
  total_limit_size 1GB
  flush_interval 5s
  retry_max_interval 60
  retry_forever true
</buffer>
```

For durability. Disk-backed.

## Multiline

```
<parse>
  @type multiline
  format_firstline /^\d{4}-\d{2}-\d{2}/
  format1 /^(?<time>\d{4}-\d{2}-\d{2}.*)$/
</parse>
```

Stack traces.

## K8s

```yaml
<source>
  @type tail
  path /var/log/containers/*.log
  pos_file /var/log/fluentd-containers.pos
  tag kubernetes.*
  <parse>
    @type json
  </parse>
</source>

<filter kubernetes.**>
  @type kubernetes_metadata
</filter>
```

Adds K8s pod metadata.

## Resources

Per node:
- 100-500 MB RAM
- ~1% CPU

For: medium-heavy.

## Performance

Ruby base: slower than Go/Rust alternatives.

For high-throughput: Fluent Bit.

## High Availability

```
App → Fluent Bit (edge) → Aggregator Fluentd → Output
```

Aggregator: heavy work; edge light.

## Plugins

```bash
fluent-gem install fluent-plugin-elasticsearch
fluent-gem install fluent-plugin-kafka
```

## OTel Compatibility

```
<source>
  @type opentelemetry
</source>
```

Receives OTLP.

## When Fluentd

- Existing Ruby shop
- Rich plugin needs
- Tag-based routing

## When Fluent Bit

- Resource constrained
- Edge collection
- Lighter footprint

## Best Practices

- Buffer to file (durability)
- Tag hierarchy
- Filter early
- Multiline patterns tested
- Monitor buffer usage

## Common Mistakes

- Memory buffer (loss on crash)
- No retry limit (stuck)
- Heavy filters (slow)
- Tag conflict

## Quick Refs

```
<source>: input
<filter>: transform
<match>: route to output
<buffer>: durability
```

```bash
fluentd -c config.conf
fluent-gem install plugin
```

## Interview Prep

**Mid**: "Fluentd basics."

**Senior**: "Pipeline design."

## Next Topic

→ [T02 — Fluent Bit (Lightweight)](T02-Fluent-Bit.md)
