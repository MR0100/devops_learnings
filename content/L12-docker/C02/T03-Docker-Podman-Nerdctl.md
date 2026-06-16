# L12/C02/T03 — Docker vs Podman vs nerdctl

## Learning Objectives

- Choose container tool
- Understand differences

## Three Tools

| | Docker | Podman | nerdctl |
|---|---|---|---|
| Daemon | Yes (dockerd) | No | No |
| Underneath | containerd | crun/runc | containerd |
| CLI compat | Original | Yes (mostly) | Yes |
| Rootless | Possible | Default | Possible |
| K8s integration | Indirect | n/a | Yes (CRI) |
| Maturity | Most | Mature | Mature |

## Docker

The original.

```bash
docker run -d nginx
docker build -t myapp .
docker push myimage
docker compose up
```

Daemonized: dockerd handles ops.

### Pros
- Most popular
- Largest ecosystem
- Docker Hub default
- Many tutorials
- Docker Desktop (Mac/Win)

### Cons
- Daemon root (security)
- Daemon SPOF
- Heavier than alternatives

## Podman

Red Hat's daemonless alternative.

```bash
podman run -d nginx
podman build -t myapp .
podman push myimage
podman-compose up   # or podman play kube
```

Same CLI; no dockerd.

### Pros
- Daemonless (no SPOF)
- Rootless default
- Pod-aware (multiple containers grouped)
- Tighter integration with systemd
- Built-in K8s YAML support (`podman play kube`)

### Cons
- Less ecosystem
- Some Docker-specific features missing
- Different volume defaults

## nerdctl

containerd's native CLI.

```bash
nerdctl run -d nginx
nerdctl build -t myapp .
nerdctl push myimage
nerdctl compose up
```

Closest to Docker; uses containerd.

### Pros
- Fast (skip dockerd)
- Closest to Docker compat
- containerd features exposed
- Good for K8s nodes

### Cons
- Smaller ecosystem
- Less polished UX

## When Docker

- Default for most
- Docker Hub / Compose deeply integrated
- Team familiar
- Mac/Windows dev (Docker Desktop)

## When Podman

- Rootless first
- No daemon preferred
- Red Hat ecosystem
- K8s-style pods locally
- Tighter security

## When nerdctl

- Already use containerd
- K8s node tooling
- Want Docker UX without dockerd
- Performance critical

## Compose

Docker Compose:
```bash
docker compose up
docker compose down
```

Podman:
```bash
podman compose up
# Or
podman-compose up
```

nerdctl:
```bash
nerdctl compose up
```

All support `docker-compose.yml`.

## Rootless

### Docker Rootless
```bash
dockerd-rootless-setuptool.sh install
# Then:
docker context use rootless
docker run nginx
```

Works but: special setup.

### Podman Rootless
```bash
podman run nginx   # already rootless
```

Default. No setup.

For: defense in depth.

## Differences

### Network
Docker bridge mode default; isolated.
Podman: similar; sometimes slirp4netns (slower).

### Volumes
Docker: `/var/lib/docker/volumes/`.
Podman: `~/.local/share/containers/storage/volumes/` (rootless).

### Build
Docker: build via dockerd.
Podman: Buildah underneath (separate but coordinated).
nerdctl: BuildKit.

## CLI Compatibility

```bash
# Most commands identical
docker run / podman run / nerdctl run
docker ps / podman ps / nerdctl ps
docker build / podman build / nerdctl build
docker pull / podman pull / nerdctl pull
```

For: drop-in replacement mostly.

## Docker-Specific Features Missing

In Podman / nerdctl (some):
- Swarm mode
- Some compose features
- Docker Hub default behavior
- Docker Desktop

For: edge cases.

## Podman Pods

```bash
podman pod create --name mypod -p 8080:80
podman run -d --pod mypod nginx
podman run -d --pod mypod alpine sleep 1000
```

K8s-style pod locally; shared network.

## Podman Play Kube

```bash
podman play kube deployment.yaml
```

Run K8s manifest locally. For dev / testing.

## K8s Migration

K8s 1.24+: containerd default (no dockershim).

If using:
- Docker: still works (containerd under)
- Containerd: direct
- crio: alternative

`crictl` for K8s container debugging:
```bash
crictl ps
crictl logs CONTAINER
crictl exec -it CONTAINER sh
```

## Docker Desktop

Mac/Windows: runs Linux VM.
- Hosts dockerd
- K8s built-in (optional)
- GUI

Licensing: paid for large companies (Docker Subscription).

Alternatives:
- Colima (open source; Mac/Linux)
- Podman Desktop
- Rancher Desktop

## Mac Docker Alternatives

```bash
# Colima
brew install colima
colima start
docker run nginx   # uses colima's docker

# Podman Desktop
brew install podman-desktop
```

For: avoid Docker Desktop license.

## Performance

| | Docker | Podman | nerdctl |
|---|---|---|---|
| Start | Daemon overhead | Faster | Faster |
| Build | dockerd | Buildah | BuildKit |
| Memory | Daemon 100+ MB | Lighter | Lighter |

For: containerd-based (Podman/nerdctl) often leaner.

## Image Compatibility

All build OCI-compliant images. Interoperate:
- Docker pushes; Podman pulls
- Same registry standards

## When Hybrid

Some use multiple:
- Docker Desktop for dev (Mac)
- Podman for production (no daemon)
- nerdctl for K8s nodes (containerd)

Per-context choice.

## Migrating Docker → Podman

Mostly drop-in:
```bash
alias docker=podman
```

Or install both; switch as needed.

Caveats:
- Network differences (slirp4netns)
- Volume mount permissions (user namespace)
- Some daemon-dependent tools (Compose alternatives)

## Containerd Direct (K8s)

```bash
ctr image pull docker.io/library/nginx:latest
ctr run -d --net-host docker.io/library/nginx:latest nginx
```

Low-level; for debugging K8s nodes.

`nerdctl` is friendlier for same.

## Production Choice

For organizations:
- K8s: containerd (1.24+ default)
- VMs running containers: Docker or Podman
- Edge / IoT: Podman often (security + minimal)
- Dev: Docker Desktop or alternatives

## License

- Docker: open source CE; paid Desktop for big orgs
- Podman: open source
- nerdctl: open source

For cost-conscious: Podman / nerdctl.

## Future

- Containerd: K8s standard
- Podman: enterprise (Red Hat)
- Docker: dev experience, still dominant
- nerdctl: K8s-adjacent tooling

All co-exist.

## Best Practices

- Pick consistent tool per env
- Document why
- Don't mix dev / prod (Docker dev → containerd prod = compatibility check)
- Test images on prod runtime in CI

## Common Mistakes

- Assuming Docker == OCI (not strictly)
- Mac Docker Desktop license surprise
- Rootless gotchas (volumes, network)
- Dockerd as cluster service (SPOF)

## Quick Refs

```bash
# Same across all three
TOOL run [-d] [-it] [-p HOST:CONTAINER] [--name NAME] IMAGE [CMD]
TOOL ps [-a]
TOOL images
TOOL build -t NAME .
TOOL push NAME
TOOL pull NAME
TOOL logs CONTAINER
TOOL exec -it CONTAINER CMD
TOOL stop / start / rm CONTAINER

# TOOL = docker | podman | nerdctl
```

## Interview Prep

**Mid**: "Docker vs Podman."

**Senior**: "Why daemonless."

**Staff**: "Container tool strategy for org."

## Next Topic

→ Move to [L12/C03 — Dockerfile Mastery](../C03/README.md)
