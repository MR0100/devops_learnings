# L02/C06/T01 — Network Interfaces

## Learning Objectives

- Manage interfaces and addresses with `iproute2` (`ip`) instead of deprecated `ifconfig`
- Understand interface types: physical, loopback, veth, bridge, VLAN, dummy
- Read interface state, statistics, MTU, and offloads with `ip` and `ethtool`
- Relate host interfaces to container networking (veth into a namespace)

## The Big Picture

A network interface is the kernel's abstraction for "a place packets enter and leave." Some are backed by real hardware (a NIC driver), most on a modern host are virtual (loopback, veth, bridge, tun/tap, vlan). Each interface has a name, an index, a MAC (link-layer) address, an MTU, an operational state, and zero or more L3 addresses.

```
  Application
      │ socket
  ┌───▼────────────────────────┐
  │      Kernel network stack   │
  │   routing │ netfilter │ qdisc│
  └───┬────────────┬────────────┘
   eth0 (NIC)   veth0 ── veth1 (in netns)
      │
   physical wire
```

`ifconfig` (net-tools) is deprecated and does not show every address or modern features (multiple IPs per interface, policy routing, namespaces). Always use `ip` from `iproute2`.

## Interface Types

| Type | Created by | Purpose |
|---|---|---|
| physical (`eth0`, `enp3s0`) | driver | real NIC |
| `lo` | kernel | loopback, 127.0.0.1/::1 |
| `veth` | `ip link add ... type veth` | pipe between namespaces; one end per netns |
| `bridge` (`br0`, `docker0`) | `ip link add ... type bridge` | virtual L2 switch |
| `vlan` (`eth0.100`) | `ip link add ... type vlan` | 802.1Q tagged sub-interface |
| `bond` | bonding driver | aggregate NICs |
| `tun`/`tap` | userspace (VPNs) | L3 (tun) / L2 (tap) software interface |
| `dummy` | `ip link add ... type dummy` | always-up sink, handy for stable IPs |

Predictable interface names (`enp3s0`, `ens5`) come from systemd-udev's naming based on bus/slot, so a NIC keeps the same name across reboots — unlike the old `eth0/eth1` race.

## Addressing with `ip`

```bash
ip a                                   # all addresses (alias: ip addr show)
ip -br a                               # one-line-per-iface summary
ip a add 192.168.1.10/24 dev eth0      # add an IPv4 address
ip a add 2001:db8::10/64 dev eth0      # add an IPv6 address
ip a del 192.168.1.10/24 dev eth0      # remove it
```

An interface can hold many addresses. The first IPv4 in a subnet is `primary`; others are `secondary`. The `scope` matters: `global` is routable, `link` is link-local, `host` never leaves the box.

## Link State and Properties

```bash
ip link show eth0
ip link set eth0 up                    # admin-up
ip link set eth0 down
ip link set eth0 mtu 9000              # jumbo frames
ip link set eth0 address 02:11:22:33:44:55   # override MAC
ip link set eth0 promisc on            # promiscuous (capture) mode
```

There are two states to distinguish:
- **Administrative state** — `UP`/`DOWN`, set by you.
- **Operational state** — `LOWER_UP` means carrier (cable/link) is present.

An interface can be admin-`UP` but operationally down (`NO-CARRIER`) if the cable is unplugged. `ip link` flags like `<BROADCAST,MULTICAST,UP,LOWER_UP>` encode both.

## Statistics and Diagnostics

```bash
ip -s link show eth0       # rx/tx packets, bytes, errors, drops
ip -s -s link show eth0    # extra error detail (collisions, carrier)
ip neigh                   # ARP/NDP neighbor cache
ip neigh flush dev eth0    # clear stale entries
```

Rising `RX dropped` usually means the socket/ring buffer is full (CPU can't keep up); rising `errors` points at hardware/cabling. The neighbor cache is the L2 equivalent of routing: it maps IP → MAC for the local segment.

## ethtool — The Hardware View

```bash
ethtool eth0                 # speed, duplex, link detected
ethtool -i eth0              # driver, firmware, bus-info
ethtool -S eth0              # NIC-level stats (ring drops, rx_missed)
ethtool -k eth0              # offload features (gso, gro, tso, checksums)
ethtool -K eth0 tso off      # toggle an offload
ethtool -g eth0              # ring buffer sizes
ethtool -G eth0 rx 4096      # grow the rx ring to reduce drops
```

Offloads (TSO/GSO/GRO/checksum) move work into the NIC. They boost throughput but can confuse packet captures (you'll see super-sized segments in `tcpdump`) and occasionally cause subtle bugs — a classic debugging step is disabling them.

## Relating to Containers

A container's `eth0` is one end of a **veth pair**; the other end lives in the host (often plugged into a bridge or, with CNIs, used as a routed endpoint).

```
   Host netns                 Container netns
  ┌──────────────┐           ┌──────────────┐
  │ docker0 ─ vethXXXX ══════╪═ eth0         │
  │   (bridge)   │   veth    │  10.244.1.5   │
  └──────────────┘           └──────────────┘
```

```bash
# Create a pair and move one end into a namespace
ip link add veth-h type veth peer name veth-c
ip link set veth-c netns mycontainer
ip link set veth-h master docker0       # plug host end into bridge
ip link set veth-h up
```

This is exactly what runtimes do under the hood — understanding `ip link` makes container networking demystified.

## /proc and /sys Tunables

```bash
sysctl net.ipv4.ip_forward                 # is this host a router?
sysctl -w net.ipv4.ip_forward=1            # enable forwarding (needed for NAT/bridges)
cat /sys/class/net/eth0/mtu
cat /sys/class/net/eth0/address            # MAC
cat /sys/class/net/eth0/operstate          # up / down
cat /sys/class/net/eth0/statistics/rx_bytes
```

`net.ipv4.ip_forward=1` is mandatory for any box that routes between interfaces — Docker, Kubernetes nodes, and NAT gateways all set it.

## Common Mistakes

- Using `ifconfig` and missing secondary addresses, IPv6, or namespace interfaces it cannot show.
- Confusing admin state (`UP`) with carrier (`LOWER_UP`); declaring a link "up" when it has `NO-CARRIER`.
- Setting an IP but forgetting `ip link set dev up`, so traffic never flows.
- Changing MTU on one side of a path only, causing fragmentation or black-holed large packets.
- Deleting the wrong address because you didn't include the prefix length (`/24`); `ip a del` needs the exact CIDR.
- Forgetting `net.ipv4.ip_forward=1` and wondering why a bridge or NAT box drops forwarded traffic.

## Best Practices

- Standardize on `iproute2` (`ip`, `bridge`, `ss`); treat `net-tools` as legacy.
- Use `ip -br a` and `ip -br link` for quick, scriptable summaries.
- Match MTU end-to-end across a path (NIC, bridge, veth, overlay) — overlays like VXLAN need ~50 bytes of headroom.
- Persist interface config in NetworkManager/`netplan`/`systemd-networkd`, not ad-hoc `ip` commands that vanish on reboot.
- When debugging throughput, check `ip -s link` drops and `ethtool -S` ring stats before blaming the application.

## Quick Refs

```bash
ip a                                  # show all addresses
ip -br a                              # brief summary
ip a add 192.168.1.10/24 dev eth0     # add address
ip a del 192.168.1.10/24 dev eth0     # remove address
ip link set eth0 up | down            # admin state
ip link set eth0 mtu 9000             # set MTU
ip -s link show eth0                  # stats
ip neigh                              # ARP/NDP cache
ip link add veth0 type veth peer name veth1   # veth pair
ip link set veth1 netns NS            # move end into namespace
ethtool -i eth0                       # driver/firmware
ethtool -k eth0                       # offloads
ethtool -S eth0                       # NIC stats
sysctl -w net.ipv4.ip_forward=1       # enable forwarding
```

## Interview Prep

**Junior**: "How do you list and bring up an interface?"
- `ip a` to list, `ip link set eth0 up` to admin-enable it; `ip a add 10.0.0.5/24 dev eth0` assigns an address.

**Mid**: "What's the difference between admin-up and operationally up?"
- Admin-up (`UP`) means you've enabled it; operationally up (`LOWER_UP`) means carrier is present — an interface can be admin-up with `NO-CARRIER` if the cable is unplugged.

**Senior**: "RX drops are climbing on a busy NIC — where do you look?"
- `ip -s link` and `ethtool -S` for ring/socket drops; grow the rx ring with `ethtool -G`, check IRQ affinity and CPU saturation, and verify offloads — drops here are buffer pressure, not the app.

**Staff**: "Explain how a container's eth0 connects to the host."
- It's one end of a veth pair created in the host netns and moved into the container's netns; the host end attaches to a bridge (docker0) or is used as a routed endpoint by the CNI, with `ip_forward` enabled so the kernel routes between them.

## Next Topic

→ [T02 — Routing](T02-Routing.md)
