# L08/C02/T02 — Trust Policies vs Permission Policies

## Learning Objectives

- Distinguish the two policy types
- Write correct trust policies

## Two Policies Per Role

| | Trust Policy | Permission Policy |
|---|---|---|
| Says | who can assume | what assumed can do |
| Required | yes (every role) | usually (unless empty role) |
| Edit | role's trust relationship | attached policies |
| Limit | one per role | up to 10 attached |

## Trust Policy

Specifies which Principal can call `sts:AssumeRole` on this role.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Service": "ec2.amazonaws.com"
    },
    "Action": "sts:AssumeRole"
  }]
}
```

This is a resource-based policy (on the role).

## Service Principal

For AWS services:
```json
{"Service": "lambda.amazonaws.com"}
{"Service": "ecs-tasks.amazonaws.com"}
{"Service": ["ec2.amazonaws.com", "ssm.amazonaws.com"]}    # multiple
```

## AWS Principal

For cross-account or IAM principals:
```json
{"AWS": "arn:aws:iam::OTHER_ACCT:root"}       # whole account
{"AWS": "arn:aws:iam::OTHER_ACCT:role/X"}     # specific role
{"AWS": "arn:aws:iam::OTHER_ACCT:user/alice"} # specific user
```

`:root` = anyone in account (still need their identity policy to allow AssumeRole).

## Federated Principal

For external IdPs:
```json
{"Federated": "arn:aws:iam::ACCT:saml-provider/Okta"}
{"Federated": "arn:aws:iam::ACCT:oidc-provider/token.actions.githubusercontent.com"}
{"Federated": "cognito-identity.amazonaws.com"}
```

## Conditions in Trust

Tighten who can assume:
```json
{
  "Effect": "Allow",
  "Principal": {"AWS": "arn:aws:iam::OTHER:root"},
  "Action": "sts:AssumeRole",
  "Condition": {
    "StringEquals": {
      "sts:ExternalId": "my-shared-secret-uuid"
    }
  }
}
```

ExternalId: prevent confused deputy. Vendor third-party should require unique ID per customer.

For OIDC (GitHub Actions):
```json
{
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:ref:refs/heads/main"
    }
  }
}
```

Lock to specific repo + branch.

## Permission Policy

What the assumed role can do — actions on AWS resources.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::my-bucket/*"
  }]
}
```

Attached to role (via AttachRolePolicy or PutRolePolicy for inline).

## Both Matter

Role assumed:
1. Trust policy says assume ALLOWED
2. Caller's identity policy says AssumeRole ALLOWED on this role
3. STS returns temp creds
4. Assumed role's permission policy applies

For cross-account: trust in target + identity in source.

## Common Patterns

### EC2 Instance Profile
```json
// Trust
{"Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}

// Permission
{"Action": "s3:GetObject", "Resource": "..."}
```

EC2 auto-assumes role; uses temp creds via metadata.

### Lambda Execution Role
```json
// Trust
{"Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}

// Permission
{"Action": "logs:CreateLogStream", ...}
```

### Cross-Account
```json
// Trust (in account B)
{
  "Principal": {"AWS": "arn:aws:iam::AAAA:role/SrcRole"},
  "Action": "sts:AssumeRole",
  "Condition": {"StringEquals": {"sts:ExternalId": "xyz"}}
}

// Source identity policy (in account A)
{
  "Action": "sts:AssumeRole",
  "Resource": "arn:aws:iam::BBBB:role/TargetRole"
}
```

### GitHub Actions OIDC
```json
// Trust
{
  "Principal": {"Federated": "arn:aws:iam::ACCT:oidc-provider/token.actions.githubusercontent.com"},
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
    },
    "StringLike": {
      "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:*"
    }
  }
}
```

`sts:AssumeRoleWithWebIdentity` instead of `sts:AssumeRole` for federated.

## sts:AssumeRole vs Variants

| Action | Use |
|---|---|
| sts:AssumeRole | Standard (cross-account, services) |
| sts:AssumeRoleWithSAML | SAML federation |
| sts:AssumeRoleWithWebIdentity | OIDC / web (Cognito, GitHub) |

Trust policy actions must match.

## Source Identity

Pass identity through assume:
```json
{
  "Condition": {
    "StringEquals": {"sts:SourceIdentity": "${aws:username}"}
  }
}
```

CloudTrail records source identity; audit who's behind the assume.

## Session Tags

Tag the session on assume; condition on tags:
```json
"Condition": {
  "StringEquals": {"aws:RequestTag/Project": "my-project"}
}
```

For ABAC.

## Editing Trust Policy

```bash
aws iam update-assume-role-policy --role-name MyRole --policy-document file://trust.json
```

Or via console: Trust Relationships tab.

CAREFUL: bad trust policy can lock you out of role.

## Confused Deputy

A scenario: legitimate service uses your role on behalf of someone unauthorized.

Mitigation: ExternalId in cross-account; or `aws:SourceAccount` condition.

```json
"Condition": {
  "StringEquals": {"aws:SourceAccount": "MY_ACCT_ID"}
}
```

For services like S3 → SNS where attacker could trick.

## Trust to Service vs Account

```json
// Service: AWS service assumes for you
{"Principal": {"Service": "ec2.amazonaws.com"}}

// Account: another account assumes for them
{"Principal": {"AWS": "arn:aws:iam::OTHER:root"}}
```

Different use cases.

## Anti-Patterns

- Trust :root in another account without ExternalId
- Trust account without restricting which roles in that account
- Trust everyone (Principal: *)
- Missing aws:SourceAccount in service trust
- Overly permissive in GitHub OIDC sub

## Best Practices

- ExternalId for vendor third-party access
- aws:SourceArn / aws:SourceAccount conditions for service triggers
- Limit OIDC sub to specific repo/branch
- Audit trust policies regularly (Access Analyzer)
- One role per use case (granular trust)

## Common Mistakes

- Permission policy missing AssumeRole (caller can't even try)
- Trust mismatched action (AssumeRole vs AssumeRoleWithWebIdentity)
- Forgetting region (some condition keys are region-specific)
- Path in role ARN (default `/`)

## Quick Refs

```bash
# View a role's trust policy
aws iam get-role --role-name MyRole --query Role.AssumeRolePolicyDocument

# Update the trust policy
aws iam update-assume-role-policy --role-name MyRole --policy-document file://trust.json

# Assume a role (standard)
aws sts assume-role --role-arn arn:aws:iam::222233334444:role/TargetRole --role-session-name demo --external-id xyz

# Assume via OIDC web identity (e.g. GitHub Actions)
aws sts assume-role-with-web-identity --role-arn arn:... --role-session-name ci --web-identity-token "$OIDC_TOKEN"
```

## Interview Prep

**Mid**: "Trust vs permission policy."

**Senior**: "GitHub Actions → AWS without keys."

**Staff**: "ExternalId for vendor access; why."

## Next Topic

→ [T03 — Resource-Based Policies](T03-Resource-Based-Policies.md)
