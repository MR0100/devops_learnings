# L12/C05/T02 — Port Mapping vs Host Networking

## Learning Objectives

- Map ports correctly
- Pick between approaches

## Port Mapping

```bash
docker run -p 8080:80 nginx
```

Host:8080 → Container:80.

iptables DNAT rule.

## Bind to Specific Interface

```bash
docker run -p 127.0.0.1:8080:80 nginx
# Only localhost
docker run -p 192.168.1.10:8080:80 nginx
# Specific IP
docker run -p 0.0.0.0:8080:80 nginx
# All interfaces (default)
```

## Random Port

```bash
docker run -p 80 nginx
# Random host port → 80
docker port mycontainer
# 80/tcp -> 0.0.0.0:32768
```

For: multiple instances; conflicts.

## Publish All

```bash
docker run -P nginx
# Maps all EXPOSE'd ports to random
```

## Range

```bash
docker run -p 8000-8010:80 nginx
```

Allocate from range.

## UDP

```bash
docker run -p 53:53/udp dns-server
```

Default TCP; specify UDP.

## Both
```bash
docker run -p 80/tcp -p 80/udp myapp
```

## Host Networking

```bash
docker run --network host nginx
```

No port mapping; uses host's interfaces directly.

Pros:
- No NAT overhead
- All host ports available
- Faster

Cons:
- No isolation
- Port conflicts
- One container per port

## Performance

Port mapping: NAT overhead ~5-10%.

Host network: native.

For high-pps (UDP DNS, packet processing): host network.

## When Port Mapping

- Multiple services on host
- Isolation important
- Standard apps
- Cloud (LB → port mapping)

## When Host Network

- High performance
- Many ports needed
- Network appliance (DNS, proxy)
- Direct on host network

## Iptables Rules

```bash
sudo iptables -t nat -L DOCKER -n
# Shows port mapping rules
```

For: troubleshooting.

## Conflicts

```bash
docker run -p 80:80 nginx
docker run -p 80:80 apache   # ERROR: port already allocated
```

Host port: one container.

For: use different host ports or container scaling tools.

## Loopback Access

From container:
```bash
docker run alpine ping host.docker.internal
# Reaches host (Mac/Win)
```

On Linux: use host IP or `--add-host`.

## Container-to-Container

Within same network: by name, no port mapping.

Cross-host: port mapping or overlay.

## Cloud LB

ALB → EC2 NodePort → Container:
- Cloud LB to instance:port
- iptables redirects to container

## K8s NodePort

```yaml
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080
```

Node:30080 → Service:80 → Pod:8080.

Similar concept; K8s manages.

## docker-compose Ports

```yaml
services:
  web:
    ports:
    - "8080:80"
    - "127.0.0.1:8443:443"
```

Same syntax.

## Best Practices

- Specific binding (127.0.0.1 for internal)
- Document mapped ports
- Avoid host network unless needed
- High ports (>1024) for app
- Map at runtime; don't bake in

## Common Mistakes

- Port conflicts
- Binding 0.0.0.0 when localhost OK
- Privileged ports as non-root (need CAP_NET_BIND_SERVICE)
- Forgetting EXPOSE for documentation

## EXPOSE in Dockerfile

```dockerfile
EXPOSE 8080
```

Documentation; doesn't open.

For `-P`: maps EXPOSE'd.

## Mac/Win Specifics

Docker Desktop:
- VM hosts containers
- Port mapping: VM → Mac
- localhost works (forwarded)

For: dev fine.

## Production

K8s usage:
- Service for port mapping
- Ingress for HTTP routing
- LoadBalancer for cloud LB

Standalone Docker uncommon in prod.

## Quick Refs

```bash
# Map
-p HOST:CONTAINER
-p IP:HOST:CONTAINER
-p HOST:CONTAINER/PROTO
-P  # all EXPOSE'd

# Inspect
docker port CONTAINER
docker inspect CONTAINER --format '{{.NetworkSettings.Ports}}'

# Host network
docker run --network host IMAGE
```

## Interview Prep

**Junior**: "Port mapping."

**Mid**: "Host vs bridge."

**Senior**: "Port allocation strategy."

## Next Topic

→ [T03 — DNS Inside Docker](T03-DNS-Docker.md)
