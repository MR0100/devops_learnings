# L08/C04/T02 — Internet Gateway, NAT Gateway, NAT Instance

## Learning Objectives

- Use IGW correctly
- Pick NAT solution

## Internet Gateway (IGW)

Horizontally scaled, redundant, HA VPC component. Free.

One per VPC. Required for any Internet connectivity.

```bash
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --vpc-id vpc-xxx --internet-gateway-id igw-xxx
```

Then add route:
```
0.0.0.0/0 → igw-xxx
```

In subnet's route table → public subnet.

## Public IP Allocation

Instance gets public IP if:
- Subnet `MapPublicIpOnLaunch=true`
- Or explicitly assigned

Public IP = ephemeral (changes on stop/start).

EIP (Elastic IP): static; you own; can move between instances. $3.60/mo if not attached (wastes IPs).

## How IGW Works

IGW translates between private VPC IPs and Internet routable IPs.

Outbound:
```
Instance (10.0.1.5, public 54.x.x.x) → IGW translates → Internet (54.x.x.x source)
```

Inbound:
```
Internet → 54.x.x.x → IGW → 10.0.1.5
```

NAT for instances WITHOUT public IPs is different (NAT GW).

## NAT Gateway

For private instances to access Internet (outbound only):
```bash
aws ec2 create-nat-gateway --subnet-id subnet-public --allocation-id eipalloc-xxx
```

In public subnet (so it has IGW route). Allocate EIP.

Then private subnet's route table:
```
0.0.0.0/0 → nat-xxx
```

Private instance → NAT GW → IGW → Internet.

## NAT GW Pricing

- $0.045/hour
- $0.045/GB processed

For 100 GB/day:
- $0.045 × 24 × 30 = $32/mo (per hour)
- $0.045 × 100 × 30 = $135/mo (data)
- Total: ~$170/mo per NAT GW

Multiple AZs: per-AZ NAT GW = $510/mo for 3 AZs minimum.

Often biggest VPC cost.

## NAT GW HA

One NAT GW per AZ. If AZ-A NAT fails, AZ-A instances lose Internet.

Configure per-AZ route table → AZ-local NAT GW.

## NAT Instance (Legacy)

EC2 doing NAT. Cheaper but you manage:
- Patch OS
- Scale capacity (single instance bottleneck)
- HA (replacement on failure)
- Source/dest check disabled

Mostly deprecated. Use NAT GW.

Why NAT instance might still exist:
- Cost (tiny VPC)
- Need specific NAT features (port forwarding)

## NAT GW Throughput

Up to 100 Gbps per NAT GW. Scales automatically.

## Cost Optimization

NAT GW is expensive. Reduce:

### 1. VPC Endpoints
For AWS service traffic, use VPC endpoints; bypass NAT GW.
- Gateway endpoint for S3, DynamoDB: free
- Interface endpoints for other services: per hour + GB

```bash
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxx \
  --service-name com.amazonaws.us-east-1.s3 \
  --vpc-endpoint-type Gateway \
  --route-table-ids rtb-xxx
```

S3 traffic now never hits NAT.

### 2. Centralized Egress
One NAT GW in shared services VPC; all other VPCs route through TGW.

Saves vs one NAT per VPC per AZ.

Tradeoff: TGW costs $0.05/GB + TGW attachment fee.

### 3. Reduce Egress Volume
- Cache externally accessed data
- Compress
- Update less frequently
- Audit what's actually going out

### 4. CloudFront for Outbound
For uploading to S3 etc.: not applicable.
For pulling from external: still through NAT.

### 5. NAT Instance Fallback
For small / non-prod: NAT instance with auto-recovery.

## Egress-Only IGW (IPv6)

For IPv6: egress-only IGW (no inbound).

No NAT needed for IPv6 (each instance has public-routable IPv6).

```bash
aws ec2 create-egress-only-internet-gateway --vpc-id vpc-xxx
```

For dual-stack: use Egress-Only IGW for v6 egress; NAT for v4.

## Inbound from Internet

Only via IGW + public IP + SG/NACL allow.

NAT GW: outbound only (returning responses OK; new inbound from Internet not).

For inbound services: use ALB / NLB in public subnet; private targets behind.

## NAT and Source IP

Outbound from private instance: NAT GW substitutes its EIP as source.

If you whitelist source IPs at destination: get NAT GW EIP; lock to that.

## Bastion Host

For SSH to private instances (legacy):
- Bastion in public subnet
- SSH bastion → SSH private

Modern: SSM Session Manager (no SSH; IAM-auth).

```bash
aws ssm start-session --target i-xxx
```

Bypasses bastion. No SG ingress. Audited via CloudTrail.

## Internet Access Patterns

| Need | Solution |
|---|---|
| Public web server | Public subnet + IGW + public IP |
| Private outbound only | Private subnet + NAT GW |
| Private to AWS service | VPC endpoint |
| Private to specific Internet | NAT GW (or VPC PrivateLink to partner) |
| Inbound from Internet | LB in public; targets private |
| IPv6 outbound | Egress-Only IGW |

## Quotas

- 5 NAT GWs per AZ (raise)
- 1 IGW per VPC

## Monitoring

NAT GW metrics:
- BytesOutToDestination
- BytesInFromSource
- PacketsDropCount
- ErrorPortAllocation (port exhaustion)

If port exhaustion: too many concurrent connections; use multiple NAT GWs or sharded.

Each NAT GW: 55k concurrent connections per destination IP+port.

## Common Mistakes

- One NAT GW for all AZs (cross-AZ cost + SPOF)
- No VPC endpoints (NAT all the things)
- Forgetting EIP for NAT (transient IP)
- IGW for outbound from private (need NAT)
- Bastion when SSM available

## Anti-Pattern: Public Resources Without Need

DB in public subnet → bad. Even if SG locks down, accidental exposure risk.

Default: private. Public only when explicitly needed (LB, web).

## Best Practices

- 1 NAT GW per AZ for HA
- VPC endpoints to reduce cost
- SSM over bastion
- Egress-Only IGW for IPv6
- Monitor NAT throughput / port exhaustion

## Quick Refs

```bash
# NAT GW
aws ec2 create-nat-gateway --subnet-id subnet-pub --allocation-id eipalloc-xxx

# Routes for private subnet
aws ec2 create-route --route-table-id rtb-priv --destination-cidr-block 0.0.0.0/0 --nat-gateway-id nat-xxx

# IGW
aws ec2 attach-internet-gateway --vpc-id vpc-xxx --internet-gateway-id igw-xxx
```

## Interview Prep

**Mid**: "When need NAT GW."

**Senior**: "Reduce NAT GW cost."

**Staff**: "Egress strategy for 50-VPC org."

## Next Topic

→ [T03 — Route Tables, Network ACLs, Security Groups](T03-RT-NACL-SG.md)
