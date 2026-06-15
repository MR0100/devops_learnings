# L02/C05/T05 — NFS, SMB, Network Filesystems

## Learning Objectives

- Export and mount NFS shares with `exportfs`, `/etc/exports`, and the right mount options
- Contrast NFSv3 vs NFSv4 and NFS vs SMB, and know when to use each
- Diagnose a hanging NFS mount and reason about `hard` vs `soft` semantics

## The Landscape

A network filesystem lets many clients share files over the network as if they were local, with the server owning the actual storage. The two dominant protocols:

| Protocol | Origin | Typical use | Default port |
|---|---|---|---|
| **NFS** | Unix/Linux | Linux-to-Linux shares, HPC, app data | 2049 (TCP) |
| **SMB/CIFS** | Windows | Windows shares, mixed/Mac environments | 445 (TCP) |

Object stores (S3) and cluster filesystems (CephFS, GlusterFS, Lustre) sit beyond these, but NFS and SMB are the workhorses for POSIX file sharing.

```
   Client A ─┐
   Client B ─┼── network ──► NFS/SMB server ──► local FS (ext4/xfs/zfs)
   Client C ─┘                                   on disk/LVM/RAID
```

## NFS Versions

| | NFSv3 | NFSv4 / v4.1 |
|---|---|---|
| State | Stateless | Stateful (leases, open/close) |
| Transport | UDP or TCP | TCP only |
| Ports | Many (portmap/rpcbind, mountd, statd…) | Single port 2049 |
| Locking | Separate NLM/NSM | Integrated into the protocol |
| Security | AUTH_SYS (host-trust) | AUTH_SYS + Kerberos (krb5/krb5i/krb5p) |
| Firewall | Painful (random ports) | Easy (one port) |
| Parallel | No | v4.1 adds pNFS |

**Use NFSv4.1+** for new deployments: one firewall port, integrated locking, and Kerberos. NFSv3 lingers for legacy and some appliances. A common production standard is **NFSv4.1 with Kerberos (krb5p)** for authenticated, encrypted access.

## Setting Up an NFS Server

```bash
# Install + enable
apt install nfs-kernel-server         # Debian/Ubuntu
systemctl enable --now nfs-server
```

Define exports in `/etc/exports`:

```
# <path>        <client>(<options>)
/srv/data       10.0.0.0/24(rw,sync,no_subtree_check)
/srv/readonly   *(ro,sync,no_subtree_check)
/srv/home       10.0.0.5(rw,sync,root_squash,no_subtree_check)
```

Apply and inspect:

```bash
exportfs -ra              # re-read /etc/exports (apply changes)
exportfs -v               # show active exports
showmount -e localhost    # what this server exports
```

### Export options that matter

| Option | Meaning |
|---|---|
| `rw` / `ro` | Read-write / read-only |
| `sync` | Reply only after data hits stable storage (safe; default) |
| `async` | Reply before flush — faster, risks data loss on crash |
| `root_squash` | Map client root to `nobody` (default, **keep it**) |
| `no_root_squash` | Client root = server root — dangerous, avoid |
| `all_squash` | Map every client UID to anonymous |
| `no_subtree_check` | Skip subtree checks — recommended (stability + speed) |

## Mounting NFS on the Client

```bash
apt install nfs-common
mount -t nfs -o vers=4.1 server:/srv/data /mnt/data
```

Persist in `/etc/fstab`:

```
server:/srv/data  /mnt/data  nfs  vers=4.1,hard,intr,_netdev,noatime  0  0
```

### Client mount options that matter

| Option | Meaning |
|---|---|
| `vers=4.1` / `nfsvers=4.1` | Pin the protocol version |
| `hard` | Retry forever on server failure — **no data loss**, but processes hang (default; correct for data) |
| `soft` | Give up after `retrans` retries and return an I/O error — **risks data corruption**, only for read-only/idempotent |
| `timeo=` / `retrans=` | Retry timeout (tenths of a second) and count |
| `intr` | Allow signals to interrupt hung calls (older kernels) |
| `_netdev` | Mount only after the network is up (essential in fstab) |
| `nconnect=4` | Open multiple TCP connections for parallel throughput |
| `noatime` | Don't push access-time updates over the network |
| `ac` / `noac` | Attribute caching on/off (`noac` for strict consistency, slow) |

**`hard` vs `soft` is the key tradeoff:** `hard` blocks indefinitely so a temporary server outage never loses or corrupts writes — the client just waits and resumes. `soft` returns errors after a timeout, which can corrupt data if a partial write is abandoned. Default to `hard` (with `_netdev`); use `soft` only for read-only, idempotent access where a hang is worse than an error.

## Diagnosing a Hanging NFS Mount

A hung NFS mount is a classic interview scenario. Walk the path from client to server:

```bash
# 1. Is it actually hung? Processes stuck in 'D' (uninterruptible) state:
ps aux | awk '$8 ~ /D/'

# 2. Can the client reach the server at all?
ping server
nc -vz server 2049             # port 2049 open?

# 3. What does the client think is mounted, and is it responsive?
mount | grep nfs
nfsstat -c                     # client RPC stats (retransmits climbing?)
stat /mnt/data                 # will hang if the mount is dead

# 4. On the server side:
showmount -e server            # is it still exporting?
exportfs -v
systemctl status nfs-server
ss -tnp | grep :2049           # connections present?
```

Typical causes and fixes:
- **Server down / network partition** → with `hard` mounts, clients wait; they recover when the server returns. With `soft`, you'd see I/O errors instead.
- **Firewall dropped 2049** → `nc -vz` fails; open the port (NFSv4 needs just 2049; v3 needs rpcbind/mountd/statd too).
- **Stale file handle** (`ESTALE`) → the exported object was removed/recreated on the server; remount or recreate the path.
- **DNS/route change** → client can't resolve/reach the server; check `ping`, `resolvectl`.

Avoid `umount` on a hung hard mount (it'll hang too); use `umount -f` or `umount -l` (lazy) to detach, then remount.

## SMB / CIFS — sharing with Windows

For mixed environments or Windows clients, use SMB (Samba on Linux):

```bash
# Mount a Windows/Samba share from Linux
mount -t cifs //server/share /mnt/share \
  -o username=alice,vers=3.0,iocharset=utf8
```

```
# /etc/fstab with a credentials file (don't put passwords inline)
//server/share  /mnt/share  cifs  credentials=/etc/smb.cred,vers=3.0,_netdev  0  0
```

Use **SMB 3.x** (encryption, better performance); avoid SMB1 (insecure, deprecated). NFS is generally preferred for Linux-to-Linux; SMB wins when Windows/macOS clients or Active Directory integration are in the mix.

## Common Mistakes

- **`soft` mounts for writable data** — silent corruption on timeout; use `hard`.
- **Omitting `_netdev`** in fstab — boot tries to mount before the network and hangs or fails.
- **`no_root_squash`** — lets a compromised client's root write as server root; keep the default `root_squash`.
- **NFSv3 through a firewall** — random rpcbind ports break; move to v4.1 (single port 2049).
- **`umount` on a hung hard mount** — it hangs too; use `umount -l`/`-f` and fix the server.
- **SMB1 or inline passwords in fstab** — use SMB 3.x and a `credentials=` file with `0600` perms.

## Best Practices

- Standardize on **NFSv4.1**, single port 2049, Kerberos (`krb5p`) where security matters.
- Mount data shares **`hard`** with `_netdev` and `noatime`; reserve `soft` for read-only/idempotent paths.
- Keep `root_squash` and `no_subtree_check`; export to specific subnets/hosts, never `*` for writable shares.
- Use `nconnect=` to scale throughput on fast links; monitor `nfsstat` retransmits.
- For SMB, require SMB 3.x with encryption and store credentials in a protected file.

## Quick Refs

```bash
# Server (NFS)
# /etc/exports:  /srv/data 10.0.0.0/24(rw,sync,root_squash,no_subtree_check)
exportfs -ra ; exportfs -v
showmount -e localhost
systemctl status nfs-server

# Client (NFS)
mount -t nfs -o vers=4.1,hard,_netdev,noatime server:/srv/data /mnt/data
# fstab:  server:/srv/data /mnt/data nfs vers=4.1,hard,_netdev,noatime 0 0
nfsstat -c

# Diagnose a hang
ps aux | awk '$8 ~ /D/'      # uninterruptible processes
nc -vz server 2049
stat /mnt/data ; nfsstat -c
umount -l /mnt/data          # lazy-detach a hung mount

# SMB
mount -t cifs //server/share /mnt/share -o credentials=/etc/smb.cred,vers=3.0
```

## Interview Prep

**Junior**: "What is NFS and what port does v4 use?"
- NFS is a protocol for mounting a remote server's directories over the network as if local; NFSv4 uses a single TCP port, 2049, which makes firewalling simple.

**Mid**: "NFSv3 vs NFSv4 — what changed?"
- v4 is stateful and TCP-only over one port (2049) with integrated locking and Kerberos support, replacing v3's stateless, multi-port (rpcbind/mountd/statd) design — so it's far easier to firewall and secure.

**Senior**: "Diagnose: an NFS mount is hanging."
- Check for processes in `D` state, verify reachability (`ping`, `nc -vz server 2049`) and that the server still exports (`showmount -e`); with a `hard` mount the client waits out a server/network outage and recovers, while firewall blocks, stale handles, or DNS changes need fixing — and you lazy-unmount (`umount -l`) rather than blocking on a normal `umount`.

**Staff**: "Design a resilient, secure NFS deployment for a fleet of app servers."
- NFSv4.1 over a single port with Kerberos (krb5p) for authenticated, encrypted access; `hard,_netdev,noatime,nconnect=N` client mounts so transient server/network failures never lose writes and throughput scales; `root_squash`, host/subnet-scoped exports, and `sync` on the server; plus monitoring of `nfsstat` retransmits and server health, with the export backed by redundant storage (RAID/replicated volume) so a single disk loss doesn't take the share down.

## Next Chapter

→ Move to [L02/C06 — Networking](../C06/README.md)
