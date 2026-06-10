# L13/C06/T04 — NetworkPolicies (Defense in Depth)

## Learning Objectives

- Apply NetworkPolicy as security control
- Design zero-trust patterns

## Recap from C04/T07

NetworkPolicy basics covered earlier. This focuses on security-oriented use.

## Why for Security

Without policy:
- Compromised pod can reach everything
- Lateral movement easy
- Data exfiltration unrestricted

With policy:
- Default deny baseline
- Explicit allow per app
- Blast radius limited

## Defense in Depth Strategy

Layer:
1. **NetworkPolicy** (L3/L4): restrict TCP/UDP/IP
2. **Service Mesh** (L7 + mTLS): authenticate + authorize HTTP
3. **App-level auth**: JWT, OAuth
4. **PSS**: limit pod capabilities

Each layer catches what others miss.

## Zero Trust Baseline

Per namespace:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

Nothing in/out. Then explicit allows.

## Required Allows (Almost Always)

### DNS Egress
```yaml
egress:
- to:
  - namespaceSelector:
      matchLabels:
        kubernetes.io/metadata.name: kube-system
    podSelector:
      matchLabels:
        k8s-app: kube-dns
  ports:
  - port: 53
    protocol: UDP
  - port: 53
    protocol: TCP
```

Without: app can't resolve any name.

### Egress to Metadata Service (Block)
```yaml
egress:
- to:
  - ipBlock:
      cidr: 0.0.0.0/0
      except:
      - 169.254.169.254/32   # AWS / Azure metadata
      - 169.254.170.2/32     # ECS metadata
```

Block instance metadata. Prevents SSRF → IAM creds.

Especially when not using IRSA / Pod Identity.

## Tier-Based Policy

```yaml
# Frontend can talk to backend
kind: NetworkPolicy
metadata:
  name: backend-from-frontend
spec:
  podSelector:
    matchLabels:
      tier: backend
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: frontend
    ports:
    - port: 8080
```

```yaml
# Backend can talk to DB
kind: NetworkPolicy
metadata:
  name: db-from-backend
spec:
  podSelector:
    matchLabels:
      tier: db
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: backend
    ports:
    - port: 5432
```

Frontend can't reach DB directly. Layered.

## Namespace Isolation

```yaml
# Block cross-namespace ingress
kind: NetworkPolicy
metadata:
  name: deny-from-other-namespaces
  namespace: production
spec:
  podSelector: {}
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: production
```

Only same-namespace traffic.

## Allow Ingress Controller

```yaml
ingress:
- from:
  - namespaceSelector:
      matchLabels:
        name: ingress-nginx
```

For: traffic from Ingress Controller pods.

## Egress to AWS Services

Pods talking to S3, DynamoDB, etc.:
```yaml
egress:
- to:
  - ipBlock:
      cidr: 0.0.0.0/0
  ports:
  - port: 443
```

Or via VPC endpoint with restricted CIDR.

For per-service Calico/Cilium: FQDN-based policies.

## Cilium FQDN Policy

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-github
spec:
  endpointSelector:
    matchLabels:
      app: ci-runner
  egress:
  - toFQDNs:
    - matchPattern: "*.github.com"
    - matchPattern: "api.github.com"
    toPorts:
    - ports:
      - port: "443"
```

Allow only GitHub egress.

For CI runners; supply chain restriction.

## Per-App Policy Pattern

For each app:
```yaml
# Allow ingress from specific apps
ingress:
- from:
  - podSelector: {matchLabels: {app: caller-app}}
  ports: [...]

# Allow egress to specific apps
egress:
- to:
  - podSelector: {matchLabels: {app: target-app}}
  ports: [...]
- to:                           # DNS
  - namespaceSelector: {...}
    podSelector: {matchLabels: {k8s-app: kube-dns}}
  ports: [{port: 53, protocol: UDP}]
```

Layered policies per workload.

## Multi-Tenant

For shared cluster (multiple teams):
- Each team: own namespace
- Default-deny ingress + egress at namespace
- Cross-namespace: explicit allows
- Audit policies

## Compliance Patterns

### PCI
Cardholder data zone:
- Strict isolation
- Egress only to specific destinations
- Audit logging

### HIPAA
PHI workloads:
- Isolated namespace
- Encryption + policies
- Cross-policy with other workloads explicit

## Detection

Cilium Hubble flow logs:
```bash
hubble observe --verdict DENIED
hubble observe --pod my-pod --verdict DENIED
```

For: spotting unexpected traffic.

Calico flow logs similar.

## SOC Integration

NetworkPolicy violations → SIEM:
- Cilium Hubble → Splunk / Datadog
- Calico Enterprise: SOC integration

For: incident response.

## CNI Requirements

NetworkPolicy needs CNI support:
- Calico: yes
- Cilium: yes (most features)
- AWS VPC CNI: needs Calico add-on
- Flannel: no

For policy: use Calico/Cilium.

## Pod-to-Pod TLS

NetworkPolicy doesn't encrypt. Just allows/denies.

For TLS:
- Service Mesh (Istio mTLS)
- App-level TLS

Combine: policy + mTLS.

## Egress Filtering

Default-deny egress is strict. Common pitfalls:
- Block DNS → apps fail
- Block updates / metrics → ops blind
- Block tracing endpoints

Document allowed egress carefully.

## Audit Mode

Cilium audit:
```yaml
spec:
  enableDefaultDeny: false   # log only
```

For: tuning before enforcement.

## Testing Policies

```bash
# Pod that should be blocked
kubectl exec pod-a -- nc -zv blocked-target 80
# Connection refused

# Pod that should work
kubectl exec pod-a -- nc -zv allowed-target 80
# Connected
```

Iterate.

## Common Mistakes

- Default-deny + forgot DNS
- Egress allow all (defeats security)
- Cross-namespace assumed (not without explicit)
- Forgot Ingress Controller namespace
- CNI doesn't support policy

## Best Practices

- Default-deny baseline per namespace
- DNS egress always allowed
- Metadata IP egress blocked
- Per-app explicit policies
- Documentation per policy
- Test denials
- Monitor with Hubble / similar
- Pair with service mesh

## Compliance

Policy as evidence:
- "Production deny-all" → SOC audit
- "PCI namespace isolation" → PCI evidence
- "Egress to S3 only via endpoint" → audit

Document.

## Network Policy + Pod Security

PSS prevents pods from being privileged.
Policy controls network traffic.

Both layers needed.

## Pattern: Production-Hardened Namespace

```yaml
# Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
---
# Default deny
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: production
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
# DNS egress
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: production
spec:
  podSelector: {}
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - port: 53
      protocol: UDP
  policyTypes: [Egress]
---
# App-specific...
```

Production-grade baseline.

## Common Mistakes

- Trusting cluster-internal traffic
- No egress filtering
- Cross-namespace defaults assumed
- Manual testing forgotten
- CNI without policy support

## Quick Refs

```bash
# Policies in namespace
kubectl get networkpolicy -n production

# Cilium
kubectl get ciliumnetworkpolicy -A
hubble observe --verdict DENIED

# Calico
calicoctl get networkpolicy
calicoctl get globalnetworkpolicy
```

## Interview Prep

**Mid**: "Default deny + allow DNS."

**Senior**: "Policy for PCI workload."

**Staff**: "Zero-trust K8s networking."

## Next Topic

→ [T05 — Secrets Encryption at Rest](T05-Secrets-Encryption.md)
