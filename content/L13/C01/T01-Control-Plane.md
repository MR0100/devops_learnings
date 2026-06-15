# L13/C01/T01 — The Control Plane

## Learning Objectives

- Diagram each control plane component and its responsibilities
- Explain the interactions between components (watch/reconcile, leader election)
- Trace a request from `kubectl` through the apiserver into etcd and back out to a kubelet
- Reason about HA topologies, failure modes, and recovery

## The Big Picture

The control plane is the cluster's brain. It holds **desired state**, observes **actual state**, and runs control loops that drive actual toward desired. It does **not** run your application containers — that's the data plane (T02). Every component talks to exactly one thing for state: the **kube-apiserver**, which is the only component that talks to **etcd**.

```
            ┌──────────────────────── Control Plane ───────────────────────┐
            │                                                               │
 kubectl ──►│  kube-apiserver ◄──────────── etcd (Raft, 3/5 members) │
 kubelet ──►│      ▲   ▲   ▲   (the ONLY writer/reader of etcd)            │
controllers►│      │   │   │                                                │
            │      │   │   └── kube-scheduler        (Pod → node binding)   │
            │      │   └────── kube-controller-mgr   (30+ control loops)    │
            │      └────────── cloud-controller-mgr  (LBs, routes, nodes)   │
            └───────────────────────────────────────────────────────────────┘
```

Everything is a **watch loop**: components subscribe to apiserver watch streams, react to changes, and write results back through the apiserver. Nothing reaches into etcd directly except the apiserver.

## The 5 Components

### 1. kube-apiserver

The front door. Every read and write — from `kubectl`, kubelets, controllers, the scheduler, operators — goes through it.

Responsibilities:
- REST API over HTTPS (port 6443 default)
- **Authentication**: client certs, bearer tokens, ServiceAccount tokens, OIDC, authn webhook
- **Authorization**: RBAC (most common), Node authorizer, ABAC, authz webhook
- **Admission control**: mutating then validating (built-in plugins + webhooks + ValidatingAdmissionPolicy) — see C06/T08
- **Schema validation** and defaulting against the OpenAPI schema
- **Persistence** to etcd (the only component that does)
- **Watch streams**: long-lived connections that push object changes to clients

It is **stateless** — all state lives in etcd — so it scales horizontally: run N apiservers behind a load balancer, all reading/writing the same etcd.

**API Priority & Fairness (APF)**: the apiserver fairly queues concurrent requests into priority levels so a noisy client (e.g. a hot-looping controller) can't starve critical traffic like leader-election or node heartbeats. APF replaced the old global `--max-requests-inflight` throttle.

### 2. etcd

The distributed key-value store — the **single source of truth**. Lose etcd without a backup, and you've lost the cluster.

- **Raft consensus**: odd-sized cluster (3, 5, 7) tolerating ⌊(n−1)/2⌋ failures — 3 nodes survive 1 loss, 5 survive 2
- One **leader** serves writes; followers replicate the log; reads can be linearizable or serializable
- Stores **every** API object (Pods, Deployments, Secrets, leases, leader-election records, events)
- **Latency-sensitive**: every write is `fsync`'d to disk — wants local SSD/NVMe and low network jitter
- **~8 GB** practical DB-size limit; needs periodic **compaction** + **defrag**
- **Encryption at rest** via `EncryptionConfiguration` (otherwise Secrets sit in plaintext in etcd and in backups)

```bash
# Health
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint health

# Snapshot (back this up daily, minimum)
etcdctl snapshot save snapshot.db
etcdctl snapshot restore snapshot.db
```

Deep dive in [T05](T05-etcd.md).

### 3. kube-scheduler

Assigns Pods that have **no `nodeName`** to a node. A three-phase pipeline:

- **Filter (predicates)**: which nodes *can* run this Pod? (free CPU/memory, taints vs tolerations, node affinity, volume zone, port conflicts)
- **Score (priorities)**: among the survivors, which node is *best*? (least-loaded, spread, image locality, inter-pod affinity)
- **Bind**: write `spec.nodeName` back via the apiserver

It's plugin-based (the scheduling framework) and extensible; you can run multiple schedulers. Internals in [T04](T04-Scheduler-Internals.md). Note: the scheduler only **decides** — the kubelet on the chosen node actually starts the Pod.

### 4. kube-controller-manager

A single binary running **30+ controllers**, each a watch-reconcile loop:

- deployment-controller — creates/updates ReplicaSets for Deployments
- replicaset-controller — creates Pods to match the desired replica count
- node-controller — marks nodes `NotReady`, evicts Pods after the eviction timeout
- job-controller, cronjob-controller — run-to-completion workloads
- endpoints / endpointslice-controller — keep Service backends in sync with ready Pods
- service-account-controller, namespace-controller, ttl-controller, … and more

Each loop is the same shape:

```
watch desired state  →  observe actual state  →  reconcile (act)  →  write status
```

This **reconciliation loop** is the fundamental Kubernetes pattern — every operator you write later (C10) follows it.

### 5. cloud-controller-manager (CCM)

Cloud-specific logic split out of the controller-manager so core Kubernetes stays cloud-agnostic:

- **service-controller**: provisions cloud load balancers for `type: LoadBalancer` Services
- **node-controller**: labels nodes with zone/region/instance-type, removes deleted cloud VMs
- **route-controller**: programs Pod-CIDR routes in the cloud's VPC route table

On managed offerings (EKS/GKE/AKS) the provider runs the CCM for you.

## The Request Path (kubectl apply → running container)

What actually happens on `kubectl apply -f deployment.yaml`:

1. `kubectl` → apiserver: `POST /apis/apps/v1/namespaces/X/deployments`
2. **Authentication** — verify who you are (client cert / token / OIDC)
3. **Authorization** — RBAC: are you allowed to `create deployments` in namespace X?
4. **Mutating admission** — webhooks/plugins may rewrite the object (inject a sidecar, set defaults)
5. **Validating admission** — webhooks/PSA/ValidatingAdmissionPolicy may reject it (e.g. "no privileged Pods")
6. **Schema validation + defaulting**, then **write to etcd**
7. apiserver returns `201 Created` to `kubectl`
8. apiserver **watch streams** notify subscribers
9. **deployment-controller** sees the new Deployment → creates a ReplicaSet
10. **replicaset-controller** sees the new RS → creates Pods (with **no** `nodeName`)
11. **scheduler** sees unscheduled Pods → filters + scores → writes `spec.nodeName`
12. **kubelet** on that node sees a Pod bound to it → pulls image, sets up CNI/CSI, starts containers
13. kubelet reports `Running` / `Ready` back to the apiserver → endpoints-controller adds the Pod to Service endpoints → traffic flows

Notice the apiserver and etcd are involved at *every* hop — components never talk to each other directly, only through the apiserver's API and watch streams.

## High Availability

```
                ┌──────────┐
                │ LB / VIP │   (e.g. controlPlaneEndpoint)
                └─────┬────┘
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      ┌───────┐   ┌───────┐   ┌───────┐
      │apisvr │   │apisvr │   │apisvr │   ← all active-active
      │sched  │   │sched  │   │sched  │   ← leader-elected (1 active)
      │ctrl   │   │ctrl   │   │ctrl   │   ← leader-elected (1 active)
      └───┬───┘   └───┬───┘   └───┬───┘
          ▼           ▼           ▼
        etcd ◄──────► etcd ◄──────► etcd   ← Raft, single write leader
```

- **apiservers are all active** — the LB spreads traffic across them; any can serve any request.
- **scheduler and controller-manager use leader election** (a `Lease` object in `kube-system`). Only the leader acts; the others stand by. This avoids two schedulers binding the same Pod twice.
- **3 control-plane nodes** is the production minimum (survives losing 1). Use 5 for very large or critical clusters.

### Stacked vs External etcd

- **Stacked** (kubeadm default): etcd runs on the same nodes as the control plane — simpler, fewer machines, but a node loss takes both an apiserver and an etcd member.
- **External**: etcd runs as its own dedicated cluster — more reliable and isolates etcd performance from control-plane load, at the cost of more machines and ops overhead. Preferred for large/tier-0 clusters.

## Failure Modes

| Component down | Impact | Recovery |
|---|---|---|
| **apiserver** (all) | No API ops; `kubectl` times out. **Existing Pods keep running**; kubelets keep containers alive but can't update status | Restart; check certs, etcd reachability, LB |
| **etcd quorum lost** | All writes fail; cluster state frozen. Pods keep running but nothing can change | Restore quorum or restore from snapshot (T05) |
| **scheduler** | New Pods stay **Pending**; running Pods unaffected | Restart (leader re-election is automatic in HA) |
| **controller-manager** | Deployments don't roll, failed nodes not evicted, Pods not GC'd, endpoints stale | Restart (leader re-election automatic in HA) |
| **CCM** | New `LoadBalancer` Services don't get an LB; volumes don't auto-attach; node labels stale | Restart / check cloud creds |
| **single control-plane node** (HA) | LB routes around it; leader re-elected; no user impact | Replace the node |

Key mental model: **the control plane manages change; the data plane runs workloads.** A dead control plane freezes the cluster's configuration but does **not** immediately kill running applications.

## Common Mistakes

- Putting etcd on slow or network-attached disks — `fsync` latency spikes cause apiserver timeouts and flapping leader elections.
- Running an **even** number of etcd members (e.g. 2 or 4) — no improvement in fault tolerance and worse split-brain risk; always use odd counts.
- Assuming "control plane down = outage" — running Pods survive; only *changes* stop.
- Forgetting `EncryptionConfiguration` — Secrets then sit in plaintext in etcd and in every etcd backup.
- No etcd backups (or never testing a restore) — the one failure you can't forward-fix.
- Treating apiserver as stateful or scaling etcd horizontally for *throughput* — etcd scales for HA, not write throughput (more members = slower writes).
- Letting one client hammer the apiserver — without APF awareness, a hot controller loop can degrade everything.

## Best Practices

- **3 (or 5) control-plane nodes** across failure domains/AZs; odd-numbered etcd.
- etcd on **local SSD/NVMe**; monitor `etcd_disk_wal_fsync_duration_seconds` and `etcd_server_leader_changes_seen_total`.
- **Automate etcd snapshots** and rehearse restore at least quarterly.
- Enable **encryption at rest** (KMS provider) for Secrets.
- Put a load balancer in front of the apiservers and use it as the `controlPlaneEndpoint`.
- Enable and centralize **audit logs** on the apiserver.
- Keep control-plane components and etcd within a low-latency network; don't stretch a single etcd cluster across high-latency regions.
- Monitor leader-election churn — frequent leader changes signal etcd or network trouble.

## Quick Refs

```bash
# Component health (control-plane node)
kubectl get componentstatuses          # legacy but quick
kubectl -n kube-system get pods         # static control-plane pods (kubeadm)

# Who is the current leader?
kubectl -n kube-system get lease        # kube-scheduler / kube-controller-manager leases

# Static pod manifests (kubeadm control plane)
ls /etc/kubernetes/manifests/
#   etcd.yaml  kube-apiserver.yaml  kube-controller-manager.yaml  kube-scheduler.yaml

# apiserver / etcd health
kubectl get --raw='/readyz?verbose'
kubectl get --raw='/livez?verbose'
etcdctl endpoint health
etcdctl endpoint status --write-out=table

# Watch the reconciliation in action
kubectl get events -A --sort-by=.lastTimestamp
```

| Component | Default port | State | Scaling |
|---|---|---|---|
| kube-apiserver | 6443 | stateless | active-active behind LB |
| etcd | 2379 (client), 2380 (peer) | the state | Raft, odd-numbered |
| kube-scheduler | 10259 | stateless | leader-elected |
| kube-controller-manager | 10257 | stateless | leader-elected |

## Interview Prep

**Mid**: "What are the components of the K8s control plane?"
- apiserver (the front door / only etcd client), etcd (source of truth), scheduler (Pod→node), controller-manager (30+ reconcile loops), cloud-controller-manager (cloud LBs/routes/nodes). Components only talk through the apiserver.

**Senior**: "etcd is down — what's the user impact?"
- All API writes fail and `kubectl` errors, so no new/changed resources. But **existing Pods keep running** — kubelets keep containers alive. Scheduling and all controllers stall. Recovery: restore quorum, or restore from the latest snapshot (which is why daily backups + a tested restore matter).

**Senior**: "How do the scheduler and controller-manager avoid acting twice in an HA setup?"
- Leader election via a `Lease`/lock object: only the leader runs the loops; standbys wait and take over on lease expiry. apiservers, by contrast, are all active because they're stateless.

**Staff**: "Design an HA control plane for a 1000-node cluster."
- **External 5-node etcd** on local NVMe (survives 2 losses), **3 apiservers** behind a load balancer used as `controlPlaneEndpoint`, leader-elected scheduler + controller-manager, encryption at rest with a KMS provider, automated etcd snapshots with periodic restore drills, audit logging, and APF tuned so node heartbeats and leader-election can't be starved by bulk clients.

**Principal**: "Walk me through the full request path of `kubectl apply -f deployment.yaml`."
- authn → authz (RBAC) → mutating admission → validating admission → schema validation/defaulting → write to etcd → `201`; then via watch: deployment-controller → ReplicaSet, replicaset-controller → Pods (no node), scheduler → binds `nodeName`, kubelet → pulls image, CNI/CSI, starts containers, reports Ready; endpoints-controller adds the Pod to Service endpoints. The apiserver + etcd sit on every hop; components never call each other directly.

## Next Topic

→ [T02 — The Data Plane](T02-Data-Plane.md)
