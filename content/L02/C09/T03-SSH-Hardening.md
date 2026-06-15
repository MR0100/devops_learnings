# L02/C09/T03 — SSH Hardening

## Learning Objectives

- Harden `sshd_config` with the directives that actually reduce attack surface
- Explain why SSH certificates beat raw public keys at fleet scale
- Design a bastion/jump-host topology with brute-force defenses and audit logging

## The Threat Model

SSH is the front door to almost every Linux server, so it is the most-probed service on the internet. Within minutes of exposing port 22, automated bots are trying `root`/`admin` with dictionary passwords. Hardening SSH means: kill password auth, kill root login, restrict who may connect, slow down brute force, and make every login auditable.

## sshd_config — The Core Directives

Server config is `/etc/ssh/sshd_config` (client config is `ssh_config` — different file). Edit, validate with `sshd -t`, then reload.

```
# /etc/ssh/sshd_config
PermitRootLogin no                 # never log in as root directly
PasswordAuthentication no          # keys only
PubkeyAuthentication yes
KbdInteractiveAuthentication no    # (older: ChallengeResponseAuthentication no)
UsePAM yes                         # keep PAM for account/session checks
PermitEmptyPasswords no
AllowGroups ssh-users              # only members of this group may connect
MaxAuthTries 3                     # disconnect after 3 failed attempts
MaxSessions 4
LoginGraceTime 30                  # seconds to authenticate before drop
ClientAliveInterval 300            # probe idle clients
ClientAliveCountMax 2              # drop after 2 missed probes (~10 min idle)
X11Forwarding no
AllowTcpForwarding no              # disable if you don't tunnel
AllowAgentForwarding no
Banner /etc/issue.net
```

| Directive | Why it matters |
|---|---|
| `PermitRootLogin no` | forces a named account + sudo, preserving audit trail |
| `PasswordAuthentication no` | eliminates the entire brute-force-the-password class |
| `AllowGroups` / `AllowUsers` | default-deny: only listed principals connect |
| `MaxAuthTries 3` | limits guesses per connection |
| `LoginGraceTime 30` | shrinks the pre-auth window (where many CVEs live) |
| `ClientAlive*` | reaps dead/idle sessions |

Apply and verify safely:

```bash
sshd -t                            # syntax check — DO THIS before reload
systemctl reload sshd              # reload without dropping existing sessions
```

Always keep your current session open and test a **new** connection before logging out. A bad config that you `restart` into can lock you out of the box.

### Crypto Hygiene

Pin modern algorithms and drop legacy ones:

```
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com
HostKeyAlgorithms ssh-ed25519,rsa-sha2-512
```

For user keys, prefer `ssh-keygen -t ed25519` (small, fast, no weak-parameter risk) over RSA-2048.

## Keys vs Certificates at Fleet Scale

Raw public keys do not scale. Every server needs every authorized user's key in `~/.ssh/authorized_keys`; revoking one person means editing every host. **SSH certificates** fix this. You stand up an SSH Certificate Authority (a keypair kept offline/in an HSM), the CA signs short-lived user certificates, and each host trusts only the CA:

```bash
# One-time on each host: trust the CA for user logins
echo "TrustedUserCAKeys /etc/ssh/ca_user.pub" >> /etc/ssh/sshd_config

# CA signs a user's key: principals + 8-hour validity
ssh-keygen -s ca_user -I "alice@2026-06-15" \
  -n alice,deploy -V +8h alice_ed25519.pub
```

| | Raw keys | Certificates |
|---|---|---|
| Onboarding | copy key to every host | host already trusts the CA |
| Revocation | edit every `authorized_keys` | expire the cert / KRL the CA-signed serial |
| Validity | forever (until removed) | short TTL (hours) |
| Principals | implicit per file | embedded, signed |

Hosts can also present **host certificates** (signed by a host CA) so clients stop blindly accepting `known_hosts` fingerprints — eliminating trust-on-first-use.

## Bastion / Jump Hosts

Don't expose every server's port 22. Expose **one** hardened bastion; everything else is reachable only through it.

```
# ~/.ssh/config on the operator's laptop
Host bastion
    HostName bastion.example.com
    User alice
    IdentityFile ~/.ssh/id_ed25519

Host app-*
    ProxyJump bastion
    User deploy
```

`ssh app-web01` now transparently hops through the bastion. The bastion should require hardware MFA (FIDO2/YubiKey via `ssh-keygen -t ed25519-sk`), forward nothing it doesn't need, and log every session. Internal hosts firewall port 22 to accept only the bastion's address.

## Brute-Force Defense and Audit

Even key-only, you want to throttle scanners and record logins:

```bash
# fail2ban: ban IPs after repeated failures (jail.local)
[sshd]
enabled  = true
maxretry = 4
findtime = 600
bantime  = 3600

# Where SSH logins are recorded:
grep sshd /var/log/auth.log           # Debian/Ubuntu
journalctl -u ssh -t sshd             # systemd journal
journalctl _COMM=sshd | grep "Accepted"   # successful logins
```

`fail2ban` (or `sshguard`) reads the auth log and inserts firewall drops for offending IPs. Pair this with auditd (next topic) so privileged sessions are recorded at the syscall level, not just connection level.

## Common Mistakes

- `restart`ing sshd into a broken config with no second session open — instant lockout.
- Leaving `PasswordAuthentication yes` "just for emergencies" — that's the brute-force surface.
- Distributing raw keys to a 500-host fleet and having no revocation story.
- Forgetting to also restrict `AllowGroups`, so any account with a key can log in.
- Exposing port 22 on every host instead of funneling through a bastion.

## Best Practices

- Keys (ed25519) only; disable passwords and root login entirely.
- Default-deny with `AllowGroups`/`AllowUsers`.
- Move to short-lived SSH certificates with a CA once past a handful of hosts.
- Funnel access through an MFA-protected bastion; firewall internal SSH to the bastion.
- Run `sshd -t` before every reload, keep a session open, and test a fresh login.
- Ship `auth.log`/journald to a central, tamper-evident store and run fail2ban.

## Quick Refs

```bash
# Validate & reload (never blind-restart)
sshd -t
systemctl reload sshd

# Keys
ssh-keygen -t ed25519 -C "alice@laptop"
ssh-keygen -t ed25519-sk            # hardware-backed (FIDO2)
ssh-copy-id -i ~/.ssh/id_ed25519.pub deploy@host

# Certificates
ssh-keygen -s ca_user -I alice -n alice,deploy -V +8h alice.pub
ssh-keygen -L -f alice-cert.pub     # inspect a cert

# Bastion
ssh -J bastion.example.com deploy@app-web01

# Audit
journalctl -u ssh | grep Accepted
fail2ban-client status sshd
```

## Interview Prep

**Junior**: "Why disable password authentication on SSH?"
- It removes the entire brute-force-the-password attack class; keys are far harder to guess and bots can't dictionary-attack them.

**Mid**: "What does `PermitRootLogin no` buy you?"
- It forces operators onto named accounts with sudo, so every privileged action is attributable instead of an anonymous shared root login.

**Senior**: "Compare SSH key auth vs certificate auth for a 500-host fleet."
- Raw keys require touching every `authorized_keys` to onboard or revoke; certificates make each host trust one CA, so you issue short-lived signed certs and revoke by expiry or KRL without editing any host.

**Staff**: "Design SSH access for a regulated environment with no standing access."
- Operators authenticate to an MFA bastion, request a just-in-time CA-signed certificate with embedded principals and an hour TTL, jump to internal hosts (which firewall 22 to the bastion and trust only the host/user CA), and every session is recorded via auditd shipped to immutable storage.

## Next Topic

→ [T04 — auditd & Logging](T04-Auditd-Logging.md)
