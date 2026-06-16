# L02/C10/T04 — Kernel Upgrades

## Learning Objectives

- Upgrade the kernel safely, keeping a known-good fallback to revert to
- Explain why most kernel changes require a reboot and how to coordinate that at scale
- Describe live patching (kpatch / Ksplice / Livepatch) and its hard limits
- Choose between stable, LTS, and HWE kernels for a given workload

## The Big Picture

The kernel is the one piece of software you cannot replace without (usually)
rebooting — it *is* the running machine. A kernel upgrade therefore couples a
package operation with a reboot-coordination problem, and at fleet scale the
reboot is the hard part, not the `apt`/`dnf` command.

```
Install new kernel pkg ──► new vmlinuz + initramfs in /boot
        │                  GRUB entry added; OLD kernel kept
        ▼
   Reboot into new kernel  ◄── revert here if it fails: pick old entry in GRUB
        │
        ▼
   uname -r confirms; remove old kernels later
```

The golden rule: **install adds a kernel, it does not remove the old one.** That
old entry in the GRUB menu is your rollback path.

## Performing the Upgrade

```bash
# Debian/Ubuntu
sudo apt update && sudo apt install --only-upgrade linux-image-generic
# or the meta-package that tracks the recommended kernel:
sudo apt install linux-generic

# RHEL/Fedora/Rocky
sudo dnf upgrade kernel            # installs alongside; keeps installonly_limit kernels

# Always confirm what's running vs installed
uname -r                           # running kernel
dpkg -l 'linux-image-*' | grep ^ii # installed kernels (Debian)
rpm -q kernel                      # installed kernels (RHEL)
```

`dnf` keeps `installonly_limit` kernels (default 3) and prunes the oldest;
Debian keeps all until you autoremove. After a successful reboot you can reclaim
space:

```bash
sudo apt autoremove --purge        # removes old, unused kernels (Debian)
# Never remove the kernel you are currently running.
```

## Why a Reboot — and Reducing Them

A new kernel image is inert until PID 1 is running on it, which only happens at
boot. Two ways to avoid a *full* firmware reboot:

- **`kexec`** — load a new kernel and jump straight into it, skipping firmware
  POST and bootloader. Cuts reboot time dramatically on big servers but still
  tears down userspace (all processes restart):

  ```bash
  sudo kexec -l /boot/vmlinuz-$(uname -r) \
       --initrd=/boot/initrd.img-$(uname -r) \
       --reuse-cmdline
  sudo kexec -e        # jump now (or `systemctl kexec`)
  ```

- **Live patching** — apply a security fix to the *running* kernel with no
  reboot at all (next section).

## Live Patching

Live patching hot-swaps fixed function code into the running kernel using
`ftrace` to redirect calls, so a CVE fix lands without a reboot.

| Tool | Vendor | Notes |
|------|--------|-------|
| **kpatch** | Red Hat | RHEL; `kpatch list` / `kpatch load` |
| **kGraft** | SUSE | merged into upstream livepatch |
| **Ksplice** | Oracle | Oracle Linux; broadest patch coverage |
| **Livepatch** | Canonical | Ubuntu; `canonical-livepatch status` |

```bash
canonical-livepatch status         # Ubuntu: what's patched live
sudo kpatch list                   # RHEL: loaded live patches
```

**Hard limits — this is the senior/staff distinction:**
- Only patches that change function *bodies* work. You **cannot** live-patch
  changes to data structure layout, `__init` code, or anything altering the
  ABI/state.
- It is for **security backports**, not feature or version upgrades — you stay
  on the same base kernel, accumulating live patches.
- Live patches accumulate and you eventually **must** reboot onto the new base
  kernel to "bank" the fixes and reset the patch stack.

So live patching *buys time* to schedule a reboot calmly; it does not eliminate
the reboot.

## Reboot Coordination at Scale

A kernel CVE means rebooting the whole fleet. Do it without an outage:

- **Rolling reboots**: drain → reboot → health-check → next. Honor
  PodDisruptionBudgets in Kubernetes (`kubectl drain --ignore-daemonsets`).
- **Maintenance windows + canary**: reboot one node, soak it, then proceed.
- **`needs-restarting`** (RHEL) / **`/var/run/reboot-required`** (Debian) tell
  you which hosts are pending a reboot:

  ```bash
  needs-restarting -r            # RHEL: exit 1 if reboot needed
  ls /var/run/reboot-required    # Debian: file exists if reboot needed
  ```

- Automate with `unattended-upgrades` + `kured` (Kubernetes Reboot Daemon),
  which serializes node reboots across a cluster behind a lock.

## Choosing a Kernel: Stable vs LTS vs HWE

- **LTS (Long-Term Support)** kernels (e.g. 6.6 LTS) get security/bugfix
  backports for years with a stable ABI — the default for servers.
- **Distro stock kernel** tracks the distro's chosen LTS line; safest, most
  tested.
- **HWE (Hardware Enablement)** on Ubuntu ships a newer kernel on an LTS release
  to support recent hardware — newer drivers, shorter support tail.
- **Mainline/stable** (kernel.org latest): newest features, fastest-moving,
  use only when you need a specific new feature (e.g. a recent `io_uring` or
  cgroup v2 capability) and can absorb the churn.

For containers, remember the host kernel is shared by every container, so a host
kernel upgrade changes the kernel under *all* workloads at once — features like
idmapped mounts or newer `io_uring` become available (or behavior changes)
fleet-wide on reboot.

## Common Mistakes

- **Removing the old kernel before validating the new one** — you delete your
  rollback path. Keep at least one prior kernel until the new one is proven.
- **Assuming live patching = upgraded.** `uname -r` still shows the old base
  kernel; auditors and CVE scanners may flag it. You still owe a reboot.
- **Rebooting the whole fleet at once** instead of rolling — turns a routine
  patch into a self-inflicted outage.
- **Forgetting DKMS/out-of-tree modules** rebuild for the new kernel; the GPU or
  storage driver may be missing on first boot into it.

## Best Practices

- Always keep N≥1 known-good fallback kernels installed; validate then prune.
- Use live patching to decouple "patch now" from "reboot when convenient," but
  schedule the banking reboot — don't let patch stacks grow unbounded.
- Roll reboots with health checks and disruption budgets; never big-bang a fleet.
- Pin to an LTS line for servers; reserve mainline for hosts that genuinely need
  a new kernel feature.
- Test kernel upgrades in staging on identical hardware/VM images first, since
  driver and ABI regressions are hardware-specific.

## Quick Refs

```bash
# Upgrade
sudo apt install linux-generic                 # Debian/Ubuntu
sudo dnf upgrade kernel                         # RHEL/Fedora
uname -r                                        # running kernel
dpkg -l 'linux-image-*' | grep ^ii              # installed (Debian)
rpm -q kernel                                   # installed (RHEL)
sudo apt autoremove --purge                     # prune old (after validating)

# Fast reboot into new kernel (still restarts userspace)
sudo kexec -l /boot/vmlinuz-$(uname -r) --initrd=/boot/initrd.img-$(uname -r) --reuse-cmdline
sudo systemctl kexec

# Live patching
canonical-livepatch status                      # Ubuntu
sudo kpatch list                                # RHEL

# Reboot needed?
needs-restarting -r                             # RHEL
ls /var/run/reboot-required                      # Debian
```

## Interview Prep

**Junior**: "Why does a kernel upgrade usually need a reboot?"
- The kernel is the running machine; the new image only takes effect when the system boots into it, so a reboot (or kexec) is required to switch.

**Mid**: "After installing a new kernel, how do you safely roll back if it fails?"
- The package install keeps the old kernel and adds it to the GRUB menu, so you reboot and select the previous entry; nothing is removed until you explicitly autoremove after the new one is validated.

**Senior**: "What is live kernel patching and what can't it do?"
- It uses ftrace to redirect calls to fixed function bodies in the running kernel for security backports with no reboot; it cannot change data-structure layout, `__init` code, or the ABI, and you still must eventually reboot onto the new base kernel.

**Staff**: "A critical kernel CVE drops across a 2,000-node fleet. Walk me through your response."
- Apply live patches immediately where supported to neutralize the CVE without downtime, then schedule rolling reboots onto the patched base kernel honoring disruption budgets and health checks (kured/drain-reboot-verify), canary first, track pending hosts via `needs-restarting`/`reboot-required`, and validate out-of-tree/DKMS modules rebuilt before declaring done.

## Next Lecture

→ Move to [L03 — Networking](../../L03-networking/README.md)
