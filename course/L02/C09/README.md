# L02/C09 — Linux Security

## Chapter Overview

Defense in depth for Linux servers. Every layer matters; staff engineers can articulate the threat model at each.

## Topics

| Topic | Title | Hours |
|---|---|---|
| [T01](T01-Users-Sudo-PAM.md) | Users, Groups, sudo, PAM | 1 hr |
| [T02](T02-SELinux-AppArmor.md) | SELinux & AppArmor (Mandatory Access Control) | 1.5 hr |
| [T03](T03-SSH-Hardening.md) | SSH Hardening (Keys, Bastion, Certificates) | 1 hr |
| [T04](T04-Auditd-Logging.md) | auditd, Logging, and File Integrity | 1 hr |
| [T05](T05-CIS-Hardening.md) | Common Hardening Checklist (CIS Benchmark) | 0.5 hr |

## Key Concepts

### Users, sudo, PAM
- `/etc/passwd`, `/etc/shadow`, `/etc/group`, `/etc/gshadow`
- `useradd`, `usermod`, `passwd`
- sudo via `/etc/sudoers` (use `visudo`)
- PAM stack at `/etc/pam.d/*` (auth, account, password, session)

### SELinux vs AppArmor
| | SELinux | AppArmor |
|---|---|---|
| Approach | Type enforcement | Path-based profiles |
| Granularity | Very fine | Coarser |
| Complexity | High | Moderate |
| Distros | RHEL family | Ubuntu, SUSE |
| Failure mode | "It works on disabled SELinux" | Easier to author |

```bash
getenforce             # SELinux: Enforcing/Permissive/Disabled
sestatus
ausearch -m AVC        # SELinux denials
audit2allow            # generate policy from denials

aa-status              # AppArmor status
aa-enforce profile     # set enforce
aa-complain profile    # set learn mode
```

### SSH Hardening Checklist

```
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
ChallengeResponseAuthentication no
UsePAM yes
AllowGroups ssh-users
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
PermitEmptyPasswords no
X11Forwarding no
AllowTcpForwarding no       # if not used
LoginGraceTime 30
Banner /etc/issue.net
```

Additional:
- SSH certificates (signed by CA) > raw keys for fleets
- Bastion / jump hosts with hardware MFA
- Fail2ban or sshguard for brute-force defense
- Audit ssh logins via `/var/log/auth.log` or journald

### auditd
The kernel audit subsystem. Logs syscalls per rules.

```bash
# /etc/audit/rules.d/audit.rules
-w /etc/passwd -p wa -k passwd_changes
-w /etc/shadow -p wa -k shadow_changes
-a always,exit -F arch=b64 -S execve -k all_execs

ausearch -k passwd_changes
aureport -au
```

### File Integrity
- AIDE (Advanced Intrusion Detection Environment)
- Tripwire (commercial)
- OSSEC

### CIS Benchmark
Center for Internet Security publishes hardened-config benchmarks per OS. Many companies require CIS Level 1 or 2 compliance. Tools:
- Lynis (audit)
- OpenSCAP (audit + auto-remediation)

## Container-Era Hardening

- Drop all capabilities, add only needed
- `readOnlyRootFilesystem: true` in K8s
- Seccomp profile (`RuntimeDefault` minimum)
- `runAsNonRoot: true`, `runAsUser: 1000` (or higher)
- Image scanning (Trivy, Grype)
- Signed images (Cosign)

Covered deeper in L20.

## Interview Themes

- "Walk me through hardening a fresh Ubuntu server."
- "SELinux is in enforcing mode and breaking my app. What now?"
- "Compare SSH key auth vs SSH certificate auth at fleet scale."
- "What audit rules would you enable on a production database server?"
