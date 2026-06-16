# L02/C10/T01 — Boot Sequence

## Learning Objectives

- Trace the full boot path from power-on to login: firmware → bootloader → kernel → initramfs → systemd
- Distinguish BIOS/MBR from UEFI/GPT boot and know where the bootloader lives in each
- Use GRUB to edit kernel parameters at boot and recover an unbootable system
- Profile and shrink boot time with `systemd-analyze`

## The Big Picture

When you press the power button, the CPU is dumb: it starts executing at a fixed
reset vector with no OS, no drivers, no filesystem. Booting is the staged process
of bootstrapping from that minimal state up to a running, networked, multi-user
machine. Each stage knows just enough to find and hand off to the next.

```
Power on
   │
   ▼
Firmware (BIOS or UEFI)        ── POST, init hardware, find boot device
   │
   ▼
Bootloader (GRUB / systemd-boot)── load kernel + initramfs into RAM
   │
   ▼
Kernel (vmlinuz)               ── decompress, init CPU/MM, mount initramfs
   │
   ▼
initramfs                      ── load drivers to reach the REAL root
   │
   ▼
Real root mounted, PID 1 = systemd
   │
   ▼
systemd targets/services       ── multi-user.target / graphical.target
   │
   ▼
Login prompt
```

## Stage 1 — Firmware: BIOS vs UEFI

The firmware lives on a flash chip on the motherboard. It runs POST (Power-On
Self-Test), initializes RAM and basic devices, then locates a boot device and
transfers control.

**BIOS (legacy)**
- 16-bit real mode, MBR (Master Boot Record) partition scheme
- The first 512 bytes of the disk hold the boot code (the *MBR boot sector*)
- Only 446 bytes for stage-1 code — too small for a real bootloader, so GRUB
  installs a tiny stub that chain-loads the rest from the disk
- Max 2 TiB disks, 4 primary partitions

**UEFI (modern)**
- 32/64-bit, GPT (GUID Partition Table), no 2 TiB limit
- Boots from a FAT32 **ESP** (EFI System Partition), usually mounted at `/boot/efi`
- Bootloaders are real `.efi` executables: `/boot/efi/EFI/<distro>/grubx64.efi`
- Boot entries are stored in NVRAM, manageable from Linux:

```bash
efibootmgr -v                 # list UEFI boot entries
ls /sys/firmware/efi          # exists only if booted in UEFI mode
```

UEFI also supports **Secure Boot**: the firmware verifies the bootloader's
signature against keys in NVRAM. With Secure Boot on, you boot a signed `shim`
that chains to a signed GRUB; unsigned kernel modules are rejected.

## Stage 2 — Bootloader (GRUB)

GRUB's job is to find a kernel, load it plus an initramfs into memory, set the
kernel command line, and jump into the kernel.

- `/boot/grub/grub.cfg` is the **generated** config — never hand-edit it
- Edit `/etc/default/grub` (timeout, default entry, kernel cmdline) then regenerate:

```bash
# Debian/Ubuntu
sudo update-grub
# RHEL/Fedora
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
```

At the GRUB menu, interactive keys save you when a system won't boot:
- `e` — edit the selected entry's kernel line for **one** boot (not persisted)
- `c` — drop to the GRUB command shell (`ls`, `set`, `linux`, `initrd`, `boot`)

Common one-time edits appended to the `linux` line:
- `single` or `1` — boot to single-user (rescue) mode
- `init=/bin/bash` — bypass init entirely to reset a forgotten root password
- `nomodeset` — disable kernel mode-setting when a GPU driver hangs the boot

## Stage 3 — The Kernel

GRUB loads the compressed kernel image (`vmlinuz`) into RAM and jumps in. The
kernel:
1. Decompresses itself
2. Sets up the CPU, interrupt tables, and memory management
3. Detects CPUs and brings them online
4. Unpacks the initramfs into a RAM-backed `tmpfs`

The kernel cannot yet read your real root filesystem — it may live on LVM, RAID,
an encrypted LUKS volume, or NFS, all of which need drivers and userspace tools.
That's what the initramfs is for.

## Stage 4 — initramfs

The **initramfs** (initial RAM filesystem) is a compressed cpio archive bundled
with the kernel in `/boot/`. It contains a minimal userspace — `busybox`, the
drivers, and the scripts needed to *find and mount the real root*.

```
initramfs runs /init  ──►  load storage drivers (nvme, virtio, raid)
                       ──►  assemble LVM / open LUKS / start mdadm
                       ──►  mount real root read-only on /sysroot
                       ──►  switch_root /sysroot /sbin/init
```

Rebuild it when you change drivers, the crypttab, or the root storage stack:

```bash
# Debian/Ubuntu (initramfs-tools)
sudo update-initramfs -u -k all
# RHEL/Fedora/SUSE (dracut)
sudo dracut -f --kver $(uname -r)
lsinitramfs /boot/initrd.img-$(uname -r) | grep nvme   # inspect contents
```

A broken or missing module in the initramfs is the classic cause of a
`dracut: Warning: /dev/mapper/...does not exist` drop-to-emergency-shell hang.

## Stage 5 — systemd (PID 1)

`switch_root` execs `/sbin/init`, which on modern distros is **systemd**. As PID 1
it brings the system to a *target*:

```
default.target ──► graphical.target
                       │ (wants)
                       ▼
                 multi-user.target ──► sshd, cron, your services
                       │ (after)
                       ▼
                 basic.target ──► sysinit.target ──► local-fs, swap, udev
```

systemd parallelizes startup by resolving the dependency graph rather than
running scripts in a fixed numeric order like the old SysV init.

## Boot Time Optimization

```bash
$ systemd-analyze
Startup finished in 3.412s (firmware) + 2.108s (loader) + 1.903s (kernel) + 6.554s (userspace) = 13.978s
graphical.target reached after 6.501s in userspace

$ systemd-analyze blame
          4.211s NetworkManager-wait-online.service
          1.880s docker.service
          1.022s snapd.service
           512ms systemd-journal-flush.service

$ systemd-analyze critical-chain
graphical.target @6.501s
└─multi-user.target @6.500s
  └─docker.service @4.610s +1.880s
    └─network-online.target @4.609s
      └─NetworkManager-wait-online.service @0.397s +4.211s
```

`blame` lists the slowest *units*; `critical-chain` shows the slowest *dependency
path* — the one that actually gates boot completion. A slow unit that nothing
waits on does not delay `graphical.target`. The usual culprit is
`*-wait-online.service` blocking on DHCP; mask it if services don't need the
network up before they start.

## Common Mistakes

- **Hand-editing `/boot/grub/grub.cfg`.** It is regenerated on the next kernel
  install and your changes vanish. Edit `/etc/default/grub` and run `update-grub`.
- **Forgetting to rebuild initramfs** after changing `/etc/crypttab`,
  `/etc/fstab` root, or adding a storage driver — you boot into an emergency shell.
- **Confusing `blame` with `critical-chain`.** Optimizing a slow unit off the
  critical path saves zero wall-clock boot time.
- **Mixing BIOS and UEFI installs.** Installing a UEFI bootloader on a
  BIOS-booted machine (or vice versa) produces a black screen with no menu.

## Best Practices

- Keep the GRUB timeout at 2–5s on servers so you can intervene without slowing
  every boot.
- Use `systemd-analyze critical-chain` before optimizing; measure, don't guess.
- Test boot-affecting changes (cmdline, fstab, crypttab) with a known-good
  fallback kernel still installed.
- On cloud images, disable `NetworkManager-wait-online` if your app starts its
  own retry logic — it is the single biggest boot-time win on most VMs.

## Quick Refs

```bash
# Where am I booted?
ls /sys/firmware/efi && echo UEFI || echo BIOS
efibootmgr -v                          # UEFI boot entries

# GRUB
sudo update-grub                       # Debian/Ubuntu
sudo grub2-mkconfig -o /boot/grub2/grub.cfg   # RHEL
# At boot menu: 'e' edit entry, 'c' GRUB shell

# initramfs
sudo update-initramfs -u -k all        # Debian/Ubuntu
sudo dracut -f --kver $(uname -r)      # RHEL/SUSE
lsinitramfs /boot/initrd.img-$(uname -r)

# Boot profiling
systemd-analyze
systemd-analyze blame
systemd-analyze critical-chain
systemd-analyze plot > boot.svg
```

## Interview Prep

**Junior**: "What is the bootloader's job?"
- Find the kernel and initramfs, load them into RAM, set the kernel command line, and hand control to the kernel — GRUB is the common one on Linux.

**Mid**: "What's the difference between BIOS and UEFI booting?"
- BIOS uses 16-bit real mode and an MBR boot sector; UEFI runs `.efi` executables from a FAT32 ESP, uses GPT, supports >2 TiB disks and Secure Boot, and stores boot entries in NVRAM.

**Senior**: "A server drops to an initramfs/emergency shell on boot. Where do you look?"
- The real root couldn't be mounted: check the storage stack (LVM/RAID/LUKS) the initramfs needs, verify the driver is baked in (`lsinitramfs`), inspect `/etc/fstab` and the root= cmdline, and rebuild the initramfs once fixed.

**Staff**: "Walk me through power-on to login and where you'd cut 5 seconds of boot time."
- Firmware POST → bootloader → kernel decompress + MM init → initramfs mounts real root → systemd reaches its target. To cut time, run `systemd-analyze critical-chain`, find the gating unit (usually `network-wait-online` or a heavy daemon), and mask or parallelize it rather than touching units off the critical path.

## Next Topic

→ [T02 — Kernel Modules](T02-Kernel-Modules.md)
