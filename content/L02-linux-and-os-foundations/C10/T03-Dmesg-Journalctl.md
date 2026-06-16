# L02/C10/T03 — dmesg & journalctl

## Learning Objectives

- Explain the kernel ring buffer and how `dmesg` reads it
- Filter kernel messages by severity, follow them live, and get human timestamps
- Use `journalctl` to query the systemd journal by boot, unit, priority, and time
- Choose between `dmesg` and `journalctl -k` and know what each can and can't see

## The Big Picture

There are two distinct log sources at the bottom of a Linux box, and they
overlap:

```
   Kernel  ──printk()──►  ring buffer (kmsg)  ──►  dmesg
                               │
                               ▼  (read by journald)
   Services ──stdout/syslog──► systemd-journald ──►  journalctl
                               │
                               ▼ (forwarded)
                         /var/log/syslog, rsyslog
```

- **`dmesg`** reads the **kernel ring buffer**: a fixed-size in-memory circular
  buffer where the kernel writes via `printk()`. It is volatile — it is wiped on
  reboot and old entries are overwritten once it fills.
- **`journalctl`** reads the **systemd journal**, which captures *both* kernel
  messages (journald reads `/dev/kmsg`) *and* every service's output, with
  structured metadata and, if persistent storage is enabled, history across
  reboots.

## dmesg — the Kernel Ring Buffer

```bash
$ dmesg | tail -5
[   12.418773] nvme nvme0: 8/0/0 default/read/poll queues
[   12.901233] EXT4-fs (nvme0n1p2): mounted filesystem with ordered data mode
[   45.110982] docker0: port 1(veth9c1) entered forwarding state
[ 1820.554301] Out of memory: Killed process 4412 (java) total-vm:8G
[ 1820.554988] oom_reaper: reaped process 4412 (java)
```

The default timestamps are **seconds since kernel boot**, which is hard to map to
wall-clock time. Useful flags:

```bash
dmesg -T                 # human-readable wall-clock timestamps
dmesg -w                 # follow (like tail -f) — wait for new messages
dmesg -H                 # human pager: colorized, relative time, less
dmesg -x                 # show facility + level (kern, warn, err...)
dmesg --level=err,warn   # only errors and warnings
dmesg --facility=kern    # kernel-facility messages only
dmesg -c                 # print AND clear the buffer (destructive — avoid)
```

`dmesg -T` is approximate: the kernel records monotonic time and `dmesg`
back-calculates wall-clock, so timestamps drift slightly after suspend. For
exact correlation, use the journal.

On hardened kernels, unprivileged `dmesg` is blocked by
`kernel.dmesg_restrict=1`; you'll need `sudo`.

## journalctl — the systemd Journal

`journalctl` with no arguments dumps the whole journal oldest-first. The power is
in the filters, which compose:

**By boot** — every boot gets a unique ID:

```bash
journalctl --list-boots          # -1 prev, 0 current, with IDs and times
journalctl -b                    # this boot only
journalctl -b -1                 # the PREVIOUS boot (post-crash forensics)
journalctl -b <boot-id>          # a specific boot
```

**Kernel-only** (the journal's view of what `dmesg` shows, but persistent):

```bash
journalctl -k                    # kernel messages, this boot
journalctl -k -b -1              # kernel messages from the previous boot
```

**By priority** — syslog levels 0 (emerg) … 7 (debug):

```bash
journalctl -p err                # err and worse (0..3)
journalctl -p warning..err       # a range
```

**By unit and time:**

```bash
journalctl -u sshd               # one service
journalctl -u sshd -f            # follow it live
journalctl --since "2026-06-15 09:00" --until "2026-06-15 10:00"
journalctl --since "1 hour ago"
journalctl _PID=4412             # structured field: a specific process
journalctl -o json-pretty        # full structured output for tooling
```

## Persistence and Size

By default many distros keep the journal in `tmpfs` (`/run/log/journal`), so it
is lost on reboot — which is why `journalctl -b -1` may show nothing. Make it
persistent:

```bash
sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald
# or set Storage=persistent in /etc/systemd/journald.conf

journalctl --disk-usage          # how much space the journal uses
sudo journalctl --vacuum-time=2weeks
sudo journalctl --vacuum-size=500M
journalctl --verify              # integrity check
```

The kernel ring buffer size is separate, set at build time
(`CONFIG_LOG_BUF_SHIFT`) and tunable at boot with `log_buf_len=`. On a noisy box
it can wrap and lose early-boot driver messages — another reason to rely on the
persistent journal for forensics.

## Worked Example: Investigating an OOM Kill

```bash
journalctl -k -p err -b               # kernel errors this boot
journalctl -k --grep "Out of memory"  # find the OOM event (-g/--grep)
journalctl --since "10 min ago" -p warning
dmesg -T --level=err | tail           # quick live check, wall-clock time
```

Cross-reference: `dmesg` confirms the kernel killed the process *now*;
`journalctl -b -1 -k` tells you whether the *last* boot ended the same way.

## Common Mistakes

- **Trusting `dmesg` across reboots.** The ring buffer is volatile; for
  post-crash analysis you need the persistent journal (`journalctl -b -1`).
- **`journalctl -b -1` returns nothing** because journal storage is `volatile`.
  Enable persistent storage *before* you need the history.
- **Running `dmesg -c`** in a script — it clears the buffer for everyone,
  destroying messages other tools rely on. Use plain `dmesg`.
- **Ignoring `kernel.dmesg_restrict`** and concluding "no messages" when you
  simply lacked privilege. Try with `sudo`.

## Best Practices

- Set `Storage=persistent` on servers so kernel and service logs survive reboots.
- Bound journal growth with `SystemMaxUse=` / `--vacuum-*` so it can't fill the
  root disk.
- Prefer `journalctl -k` over `dmesg` when you need filtering, time ranges, or
  cross-boot history; keep `dmesg -T`/`-w` for fast live driver-level debugging.
- Pipe structured output (`-o json`) into your log shipper rather than scraping
  `/var/log/syslog` text.

## Quick Refs

```bash
# dmesg (kernel ring buffer, volatile)
dmesg -T                       # wall-clock timestamps
dmesg -w                       # follow live
dmesg --level=err,warn         # filter by level
dmesg -x                       # show facility + level

# journalctl (systemd journal)
journalctl -k                  # kernel messages
journalctl -b / -b -1          # this / previous boot
journalctl --list-boots
journalctl -u sshd -f          # follow a unit
journalctl -p err              # priority err and worse
journalctl --since "1 hour ago" --until now
journalctl -g "Out of memory"  # grep
journalctl --disk-usage
sudo journalctl --vacuum-time=2weeks
```

## Interview Prep

**Junior**: "How do you see kernel boot messages?"
- `dmesg` prints the kernel ring buffer; add `-T` for readable timestamps, `-w` to follow it live as new messages arrive.

**Mid**: "What's the difference between `dmesg` and `journalctl -k`?"
- Both show kernel messages, but `dmesg` reads the volatile in-memory ring buffer (lost on reboot), while `journalctl -k` reads the systemd journal, which can persist across boots and supports filtering by time, priority, and boot.

**Senior**: "A server rebooted unexpectedly overnight. How do you find out why?"
- `journalctl -b -1 -p err` and `journalctl -k -b -1` to read the previous boot's kernel and error logs for a panic, OOM, or hardware fault — provided journal storage is persistent; if it isn't, the evidence is gone and I'd enable it for next time.

**Staff**: "Logs from early boot keep disappearing before you can read them. Why, and what do you change?"
- The kernel ring buffer wrapped (too small for the message volume) and/or the journal is volatile — increase `log_buf_len`, set journald `Storage=persistent` with a bounded `SystemMaxUse`, and forward to a central log store so transient nodes' boot logs survive the node itself.

## Next Topic

→ [T04 — Kernel Upgrades](T04-Kernel-Upgrades.md)
