# L02/C10 — Boot Process & Kernel

## Chapter Overview

Understanding the boot sequence is essential for: BIOS-level debugging, custom kernels, immutable infrastructure, fast boot times, kernel upgrades, kexec.

## Topics

| Topic | Title | Hours |
|---|---|---|
| [T01](T01-Boot-Sequence.md) | BIOS/UEFI → Bootloader → Kernel → initramfs → systemd | 1 hr |
| [T02](T02-Kernel-Modules.md) | Kernel Modules | 0.5 hr |
| [T03](T03-Dmesg-Journalctl.md) | Reading dmesg and journalctl | 0.5 hr |
| [T04](T04-Kernel-Upgrades.md) | Kernel Upgrades, Live Patching | 1 hr |

## Boot Sequence

```
Power on
   ↓
BIOS or UEFI firmware
   ↓
Bootloader (GRUB, systemd-boot, EFI direct)
   ↓
Kernel loaded into RAM, initrd/initramfs mounted
   ↓
Kernel initializes drivers, mounts root
   ↓
PID 1 = /sbin/init = systemd
   ↓
systemd starts targets, services
   ↓
multi-user.target / graphical.target reached
```

### UEFI vs BIOS
- BIOS — legacy, MBR partition table, 16-bit
- UEFI — modern, GPT partition table, 64-bit, Secure Boot
- ESP (EFI System Partition) holds bootloader

### GRUB
`/boot/grub/grub.cfg` (generated); edit `/etc/default/grub` + `update-grub`.
Useful commands at boot:
- `e` edit kernel params (one-time)
- `c` GRUB shell

### initramfs
- Temporary root filesystem
- Loads drivers needed to mount the real root (RAID, LVM, encrypted, NFS root)
- Rebuilt with `update-initramfs` / `dracut`

### Kernel Modules
```bash
lsmod                       # loaded modules
modprobe nvme               # load
modprobe -r nvme            # unload
modinfo nvme                # info
modprobe.d/*.conf           # autoloading, options
/etc/modules                # load at boot
```

### dmesg & journald
```bash
dmesg | tail -50            # kernel ring buffer
dmesg -w                    # follow
dmesg -T                    # human timestamps
dmesg --level=err           # filter

journalctl -k               # kernel-only logs
journalctl -b               # current boot
journalctl --list-boots
journalctl -b -1            # previous boot
```

### Kernel Upgrades
- `apt upgrade linux-image-generic` / `dnf upgrade kernel`
- Reboot required (usually)
- Multiple kernels kept; revert via GRUB

### Live Patching
- kpatch (Red Hat), kgraft (SUSE), Canonical Livepatch
- Apply security fixes without reboot
- Limited to certain patch classes; not arbitrary changes

### Container Implications
- Containers share the host kernel
- Kernel module updates affect all containers
- Some container features need specific kernel versions (e.g., user namespaces, idmapped mounts, io_uring)

## Boot Time Optimization

```bash
systemd-analyze              # total time, kernel+userspace
systemd-analyze blame        # slowest units
systemd-analyze critical-chain
```

## Interview Themes

- "Walk me through what happens from power-on to login."
- "How would you investigate a slow boot?"
- "Compare BIOS and UEFI."
- "How does live kernel patching work and what are its limits?"

## End of L02

You've completed the Linux foundations. Next is networking deep dive.

## Next

→ [L03 — Networking Deep Dive (OSI to BGP)](../../L03-networking/README.md)
