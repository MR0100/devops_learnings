# L26/C05 — Networking Cost Traps

## Topics

- **T01 Cross-AZ Traffic** — Microservices spanning AZs
- **T02 NAT Gateway Costs** — Hidden bills
- **T03 Data Egress** — To Internet

## Cross-AZ Cost

AWS charges $0.01/GB cross-AZ for each direction (so $0.02/GB round trip).

A chatty microservice (1000 req/s, 10 KB each) calling cross-AZ:
```
1000 * 10000 bytes/sec = 10 MB/s = 26 TB/month
26000 * 0.02 = $520/month for one chatty pair
```

Multiply across hundreds of pairs at scale: thousands of $/month.

### Mitigations

#### Topology-Aware Routing (K8s)
```yaml
apiVersion: v1
kind: Service
spec:
  internalTrafficPolicy: Local        # prefer same-node
  # or
  topologyKeys: ["kubernetes.io/hostname", "topology.kubernetes.io/zone", "*"]
```

#### Topology Aware Hints
EndpointSlices include topology hints; kube-proxy prefers local.

#### Per-AZ Caches
Cache layer in each AZ; reduce cross-AZ.

#### Locality-Aware Load Balancing
Service mesh (Istio, Cilium) supports zone-aware routing.

#### Co-locate Chatty Workloads
Pod affinity to keep dependent services together.

## NAT Gateway

$0.045/hr per NAT GW + $0.045/GB data processed.

A high-egress workload:
```
1 TB/day through NAT × 30 days = 30 TB
30000 × 0.045 = $1350/month/NAT (just data; not the $0.045/hr)
```

Plus 3 AZs × $0.045/hr × 730h = $98/month minimum for HA.

### Mitigations

#### VPC Endpoints (Gateway, free)
S3 and DynamoDB only. Traffic goes through gateway endpoint, not NAT.

#### Interface VPC Endpoints
For other AWS APIs (SQS, ECR, SSM, KMS, etc.) — $0.01/hr/AZ + $0.01/GB.
Cheaper than NAT egress for AWS API traffic.

#### Direct Internet for Public Subnets
For services that don't need NAT (public ALB, etc.), use IGW directly.

#### Centralized Egress
- Spoke VPCs route 0/0 to TGW
- TGW routes to Egress VPC
- One set of NAT GWs serves all
- Reduces total NAT count

### Egress VPC Pattern
```
Spoke VPC 1 ─┐
Spoke VPC 2 ─┼─→ TGW ─→ Egress VPC ─→ NAT GW ─→ IGW
Spoke VPC 3 ─┘
```

One AZ × NAT GWs instead of per-VPC.

## Data Egress to Internet

| Tier (per GB) | Price |
|---|---|
| First 10 TB/month | $0.09 |
| Next 40 TB | $0.085 |
| Next 100 TB | $0.07 |
| Over 150 TB | $0.05 |

CloudFront egress is cheaper (~$0.085/GB first 10TB, drops faster).

### Cheaper Egress Strategies
- **Cloudflare R2** — $0 egress (intentional disruption)
- **Backblaze B2** — $0.01/GB
- **CloudFront** — slightly cheaper than direct
- **AWS DataSync** for one-time transfer

### Egress Sources to Audit
- API responses
- User downloads
- Backups crossing region/cloud
- Logs to 3rd-party (Datadog, Splunk)
- Cross-cloud data syncs

## Inter-Region Replication

$0.02/GB for cross-region within AWS.

100 TB cross-region replication = $2000/month.

Strategies:
- Replicate only what's needed (not entire datasets)
- Compress before transfer
- Schedule during off-peak (no price diff, but bandwidth available)

## Cross-Cloud Egress

If you're sending data from AWS to GCP:
- Pay AWS egress ($0.09/GB)
- Pay GCP ingress (usually $0)
- Worst case: $90/TB cross-cloud

Plan to minimize.

## VPC Flow Logs Cost Analysis

Enable VPC Flow Logs → S3 → query with Athena. Find top talkers:

```sql
SELECT
  srcaddr, dstaddr,
  SUM(bytes) / 1024 / 1024 / 1024 AS gb_transferred
FROM vpc_flow_logs
WHERE day = '2026-06-09'
GROUP BY srcaddr, dstaddr
ORDER BY gb_transferred DESC
LIMIT 20;
```

Find chatty pairs; investigate; optimize.

## Avoid

### Public IP per Pod / Instance
Each public IP: $0.005/hr if charged. Use shared egress.

### Cross-Region Service Calls in Loops
Latency + cost. Cache or denormalize.

### Unbounded API Responses
Pagination prevents accidental TB transfers.

## Connect to FinOps

Networking costs are often "untaggable" — you can't easily attribute to a service. Strategies:
- VPC Flow Logs → attribute by source/dest IP → pod → service
- Pod-level network monitoring (Cilium Hubble)
- Manual apportionment (50% to service A based on traffic share)

## Interview Themes

- "Cross-AZ chatter — solve"
- "Reduce NAT GW costs"
- "Egress strategies"
- "VPC Flow Logs for cost analysis"
- "Cross-cloud data movement"
