# L02/C06/T03 — iptables & nftables

## Learning Objectives

- Understand netfilter hooks, tables, and chains and how a packet traverses them
- Write filtering and NAT rules in both `iptables` and `nftables` syntax
- Use connection tracking (`conntrack`) and size it correctly
- Relate netfilter to Docker/Kubernetes (`kube-proxy`, MASQUERADE, DNAT)

## The Big Picture

`iptables` and `nftables` are front-ends to **netfilter**, the kernel's packet-processing framework. Netfilter exposes hooks at fixed points in the packet path; chains attach to those hooks; rules in a chain match packets and apply a verdict (`ACCEPT`, `DROP`, `DNAT`, `MASQUERADE`, ...).

```
                 ┌── PREROUTING ──┐         ┌── POSTROUTING ──┐
   wire ──► nic ─┤  (raw,mangle,  ├─ routing ┤   (mangle,nat)  ├─► nic ──► wire
                 │   nat:DNAT)    │  decision│   nat:SNAT/MASQ │
                 └────────────────┘    │     └─────────────────┘
                          ┌────────────┴───────────┐
                       local in (INPUT)      forward (FORWARD)
                          │                        │
                      local process ──► local out (OUTPUT)
```

## iptables: Tables and Chains

| Table | Purpose | Key chains |
|---|---|---|
| `filter` | accept/drop (default) | INPUT, FORWARD, OUTPUT |
| `nat` | address/port translation | PREROUTING, POSTROUTING, OUTPUT |
| `mangle` | packet header tweaks, marking | all five |
| `raw` | conntrack exemptions (`NOTRACK`) | PREROUTING, OUTPUT |

Rules in a chain are processed **top-down**; the first terminating verdict wins. Each chain has a default **policy** (often `ACCEPT` or `DROP`) applied if no rule matches.

```bash
iptables -L -n -v --line-numbers          # list filter table, no DNS, counters
iptables -A INPUT -p tcp --dport 22 -j ACCEPT       # append: allow SSH
iptables -I INPUT 1 -i lo -j ACCEPT                 # insert at top: allow loopback
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -P INPUT DROP                              # default-deny policy
iptables -D INPUT 3                                 # delete rule #3
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE   # SNAT for egress
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to 10.0.0.5:8080
iptables-save > /etc/iptables/rules.v4              # persist
iptables-restore < /etc/iptables/rules.v4
```

`MASQUERADE` is SNAT that auto-picks the egress interface's IP — exactly what Docker does so containers can reach the internet through the host.

## nftables: The Modern Replacement

`nftables` unifies IPv4/IPv6/ARP/bridge into one tool with a single ruleset, atomic reloads, named sets/maps, and far better performance at scale (it avoids the linear rule scan that cripples large iptables rulesets).

```bash
nft list ruleset                         # everything
nft add table inet myfw                  # 'inet' family = v4+v6
nft 'add chain inet myfw input { type filter hook input priority 0 ; policy drop ; }'
nft add rule inet myfw input ct state established,related accept
nft add rule inet myfw input iif lo accept
nft add rule inet myfw input tcp dport 22 accept
nft add rule inet myfw input tcp dport { 80, 443 } accept   # anonymous set
nft -f /etc/nftables.conf                # atomic load of a whole file
```

### iptables vs nftables

| Aspect | iptables | nftables |
|---|---|---|
| Families | one binary each (iptables, ip6tables, arptables, ebtables) | unified (`inet`, `ip`, `ip6`, `arp`, `bridge`) |
| Rule eval | linear scan per chain | sets/maps, O(1) lookups |
| Reloads | per-rule, non-atomic | atomic file load |
| Counters | always on | opt-in |
| Status | legacy, still default in many distros | the future; `iptables-nft` shim maps old syntax onto nft |

Most modern distros ship `iptables` as a thin wrapper (`iptables-nft`) over the nftables kernel API — so the two coexist. Check with `iptables --version` (look for `nf_tables`).

## Connection Tracking (conntrack)

Conntrack is netfilter's stateful engine. It records every flow (5-tuple + state) so you can write rules like "allow replies to connections we initiated" and so NAT can reverse-translate return packets.

```bash
conntrack -L                              # current tracked connections
conntrack -L -p tcp --dport 443           # filter
conntrack -E                              # live event stream
conntrack -S                              # per-CPU stats (look for 'insert_failed', 'drop')
cat /proc/sys/net/netfilter/nf_conntrack_count   # current entries
sysctl net.netfilter.nf_conntrack_max            # table capacity
```

Connection states used in rules: `NEW`, `ESTABLISHED`, `RELATED`, `INVALID`.

### Sizing conntrack — the classic outage

When the table fills, **new connections are dropped** and you see seemingly random "connection reset"/timeout errors under load. Symptoms: `nf_conntrack: table full, dropping packet` in `dmesg`, rising `conntrack -S` `drop`/`insert_failed`.

```bash
sysctl -w net.netfilter.nf_conntrack_max=1048576
# hash bucket count should be ~ max/8
echo 131072 > /sys/module/nf_conntrack/parameters/hashsize
sysctl -w net.netfilter.nf_conntrack_tcp_timeout_established=86400
```

High-throughput proxies, NAT gateways, and busy Kubernetes nodes routinely need conntrack tuning. Traffic that needn't be tracked can be exempted in the `raw` table with `-j NOTRACK`.

## Packet Marking and Integration

```bash
iptables -t mangle -A PREROUTING -s 10.8.0.0/24 -j MARK --set-mark 0x1
# then route on the mark (ties into T02 policy routing)
ip rule add fwmark 0x1 table 100
```

Marks are the glue between netfilter and policy routing: mark in mangle, steer with `ip rule`.

## Relating to Containers and Kubernetes

- **Docker** writes `nat` rules: `MASQUERADE` for outbound, `DNAT` in the `DOCKER` chain for published ports (`-p 8080:80`).
- **kube-proxy (iptables mode)** programs huge chains of `DNAT` rules to load-balance Service VIPs across pod endpoints — and is exactly why large clusters moved to **IPVS** or **nftables/eBPF** (Cilium) to escape the linear scan.
- Pod-to-external traffic is SNAT'd (MASQUERADE) to the node IP; conntrack remembers the mapping to reverse it on the reply.
- Tracing rules: `iptables-save -t nat` / `nft list ruleset` shows exactly what the runtime injected.

## Common Mistakes

- Setting `-P INPUT DROP` before allowing `lo` and ESTABLISHED — you lock yourself out.
- Using `-A` (append) when you meant `-I` (insert), so your rule lands after a broad `DROP`.
- Forgetting the stateful ESTABLISHED,RELATED rule, so return traffic is blocked.
- Not persisting rules (`iptables-save`/`nftables.conf`) — they vanish on reboot.
- Ignoring conntrack sizing until the table fills and "random resets" appear under load.
- Mixing legacy `iptables-legacy` and `iptables-nft` on the same host, splitting the ruleset across two backends.

## Best Practices

- Default-deny on INPUT, but allow `lo` and `ESTABLISHED,RELATED` first.
- Prefer `nftables` for new work; use the `inet` family to cover v4+v6 once.
- Load full rulesets atomically (`nft -f` / `iptables-restore`) rather than rule-by-rule.
- Monitor `conntrack -S` and `nf_conntrack_count` vs `_max`; alert before saturation.
- Comment rules and keep them in version control; treat the firewall as code.
- On a Kubernetes node, don't hand-edit kube-proxy's chains — let the controller own them.

## Quick Refs

```bash
iptables -L -n -v --line-numbers                 # list filter
iptables -A INPUT -p tcp --dport 22 -j ACCEPT    # allow SSH
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to 10.0.0.5:8080
iptables-save > rules.v4 ; iptables-restore < rules.v4

nft list ruleset
nft add table inet fw
nft 'add chain inet fw input { type filter hook input priority 0; policy drop; }'
nft add rule inet fw input ct state established,related accept
nft add rule inet fw input tcp dport { 22, 80, 443 } accept
nft -f /etc/nftables.conf

conntrack -L ; conntrack -S ; conntrack -E
sysctl net.netfilter.nf_conntrack_max
```

## Interview Prep

**Junior**: "How do you allow inbound SSH with iptables?"
- `iptables -A INPUT -p tcp --dport 22 -j ACCEPT` (and make sure it's above any broad DROP).

**Mid**: "What does MASQUERADE do and where?"
- It's SNAT in the `nat` POSTROUTING chain that rewrites the source to the egress interface's IP, letting private/container addresses reach the internet; conntrack reverses it on replies.

**Senior**: "Users report random connection resets under peak load — first suspicion?"
- A full conntrack table: check `dmesg` for "table full", `conntrack -S` drops, and `nf_conntrack_count` vs `_max`; raise `nf_conntrack_max` and hashsize, tune timeouts, or NOTRACK traffic that doesn't need state.

**Staff**: "Why did large clusters move off iptables-mode kube-proxy?"
- iptables evaluates chains linearly, so thousands of Services create O(n) rule scans and slow, non-atomic updates; IPVS (hash-based) and nftables/eBPF (Cilium) give O(1) lookups and atomic programming, dramatically lowering latency and control-plane churn at scale.

## Next Topic

→ [T04 — Network Namespaces](T04-Network-Namespaces.md)
