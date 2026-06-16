# L12/C05 — Container Networking

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Networks.md) | Bridge, Host, None, Overlay Networks | 1 hr |
| [T02](T02-Port-Mapping.md) | Port Mapping vs Host Networking | 0.5 hr |
| [T03](T03-DNS-Docker.md) | DNS Inside Docker | 0.5 hr |

## Network Drivers

### bridge (default)
- Default network for containers without `--network` flag
- Containers get IPs from the bridge subnet
- NAT for outbound; port mapping for inbound

```bash
docker network ls
docker network inspect bridge
```

Custom bridges (recommended for multi-container apps):
```bash
docker network create mynet
docker run --network mynet --name api myimage
docker run --network mynet --name web nginx   # can reach api by name
```

Custom bridges add auto-DNS (containers can talk by name).

### host
- Container uses host's network namespace directly
- No isolation; no port mapping needed
- Fastest (no NAT, no veth)
- Mac/Windows: emulated via VM, less useful

```bash
docker run --network host nginx
# nginx binds to host:80 directly
```

### none
- No network at all
- For workloads that explicitly don't need network

### overlay
- Multi-host networking (Docker Swarm, K8s)
- VXLAN encapsulation between hosts
- Containers across hosts can talk by IP/name

### macvlan
- Container gets its own MAC + IP on host LAN
- Looks like a real host on the network
- Use for legacy apps requiring real L2

### ipvlan
- Like macvlan but shares MAC; uses L3
- Newer; more cloud-friendly

## Port Mapping

```bash
docker run -p 8080:80 nginx           # host:container
docker run -p 127.0.0.1:8080:80 nginx # bind to specific IP
docker run -p 8080:80/udp nginx       # UDP
docker run -P nginx                    # publish all exposed (random host ports)
```

How it works:
- Docker installs an iptables NAT rule
- DNAT: incoming `host:8080` → `container_ip:80`
- Source NAT (MASQUERADE) for outbound from container

Limitation: `-p` is per-container; doesn't scale to clusters. K8s Services solve this.

### Host network avoids the NAT
- No `-p` needed
- Lower latency
- But shares host's port space (conflicts!)

## Container Communication

### Same custom bridge: by name
```bash
docker network create mynet
docker run -d --network mynet --name db postgres
docker run -d --network mynet --name api -e DB_HOST=db myapi
# api can connect to db:5432
```

### Different networks
- Containers on different bridges can't talk directly
- Cross-network requires shared network or NAT

### Inter-container DNS
Docker's built-in DNS server resolves container names to IPs (on user-defined networks).

## /etc/resolv.conf in Container

```bash
docker run busybox cat /etc/resolv.conf
```

Default:
- Docker's embedded DNS server (127.0.0.11) on user-defined networks
- Or inherits host's nameservers

Configure:
```bash
docker run --dns 8.8.8.8 --dns-search example.com busybox
```

## Network Inspection

```bash
docker network ls
docker network inspect mynet
docker inspect --format '{{.NetworkSettings.IPAddress}}' container
docker exec container ip a
docker exec container ss -tlnp
```

## MTU

If you've ever seen weird hangs:
- Default Docker bridge MTU 1500
- VPN/cloud overlays often need lower (1450, 1400)
- Symptom: small packets work, big packets stall (handshake completes, data hangs)

Set:
```bash
# /etc/docker/daemon.json
{ "mtu": 1450 }
```

## Common Issues

| Symptom | Likely Cause |
|---|---|
| Can't reach external services | iptables on host blocking; Docker chain order |
| Container can't be reached from host | Bound to 127.0.0.1 inside; bind to 0.0.0.0 |
| `-p` doesn't expose | Container also needs to listen on 0.0.0.0:port |
| DNS slow inside container | musl libc (alpine) DNS quirks |
| Conntrack table full | High connection rate; raise nf_conntrack_max |

## Production Note

For multi-host (Docker Swarm / K8s), Docker network drivers are largely irrelevant — orchestrator-level networking (Swarm overlay, K8s CNI) takes over. Most teams skip Docker networking deep-dive and learn K8s CNI instead.

## Interview Themes

- "Compare bridge, host, overlay, none"
- "How does -p work?"
- "Container A wants to talk to container B — set up"
- "Docker DNS — how?"
- "When host network mode?"
