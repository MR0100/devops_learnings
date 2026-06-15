# L12/C02/T01 — dockerd, containerd, runc

## Learning Objectives

- Map Docker architecture
- Understand each component

## Architecture

```
Docker CLI (docker)
   ↓ REST API
dockerd (Docker daemon)
   ↓ gRPC
containerd
   ↓ shim
runc (or other OCI runtime)
   ↓ Linux kernel
Container (process)
```

Each: specific responsibility.

## docker CLI

User-facing tool:
```bash
docker run nginx
```

Just translates to REST API call to dockerd. No business logic.

## dockerd

Docker daemon:
- Manages images (pull, push, tag)
- Networks (bridge, overlay)
- Volumes
- High-level container API

Listens on:
- Unix socket: /var/run/docker.sock
- TCP (optional): tcp://0.0.0.0:2375

Calls containerd for lifecycle.

## containerd

Container lifecycle:
- Pull images (via OCI distribution)
- Manage container state
- Snapshot management
- Start/stop containers
- Calls runc

Used by:
- Docker
- Kubernetes (since 1.24 default; dockershim removed)
- Podman (via crun)

CRI plugin: implements K8s CRI.

## runc

Low-level runtime:
- Reads OCI spec
- Creates namespaces / cgroups
- Calls clone() / execve()
- One container per runc invocation

After container started: runc exits. containerd-shim manages.

## containerd-shim

Per-container process:
- Reparents container if containerd restarts
- Reports exit
- Manages stdio (logs)
- Reaps zombie

For: container survival across containerd restart.

## Why Layered

- Separation of concerns
- Each: testable
- Each: replaceable
- runc: tiny, focused
- containerd: more features
- dockerd: even more features (build, swarm)

K8s uses containerd directly (skips dockerd) since 1.24.

## OCI Standards

Standards for interop:
- OCI image spec (layers, config)
- OCI runtime spec (config.json for runc)
- OCI distribution spec (registry HTTP API)

For: Docker, containerd, runc, Podman, etc. all interop.

## Run Container Flow

```
docker run nginx
  ↓
dockerd: pull image if needed
  ↓
dockerd: prepare container config
  ↓
dockerd → containerd: create container
  ↓
containerd: snapshot image layers (overlayfs)
  ↓
containerd → runc: start container
  ↓
runc: setup namespaces, cgroups, mount, etc.
  ↓
runc: execve(nginx)
  ↓
nginx running; runc exits
  ↓
containerd-shim: monitor
```

## Alternative Runtimes

- runc: default OCI runtime
- crun: lightweight C alternative
- gVisor: VM-like isolation
- Kata Containers: full VM per container
- youki: Rust runtime

For special needs: alternative runtime.

## gVisor

User-space kernel:
- Intercepts syscalls
- Runs in user space (not host kernel)
- Stronger isolation than runc
- Slower; subset of syscalls

For multi-tenant SaaS.

## Kata Containers

Real VM per container:
- Full isolation
- Slower start
- More overhead
- Stronger isolation

For: high-security needs.

```yaml
# K8s
spec:
  runtimeClassName: kata
```

## Podman

Daemonless alternative:
- No dockerd
- Each podman call: independent
- Rootless by default
- Compatible CLI (docker → podman)

For: avoiding daemon root + rootless first.

## nerdctl

containerd CLI:
- Docker-compatible
- Closer to containerd
- Faster (no dockerd)

For: containerd direct.

## Docker vs Podman vs nerdctl

| | Docker | Podman | nerdctl |
|---|---|---|---|
| Daemon | Yes (dockerd) | No | No |
| Compatible CLI | Original | Yes (mostly) | Yes |
| Rootless | Possible | Default | Possible |
| Underneath | containerd | crun/runc | containerd |
| K8s usage | Indirect | n/a | Yes (CRI) |

For most: Docker still standard.

## K8s + Containerd

K8s 1.24+ removed dockershim. Now uses containerd directly via CRI.

For: no dockerd in K8s nodes.

Functionally: same. Less components.

## Inspect

```bash
# Daemon info
docker info

# containerd status
systemctl status containerd

# Show containers via ctr (containerd's CLI)
ctr containers list
ctr c ls

# Or nerdctl
nerdctl ps
```

## Restart Behavior

Restart dockerd: containers keep running (containerd-shim).

Restart containerd: containers keep running.

Restart runc: N/A (runc exits after start).

Restart kernel: everything dies.

## Logs

Containers' logs:
- stdout/stderr → containerd shim → file
- /var/lib/docker/containers/<id>/<id>-json.log

Or syslog / journal (configurable).

## Performance

- Container start: ~1s (most for runc + setup)
- Cached image: instant pull
- New image: time to download + extract

For low-latency: pre-pull images; warm containers.

## Networking Components

Docker networking:
- libnetwork: networking library
- CNI plugins (K8s)
- iptables for bridge mode

containerd: relies on CNI for networking (K8s).

## Storage Components

- overlay2: image layers (covered C01/T04)
- volumes: separate from image layers

## Configuration

```bash
# Daemon
/etc/docker/daemon.json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {"max-size": "10m", "max-file": "3"}
}
```

```bash
systemctl restart docker
```

## Resource Use

dockerd: ~50-100 MB memory
containerd: ~20-50 MB
runc: ~10 MB per invocation (exits)

Total: ~100 MB for Docker setup.

## Production Setup

For K8s: just containerd (no dockerd needed).

For standalone: full Docker.

For: rootless development: Podman.

## Migration

From Docker → containerd (K8s):
- Already using K8s with Docker: migrate to containerd
- Same images / commands; different runtime
- `crictl` instead of `docker` for direct ctr ops

```bash
# crictl (CRI client)
crictl ps
crictl images
crictl exec ...
```

## Best Practices

- For K8s: containerd
- For dev: Docker or Podman
- Configure log rotation
- Monitor daemon health
- Update daemon (security)

## Common Mistakes

- Believing Docker = containerd (different)
- Running containers via runc directly (low-level)
- No daemon monitoring

## Security

- Docker socket: root-equivalent (don't expose)
- dockerd: typically root
- Podman rootless: better
- Containerd: similar to Docker

## Quick Refs

```bash
docker version
docker info
docker system df

# containerd CLI
ctr containers list
ctr images list

# K8s
crictl ps
crictl images

# Podman
podman ps
podman images
```

## Interview Prep

**Mid**: "Docker components."

**Senior**: "Why containerd in K8s."

**Staff**: "Runtime architecture for security."

## Next Topic

→ [T02 — OCI Image & Runtime Spec](T02-OCI-Spec.md)
