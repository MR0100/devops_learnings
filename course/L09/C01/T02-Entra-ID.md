# L09/C01/T02 — Entra ID (formerly Azure AD)

## Learning Objectives

- Understand Entra ID
- Use for cloud + on-prem identity

## Entra ID

Microsoft's identity:
- Cloud IdP
- SSO
- MFA
- Conditional Access
- Identity Protection

Rebranded from "Azure AD" (2023). Same product.

## Vs AD (On-Prem)

| | AD (DS) | Entra ID |
|---|---|---|
| Protocol | LDAP, Kerberos | OAuth, OIDC, SAML |
| For | On-prem apps | Cloud + modern apps |
| Hierarchy | OU tree | Flat (mostly) |
| Sync | Replication | Entra Connect (sync) |

Many orgs run both; Entra Connect syncs.

## Users

```bash
az ad user create --display-name "Alice" --user-principal-name alice@example.com --password ...
```

Or sync from on-prem AD.

## Groups

Security or M365:
```bash
az ad group create --display-name "Engineers" --mail-nickname engineers
az ad group member add --group "Engineers" --member-id USER_ID
```

For: RBAC assignment.

## Service Principals

For apps:
```bash
az ad sp create-for-rbac --name my-app
# Outputs: appId, password, tenant
```

Like AWS IAM users for services.

For: CI/CD, automation.

## Managed Identity

Azure-managed; no creds:
```bash
az identity create --name my-mi --resource-group myrg
```

Two types:
- **System-assigned**: tied to resource
- **User-assigned**: standalone, attachable to many

For: VMs, AKS, Functions; no secrets to manage.

## Workload Identity (AKS)

K8s SA → Entra:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    azure.workload.identity/client-id: CLIENT_ID
  name: my-sa
```

Pod uses SA → token exchanged for Entra → Azure resources.

Equivalent to IRSA (EKS).

## Conditional Access

Policies:
- Require MFA from outside corp network
- Block non-managed devices
- Block by country
- Require compliant device

```
If user = HR group AND location = outside US:
  Require MFA + managed device
```

For: zero trust.

## MFA

Methods:
- Authenticator app (push notification)
- Phone (SMS, voice — less secure)
- FIDO2 / WebAuthn (passwordless)
- Windows Hello

For all admin: MFA mandatory.

## Privileged Identity Management (PIM)

JIT elevation:
- "I'm an eligible Owner; activate for 1 hr"
- Reason required
- Approval workflow
- Audit log

For: reduce standing access.

## Identity Protection

ML-driven:
- Detects compromised accounts
- Risky sign-ins
- Atypical travel
- Leaked credentials

Auto-actions: force MFA, block.

## RBAC

Built-in roles:
- Owner
- Contributor
- Reader
- User Access Administrator
- (many service-specific)

Assign to user, group, SP:
```bash
az role assignment create \
  --assignee USER \
  --role Contributor \
  --scope /subscriptions/SUB_ID
```

## Custom Roles

```json
{
  "Name": "Storage Manager",
  "Actions": [
    "Microsoft.Storage/*",
    "Microsoft.Resources/subscriptions/resourceGroups/read"
  ],
  "NotActions": ["Microsoft.Storage/storageAccounts/delete"],
  "AssignableScopes": ["/subscriptions/SUB_ID"]
}
```

```bash
az role definition create --role-definition role.json
```

For: principle of least privilege.

## App Registrations

OAuth client setup:
- App ID
- Secret or cert
- Redirect URI
- Permissions

For: integrating apps with Entra.

## Federation (External IDs)

B2B: invite external users.
B2C: customer-facing.

For: vendor access; SaaS apps.

## Federated Credentials

OIDC:
- GitHub Actions → Entra (no secret)
- AWS → Entra

```bash
az ad app federated-credential create \
  --id APP_ID \
  --parameters '{"name": "github", "issuer": "https://token.actions.githubusercontent.com", ...}'
```

For: cross-cloud / CI federation.

## Single Sign-On

Configure SaaS apps:
- SAML
- OIDC
- Password-based (less secure)

Entra as IdP.

## Comparison to AWS

| | AWS IAM Identity Center | Entra ID |
|---|---|---|
| Identity | SSO + IAM | Entra ID |
| Federation | SAML, OIDC | SAML, OIDC |
| MFA | Yes | Yes |
| Conditional Access | (via SCPs partially) | Robust |
| PIM | IAM Identity Center (basic) | PIM (mature) |

Entra: enterprise focus, mature.

## Audit Logs

```bash
az monitor activity-log list --resource-group myrg
```

Or via Sign-In Logs (Entra portal).

For: compliance, forensics.

## Best Practices

- MFA everywhere (admin mandatory)
- Conditional Access policies
- PIM for prod admin
- Managed Identity (not creds)
- Workload Identity (AKS)
- Audit logs
- No standing prod admin

## Common Mistakes

- Static SP secrets (rotate)
- Owner role too broad
- No MFA
- Shared admin accounts
- No CA policies

## Entra Connect

Sync on-prem AD → Entra:
- User/group sync
- Password hash sync
- Pass-through auth (no hash)
- AD FS federation

For hybrid identity.

## Quick Refs

```bash
# Users
az ad user list
az ad user create --display-name NAME --user-principal-name UPN

# Groups
az ad group create
az ad group member add

# SP
az ad sp create-for-rbac

# Role assignment
az role assignment create --assignee X --role Y --scope Z
```

## Interview Prep

**Junior**: "What's Entra ID."

**Mid**: "Managed Identity vs SP."

**Senior**: "Conditional Access design."

**Staff**: "Hybrid identity at FAANGM scale."

## Next Topic

→ [T03 — Compute (VMs, VMSS, AKS, App Service, Functions)](T03-Compute.md)
