# L02/C01/T02 — Filesystem Hierarchy Standard (FHS)

## Learning Objectives

- Know where to look for any system file
- Understand why directories exist where they do
- Use the right place for application data, configs, and runtime state

## The Standard Layout

```
/
├── bin    → /usr/bin       Essential user binaries (cp, ls, mv)
├── sbin   → /usr/sbin      Essential system binaries (mount, fsck)
├── lib    → /usr/lib       Essential shared libraries
├── boot                    Bootloader files, kernel images
├── dev                     Device files (/dev/null, /dev/sda)
├── etc                     Host-specific configuration
├── home                    User home directories
├── mnt                     Temporary mount points
├── media                   Removable media mount points
├── opt                     Optional add-on packages
├── proc                    Virtual: process info & kernel data
├── root                    Root user's home
├── run                     Runtime data (PID files, sockets)
├── srv                     Site-specific data served by the system
├── sys                     Virtual: kernel & device interface
├── tmp                     Temporary files (cleared at reboot)
├── usr                     Read-only user programs and data
│   ├── bin
│   ├── lib
│   ├── local              Locally installed software
│   ├── sbin
│   └── share              Architecture-independent data
└── var                     Variable data
    ├── lib                Persistent state of services
    ├── log                Log files
    ├── run    → /run      Runtime variable data
    ├── spool              Print/mail/cron spool
    └── tmp                Persistent temp (survives reboot)
```

## Important Distinctions

### `/etc` vs `/var` vs `/usr`
- `/etc` — configuration that changes the system's behavior
- `/var` — data that changes during normal operation
- `/usr` — files that don't change without a package update

### `/run` vs `/tmp` vs `/var/tmp`
- `/run` — tmpfs (in RAM), cleared at boot; PID files, sockets
- `/tmp` — usually tmpfs in modern distros; cleared at boot
- `/var/tmp` — persistent temp across reboots

### `/proc` and `/sys` — Virtual Filesystems
These are not on disk. Reading them queries kernel state.

| Path | Returns |
|---|---|
| `/proc/cpuinfo` | CPU details |
| `/proc/meminfo` | Memory stats |
| `/proc/<pid>/` | Per-process info |
| `/proc/<pid>/status` | Process status (use this, not ps, sometimes) |
| `/proc/<pid>/limits` | Resource limits |
| `/proc/<pid>/maps` | Memory maps |
| `/proc/<pid>/fd/` | Open file descriptors |
| `/sys/class/net/` | Network interfaces |
| `/sys/fs/cgroup/` | Cgroup hierarchy |
| `/sys/kernel/` | Kernel tunables |

## Where Application Code Goes

- System package: `/usr/bin`, `/usr/lib`
- Local install (manual): `/usr/local/bin`, `/usr/local/lib`
- Third-party / vendor: `/opt/<vendor>` (e.g., `/opt/datadog-agent`)
- Containerized: anywhere; OCI standard puts apps at `/`

## Where Data Goes

- Service state: `/var/lib/<service>` (e.g., `/var/lib/postgresql`)
- Logs: `/var/log/<service>` (or `journalctl`)
- Caches: `/var/cache/<service>`
- Runtime sockets/PIDs: `/run/<service>`

## /usr Merge

Modern distros symlink `/bin → /usr/bin`, `/sbin → /usr/sbin`, etc. This is "the /usr merge" — completed in Fedora 17 (2012), Debian buster (2019), Ubuntu 19.10. The reason: simplification and snapshot/atomic upgrade compatibility.

## Interview Prep

**Junior**: "What's in /etc?"

**Mid**: "Where should an application write logs and runtime PID files?"

**Senior**: "Walk me through what `/proc` and `/sys` are and how you use them in production debugging."

## Next Topic

→ [T03 — File Permissions, ACLs, Capabilities](T03-Permissions-ACLs-Capabilities.md)
