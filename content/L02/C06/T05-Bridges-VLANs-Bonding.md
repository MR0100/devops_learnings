# L02/C06/T05 — Bridges, VLANs, Bonding

## Learning Objectives

- Build and inspect a Linux bridge (virtual L2 switch) and relate it to `docker0`
- Create and tag 802.1Q VLAN sub-interfaces
- Aggregate NICs with bonding (LACP, active-backup) for throughput and resilience
- Know which of these matter on bare metal vs cloud, and how containers use them

## Linux Bridges

A bridge is a virtual L2 switch in the kernel. It learns MAC addresses on each port and forwards frames between them — exactly like a physical switch. It's the backbone of `docker0` and most bridge-mode container networking.

```
        ┌──────────── br0 (bridge) ───────────┐
        │  learns MACs, forwards L2 frames     │
        └──┬───────────┬───────────┬───────────┘
        eth0        vethA        vethB
       (uplink)   (container)  (container)
```

```bash
# modern iproute2 way (brctl is legacy)
ip link add br0 type bridge
ip link set br0 up
ip link set eth0 master br0        # enslave a port to the bridge
ip link set vethA master br0
bridge link                        # show bridge ports
bridge fdb show                    # forwarding database (learned MACs)
bridge fdb show br br0
ip -d link show br0                # detailed bridge settings (STP, vlan_filtering)
```

Toggle features via `/sys` or `ip link`:

```bash
ip link set br0 type bridge stp_state 1          # spanning tree on
ip link set br0 type bridge vlan_filtering 1     # VLAN-aware bridge
cat /sys/class/net/br0/bridge/stp_state
```

A VLAN-aware bridge (`vlan_filtering 1`) lets you assign VLANs per port with `bridge vlan add` — this is how a single bridge can trunk multiple VLANs, the way OVS or `macvtap` setups do for VMs.

## VLANs (802.1Q)

A VLAN partitions one physical link into many isolated L2 segments using a 4-byte tag (12-bit VLAN ID, 1–4094). A "trunk" carries multiple tagged VLANs; an "access" port carries one untagged VLAN.

```bash
ip link add link eth0 name eth0.100 type vlan id 100   # tagged sub-iface
ip link set eth0.100 up
ip a add 192.168.100.5/24 dev eth0.100
ip -d link show eth0.100            # confirm vlan id 100
ip link del eth0.100
```

```
   eth0 (trunk, tagged)
    ├── eth0.100  → VLAN 100  (192.168.100.0/24)
    └── eth0.200  → VLAN 200  (192.168.200.0/24)
```

The upstream switch port must be configured as a trunk allowing those VLAN IDs, or tagged frames are dropped. VLANs are common on bare-metal hosts to separate storage/management/tenant traffic over one NIC; in cloud you typically use separate ENIs/subnets/VPCs instead.

## Bonding (Link Aggregation)

Bonding combines several NICs into one logical interface for **throughput** (aggregate bandwidth) and/or **redundancy** (survive a NIC/cable/switch failure).

| Mode | Name | Behavior | Needs switch config |
|---|---|---|---|
| 0 | balance-rr | round-robin packets | yes (etherchannel) |
| 1 | active-backup | one active NIC, others standby | no |
| 4 | 802.3ad (LACP) | standards-based aggregation | yes (LACP) |
| 6 | balance-alb | adaptive load balancing | no |

`active-backup` (mode 1) is the safe default when you don't control the switch; `802.3ad`/LACP (mode 4) gives real aggregation but requires matching switch config.

```bash
ip link add bond0 type bond mode 802.3ad
ip link set eth0 down ; ip link set eth0 master bond0
ip link set eth1 down ; ip link set eth1 master bond0
ip link set bond0 up
cat /proc/net/bonding/bond0       # mode, active slave, link status, LACP info
```

With NetworkManager:

```bash
nmcli con add type bond ifname bond0 mode active-backup
nmcli con add type ethernet ifname eth0 master bond0
nmcli con add type ethernet ifname eth1 master bond0
nmcli con up bond0
```

Bonding is a bare-metal concern: physical servers bond two NICs to two switches for HA. In the cloud the hypervisor/ENI already handles redundancy and bandwidth, so you rarely bond inside a VM.

## How They Stack Together

These primitives compose. A common bare-metal pattern: bond two NICs, trunk VLANs over the bond, and bridge each VLAN for VMs/containers.

```
  eth0 ┐
       ├─ bond0 ── bond0.100 (VLAN) ── br-vlan100 ── vethA/vethB
  eth1 ┘                              (bridge into containers)
```

```bash
ip link add bond0 type bond mode 802.3ad
ip link add link bond0 name bond0.100 type vlan id 100
ip link add br-vlan100 type bridge
ip link set bond0.100 master br-vlan100
```

## A Note on tc / Traffic Shaping

Each interface (including bridges and bonds) has queueing disciplines (`qdisc`) you can shape with `tc`:

```bash
tc qdisc show dev eth0
tc qdisc add dev eth0 root tbf rate 100mbit burst 32kbit latency 400ms  # rate limit
tc qdisc add dev eth0 root netem delay 100ms loss 1%                     # emulate latency/loss
tc -s qdisc show dev eth0
```

`netem` is invaluable for testing how services behave under latency or packet loss; container runtimes and CNIs use `tc` for per-pod bandwidth limits.

## Relating to Containers

- `docker0` is just a Linux bridge with MASQUERADE — everything in T04 applies.
- **macvlan/ipvlan** drivers give containers a real presence on a VLAN/physical L2 without a bridge — useful when containers need to look like first-class hosts on the network.
- VLAN-aware bridges + `bridge vlan` let one bridge serve multiple isolated tenant networks.
- `tc` provides the per-container bandwidth limits some CNIs expose.

## Common Mistakes

- Enslaving an interface to a bridge while it still has an IP — move the IP to the bridge instead.
- Configuring a VLAN sub-interface but leaving the switch port as an access port (no trunk), so tagged frames are dropped.
- Choosing LACP (mode 4) without configuring LACP on the switch — links flap or only one stays up.
- Expecting bonding to double single-flow throughput; most modes hash per-flow, so one TCP stream rides one NIC.
- Forgetting STP on bridges with redundant paths, creating an L2 loop and a broadcast storm.
- Bonding inside a cloud VM where the hypervisor already provides HA — adds complexity for no gain.

## Best Practices

- Put the IP on the bridge, not on the enslaved NIC.
- Use `active-backup` when you don't control the switch; LACP only with matching switch config.
- Verify bonds with `/proc/net/bonding/bond0` and VLANs with `ip -d link show`.
- Persist bridges/VLANs/bonds in netplan/NetworkManager/`systemd-networkd`, not transient `ip` commands.
- Enable STP on bridges with any chance of redundant L2 paths.
- Use `tc netem` in staging to validate behavior under latency and loss before production.

## Quick Refs

```bash
# bridge
ip link add br0 type bridge ; ip link set br0 up
ip link set eth0 master br0
bridge link ; bridge fdb show
ip link set br0 type bridge vlan_filtering 1

# vlan
ip link add link eth0 name eth0.100 type vlan id 100
ip link set eth0.100 up ; ip a add 192.168.100.5/24 dev eth0.100

# bonding
ip link add bond0 type bond mode 802.3ad
ip link set eth0 master bond0 ; ip link set eth1 master bond0
cat /proc/net/bonding/bond0
nmcli con add type bond ifname bond0 mode active-backup

# traffic shaping
tc qdisc add dev eth0 root tbf rate 100mbit burst 32kbit latency 400ms
tc qdisc add dev eth0 root netem delay 100ms loss 1%
```

## Interview Prep

**Junior**: "What is a Linux bridge?"
- A virtual L2 switch in the kernel that learns MAC addresses and forwards frames between its ports; `docker0` is one.

**Mid**: "How do you isolate two networks over one NIC?"
- 802.1Q VLANs: create tagged sub-interfaces (`eth0.100`, `eth0.200`) on a trunked switch port, each on its own subnet and broadcast domain.

**Senior**: "Difference between active-backup and 802.3ad bonding?"
- Active-backup uses one NIC with the rest on standby for pure redundancy and needs no switch support; 802.3ad/LACP aggregates links for bandwidth and failover but requires LACP configured on the switch and hashes flows across members.

**Staff**: "Design NIC layout for an HA bare-metal hypervisor running container workloads."
- Bond two NICs in LACP (or active-backup across two switches for switch redundancy), trunk management/storage/tenant VLANs over the bond, bridge each VLAN for container/VM attachment, enable STP on bridges, and apply `tc` for per-tenant bandwidth — giving link redundancy, segmentation, and isolation on one physical layout.

## Next Chapter

→ Move to [L02/C07 — Namespaces & cgroups](../C07/README.md)
