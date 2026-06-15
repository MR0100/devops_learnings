# L02/C09/T04 — auditd & Logging

## Learning Objectives

- Explain what the kernel audit subsystem records and how `auditd` consumes it
- Write watch and syscall rules, then query them with `ausearch` and `aureport`
- Combine auditd, journald, and file-integrity tooling into a tamper-evident logging story

## What auditd Is

`auditd` is the userspace daemon for the **Linux kernel audit subsystem**. The kernel can emit an audit event whenever a process makes a syscall or touches a watched file; `auditd` writes those events to `/var/log/audit/audit.log`. It is distinct from syslog/journald: auditd answers "*who* did *what* to *which* object, and was it allowed," at the syscall boundary, which is exactly what compliance frameworks (PCI-DSS, CIS, STIG) require.

Two record sources feed it:
- **File watches** — alert when a path is read/written/executed/has attributes changed.
- **Syscall rules** — alert when a matching syscall is made (optionally filtered by user, arch, success).

## Rules: Watches and Syscalls

Rules live in `/etc/audit/rules.d/*.rules`, which `augenrules` compiles into the active set at boot. You can also load rules at runtime with `auditctl`.

```
# /etc/audit/rules.d/hardening.rules

# --- File watches:  -w PATH -p PERMS -k KEY ---
-w /etc/passwd  -p wa -k identity        # w=write, a=attr change
-w /etc/shadow  -p wa -k identity
-w /etc/sudoers -p wa -k scope
-w /etc/ssh/sshd_config -p wa -k sshd_config
-w /var/log/audit/ -p wa -k auditlog      # watch the audit log itself

# --- Syscall rules:  -a action,filter -F fields -S syscall -k KEY ---
-a always,exit -F arch=b64 -S execve -k exec        # every program execution
-a always,exit -F arch=b64 -S unlink -S rename -k delete
-a always,exit -F arch=b64 -F euid=0 -S mount -k root_mount

# --- Lock the config (must be LAST) ---
-e 2
```

| Token | Meaning |
|---|---|
| `-w PATH` | watch a file or directory |
| `-p rwxa` | trigger on read / write / execute / attribute change |
| `-k KEY` | a searchable tag for this rule |
| `-a always,exit` | log on syscall exit |
| `-F arch=b64` | filter to 64-bit syscalls (do `b32` too for full coverage) |
| `-F euid=0` | only when effective UID is root |
| `-S execve` | the syscall to match |
| `-e 2` | make the rule set **immutable until reboot** |

`-e 2` is the integrity capstone: once set, rules cannot be changed without a reboot, so an attacker who roots the box cannot quietly delete the rule watching their tracks. Always place it last.

```bash
auditctl -l        # list active rules
auditctl -s        # status (enabled, backlog, lost events)
augenrules --load  # compile rules.d/ and load
```

## Querying: ausearch and aureport

Raw `audit.log` is dense (`type=SYSCALL ... a0=... key="identity"`). Two tools make it usable.

**`ausearch`** finds events by key, user, time, or syscall and resolves numeric IDs to names:

```bash
ausearch -k identity                     # everything tagged "identity"
ausearch -k exec -ts today               # executions since midnight
ausearch -ua deploy -ts recent           # actions by audit-uid deploy
ausearch -m AVC                          # SELinux denials (see T02)
ausearch -i -k sudoers                   # -i interprets IDs to names
```

**`aureport`** summarizes:

```bash
aureport -au               # authentication report (success/fail)
aureport -l               # login report
aureport -f               # file access report
aureport -x --summary      # executable summary (what ran, how often)
aureport --failed          # all failed events
```

The `auid` (audit/login UID) is the key forensic field: it is the **original** login identity, preserved across `su`/`sudo`. So even after a user becomes root, `ausearch -ua alice` still attributes the action to Alice — that's why audit beats plain process UID for accountability.

## journald and Log Shipping

`auditd` covers syscalls; **journald** (`systemd-journald`) captures everything else — service stdout/stderr, kernel messages, login events.

```bash
journalctl -u nginx --since "1 hour ago"
journalctl -p err -b              # errors this boot
journalctl _UID=1001              # everything by UID 1001
journalctl -f                     # follow (tail)
```

Local logs are not enough — an attacker who gains root can edit or wipe them. Hardening the logging story:
- **Forward off-box**: ship to a central collector (rsyslog `@@host`, journald `ForwardToSyslog`, or an agent like Vector/Fluent Bit) so a compromised host can't erase the only copy.
- **Persist the journal**: set `Storage=persistent` in `/etc/systemd/journald.conf` and cap with `SystemMaxUse=`.
- **Watch the audit log itself** (`-w /var/log/audit/`) so tampering is recorded.

## File Integrity Monitoring

FIM detects unauthorized changes to system files by comparing against a known-good baseline.

| Tool | Notes |
|---|---|
| **AIDE** | Advanced Intrusion Detection Environment; open source, cron-driven baseline diffs |
| **Tripwire** | mature, commercial edition available |
| **OSSEC** | host IDS with real-time FIM + active response |

```bash
aideinit                          # build the baseline DB
aide --check                      # diff filesystem vs baseline
aide --update                     # accept current state as new baseline
```

Store the AIDE database and its config off-host (or read-only) — otherwise an attacker just rebaselines after planting their changes. FIM and auditd are complementary: auditd tells you *the moment* a watched file changed and *who*; AIDE catches anything that slipped through by periodic full comparison.

## Common Mistakes

- Forgetting `-e 2`, so rules can be silently removed after a compromise.
- Auditing `execve` on a busy host without thought — huge log volume and lost events; size the backlog (`-b`) and ship logs.
- Only adding `b64` syscall rules, missing 32-bit syscalls on a multilib host.
- Keeping logs and the AIDE baseline only on the same box that they're meant to protect.
- Confusing process UID with `auid` — `su -` hides identity unless you query the audit UID.

## Best Practices

- Watch the high-value files: `passwd`, `shadow`, `sudoers`, `sshd_config`, and `/etc/audit` itself.
- Tag every rule with a `-k` key so `ausearch -k` is fast and consistent.
- Make rules immutable with `-e 2` after loading.
- Forward auditd and journald to a central, append-only store immediately.
- Run AIDE on a schedule with its database kept read-only/off-host.
- Monitor `auditctl -s` for lost events and tune the backlog limit.

## Quick Refs

```bash
# Rules
auditctl -l                       # list active rules
auditctl -s                       # status / lost events
augenrules --load                 # load /etc/audit/rules.d/
-w /etc/shadow -p wa -k identity  # file watch (in rules file)
-a always,exit -F arch=b64 -S execve -k exec   # syscall rule

# Search & report
ausearch -k identity -i
ausearch -ua alice -ts today
aureport -au                      # auth report
aureport -x --summary             # what executed

# journald
journalctl -u sshd --since today
journalctl -p err -b

# File integrity
aide --check
```

## Interview Prep

**Junior**: "What does auditd do that journald doesn't?"
- auditd records syscall-level events ("who touched `/etc/shadow` and was it allowed"), giving the accountability trail compliance frameworks require; journald captures service and system messages.

**Mid**: "How would you detect any change to `/etc/sudoers`?"
- Add `-w /etc/sudoers -p wa -k scope` to `/etc/audit/rules.d/` and query with `ausearch -k scope`; pair with AIDE for periodic baseline diffs.

**Senior**: "Why is `auid` more useful than the process UID in a breach investigation?"
- `auid` is the original login identity preserved across `su`/`sudo`, so an action stays attributed to the human even after they escalate to root, whereas process UID just shows `0`.

**Staff**: "Design an audit pipeline that an attacker with root can't cover up."
- Make audit rules immutable with `-e 2`, watch the audit log directory itself, ship auditd and journald in real time to an append-only/WORM central store off the host, and keep the AIDE baseline read-only and external so local tampering is both prevented and independently detectable.

## Next Topic

→ [T05 — CIS Hardening](T05-CIS-Hardening.md)
