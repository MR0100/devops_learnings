# L13/C04/T07 — NetworkPolicies

## Learning Objectives

- Enforce network isolation
- Apply default-deny

## NetworkPolicy

K8s firewall for pod traffic:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-allow-from-frontend
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - port: 8080
```

## Default Behavior

Without policy:
- All pods can talk to all pods
- Wide open

With policy:
- Selected pods restricted per policy
- Other pods unaffected unless covered by their own policy

## Requirements

CNI must support:
- Calico: yes
- Cilium: yes
- AWS VPC CNI: need Calico add-on
- Flannel: no

## Default Deny

Block all ingress:
```yaml
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

`podSelector: {}` selects all pods. No `ingress` rules: nothing allowed.

For: zero trust baseline.

## Default Deny Egress

```yaml
metadata:
  name: default-deny-egress
spec:
  podSelector: {}
  policyTypes:
  - Egress
```

Pods can't reach anything (including DNS!).

Combine with: explicit allow rules.

## Allow DNS

Almost always needed:
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
```

Without: pod can't resolve any name.

## Allow Specific Egress

```yaml
egress:
- to:
  - podSelector:
      matchLabels:
        app: db
  ports:
  - port: 5432
```

Pod can reach db pods on port 5432.

```yaml
egress:
- to:
  - ipBlock:
      cidr: 0.0.0.0/0
      except:
      - 169.254.0.0/16
  ports:
  - port: 443
```

HTTPS to anywhere except link-local (metadata service).

## Selectors

### podSelector
```yaml
podSelector:
  matchLabels:
    app: db
```

Pods in same namespace with label.

### namespaceSelector
```yaml
namespaceSelector:
  matchLabels:
    name: production
```

Pods in matching namespaces.

### Combined
```yaml
- namespaceSelector:
    matchLabels:
      name: web-ns
  podSelector:
    matchLabels:
      app: web
```

Pods in web-ns namespace with `app=web`.

(Note: combined = AND. Separate items = OR.)

## ipBlock

```yaml
- ipBlock:
    cidr: 10.0.0.0/8
    except:
    - 10.0.5.0/24
```

For: external IPs (not pod-selected).

## Ingress Rules

```yaml
ingress:
- from:
  - podSelector: {matchLabels: {app: frontend}}
  ports:
  - port: 8080

- from:
  - ipBlock: {cidr: 192.168.0.0/16}
  ports:
  - port: 8080
```

Two rules: any matching = allowed.

## Egress Rules

```yaml
egress:
- to:
  - podSelector: {matchLabels: {app: db}}
  ports:
  - port: 5432

- to:
  - namespaceSelector: {matchLabels: {name: kube-system}}
    podSelector: {matchLabels: {k8s-app: kube-dns}}
  ports:
  - port: 53
    protocol: UDP
```

## Combining Selectors

Same `from` / `to` entry: AND
Separate: OR

```yaml
ingress:
- from:
  - namespaceSelector: {...}     # OR
    podSelector: {...}            # AND with namespace
  - podSelector: {...}            # OR
```

Tricky; test carefully.

## Common Patterns

### Allow Same Namespace
```yaml
ingress:
- from:
  - namespaceSelector:
      matchLabels:
        kubernetes.io/metadata.name: my-namespace
```

### Allow From Specific Namespace
```yaml
- namespaceSelector:
    matchLabels:
      name: frontend
```

### Allow All in Same Namespace
```yaml
ingress:
- from:
  - podSelector: {}     # all pods in same namespace
```

### Allow Specific Service
```yaml
ingress:
- from:
  - podSelector:
      matchLabels:
        app: api
  ports:
  - port: 5432
```

## Default Deny + Allow Patterns

1. Apply default-deny (ingress + egress).
2. Per-namespace / per-app: allow rules.
3. Iterate.

For zero-trust.

## Egress to External

```yaml
egress:
- to:
  - ipBlock:
      cidr: 0.0.0.0/0
  ports:
  - port: 443
```

Allow all HTTPS outbound.

Or domain-based (Cilium-only):
```yaml
# CiliumNetworkPolicy
egress:
- toFQDNs:
  - matchPattern: "*.amazonaws.com"
```

## Cilium L7 Policies

Beyond L3/L4:
```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
spec:
  endpointSelector:
    matchLabels:
      app: web
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: api
    toPorts:
    - ports:
      - port: "8080"
      rules:
        http:
        - method: GET
          path: "/users"
        - method: POST
          path: "/users"
```

Restrict by method/path. For: granular policy.

## Calico GlobalNetworkPolicy

Cluster-wide policy:
```yaml
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
spec:
  selector: all()
  types: [Ingress, Egress]
  ingress:
  - action: Deny
    source:
      nets: [1.2.3.0/24]
```

For: blanket org policy.

## NetworkPolicy + Service Mesh

NetworkPolicy: L3/L4 (IP/port).
Service Mesh (Istio): L7 (HTTP).

Use both:
- NetworkPolicy for baseline isolation
- AuthorizationPolicy (Istio) for HTTP-level

## Multi-Tenant

Per-namespace policies:
- Default deny across all
- Per-namespace: allow within
- Cross-namespace: explicit

Operators (Project Calico) help manage at scale.

## Testing

```bash
# Pod that can't connect
kubectl exec pod-a -- nc -zv db 5432
# Connection refused

# Add policy
kubectl apply -f allow-db.yaml

# Retry
kubectl exec pod-a -- nc -zv db 5432
# Connected
```

Iterate.

## Cilium Hubble

Real-time flow visibility:
```bash
hubble observe --from-label app=web --to-label app=db --verdict DENIED
```

See denied connections. Helps tune policy.

## Common Issues

### DNS Fails
Forgot egress to kube-dns.

### Ingress Doesn't Work
Forgot policy for that traffic.

### Existing Connections OK; New Blocked
Conntrack: existing tracked. New: policy-checked.

### Policy Doesn't Apply
CNI doesn't support (Flannel, default AWS VPC CNI).

## Performance

Calico, Cilium: efficient even at scale.

Heavy policy (1000s): test perf.

## Best Practices

- Default deny baseline
- Explicit allow per app
- Namespace-level segmentation
- DNS allowed
- Egress to AWS metadata blocked (security)
- Document policy rationale
- Test denials
- Use Cilium / Calico for full policy support

## Common Mistakes

- No DNS egress → app fails
- Forgot HTTPS egress → no outbound APIs
- Same-namespace allow assumed (not by default with default-deny)
- Flannel + expecting policy
- Policy in dev not prod (inconsistency)

## Hubble for Cilium

```bash
hubble observe --follow
hubble observe --pod my-pod
hubble observe --verdict DENIED
```

For debugging.

## Calico calicoctl

```bash
calicoctl get networkpolicy
calicoctl get globalnetworkpolicy
calicoctl apply -f policy.yaml
```

## Policy Testing

For development: relax policies, then tighten.

Or `audit` mode (Cilium):
```yaml
spec:
  endpointSelector: {...}
  enableDefaultDeny: false  # log violations
```

Test in production-like; tighten.

## Quick Refs

```yaml
# Default deny (ingress)
kind: NetworkPolicy
spec:
  podSelector: {}
  policyTypes: [Ingress]

# Allow from app
spec:
  podSelector:
    matchLabels:
      app: web
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - port: 8080

# Allow egress DNS
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
```

## Interview Prep

**Mid**: "NetworkPolicy basics."

**Senior**: "Default deny pattern."

**Staff**: "Multi-tenant network isolation."

## Next Topic

→ Move to [L13/C05 — Storage in Kubernetes](../C05/README.md)
