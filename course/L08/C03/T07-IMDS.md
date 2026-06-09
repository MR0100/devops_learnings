# L08/C03/T07 — EC2 Metadata Service (IMDSv1 vs IMDSv2)

## Learning Objectives

- Understand IMDS
- Force IMDSv2

## IMDS

Instance Metadata Service: HTTP endpoint accessible from inside EC2:
```
http://169.254.169.254/latest/meta-data/
```

Returns:
- Instance ID
- AMI ID
- Public IP, Private IP
- Hostname
- Region, AZ
- Security groups
- IAM role + temp creds!

Without auth historically. SDKs use it.

## The Problem (IMDSv1)

If your app has SSRF (server-side request forgery), attacker tricks app to fetch:
```
http://169.254.169.254/latest/meta-data/iam/security-credentials/MyRole
```

→ returns IAM creds. Attacker now has your role's permissions.

Capital One 2019 breach: SSRF → IMDSv1 → AWS creds → S3 exfil → 100M customer records.

## IMDSv2

Session-based:
```bash
# 1. Get token
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# 2. Use token
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/iam/security-credentials/MyRole
```

Requires PUT to get token; can't be forged via simple GET.

SSRF attackers (typical) can't make PUT requests; protected.

## Forcing IMDSv2

Launch template:
```yaml
MetadataOptions:
  HttpTokens: required        # only IMDSv2
  HttpPutResponseHopLimit: 1  # tokens can't traverse containers (default 1; tighter = safer)
  HttpEndpoint: enabled
```

Or via API:
```bash
aws ec2 modify-instance-metadata-options \
  --instance-id i-xxx \
  --http-tokens required \
  --http-put-response-hop-limit 1
```

For organization-wide enforcement: SCP:
```json
{
  "Effect": "Deny",
  "Action": "ec2:RunInstances",
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {"ec2:MetadataHttpTokens": "required"}
  }
}
```

## Hop Limit

`HttpPutResponseHopLimit`: how many hops the token response can traverse.

For pods in EKS using node IMDS: hop > 1 (token via Docker network).

For pure VM: hop = 1.

Better: use IRSA, not pod-level IMDS.

## Disabling IMDS Entirely

For containers using IRSA (not node creds):
```
HttpEndpoint: disabled
```

Reduces attack surface further.

## SDK Behavior

Modern AWS SDKs prefer IMDSv2 automatically:
- Try IMDSv2 first
- Fallback to IMDSv1 if instance allows

Force IMDSv2 only: incompatible SDKs (very old) break.

## What's In Metadata

```bash
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/
ami-id
ami-launch-index
hostname
iam/
instance-action
instance-id
instance-type
local-hostname
local-ipv4
mac
network/
placement/
public-hostname
public-ipv4
reservation-id
security-groups
services/
spot/
tags/
```

Read each:
```bash
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/instance-id
i-0abc123def456
```

Useful in bootstrap scripts.

## User Data

```bash
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/user-data
# Returns script
```

User data set at launch; appears here.

## IAM Creds

```bash
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/MyRole
{
  "AccessKeyId": "ASIA...",
  "SecretAccessKey": "...",
  "Token": "...",
  "Expiration": "2026-06-09T14:00:00Z"
}
```

SDKs auto-refresh.

## Instance Tags

Enabled per instance:
```bash
aws ec2 modify-instance-metadata-options --instance-id i-xxx --instance-metadata-tags enabled
```

Then:
```bash
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/tags/instance/Environment
prod
```

Useful for env-aware bootstrapping (avoid hardcoding).

## Spot Termination

Detect impending Spot termination:
```bash
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/spot/instance-action
# Returns 200 with action time if scheduled; 404 otherwise
```

Poll every 5s; on 200: drain.

## Checking IMDSv1 Usage

CloudWatch metric `MetadataNoToken`:
- Count of IMDSv1 calls
- Should be 0 if IMDSv2 enforced

For migration, find what's using IMDSv1; update or replace.

## Auditing

```bash
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,MetadataOptions]'
```

Check `HttpTokens`:
- `optional`: IMDSv1 allowed
- `required`: IMDSv2 only

## Migration to IMDSv2

1. Audit: who uses IMDSv1
2. Update SDKs
3. Test
4. Roll out HttpTokens=required
5. Enforce via SCP

## Best Practices

- IMDSv2 always required
- Hop limit 1 (or as needed)
- For containers: IRSA instead
- Monitor IMDSv1 calls
- Block via SCP

## Common Mistakes

- IMDSv1 enabled (legacy default)
- Hop limit too high
- IMDSv1 in containers (use IRSA)
- App calling IMDS instead of SDK (don't)

## SSRF Mitigation

Beyond IMDS:
- WAF rules blocking internal IP requests from app
- Network policies
- Audit code for URL-based fetches

## Quick Refs

```bash
# Get token
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# Use
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/

# Audit
aws ec2 describe-instances --filters Name=metadata-options.http-tokens,Values=optional
```

## Interview Prep

**Mid**: "IMDSv1 vs IMDSv2."

**Senior**: "Capital One breach root cause."

**Staff**: "Org-wide IMDSv2 enforcement."

## Next Topic

→ Move to [L08/C04 — VPC & Networking](../C04/README.md)
