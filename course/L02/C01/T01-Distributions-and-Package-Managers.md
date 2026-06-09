# L02/C01/T01 — Distributions and Package Managers

## Learning Objectives

- Choose the right distribution for a workload
- Master the package managers you'll encounter most often
- Understand stability vs cutting-edge tradeoffs

## Major Distribution Families

### Debian Family (Debian, Ubuntu, Linux Mint)
- Package Manager: `apt` (frontend) over `dpkg` (backend)
- Stability: very stable (Debian); LTS releases (Ubuntu)
- Common in: cloud images, dev workstations, general servers

### Red Hat Family (RHEL, CentOS Stream, Rocky, AlmaLinux, Fedora)
- Package Manager: `dnf` (modern) / `yum` (legacy) over `rpm`
- Stability: very stable (RHEL); cutting edge (Fedora)
- Common in: enterprise, Kubernetes hosts (UBI), regulated industries

### Alpine
- Package Manager: `apk`
- Notable: musl libc (not glibc), tiny footprint
- Common in: container base images, embedded

### Arch / Manjaro
- Package Manager: `pacman`
- Notable: rolling release, AUR
- Common in: power user workstations

### Container-First Distros
- Bottlerocket (AWS), Talos (Kubernetes), CoreOS / Flatcar — minimal, immutable, k8s-focused

## Package Manager Cheat Sheet

| Action | apt | dnf | apk |
|---|---|---|---|
| Update repo index | `apt update` | `dnf check-update` | `apk update` |
| Install | `apt install pkg` | `dnf install pkg` | `apk add pkg` |
| Remove | `apt remove pkg` | `dnf remove pkg` | `apk del pkg` |
| Search | `apt search term` | `dnf search term` | `apk search term` |
| Show info | `apt show pkg` | `dnf info pkg` | `apk info pkg` |
| List installed | `dpkg -l` | `rpm -qa` | `apk info` |
| List files in pkg | `dpkg -L pkg` | `rpm -ql pkg` | `apk info -L pkg` |
| Find which pkg owns file | `dpkg -S /path` | `rpm -qf /path` | `apk info --who-owns /path` |

## Stability vs Cutting Edge

| Distro | Kernel | glibc | Notes |
|---|---|---|---|
| Debian Stable | 6.1 LTS | 2.36 | Conservative; great for prod |
| Ubuntu LTS | 6.5/6.8 | 2.39 | Balanced; 5-yr support |
| RHEL 9 | 5.14 | 2.34 | Enterprise stable; 10-yr support |
| Fedora 40 | 6.8 | 2.39 | Bleeding edge; 13-month lifecycle |
| Alpine | 6.6 | musl 1.2 | Minimal; container-optimized |

## When to Pick What

| Use Case | Pick |
|---|---|
| AWS production servers | Amazon Linux 2023 (RHEL-based, AWS-tuned) |
| GCP production servers | Container-Optimized OS or Debian |
| K8s node images | Bottlerocket / Talos / Flatcar |
| Container base images | distroless > Alpine > debian-slim > ubuntu |
| Workstations | Ubuntu LTS / Fedora / Pop!_OS |
| Long-term-stable legacy | RHEL with extended support |

## A Note on Alpine and musl

Alpine uses musl libc instead of glibc. This causes:
- Smaller binaries
- Some glibc-only programs break (especially with DNS resolver edge cases)
- Different malloc behavior — has caused real Python performance regressions
- Use Alpine for small, well-tested tooling; not always for application runtime

## Interview Prep

**Junior**: "What's the difference between apt and yum?"

**Mid**: "When would you choose Alpine over Ubuntu for a container image?"

**Senior**: "Walk me through how you'd standardize 100s of Linux servers across teams."

## Next Topic

→ [T02 — Filesystem Hierarchy Standard (FHS)](T02-Filesystem-Hierarchy.md)
