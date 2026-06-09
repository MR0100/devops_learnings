# L13/C01/T01 — The Control Plane

## Learning Objectives

- Diagram each control plane component and its responsibilities
- Explain interactions between components
- Reason about HA and failure modes

## The 4 Major Components

### 1. kube-apiserver

The front door. Everything goes through it.

- REST API over HTTPS (port 6443 default)
- Authentication (certificates, tokens, OIDC, webhook)
- Authorization (RBAC, webhook)
- Admission controllers (mutating, validating)
- Persistence to etcd
- Watch streams to clients (kubectl, kubelet, controllers)

Horizontal scaling: run multiple apiservers behind a load balancer; all read/write etcd directly.

### 2. etcd

The distributed KV store.

- Raft consensus (odd-numbered cluster: 3, 5, 7)
- Stores: every K8s object, secrets, leader election state
- Latency-sensitive (uses fsync)
- 8 GB practical limit
- Encryption at rest via EncryptionConfiguration

```bash
# Health
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint health

# Snapshot
etcdctl snapshot save snapshot.db
etcdctl snapshot restore snapshot.db
```

### 3. kube-scheduler

Assigns Pods (with no nodeName) to a node.

- Filters: which nodes CAN run this pod (resource, taints, affinity, etc.)
- Scores: which node SHOULD run it (lower spread, NUMA, image locality, etc.)
- Binds: writes nodeName back to the pod
- Plugins-based (extensible)

### 4. kube-controller-manager

A binary that runs many controllers:
- deployment-controller
- replicaset-controller
- node-controller
- service-controller
- endpoints-controller
- namespace-controller
- ... 30+ controllers

Each runs a control loop: watch desired state, observe actual, take action.

### 5. cloud-controller-manager

Cloud-specific: provisions load balancers, attaches volumes, adds routes for the cloud's VPC. Runs the cloud-specific node controllers.

## High Availability

```
       ┌──────────┐
       │ LB / VIP │
       └─────┬────┘
             ▼
   ┌─────────┬─────────┐
   │ apisvr  │ apisvr  │  (active-active)
   │ + sched │ + sched │  (leader election among schedulers)
   │ + ctrl  │ + ctrl  │  (leader election among controllers)
   └────┬────┴────┬────┘
        ▼         ▼
       etcd ◄─► etcd ◄─► etcd  (Raft, single leader for writes)
```

**Recommended**: 3 control plane nodes for production. Schedulers and controllers use leader election (only 1 active); apiservers are all active.

### Stacked vs External etcd

- **Stacked**: etcd runs on same nodes as control plane (kubeadm default)
- **External**: etcd is a separate cluster
- External is more reliable but more operational overhead

## Resource Path

A `kubectl apply deployment.yaml`:
1. kubectl → apiserver: POST /apis/apps/v1/namespaces/X/deployments
2. apiserver authn (cert)
3. apiserver authz (RBAC)
4. mutating admission webhooks (e.g., inject sidecar)
5. validating admission webhooks (e.g., OPA)
6. apiserver writes to etcd
7. apiserver returns 201 to kubectl
8. apiserver watch streams notify controllers
9. deployment-controller sees new Deployment → creates ReplicaSet
10. replicaset-controller sees new RS → creates Pods (no node)
11. scheduler sees Pods → picks nodes → updates pod.spec.nodeName
12. kubelet on that node sees pod with own nodeName → runs container

## Failure Modes

| Component Down | Impact |
|---|---|
| apiserver | All API ops fail; existing pods keep running; kubelet keeps reporting status (but can't update) |
| etcd quorum lost | All writes fail; reads from leader fail; pods keep running |
| scheduler | New pods are Pending; existing pods unaffected |
| controller-manager | Deployments don't roll; nodes not marked NotReady; pods not GC'd |
| ccm | New LBs not provisioned; volumes don't attach automatically |

## Interview Prep

**Mid**: "What are the components of the K8s control plane?"

**Senior**: "etcd is down. What's the user impact?"
- API ops fail. Existing pods keep running. Scheduling stops.

**Staff**: "Design an HA control plane for a 1000-node cluster."
- 5-node etcd (external), 3 apiservers behind LB, leader-elected scheduler/controller-manager, etcd on local NVMe.

**Principal**: "Walk me through the full request path of a `kubectl apply -f deployment.yaml`."

## Next Topic

→ [T02 — The Data Plane](T02-Data-Plane.md)
