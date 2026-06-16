# L26/C05/T02 — NAT Gateway Costs

## Learning Objectives

- Reduce NAT cost
- Use endpoints

## NAT Gateway

AWS NAT Gateway:
- $0.045/hr ($33/mo)
- $0.045/GB processed

For high traffic: huge.

## Example

10 TB/month through NAT:
- $33 hourly + $450 processing = $483/mo per NAT

If 3 NATs (one per AZ):
- $1450/mo

## Causes

Private subnet → Internet:
- All goes via NAT
- Even AWS services

## Mitigations

### VPC Endpoints

For AWS services:
```bash
aws ec2 create-vpc-endpoint --vpc-id ... --service-name com.amazonaws.us-east-1.s3
```

- S3: gateway endpoint (free)
- DynamoDB: gateway endpoint (free)
- Other: interface endpoint ($0.01/hr + GB)

For: bypass NAT.

## PrivateLink

For SaaS providers:
- Avoid public Internet
- Avoid NAT

## Shared NAT

Multi-VPC:
- One NAT in transit VPC
- Others use Transit Gateway
- Centralize NAT

## Self-Managed NAT

EC2 instance:
- Cheaper per GB
- More ops
- Single point

For: low-traffic non-prod.

## VPC Lattice

Newer:
- Service-to-service without NAT
- AWS-managed

## Tracking

```sql
SELECT 
  SUM(line_item_unblended_cost) AS nat_cost
FROM cur
WHERE line_item_usage_type LIKE '%NatGateway%'
```

## Hot Sources

Top NAT consumers:
- Container pulls (Docker Hub via NAT)
- Updates (apt update)
- External APIs
- AWS SDK calls

## Container Pulls

Mitigation:
- ECR pull-through cache
- Pre-pull
- ECR replication

For: avoid Docker Hub via NAT.

## Apt Updates

```bash
# Use VPC mirror or pull from S3
```

## Best Practices

- VPC endpoints for AWS services
- ECR pull-through
- Centralized NAT
- Monitor top consumers
- Per-AZ NAT (HA) or centralized (cost)

## Common Mistakes

- All traffic via NAT (S3, DynamoDB)
- No endpoints
- Per-AZ NAT for small (overkill)
- No monitoring (bill shock)

## Quick Refs

```bash
# Gateway endpoint
aws ec2 create-vpc-endpoint --service-name com.amazonaws.REGION.s3

# Interface endpoint
aws ec2 create-vpc-endpoint --vpc-endpoint-type Interface --service-name com.amazonaws.REGION.ec2

# Check NAT usage
aws ec2 describe-nat-gateways
CloudWatch BytesOutToDestination
```

## Interview Prep

**Mid**: "NAT cost."

**Senior**: "Reduce NAT."

**Staff**: "Network architecture."

## Next Topic

→ [T03 — Data Egress](T03-Egress.md)
