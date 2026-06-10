# L24/C04/T02 — Consul, Eureka

## Learning Objectives

- Use Consul / Eureka
- Operational considerations

## Consul

HashiCorp; service registry + KV + DNS + health checks:

```bash
consul agent -server -bootstrap-expect=3 ...
```

3+ servers (Raft).

## Register Service

```hcl
service {
  name = "web"
  port = 8080
  check {
    http = "http://localhost:8080/health"
    interval = "10s"
  }
}
```

## Discover

DNS:
```
dig web.service.consul
```

HTTP:
```
curl http://localhost:8500/v1/catalog/service/web
```

## KV

```bash
consul kv put db/host primary
consul kv get db/host
```

For: config.

## ACLs

```bash
consul acl token create -policy-name read-only
```

For: secure.

## Consul Connect

(See L14/C04.)

Service mesh.

## Multi-DC

Federation:
```bash
consul join -wan other-dc-server
```

## Eureka

Netflix; less popular now:
- AWS-friendly
- Spring Cloud integration

```python
eureka_client.init(
    eureka_server="http://eureka:8761/eureka",
    app_name='my-app',
    instance_port=8080,
)
```

## Heartbeat

Service:
- Registers
- Heartbeats every 30s
- After 90s missed: deregistered

## AP System

Eureka: Availability over Consistency.

For: AWS where partitions common.

## Compared

| | Consul | Eureka | K8s native |
|---|---|---|---|
| Origin | HashiCorp | Netflix | K8s |
| KV | yes | no | etcd via API |
| DNS | yes | no | yes |
| Health checks | yes | yes | yes |
| Multi-DC | yes | yes | partial |
| Multi-cloud | yes | yes | per-cluster |

## When Consul

- Multi-platform (VMs + K8s)
- HashiCorp stack
- Need KV + DNS

## When Eureka

- Spring ecosystem
- Existing investment

## When K8s Native

- K8s only
- Don't want extra deps

## Operations

### Consul
- 3-5 servers (HA)
- Backup snapshots
- Audit logs
- ACL strict

### Eureka
- 3+ instances
- Self-preservation mode (don't deregister all)

## Best Practices

- 3-5 servers
- Health checks
- ACLs
- Backup
- Multi-AZ

## Common Mistakes

- 1 instance (SPOF)
- No ACL (open access)
- No backup
- Self-preservation off (mass deregister)

## Quick Refs

```bash
consul agent / members / catalog services
consul kv put / get
consul intention create
```

## Interview Prep

**Mid**: "Service discovery tools."

**Senior**: "Consul features."

**Staff**: "Discovery architecture."

## Next Topic

→ Move to [L24/C05 — BGP, Anycast, ECMP](../C05/README.md)
