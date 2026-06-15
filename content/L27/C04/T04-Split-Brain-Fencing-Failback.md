# L27/C04/T04 — Split-Brain, Fencing & Failback

## Learning Objectives

- Explain split-brain and why naive failover can cause it
- Prevent dual-primary writes with quorum, fencing, and STONITH
- Run a safe, ordered failback after the primary recovers

Failover gets the headlines, but the dangerous failure modes are what happens
*around* it: two nodes both believing they're primary (split-brain), and the
messy return home afterward (failback). Getting failover fast but split-brain
wrong corrupts data — a worse outcome than the original outage.

## Split-Brain

Split-brain is when a network partition (or a false failure detection) leaves
**two nodes both acting as primary**, each accepting writes. When the partition
heals, you have two divergent histories and no safe way to merge them — silent
data loss or corruption.

```
        ╳ partition
   ┌──────────┐    ╳    ┌──────────┐
   │ Primary  │  ╳ ╳ ╳  │ Replica  │  ← can't see primary
   │ (writes) │    ╳    │ promotes │     so promotes itself
   └──────────┘    ╳    │ (writes) │
        │          ╳    └──────────┘
   clients A write here  clients B write there
        └────────── partition heals ──────────┘
                  two conflicting truths
```

The trigger is almost always **failure detection that can't distinguish "the
primary is dead" from "I can't reach the primary."** A replica that promotes on
"can't reach" — while the old primary is alive and still serving the other side
of the partition — is the textbook cause.

## Prevention 1: Quorum (majority)

Require a **majority** of nodes to agree before any node acts as primary. With
an odd number of members, only the side of a partition holding the majority can
elect/keep a leader; the minority side refuses writes. This is how Raft, etcd,
ZooKeeper, Patroni's DCS, and MongoDB replica sets avoid split-brain.

```
5-node cluster, partition 3 | 2
  majority side (3): keeps/elects leader, serves writes
  minority side (2): no quorum → steps down, read-only / rejects
```

Consequences to internalize:

- **Odd member counts** (3, 5) so a partition always has a clear majority
- A **two-node cluster cannot self-arbitrate** — a 1|1 split has no majority;
  add a third voter (a witness/arbiter) or you have no protection
- The minority must **fail closed** (reject writes), not keep serving

## Prevention 2: Fencing

Quorum decides *who should be* primary; **fencing makes the old primary
actually stop**. Fencing isolates a node suspected of being faulty so it can no
longer affect shared state, even if it's still running and thinks it's primary.

- **Resource fencing** — revoke the node's access to the shared resource:
  detach the EBS volume, revoke the DB's storage lease, pull its IAM/role,
  remove it from the load balancer's target group.
- **Network fencing** — block the node at the firewall/security group so it
  can't reach clients or shared storage.
- **Token/epoch fencing** — every leader gets a monotonically increasing
  **fencing token**; the shared resource (storage, lock service) rejects any
  request carrying an older token. This stops a *paused* old leader that wakes
  up and tries to write with a stale belief that it's still primary.

```
leader epoch 7 writes  → storage accepts (token 7 ≥ 7)
old leader (epoch 6) wakes, writes → storage REJECTS (token 6 < 7)
```

Fencing tokens are the robust, software-only defense and the reason
lock-service-based leader election (etcd lease, ZooKeeper) is safe even with
GC pauses and clock skew.

## Prevention 3: STONITH

**STONITH** — "Shoot The Other Node In The Head" — is the bluntest fence: the
new primary forcibly **powers off or reboots** the old node before taking over,
guaranteeing it cannot issue another write. Common in Pacemaker/Corosync HA
clusters via an IPMI/PDU/cloud-API power control.

- Use when you cannot otherwise guarantee the old primary is silent (shared
  storage, no token support)
- The power-control path itself must be reliable, or STONITH becomes the single
  point of failure (a node that can't be shot can't be safely replaced)

```
detect old primary unhealthy → STONITH (power off via IPMI/cloud API)
   → confirm down → promote replica → resume writes
```

STONITH/quorum/fencing are layered, not alternatives: quorum to *decide*, a
fencing token or STONITH to *enforce*.

## Cloud-Managed Equivalents

You rarely hand-roll this; managed services bake it in:

- **RDS Multi-AZ** — AWS arbitrates failover and repoints the DNS endpoint; the
  old primary is fenced from the standby's storage. No dual-primary.
- **Aurora** — shared storage volume with a single writer; promotion is
  storage-level, so two writers can't both commit.
- **Patroni (Postgres)** — uses a DCS (etcd/Consul) for quorum leader election
  plus a fencing/`pg_rewind` step before reattaching the old primary.
- **MongoDB / Raft systems** — majority write concern + election epochs.

Know the principle so you can verify the managed service actually provides it —
and so you recognize when a DIY setup (e.g. two-node Postgres with naive
promotion) is unprotected.

## Failback

Failback is returning to the original primary/region after it recovers. It is
**not** the reverse of failover — done carelessly it re-creates split-brain or
loses the writes that happened in DR.

Safe, ordered procedure:

```
1. Confirm the original primary/region is genuinely healthy and stable
2. Make the old primary a REPLICA of the current (DR) primary —
   never let it resume as primary with its stale data
3. Replicate DR → old primary; wait for replication lag ≈ 0
4. Schedule a low-traffic failback window
5. Quiesce writes briefly, confirm zero lag, then promote the old primary
6. Fence the DR side from resuming as primary; repoint traffic
7. Verify steady state; keep DR as the new standby
```

Key rules:

- The recovered node **must come back as a replica first** — resuming it as
  primary with pre-failure data is an instant split-brain.
- Reconcile any writes that happened in DR *before* cutting back, or you lose
  them.
- Failback is a planned, low-traffic operation. **Often the right call is to
  stay on DR** until a maintenance window rather than rush back.

## Common Mistakes

- Promoting a replica on "can't reach primary" without quorum → split-brain
- Two-node clusters with no witness/arbiter → a 1|1 partition can't be resolved
- Quorum without fencing → a paused old primary wakes and writes stale data
- No fencing token, so a GC-paused old leader corrupts shared storage
- Treating failback as "just fail over the other way" → loses DR-era writes or splits brain
- Letting the recovered primary resume as primary with its old data
- A STONITH power-control path that is itself unreliable or a single point of failure

## Best Practices

- Use odd-sized quorum (3/5) and make the minority side fail closed
- Add a witness/arbiter for any two-node pair; never let two nodes self-arbitrate
- Layer enforcement on top of quorum: fencing tokens (preferred) or STONITH
- Prefer managed services (RDS/Aurora/Patroni) that provide quorum+fencing, and verify it
- Always bring a recovered node back as a replica first; reconcile DR writes before promoting
- Treat failback as a planned, low-traffic, runbooked operation — drill it like failover
- Pick consistency over availability for write paths where divergence is unacceptable (CP)

## Quick Refs

```
Split-brain : two primaries after a partition → divergent writes
Prevent:
  Quorum   → only the majority side leads (odd counts, witness for 2-node)
  Fencing  → make the old primary stop: revoke resource / network / token(epoch)
  STONITH  → power off the old node before promoting

Fencing token: storage rejects writes carrying an older epoch
Failback: recover → rejoin as REPLICA → sync → quiesce → promote → fence DR
Rule: never let a recovered node resume as primary with stale data
```

## Interview Prep

**Junior**: "What is split-brain?" — When a network partition leaves two nodes both acting as primary, each taking writes. After the partition heals you have two conflicting versions of the data with no safe way to merge them — corruption or data loss.

**Mid**: "How do you prevent split-brain?" — Quorum: require a majority of nodes to agree before any node is primary, with odd member counts so a partition always has a clear majority and the minority side rejects writes. A two-node cluster needs a third witness, because a 1|1 split has no majority to break the tie.

**Senior**: "Quorum says who's primary — how do you make the old one actually stop?" — Fencing. Revoke the suspected node's access to shared state (detach the volume, remove from the LB, network-block it), or use fencing tokens where each leader gets a monotonically increasing epoch and the shared resource rejects writes carrying an older token — which stops a GC-paused old leader that wakes up stale. STONITH (power the node off) is the blunt last resort when you can't otherwise guarantee silence.

**Staff**: "Walk me through a safe failback after a regional failover." — Failback is not the reverse of failover. First confirm the original region is genuinely stable, then rejoin the old primary as a *replica* of the current DR primary — never resume it with its stale pre-failure data, which would be instant split-brain. Replicate DR→old until lag is ~0, pick a low-traffic window, quiesce writes, confirm zero lag, promote the old primary, fence the DR side from resuming, repoint traffic, and verify. Often the right decision is to stay on DR until a planned window rather than rush back; either way, drill it like you drill failover.

## Next Topic

→ Move to [L27/C05 — Backups That Actually Work](../C05/README.md)
