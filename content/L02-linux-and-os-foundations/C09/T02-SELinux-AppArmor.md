# L02/C09/T02 — SELinux & AppArmor

## Learning Objectives

- Explain Mandatory Access Control (MAC) and how it differs from the DAC permission bits
- Operate SELinux: modes, contexts, booleans, and turning a denial into a policy module
- Operate AppArmor: profiles, enforce vs complain mode, and where its model differs from SELinux

## DAC vs MAC

Standard Unix permissions are **Discretionary** Access Control (DAC): the *owner* of a file decides who can read it, and root bypasses everything. MAC adds a second gate the owner cannot relax — a system-wide policy that constrains even root. A web server running as root can still be blocked by policy from reading `/etc/shadow` if its type isn't allowed to. MAC is what contains a compromised daemon: the attacker gets the daemon's confinement, not the run-as user's full power.

Two implementations dominate, and the distro usually picks for you:

| | SELinux | AppArmor |
|---|---|---|
| Model | Type Enforcement (labels) | Path-based profiles |
| Granularity | Very fine | Coarser |
| Complexity | High | Moderate |
| Default on | RHEL / Fedora / CentOS | Ubuntu / Debian / SUSE |
| Failure mode | "Just disable SELinux" (don't) | Easier to author |

## SELinux: Modes

SELinux runs in one of three modes:

| Mode | Behavior |
|---|---|
| `Enforcing` | policy denials are blocked **and** logged |
| `Permissive` | denials are **logged but allowed** — the debugging mode |
| `Disabled` | subsystem off; requires reboot to re-enable with relabel |

```bash
getenforce                 # current mode
sestatus                   # mode + policy + mount status
setenforce 0               # -> Permissive (runtime, not persistent)
setenforce 1               # -> Enforcing
```

Persist the mode in `/etc/selinux/config` (`SELINUX=enforcing`). Never reach for `Disabled` to fix a bug — drop to `Permissive`, collect the denials, fix policy, then return to `Enforcing`.

## SELinux: Contexts (Labels)

Every process, file, port, and socket carries a **security context**:

```
user:role:type:level
system_u:object_r:httpd_sys_content_t:s0
```

Type Enforcement is almost entirely about the **type** field (the `_t`). A process of type `httpd_t` may only touch files whose type the policy permits (e.g. `httpd_sys_content_t`). View and set labels with the `Z` flag:

```bash
ls -Z /var/www/html        # file contexts
ps -eZ | grep nginx        # process contexts
id -Z                      # your context
```

The classic failure: you move content into a non-standard directory and the type is wrong, so the daemon is denied.

```bash
# Persistently teach the policy that /srv/web is web content...
semanage fcontext -a -t httpd_sys_content_t "/srv/web(/.*)?"
restorecon -Rv /srv/web    # ...then apply the label to the files

# Allow a service on a non-standard port
semanage port -a -t http_port_t -p tcp 8443
```

`restorecon` resets a file to its policy-defined label; `chcon` sets one temporarily (lost on relabel). Prefer `semanage fcontext` + `restorecon` so it survives.

## SELinux: Booleans

Booleans are policy switches that toggle whole behaviors without writing new policy:

```bash
getsebool -a | grep httpd            # list httpd-related toggles
setsebool -P httpd_can_network_connect on   # -P = persist across reboot
```

`httpd_can_network_connect`, `httpd_can_network_connect_db`, and `nfs_export_all_rw` are common ones you flip to let a confined service reach out.

## SELinux: From Denial to Policy

When something breaks under `Enforcing`, the kernel logs an **AVC** (Access Vector Cache) denial. The workflow:

```bash
ausearch -m AVC -ts recent           # recent denials
ausearch -m AVC -ts today | audit2allow -m myapp   # human-readable module
ausearch -m AVC -ts today | audit2allow -M myapp   # build .pp + .te files
semodule -i myapp.pp                 # install the generated module
sealert -a /var/log/audit/audit.log  # setroubleshoot's plain-English advice
```

`audit2allow` is powerful and dangerous: it will happily generate a rule that re-allows exactly what an exploit was attempting. Read the `.te` it produces and grant the *minimum* needed — don't blanket-allow.

## AppArmor: Profiles

AppArmor confines programs by **path**. A profile lists the files a binary may read/write/execute and the capabilities it may use. Profiles live in `/etc/apparmor.d/`, named after the binary path with slashes turned to dots (`usr.sbin.nginx`).

```
# /etc/apparmor.d/usr.sbin.nginx (excerpt)
#include <tunables/global>
/usr/sbin/nginx {
  #include <abstractions/base>
  capability net_bind_service,
  /var/www/html/** r,
  /var/log/nginx/*.log w,
  /etc/nginx/** r,
  deny /etc/shadow rwklx,
}
```

Each profile is in one of two states:

| Mode | Behavior |
|---|---|
| `enforce` | violations blocked and logged |
| `complain` | violations logged only (learning mode) |

```bash
aa-status                            # which profiles loaded, in which mode
aa-complain /usr/sbin/nginx          # set learning mode
aa-enforce  /usr/sbin/nginx          # set enforce
aa-logprof                           # interactively build rules from logged events
apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx   # reload one profile
```

The path-based model is easier to read than SELinux labels but is weaker against tricks like hard links and bind mounts that present the same inode under a different path — SELinux labels the inode, AppArmor watches the path.

## Common Mistakes

- Setting SELinux to `Disabled` to "fix" an app instead of `Permissive` + `audit2allow`.
- Using `chcon` for a permanent fix — the next `restorecon`/relabel reverts it; use `semanage fcontext`.
- Blindly piping every denial through `audit2allow -M` and installing it, re-permitting the exact exploit.
- Forgetting `-P` on `setsebool`, so the change vanishes on reboot.
- Assuming AppArmor `complain` mode protects anything — it only logs.

## Best Practices

- Keep MAC in enforcing mode in production; treat permissive as a temporary debugging window.
- Fix label problems with `semanage fcontext` + `restorecon`, not `chcon`.
- Prefer a boolean over a custom module when one exists.
- Author/extend AppArmor profiles in `complain` first, harvest with `aa-logprof`, then `aa-enforce`.
- Review any `audit2allow` output line by line; grant least privilege.

## Quick Refs

```bash
# SELinux
getenforce; sestatus
setenforce 0|1                       # runtime mode
ls -Z / ps -eZ                       # contexts
semanage fcontext -a -t TYPE "PATH(/.*)?" && restorecon -Rv PATH
semanage port -a -t http_port_t -p tcp 8443
getsebool -a | grep svc; setsebool -P bool on
ausearch -m AVC -ts recent | audit2allow -M mymod && semodule -i mymod.pp

# AppArmor
aa-status
aa-complain /path/to/bin
aa-enforce  /path/to/bin
aa-logprof
apparmor_parser -r /etc/apparmor.d/profile
```

## Interview Prep

**Junior**: "What's the difference between file permissions and SELinux?"
- Permissions are discretionary (the owner and root decide); SELinux is a system-wide mandatory policy that even root can't override.

**Mid**: "SELinux is blocking my web app from reading files in `/srv`. How do you fix it properly?"
- Relabel the path to the right type with `semanage fcontext -a -t httpd_sys_content_t '/srv(/.*)?'` then `restorecon -Rv /srv`, rather than disabling SELinux.

**Senior**: "An app breaks under enforcing mode. Walk me through diagnosing without turning SELinux off."
- Switch to `Permissive`, reproduce, collect AVCs with `ausearch -m AVC`, generate a candidate module with `audit2allow`, review the `.te` for least privilege, install with `semodule -i`, then return to `Enforcing`.

**Staff**: "Compare SELinux type enforcement to AppArmor path profiles for confining a fleet of microservices."
- SELinux labels inodes so it resists hardlink/bind-mount path tricks and gives finer port/socket control, at the cost of steep policy authoring; AppArmor's path profiles are faster to write and audit but weaker against path-aliasing attacks — choose by distro standardization and the threat model you're defending.

## Next Topic

→ [T03 — SSH Hardening](T03-SSH-Hardening.md)
