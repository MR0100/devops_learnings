# L02/C06/T02 — Routing

## Learning Objectives

- Read and modify the routing table with `ip route`
- Understand longest-prefix match, metrics, and the default gateway
- Use multiple routing tables and policy rules (`ip rule`) for source/dest-based routing
- Relate routing to container/Kubernetes node networking and multi-NIC hosts

## The Big Picture

Routing answers one question for every outbound packet: *which interface and next-hop should this go to?* The kernel picks the most specific matching route (longest prefix), then sends the packet either directly (on-link) or to a gateway.

```
   packet to 8.8.8.8
        │
   ┌────▼─────────────────────────┐
   │ pick routing table (ip rule)  │
   │ within table: longest-prefix  │
   └────┬─────────────────────────┘
        │ match: default via 192.168.1.1 dev eth0
        ▼
   send to gateway MAC (from ARP) out eth0
```

## Reading the Table

```bash
ip r                       # main table (alias: ip route show)
ip r get 8.8.8.8           # which route WOULD be used for this dest
ip r get 8.8.8.8 from 10.0.0.5   # simulate a specific source
ip -6 r                    # IPv6 routes
```

A typical line:

```
default via 192.168.1.1 dev eth0 proto dhcp metric 100
10.0.0.0/24 dev eth0 proto kernel scope link src 10.0.0.5
```

- `default` = `0.0.0.0/0`, the catch-all gateway.
- `scope link` = directly reachable, no gateway needed.
- `src` = preferred source address the kernel will stamp on packets.
- `metric` = tie-breaker; lower wins when prefixes are equal length.

## Longest-Prefix Match

The kernel always chooses the **most specific** route, regardless of order:

| Destination | Routes present | Chosen |
|---|---|---|
| 10.1.2.3 | `default`, `10.0.0.0/8`, `10.1.0.0/16` | `10.1.0.0/16` |
| 172.16.5.5 | `default`, `10.0.0.0/8` | `default` |

Prefix length wins first; metric only breaks ties between equal-length prefixes.

## Modifying Routes

```bash
ip r add 10.20.0.0/16 via 192.168.1.254 dev eth0    # static route via gateway
ip r add 10.30.0.0/16 dev eth1                       # on-link, no gateway
ip r add default via 192.168.1.1                     # set default gateway
ip r replace default via 192.168.1.1 metric 50       # idempotent change
ip r del 10.20.0.0/16                                 # remove
ip r flush cache                                      # clear route cache
```

`replace` is idempotent (add-or-update) and safer in automation than `add`, which errors if the route exists.

## Multiple Tables and Policy Routing

The default match uses the `main` table, but Linux supports up to 2^32 tables. **Policy routing** (`ip rule`) chooses the table based on packet attributes — source IP, fwmark, incoming interface — *before* the longest-prefix lookup runs.

```bash
ip rule                                  # list rules (by priority)
ip rule add from 10.8.0.0/24 table 100   # source-based: this subnet uses table 100
ip rule add fwmark 0x1 table 200         # mark-based (set by iptables/nft)
ip rule add iif eth1 table 200           # by incoming interface
ip r add default via 10.8.0.1 table 100  # populate that table
ip rule del from 10.8.0.0/24 table 100
```

Built-in rules and their priorities:

```
0:    from all lookup local      # local/broadcast addresses (never delete)
32766: from all lookup main      # your normal routes
32767: from all lookup default   # usually empty
```

Rules are evaluated by ascending priority; the first table that returns a match wins. Name tables in `/etc/iproute2/rt_tables` for readability.

Use cases: multi-WAN egress (route per source IP), VPN split-tunnel, Kubernetes nodes where a CNI marks traffic and steers it through a specific table.

## ARP / Neighbor Resolution

Once a route picks a next-hop IP, the kernel needs its MAC for the local segment:

```bash
ip neigh                          # show cache (REACHABLE, STALE, FAILED)
ip neigh add 10.0.0.1 lladdr aa:bb:cc:dd:ee:ff dev eth0   # static entry
ip neigh flush dev eth0
```

A `FAILED` neighbor for your gateway means L2 is broken even if the route looks correct — a common "route is right but nothing works" cause.

## Useful Tunables

```bash
sysctl net.ipv4.ip_forward                       # route between interfaces
sysctl net.ipv4.conf.all.rp_filter               # reverse-path filtering
sysctl -w net.ipv4.conf.all.rp_filter=2          # loose mode for asymmetric routing
sysctl net.ipv4.conf.all.accept_redirects        # ICMP redirect handling
```

**`rp_filter`** drops packets whose source wouldn't route back out the same interface. Strict mode (1) silently kills asymmetric and policy-routed traffic — set loose (2) on multi-homed or VPN boxes when packets mysteriously vanish.

## Relating to Containers and Kubernetes

- Each container/namespace has its **own** routing table — usually just `default via <bridge IP>` plus an on-link route to its subnet.
- Bridge-mode containers route out via the host bridge, then the host's own routes carry them upstream (often with NAT).
- Routed CNIs (Calico, Cilium native routing) add per-pod `/32` routes on the node, and node-to-node routes (or BGP) for cross-node pod traffic — no overlay, just routing.
- `ip r get <podIP>` on a node is the fastest way to see how pod traffic is steered.

```
Node A                          Node B
 pod 10.244.1.5/32 dev cali...   pod 10.244.2.7/32 dev cali...
 route: 10.244.2.0/24 via NodeB  route: 10.244.1.0/24 via NodeA
```

## Common Mistakes

- Assuming route order matters — it's longest-prefix, then metric, never insertion order.
- Adding a default route on a second NIC and clobbering the first; use distinct metrics or policy routing.
- Forgetting `ip_forward=1`, so the box accepts but never forwards packets.
- Strict `rp_filter` silently dropping asymmetric/policy-routed traffic with no log.
- Editing routes live with `ip r` and losing them on reboot (not persisted in netplan/NetworkManager).
- Deleting the `local` table rule (priority 0) and breaking loopback/local delivery.

## Best Practices

- Use `ip r get <dest>` to verify intent instead of eyeballing the table.
- Prefer `ip r replace` over `add` in scripts for idempotency.
- Name custom tables in `/etc/iproute2/rt_tables`; document why each rule exists.
- Use metrics deliberately on multi-WAN/multi-NIC hosts so failover is predictable.
- Persist routes via your distro's network manager; treat live `ip` commands as debugging.
- On multi-homed hosts, set `rp_filter=2` (loose) to avoid invisible drops.

## Quick Refs

```bash
ip r                                  # main table
ip r get 8.8.8.8                      # route that would be used
ip r add 10.0.0.0/8 via 192.168.1.1   # add via gateway
ip r add 10.0.0.0/24 dev eth1         # add on-link
ip r replace default via 192.168.1.1  # idempotent default
ip r del 10.0.0.0/8                   # delete
ip rule                               # policy rules
ip rule add from 10.8.0.0/24 table 100
ip r add default via 10.8.0.1 table 100
ip neigh                              # ARP/NDP cache
sysctl -w net.ipv4.ip_forward=1       # enable forwarding
sysctl -w net.ipv4.conf.all.rp_filter=2   # loose rpf
```

## Interview Prep

**Junior**: "How do you see and set the default gateway?"
- `ip r` shows it as the `default` route; `ip r add default via 192.168.1.1` (or `replace`) sets it.

**Mid**: "Two routes match a destination — which wins?"
- Longest prefix wins first (most specific), and metric only breaks ties between equal-length prefixes; insertion order is irrelevant.

**Senior**: "Traffic from one subnet must egress a different gateway. How?"
- Policy routing: `ip rule add from <subnet> table 100` plus a `default` in table 100, possibly relaxing `rp_filter` so the asymmetric path isn't dropped.

**Staff**: "Walk a packet from a pod on Node A to a pod on Node B in a routed CNI."
- Pod's netns has a default via the node's veth; the node has a `/32` (or `/24`) route to the peer pod range via Node B (installed by the CNI or BGP); `ip_forward` lets the node route it, neighbor resolution finds Node B's MAC, and the peer node has the symmetric route back — no overlay encapsulation involved.

## Next Topic

→ [T03 — iptables & nftables](T03-Iptables-Nftables.md)
