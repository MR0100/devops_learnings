# L02/C09/T01 — Users, sudo, PAM

## Learning Objectives

- Map the local account databases (`passwd`, `shadow`, `group`, `gshadow`) and how they interlock
- Author safe `sudo` policy via `visudo` and understand privilege escalation risk
- Read and modify the PAM stack (`auth`, `account`, `password`, `session`) without locking yourself out

## The Account Databases

Local identity on a Linux host lives in four world-readable-or-not files. They are flat, colon-delimited, and edited by tools — almost never by hand.

| File | Mode | Holds | Key columns |
|---|---|---|---|
| `/etc/passwd` | `644` | account record | name, UID, GID, GECOS, home, shell |
| `/etc/shadow` | `640` (root:shadow) | password hashes + aging | name, hash, last-change, min, max, warn |
| `/etc/group` | `644` | group memberships | name, GID, member list |
| `/etc/gshadow` | `640` | group passwords + admins | name, hash, admins, members |

A `passwd` line:

```
deploy:x:1001:1001:Deploy User:/home/deploy:/bin/bash
```

The `x` in field 2 means "the real hash lives in `/etc/shadow`." A shadow line:

```
deploy:$6$rounds=5000$abc...:19700:0:90:7:::
```

`$6$` is the SHA-512 crypt scheme (`$y$` is yescrypt on newer distros). The numeric fields are days-since-epoch of last change, min age, **max age (90)**, and a 7-day expiry warning. A `!` or `*` in the hash field means the account cannot authenticate by password (it may still log in by key).

## Managing Accounts

```bash
useradd -m -s /bin/bash -G sudo,docker deploy   # create + home + supplementary groups
passwd deploy                                   # set/reset password
usermod -aG wheel deploy                         # APPEND group (omit -a and you replace!)
chage -l deploy                                  # view password aging
chage -M 90 -W 7 deploy                          # enforce 90-day max, 7-day warn
userdel -r olduser                               # remove + home
```

The single most common foot-gun: `usermod -G docker deploy` **replaces** every supplementary group instead of adding one. Always use `-aG`.

UID conventions matter for security: `0` is root, `1–999` are system/service accounts, `1000+` are humans. Service accounts should have `/usr/sbin/nologin` as their shell so a compromised daemon cannot drop to an interactive shell.

## sudo and `/etc/sudoers`

`sudo` consults `/etc/sudoers` and the drop-in directory `/etc/sudoers.d/`. **Never** open these with a plain editor — use `visudo`, which syntax-checks before saving and refuses to write a broken file that would lock out all privilege escalation.

```
# /etc/sudoers
# user  host = (runas) commands
root    ALL=(ALL:ALL) ALL
%sudo   ALL=(ALL:ALL) ALL          # Debian/Ubuntu: members of group "sudo"
%wheel  ALL=(ALL)     ALL          # RHEL family: group "wheel"
```

A scoped, production-friendly rule grants only what an operator needs:

```
# /etc/sudoers.d/deploy   (validate with: visudo -cf /etc/sudoers.d/deploy)
Cmnd_Alias SVC = /bin/systemctl restart app, /bin/systemctl status app
deploy  ALL=(root) NOPASSWD: SVC
Defaults:deploy  log_output, !syslog
Defaults  logfile=/var/log/sudo.log, lecture=once
```

Key directives:

| Directive | Effect |
|---|---|
| `NOPASSWD:` | skip the password prompt (use sparingly — convenient but weakens auth) |
| `Cmnd_Alias` | named set of commands for reuse |
| `Defaults requiretty` | refuse sudo without a real TTY (blocks some script abuse) |
| `Defaults timestamp_timeout=5` | minutes the auth ticket is cached |
| `Defaults log_output` | record stdout/stderr of sudo sessions (I/O logging) |

Avoid `ALL` in the command field for non-admins, and never grant a command that can shell out (`vim`, `less`, `find -exec`, `tar --to-command`) — those are trivial privilege-escalation gadgets even when "scoped."

## PAM — Pluggable Authentication Modules

PAM decouples *how* a program authenticates from the program itself. `login`, `sshd`, `sudo`, and `cron` all call into PAM rather than reading `/etc/shadow` directly. Config lives in `/etc/pam.d/<service>`, one file per service, plus shared fragments like `common-auth` (Debian) or `system-auth` (RHEL).

A PAM rule has four columns:

```
type     control      module          arguments
auth     required     pam_unix.so      try_first_pass
```

The four **types** (management groups), run in order:

| Type | Question it answers |
|---|---|
| `auth` | Is the user who they claim? (passwords, keys, OTP) |
| `account` | Is the account allowed right now? (expiry, time, host) |
| `password` | How are credentials changed? (complexity rules) |
| `session` | What to set up/tear down per login? (limits, mounts, logging) |

The **control** field decides flow:

| Control | Meaning |
|---|---|
| `required` | must pass; failure remembered but stack continues (no leak of which step failed) |
| `requisite` | must pass; failure returns *immediately* |
| `sufficient` | success short-circuits the rest of that type (if no prior `required` failed) |
| `optional` | result ignored unless it is the only module |

A hardened `auth` stack with lockout and a one-time push factor:

```
# /etc/pam.d/sshd  (excerpt)
auth     required   pam_faillock.so preauth  deny=5 unlock_time=900
auth     [success=1 default=bad]  pam_unix.so try_first_pass
auth     [default=die]  pam_faillock.so authfail deny=5 unlock_time=900
auth     required   pam_google_authenticator.so nullok
account  required   pam_faillock.so
session  required   pam_limits.so
```

Useful modules: `pam_unix` (shadow auth), `pam_faillock` / `pam_tally2` (brute-force lockout), `pam_pwquality` (password complexity), `pam_limits` (ties into `/etc/security/limits.conf`), `pam_access` (host/user allow rules), `pam_exec` (run a script — e.g. send a login alert).

**Test PAM changes in a second session.** Keep one root shell open, edit in another, and verify a fresh login works before closing the safety session. A bad `common-auth` line can lock out every account on the box.

## Common Mistakes

- Editing `/etc/sudoers` with `vi` directly and saving a syntax error — escalation is now broken for everyone. Always `visudo`.
- `usermod -G` without `-a`, wiping a user out of `docker`/`sudo`.
- Granting `NOPASSWD: ALL` "temporarily" and never removing it.
- Allowing sudo to an editor or pager — instant root shell via `:!sh`.
- Editing PAM over your only SSH session with no fallback root shell open.

## Best Practices

- One human = one named account; no shared logins. Audit trails depend on identity.
- Service accounts get `nologin` shells and no password.
- Scope sudo to specific commands; prefer group-based rules (`%wheel`) over per-user.
- Enable `pam_faillock` for lockout and `pam_pwquality` for complexity.
- Enforce password aging with `chage`, and rotate or disable departing users immediately (`usermod -L`, `chage -E 0`).

## Quick Refs

```bash
# Accounts
useradd -m -s /bin/bash -G sudo deploy
usermod -aG docker deploy        # APPEND, never -G alone
chage -M 90 -W 7 deploy          # password aging
usermod -L deploy                # lock; -U to unlock

# sudo
visudo                           # edit /etc/sudoers safely
visudo -cf /etc/sudoers.d/app    # check a drop-in
sudo -l -U deploy                # what can deploy run?

# PAM
ls /etc/pam.d/                   # per-service stacks
faillock --user deploy           # view lockout counters
faillock --user deploy --reset   # clear them
```

## Interview Prep

**Junior**: "Where are Linux password hashes stored?"
- In `/etc/shadow` (mode `640`, root-owned), not `/etc/passwd`; the `x` in passwd just points there.

**Mid**: "Why use `visudo` instead of editing `/etc/sudoers`?"
- It syntax-checks before saving and locks the file, so a typo can't leave the box with no working privilege escalation.

**Senior**: "Why is granting `sudo vim` to an operator dangerous if you only wanted them to edit one config?"
- Editors can shell out (`:!sh`) as root, so command-scoped sudo to any program that spawns a shell is effectively `sudo ALL`.

**Staff**: "Design a login path that survives a compromised SSH daemon credential leak."
- Layer `auth` with `pam_faillock` lockout plus a second factor (`pam_google_authenticator`/hardware OTP), enforce key-only via sshd, and log every session with `pam_exec` and sudo I/O logging so a leaked secret alone is insufficient and is detectable.

## Next Topic

→ [T02 — SELinux & AppArmor](T02-SELinux-AppArmor.md)
