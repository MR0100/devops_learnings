# L18/C04/T02 — Fluent Bit (Lightweight)

## Learning Objectives

- Deploy Fluent Bit
- Compare to alternatives

## Fluent Bit

CNCF; C-based log forwarder:
- 10× lighter than Fluentd
- Fast (no GC)
- K8s-friendly
- Many outputs

## Install

```bash
helm install fluent-bit fluent/fluent-bit
```

K8s DaemonSet typical.

## Config

```ini
[SERVICE]
    flush     5
    daemon    off
    log_level info

[INPUT]
    name              tail
    path              /var/log/containers/*.log
    parser            cri
    tag               kube.*
    refresh_interval  5

[FILTER]
    name                kubernetes
    match               kube.*
    kube_url            https://kubernetes.default.svc:443
    merge_log           on

[FILTER]
    name        modify
    match       kube.*
    add         cluster_name production

[OUTPUT]
    name              loki
    match             kube.*
    host              loki
    port              3100
    labels            job=fluentbit, $kubernetes['namespace_name'], $kubernetes['labels']['app']
```

## Plugins

- inputs: tail, systemd, http, tcp, kafka
- filters: kubernetes, modify, grep, parser
- outputs: ES, Loki, S3, Kafka, splunk, datadog, OTel

## Resources

- ~10-50 MB RAM
- < 1% CPU

For: edge collection at scale.

## Compared

| | Fluent Bit | Fluentd |
|---|---|---|
| Language | C | Ruby |
| Memory | 10-50 MB | 100-500 MB |
| Plugins | fewer | many |
| Speed | fast | slower |
| Maintenance | easier | more complex |

## K8s DaemonSet

```yaml
apiVersion: apps/v1
kind: DaemonSet
spec:
  template:
    spec:
      containers:
        - name: fluent-bit
          image: fluent/fluent-bit
          volumeMounts:
            - name: varlog
              mountPath: /var/log
            - name: config
              mountPath: /fluent-bit/etc
```

Reads /var/log/containers.

## Multiline

```ini
[FILTER]
    name             multiline
    match            *
    multiline.parser python
```

Detect multi-line; combine.

## Backpressure

```ini
[SERVICE]
    storage.backlog.mem_limit 5M
    storage.path /var/log/flb-storage
```

File-backed buffer.

## OTel

```ini
[OUTPUT]
    name                opentelemetry
    match               *
    host                otel-collector
    port                4318
```

For: OTel pipeline.

## Routing

Multiple outputs:
```ini
[OUTPUT]
    name                loki
    match               kube.namespace.app
    ...

[OUTPUT]
    name                es
    match               kube.namespace.app
    ...
```

Send to both.

## When Fluent Bit

- K8s
- Resource-constrained
- Edge collection
- Cloud-native

## When Fluentd

- Complex transforms
- Rich plugin needs
- Existing Ruby ecosystem

## Best Practices

- DaemonSet per K8s node
- Kubernetes filter (auto metadata)
- Buffer to disk
- Limits set (mem)
- Test config (`fluent-bit -t`)

## Common Mistakes

- Memory buffer only (loss)
- No multiline (broken stacks)
- Overlapping inputs (dup logs)
- Missing parser

## Quick Refs

```ini
[SERVICE], [INPUT], [FILTER], [OUTPUT]
```

```bash
fluent-bit -c fluent-bit.conf
fluent-bit -t   # test
```

## Interview Prep

**Mid**: "Fluent Bit vs Fluentd."

**Senior**: "K8s log collection."

## Next Topic

→ [T03 — Vector (Rust-Based)](T03-Vector.md)
