# L02/C01/T02 — Filesystem Hierarchy Standard (FHS)

## Learning Objectives

- Know where to look for any system file and why it lives there
- Distinguish configuration (`/etc`), variable state (`/var`), and immutable program data (`/usr`)
- Place application binaries, data, configs, and runtime state in the correct, FHS-compliant locations
- Use the virtual filesystems `/proc` and `/sys` for production debugging

## The Standard Layout

```
/
├── bin    → /usr/bin       Essential user binaries (cp, ls, mv)
├── sbin   → /usr/sbin      Essential system binaries (mount, fsck)
├── lib    → /usr/lib       Essential shared libraries, kernel modules
├── boot                    Bootloader files, kernel + initramfs images
├── dev                     Device nodes (/dev/null, /dev/sda) — devtmpfs
├── etc                     Host-specific configuration (text, no binaries)
├── home                    User home directories
├── mnt                     Temporary admin mount points
├── media                   Removable media auto-mount points
├── opt                     Self-contained third-party packages
├── proc                    Virtual: process + kernel state (procfs)
├── root                    Root user's home
├── run                     Runtime data: PID files, sockets (tmpfs)
├── srv                     Site-specific data served by the system
├── sys                     Virtual: kernel + device interface (sysfs)
├── tmp                     Temporary files (often tmpfs, cleared at boot)
├── usr                     Read-only-ish user programs and data
│   ├── bin
│   ├── lib
│   ├── local              Locally compiled/installed software
│   ├── sbin
│   └── share              Architecture-independent data (man, docs)
└── var                     Variable data
    ├── lib                Persistent state of services (databases)
    ├── log                Log files
    ├── cache              Regenerable cache data
    ├── run    → /run      Runtime variable data (legacy symlink)
    ├── spool              Print/mail/cron/at spool queues
    └── tmp                Persistent temp (survives reboot)
```

## Important Distinctions

### `/etc` vs `/var` vs `/usr`
- `/etc` — configuration that changes the system's *behavior*; should be hand- or tool-editable text, no large data, no binaries
- `/var` — data that changes during *normal operation* (logs, queues, databases, caches)
- `/usr` — files that don't change without a package operation; mountable read-only on hardened/immutable systems

This separation is what makes read-only-root and atomic-upgrade designs possible: mount `/usr` read-only, keep mutable state in `/var` and `/etc`.

### `/run` vs `/tmp` vs `/var/tmp`

| Path | Backing | Lifetime | Use |
|---|---|---|---|
| `/run` | tmpfs (RAM) | cleared at boot | PID files, unix sockets, lock files |
| `/tmp` | tmpfs in modern distros | cleared at boot / by `systemd-tmpfiles` | short-lived scratch |
| `/var/tmp` | on-disk | persists across reboot | larger temp that must survive a restart |

A classic bug: writing multi-GB scratch to `/tmp` when it's a RAM-backed tmpfs sized at 50% of memory — you OOM the box instead of using disk. Use `/var/tmp` or an explicit scratch volume for big files.

### `/proc` and `/sys` — Virtual Filesystems
These are not on disk. Every read synthesizes kernel state on the fly; writes can tune the kernel live.

| Path | Returns / does |
|---|---|
| `/proc/cpuinfo` | CPU model, flags, core count |
| `/proc/meminfo` | Memory stats (MemAvailable, Slab, Committed_AS) |
| `/proc/loadavg` | 1/5/15-min load + running/total tasks |
| `/proc/<pid>/status` | Human-readable process state, VmRSS, threads |
| `/proc/<pid>/limits` | Effective rlimits (open files, etc.) |
| `/proc/<pid>/maps` | Memory mappings (find shared libs, mmap'd files) |
| `/proc/<pid>/fd/` | Open file descriptors (symlinks to real targets) |
| `/proc/<pid>/cgroup` | Which cgroups the process belongs to |
| `/proc/sys/...` | Kernel tunables (same surface as `sysctl`) |
| `/sys/class/net/` | Network interfaces and their attributes |
| `/sys/fs/cgroup/` | cgroup v2 hierarchy: limits and accounting |
| `/sys/kernel/mm/transparent_hugepage/` | THP mode (perf-sensitive) |

```bash
# Find which deleted file is still holding disk (classic "df full, du clean")
ls -l /proc/*/fd/ 2>/dev/null | grep deleted

# What is PID 4242 actually waiting on?
cat /proc/4242/status        # State: D (uninterruptible) => I/O
cat /proc/4242/wchan         # kernel function it's blocked in

# Tune a sysctl live (non-persistent)
echo 1 > /proc/sys/net/ipv4/ip_forward
sysctl -w net.ipv4.ip_forward=1     # equivalent, preferred
```

## Where Application Code Goes

- System package: `/usr/bin`, `/usr/lib` (managed by the package manager — don't hand-edit)
- Local install (manual `make install`): `/usr/local/bin`, `/usr/local/lib` (kept separate so package upgrades never clobber it)
- Third-party / vendor self-contained: `/opt/<vendor>` (e.g., `/opt/datadog-agent`, `/opt/google/chrome`)
- Containerized: anywhere; the OCI convention often puts the app at `/app` or `/`

## Where Data Goes

- Service persistent state: `/var/lib/<service>` (e.g., `/var/lib/postgresql`, `/var/lib/docker`)
- Logs: `/var/log/<service>` (or the journal via `journalctl`)
- Regenerable caches: `/var/cache/<service>`
- Runtime sockets/PIDs: `/run/<service>`

## /usr Merge

Modern distros symlink `/bin → /usr/bin`, `/sbin → /usr/sbin`, `/lib → /usr/lib`. This is "the /usr merge" — completed in Fedora 17 (2012), Debian buster (2019), Ubuntu 19.10. The payoff: a single `/usr` tree can be snapshotted, mounted read-only, shared across containers, and atomically swapped on upgrade. It also ends the historic `/bin` vs `/usr/bin` "needed at early boot?" guessing game.

## systemd-tmpfiles and File Lifecycle

You rarely clean `/tmp`, `/run`, or volatile dirs by hand anymore. `systemd-tmpfiles` reads `/usr/lib/tmpfiles.d/` and `/etc/tmpfiles.d/` to create, set permissions on, and age out files declaratively:

```bash
# Example /etc/tmpfiles.d/myapp.conf line:
#   d /run/myapp 0750 myapp myapp -
systemd-tmpfiles --create        # apply now
systemd-tmpfiles --clean         # age out per config
```

This is the right place to ensure `/run/myapp` exists with correct ownership before your service starts, rather than `mkdir`-ing in an ExecStartPre.

## Common Mistakes

- Writing large scratch to `/tmp` when it's RAM-backed tmpfs, OOM-ing the host
- Putting service state in `/usr` (which may be read-only) instead of `/var/lib`
- Hand-editing files in `/usr/bin` or `/usr/lib` — overwritten on the next package upgrade; use `/usr/local` or `/opt`
- Confusing the "disk full but du shows nothing" case — a deleted-but-open file; find it via `/proc/*/fd`
- Persisting anything important to `/run` — it vanishes on reboot

## Best Practices

- Follow FHS so monitoring, backup, and config-management tooling find things where they expect
- Keep `/etc` as text under version control or config management; never store binaries or large blobs there
- Use `/opt/<vendor>` for self-contained third-party agents so uninstall is a single directory removal
- Manage runtime dirs with `systemd-tmpfiles`, not ad-hoc `mkdir` in init scripts
- Treat `/proc` and `/sys` as your first stop in incident response before reaching for heavyweight tools

## Quick Refs

```bash
df -h /tmp /var /run                      # see backing + free space per area
mount | column -t                         # what's mounted, with options
findmnt /var/lib/docker                   # filesystem, source, options for a path
ls -l /proc/$$/fd                         # this shell's open file descriptors
cat /proc/mounts                          # raw kernel view of mounts
du -xsh /var/* 2>/dev/null | sort -rh     # biggest consumers under /var
```

## Interview Prep

**Junior**: "What's in `/etc`?"
- Host-specific configuration as editable text — service configs, users, network, no binaries or large data.

**Mid**: "Where should an application write logs and runtime PID files?"
- Logs to `/var/log/<service>` (or stdout for the journal/container), persistent state to `/var/lib/<service>`, and PID files/sockets to `/run/<service>` since `/run` is tmpfs cleared at boot.

**Senior**: "`df` says the disk is full but `du` finds nothing. What's happening?"
- A process is holding a deleted-but-still-open file, so the blocks aren't freed until the fd closes; find it with `ls -l /proc/*/fd | grep deleted` and restart or truncate the holder.

**Staff**: "Explain `/proc` and `/sys` and how you use them in production debugging."
- Both are virtual filesystems synthesizing live kernel state: `/proc/<pid>/` for per-process state, fds, memory maps, and limits; `/sys` for device and cgroup attributes plus tunables. They're the lowest-overhead, dependency-free way to inspect and tune a running system during an incident.

## Next Topic

→ [T03 — File Permissions, ACLs, Capabilities](T03-Permissions-ACLs-Capabilities.md)
