# L08/C04/T07 — Egress Controls & Centralized Egress

## Learning Objectives

- Control outbound traffic
- Centralize for cost / security

## Why Control Egress

- Cost: egress to Internet $0.09/GB
- Security: prevent data exfiltration
- Compliance: limit destinations
- Performance: route via CDN

Without controls: any pod / instance can phone home anywhere.

## Default Behavior

- SG outbound: allow all
- NAT GW: any destination
- Internet: any

For sensitive: lock down.

## Egress Filtering

### SG Outbound
Restrict per workload:
```
DB-SG egress:
  443 to S3 prefix list
  53 to VPC DNS
  No 0.0.0.0/0
```

Prevents compromised DB from calling out.

### NACL
Subnet-level deny rules.

### Network Firewall
Managed L3-L7 filter:
- Allowlist domains
- Block by hostname (SNI inspection)
- Suricata rules
- IPS

```
Allow: github.com, *.amazonaws.com
Deny: everything else
```

Cost: $0.395/hour endpoint + $0.065/GB.

## Centralized Egress Pattern

Instead of NAT GW per VPC, single egress VPC:

```
Workload VPC-A ─┐
Workload VPC-B ─┼─ TGW ─→ Egress VPC ─→ NAT GW ─→ Internet
Workload VPC-C ─┘
```

Workload VPCs: no NAT. Default route → TGW → Egress VPC.

Egress VPC: NAT GW (one per AZ for HA).

## Centralized Egress Benefits

### Cost
Instead of N × 3 NAT GWs (one per VPC per AZ), only 3.

For 10 VPCs: $4900/mo → $510/mo = saves $4400/mo.

### Security
All egress through one path. Network firewall inspects everything.

### Observability
One place for flow logs.

### Compliance
Easier to demonstrate "no direct Internet egress."

## Cost

TGW adds:
- $0.05/hour per attachment
- $0.02/GB

For 10 VPCs × 100 GB/day:
- TGW: $360 + $600/mo (data through TGW)
- Save NAT: $4400 (as above)
- Net save: ~$3400/mo

Worth it at scale.

## Architecture

```
Egress VPC (10.255.0.0/16)
  Public subnets: NAT GW per AZ (with EIP)
  TGW attachment: in transit subnets

Workload VPC-X (10.X.0.0/16)
  Private subnets only
  TGW attachment
  Route: 0.0.0.0/0 → TGW
```

TGW route table:
- Workload routes propagated to Egress VPC route
- Egress VPC sends back 0.0.0.0/0 to all workloads

## Network Firewall Integration

Add Network Firewall in Egress VPC:

```
Workload → TGW → Egress firewall subnet → Firewall → NAT GW → Internet
```

Inspection on egress. Block bad domains; allow approved.

```
Stateful rules:
  alert tls any any -> any any (tls.sni; content:"badsite.com"; sid:1)
  pass http any any -> any any (msg:"Allow GitHub"; http.host; content:"github.com")
```

## Egress to AWS Services

Don't centralize for AWS:
- Use VPC endpoints in workload VPCs
- S3 / DynamoDB gateway (free)
- Interface endpoints for others

Saves egress (free vs $0.09/GB via NAT).

## Allowlist Strategy

Tier:
- Tier 1 (most apps): allow only S3 + ECR via endpoint
- Tier 2 (with egress): allowlist specific Internet (package mirrors, API partners)
- Tier 3 (open): few apps with full egress (CI runners)

## Per-Workload Egress

Some prefer per-VPC NAT for isolation:
- Workload's egress IP distinct (for partner allowlists)
- Independent egress
- Tradeoff: cost vs isolation

## DNS Egress

DNS queries also "egress":
- VPC DNS by default (private)
- Custom DNS: via Resolver outbound endpoint
- Block malicious domains: Route53 DNS Firewall

## DNS Firewall

```bash
aws route53resolver create-firewall-domain-list ...
aws route53resolver create-firewall-rule-group ...
```

Block lookups for known-bad domains.

## Egress Monitoring

VPC Flow Logs filtered for egress:
- Volume by destination
- Anomalies
- Unexpected destinations

Top destinations report → spot data exfil.

## Service-Specific Egress

### Lambda
In VPC: egress via NAT or VPC endpoints. Without VPC: AWS-managed (no charge to you).

### EKS Pods
Egress like any VPC traffic. Use VPC endpoints + network policy.

### Fargate
Each task has ENI; SG controls egress.

## CloudFront for Inbound Egress

When customers download from your S3:
- Direct: pay egress every request
- Via CloudFront: cache; cheaper after volume

For static content: always CloudFront.

## Common Mistakes

- All-allow SG outbound everywhere
- Per-VPC NAT GW × 3 AZs × 10 VPCs (massive bill)
- No VPC endpoints (S3 via NAT)
- No egress filtering (compromised → exfil free)
- No monitoring

## Best Practices

- VPC endpoints for AWS services
- Centralized egress for Internet (5+ VPCs)
- Network Firewall for sensitive
- DNS Firewall
- Restrict SG egress (no `0.0.0.0/0` default)
- Flow logs + analysis

## Egress IP Strategy

For partner allowlist:
- Reserve EIPs for NAT GWs
- Centralized: small set of IPs
- Per-VPC: many; harder

Document; partner adds; tested.

## Multi-Region Egress

Each region: own egress VPC + Network Firewall.
Or central in primary region with cross-region traffic (cost trade).

## Connect to Internet Without IGW?

For super-secure: no Internet at all.
- Use VPN to corp network
- Corp network is "Internet"
- Or NAT64 + private endpoints only

Rare; high security needs.

## Architecture Example

```
Org has:
  3 prod accounts (us-east-1, us-west-2)
  5 dev accounts
  1 shared services account

Shared Services:
  Egress VPC per region
    NAT GW × 3 AZs
    Network Firewall
  TGW connects all workload VPCs

Cost: ~$1500/mo for centralized egress
vs ~$10k/mo per-VPC NAT
```

## Quick Refs

```bash
# Network Firewall
aws network-firewall create-firewall ...

# DNS Firewall
aws route53resolver create-firewall-rule-group ...

# Flow Logs
aws ec2 create-flow-logs --resource-type VPC --resource-ids vpc-xxx --traffic-type ALL --log-destination s3://bucket/
```

## Interview Prep

**Mid**: "Why centralize egress."

**Senior**: "Network Firewall for compliance."

**Staff**: "Egress architecture for 50-VPC org."

## Next Topic

→ [T08 — Elastic Load Balancing (ALB, NLB, GWLB)](T08-Elastic-Load-Balancing.md)
