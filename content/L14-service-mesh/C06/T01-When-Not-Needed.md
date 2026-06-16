# L14/C06/T01 — When You Don't Need a Mesh

## Learning Objectives

- Recognize over-engineering
- Pick simpler

## Signs You Don't Need a Mesh

### Few Services
- < 10 services
- Simple topology
- Tight coupling acceptable

### Single Stack
- All Go (use ConnectRPC)
- All Java (use Spring features)
- Built-in libs cover

### No Compliance Need
- mTLS not required
- Network already trusted (private cluster)

### Limited Traffic Management
- No canaries
- No A/B
- Simple rollouts

### Small Team
- 1-3 SREs
- Mesh ops burden

### Resource Constrained
- Edge devices
- IoT
- Tiny clusters

For: simpler tools.

## Alternatives

### K8s Native
- Ingress controller (nginx, traefik)
- Network policies (CiliumNetworkPolicy)
- HPA / VPA
- Built-in DNS

### Library
- gRPC retry / timeout policies
- Hystrix (Java)
- Polly (.NET)

### API Gateway Only
- Kong, Tyk, Ambassador
- North-south only
- Apps handle east-west

### Cilium CNI
- L4 mTLS via WireGuard
- L7 NetworkPolicy
- No sidecars

## What You Lose Without Mesh

- Auto mTLS
- Centralized observability
- Traffic shifting
- L7 policy

For: maybe OK.

## What You Save

- ~10-20% RAM
- Operational complexity
- Onboarding time
- Debug surface

## Specific Use Cases

### Microservices < 5
mesh overkill.

### Monolith
no.

### Internal-only, trusted network
no mTLS need.

### Stateless web tier behind ALB
ALB handles routing.

## Adoption Pattern

### Start Simple
- K8s + Ingress
- Network policies (deny by default)
- Apps responsible for retries

### Grow
- Add Linkerd if mTLS or observability needed
- Add Istio if many features needed
- Avoid: yo-yo (add, remove)

## Cilium Service Mesh

Eats some mesh territory:
- L4 mTLS (kernel-level)
- L7 NetworkPolicy
- Hubble observability

Without sidecars. Lower cost.

For: lighter "mesh-like".

## Service Mesh Anti-Patterns

### Add for Buzzword
"Industry uses mesh." Not a reason.

### Adopt Then Bypass
Sidecar injected but disabled for performance.

### All Features Day 1
Overwhelming; instability.

### Skip Training
Team can't debug.

### Mesh for Egress Only
Better: NetworkPolicy.

## Right-Size Decision

### Phase 1: K8s + Ingress + NetPol
For 0-50 services. Often enough.

### Phase 2: Lightweight Mesh
Linkerd. For mTLS + basic obs.

### Phase 3: Full Mesh
Istio. For complex routing, multi-cluster.

### Phase 4: Optimize
Ambient mode or Cilium for cost.

## Cost-Benefit

### Cost
- CPU/memory per pod
- Team learning
- Upgrades
- Debug complexity

### Benefit
- Security
- Observability
- Traffic management

For small: cost > benefit.
For large polyglot: benefit > cost.

## What Mesh Doesn't Fix

- Bad APIs
- Slow services
- Bugs
- Wrong architecture
- Cost (often increases)

## When to Remove Mesh

- Team can't operate it
- Cost too high
- Don't use features
- Replaced by simpler (Cilium)

For: migrate out deliberately.

## Migration Out

1. Document what mesh features used
2. Find alternatives:
   - mTLS → NetworkPolicy + Cilium
   - Retries → app library
   - Observability → app metrics
   - Routing → Ingress + Gateway API
3. Test alternatives in staging
4. Migrate service by service
5. Remove mesh

## Real-World Hesitation

Many enterprise:
- Trial Istio for 6 months
- Decide: too complex
- Stick with K8s native + libs

For: valid choice.

## Polyglot Caveat

If many languages, mesh more valuable (libs differ).

If monoglot (all Go): library possible.

## Risk Assessment

### Adopt Mesh Without Mature K8s
Stack on top of unstable. Don't.

First: rock-solid K8s.
Then: maybe mesh.

### Adopt Mesh Without Observability
Mesh adds observability but assumes you can use it.

First: Prometheus, Grafana, Jaeger.
Then: mesh fills gaps.

### Adopt Mesh Without Security Story
Mesh enforces auth/mTLS but you need to design policy.

First: threat model.
Then: mesh enforces.

## Best Practices

- Start without mesh
- Add when need clear
- Justify with data (not buzz)
- Train team thoroughly
- Document why

## Common Mistakes

- Adopt immediately
- Skip alternatives
- Force on smaller projects
- No skill plan

## Quick Decision

```
Few services + simple? → No mesh
Many services + polyglot + security + observability? → Mesh
Cilium CNI? → Cilium mesh option
Linkerd for simplicity, Istio for features
```

## Quick Refs

```
# Skip the mesh when...
< 10 services / simple topology
single language stack (use its libs)
trusted private network, no mTLS mandate
no canary / A/B / L7 routing need
1-3 SREs, no ops headroom

# Replace mesh features without a mesh
mTLS          → Cilium (WireGuard) / NetworkPolicy
retries/timeout → app library (gRPC, Polly, Resilience4j)
north-south    → Ingress / Gateway API + API gateway (Kong, ...)
east-west L7   → CiliumNetworkPolicy
observability  → Prometheus + Grafana + Jaeger + Hubble

# Adoption phases
P1  K8s + Ingress + NetworkPolicy   (0-50 svcs, often enough)
P2  Linkerd                         (mTLS + basic obs)
P3  Istio                           (complex routing, multi-cluster)
P4  Ambient / Cilium                (cost optimize)

# Prereqs before adopting (all three first)
rock-solid K8s · existing obs stack · a security/policy story
```

## Interview Prep

**Mid**: "Why no mesh."

**Senior**: "Alternatives to mesh."

**Staff**: "Right-size architecture."

## Next Topic

→ [T02 — Cilium Service Mesh (eBPF)](T02-Cilium-Mesh.md)
