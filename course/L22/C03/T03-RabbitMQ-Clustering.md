# L22/C03/T03 — RabbitMQ Clustering

## Learning Objectives

- Build RabbitMQ cluster
- HA setup

## Cluster

Multiple nodes share metadata:
- Federation
- Distributed
- HA

## Setup

```bash
# Node 1
rabbitmq-server -detached

# Node 2
rabbitmqctl stop_app
rabbitmqctl join_cluster rabbit@node1
rabbitmqctl start_app

# Node 3
similar
```

## Erlang Cookie

```
/var/lib/rabbitmq/.erlang.cookie
```

Same across nodes.

For: cluster auth.

## Cluster Type

### RAM Nodes
Metadata in memory.
Faster; lost on restart.

### Disk Nodes
Metadata on disk.
Default; recommended.

## Quorum

Need majority for cluster:
- 3 nodes: 2 majority
- 5 nodes: 3 majority

For: split-brain.

## Network Partition

```ini
cluster_partition_handling = pause_minority
```

If minority: pause; wait for heal.

For: avoid split-brain.

## Federation

Cross-cluster:
- Sender → receiver
- Replicate messages

For: geographically separated.

## Shovel

Move messages between brokers:
- One-time
- Or continuous

For: migration.

## Mirroring Old

Mirrored queues across nodes (legacy).

Replaced by quorum.

## Quorum HA

Quorum queue:
- 3+ replicas
- Auto leader election
- Survives node loss

For: built-in HA.

## Monitoring

```bash
rabbitmqctl cluster_status
rabbitmqctl list_queues
rabbitmqadmin --host=node1 list nodes
```

## Web UI

```bash
rabbitmq-plugins enable rabbitmq_management
```

Port 15672.

## Load Balancer

In front of cluster:
- HAProxy / nginx
- Spread connections

## Production

For HA:
- 3+ nodes
- Quorum queues
- pause_minority
- Backup metadata
- Monitor

## Cost

- 3 RabbitMQ instances: $300-1000/mo (on cloud)
- Plus storage

## Compared to Cloud SQS

- SQS: managed; no ops
- RabbitMQ: features + complexity

For low ops: SQS.
For feature need: RabbitMQ.

## Best Practices

- 3+ nodes
- Quorum queues
- pause_minority
- Backup definitions
- Monitor lag / queue depth

## Common Mistakes

- 2-node cluster (split brain easy)
- Default mirroring (use quorum)
- No backup
- Mix queue types badly

## Quick Refs

```bash
# Cluster
rabbitmqctl cluster_status / join_cluster / forget_cluster_node

# Queue
rabbitmqctl list_queues / set_policy

# Federation / Shovel
rabbitmq-plugins enable rabbitmq_federation / rabbitmq_shovel
```

## Interview Prep

**Mid**: "RabbitMQ cluster."

**Senior**: "HA design."

## Next Topic

→ Move to [L22/C04 — Pulsar](../C04/README.md)
