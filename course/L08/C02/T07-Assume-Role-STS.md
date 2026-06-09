# L08/C02/T07 — Assume Role, STS, External ID

## Learning Objectives

- Use STS to assume roles
- Understand external ID

## STS

Security Token Service. Issues short-lived AWS credentials.

Endpoint: `sts.amazonaws.com` (global) or regional (`sts.us-east-1.amazonaws.com`).

## Operations

| Op | Use |
|---|---|
| AssumeRole | IAM role from same/different account |
| AssumeRoleWithSAML | After SAML assertion |
| AssumeRoleWithWebIdentity | After OIDC token (IRSA, Cognito, GitHub) |
| GetSessionToken | Temp creds for IAM user (with MFA) |
| GetCallerIdentity | Who am I |
| GetFederationToken | Temp creds via IAM user (rare) |

## AssumeRole

```bash
aws sts assume-role \
  --role-arn arn:aws:iam::OTHER:role/CrossAccountRole \
  --role-session-name my-session
```

Returns:
```json
{
  "Credentials": {
    "AccessKeyId": "ASIA...",
    "SecretAccessKey": "...",
    "SessionToken": "...",
    "Expiration": "2026-06-09T14:00:00Z"
  }
}
```

Use these to call AWS as the role.

## Session Token

Difference from regular access keys: signed; tied to session; needed in `Authorization` header.

```bash
export AWS_ACCESS_KEY_ID=ASIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...
aws s3 ls    # uses assumed role creds
```

## Session Duration

Default: 1 hour. Configure:
```bash
aws sts assume-role --duration-seconds 3600 ...
```

Max: 12 hours (configurable per role).

Role chain (assume from already-assumed): max 1 hour each, regardless of role setting.

## External ID

For cross-account access (especially with third-party vendors):
```json
// Trust policy in role
{
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::VENDOR:root"},
  "Action": "sts:AssumeRole",
  "Condition": {
    "StringEquals": {"sts:ExternalId": "unique-per-customer-uuid"}
  }
}
```

Caller must provide same ID:
```bash
aws sts assume-role --external-id unique-per-customer-uuid ...
```

## Why External ID

Confused deputy problem:
- Vendor X serves many customers
- Customer A's role trusts Vendor X's account
- Customer B trusts Vendor X
- B asks Vendor X to read A's account: nothing prevents

External ID: unique secret per customer; vendor must provide. Stops B from impersonating A.

## When To Use External ID

- Third-party SaaS accessing your AWS (Datadog, Vanta, Snyk)
- Cross-account access where caller is shared

Not strictly needed when:
- Same-account assume
- You control both source and target accounts (still good practice)

## sts:AssumeRoleWithWebIdentity

For OIDC. Caller provides token from IdP (Cognito, Google, GitHub Actions).

```bash
aws sts assume-role-with-web-identity \
  --role-arn arn:... \
  --role-session-name my \
  --web-identity-token "$OIDC_TOKEN"
```

Used by:
- IRSA
- GitHub Actions OIDC
- Cognito federated

## sts:AssumeRoleWithSAML

For SAML federation.

```bash
aws sts assume-role-with-saml \
  --role-arn arn:... \
  --principal-arn arn:aws:iam::ACCT:saml-provider/Okta \
  --saml-assertion "$SAML_ASSERTION"
```

## GetSessionToken

For MFA-protected access:
```bash
aws sts get-session-token --serial-number arn:aws:iam::123:mfa/alice --token-code 123456
```

Returns 1-hour creds with MFA-asserted context. Useful for IAM user wanting MFA-required ops.

## GetCallerIdentity

```bash
aws sts get-caller-identity
```

Returns:
- UserId
- Account
- Arn

Useful for debugging: "what creds am I using right now?"

## Session Tags

Tag the session:
```bash
aws sts assume-role --tags Key=Project,Value=X ...
```

Available in policies as `aws:RequestTag/Project`.

For ABAC.

## Source Identity

Pass identity through:
```bash
aws sts assume-role --source-identity alice ...
```

CloudTrail records source identity. Audit who's behind the assume.

Force via condition:
```json
"Condition": {
  "StringEqualsIfExists": {"sts:SourceIdentity": "${aws:username}"}
}
```

## Role Chaining

Assume Role A; then from A, assume Role B. Limits:
- Max 1 hour per chain step (regardless of role setting)
- Each assume logged separately

Use for: complex cross-account / cross-service paths.

## CLI Profiles

Configure role assumption in `~/.aws/config`:
```ini
[profile prod]
role_arn = arn:aws:iam::PROD_ACCT:role/DeployRole
source_profile = main
mfa_serial = arn:aws:iam::123:mfa/alice

[profile main]
aws_access_key_id = ...
aws_secret_access_key = ...
```

```bash
aws s3 ls --profile prod
# Auto-assumes role; uses creds
```

For SSO:
```ini
[profile prod-sso]
sso_start_url = https://my-org.awsapps.com/start
sso_region = us-east-1
sso_account_id = 123
sso_role_name = Admin
region = us-east-1
```

```bash
aws sso login --profile prod-sso
aws s3 ls --profile prod-sso
```

## SDK Auto-Assume

AWS SDK looks for credentials in order:
1. Explicit (passed to client)
2. Environment vars
3. Shared credentials file
4. AWS_PROFILE
5. Container creds (ECS / EKS)
6. EC2 Instance Metadata Service

Assume role: SDK auto-handles refresh as creds expire.

## Audit

CloudTrail `AssumeRole` events:
- Who assumed
- What role
- Source IP / user agent
- Source identity

Alert on:
- Unusual source IP
- After-hours assumes
- Privileged roles assumed from non-admin

## Best Practices

- External ID for vendor third-party
- Restrict trust to specific roles (not whole account)
- Use Condition on Principal where possible
- Source Identity for audit
- Short sessions for sensitive ops
- MFA condition for high-risk

## Common Mistakes

- External ID not used for vendor access
- Trust :root in another account broadly
- Hardcoded ExternalId (treat as secret)
- Long-lived session tokens stored
- Role chaining for everything (complex)

## Quick Refs

```bash
# Get my current identity
aws sts get-caller-identity

# Assume role
aws sts assume-role --role-arn ... --role-session-name ...

# Use returned creds
export AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... AWS_SESSION_TOKEN=...

# Check role you're using
aws sts get-caller-identity
```

## Interview Prep

**Junior**: "What does AssumeRole do?"

**Mid**: "External ID purpose."

**Senior**: "Cross-account role chain — design."

**Staff**: "STS for vendor third-party integration."

## Next Topic

→ Move to [L08/C03 — EC2 & Compute](../C03/README.md)
