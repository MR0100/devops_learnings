# L02/C01/T03 — File Permissions, ACLs, Capabilities

## Learning Objectives

- Master the standard rwx permission model
- Use ACLs for fine-grained access
- Use Linux capabilities instead of `setuid root`

## Standard Permissions

```
-rwxr-xr-x  user:group  file
│└─┬─┘└─┬─┘└─┬─┘
│  │    │    └ Other (everyone else)
│  │    └ Group
│  └ Owner (user)
└ File type (- file, d dir, l link, b block, c char, p pipe, s socket)
```

### Reading Permissions Numerically
- r = 4, w = 2, x = 1
- rwx = 7, rw- = 6, r-x = 5, r-- = 4
- `chmod 755 file` → rwxr-xr-x
- `chmod 644 file` → rw-r--r--
- `chmod 600 file` → rw-------

### Special Bits
- **setuid (4xxx)**: run as the file's owner
- **setgid (2xxx)**: run as the file's group; on dir → new files inherit dir's group
- **sticky (1xxx)**: only owner can delete (used on `/tmp`)

```bash
chmod u+s file       # setuid
chmod g+s dir        # setgid
chmod +t dir         # sticky
ls -l                # shows s, S, t, T
```

### Default Permissions: umask

`umask` subtracts permissions from defaults (666 file, 777 dir).
- `umask 022` → files 644, dirs 755 (common)
- `umask 027` → group r, others nothing (more secure)

## POSIX ACLs

When 3-level perms aren't enough:

```bash
setfacl -m u:alice:rwx file        # grant alice rwx
setfacl -m g:devs:rx file          # grant group devs rx
setfacl -m d:u:bob:rwx dir         # default ACL on dir
getfacl file                       # view ACLs
```

ACLs show as `+` in `ls -l`:
```
-rw-rwxr-x+ 1 owner group  file
```

## Linux Capabilities

Capabilities split root's omnipotence into 40+ specific powers. Instead of `setuid root`, give a binary just the capability it needs.

Common capabilities:
- `CAP_NET_BIND_SERVICE` — bind ports < 1024
- `CAP_NET_ADMIN` — network admin (configure interfaces)
- `CAP_SYS_ADMIN` — broad ("the new root"); avoid
- `CAP_SYS_PTRACE` — trace other processes
- `CAP_DAC_OVERRIDE` — bypass file permission checks
- `CAP_CHOWN` — change file ownership

```bash
getcap /usr/bin/ping             # see capabilities
setcap cap_net_bind_service+ep /usr/bin/myapp
getcap -r /usr/bin/              # recursive
```

### Containers and Capabilities

Docker drops most capabilities by default. To grant:
```bash
docker run --cap-add NET_ADMIN myimage
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE myimage
```

Kubernetes:
```yaml
securityContext:
  capabilities:
    drop: ["ALL"]
    add: ["NET_BIND_SERVICE"]
```

## Why Capabilities Matter

Pre-capabilities: a setuid root binary could do **anything**. One vulnerability = full root. With capabilities, a vulnerable binary that only had `CAP_NET_BIND_SERVICE` couldn't `chown`, `setuid`, modify `/etc/passwd`, etc.

## Common Mistakes

- Using `chmod 777` "to make it work" — almost always wrong
- Using `setuid root` instead of capabilities
- Forgetting `setgid` on team shared dirs (causes wrong group ownership)
- Confusing ACL behavior with default perms

## Interview Prep

**Junior**: "Explain chmod 755."

**Mid**: "When would you use ACLs over standard perms?"

**Senior**: "We need an app to bind port 80 without running as root. How?"
- `setcap cap_net_bind_service+ep` on the binary, OR use systemd `AmbientCapabilities`, OR run with K8s `securityContext`.

## Next Topic

→ [T04 — Essential Commands](T04-Essential-Commands.md)
