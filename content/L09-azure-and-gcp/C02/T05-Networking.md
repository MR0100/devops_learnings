# L09/C02/T05 — Networking (VPC, Cloud Load Balancing, Cloud Armor)

## Learning Objectives

- Build GCP networks
- Use global LBs

## VPC

= AWS VPC / Azure VNet, but **global**:
```bash
gcloud compute networks create my-vpc --subnet-mode=custom
gcloud compute networks subnets create my-subnet \
  --network=my-vpc \
  --range=10.0.1.0/24 \
  --region=us-central1
```

Unique: VPC spans regions. Subnets are regional.

## Subnet Modes

- **Auto**: GCP creates subnets per region (default; not for prod)
- **Custom**: you create subnets explicitly

Always use custom for prod.

## Firewall Rules

VPC-level (not per-instance):
```bash
gcloud compute firewall-rules create allow-https \
  --network=my-vpc \
  --allow=tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=https-server
```

Tags or SAs as targets.

## Tags vs Service Accounts (Targets)

```bash
# Tag
gcloud compute instances add-tags my-vm --tags=https-server

# Or SA
--target-service-accounts=my-sa@PROJ.iam...
```

SA target: more secure (immutable).

## Hierarchical Firewall

```bash
gcloud compute firewall-policies create-rule 1000 \
  --action=ALLOW --src-ip-ranges=10.0.0.0/8 \
  --layer4-configs=tcp:443 \
  --firewall-policy=org-policy
```

Org / folder-level firewall. Cascades to projects.

For: enterprise consistency.

## VPC Peering

```bash
gcloud compute networks peerings create my-peer \
  --network=vpc-a --peer-network=vpc-b \
  --peer-project=other-proj
```

Non-transitive (like AWS). Direct only.

## Shared VPC

Host project owns VPC; service projects use:
```bash
gcloud compute shared-vpc enable HOST_PROJ
gcloud compute shared-vpc associated-projects add SVC_PROJ --host-project=HOST_PROJ
```

For: centralized network; many teams.

## Cloud Router + Cloud NAT

NAT for outbound:
```bash
gcloud compute routers create my-router \
  --network=my-vpc --region=us-central1
gcloud compute routers nats create my-nat \
  --router=my-router --region=us-central1 \
  --nat-all-subnet-ip-ranges \
  --auto-allocate-nat-external-ips
```

= AWS NAT Gateway.

## Private Google Access

```bash
gcloud compute networks subnets update my-subnet \
  --region=us-central1 \
  --enable-private-ip-google-access
```

Resources without public IP: access Google APIs.

For: no Internet but GCP API access.

## Cloud Load Balancing

GCP LB types:

### Global External Application LB
HTTP/S, anycast, multi-region. = AWS CloudFront+ALB.

### Regional External Application LB
HTTP/S, single region. = ALB.

### Global External Network LB
TCP/UDP, anycast. = AWS NLB-like global.

### Regional External Network LB
TCP/UDP, single region. = NLB.

### Internal LBs
Same types but VPC-internal.

## Global HTTPS LB

```bash
gcloud compute backend-services create my-backend \
  --protocol=HTTP --port-name=http \
  --health-checks=my-hc --global

gcloud compute url-maps create my-url-map --default-service=my-backend
gcloud compute target-https-proxies create my-proxy --ssl-certificates=my-cert --url-map=my-url-map

gcloud compute forwarding-rules create my-fwd \
  --address=my-static-ip --global \
  --target-https-proxy=my-proxy --ports=443
```

Anycast IP: single IP routes globally.

## Backend Services

Sources:
- Instance Groups (MIG)
- NEG (Network Endpoint Group): VMs, K8s, hybrid
- Cloud Run / Functions / App Engine

## Network Endpoint Groups (NEG)

```bash
gcloud compute network-endpoint-groups create my-neg \
  --region=us-central1 \
  --network-endpoint-type=SERVERLESS \
  --cloud-run-service=my-svc
```

For: Cloud Run / Functions as LB backend.

## Cloud Armor

WAF + DDoS:
```bash
gcloud compute security-policies create my-policy
gcloud compute security-policies rules create 1000 \
  --security-policy=my-policy \
  --action=deny-403 \
  --src-ip-ranges=1.2.3.4/32
```

Attach to LB.

Rules:
- IP allow/deny
- Geo
- Preconfigured (OWASP top 10)
- Rate limiting
- Bot management

For: app protection.

## Cloud CDN

```bash
gcloud compute backend-services update my-backend --enable-cdn --global
```

CDN integrated with LB. Edge caching.

## Cloud DNS

```bash
gcloud dns managed-zones create my-zone \
  --dns-name=example.com. --description="My zone"

gcloud dns record-sets create www.example.com. \
  --zone=my-zone \
  --type=A --ttl=300 \
  --rrdatas=1.2.3.4
```

Public + private zones.

## Cloud Interconnect

= AWS Direct Connect / Azure ExpressRoute:
- Dedicated: 10/100 Gbps
- Partner: via partners
- Cross-cloud: with AWS, Azure (Partner Interconnect)

## VPN

```bash
gcloud compute target-vpn-gateways create my-vpn ...
```

Site-to-site IPSec.

## VPC Service Controls

Perimeter around resources:
- Restricts data flow
- Even with valid creds, blocks ex-perimeter access
- Compliance / exfiltration prevention

## Private Service Connect

Like AWS PrivateLink:
```bash
gcloud compute forwarding-rules create my-psc \
  --network=my-vpc --address=my-address \
  --target-service-attachment=...
```

For: access services privately.

## IPv6

Dual-stack VPC and LBs supported.

```bash
gcloud compute networks subnets create my-subnet \
  --stack-type=IPV4_IPV6 \
  --ipv6-access-type=EXTERNAL
```

## Comparison

| GCP | AWS | Azure |
|---|---|---|
| VPC | VPC (regional) | VNet |
| Subnet (regional) | Subnet (per-AZ) | Subnet |
| Firewall (VPC) | SG / NACL | NSG |
| Cloud NAT | NAT Gateway | NAT Gateway |
| Global LB | CloudFront+ALB+R53 | Front Door |
| Regional LB | ALB / NLB | App Gateway / LB |
| Cloud Armor | WAF + Shield | WAF + DDoS Protection |
| Cloud CDN | CloudFront | CDN |
| Interconnect | Direct Connect | ExpressRoute |
| Private Service Connect | PrivateLink | Private Endpoint |
| VPC SC | (no direct) | (no direct) |

## Quirks

- VPC = global (unique)
- Subnets are regional (not zonal)
- Routing tables: VPC-level (mostly automatic)
- No NACL equivalent (only firewall rules)

## Best Practices

- Custom subnets
- SA as firewall target (immutable)
- Hierarchical firewall (org policy)
- Cloud Armor on public LB
- Private Google Access
- Shared VPC for enterprise
- VPC SC for sensitive

## Common Mistakes

- Auto-mode VPC (no control)
- Tags for firewall (mutable)
- Cross-region peering misunderstanding (it's just network policy)
- No Cloud Armor
- Public IPs everywhere

## Quick Refs

```bash
# VPC
gcloud compute networks / subnets

# Firewall
gcloud compute firewall-rules create

# NAT
gcloud compute routers / nats

# LB
gcloud compute backend-services / url-maps / target-https-proxies

# Cloud Armor
gcloud compute security-policies

# DNS
gcloud dns managed-zones / record-sets

# VPN / Interconnect
gcloud compute vpn-gateways / interconnects
```

## Interview Prep

**Junior**: "GCP VPC."

**Mid**: "Global vs regional LB."

**Senior**: "Cloud Armor strategy."

**Staff**: "Multi-region GCP architecture."

## Next Topic

→ [T06 — Deployment Manager, Config Connector](T06-Deployment-Manager.md)
