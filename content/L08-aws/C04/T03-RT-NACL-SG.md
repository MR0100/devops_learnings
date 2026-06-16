# L08/C04/T03 — Route Tables, Network ACLs, Security Groups

## Learning Objectives

- Use RT/NACL/SG correctly
- Defense in depth

## Route Table

Maps CIDR → next hop. Determines where packets go.

```
Destination       Target
10.0.0.0/16       local
0.0.0.0/0         igw-xxx
192.168.0.0/16    tgw-xxx
```

Each subnet associated with one route table. Multiple subnets can share.

## Local Route

Auto-added. CIDR of VPC → local. Always present.

## Default Route

`0.0.0.0/0`:
- igw-xxx: Internet via IGW (public)
- nat-xxx: Internet via NAT (private)
- tgw-xxx: through TGW
- vgw-xxx: through VPN
- Blackhole: drop

## Longest Prefix Match

Specific routes win over general:
```
0.0.0.0/0        → IGW
10.0.0.0/8       → TGW (to on-prem 10.x)
10.1.0.0/16      → VPC peering
```

Traffic to 10.1.5.x: matches /16 (most specific).

## Main Route Table

Each VPC has one. Default for subnets not explicitly associated.

Best practice: don't use main; explicitly associate each subnet.

## Security Groups (SG)

Stateful firewall at ENI / instance level.

- Allow rules only (no deny)
- Inbound + outbound
- Stateful: response auto-allowed
- Reference: CIDR, prefix list, other SG

```
Inbound:
  Port 443 from 0.0.0.0/0
  Port 22 from MyIP/32
  Port 5432 from app-sg

Outbound:
  All to 0.0.0.0/0  (default)
```

## SG Referencing SG

```
DB-SG inbound: port 5432 from app-sg
```

Any instance with `app-sg` can connect.

Powerful: no IP management; team grants based on role.

## Default SG

Each VPC has default SG. New ENIs in this SG by default.

Recommendation: don't use default; create explicit per role.

## SG Limits

- 60 inbound + 60 outbound rules per SG
- 5 SGs per ENI (raise to 16)

For more rules: split SGs.

## Prefix Lists

Named lists of CIDRs (yours or AWS-managed). Reference in SG / route table.

```bash
aws ec2 create-managed-prefix-list --address-family IPv4 --max-entries 10 --prefix-list-name corp-cidrs
```

Update once; affects all references.

## AWS-Managed Prefix Lists

For AWS service IPs (CloudFront, S3, etc.):
```
com.amazonaws.us-east-1.s3 → list of S3 IPs
```

Auto-updated.

## NACL (Network ACL)

Subnet-level firewall. Stateless. Allow + Deny rules; ordered (lowest rule number wins).

```
Rule    Type    Protocol  Port  Source    Allow/Deny
100     HTTP    TCP       80    0.0.0.0/0  ALLOW
200     SSH     TCP       22    1.2.3.4/32 DENY
*       ALL     ALL       ALL   0.0.0.0/0  DENY
```

Stateless: must allow return traffic explicitly.

## Default NACL

Allow all in / out. Subnets associated with default unless explicit.

## When NACL

- Subnet-level explicit boundary
- Block specific IP at edge
- Defense in depth (with SG)

Most use only SGs; NACL for specific compliance / blocklist.

## SG vs NACL

| | SG | NACL |
|---|---|---|
| Level | Instance | Subnet |
| Stateful | Yes | No |
| Rules | Allow only | Allow + Deny |
| Order | N/A (all eval) | Numbered |
| Default | Deny all | Allow all |
| Per | ENI | Subnet |

## Best Practices

SG:
- Never `0.0.0.0/0` on 22 (SSH); use SSM
- Reference SGs by name (not IP)
- One SG per role (web-sg, db-sg, app-sg)
- Egress restrict for sensitive (DB shouldn't egress to Internet)

NACL:
- Default allow-all; lock with SG
- Use for explicit blocks
- Remember stateless (return traffic)

Route Table:
- Per-subnet, per-AZ NAT route
- Explicit (no default to main)
- Document blackholes

## SG Strategy

Tier-based:
```
internet-sg: ALB allowed from Internet
web-sg: app from ALB
app-sg: backend from web
db-sg: DB from app
```

Each tier explicit.

## Stateful Behavior

SG: connection established, response auto-flows back.

```
Outbound: TCP to port 80 (allowed)
Inbound response: auto-allowed (state tracked)
```

NACL: stateless. Outbound rule needed for request; inbound rule needed for response.

Common gotcha: ephemeral ports for return.

## Audit

```bash
# List SGs
aws ec2 describe-security-groups

# Rules in SG
aws ec2 describe-security-group-rules --filters Name=group-id,Values=sg-xxx

# Find 0.0.0.0/0 on 22 / 3389
aws ec2 describe-security-groups --filters Name=ip-permission.cidr,Values=0.0.0.0/0,Name=ip-permission.from-port,Values=22
```

## SG with Lambda / RDS / ECS

Many AWS services accept SG association:
- Lambda in VPC: SG controls outbound
- RDS: SG controls inbound to DB
- ECS task: SG per task
- ALB / NLB: SG controls who can connect

Treat consistently.

## Common Mistakes

- 0.0.0.0/0 on 22 / 3389
- Default SG (everything)
- Egress unrestricted from sensitive
- SG referencing IPs (won't follow new instances)
- NACL stateless return blocking

## Egress Filtering

Default outbound: all allow. For sensitive:
```
DB-SG outbound:
  TCP 443 to S3 prefix list  (backups)
  TCP 80 to package mirror IP
  ... explicit
```

Limits damage if compromised.

## Cross-Account SG

SG can't be referenced across accounts directly.

Workarounds:
- Reference IP CIDRs
- VPC peering with name resolution
- Or use shared VPC

## Migrating SG Rules

For changes:
- Add new rule
- Test
- Remove old

Avoid removing → re-adding (window without).

## Logging

VPC Flow Logs show SG / NACL decisions:
```
action: ACCEPT / REJECT
```

Investigate REJECT to find blocked legitimate traffic.

## Defense in Depth

Layer:
1. WAF (L7 attack)
2. NACL (subnet-level deny)
3. SG (instance-level allow)
4. Host firewall (iptables)
5. App-level auth

Each layer catches what others miss.

## Network Firewall

Managed firewall for VPC; deep packet inspection; Suricata rules.
For: high-security, compliance, IPS/IDS.

Pricing: hourly + GB processed.

## Common Mistakes

- Wide CIDR in SG (0.0.0.0/0)
- Forgetting return traffic (NACL)
- SG with no description
- Hardcoded IPs (use prefix lists)
- Outbound allow-all from sensitive

## Quick Refs

```bash
# Create SG
aws ec2 create-security-group --group-name app-sg --description "App tier" --vpc-id vpc-xxx

# Add rule
aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 443 --cidr 0.0.0.0/0

# Reference another SG
aws ec2 authorize-security-group-ingress --group-id sg-app --protocol tcp --port 5432 --source-group sg-db
```

## Interview Prep

**Junior**: "SG vs NACL."

**Mid**: "Design SGs for 3-tier app."

**Senior**: "Audit SGs for least privilege."

**Staff**: "Network microsegmentation strategy."

## Next Topic

→ [T04 — VPC Peering vs Transit Gateway](T04-Peering-TGW.md)
