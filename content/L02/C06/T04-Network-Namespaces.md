# L02/C06/T04 — Network Namespaces

## Learning Objectives

- Explain what a network namespace isolates and why it underpins containers
- Create namespaces and connect them with veth pairs
- Build a working two-namespace topology with a bridge and NAT
- Map manual `ip netns` operations to what container runtimes do automatically

## The Big Picture

A **network namespace** is a private copy of the entire network stack: its own interfaces, routing tables, ARP/neighbor cache, netfilter rules, `/proc/sys/net` tunables, and socket/port space. A process inside one sees only that namespace's networking. This is the single most important primitive behind container networking — a container is mostly "a process in its own set of namespaces."

```
        Host (root) network namespace
   ┌──────────────────────────────────────────┐
   │ eth0   lo   docker0(bridge)               │
   │                  │                        │
   │             vethA│  vethC                 │
   └──────────────────┼───────┼────────────────┘
                      │ veth  │ veth
      ┌───────────────┼──┐ ┌──┼───────────────┐
      │ netns red     │  │ │  │  netns blue    │
      │  eth0 ────────┘  │ │  └──────── eth0   │
      │  10.0.0.2/24     │ │   10.0.0.3/24     │
      └──────────────────┘ └───────────────────┘
```

Each namespace has its own `lo` (starts down), its own routing table, and its own firewall — completely independent of the host.

## Creating and Inspecting Namespaces

```bash
ip netns add red                  # create a named namespace
ip netns list                     # list named namespaces
ip netns exec red ip a            # run a command inside it
ip netns exec red bash            # interactive shell inside it
ip netns delete red               # remove
```

`ip netns` stores a bind-mount under `/var/run/netns/<name>`, which is why named namespaces persist even with no process in them. The lower-level primitive is `unshare`:

```bash
unshare --net bash                # new netns for this shell (anonymous)
ip a                              # only lo, and it's down
```

Docker's namespaces are *not* named, so they don't appear in `ip netns list` by default — but you can expose one:

```bash
pid=$(docker inspect -f '{{.State.Pid}}' mycontainer)
mkdir -p /var/run/netns
ln -sf /proc/$pid/ns/net /var/run/netns/mycontainer
ip netns exec mycontainer ip a    # now visible to ip netns
nsenter -t $pid -n ip a           # same idea without the symlink
```

## veth Pairs — The Connector

A namespace is an island; a **veth pair** is the cable between islands. It's two interfaces always created together — a packet into one comes out the other. Move one end into a namespace and you've bridged the two stacks.

```bash
ip link add veth-red type veth peer name veth-host   # create the pair
ip link set veth-red netns red                       # move one end into 'red'
ip link set veth-host up                             # bring host end up
ip netns exec red ip link set veth-red up
ip netns exec red ip link set lo up                  # don't forget loopback
ip netns exec red ip a add 10.0.0.2/24 dev veth-red
ip a add 10.0.0.1/24 dev veth-host                   # host end gets the .1
ip netns exec red ip r add default via 10.0.0.1      # default route out
```

Now `ping 10.0.0.2` from the host and `ip netns exec red ping 10.0.0.1` both work — you've reproduced the core of container networking by hand.

## Connecting Many Namespaces via a Bridge

Two namespaces could share a veth directly, but to connect *many* you put a **bridge** in the host and plug each namespace's host-side veth into it (this is the `docker0` model).

```bash
# bridge in host
ip link add br0 type bridge
ip a add 10.0.0.1/24 dev br0
ip link set br0 up

# for each namespace (red, blue ...)
ip netns add red
ip link add veth-red type veth peer name veth-red-br
ip link set veth-red netns red
ip link set veth-red-br master br0          # plug host end into the bridge
ip link set veth-red-br up
ip netns exec red ip link set lo up
ip netns exec red ip link set veth-red up
ip netns exec red ip a add 10.0.0.2/24 dev veth-red
ip netns exec red ip r add default via 10.0.0.1
```

Repeat with `blue`/`10.0.0.3` and the two namespaces can ping each other through `br0` — a software L2 switch.

## Giving Namespaces Internet (NAT)

The namespace can reach the host, but to reach the outside world the host must forward and SNAT its traffic:

```bash
sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o eth0 -j MASQUERADE
iptables -A FORWARD -i br0 -o eth0 -j ACCEPT
iptables -A FORWARD -i eth0 -o br0 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
```

This is precisely Docker's default bridge networking: bridge + veth per container + `ip_forward` + MASQUERADE.

## What Runtimes Do for You

| Manual step | Runtime equivalent |
|---|---|
| `ip netns add` / `unshare --net` | runtime creates the netns on container start |
| `ip link add veth` + move into ns | CNI plugin / libnetwork creates the veth pair |
| plug host end into `br0` | attach to `docker0` (bridge CNI) or routed endpoint |
| assign IP + default route | IPAM plugin allocates IP, installs routes |
| MASQUERADE + ip_forward | runtime/CNI installs NAT and forwarding rules |

Kubernetes adds the **pause container**: it owns the netns so app containers in a pod join it (`--net=container:pause`) and thus share one IP and localhost — which is why containers in a pod reach each other over `127.0.0.1`.

## Common Mistakes

- Forgetting to bring up `lo` inside the namespace — loopback-based health checks and IPC fail.
- Bringing up only one end of the veth pair (both ends and the bridge must be `up`).
- Setting addresses/routes but missing `ip_forward` or MASQUERADE, so nothing reaches the internet.
- Expecting `ip netns list` to show Docker/containerd namespaces (they're anonymous unless you bind-mount them).
- Leaking namespaces/veth pairs in scripts — deleting a netns removes interfaces inside it, but dangling host-side veths can pile up.
- Assuming firewall rules are shared — each namespace has its own netfilter ruleset.

## Best Practices

- Always `ip link set lo up` first thing inside a new namespace.
- Use `ip netns exec <ns> <cmd>` (or `nsenter -t PID -n`) to debug rather than guessing from the host.
- Tear down cleanly: `ip netns delete` removes the namespace and the interfaces it contains.
- Prefer letting CNIs/runtimes manage production namespaces; use manual `ip netns` for learning and ad-hoc debugging.
- Keep an isolated test topology in a script so you can rebuild it repeatably.

## Quick Refs

```bash
ip netns add red                       # create
ip netns list                          # list named ns
ip netns exec red <cmd>                # run in ns
ip netns delete red                    # remove
unshare --net bash                     # anonymous netns shell

ip link add veth0 type veth peer name veth1   # veth pair
ip link set veth1 netns red                    # move into ns
ip netns exec red ip link set lo up            # bring loopback up
ip netns exec red ip a add 10.0.0.2/24 dev veth1
ip netns exec red ip r add default via 10.0.0.1

# expose a docker container's netns
pid=$(docker inspect -f '{{.State.Pid}}' NAME)
ln -sf /proc/$pid/ns/net /var/run/netns/NAME
nsenter -t $pid -n ip a

sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o eth0 -j MASQUERADE
```

## Interview Prep

**Junior**: "What does a network namespace isolate?"
- The whole network stack: interfaces, routing table, ARP cache, firewall rules, and port/socket space — a process inside sees only that namespace's networking.

**Mid**: "How do two namespaces talk to each other?"
- A veth pair: two linked interfaces, one end in each namespace (or one in a host bridge), so a packet into one end exits the other; add IPs and routes and they communicate.

**Senior**: "Reproduce Docker's default bridge networking by hand."
- Create a bridge with an IP, a veth per namespace with the host end plugged into the bridge, assign each namespace an IP and default route via the bridge, then enable `ip_forward` and MASQUERADE the subnet out the uplink.

**Staff**: "Why do containers in the same Kubernetes pod share an IP and localhost?"
- They join a single network namespace owned by the pause container (`--net=container:pause`), so they share its interfaces, IP, and loopback — letting them communicate over 127.0.0.1 while remaining separate in other namespaces.

## Next Topic

→ [T05 — Bridges, VLANs, Bonding](T05-Bridges-VLANs-Bonding.md)
