# L02/C09/T05 — CIS Hardening

## Learning Objectives

- Explain what the CIS Benchmarks are and how Level 1 vs Level 2 profiles differ
- Audit and remediate a host with OpenSCAP and Lynis
- Tie the chapter together into a repeatable "harden a fresh server" workflow

## What the CIS Benchmarks Are

The **Center for Internet Security (CIS)** publishes consensus-driven, prescriptive hardening guides — *Benchmarks* — for specific OS versions (Ubuntu 22.04, RHEL 9, etc.), and for Docker, Kubernetes, and cloud providers. Each benchmark is a numbered list of checks, every one with a rationale, an audit command, and a remediation step. Many organizations are contractually or regulatorily required to certify CIS Level 1 or Level 2 compliance, so this is the checklist auditors actually run against.

Two profiles set the bar:

| Profile | Intent | Trade-off |
|---|---|---|
| **Level 1** | sensible defaults, low operational friction | should not break normal use |
| **Level 2** | defense-in-depth for high-security environments | may disable features / reduce usability |

A complementary mapping, **STIG** (DISA Security Technical Implementation Guides), covers US government systems and overlaps heavily with CIS L2.

## Representative Controls

CIS benchmarks span the whole host. A flavor of what the checks look like:

| Area | Example control |
|---|---|
| Filesystem | separate partition for `/tmp`, `/var/log`; `nodev,nosuid,noexec` mount options |
| Modules | disable unused filesystems (`cramfs`, `udf`) and protocols (`dccp`, `sctp`) |
| Services | remove/disable `telnet`, `rsh`, `xinetd`, unused listeners |
| Network | `net.ipv4.ip_forward=0`, ignore ICMP redirects, enable SYN cookies |
| Auth | password aging, `pam_pwquality`, lockout (ties back to T01) |
| SSH | the `sshd_config` hardening from T03 |
| Logging | auditd rules + persistent journald (T04) |
| Permissions | correct mode/owner on `/etc/passwd`, `/etc/shadow`, cron files |

These aren't novel — they are exactly the topics in C01–C04 of this chapter, codified as a scored, auditable list.

A handful of sysctl hardening defaults that appear in nearly every benchmark:

```
# /etc/sysctl.d/60-cis.conf
net.ipv4.ip_forward = 0                       # not a router
net.ipv4.conf.all.accept_redirects = 0        # ignore ICMP redirects
net.ipv4.conf.all.send_redirects = 0
net.ipv4.tcp_syncookies = 1                   # SYN-flood resistance
net.ipv4.conf.all.rp_filter = 1               # reverse-path / anti-spoof
kernel.randomize_va_space = 2                 # full ASLR
fs.suid_dumpable = 0                          # no core dumps from setuid binaries
```

Apply with `sysctl --system`. Each line maps to a numbered CIS control, so a scanner can verify it and an auditor can trace it.

## Auditing with OpenSCAP

**OpenSCAP** is the reference implementation of SCAP (Security Content Automation Protocol). It evaluates a host against machine-readable policy content (`ssg`, the SCAP Security Guide) and can both **report** and **auto-remediate**.

```bash
# Install the scanner + content
dnf install -y openscap-scanner scap-security-guide   # RHEL family

# List available profiles in the content
oscap info /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml

# Audit against the CIS Level 1 profile -> HTML report
oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cis \
  --results scan.xml --report report.html \
  /usr/share/xml/scap/ssg/content/ssg-rhel9-ds.xml

# Generate a remediation script (review before running!)
oscap xccdf generate fix \
  --profile xccdf_org.ssgproject.content_profile_cis \
  --output remediate.sh scan.xml
```

OpenSCAP's superpower is automated remediation, but never run the generated fix blind — a control like "disable IP forwarding" will break a host that is meant to be a router or NAT gateway. Review, test in staging, then apply via configuration management.

## Auditing with Lynis

**Lynis** is a lighter, agentless shell-based auditor — great for a quick health check and for environments where installing SCAP content is overkill.

```bash
lynis audit system           # full audit, prints findings + a hardening index
lynis show details TEST-ID    # explain a specific finding
```

Lynis prints **warnings** and **suggestions** and a *hardening index* score (0–100). It doesn't remediate — it tells you what to fix and points at the relevant control. Use Lynis for fast feedback and OpenSCAP/SSG when you need formal, profile-mapped, auditor-grade reports.

| Tool | Strength | Remediates? |
|---|---|---|
| OpenSCAP + SSG | formal CIS/STIG profiles, machine-readable, auditor-grade | yes (generates fixes) |
| Lynis | fast, agentless, readable suggestions | no |

## Putting It Together: Harden a Fresh Server

The canonical interview question — "walk me through hardening a fresh Ubuntu box" — is just this chapter applied in order:

1. **Patch**: `apt update && apt full-upgrade`; enable unattended security updates.
2. **Accounts (T01)**: create a named admin, add to `sudo`, disable direct root, enforce password aging and `pam_faillock`.
3. **SSH (T03)**: keys only, `PermitRootLogin no`, `AllowGroups`, modern ciphers; validate with `sshd -t`.
4. **Firewall**: default-deny inbound (`ufw default deny incoming`), allow only required ports.
5. **MAC (T02)**: keep SELinux/AppArmor in enforcing mode; fix labels rather than disabling.
6. **Audit & logs (T04)**: install auditd with watch rules, make them immutable, ship logs off-box.
7. **Kernel/sysctl**: disable IP forwarding, enable SYN cookies, restrict `dmesg`/`ptrace`.
8. **Minimize**: remove unused packages and listeners; `nodev,nosuid,noexec` on `/tmp`.
9. **Verify (T05)**: run Lynis / OpenSCAP against CIS L1, remediate, re-scan, and bake the result into an image or Ansible/Packer pipeline so every new host starts hardened.

The last point is the staff-level insight: hardening a server by hand once is fine for a lab, but compliance at scale means the benchmark is enforced by automation (golden image + config management + CI scan), not a person running a checklist.

## Common Mistakes

- Running OpenSCAP's generated remediation blindly and breaking a router, NAT host, or a service that legitimately needs a "disabled" feature.
- Treating a Lynis hardening index of 100 as the goal regardless of whether the controls fit the workload.
- Hardening one server by hand and never encoding it, so the 50th host drifts.
- Applying Level 2 everywhere when Level 1 is the contractual requirement, causing needless breakage.
- Scanning once at build and never re-scanning for configuration drift.

## Best Practices

- Pick the right profile (usually L1) for the workload; reserve L2 for high-security tiers.
- Scan, review, remediate in staging, re-scan, then promote — never auto-fix production blind.
- Encode the hardened state in a golden image and config management (Ansible/Packer), not manual steps.
- Run a CIS scan in CI/CD and on a schedule to catch drift.
- Keep the benchmark version matched to the OS version; controls change between releases.

## Quick Refs

```bash
# OpenSCAP
oscap info ssg-rhel9-ds.xml
oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_cis \
  --results scan.xml --report report.html ssg-rhel9-ds.xml
oscap xccdf generate fix --profile ..._cis --output fix.sh scan.xml

# Lynis
lynis audit system
lynis show details TEST-ID

# Fresh-server essentials
apt full-upgrade
ufw default deny incoming && ufw allow OpenSSH && ufw enable
sysctl -w net.ipv4.ip_forward=0
```

## Interview Prep

**Junior**: "What is a CIS Benchmark?"
- A consensus, prescriptive hardening checklist published per OS, where each item has a rationale, an audit step, and a remediation step.

**Mid**: "Difference between CIS Level 1 and Level 2?"
- Level 1 is sensible low-friction hardening that shouldn't break normal use; Level 2 is deeper defense-in-depth for high-security environments and may disable features or reduce usability.

**Senior**: "How would you check and enforce CIS compliance on a fleet?"
- Scan with OpenSCAP against the SSG CIS profile for a report, review and stage the generated remediation, then bake the hardened state into a golden image plus Ansible and re-scan in CI to catch drift.

**Staff**: "Why is running OpenSCAP's auto-remediation in production risky, and what's the right pipeline?"
- A generic fix can disable a feature a host legitimately needs (e.g. IP forwarding on a NAT gateway), so you scan, review per-control, remediate and test in staging, and promote via config-managed golden images with a scheduled CI scan rather than mutating live hosts.

## Next Chapter

→ Move to [L02/C10 — Boot & Kernel](../C10/README.md)
