# L02/C02/T05 — systemd Deep Dive

## Learning Objectives

- Master systemd unit files
- Use targets, dependencies, and ordering
- Operate journalctl as a structured log source
- Apply systemd's cgroup integration for resource limits

## What systemd Is

- PID 1 on most modern Linux distros (Debian, Ubuntu, RHEL, Fedora, SUSE, Arch)
- Service manager (units)
- System log aggregator (journald)
- Login manager (logind)
- Network manager (networkd)
- DNS resolver (resolved)
- Time sync (timesyncd)

It's polarizing because it does a lot. But it's the de-facto standard.

## Unit Types

- `.service` — daemon
- `.socket` — socket-activated service
- `.target` — group of units (~runlevel)
- `.timer` — cron replacement
- `.mount` / `.automount` — filesystem mounts
- `.path` — path-triggered action
- `.device` — device unit (from udev)
- `.scope` — externally created processes

## Writing a Service Unit

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application
After=network-online.target postgresql.service
Wants=network-online.target
Requires=postgresql.service

[Service]
Type=simple
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
EnvironmentFile=/etc/myapp/env
ExecStart=/opt/myapp/bin/myapp
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5
TimeoutStopSec=30
KillMode=mixed
KillSignal=SIGTERM

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/myapp /var/log/myapp
PrivateTmp=true
PrivateDevices=true

# Resource limits (cgroups)
MemoryMax=2G
CPUQuota=200%
TasksMax=1024

[Install]
WantedBy=multi-user.target
```

### Service Types
- `simple` — ExecStart is the main process (default)
- `forking` — ExecStart forks; main process is the parent
- `oneshot` — runs once and exits (good for setup)
- `notify` — uses sd_notify() to signal readiness
- `dbus` — registers a D-Bus name

## Common Operations

```bash
systemctl start myapp
systemctl stop myapp
systemctl restart myapp
systemctl reload myapp
systemctl status myapp
systemctl enable myapp        # start on boot
systemctl disable myapp
systemctl daemon-reload       # reload unit files

systemctl list-units --type=service --state=running
systemctl list-unit-files --state=enabled
systemctl list-dependencies myapp

systemctl edit myapp          # override
systemctl edit --full myapp   # edit full unit

systemctl cat myapp           # show effective unit
```

## journald

System log aggregator. Logs are structured and indexed.

```bash
journalctl                            # all logs
journalctl -u myapp                   # specific unit
journalctl -u myapp -f                # follow
journalctl -u myapp --since "1 hour ago"
journalctl -u myapp -p err            # err and higher
journalctl -u myapp -o json-pretty    # JSON output
journalctl --disk-usage               # current usage
journalctl --vacuum-size=500M         # trim
journalctl _PID=1234                  # by PID
journalctl _SYSTEMD_UNIT=myapp.service
```

Logging from your app to journal:
- Write to stdout/stderr — journald captures it
- Use `systemd-cat -t mytag <command>`
- Use `sd-journal` library for structured fields

### Persistent Journals
```bash
mkdir -p /var/log/journal
systemd-tmpfiles --create --prefix /var/log/journal
systemctl restart systemd-journald
```

## Timers (cron replacement)

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=Daily Backup

[Timer]
OnCalendar=daily
Persistent=true     # if missed, run on next boot

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/backup.service
[Unit]
Description=Backup Service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
```

Activate: `systemctl enable --now backup.timer`

Why prefer over cron:
- Better logging via journald
- Persistent across missed runs
- Native cgroup-based resource limits
- Dependency on other units

## Cgroup Integration

systemd places every unit in a cgroup. Limits via:
- `MemoryMax`, `MemoryHigh`, `MemorySwapMax`
- `CPUQuota`, `CPUWeight`, `AllowedCPUs`
- `IOWeight`, `IOReadBandwidthMax`
- `TasksMax`

Inspect:
```bash
systemctl status myapp        # shows cgroup, current RSS, CPU%
systemd-cgtop                 # like top, per-cgroup
```

## Common Mistakes

- Forgetting `daemon-reload` after editing units
- Wrong `Type=` (use `simple` unless you have reason)
- `After=` without `Wants=`/`Requires=` (After only orders, doesn't pull in)
- Hardcoded paths in unit files (use `EnvironmentFile=`)
- Editing vendor units in `/lib/systemd/system` instead of overriding via drop-ins
- Confusing `enable` (start at boot) with `start` (start now) — they're independent

## Best Practices

- **Override with drop-ins, not edits** — `systemctl edit <unit>` writes to `/etc/systemd/system/<unit>.d/override.conf`, surviving package upgrades.
- **Always `daemon-reload` after changing unit files** — systemd caches parsed units; skipping it runs the stale definition.
- **Pull in dependencies, then order them** — use `Wants=`/`Requires=` to start a dependency and `After=` to sequence it; `After=` alone only orders.
- **Lean on the supervisor** — set `Restart=on-failure` with `RestartSec=`, and `StartLimitBurst`/`StartLimitIntervalSec` to avoid crash-loop storms.
- **Sandbox services** — `NoNewPrivileges=`, `ProtectSystem=strict`, `PrivateTmp=`, and `User=` shrink blast radius for free.
- **Externalize config** — `EnvironmentFile=` instead of hardcoded paths/secrets in the unit.

## Quick Refs

```bash
# lifecycle
systemctl start|stop|restart|reload <unit>
systemctl enable --now <unit>      # start now AND at boot
systemctl status <unit>            # state + recent logs
systemctl daemon-reload            # after editing unit files
systemctl edit <unit>              # create a drop-in override

# inspection
systemctl list-units --type=service --state=running
systemctl cat <unit>               # effective unit + drop-ins
systemd-analyze blame              # slowest units at boot
journalctl -u <unit> -f            # follow a unit's logs
journalctl -u <unit> --since "1h ago" -p err
```

**`Type=` cheat**: `simple` (default, foreground) · `exec` (like simple, waits for exec) · `forking` (classic double-fork daemons) · `oneshot` (run-and-exit, pair with `RemainAfterExit=yes`) · `notify` (app calls `sd_notify`).

## Interview Prep

**Mid**: "Write a systemd unit for a Python web app."

**Senior**: "Compare systemd timers to cron."

**Staff**: "Diagnose: 'My app sometimes starts before the network is up.' What changes do you make?"
- `After=network-online.target`, `Wants=network-online.target`, ensure NetworkManager-wait-online or systemd-networkd-wait-online is enabled.

## Next Chapter

→ [C03 — Memory Management](../C03/README.md)
