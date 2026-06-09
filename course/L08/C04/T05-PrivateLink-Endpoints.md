# L08/C04/T05 — PrivateLink & VPC Endpoints (Interface, Gateway)

## Learning Objectives

- Use VPC endpoints
- Apply PrivateLink for private SaaS

## VPC Endpoints

Private connection from VPC to AWS service (or partner service via PrivateLink). No Internet, no NAT.

Two types:
- **Gateway endpoint**: S3, DynamoDB only. Free.
- **Interface endpoint**: most other AWS services + PrivateLink. Per-hour + GB.

## Gateway Endpoints

Add route to route table:
```
S3 prefix list → vpce-xxx
```

Traffic to S3 routed via endpoint, not Internet.

```bash
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxx \
  --service-name com.amazonaws.us-east-1.s3 \
  --vpc-endpoint-type Gateway \
  --route-table-ids rtb-xxx
```

Free. Use for S3 / DynamoDB always.

## Interface Endpoints

ENI in your subnets; DNS resolves to private IP.

```bash
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxx \
  --service-name com.amazonaws.us-east-1.secretsmanager \
  --vpc-endpoint-type Interface \
  --subnet-ids subnet-A subnet-B subnet-C \
  --security-group-ids sg-xxx
```

Each ENI: $0.01/hour. Per GB processed: $0.01.

For 24/7 × 3 AZs: ~$22/mo per endpoint. 

For high-traffic services: cheaper than NAT GW. Low traffic: NAT GW might be cheaper.

## Endpoint Policy

IAM-style policy on endpoint. Restrict what the endpoint can access:
```json
{
  "Statement": [{
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": [
      "arn:aws:s3:::my-bucket",
      "arn:aws:s3:::my-bucket/*"
    ]
  }]
}
```

Only your bucket accessible via this endpoint. Defense in depth.

## DNS Resolution

Interface endpoint creates private DNS:
- `secretsmanager.us-east-1.amazonaws.com` → private IP

Enable "Private DNS Names" in endpoint settings. SDKs use endpoint automatically.

For custom DNS: VPC must have DNS resolution + hostnames enabled.

## Services With Interface Endpoints

Hundreds. Examples:
- SSM (Systems Manager)
- Secrets Manager
- KMS
- ECR (image pulls)
- SQS, SNS
- CloudWatch (logs, metrics)
- Lambda
- STS
- Most APIs

For high-traffic AWS service access from private subnets: endpoint > NAT.

## PrivateLink

Mechanism behind interface endpoints. Also lets:
- Partners expose services to your VPC privately
- You expose services to other VPCs privately

## PrivateLink Service Provider

Create endpoint service:
```bash
aws ec2 create-vpc-endpoint-service-configuration \
  --network-load-balancer-arns arn:aws:elasticloadbalancing:... \
  --acceptance-required \
  --allowed-principals "arn:aws:iam::OTHER:root"
```

Backed by your NLB. Customers create endpoint to consume.

Why: SaaS available to customer VPCs without Internet.

## PrivateLink Consumer

Customer creates interface endpoint pointing at your service name.

Traffic from their VPC → PrivateLink → your NLB → your service.

No VPC peering. CIDRs can overlap. Secure.

## Use Cases

### S3 Without NAT
Save $1000s/mo. Always use S3 gateway endpoint.

### Lambda VPC Access to KMS / Secrets
Lambda in VPC accessing KMS via interface endpoint. No NAT cost.

### EKS Pulling ECR
ECR pulls via endpoint. Saves NAT for image traffic.

### SaaS to Customer VPC
Snowflake, MongoDB Atlas, Datadog: offer via PrivateLink.

## Cost Comparison

For 10 GB/day S3 traffic:
- Via NAT GW: $0.045 × 10 × 30 = $13.50/mo + $32 NAT GW base = $46
- Via Gateway endpoint: FREE
- Save: $46/mo per VPC per NAT GW

Multi-VPC, multi-AZ: significant savings.

For 100 GB/day Secrets Manager:
- Via NAT: $135 + NAT base
- Via Interface endpoint: $22 (3 ENIs) + $30 data = $52

## Centralized Endpoint Pattern

Don't create endpoints in every VPC. Central VPC with endpoints; share via Route53 Resolver or NLB:
- Shared Services VPC: all interface endpoints
- Other VPCs: send AWS service traffic via TGW to Shared Services
- Use Resolver rules for DNS

Saves endpoint cost; centralized management.

## Limits

- 50 endpoints per VPC (raise)
- 1 gateway endpoint per service per VPC (one S3, one DynamoDB)

## Interface vs Gateway

| | Gateway | Interface |
|---|---|---|
| Services | S3, DynamoDB only | Most |
| Cost | Free | Per hour + GB |
| Connection | Route table | ENI in subnet |
| DNS | Public name (route changes) | Private DNS |
| Cross-region | No | No |

## Endpoint per AZ

Interface endpoint: one ENI per subnet (each subnet in different AZ).

For HA: deploy in 3 AZs. Cost adds up; weigh against NAT savings.

## Conditions

Endpoint policy + IAM policy + bucket policy together. Tight control.

Common: bucket policy denies access NOT through endpoint:
```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "s3:*",
  "Resource": ["arn:aws:s3:::my-bucket", "arn:aws:s3:::my-bucket/*"],
  "Condition": {
    "StringNotEquals": {"aws:SourceVpce": "vpce-xxx"}
  }
}
```

Bucket only accessible via specific endpoint. No Internet, no other VPC.

## Monitoring

CloudWatch endpoint metrics:
- BytesProcessed
- PacketsIn/Out
- Active connections

Track usage / cost.

## Common Mistakes

- No S3 gateway endpoint (paying NAT for S3 traffic)
- Interface endpoint in one AZ (SPOF)
- No endpoint policy (too open)
- Forgetting DNS resolution settings
- Endpoint without route table association (gateway)

## Best Practices

- Always S3 + DynamoDB gateway endpoints
- Interface endpoints for high-traffic AWS services
- Endpoint policy for least privilege
- 3 AZs for HA
- Monitor / right-size
- Bucket policy enforcing endpoint

## PrivateLink for SaaS

Customer using SaaS via PrivateLink:
- Customer creates endpoint
- Endpoint connects to SaaS provider's NLB
- Traffic private; not via Internet
- Customer's data doesn't transit Internet

Increasingly required for enterprise.

## DX + PrivateLink

On-prem accesses AWS service via Direct Connect + PrivateLink, end-to-end private.

## VPC Endpoint Services in Other Regions

Per region. No cross-region endpoint (use Internet or VPN).

## Quick Refs

```bash
# Gateway endpoint
aws ec2 create-vpc-endpoint --vpc-id vpc-xxx --service-name com.amazonaws.us-east-1.s3 --vpc-endpoint-type Gateway --route-table-ids rtb-xxx

# Interface endpoint
aws ec2 create-vpc-endpoint --vpc-id vpc-xxx --service-name com.amazonaws.us-east-1.secretsmanager --vpc-endpoint-type Interface --subnet-ids ... --security-group-ids ...

# Service-specific endpoint policy
aws ec2 modify-vpc-endpoint --vpc-endpoint-id vpce-xxx --policy-document file://policy.json
```

## Interview Prep

**Mid**: "VPC endpoint vs NAT GW."

**Senior**: "Centralized endpoint pattern."

**Staff**: "PrivateLink for SaaS exposure."

## Next Topic

→ [T06 — Direct Connect & Site-to-Site VPN](T06-DX-VPN.md)
