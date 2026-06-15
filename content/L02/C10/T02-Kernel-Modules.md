# L02/C10/T02 — Kernel Modules

## Learning Objectives

- Explain what a loadable kernel module (LKM) is and why the kernel is modular
- List, inspect, load, and unload modules with `lsmod`, `modinfo`, `modprobe`, `rmmod`
- Configure module options, blacklists, and boot-time autoloading via `modprobe.d` and `modules-load.d`
- Understand dependency resolution and why `modprobe` beats `insmod`

## The Big Picture

The Linux kernel is monolithic but **modular**: most drivers and features can be
compiled as separate `.ko` (kernel object) files and loaded into the running
kernel on demand instead of being baked into the kernel image. This keeps the
core kernel small, lets you support thousands of devices without a giant boot
image, and lets you load a new driver without rebooting.

```
   Running kernel (vmlinuz, always resident)
          ▲           ▲           ▲
          │ insert    │           │
       ┌──┴──┐     ┌──┴──┐     ┌──┴──┐
       │ nvme│     │ i915│     │ xfs │   ← loadable modules (.ko)
       └─────┘     └─────┘     └─────┘
   /lib/modules/$(uname -r)/kernel/...
```

A module runs in **kernel space**: it shares the kernel's address space, can
crash the whole box, and is tied to the exact kernel version it was built
against (`vermagic`). That is why a kernel upgrade requires rebuilding
out-of-tree modules like the NVIDIA driver.

## Listing and Inspecting Modules

```bash
$ lsmod
Module                  Size  Used by
nvme                   53248  3
nvme_core             131072  4 nvme
xfs                  2052096  2
overlay               147456  1
bridge                311296  1 br_netfilter
```

- **Used by** is the reference count plus the modules depending on this one. A
  module with a nonzero count cannot be unloaded until its users are gone.

`modinfo` shows metadata, dependencies, and the parameters a module accepts:

```bash
$ modinfo nvme
filename:       /lib/modules/6.8.0-40-generic/kernel/drivers/nvme/host/nvme.ko
license:        GPL
author:         Matthew Wilcox <willy@linux.intel.com>
depends:        nvme-core
vermagic:       6.8.0-40-generic SMP preempt mod_unload
parm:           use_threaded_interrupts:int
parm:           io_queue_depth:set io queue depth (uint)
```

`vermagic` must match the running kernel or the load is rejected with
`Invalid module format`.

## Loading and Unloading

There are two tools. Use `modprobe`, almost never `insmod`.

```bash
sudo modprobe nvme              # load nvme AND its dependency nvme-core
sudo insmod /path/to/nvme.ko    # load ONE file, no dependency resolution

sudo modprobe -r nvme           # unload, respecting dependents
sudo rmmod nvme                 # force-ish single unload, no deps
```

`modprobe` reads the dependency map in
`/lib/modules/$(uname -r)/modules.dep` (built by `depmod`) and pulls in
everything required. `insmod` takes a single file path and fails if a dependency
isn't already loaded — it exists mostly for development.

Pass options at load time:

```bash
sudo modprobe nvme io_queue_depth=1024
```

## Boot-Time Autoloading and Options

Most modules load automatically: **udev** matches a device's
`MODALIAS` against the table in `modules.alias` and calls `modprobe`. For
modules with no triggering device (e.g. a tunneling or filesystem module you
want preloaded), declare them explicitly.

**Force-load at boot** — one module per line:

```bash
# /etc/modules-load.d/wireguard.conf
wireguard
```

(On older Debian this was the single file `/etc/modules`.)

**Set persistent options or aliases** under `/etc/modprobe.d/*.conf`:

```bash
# /etc/modprobe.d/nvme.conf
options nvme io_queue_depth=1024
```

**Blacklist a module** so udev won't autoload it (common for swapping a buggy
in-tree driver for a vendor one):

```bash
# /etc/modprobe.d/blacklist-nouveau.conf
blacklist nouveau
install nouveau /bin/false      # belt-and-suspenders: refuse even explicit loads
```

After editing config that affects early boot, rebuild the initramfs so the
change applies before the real root is mounted:

```bash
sudo update-initramfs -u        # Debian/Ubuntu
sudo dracut -f                  # RHEL/SUSE
```

## depmod and the Module Database

`depmod` scans `/lib/modules/<ver>/` and regenerates the dependency
(`modules.dep`) and alias (`modules.alias`) databases. It runs automatically
when a kernel package is installed. Run it manually only when you drop a `.ko`
into the tree by hand:

```bash
sudo depmod -a
```

## Signed Modules and Secure Boot

With Secure Boot enabled, the kernel enforces **module signing**: an unsigned or
wrongly-signed module is rejected and you'll see
`Loading of unsigned module is rejected` in `dmesg`. Out-of-tree modules (DKMS
builds like NVIDIA, VirtualBox) must be signed with a Machine Owner Key (MOK)
enrolled via `mokutil`, or Secure Boot must be disabled. This is the most common
reason a freshly-built driver silently fails to load.

## Common Mistakes

- **Using `insmod` and getting `Unknown symbol`** — it didn't load the
  dependency. Use `modprobe`, which resolves the graph.
- **Editing `/etc/modprobe.d` and expecting an early-boot effect without
  rebuilding initramfs.** The initramfs has its own copy of the config.
- **Blacklisting only with `blacklist`** — that stops *udev autoload* but an
  explicit `modprobe` still works; add `install <mod> /bin/false` to truly block.
- **Forgetting `vermagic`/Secure Boot signing** after a kernel upgrade, then
  wondering why the GPU driver vanished. The module must be rebuilt and re-signed.

## Best Practices

- Prefer `modprobe`/`modprobe -r` over `insmod`/`rmmod` everywhere; let it manage
  dependencies and reference counts.
- Keep all autoload and option config in version-controlled files under
  `/etc/modules-load.d/` and `/etc/modprobe.d/`, not ad-hoc runtime commands.
- Use DKMS for out-of-tree modules so they rebuild automatically on each kernel
  upgrade.
- Always `modinfo` an unfamiliar module before loading it on a production box —
  check `vermagic`, `depends`, and `signer`.

## Quick Refs

```bash
lsmod                          # loaded modules + refcounts
modinfo nvme                   # metadata, params, vermagic, signer
modprobe nvme                  # load with dependency resolution
modprobe nvme io_queue_depth=1024
modprobe -r nvme               # unload (respects dependents)
insmod /path/mod.ko            # load single file, no deps (rare)
rmmod nvme                     # unload single module
depmod -a                      # rebuild modules.dep / modules.alias

# Persistent config
echo wireguard | sudo tee /etc/modules-load.d/wireguard.conf
# /etc/modprobe.d/x.conf:  options <mod> key=val | blacklist <mod>
mokutil --list-enrolled        # Secure Boot MOK keys
```

## Interview Prep

**Junior**: "What is a kernel module?"
- A loadable `.ko` file — usually a driver or filesystem — that the kernel can insert into or remove from itself at runtime, so you don't need every feature compiled into the boot image.

**Mid**: "What's the difference between `insmod` and `modprobe`?"
- `insmod` loads one exact file with no dependency handling; `modprobe` looks up `modules.dep`, pulls in every required module, and reads options/blacklists from `/etc/modprobe.d`, so it's what you use in practice.

**Senior**: "How do you stop a driver from autoloading and force a vendor one instead?"
- Blacklist the in-tree module in `/etc/modprobe.d` (with `install <mod> /bin/false` to block explicit loads too), declare the replacement in `modules-load.d` or via DKMS, and rebuild the initramfs so it takes effect at early boot.

**Staff**: "After a kernel upgrade the NVIDIA module fails to load. Diagnose."
- Check `dmesg` for `Invalid module format` (vermagic mismatch — module built for the old kernel; rebuild via DKMS) or `unsigned module is rejected` under Secure Boot (re-sign with an enrolled MOK or disable Secure Boot); confirm `depmod` ran and `modinfo` reports the running kernel's vermagic.

## Next Topic

→ [T03 — dmesg & journalctl](T03-Dmesg-Journalctl.md)
