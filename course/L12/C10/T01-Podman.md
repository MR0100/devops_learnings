# L12/C10/T01 — Podman (Daemonless)

## Learning Objectives

- Use Podman
- Migrate from Docker

## Podman

Red Hat's daemonless container engine:
- No dockerd
- Rootless default
- Docker-compatible CLI
- K8s pod support

## Install

```bash
# RHEL/CentOS
sudo dnf install -y podman

# Ubuntu
sudo apt install -y podman

# macOS
brew install podman
podman machine init
podman machine start
```

## Basics

```bash
podman run -d nginx
podman ps
podman build -t myapp .
podman push myimage
podman pull image
```

Same as Docker.

## Architecture

```
podman → conmon → runc → container
```

No daemon. Each command: independent process.

## Rootless

```bash
podman run nginx
# Already rootless; no setup
```

User namespace mapping. Container "root" = user.

## Pods

```bash
podman pod create --name mypod -p 8080:80
podman run -d --pod mypod nginx
podman run -d --pod mypod alpine sleep 1000
```

K8s-like pods locally. Shared network.

## Play Kube

```bash
podman play kube deployment.yaml
```

Apply K8s YAML locally. Limited but useful.

## Generate Kube

```bash
podman generate kube mypod > pod.yaml
```

Export running setup as K8s YAML.

For: prototype → K8s.

## systemd Integration

```bash
podman generate systemd --name mycontainer > ~/.config/systemd/user/mycontainer.service
systemctl --user enable mycontainer.service
systemctl --user start mycontainer.service
```

Container as systemd unit. Auto-restart, etc.

For: production single-host.

## Quadlet

Modern systemd integration:
```ini
# /etc/containers/systemd/myapp.container
[Container]
Image=nginx
PublishPort=8080:80

[Service]
Restart=on-failure
```

```bash
systemctl daemon-reload
systemctl start myapp
```

For: simpler than systemd-generate.

## Docker Compatibility

```bash
alias docker=podman
docker run nginx   # works (mostly)
```

Most commands identical.

## Differences

| | Docker | Podman |
|---|---|---|
| Daemon | Yes | No |
| Rootless | Optional | Default |
| Compose | docker compose | podman-compose or play kube |
| Volumes | /var/lib/docker | ~/.local/share/containers |
| Network | iptables | slirp4netns (rootless) |

## Compose

```bash
# Option 1: podman-compose
pip install podman-compose
podman-compose up

# Option 2: docker compose (with podman socket)
systemctl --user start podman.socket
export DOCKER_HOST=unix:///run/user/$(id -u)/podman/podman.sock
docker compose up
```

## Limitations

Rootless:
- Slow network (slirp4netns)
- Privileged ports require workaround
- Some legacy apps fail

## Performance

- Container start: similar to Docker
- Network (rootless): slower
- Image build: Buildah (often faster)

## Build

```bash
podman build -t myapp .
```

Uses Buildah underneath.

Or:
```bash
buildah bud -t myapp .
buildah build -t myapp .
```

## Migration from Docker

Most works:
```bash
podman run -p 8080:80 -v /data:/data nginx
```

Issues:
- Rate limits on Docker Hub (same)
- Permissions (UID differences)
- Some Docker-specific features

For: gradual migration.

## When Podman

- Daemonless preferred
- Rootless first
- Red Hat ecosystem
- K8s-style local
- Security-sensitive

## When Docker

- Compose-heavy workflows
- Mac/Win (Docker Desktop better polished)
- Team familiar
- Existing infrastructure

## Best Practices

- Rootless for dev
- Quadlets for systemd
- play kube for K8s migration
- Backup volumes (different location)
- Test compatibility

## Common Mistakes

- Privileged ports rootless (use >1024 or port forward)
- Volume permissions (UID differences)
- Expecting daemon (it's not there)
- Docker-only features

## Real Use Cases

- CI runners (rootless safer)
- Production single-host (systemd integration)
- Dev (default rootless)
- Edge devices (lightweight, no daemon)

## Docker Desktop Alternative

For Mac/Linux: Podman Desktop.

GUI; familiar; avoids Docker license.

## CRI-O Connection

CRI-O: K8s container runtime (alternative to containerd).
Podman: standalone CLI.

Same low-level: runc.

For K8s nodes: CRI-O or containerd.

## Quick Refs

```bash
# Basics
podman run / ps / images / pull / push / build
podman exec / logs / stop / rm

# Pods
podman pod create / list / rm
podman play kube FILE.yaml
podman generate kube CONTAINER > pod.yaml

# Compose
podman-compose up

# Systemd
podman generate systemd --name CONTAINER
```

## Interview Prep

**Mid**: "Podman vs Docker."

**Senior**: "Why daemonless."

**Staff**: "Podman migration strategy."

## Next Topic

→ [T02 — Buildah for Image Building](T02-Buildah.md)
