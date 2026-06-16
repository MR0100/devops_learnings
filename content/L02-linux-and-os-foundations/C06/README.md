# L02/C06 — Linux Networking Stack

## Chapter Overview

The Linux network stack is what every microservice, every load balancer, every Kubernetes CNI ultimately relies on. Deep familiarity here is what separates senior from staff.

## Topics

| Topic | Title | Hours |
|---|---|---|
| [T01](T01-Interfaces.md) | Network Interfaces, ifconfig vs ip | 1 hr |
| [T02](T02-Routing.md) | Routing Tables and Policy Routing | 1.5 hr |
| [T03](T03-Iptables-Nftables.md) | iptables, nftables, conntrack | 2 hr |
| [T04](T04-Network-Namespaces.md) | Network Namespaces (The Foundation of Containers) | 1.5 hr |
| [T05](T05-Bridges-VLANs-Bonding.md) | Bridges, VLANs, Bonding | 1 hr |

## Key Concepts

### Modern Networking via `ip`

`ifconfig` is deprecated. Use `ip` from iproute2:

```bash
ip a                              # all addresses
ip a add 192.168.1.10/24 dev eth0
ip a del 192.168.1.10/24 dev eth0
ip link set eth0 up/down
ip link show
ip r                              # routing table
ip r add 10.0.0.0/8 via 192.168.1.1
ip r get 8.8.8.8                  # which route would be used
ip -s link                        # interface stats
ip neigh                          # arp table
ip rule                           # policy routing rules
ip route flush cache
```

### Routing
- Main table: `ip r` shows default routes
- Policy routing: multiple tables, rules pick by source/dest
- `ip rule add from 192.168.1.0/24 table 100`
- Common in: multi-WAN routers, dual-stacked hosts, K8s nodes with multiple CNIs

### Packet Filtering

#### iptables (legacy but still common)
- Tables: filter (default), nat, mangle, raw
- Chains: INPUT, OUTPUT, FORWARD; PREROUTING, POSTROUTING (nat)
- Rules processed top-down per chain

```bash
iptables -L -n -v --line-numbers
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables-save
iptables-restore < rules.txt
```

#### nftables (modern)
- Replacement for iptables, single tool for IPv4/IPv6/ARP/bridge
- Hierarchical: tables > chains > rules
- `nft list ruleset`

#### conntrack
- Connection tracking table (state machine for connections)
- Visible: `conntrack -L`, `/proc/net/nf_conntrack`
- Critical to size correctly: `net.netfilter.nf_conntrack_max`
- Causes weird "connection reset" issues when full

### Network Namespaces
- Each namespace has its own interfaces, routing tables, iptables
- Created via `unshare -n` or `ip netns add NAME`
- Connected via `veth` pairs
- The foundation under containers (covered more in C07)

```bash
ip netns add red
ip link add veth-red type veth peer name veth-host
ip link set veth-red netns red
ip netns exec red ip a
ip netns exec red ip a add 10.0.0.2/24 dev veth-red
```

### Linux Bridges
- Virtual L2 switch
- `brctl` (legacy) or `ip link add br0 type bridge`
- Default Docker bridge: `docker0`

### VLANs
- 802.1Q tagging
- `ip link add link eth0 name eth0.100 type vlan id 100`

### Bonding
- Combine multiple NICs (LACP, active-backup)
- `/etc/network/interfaces` or NetworkManager config
- Common in BM hardware; cloud uses ENI bandwidth aggregation

## Troubleshooting Toolkit (also in C08)

- `tcpdump` / `wireshark`
- `ss -tulpn` / `ss -ntp`
- `netstat` (legacy, use `ss`)
- `mtr` (combines ping + traceroute)
- `curl -v` / `httpie`
- `nmap` (with permission)

## Interview Themes

- "Trace a packet from your pod to an external IP."
- "Why might conntrack be your bottleneck?"
- "How do network namespaces make containers possible?"
- "iptables vs nftables — which and why?"
