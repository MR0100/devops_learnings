# L08/C04 — VPC & Networking

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-VPC-Architecture.md) | VPC Architecture (CIDR, Subnets, AZs) | 1.5 hr |
| [T02](T02-IGW-NAT.md) | Internet Gateway, NAT Gateway, NAT Instance | 1 hr |
| [T03](T03-RT-NACL-SG.md) | Route Tables, Network ACLs, Security Groups | 1 hr |
| [T04](T04-Peering-TGW.md) | VPC Peering vs Transit Gateway | 1 hr |
| [T05](T05-PrivateLink-Endpoints.md) | PrivateLink & VPC Endpoints | 1 hr |
| [T06](T06-DX-VPN.md) | Direct Connect & Site-to-Site VPN | 1 hr |
| [T07](T07-Egress-Controls.md) | Egress Controls & Centralized Egress | 1 hr |
| [T08](T08-Elastic-Load-Balancing.md) | Elastic Load Balancing (ALB, NLB, GWLB) | 1 hr |

## VPC Reference Architecture

```
VPC 10.0.0.0/16   (us-east-1)
│
├── AZ a (us-east-1a)
│   ├── public  10.0.1.0/24    ← ALB, NAT GW, Bastion
│   ├── private 10.0.11.0/24   ← App tier
│   └── data    10.0.21.0/24   ← RDS, ElastiCache
├── AZ b (us-east-1b)
│   └── (same pattern)
└── AZ c (us-east-1c)
    └── (same pattern)

Route Tables:
- Public RT:  0.0.0.0/0 → IGW
- Private RT (per AZ): 0.0.0.0/0 → NAT GW in same AZ
- Data RT: no Internet route
```

### Subnet Sizing
- /24 = 251 usable IPs (5 reserved by AWS)
- /20 = 4091 usable
- Plan generously; can't change subnet CIDR after creation
- AWS reserves: .0 (network), .1 (router), .2 (DNS), .3 (future), .255 (broadcast)

## Internet Gateway (IGW)

- Attached to VPC (1:1)
- Required for public Internet
- Itself doesn't cost
- A subnet is "public" if its route table has `0.0.0.0/0 → IGW`
- Instances need public IP or Elastic IP for inbound

## NAT Gateway

- Outbound-only Internet from private subnets
- AZ-scoped (one per AZ for HA)
- ~$0.045/hr + $0.045/GB processed
- High-egress chatty workloads → big bills

### NAT Instance (legacy)
- Self-managed EC2 with iptables MASQUERADE
- Cheaper but ops burden
- Use NAT GW unless you need quirks (e.g., HA across regions)

## Security Groups (SG)

- Stateful — return traffic auto-allowed
- Per ENI (and instance)
- Allow rules only (no deny)
- Default outbound: allow all
- Default inbound: deny all (except references)

```hcl
# Terraform example
resource "aws_security_group" "app" {
  vpc_id = aws_vpc.main.id
  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]   # reference, not CIDR
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

**Reference other SGs** rather than CIDR ranges for inter-tier traffic — survives subnet changes.

## NACL (Network ACL)

- Stateless — must allow return traffic explicitly
- Per subnet
- Allow + deny rules
- Numbered (lowest first)
- Default NACL: allow all
- Custom NACL: deny all

> Modern practice: use SGs primarily. Use NACLs for subnet-wide bans (e.g., block known bad IPs from data subnet).

## Route Tables

- Each subnet has exactly one RT (default if unassigned)
- Routes evaluated longest-prefix-match
- Common destinations: local (VPC CIDR, automatic), IGW, NAT GW, VPC peering, TGW, VPC endpoint, VPN

## VPC Peering

- 1:1 between two VPCs
- Same or different account/region
- No transitive routing (A↔B and B↔C don't enable A↔C)
- CIDRs cannot overlap
- Best for: simple 2-VPC connections

## Transit Gateway (TGW)

- Hub-and-spoke for many VPCs + on-prem
- Transitive
- Route tables on TGW for traffic policy (segregation)
- Attachments: VPC, VPN, DX gateway, peering (cross-region or cross-account)
- $0.05/hr per attachment + data processing

### TGW Patterns
- Centralized egress (all VPCs → TGW → egress VPC → NAT GW → IGW)
- Inspection VPC (traffic through FW appliance)
- Cross-region (TGW peering)

## PrivateLink

Expose service privately to other VPCs.

### Components
- Producer: NLB in front of service
- VPC Endpoint Service: PrivateLink endpoint on the NLB
- Consumer: Interface VPC Endpoint (ENI) in their VPC

Benefits:
- No CIDR conflict (consumer connects to ENI IP)
- Private (no Internet)
- Cross-account / cross-VPC
- One-way (consumer → producer)

Use cases: SaaS providers exposing service to customers in private; internal service sharing.

## VPC Endpoints

### Gateway Endpoints (free)
- S3, DynamoDB only
- Route table entry; traffic stays in AWS network
- Use when in-VPC apps access S3/DynamoDB

### Interface Endpoints (Interface VPC Endpoint, aka PrivateLink to AWS services)
- For most AWS services (SQS, ECR, SSM, KMS, Secrets Manager, etc.)
- ENI per AZ; $0.01/hr/AZ + $0.01/GB
- Use when: avoiding NAT GW costs; private access requirement

**Big savings tip**: traffic via Interface Endpoints skips NAT GW data processing.

## Direct Connect

- Dedicated 1/10/100 Gbps fiber from on-prem to AWS
- Lower, consistent latency
- Egress cheaper (~$0.02/GB vs $0.09/GB Internet)
- Setup: cross-connect at DX location → VIF → VPC or TGW
- Best with redundant connections (different DX locations)

## Site-to-Site VPN

- IPSec tunnel over Internet
- AWS VPN GW or TGW as the AWS endpoint
- 1.25 Gbps per tunnel (active/active 2.5)
- Use: lower-volume hybrid; DR for DX

## Centralized Egress Pattern

```
Each Spoke VPC:
   - Private subnets
   - No NAT GW
   - Route 0.0.0.0/0 → TGW

TGW:
   - Routes egress traffic to Egress VPC

Egress VPC:
   - NAT GW per AZ
   - Optional FW (Network Firewall, Palo Alto VM-Series)
```

Saves NAT GW cost across many VPCs and enables central egress policies.

## Elastic Load Balancing

Distributes traffic across targets in multiple AZs. Modern types:

- **ALB (L7)**: HTTP/HTTPS/gRPC; routes on host, path, header, method; WAF + Cognito/OIDC auth; Lambda and IP targets.
- **NLB (L4)**: TCP/UDP/TLS; ultra-low latency, static/Elastic IP, source-IP preservation, PrivateLink front-end.
- **GWLB (L3)**: transparently inserts inline appliances (firewall/IDS) via GENEVE for centralized inspection.

Targets live in **target groups** (instance / ip / lambda / alb) with **health checks**; **listeners** apply rules. ALB cross-zone balancing is on and free; NLB/GWLB cross-zone is off by default. Prefer stateless apps over sticky sessions. CLB is legacy — avoid for new builds.

## Common Mistakes

- Too-small VPC CIDR (must recreate)
- NAT GW in only one AZ (SPOF)
- Overly permissive SGs (default to deny, add specific)
- Forgetting to add Gateway Endpoint for S3 (paying NAT processing)
- Cross-AZ chatter (DB in AZ-a, app in AZ-b)
- Wrong VPC CIDR for peering (overlap)

## Interview Themes

- "Design a multi-AZ VPC"
- "When VPC Peering vs TGW?"
- "How does PrivateLink work?"
- "NAT Gateway costs — how to reduce?"
- "Compare SG and NACL"
- "Centralized egress — design"
- "ALB vs NLB vs GWLB — when each?"
