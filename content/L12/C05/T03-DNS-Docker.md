# L12/C05/T03 — DNS Inside Docker

## Learning Objectives

- Use Docker DNS
- Troubleshoot resolution

## Docker DNS

Custom bridge networks: built-in DNS server at 127.0.0.11.

```bash
docker network create app
docker run -d --network app --name web nginx
docker run --network app alpine ping web   # works
```

## Default Bridge

`docker0` bridge: no DNS for container names.

```bash
docker run -d --name web nginx
docker run alpine ping web   # fails (default bridge)
```

For DNS: use custom bridge.

## /etc/resolv.conf

```bash
docker run --rm alpine cat /etc/resolv.conf
# nameserver 127.0.0.11
# options ndots:0
```

127.0.0.11: Docker's embedded DNS.

## External DNS

Forwarded:
- Docker DNS → host DNS → upstream
- Or container DNS forwards explicitly

```bash
docker run --dns 8.8.8.8 alpine
```

Override DNS.

## Custom DNS

```bash
docker run \
  --dns 8.8.8.8 \
  --dns 1.1.1.1 \
  --dns-search example.com \
  alpine
```

Multiple; with search domain.

## docker-compose

```yaml
services:
  web:
    image: nginx
  app:
    image: myapp
    environment:
      REDIS_HOST: redis   # resolves to redis service
  redis:
    image: redis
```

Compose creates network; service name resolves.

## Hostname Aliases

```bash
docker run --network mynet --network-alias api app
```

Container reachable as `api`.

For: multiple names per container.

## Add Host

```bash
docker run --add-host db:192.168.1.10 alpine
```

Adds to /etc/hosts.

For: external services with fixed IP.

## Inspect

```bash
docker exec mycontainer cat /etc/resolv.conf
docker exec mycontainer cat /etc/hosts
docker exec mycontainer nslookup web
```

## Service Discovery

In custom bridge:
- Container name → IP
- Service name (Compose) → IP
- Alias → IP

DNS round-robin for multiple matching.

## DNS for Scaled Services

```yaml
services:
  worker:
    image: worker
    deploy:
      replicas: 3
```

`worker` resolves to multiple IPs (round-robin).

## Troubleshooting

### Can't Resolve
```bash
docker exec mycontainer nslookup target
# Server: 127.0.0.11
# Address: 127.0.0.11#53

# OK: returns IP
# Fail: no answer
```

Causes:
- Wrong network (different bridge)
- Service not running
- Typo

### External DNS Fails
```bash
docker exec mycontainer nslookup google.com
# Should resolve

# If fails:
# - Check host DNS
# - Check firewall (port 53)
# - Try --dns explicitly
```

## ndots Setting

```
options ndots:0
```

Affects resolution:
- ndots:0: try as-is first
- ndots:5: try with search domains first

Higher: more searches; slower if external.

For K8s: ndots:5 default; can be issue.

## Search Domains

```bash
docker run --dns-search example.com alpine
# nslookup web → web.example.com
```

For: company internal names.

## DNS Caching

Container resolver may cache.
- TTL respected
- For dynamic: low TTL

## Custom Networks vs Default

Always use custom:
```bash
docker network create app
docker run --network app ...
```

For DNS, isolation, modern features.

## Compose Network Naming

Default: `<project>_default`.

Services resolve by name in this network.

Override:
```yaml
networks:
  custom:
    name: my-custom-net
```

## K8s DNS

CoreDNS in cluster:
- Resolves service names
- `service.namespace.svc.cluster.local`

Different from Docker DNS.

Covered in L13/C04.

## Embedded DNS Limitations

Docker embedded DNS:
- Only on custom bridges
- Not configurable via daemon
- Limited to internal

For sophisticated: external (CoreDNS for K8s).

## Best Practices

- Custom bridge always
- Service names via Compose
- Aliases for multiple names
- External DNS via --dns
- Test resolution in CI

## Common Mistakes

- Default bridge for service discovery
- Hardcoded IPs (use names)
- DNS issues on Mac/Win (Docker Desktop quirks)
- Forgetting /etc/hosts vs DNS

## Override /etc/hosts

```bash
docker run --add-host=example.com:192.168.1.10 alpine
```

For: testing specific IPs.

## K8s Migration

When moving from Docker Compose to K8s:
- Service names mostly compatible
- Use K8s Services (similar concept)
- DNS resolution: `service.namespace.svc.cluster.local`

## Real-World

Microservices stack:
```yaml
services:
  api:
    image: myapi
    environment:
      REDIS: redis
      DB: postgres
      QUEUE: rabbit
  redis:
    image: redis
  postgres:
    image: postgres
  rabbit:
    image: rabbitmq
```

API uses DNS to find dependencies.

## Quick Refs

```bash
# Inspect DNS
docker exec CONTAINER cat /etc/resolv.conf
docker exec CONTAINER nslookup NAME

# Run with custom DNS
docker run --dns SERVER --dns-search DOMAIN ...

# Add host entry
docker run --add-host NAME:IP ...

# Network alias
docker run --network NET --network-alias NAME ...
```

## Interview Prep

**Junior**: "Service discovery in Docker."

**Mid**: "Default bridge vs custom."

**Senior**: "DNS troubleshooting."

## Next Topic

→ Move to [L12/C06 — Storage in Containers](../C06/README.md)
