# L27/C01/T01 — RTO, RPO, MTD

## Learning Objectives

- Define RTO, RPO, and MTD precisely and tell them apart
- Derive each from the architecture, then validate it with drills
- Tier services and match recovery investment to business value

(Covered for databases in L21/C06/T01 — this is the broader system view.)

These three numbers are the contract between engineering and the business for
*how bad an outage is allowed to be*. They are not aspirations; they are
testable targets that drive concrete architecture and spend.

## RTO — Recovery Time Objective

The maximum acceptable **downtime**: how long the service can be unavailable
before recovery completes. Measured in seconds → hours. RTO is about *time to
restore service*.

## RPO — Recovery Point Objective

The maximum acceptable **data loss**, expressed as time: how much recent data
you can afford to lose. An RPO of 5 minutes means a disaster may cost up to the
last 5 minutes of writes. RPO is about *how current the recovered data is*, and
it's set almost entirely by your replication/backup cadence.

```
        ← RPO →            ← RTO →
──────●────────█──────────────────●────────────▶ time
  last good    DISASTER       service restored
   data point  (T0)

RPO = data between last safe point and T0 that is lost
RTO = wall-clock from T0 until users are served again
```

The two are independent. You can have RPO 0 (synchronous replication, no data
loss) but RTO of 30 minutes (slow manual failover), or RPO 1 hour (hourly
backup) but RTO 5 minutes (fast restore of a small dataset). Design for each
separately.

## MTD — Maximum Tolerable Downtime

The business-driven ceiling: the point past which the outage causes
*catastrophic* harm — contractual penalties, regulatory breach, lost customers,
existential damage. MTD bounds RTO: **RTO must be comfortably less than MTD**,
because RTO is the target and MTD is the cliff. The gap between them is your
margin for the failover taking longer than planned.

```
RTO (target) ───────── margin ───────── MTD (catastrophe)
```

## Worked Tiers

| Tier | Example          | RTO     | RPO     | MTD     |
|------|------------------|---------|---------|---------|
| 1 — Mission-critical | Payments, auth   | < 1 min | 0       | ~4 h    |
| 2 — Important        | Core user-facing | < 1 h   | ~15 min | ~1 day  |
| 3 — Standard         | Internal tools   | ~4 h    | ~1 h    | ~3 days |
| 4 — Batch/analytics  | Reporting        | ~1 day  | ~1 day  | ~1 week |

One RTO/RPO for everything is the classic mistake: it either over-spends on
batch jobs or under-protects payments. Tier first, then assign targets.

## Deriving RTO (don't guess it)

RTO is the sum of the failover phases — measure each, don't assert the total:

```
RTO = T_detect + T_decide + T_execute + T_verify

  T_detect  : health checks fail → alert fires        (seconds–minutes)
  T_decide  : auto-trigger, or human assesses+approves (0 → minutes)
  T_execute : DNS/promote/LB switch, region warm-up    (seconds–minutes)
  T_verify  : confirm steady state restored            (minutes)
```

The biggest lever is usually `T_decide`: automated failover collapses it to
near-zero, semi-automatic (page a human to approve) adds minutes, manual adds
more. `T_execute` is dominated by DNS TTL/propagation and DR-region warm-up.

## Deriving RPO (it equals your replication lag)

RPO is set by how you move data, not by a wish:

| Mechanism                         | Resulting RPO        |
|-----------------------------------|----------------------|
| Synchronous replication           | 0                    |
| Async replication (same/near region) | seconds            |
| Async cross-region replication    | seconds → minutes    |
| Periodic snapshots                | snapshot interval    |
| Daily backup                      | up to 24 hours       |

To improve RPO, increase replication frequency or go synchronous — which costs
write latency and money. RPO 0 across regions is rarely worth it because
synchronous cross-region commits pay 50–200 ms RTT on every write.

## Cost vs Targets

Tighter targets cost more, non-linearly:

```
RPO 0   → synchronous replication (write-latency + infra cost)
RTO ~0  → active/active multi-region (2×+ infra, conflict handling)
RTO min → warm standby (idle capacity you pay for)
loose   → backup & restore (cheapest, slowest)
```

The discipline is to match the spend to the *value at risk*, tier by tier — and
to say "no" to RTO/RPO promises the architecture can't actually meet.

## Validate With Drills

Targets you don't test are fiction. Run DR drills (Game Days — L25/C04) at
least quarterly and record **actual** RTO and RPO against target:

- If actual RTO > target → invest (more automation, lower DNS TTL, pre-warmed DR)
- If actual RPO > target → tighten replication or backup cadence
- Trend the deltas over time; drift between drills is normal and must be caught

## Communicating to the Business

Translate the numbers into consequences the business owns:

- "RTO 1 hour means a region failure can keep checkout down up to an hour."
- "RPO 5 minutes means a disaster can lose up to the last 5 minutes of orders."

This is how you get sign-off on the spend (or an explicit acceptance of the
risk) rather than discovering the mismatch during a real incident.

## Common Mistakes

- One RTO/RPO for the whole platform → over-spend or under-protect
- Setting targets you've never measured against a real drill
- Confusing RTO (downtime) with RPO (data loss) in design discussions
- Promising RPO 0 without synchronous replication actually in place
- Drilling annually (or never) → targets silently drift out of compliance
- Ignoring MTD, so RTO has no margin and any slow failover is catastrophic

## Best Practices

- Tier services first; assign RTO/RPO/MTD per tier, documented and signed off
- Derive RTO from the failover phases and RPO from replication lag — don't guess
- Keep RTO comfortably under MTD; the gap is your safety margin
- Validate quarterly with drills; track actual vs target and close the gap
- Match investment to value at risk; refuse targets the architecture can't meet
- Phrase targets to the business in terms of downtime and lost data, not jargon

## Quick Refs

```
RTO : max downtime         = T_detect + T_decide + T_execute + T_verify
RPO : max data loss        = your replication/backup lag
MTD : catastrophe ceiling  → RTO must be < MTD (with margin)

Independent: RPO 0 ≠ fast RTO, and fast RTO ≠ RPO 0
Tier 1 ~ RTO<1m/RPO 0 ; Tier 4 ~ RTO 1d/RPO 1d
```

## Interview Prep

**Junior**: "What are RTO and RPO?" — RTO is the maximum acceptable downtime (time to restore service); RPO is the maximum acceptable data loss expressed as time (how much recent data you can lose). MTD is the business-set point past which an outage is catastrophic.

**Mid**: "How are RTO and RPO independent?" — They measure different things, so you tune them separately: synchronous replication gives RPO 0 but you can still have a slow (30-min) manual failover, and an hourly backup gives RPO 1 hour but a tiny dataset can restore in minutes. One doesn't imply the other.

**Senior**: "How do you derive an RTO instead of guessing it?" — Sum the failover phases — detect, decide, execute, verify — and measure each with a drill. The decide phase dominates: automation drives it toward zero, while a human-in-the-loop adds minutes. RPO, separately, just equals your replication or backup lag, so you improve it by replicating more often or synchronously.

**Staff**: "How do you set DR targets across a whole platform?" — Tier services by business value and assign RTO/RPO/MTD per tier rather than one number for everything; ensure RTO sits comfortably under MTD with margin; match spend to value at risk (active/active only for tier 1, backup/restore for tier 4); validate quarterly with drills tracking actual vs target; and refuse to promise targets — like cross-region RPO 0 — that the architecture can't meet without unacceptable write latency or cost.

## Next Topic

→ [T02 — DR Strategies](T02-DR-Strategies.md)
