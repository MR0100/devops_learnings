# L07/C09/T02 — Vendor Lock-In: Reality vs Myth

## Learning Objectives

- Reason about lock-in honestly
- Pick services consciously

## The Lock-In Spectrum

```
Less lock-in                    More lock-in
EC2 (VM) → K8s → RDS Postgres → DynamoDB → Lambda → Cognito → Step Functions
```

Pick consciously per workload.

## Why Lock-In Exists

Cloud services compete via:
- Proprietary features
- Pricing models
- Performance
- Integration

Differentiated features ARE the value. Avoiding them = avoiding the cloud's benefit.

## Types of Lock-In

### Service Lock-In
DynamoDB schema doesn't port to MongoDB. Lambda triggers don't exist elsewhere.

### Data Lock-In
S3 has 100 TB. Moving takes weeks; egress costs $9k.

### Talent Lock-In
Team knows AWS. Re-skilling takes months.

### Operational Lock-In
Runbooks, monitoring, IAM patterns are AWS-specific.

### Contract Lock-In
3-year EDP for $X commitment.

The last 3 often matter more than service-level lock.

## The "Multi-Cloud for Lock-In Avoidance" Myth

Plan: design app to run on any cloud. Reality:
- Tooling 3× more complex
- Skills 3× expensive
- Networking cost real
- Lowest common denominator (no Spanner; no Lambda)
- "Theoretical portability" rarely exercised

Cost of avoidance often > cost of switching (if ever needed).

## When Lock-In Matters

- Acquired by org using different cloud
- Cloud raises prices dramatically
- Cloud sunsets a service
- Regulatory forces move
- Performance / SLA degrades

Rare; but possible.

## When Lock-In Doesn't Matter

- Stable cloud relationship
- Service is mature & well-supported
- Switching cost < migration cost when needed
- Competitive features outweigh switching risk

Most apps.

## Cost of Switching

DynamoDB → MongoDB: weeks of dev + data migration + testing.
Lambda → Cloud Functions: weeks if architecture is small; months if big.
S3 → GCS: weeks; egress $.
EC2 → Compute Engine: days (with Terraform); container images directly port.

Switching is expensive but usually not impossible.

## Mitigation Strategies

### Standards-Based
- Use Postgres (open source) → RDS or Aurora or Cloud SQL all support
- Use containers → run on EKS, GKE, AKS
- Use S3 API → GCS supports; minio supports
- Use Terraform → resources varied but tool common

### Abstraction Layers
- Crossplane: K8s-native multi-cloud
- Pulumi: cloud-agnostic IaC
- Knative: portable serverless

Cost: lowest-common-denominator features only.

### Strategic Picks
Pick portable for foundation (compute, storage, IAM); proprietary for clear value-add (BigQuery analytics, DynamoDB high-scale).

### Exit Plan
Document; estimate cost. If years > 5 to switch: you're locked. If <6 months: fine.

## Real-World Examples

### Dropbox Migration off AWS
2015-2017: built own DC; moved off S3.
Saved $75M/yr. Took years; many engineers.
Possible because Dropbox's scale was big enough.

For most: impossible.

### Snap Multi-Cloud
GCP + AWS. Significant complexity. Did it for negotiating leverage and resilience.

### Netflix on AWS
All-in AWS. Used proprietary services (Lambda, Kinesis, S3). Highly optimized for AWS. Lock-in by design; benefit > cost.

## Open Source Alternatives

For some lock-in concerns, open-source equivalents exist:
- S3 → MinIO (self-host)
- DynamoDB → ScyllaDB / Cassandra
- Lambda → OpenFaaS, Knative
- BigQuery → ClickHouse, Trino
- Cognito → Keycloak

If lock-in critical: pick one with OSS parallel.

## Negotiating Leverage

Multi-cloud strategy (even just lip service) gets you discounts. Sales reps fear losing.

But don't actually multi-cloud unless needed.

## The "Vendor Lock-In Tax"

Avoiding lock-in costs:
- Engineering time
- Performance (LCD)
- Slower innovation

Often: this tax > the lock-in cost itself.

## Best Practices

1. Use proprietary services where they add clear value
2. Use portable services where you can (Postgres, K8s, containers)
3. Use Terraform / OpenTofu — switching providers within Terraform easier
4. Document data dependencies; estimate switch cost periodically
5. Don't avoid Lambda because "lock-in" — Lambda is amazing
6. Don't avoid Aurora because "Postgres" — Aurora is amazing

## Hybrid Lock-In

Sometimes worse:
- Heavy AWS + heavy on-prem
- Can't fully exploit either
- Maintain expertise in both
- Network costs to bridge

If you've committed to cloud: commit. Don't half-stay on-prem.

## Common Mistakes

- Avoid Lambda → use EC2 + Cron → more ops; no scale
- Avoid Aurora → self-host Postgres → less reliable
- Multi-cloud abstraction → lose features both clouds offer
- Always-portable → never use cloud's actual strengths

## When To Genuinely Worry

- Regulator says "must be able to move"
- Customer contract demands it
- Strategic dependency (not vendor's customer's choice)
- Vendor relationship deteriorating

Otherwise: use the cloud's strengths.

## Quick Refs

Lock-in spectrum (pick consciously per workload):

```
Less lock-in  ← EC2 → K8s → RDS Postgres → DynamoDB → Lambda → Cognito → Step Functions →  More lock-in
```

Five kinds of lock-in — the last three usually bite harder than service-level lock:

| Type | Example |
|---|---|
| Service | DynamoDB schema doesn't port to MongoDB |
| Data | Moving 100 TB out of S3 = weeks + egress $ |
| Talent | Team re-skilling takes months |
| Operational | Runbooks/monitoring/IAM are cloud-specific |
| Contract | 3-yr committed-spend agreement |

OSS escape hatches if portability is truly required: S3 → MinIO · DynamoDB → ScyllaDB/Cassandra · Lambda → OpenFaaS/Knative · BigQuery → ClickHouse/Trino · Cognito → Keycloak.

Exit-plan rule of thumb: if switching would take >5 years you're effectively locked; if <6 months you're fine. Avoiding lock-in has its own "tax" (engineering time, lowest-common-denominator features) that often exceeds the lock-in cost itself.

## Interview Prep

**Mid**: "Vendor lock-in — concern?"

**Senior**: "Multi-cloud strategy tradeoffs."

**Staff**: "Migration off proprietary service — plan."

## Next Topic

→ [T03 — Multi-Cloud Strategy Tradeoffs](T03-Multi-Cloud.md)
