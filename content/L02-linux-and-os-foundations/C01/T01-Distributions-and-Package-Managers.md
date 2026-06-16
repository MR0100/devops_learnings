# L02/C01/T01 — Distributions and Package Managers

## Learning Objectives

- Choose the right distribution for a given workload and lifecycle constraint
- Master the package managers you'll touch daily: `apt`/`dpkg`, `dnf`/`rpm`, `apk`, `pacman`
- Reason about the stability vs cutting-edge tradeoff in terms of kernel, libc, and support windows
- Understand dependency resolution, transactions, and how package state lives on disk

## What a Distribution Actually Is

A distro is a curated set of choices layered on top of the Linux kernel: a libc (glibc or musl), an init system (almost always systemd now), a package format and manager, a default toolchain, and a release/support policy. Two distros running the same `6.8` kernel can behave very differently because of glibc version, default `vm.*` sysctls, SELinux vs AppArmor, and how aggressively they backport security fixes.

The distinction that matters in production is the **release model**: point releases (Debian, RHEL, Ubuntu LTS) freeze a snapshot and only backport fixes, while rolling releases (Arch, openSUSE Tumbleweed) ship upstream continuously. Point releases trade newer features for a stable ABI you can build against for years.

## Major Distribution Families

### Debian Family (Debian, Ubuntu, Linux Mint)
- Package Manager: `apt` (frontend) over `dpkg` (backend); `.deb` packages
- Stability: very stable (Debian); LTS releases with 5-yr support (Ubuntu)
- Common in: cloud base images, dev workstations, general-purpose servers
- Config-as-data: package config questions go through `debconf`; `/etc/apt/sources.list.d/` holds repos

### Red Hat Family (RHEL, CentOS Stream, Rocky, AlmaLinux, Fedora)
- Package Manager: `dnf` (modern) / `yum` (legacy alias) over `rpm`; `.rpm` packages
- Stability: very stable with a 10-yr lifecycle (RHEL); CentOS Stream is the *upstream* of RHEL now (rolling-ish); Fedora is bleeding edge
- Common in: enterprise, regulated industries, Kubernetes hosts (Red Hat UBI base images), OpenShift
- SELinux enforcing by default; `dnf` modularity and `dnf history` transactions

### Alpine
- Package Manager: `apk` (`apk add`/`del`); `.apk` packages
- Notable: musl libc (not glibc), BusyBox userland, ~5 MB base image
- Common in: container base images, embedded, CI runners where image pull time matters

### Arch / Manjaro
- Package Manager: `pacman`; AUR for community PKGBUILDs
- Notable: rolling release, minimal opinionation, excellent docs (the Arch Wiki)
- Common in: power-user workstations; rarely production servers

### Container-First / Immutable Distros
- Bottlerocket (AWS), Talos (Kubernetes, no SSH/shell), Flatcar/Fedora CoreOS — minimal, read-only root, atomic A/B upgrades, no package manager in the traditional sense
- You don't `apt install` on these; you bake images or run everything as containers

## Package Manager Cheat Sheet

| Action | apt | dnf | apk | pacman |
|---|---|---|---|---|
| Update repo index | `apt update` | `dnf check-update` | `apk update` | `pacman -Sy` |
| Install | `apt install pkg` | `dnf install pkg` | `apk add pkg` | `pacman -S pkg` |
| Remove | `apt remove pkg` | `dnf remove pkg` | `apk del pkg` | `pacman -R pkg` |
| Upgrade all | `apt upgrade` | `dnf upgrade` | `apk upgrade` | `pacman -Syu` |
| Search | `apt search term` | `dnf search term` | `apk search term` | `pacman -Ss term` |
| Show info | `apt show pkg` | `dnf info pkg` | `apk info pkg` | `pacman -Si pkg` |
| List installed | `dpkg -l` | `rpm -qa` | `apk info` | `pacman -Q` |
| List files in pkg | `dpkg -L pkg` | `rpm -ql pkg` | `apk info -L pkg` | `pacman -Ql pkg` |
| Find pkg owning file | `dpkg -S /path` | `rpm -qf /path` | `apk info --who-owns /path` | `pacman -Qo /path` |
| Verify integrity | `debsums pkg` | `rpm -V pkg` | `apk audit` | `pacman -Qkk pkg` |

## dpkg/rpm — The Layer Underneath

`apt` and `dnf` are dependency-resolving frontends. The real package database lives lower:

```bash
# Debian: package state under /var/lib/dpkg
dpkg -l | awk '/^ii/{print $2}'         # ii = installed OK
cat /var/lib/dpkg/status                # full package metadata

# RHEL: rpmdb (now sqlite under /var/lib/rpm)
rpm -qa --last | head                   # recently installed, newest first
rpm -q --changelog kernel | head        # security changelog for audits
rpm -qf /usr/bin/ssh                    # which package owns this binary
```

When `apt`/`dnf` get wedged (interrupted upgrade), you drop to the backend: `dpkg --configure -a` or `rpm --rebuilddb`.

## Transactions, Locks, and Rollback

`dnf` records every transaction and can undo one — invaluable when a `dnf upgrade` breaks a box:

```bash
dnf history                    # list transactions with IDs
dnf history info 42            # what changed in transaction 42
dnf history undo 42            # roll it back
```

`apt` has no native rollback (snapshot the filesystem with LVM/btrfs/ZFS instead). Both serialize behind a lock — `/var/lib/dpkg/lock-frontend` and the rpm transaction lock — which is why unattended-upgrades running in the background causes `Could not get lock` errors in your automation. Always gate package ops behind a check or `DEBIAN_FRONTEND=noninteractive` + retries.

## Stability vs Cutting Edge

| Distro | Kernel | libc | Lifecycle | Notes |
|---|---|---|---|---|
| Debian Stable | 6.1 LTS | glibc 2.36 | ~3 yr + LTS | Conservative; great for prod baselines |
| Ubuntu 24.04 LTS | 6.8 | glibc 2.39 | 5 yr (10 w/ Pro) | Balanced; ubiquitous cloud images |
| RHEL 9 | 5.14 (backported) | glibc 2.34 | 10 yr | Stable ABI; security backports, old version strings |
| Fedora 40 | 6.8 | glibc 2.39 | ~13 months | Bleeding edge; RHEL's proving ground |
| Alpine 3.20 | 6.6 | musl 1.2 | 2 yr | Minimal; container-optimized |

The RHEL trap: `kernel 5.14` looks ancient but Red Hat backports thousands of fixes into it, so CVE scanners that only read version strings produce false positives. Trust `rpm -q --changelog` and Red Hat's OVAL data, not the version number.

## When to Pick What

| Use Case | Pick |
|---|---|
| AWS production servers | Amazon Linux 2023 (RHEL-ish, AWS-tuned, free support) |
| GCP production servers | Container-Optimized OS or Debian |
| K8s node images | Bottlerocket / Talos / Flatcar (immutable, fast patch) |
| Container base images | distroless > Alpine > debian-slim > ubuntu |
| Regulated / long-support | RHEL or a rebuild (Rocky/Alma) with vendor SLAs |
| Workstations | Ubuntu LTS / Fedora / Pop!_OS |

## A Note on Alpine and musl

Alpine swaps glibc for musl, which is the source of most "works on my Ubuntu, breaks in the Alpine container" surprises:
- Smaller binaries and images, faster pulls
- Some glibc-only programs break — historically musl's stub `getaddrinfo` lacked full `/etc/nsswitch.conf` and DNS edge-case behavior, breaking certain resolvers
- Different `malloc` (musl's was simpler/slower); Python and some JVM/glibc-assuming workloads showed real performance regressions and required glibc-based images instead
- No `ldd` semantics you expect; precompiled glibc wheels/binaries won't run without `gcompat`

Rule of thumb: Alpine for small, well-tested tooling and statically linked Go binaries; prefer `debian-slim` or distroless for dynamically linked application runtimes.

## Common Mistakes

- Running `apt upgrade` interactively in automation without `DEBIAN_FRONTEND=noninteractive`, causing hangs on config prompts
- Using `pacman -Sy pkg` (partial upgrade) instead of `pacman -Syu` — on a rolling distro this produces a broken, partially-updated system
- Trusting kernel/glibc version strings on RHEL for CVE assessment instead of the vendor's backport data
- Building on glibc, deploying on Alpine, and being surprised when DNS or precompiled binaries fail
- Forgetting `apk add --no-cache` in Dockerfiles, leaving the package index in the image layer

## Best Practices

- Pin a single base distro family per fleet to standardize tooling, sysctls, and security baselines
- Use `apt-get` (not `apt`) in scripts — `apt`'s CLI is explicitly "not stable for scripting"
- Cache packages with a local mirror/proxy (apt-cacher-ng, Pulp, Artifactory) to survive upstream outages and speed builds
- Drive package state declaratively (Ansible/Puppet) and verify integrity with `rpm -Va` / `debsums` in audits
- For containers: multi-stage builds, `--no-cache`, and prefer distroless for the final runtime image

## Quick Refs

```bash
cat /etc/os-release                       # universal distro identification
apt-get -y install pkg                    # scriptable install (Debian)
dnf -y install pkg && dnf history         # install + audit trail (RHEL)
apk add --no-cache pkg                    # container-friendly install
dpkg -S $(which nginx)                    # which package owns this binary
rpm -qf $(readlink -f /usr/bin/python3)   # same, RPM world
dnf history undo last                     # roll back the last transaction
```

## Interview Prep

**Junior**: "What's the difference between `apt` and `dnf`?"
- Both are dependency-resolving frontends; `apt` manages `.deb` via `dpkg` on Debian/Ubuntu, `dnf` manages `.rpm` via `rpm` on RHEL/Fedora.

**Mid**: "When would you choose Alpine over Ubuntu for a container image?"
- Alpine for tiny, statically linked tooling where image size and pull time dominate; avoid it for glibc-dependent runtimes (some Python/JVM workloads) where musl causes DNS or performance regressions.

**Senior**: "A `dnf upgrade` broke production. How do you recover fast?"
- `dnf history` to find the transaction, `dnf history undo <id>` to roll it back, then snapshot/AMI the box and reproduce the failure off the critical path before retrying.

**Staff**: "Standardize package management across 100s of servers in multiple teams."
- Single base-distro family, internal package mirror/proxy for reproducibility and supply-chain control, declarative config management for desired state, automated drift detection (`rpm -Va`), and a tested patch pipeline with staged rollout and snapshot-based rollback.

## Next Topic

→ [T02 — Filesystem Hierarchy Standard (FHS)](T02-Filesystem-Hierarchy.md)
