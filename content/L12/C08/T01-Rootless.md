# L12/C08/T01 — Rootless Containers

## Learning Objectives

- Run rootless containers
- Apply security model

## Rootless

Container runtime + containers run as non-root user.

Without root:
- Compromise limited to user
- No privileged operations possible
- Better security posture

## Why

- Defense in depth
- Multi-user systems
- Compliance (no root daemon)
- Container escape limited

## Docker Rootless

```bash
dockerd-rootless-setuptool.sh install
```

Setup:
- User-mode dockerd
- User namespace mapping
- Network via slirp4netns (slower)
- Storage in $HOME

## Podman Rootless (Default)

```bash
podman run nginx
```

Already rootless. No special setup.

For: easier than Docker rootless.

## How

User namespace:
- Container UID 0 = host UID 100000
- Container UID 1000 = host UID 101000

Container "root" is actually limited host user.

For: escape doesn't grant root.

## Capabilities

Rootless: limited capabilities by default.

Can't:
- Bind privileged ports (<1024)
- Use most CAP_*
- Mount certain filesystems

For: use unprivileged ports.

## Storage

Rootless storage:
- `~/.local/share/docker/` (Docker)
- `~/.local/share/containers/` (Podman)

Permissions: user's only.

## Network

```bash
docker info
# Network: rootless uses slirp4netns
```

Slower than root mode:
- Bridge networking via user-space NAT
- slirp4netns or rootlesskit

For: dev mode acceptable.

## Limitations

Rootless can't:
- Bind ports <1024 (need cap or port forward)
- Some volume types
- Network performance: slower
- Some legacy apps fail

For: most modern apps work.

## Port Mapping

```bash
docker run -p 8080:80 nginx   # OK (>1024)
docker run -p 80:80 nginx    # Fail (rootless)
```

Workaround:
- Use port forwarding (host iptables)
- Or use port >1024

## sysctls

Some sysctls require root:
```bash
docker run --sysctl net.ipv4.ip_unprivileged_port_start=80 ...
```

For ports <1024 rootless.

## Apparmor / SELinux

Rootless: limited LSM access. Most policies don't apply.

## K8s Rootless

For nodes:
- Most don't run rootless (containerd as root)
- Pods can run rootless (PSS restricted)

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
```

## When Rootless

- Dev environments
- Multi-user systems
- Strict security
- Compliance

## When Root

- Production K8s nodes
- Bare metal performance
- Specific tools (network analyzers)

## Setup Docker Rootless

```bash
# Install
dockerd-rootless-setuptool.sh install

# Set env
export PATH=$HOME/bin:$PATH
export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock

# Test
docker info
```

## Configuration

`~/.config/docker/daemon.json`:
```json
{
  "storage-driver": "fuse-overlayfs"
}
```

Some features differ in rootless.

## Performance

- Network: 30-50% slower
- Disk: similar
- CPU: similar

For low-network dev: fine.
For high-perf prod: rooted.

## Volume Permissions

```bash
# Host UID 1000 owns file
echo "data" > /tmp/myfile
chmod 644 /tmp/myfile

# Rootless container with same UID can read
docker run -v /tmp/myfile:/data alpine cat /data
```

User UID consistent host ↔ container.

## subuid / subgid

Map ranges:
```bash
cat /etc/subuid
# user:100000:65536

cat /etc/subgid
# user:100000:65536
```

User has 65536 UIDs to map into containers.

## Idmapped Mounts (Newer)

```bash
docker run --userns=keep-id -v /host:/container alpine
```

Modern user namespace mapping. Better permission handling.

## Migration to Rootless

For team:
1. Test app in rootless dev
2. Identify port issues (use >1024)
3. Network perf acceptable?
4. Switch dev workflow
5. Document differences

## Best Practices

- Rootless for dev (where possible)
- Use Podman for default rootless
- Test compat (some apps require capabilities)
- Document UID strategy
- Pod Security Standards in K8s

## Common Mistakes

- Privileged ports in rootless
- Wrong UID mapping
- Volume permissions wrong
- Expect root capabilities

## K8s Pod Security

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  allowPrivilegeEscalation: false
  capabilities:
    drop: [ALL]
  readOnlyRootFilesystem: true
  seccompProfile:
    type: RuntimeDefault
```

For: full rootless + locked-down pod.

## Verify

```bash
docker run --rm alpine id
# uid=0(root) gid=0(root)   [in container; mapped on host]

# On host (find docker proc)
ps -ef | grep alpine
# UID 100000 (user namespace mapped)
```

## Quick Refs

```bash
# Docker rootless install
dockerd-rootless-setuptool.sh install

# Podman rootless (default)
podman run IMAGE

# K8s
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
```

## Interview Prep

**Mid**: "Rootless container benefits."

**Senior**: "Rootless vs root for production."

**Staff**: "Rootless migration plan."

## Next Topic

→ [T02 — Image Scanning](T02-Image-Scanning.md)
