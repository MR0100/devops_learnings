# L12/C01/T05 — Capabilities & Seccomp

## Learning Objectives

- Drop Linux capabilities
- Apply seccomp profiles

## Linux Capabilities

Granular root permissions:
- Traditional root: all-or-nothing
- Capabilities: split into ~40

Examples:
- CAP_NET_ADMIN: network config
- CAP_SYS_ADMIN: many things (avoid)
- CAP_NET_BIND_SERVICE: bind ports <1024
- CAP_CHOWN: change ownership
- CAP_SETUID, CAP_SETGID
- CAP_DAC_OVERRIDE: bypass file permissions
- CAP_KILL: send signals

For: privilege without full root.

## Container Default

Docker default: dropped most capabilities.

Granted by default:
- CAP_CHOWN, CAP_DAC_OVERRIDE, CAP_FOWNER, CAP_FSETID
- CAP_KILL, CAP_SETGID, CAP_SETUID, CAP_SETPCAP
- CAP_NET_BIND_SERVICE, CAP_NET_RAW
- CAP_SYS_CHROOT
- CAP_MKNOD, CAP_AUDIT_WRITE, CAP_SETFCAP

Dropped: CAP_NET_ADMIN, CAP_SYS_ADMIN, etc.

For: most apps fine.

## Drop All; Add Specific

```bash
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE nginx
```

Best practice: drop all; add only needed.

K8s:
```yaml
securityContext:
  capabilities:
    drop: [ALL]
    add: [NET_BIND_SERVICE]
```

## Privileged

```bash
docker run --privileged ...
```

ALL capabilities + access to /dev + etc.

For:
- Docker-in-Docker
- CSI drivers
- Some hardware access

DANGEROUS; defeats most isolation.

## Identify Needed

Test container; check what fails:
```bash
docker run --cap-drop=ALL --user 1000 nginx
# Errors if missing caps
```

Add needed; iterate.

## Inspect

```bash
# Capabilities of process
cat /proc/<PID>/status | grep Cap
# CapInh, CapPrm, CapEff, CapBnd, CapAmb (5 sets)

# Decode
capsh --decode=00000000a80425fb
```

## Specific Capabilities Examples

### NET_BIND_SERVICE
Bind to ports < 1024 (e.g., 80, 443).

Without: app must use port > 1024.

### CAP_NET_RAW
Raw sockets (ping, etc.).

Often safe to drop.

### CAP_SYS_ADMIN
Mount, chroot, set hostname, more.

Almost always avoid.

### CAP_SYS_PTRACE
Debug other processes (strace).

Usually avoid; security risk.

## seccomp

Secure computing mode: restrict syscalls.

Linux has ~300 syscalls. Most apps need ~50.

Block dangerous ones.

## Default Profile

Docker default seccomp profile blocks ~50 dangerous syscalls:
- `reboot`, `kexec_load`
- `swapon`, `umount`
- Many others

For: defense in depth.

## Custom Profile

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "syscalls": [
    {
      "names": ["read", "write", "open", "close", ...],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

Allowlist syscalls.

```bash
docker run --security-opt seccomp=profile.json nginx
```

## K8s Seccomp

```yaml
securityContext:
  seccompProfile:
    type: RuntimeDefault   # use container runtime's default
```

Or:
```yaml
seccompProfile:
  type: Localhost
  localhostProfile: my-profile.json
```

Pod Security Standards `restricted` requires `RuntimeDefault`.

## strace to Identify

What syscalls does app use?
```bash
strace -c nginx
# Summary of syscalls
```

For: building custom profile.

## Unconfined

```bash
docker run --security-opt seccomp=unconfined ...
```

No syscall filter. Dangerous.

Avoid in production.

## Combined Defense

Container security layers:
1. User namespace (UID mapping)
2. Capabilities (root privileges granular)
3. Seccomp (syscall whitelist)
4. AppArmor / SELinux (path-based / label-based)
5. NetworkPolicy (network isolation)

Each catches what others miss.

## Real-World

For typical app:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  capabilities:
    drop: [ALL]
    add: [NET_BIND_SERVICE]   # if needed
  seccompProfile:
    type: RuntimeDefault
  readOnlyRootFilesystem: true
```

Strong defense.

## Pod Security Standards

`restricted` profile requires:
- runAsNonRoot
- runAsUser != 0
- allowPrivilegeEscalation: false
- capabilities drop ALL
- seccompProfile RuntimeDefault

For prod: PSS restricted.

## CAP Without Root

Some caps usable without root via file caps:
```bash
setcap cap_net_bind_service=+ep ./myapp
```

Then user can bind to <1024 ports.

For: avoid running as root entirely.

## AppArmor (Defense in Depth)

```bash
docker run --security-opt apparmor=docker-default nginx
```

Path-based MAC. Restricts file access.

## SELinux

For RHEL / similar:
```bash
docker run --security-opt label=type:my_label nginx
```

Label-based MAC. Strict.

## Common Mistakes

- Privileged container (no isolation)
- Drop ALL but need specific (errors)
- No seccomp (all syscalls)
- Run as root (no need)
- Capabilities granted but not needed

## Best Practices

- runAsNonRoot
- Drop ALL capabilities; add specific
- seccompProfile: RuntimeDefault
- readOnlyRootFilesystem
- No privileged
- Drop CAP_SYS_ADMIN especially

## Test

Run with strict settings; observe failures:
```bash
docker run \
  --cap-drop=ALL \
  --security-opt seccomp=default \
  --user 1000 \
  --read-only \
  myapp
```

Add what's needed; document.

## CIS Benchmark

CIS Docker Benchmark recommends:
- Drop capabilities not needed
- seccomp default
- AppArmor / SELinux
- Non-root

Audit via:
```bash
docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -v /var/lib:/var/lib -v /var/run/docker.sock:/var/run/docker.sock \
  -v /etc:/etc docker/docker-bench-security
```

## Profile Generation

eBPF-based tools generate seccomp profiles:
- syscall2seccomp
- security-profiles-operator (K8s)

Run app; capture syscalls; generate.

For: customized profiles.

## Falco

Runtime detection:
- Suspicious syscalls
- File modifications
- Network anomalies

Alerts on violations.

For: detect attacks even with defenses.

## Quick Refs

```bash
# Docker
docker run --cap-drop=ALL --cap-add=X --user 1000 --read-only IMAGE
docker run --security-opt seccomp=profile.json --security-opt no-new-privileges IMAGE

# Inspect
cat /proc/PID/status | grep Cap
capsh --decode=0x...
capsh --print

# K8s securityContext (above)
```

## Interview Prep

**Mid**: "Drop capabilities."

**Senior**: "seccomp profile."

**Staff**: "Container security strategy."

## Next Topic

→ Move to [L12/C02 — Docker Architecture](../C02/README.md)
