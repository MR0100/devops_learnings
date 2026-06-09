# L08/C04/T01 — VPC Architecture (CIDR, Subnets, AZs)

## Learning Objectives

- Design VPC for production
- Plan CIDR space

## VPC Overview

Virtual Private Cloud: logically isolated network in AWS. Choose CIDR; subdivide into subnets.

One VPC: one region; many AZs.

## CIDR Planning

Pick VPC CIDR:
- /16 (65k IPs): typical for prod
- /20 (4k): smaller scope
- RFC 1918 ranges: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16

Avoid overlap with:
- On-prem networks (for VPN/DX)
- Other VPCs (for peering)
- Common defaults (192.168.0.0/24 home routers)

## Subnet Planning

For 3 AZs:
```
10.0.0.0/16 VPC

10.0.0.0/20    AZ-A public (4096 IPs)
10.0.16.0/20   AZ-A private app
10.0.32.0/20   AZ-A private DB
10.0.48.0/20   AZ-A reserved

10.0.64.0/20   AZ-B (same structure)
...

10.0.128.0/20  AZ-C
...
```

Leave room for growth.

## AWS Reserved IPs

In each subnet, AWS reserves 5:
- .0: network
- .1: VPC router
- .2: DNS
- .3: future use
- .last: broadcast

So /24 subnet (256) has 251 usable.

## Subnet Sizing

Smaller subnets: more boundaries, harder to expand.
Larger subnets: simpler, easier.

Recommendation: /24 (~250 IPs) or /22 (~1000 IPs) per subnet.

For EKS: pods consume VPC IPs (VPC CNI); plan large /18 or /16 for K8s subnets.

## Public vs Private

**Public Subnet**: route to IGW exists. Instances with public IP reachable.

**Private Subnet**: no IGW route. NAT for outbound.

Typical:
- LB in public
- App tier in private
- DB tier in private (extra-private; no NAT)

## DB-Only Subnet

For databases: no outbound Internet at all:
- No NAT GW route
- No IGW route
- Communicates only within VPC

Stronger security boundary.

## VPC Endpoints

Avoid Internet for AWS service traffic:
- Gateway endpoints (S3, DynamoDB): free
- Interface endpoints (others): per hour

```bash
aws ec2 create-vpc-endpoint --vpc-id vpc-xxx --service-name com.amazonaws.us-east-1.s3 --vpc-endpoint-type Gateway --route-table-ids rtb-xxx
```

Saves NAT cost; improves security.

## Routes

Route table maps CIDR → target:
```
10.0.0.0/16     local
0.0.0.0/0       igw-xxx          (public)
0.0.0.0/0       nat-xxx          (private)
```

One route table per subnet (associated).

## IGW

Internet Gateway: one per VPC; free.
Allows instances with public IPs (and routes via IGW) to reach Internet.

## NAT GW

For private subnet outbound:
- $0.045/hour
- $0.045/GB processed

One per AZ for HA. Often biggest cost item.

To save: VPC endpoints for AWS services, centralized egress (covered T07).

## Limits

Per VPC:
- 200 subnets
- 200 route tables
- 5 IGW (1 active)
- 2500 SGs
- 60 inbound + 60 outbound rules per SG

Per region:
- 5 VPCs (raise to 100s)
- 500 NAT GW (raise)

Raise via Service Quotas.

## Multi-AZ Design

Minimum 2 AZs, ideally 3, for HA.

```
VPC (10.0.0.0/16)
├── AZ-A
│   ├── Public /20
│   ├── Private app /20
│   └── Private DB /20
├── AZ-B (same)
└── AZ-C (same)
```

LB across all 3; app across all 3; DB primary in one + replica in others.

## Default VPC

Each region: one default VPC. Pre-configured.

Recommend: delete default; use custom. Forces explicit design.

```bash
aws ec2 delete-vpc --vpc-id vpc-default
```

## Tagging

```
Tags:
  Name: prod-vpc
  Environment: prod
  ManagedBy: terraform
```

Every resource. Required for cost allocation, audit.

## VPC Flow Logs

Capture traffic metadata:
```
src-ip src-port dst-ip dst-port protocol bytes packets action
```

Use for:
- Security investigation
- Debugging (why can't A reach B?)
- Cost analysis (where's traffic going?)

Store in S3 / CloudWatch.

```bash
aws ec2 create-flow-logs --resource-type VPC --resource-ids vpc-xxx --traffic-type ALL --log-destination s3://bucket/logs/
```

## DNS

VPC has built-in resolver:
- Resolve AWS services (s3.amazonaws.com)
- Resolve EC2 hostnames within VPC
- Optionally: Route53 Private Hosted Zone for custom domain

Enable DNS hostnames + resolution in VPC settings.

## DHCP Options

Set per VPC:
- domain-name-servers (default: AmazonProvidedDNS)
- domain-name
- ntp-servers
- netbios-name-servers

Custom: when you have on-prem AD / internal DNS to use.

## IPv6

Modern: dual-stack VPC.
- /56 allocated to VPC
- /64 per subnet
- Each instance gets public IPv6 (no NAT needed)

Adoption growing; eventually default.

## Network ACL

Subnet-level firewall; stateless. Allow + Deny rules; ordered.

Default: allow all. Most use SGs (stateful) instead.

NACL useful: defense in depth; explicit deny.

## Architecture Patterns

### 3-Tier
- Public: LB
- Private app: web/app servers
- Private DB: RDS, ElastiCache

### Hub-and-Spoke
- Central VPC (shared services, networking)
- Spoke VPCs per workload
- TGW connects

### VPC per Account
- Each AWS account: own VPC
- Connect via TGW

### Shared VPC
- One owner account creates VPC
- Shares subnets with other accounts via RAM
- Cost split; centralized network ops

## Sizing for K8s

EKS uses VPC CNI: pods consume VPC IPs.

For 100 nodes × 50 pods = 5000 IPs needed.
Plus services, ENIs.

Recommendation: /16 for prod EKS VPC.

## Common Mistakes

- Overlapping CIDRs (breaks peering)
- /24 VPC (runs out fast)
- Single AZ
- No flow logs
- Public DB
- Wide SG (0.0.0.0/0)
- Default VPC kept

## Best Practices

- Plan CIDR org-wide (IPAM)
- 3 AZs minimum
- Private app + DB subnets
- VPC endpoints for high-traffic services
- Flow logs always
- Documented architecture
- Tag everything
- IaC (Terraform / CloudFormation)

## Quick Refs

```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# Subnet
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24 --availability-zone us-east-1a

# IGW
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --vpc-id vpc-xxx --internet-gateway-id igw-xxx

# Route
aws ec2 create-route --route-table-id rtb-xxx --destination-cidr-block 0.0.0.0/0 --gateway-id igw-xxx
```

## Interview Prep

**Junior**: "Subnet vs VPC."

**Mid**: "Design VPC for 3-tier app."

**Senior**: "VPC for EKS at scale."

**Staff**: "Multi-account network architecture."

## Next Topic

→ [T02 — Internet Gateway, NAT Gateway, NAT Instance](T02-IGW-NAT.md)
