# L13/C15/T02 — Fluent Bit / Fluentd / Vector DaemonSets

## Learning Objectives

- Pick log agent
- Configure for production

## Agents

| | Language | Resource | Speed | Plugins |
|---|---|---|---|---|
| Fluent Bit | C | Very low (50 MB) | Fast | Many |
| Fluentd | Ruby | High (256 MB+) | Slower | Most |
| Vector | Rust | Low (100 MB) | Fastest | Growing |
| Filebeat | Go | Medium | Medium | ELK ecosystem |

For K8s: Fluent Bit or Vector recommended. Fluentd legacy.

## Fluent Bit

Lightweight; native K8s integration:
```yaml
[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            cri
    Tag               kube.*
    Refresh_Interval  5
    Mem_Buf_Limit     50MB
    Skip_Long_Lines   On

[FILTER]
    Name                kubernetes
    Match               kube.*
    Kube_URL            https://kubernetes.default.svc:443
    Kube_CA_File        /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    Kube_Token_File     /var/run/secrets/kubernetes.io/serviceaccount/token
    Merge_Log           On
    K8S-Logging.Parser  On
    K8S-Logging.Exclude Off

[OUTPUT]
    Name        loki
    Match       *
    host        loki.monitoring.svc.cluster.local
    port        3100
    labels      job=fluentbit, $kubernetes['namespace_name']
```

## Pipelines

```
INPUT → FILTER → OUTPUT
```

- INPUT: tail file, listen, etc.
- FILTER: modify, enrich, drop
- OUTPUT: send to backend

## K8s Filter

Adds metadata from K8s API:
- namespace
- pod
- container
- labels
- annotations

```ini
[FILTER]
    Name                kubernetes
    Kube_URL            https://kubernetes.default.svc:443
```

For: searchable by team, env, etc.

## Multiline Parser

For stack traces:
```ini
[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            cri
    Multiline.parser  java,go

[MULTILINE_PARSER]
    name          java
    type          regex
    flush_timeout 1000
    rule          "start_state"    "/(Exception|Error)/"  "cont"
    rule          "cont"           "/^\s+at/"             "cont"
```

Joins consecutive lines.

## Filters

### Modify
```ini
[FILTER]
    Name modify
    Match kube.*
    Add cluster prod
    Rename log message
```

### Grep (Drop)
```ini
[FILTER]
    Name grep
    Match kube.*
    Exclude kubernetes['namespace_name'] kube-system
```

Drop logs from kube-system.

### Parser
```ini
[FILTER]
    Name parser
    Match kube.var.log.containers.my-app*
    Key_Name log
    Parser my-json
```

Apply parser to specific match.

## Outputs

### Loki
```ini
[OUTPUT]
    Name        loki
    Match       *
    host        loki
    port        3100
    labels      job=fluentbit, namespace=$kubernetes['namespace_name']
```

### Elasticsearch
```ini
[OUTPUT]
    Name      es
    Match     *
    Host      elasticsearch.elastic.svc
    Port      9200
    Index     kube-logs
    Type      _doc
    Suppress_Type_Name On
```

### S3
```ini
[OUTPUT]
    Name     s3
    Match    *
    bucket   my-logs
    region   us-east-1
    total_file_size 10M
    upload_timeout 10m
```

### Multiple Outputs
```ini
[OUTPUT]
    Name loki
    Match *
    ...

[OUTPUT]
    Name s3
    Match *
    ...
```

Same logs to both.

## Vector

Modern, fast (Rust):
```yaml
sources:
  kubernetes_logs:
    type: kubernetes_logs

transforms:
  parse_json:
    type: remap
    inputs: [kubernetes_logs]
    source: |
      .parsed = parse_json!(.message)

sinks:
  loki:
    type: loki
    inputs: [parse_json]
    endpoint: http://loki:3100
    labels:
      namespace: '{{ kubernetes.pod_namespace }}'
```

VRL (Vector Remap Language) for transformations.

## Resource Usage

Fluent Bit DaemonSet:
- 100m CPU, 200Mi memory per node
- For 1000-node cluster: 100 CPU, 200 GB memory

Vector similar.

Fluentd: 4-10× more memory typically.

## High-Volume

For huge volume (TB/day):
- Aggregation layer (Fluentd / Fluent Bit) before final
- Buffer + retry
- Compression
- Sampling

## Buffer Disk

For unreliable backend:
```ini
[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    storage.type      filesystem
    Tag               kube.*

[SERVICE]
    storage.path      /var/log/flb-storage/
```

Logs buffered to disk if backend down; replayed.

## DaemonSet Configuration

```yaml
spec:
  template:
    spec:
      hostNetwork: true
      tolerations:
      - operator: Exists
      containers:
      - name: fluent-bit
        resources:
          requests: {cpu: 100m, memory: 200Mi}
          limits: {cpu: 500m, memory: 1Gi}
        volumeMounts:
        - name: varlog
          mountPath: /var/log
          readOnly: true
        - name: dockerlibs
          mountPath: /var/lib/docker/containers
          readOnly: true
        - name: config
          mountPath: /fluent-bit/etc
```

## Performance Tuning

- Mem_Buf_Limit: per input buffer (50MB default)
- Refresh_Interval: how often tail check new files
- Skip_Long_Lines: drop > N bytes
- Output: tune batch / concurrency

## CRI Parser

```ini
[PARSER]
    Name        cri
    Format      regex
    Regex       ^(?<time>[^ ]+) (?<stream>stdout|stderr) (?<logtag>[^ ]*) (?<message>.*)$
    Time_Key    time
    Time_Format %Y-%m-%dT%H:%M:%S.%L%z
```

Pre-built for K8s logs.

## Tag Routing

```ini
[INPUT]
    Tag kube.*

[OUTPUT]
    Name loki
    Match kube.var.log.containers.app-*

[OUTPUT]
    Name s3
    Match kube.var.log.containers.audit-*
```

Different outputs per match.

## ConfigMap Mount

```yaml
volumes:
- name: config
  configMap:
    name: fluent-bit-config
volumeMounts:
- name: config
  mountPath: /fluent-bit/etc
```

ConfigMap with fluent-bit.conf + parsers.conf.

## Reload on Config Change

Some agents support hot reload. Or restart DaemonSet:
```bash
kubectl rollout restart daemonset/fluent-bit
```

## Monitoring Agent

Self-metrics:
```
fluentbit_input_records_total
fluentbit_output_records_total
fluentbit_output_errors_total
```

Scrape with Prometheus.

Alert on:
- Output errors
- Buffer overflow
- High latency

## Choosing Agent

Fluent Bit:
- Standard for K8s
- Mature
- Many outputs
- Default

Vector:
- Newer
- Faster
- VRL powerful
- Cloud-native

Fluentd:
- Legacy
- More plugins
- Higher resource

For new: Fluent Bit or Vector.

## Best Practices

- Fluent Bit / Vector as DaemonSet
- K8s metadata enrichment
- Structured JSON logs from apps
- Sampling for high volume
- Disk buffer for reliability
- Monitor agent itself
- Drop noise (health checks, etc.)

## Common Mistakes

- Wrong volume mounts (logs not collected)
- No K8s filter (no metadata)
- All to one backend (DR risk)
- Forgot multiline parser
- No agent monitoring
- No tolerations (misses tainted nodes)

## Quick Refs

```bash
# Install Fluent Bit
helm install fluent-bit fluent/fluent-bit

# Vector
helm install vector vector/vector

# Verify
kubectl get pods -n logging
kubectl logs -n logging fluent-bit-xxx

# Reload (Fluent Bit supports SIGHUP)
kubectl exec fluent-bit-xxx -- killall -HUP fluent-bit
```

## Interview Prep

**Mid**: "Fluent Bit vs Fluentd."

**Senior**: "K8s log enrichment."

**Staff**: "Log agent for 5000-node cluster."

## Next Topic

→ [T03 — Loki & ELK on K8s](T03-Loki-ELK.md)
