# L13/C04/T03 — kube-proxy Modes (iptables vs IPVS vs eBPF)

## Learning Objectives

- Pick kube-proxy mode
- Diagnose performance

## kube-proxy

Per-node component. Routes Service traffic to backing pods.

Watches:
- Services
- Endpoints / EndpointSlices

Programs node's network:
- iptables / IPVS / eBPF rules
- ClusterIP → pod IPs

## iptables Mode (Default)

For each Service: chain of iptables rules.

```
ClusterIP:80
↓ (PREROUTING / OUTPUT)
KUBE-SVC-XXX (chain)
↓ random selection (statistic match)
KUBE-SEP-XXX (specific endpoint)
↓ DNAT to pod IP:port
```

Each Service: 2-3 rules + 1 chain per endpoint.

For 10000 services × 100 endpoints: 1M+ iptables rules. Slow.

### Performance

- Add/remove rule: O(n) (rewrite chains)
- Lookup: also O(n) (chain traversal)
- CPU: high at scale

For small clusters: fine. For 5000+ services: switch.

## IPVS Mode

Linux IPVS (kernel-level LB):
- Hash-based; O(1)
- Many algorithms: round-robin, weighted, least-conn, source-hashing, etc.
- Better at scale

Enable:
```bash
# kube-proxy flag
--proxy-mode=ipvs
--ipvs-scheduler=rr
```

Per Service: ipvsadm rule.

### Algorithms

- `rr`: round-robin (default)
- `lc`: least connections
- `dh`: destination hashing
- `sh`: source hashing
- `wrr`: weighted round-robin

For stateful sessions: `sh`.

## Cilium eBPF (Replaces kube-proxy)

eBPF programs in kernel:
- Routes Service traffic without iptables
- Faster than IPVS
- Programmable

Enable Cilium with `kubeProxyReplacement=strict`:
```bash
helm install cilium ... --set kubeProxyReplacement=strict
```

Then disable kube-proxy DaemonSet (Cilium replaces).

## Comparison

| | iptables | IPVS | eBPF (Cilium) |
|---|---|---|---|
| Lookup | O(n) | O(1) | O(1) |
| Add rule | O(n) | O(1) | O(1) |
| Programmable | Limited | No | Yes |
| Observability | Hard | Limited | Excellent (Hubble) |
| Mature | Yes | Yes | Yes |
| L7 | No | No | Yes |
| Default | Yes | No | No |

For huge clusters: IPVS minimum; Cilium ideal.

## Service Types Behavior

All modes support:
- ClusterIP
- NodePort
- LoadBalancer

Implementation differs underneath.

## Source IP Preservation

iptables NAT: source IP rewritten (cluster's node IP).

For externalTrafficPolicy=Local: preserved (only pods on same node as LB).

IPVS: similar.

For real source IP: PROXY protocol at LB.

## SessionAffinity

```yaml
sessionAffinity: ClientIP
```

Sticky based on client IP.

iptables: limited; IPVS: better.

## Mode Detection

```bash
# kube-proxy logs
kubectl logs -n kube-system kube-proxy-xyz | grep "proxy-mode"

# Or check rules
iptables -t nat -L | head    # iptables
ipvsadm -l                    # IPVS
```

## Tuning

iptables:
- Reduce service churn (stable endpoints)
- Use `iptables-restore` for batch updates (modern kube-proxy does)

IPVS:
- Per-service tunables (timeout, etc.)

Cilium:
- `kubeProxyReplacement: strict`
- `loadBalancer.algorithm: maglev` (consistent hashing)

## Diagnosis

### Service Slow / Connection Drops
- iptables churn (many endpoint changes)
- IPVS connection table full
- Conntrack table full

```bash
# Conntrack
sysctl net.netfilter.nf_conntrack_count
sysctl net.netfilter.nf_conntrack_max
```

Increase if at limit.

### Specific Service Slow
- Many endpoints; iptables linear scan
- Use IPVS / Cilium

### Random Connection Resets
- Conntrack timeout for idle
- TCP_NODELAY in app

## Migration

iptables → IPVS:
- Update kube-proxy flag
- Restart kube-proxy DaemonSet
- Validate
- Monitor

iptables → Cilium:
- Install Cilium with kubeProxyReplacement=strict
- Wait Cilium ready
- Disable kube-proxy DaemonSet
- Validate

For prod: test in dev/staging first.

## NodePort Range

Default 30000-32767. Configurable:
```
--service-node-port-range=20000-40000
```

For: more services using NodePort.

## ExternalTrafficPolicy

```yaml
externalTrafficPolicy: Local
```

LB → only pods on same node:
- Source IP preserved
- Uneven distribution (if pods not on every node)

```yaml
externalTrafficPolicy: Cluster   # default
```

LB → any node → kube-proxy → any pod:
- Source IP NAT'd
- Even distribution

## Internal Traffic Policy

```yaml
internalTrafficPolicy: Local
```

Pod → Service → only pods on same node.

For: latency / locality.

## Network Diagram

```
External traffic
    ↓
LB (cloud-provisioned)
    ↓
Node A NodePort
    ↓
kube-proxy iptables/IPVS/eBPF
    ↓ DNAT
Pod (could be on Node A or B; depending on policy)
```

## Best Practices

- IPVS for 1000+ services
- Cilium for performance + observability
- externalTrafficPolicy=Local for source IP needed
- Conntrack tuning for huge connections
- Service mesh for L7 (but with cost)

## Common Mistakes

- iptables in large cluster (slow)
- Conntrack table exhaustion
- Wrong externalTrafficPolicy
- Service mesh expecting kube-proxy

## kube-proxy Failure

Node still routes (rules exist):
- Existing connections persist
- New Service / endpoint changes not picked up

Restart kube-proxy: re-syncs.

For Cilium replacing kube-proxy: Cilium agent handles.

## Observability

iptables/IPVS: limited.

eBPF / Cilium: Hubble shows flows real-time.

For: debugging "which pod served this request."

## Quick Refs

```bash
# Mode
kubectl logs -n kube-system kube-proxy-xyz

# iptables rules for service
iptables -t nat -L KUBE-SERVICES -n

# IPVS
ipvsadm -l

# Cilium
cilium status
cilium service list
```

## Interview Prep

**Mid**: "iptables vs IPVS."

**Senior**: "Cilium replacing kube-proxy."

**Staff**: "Slow service at scale — diagnose."

## Next Topic

→ [T04 — Services (ClusterIP, NodePort, LoadBalancer, Headless)](T04-Services.md)
