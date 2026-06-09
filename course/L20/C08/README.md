# L20/C08 — Zero Trust

## Topics

- **T01 BeyondCorp Model** — Google's framework
- **T02 Service-to-Service Identity (SPIFFE/SPIRE)** — Workload identity
- **T03 mTLS Everywhere** — Encryption + auth between services

## The Old Model: Castle and Moat

```
[Untrusted Internet]
      ↓
[Firewall / VPN]
      ↓
[Trusted Internal Network]
   - Free to talk between services
   - Implicit trust
```

Problems:
- One breach = lateral movement
- VPN is just a key; stolen = full access
- Remote work / SaaS broke the perimeter
- Cloud / hybrid have no clean perimeter

## Zero Trust

Three tenets:
1. **Verify explicitly** — every request, regardless of source
2. **Least privilege** — minimum access per request
3. **Assume breach** — design for the inevitable

No implicit trust based on network location.

## BeyondCorp (Google, 2014)

Google's seminal zero-trust paper. Key elements:

- **Device inventory**: every device known + assessed
- **User identity**: SSO with strong factor
- **Per-request authorization**: Access Proxy evaluates each request
- **No VPN**: services reachable from anywhere via authorized device

User experience:
- No VPN; access from any network
- But strong device check + identity check per request

## Workload Identity (Service-to-Service)

Each workload (service, pod, function) has its own identity — not a shared service account.

### SPIFFE (Standard)
> Secure Production Identity Framework for Everyone

A SPIFFE ID:
```
spiffe://example.org/ns/production/sa/myapp
```

SVIDs (SPIFFE Verifiable Identity Documents): X.509 certs or JWTs.

### SPIRE (Implementation)
- Reference implementation of SPIFFE
- Issues SVIDs to workloads
- Authenticates workloads via "node attestation" + "workload attestation"

### Istio + SPIFFE
Istio's `cluster.local/ns/NS/sa/SA` identity is a SPIFFE-compatible ID. Used for mTLS.

### Cloud-Specific
- **AWS IRSA / Pod Identity**: K8s SA → AWS role
- **GCP Workload Identity**: K8s SA → GCP SA
- **Azure Workload Identity**: K8s SA → Entra ID app

These are all forms of workload identity.

## mTLS Everywhere

Mutual TLS:
- Client presents cert; server verifies
- Server presents cert; client verifies
- Both authenticated

### Why
- Verifies identity, not just IP
- Encrypts traffic (defense in depth)
- Standard mechanism

### Implementation
- Manual: cert distribution + rotation = pain
- Service mesh: auto (Istio, Linkerd, Consul Connect)
- SPIFFE/SPIRE: vendor-neutral

### Without a Mesh
For limited scope, manual mTLS works:
- cert-manager issues certs
- App configures TLS with client cert verification
- Rotation handled by cert-manager (90-day Let's Encrypt or internal CA)

## Identity-Aware Proxy (IAP)

Sits in front of services; authenticates + authorizes per request.

### Google IAP
- Replaces VPN for app access
- Verifies user identity + device posture
- Per-app policy

### Pomerium (OSS)
Self-host identity-aware proxy.

### AWS Verified Access
Similar AWS-native offering.

### Use Case
- Internal admin tools — replace VPN with IAP
- Customer apps with SSO requirement

## Continuous Evaluation

Pre-zero-trust: authenticate once, valid for session (hours).
Zero-trust: re-evaluate per request (or every few minutes).

- Token short-lived (minutes)
- Each request checks: identity, device posture, network position, policy
- Anomalies (new device, unusual location) trigger re-auth

## Practical Adoption

### Phase 1: Identity Foundation
- SSO everywhere (Okta, Entra ID, Workspace)
- MFA mandatory
- Device inventory
- Strong identity for workloads (IRSA / Workload Identity)

### Phase 2: Encrypt Service-to-Service
- Service mesh OR per-app mTLS
- Eliminate clear-text internal traffic

### Phase 3: Per-Request Authorization
- AuthZ at API gateway / mesh
- OPA / Cedar / custom AuthZ service
- Audit log every authz decision

### Phase 4: Continuous Evaluation
- Short-lived tokens
- Posture checks
- Anomaly detection

Most companies are still in Phase 1-2.

## Microsegmentation

Network policy at the workload level:
- K8s NetworkPolicy
- Cilium Network Policy (L7-aware)
- Cloud-native (AWS VPC Lattice, Azure NSG)

Default-deny + explicit allows by workload identity.

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: api-from-frontend
spec:
  endpointSelector:
    matchLabels:
      app: api
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: frontend
      toPorts:
        - ports: [{ port: '8080', protocol: TCP }]
          rules:
            http:
              - method: GET
                path: '/api/v1/.*'
              - method: POST
                path: '/api/v1/orders'
```

L7-aware network policy. Very Zero Trust.

## Common Misconceptions

- "We have VPN, so we're Zero Trust" — no
- "We use Okta" — necessary but not sufficient
- "We have mTLS via the mesh" — strong start but not complete
- "Zero Trust means no trust at all" — no, it means no implicit trust

## Interview Themes

- "Zero Trust — define and implement"
- "BeyondCorp model"
- "SPIFFE / Workload Identity"
- "mTLS — how achieve everywhere?"
- "Microsegmentation — L4 vs L7"
