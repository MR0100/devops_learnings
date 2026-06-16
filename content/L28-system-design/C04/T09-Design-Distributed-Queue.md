# L28/C04/T09 — Design a Distributed Queue / Job Scheduler

## Learning Objectives

- Design a durable distributed queue and a scheduler on top of it
- Reason about delivery semantics (at-least-once vs exactly-once)
- Derive partition and storage counts from throughput

## Requirements

### Functional
- Producers enqueue jobs; consumers dequeue and process
- At-least-once delivery (no silent loss)
- Delayed / scheduled jobs ("run at T", "in 5 min")
- Retries with backoff; dead-letter queue (DLQ) after N attempts
- Visibility into queue depth, age, in-flight count

### Non-Functional
- Durable: an acked enqueue survives a broker crash
- Ordered **per key** (global ordering is not required and is expensive)
- p99 enqueue < 10 ms
- Scales horizontally with traffic

## Estimation (back-of-envelope, derived)

```
enqueue_rate      = 100,000 jobs/s   (peak, given)
avg_job_size      = 2 KB
write_bw          = 100k × 2 KB      = 200 MB/s
retention         = 7 days (replay window)
storage           = 100k jobs/s × 2 KB × 86,400 × 7
                  ≈ 120 TB  (before replication)
```
With replication factor 3: ~360 TB raw. That's a cluster, not a node.

Partition count is derived from per-partition throughput, not guessed:
```
per_partition_write ≈ 10 MB/s        (safe single-partition ceiling)
partitions          = write_bw / per_partition_write = 200 / 10 = 20
```
Round up for headroom and future growth → ~32 partitions. Consumer parallelism is then **bounded by partition count** (one consumer per partition within a group) — a key design consequence to call out.

## High-Level Design

```
Producers
   │ enqueue (key → partition = hash(key) % P)
   ▼
[Broker cluster: P partitions, RF=3]
   │  append-only log per partition (offset-ordered)
   ▼
Consumer groups (≤ P consumers each)
   │  pull batch → process → commit offset
   ├─ success → advance offset
   ├─ retry   → re-deliver with backoff
   └─ N fails → DLQ
        ▲
[Scheduler]  ── due jobs ──► enqueue into main queue
   (timer wheel / sorted store of {run_at, job})
```

- **Log-structured partitions** (Kafka-style): append-only, ordered by offset, replicated. Consumers track an **offset**, which makes replay and at-least-once natural.
- **Scheduler** is a separate component that holds future-dated jobs and moves them into the queue when due.

## Deep Dive: Delivery Semantics

The classic trap — "exactly-once" is mostly a lie at the transport layer:
- **At-most-once**: ack before processing → fast, loses jobs on crash. Rarely acceptable.
- **At-least-once**: process, then commit offset → on crash you reprocess. **Default choice.**
- **Exactly-once**: only achievable as *effectively-once* = at-least-once delivery **+ idempotent consumers** (see C03/T01). The queue can't give it alone; the consumer must dedupe on a job id.

So the design states: **at-least-once + idempotency key per job**. The consumer records processed job ids (or writes results idempotently) so re-delivery is harmless.

**Visibility timeout vs offset commit** — two families:
- *Offset model* (Kafka): consumer owns a partition, commits offset after processing. Ordered, high throughput, parallelism capped at P.
- *Visibility-timeout model* (SQS): message is hidden while in-flight; consumer deletes on success or it reappears after the timeout. No per-key order, but parallelism is unbounded.

Pick offset model when **order per key** matters; visibility model when you want **massive fan-out** and don't need order.

## Deep Dive: The Scheduler

Scheduling = "enqueue this in the future." Two implementations:
- **Sorted store** (Redis ZSET / DB table keyed by `run_at`): a poller pulls `WHERE run_at ≤ now` every tick and enqueues. Simple, scales to millions of timers, second-level precision.
- **Hashed timer wheel**: O(1) insert/expire, sub-second precision, but in-memory — needs durable backing for restart safety.

Make the move atomic so two scheduler replicas don't double-enqueue: claim due jobs with an atomic conditional update (`UPDATE ... WHERE state='pending' AND run_at<=now RETURNING ...`) or a `ZPOPMIN`-style pop. Cron-style recurring jobs = re-insert the next occurrence after firing.

## Bottlenecks & Failure Modes

- **Hot partition**: a skewed key (one tenant) saturates one partition. Mitigate by hashing on a higher-cardinality key or salting.
- **Consumer lag**: producers outrun consumers → depth grows. Alarm on **age of oldest message**, not just depth; autoscale consumers up to P, then add partitions (a heavier operation).
- **Poison message**: one bad job fails forever and blocks the partition (in offset model). Cap retries → route to **DLQ**, keep the partition flowing.
- **Duplicate delivery**: guaranteed under at-least-once → idempotent consumer is mandatory, not optional.
- **Broker loss**: RF=3 + acks=all means an acked write survives one (or two) broker failures; acks=1 is faster but loses the tail on leader crash.
- **Thundering scheduler**: 1M jobs all due at midnight → spread with jitter or rate-limit the enqueue drain.

## Trade-Offs

- **Order vs parallelism**: per-partition order caps consumers at P; unordered visibility-timeout queues fan out without limit.
- **Latency vs durability**: `acks=all` + fsync is durable but slower than `acks=1`.
- **Build vs buy**: SQS/SNS (managed, visibility model) vs Kafka (ordered log, replay) vs Redis Streams (light, fast) vs Temporal (durable workflows, not just a queue).
- **Push vs pull**: pull (consumer-paced) gives natural backpressure (see C03/T02); push risks overwhelming slow consumers.

## Real Examples

- **Kafka**: partitioned replicated log; offset model; replay via retained offsets.
- **AWS SQS**: visibility-timeout model, at-least-once, DLQ built in; FIFO queues add per-group ordering.
- **Sidekiq / Celery**: app-level job queues on Redis/RabbitMQ with retries + scheduled jobs.
- **Temporal / Airflow**: durable scheduling and workflow orchestration above the raw queue.

## Best Practices

- At-least-once + idempotent consumers (assume duplicates)
- DLQ after bounded retries; alert on DLQ growth
- Alarm on oldest-message age, not just depth
- Exponential backoff **with jitter** on retries
- Partition on a high-cardinality key to avoid hot partitions

## Common Mistakes

- Claiming "exactly-once" without idempotency
- No DLQ → one poison message wedges a partition
- Unbounded retries (tight loops, amplified load)
- Monitoring depth but not message age
- More consumers than partitions (idle consumers in offset model)

## Quick Refs

```
partitions = write_bw / per_partition_write
consumers ≤ partitions (offset model)

Semantics:
  at-most-once   — fast, lossy
  at-least-once  — default; expect dupes
  effectively-once = at-least-once + idempotency

Scheduler: sorted store (ZSET) or timer wheel
Retry → backoff+jitter → DLQ after N
```

## Interview Prep

**Mid**: "What delivery guarantee would you give and why?" — At-least-once: process the job, then commit the offset, so a crash reprocesses rather than loses. At-most-once risks silent loss, and true exactly-once isn't a transport property — so I pair at-least-once with idempotent consumers.

**Senior**: "A job got delivered twice and charged a customer twice — how do you prevent that?" — That's expected under at-least-once. The fix is an idempotency key per job: the consumer records processed ids (or writes the charge keyed on the id with `INSERT ... ON CONFLICT DO NOTHING`), so re-delivery is a no-op. The queue can't promise exactly-once; the consumer makes reprocessing harmless.

**Staff**: "Queue depth is exploding during a traffic spike — walk me through it." — First check whether producers outran consumers or a poison message wedged a partition. Scale consumers up to the partition count; if that's saturated, the real lever is partition count, which needs rebalancing. I alarm on oldest-message age (latency SLO) over raw depth, route repeat failures to a DLQ so one bad job can't block a partition, and apply backpressure to producers so the spike sheds load instead of amplifying.

**Principal**: "Design a scheduler for tens of millions of future-dated jobs with second-level precision." — A durable sorted store keyed by `run_at` (sharded ZSET or partitioned table), drained by a poller that atomically claims due jobs so replicas don't double-fire; recurring jobs re-insert their next occurrence on fire. Spread midnight-storm bursts with jitter and rate-limit the enqueue drain so the downstream queue isn't swamped. For exactly-once *effects*, the fired job carries an idempotency key end to end.

## Next Topic

→ [T10 — Design a Key-Value / Cache Store](T10-Design-KV-Cache-Store.md)
