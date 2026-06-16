# L07/C08/T03 — Federated Identity (SAML, OIDC)

## Learning Objectives

- Understand SAML and OIDC
- Federate to cloud / SaaS

## Why Federate

One identity (employee account); access many systems.

Without federation: separate creds in AWS, GCP, GitHub, Datadog, Jira, ... = unmanageable.

With federation: SSO; consistent off-boarding; MFA enforced once.

## Identity Provider (IdP)

Authoritative source of identity:
- Okta, Auth0, Azure AD, Google Workspace, Ping
- Hosts user database; enforces MFA

## Service Provider (SP)

Application receiving federated identity:
- AWS, GCP, Slack, GitHub, etc.

## SAML 2.0

XML-based. Older but still huge in enterprise.

### Flow (SP-Initiated)
1. User visits SP (e.g., AWS console)
2. SP redirects to IdP with SAML AuthnRequest
3. User authenticates at IdP
4. IdP redirects back to SP with signed SAML assertion
5. SP validates signature; logs user in

### Components
- IdP metadata: URL, cert, public key
- SP metadata: ACS URL (assertion consumer), audience
- Assertion: signed XML with claims (user, attributes)

### Setup AWS SAML
1. Register IdP in AWS IAM (upload metadata)
2. Create role with trust policy allowing IdP
3. In IdP, map user groups to AWS roles
4. User signs in via IdP → assumes role

## OIDC (OpenID Connect)

Built on OAuth 2.0; JSON-based; modern.

### Flow (Authorization Code)
1. User visits app
2. App redirects to IdP /authorize
3. User authenticates
4. IdP redirects back with code
5. App exchanges code for tokens (ID, Access, Refresh)
6. App reads ID token claims

### ID Token (JWT)
```json
{
  "iss": "https://idp.example.com",
  "sub": "user123",
  "aud": "my-app",
  "exp": 1717584000,
  "name": "Alice",
  "email": "alice@example.com",
  "groups": ["admins"]
}
```

Signed by IdP; app verifies.

### Scopes
What access requested:
- `openid` (required for OIDC)
- `profile` (name, picture)
- `email`
- Custom (`my-app:admin`)

User consents; sees what's shared.

## SAML vs OIDC

| | SAML | OIDC |
|---|---|---|
| Format | XML | JSON (JWT) |
| Age | 2005 | 2014 |
| Mobile-friendly | Awkward | Native |
| Tokens | Assertion | ID + Access |
| Common use | Enterprise SaaS | New apps, OAuth |
| Standard | Yes | Yes |

Modern apps: OIDC.
Enterprise SaaS that's been around: SAML.

Many SaaS support both.

## OIDC Federation to AWS

```
1. Configure GitHub Actions OIDC provider in AWS
2. Create IAM role with trust policy:
   - Federated: arn:aws:iam::123:oidc-provider/token.actions.githubusercontent.com
   - Condition: sub like "repo:my-org/my-repo:ref:refs/heads/main"
3. Workflow assumes role
```

No long-lived AWS keys in GitHub.

## OAuth 2.0 vs OIDC

OAuth 2.0: authorization framework. Grants access to APIs.
OIDC: built on OAuth; adds identity (who's the user).

Use OAuth 2.0 alone for delegating API access (like "let GitHub act on your behalf").
Use OIDC for "log in with X".

## OAuth 2.0 Flows

- Authorization Code: most secure; web apps
- Authorization Code + PKCE: SPAs, mobile (no client secret)
- Client Credentials: service-to-service
- Refresh Token: long-lived sessions
- (Deprecated: Implicit, Password)

## JWT

JSON Web Token: signed string.

Structure: `header.payload.signature` (base64-url-encoded).

```
eyJhbGciOiJSUzI1NiIs...   header
.eyJzdWIiOiJ1c2VyMSI...    payload
.SflKxwRJSMeKKF2QT4f...    signature
```

Decoded payload (claims):
```json
{
  "sub": "user1",
  "exp": 1717584000,
  "iss": "issuer"
}
```

Verify signature with IdP public key (JWKs URL).

## JWT Pitfalls

- Don't use `alg: none` (no sig)
- Verify `iss`, `aud`, `exp`
- Public key rotation
- Don't store sensitive in unsigned JWT
- Stateless: can't easily revoke (use short expiry + refresh)

## Refresh Tokens

Long-lived (days); used to get new access tokens without re-login.
Store securely; rotate; revoke on logout.

Access tokens: short (minutes); use for API.

## Logout

Federated logout hard:
- Local logout: clear app session
- Single Logout (SLO): SAML/OIDC; tells IdP; IdP tells other apps
- Token revocation (OAuth): if supported

In practice: short token expiry + idle timeout.

## Multi-tenant

For SaaS serving multiple orgs:
- Each org has its own IdP
- App discovers IdP per email domain
- User redirected to their org's IdP

## SCIM

Provisioning protocol: IdP pushes user changes to apps.
- New hire: created in IdP, propagated to GitHub, Slack, etc.
- Promotion: groups updated
- Departure: deactivated everywhere

Combined with SSO: full lifecycle automation.

## AWS IAM Identity Center (formerly SSO)

AWS's managed SSO portal.
- Connect to external IdP (or use built-in)
- Users see all AWS accounts they have access to
- Assume role with one click
- CLI: `aws sso login`

Strongly recommended for orgs with 2+ AWS accounts.

## Common Mistakes

- IdP without MFA
- Per-app passwords (no federation)
- Long-lived tokens
- Trust IdP claims without validation
- One IdP for all (single point of failure)
- No deprovisioning flow

## Best Practices

- Single IdP per org (Okta, Azure AD, ...)
- MFA enforced
- Federate everything
- SCIM for provisioning
- Short-lived tokens; refresh
- Audit logs in IdP

## Modern Architecture

```
User → IdP (Okta) → MFA
              ↓
              SAML/OIDC
              ↓
  AWS, GCP, Slack, GitHub, Datadog, ...
```

Add new SaaS → just enable in Okta.

## Common Pitfall: Token Audience

JWT with audience for one app used to access another. Verify `aud` claim.

## ID Federation vs Workload Identity Federation

ID Federation: humans (SAML, OIDC).
Workload ID Federation: services (CI/CD OIDC to cloud).

Same principles; different principals.

## Quick Refs

SAML vs OIDC:

| | SAML 2.0 | OIDC |
|---|---|---|
| Format | XML assertion | JSON / JWT |
| Built on | Standalone | OAuth 2.0 |
| Best for | Legacy enterprise SaaS | New apps, mobile, CI/CD |
| Tokens | Signed assertion | ID + Access (+ Refresh) |

OAuth 2.0 flow picker: Authorization Code (web apps) · Authorization Code + PKCE (SPAs/mobile) · Client Credentials (service-to-service) · Refresh Token (long sessions). Implicit/Password are deprecated.

JWT must-verify: `iss`, `aud`, `exp`, and the signature against the IdP's JWKS — reject `alg: none`. Access tokens short-lived (minutes), refresh tokens long-lived and revocable.

Key terms: **IdP** = identity source (Okta/Azure AD) · **SP** = app consuming identity · **SCIM** = auto-provision/deprovision users to apps · **Identity Center** = AWS managed SSO portal (`aws sso login`). ID federation = humans; Workload Identity Federation = services/CI-CD.

## Interview Prep

**Mid**: "SAML vs OIDC."

**Senior**: "Set up GitHub Actions → AWS without keys."

**Staff**: "Identity architecture for 5000-employee org."

## Next Topic

→ Move to [L07/C09 — Choosing a Cloud](../C09/README.md)
