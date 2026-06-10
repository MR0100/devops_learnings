# L18/C02/T04 — Index Lifecycle Management

## Learning Objectives

- Configure ILM
- Optimize cost

## ILM

Auto-manage index lifecycle:
- Hot: writable, fast
- Warm: read-only
- Cold: searchable, slow
- Frozen: rare access
- Delete: gone

## Phases

```
Hot:
- SSD
- Replicated
- High IOPS

Warm:
- Cheaper disks
- Smaller shard count

Cold:
- Searchable but slow
- HDD or compressed

Frozen:
- S3 / object storage
- Searched rarely

Delete:
- Auto-remove
```

## Policy

```json
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_size": "50GB",
            "max_age": "7d"
          },
          "set_priority": { "priority": 100 }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": { "number_of_shards": 1 },
          "forcemerge": { "max_num_segments": 1 },
          "allocate": { "include": { "data": "warm" } },
          "set_priority": { "priority": 50 }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "allocate": { "include": { "data": "cold" } },
          "set_priority": { "priority": 0 }
        }
      },
      "frozen": {
        "min_age": "90d",
        "actions": {
          "searchable_snapshot": { "snapshot_repository": "s3-backup" }
        }
      },
      "delete": {
        "min_age": "365d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

## Rollover

When index hits size/age:
- Create new index
- New writes to new
- Old becomes warm-eligible

```json
"rollover": {
  "max_size": "50GB",
  "max_age": "7d",
  "max_docs": 1000000
}
```

## Index Templates

```json
PUT /_index_template/logs-template
{
  "index_patterns": ["logs-*"],
  "data_stream": {},
  "template": {
    "settings": {
      "index.lifecycle.name": "logs-policy",
      "index.lifecycle.rollover_alias": "logs"
    },
    "mappings": { ... }
  }
}
```

Auto-apply to new logs-* indices.

## Data Streams

Modern:
- Hides rollover complexity
- Single logical "stream"
- Backing indices managed

```bash
POST /logs/_doc
{ ... }
```

Writes to current backing index.

## Tiers

Allocate to specific nodes:
```yaml
node.attr.data: hot

# OR

node.roles: [data_hot]
```

ILM places shards on right nodes.

## Searchable Snapshots

Frozen tier:
- Index in S3
- Search lazy-loads
- Cheap storage; slow query

For: years of retention.

## Hot/Warm Sizing

For 100 GB/day, 7 days hot:
- 700 GB hot data
- ~1 TB with replicas

For 30 days warm: 3 TB.

For 90 days cold (frozen): 9 TB but in S3 cheap.

## Cost Tier

| Tier | Storage cost/GB/mo |
|---|---|
| Hot (SSD) | $0.20 |
| Warm (HDD) | $0.08 |
| Cold | $0.04 |
| Frozen (S3) | $0.02 |

For: order-of-magnitude savings.

## Triggers

Manual:
```bash
POST /logs/_lifecycle/explain
POST /logs/_rollover
```

For: troubleshoot or force.

## Status

```bash
GET /logs/_ilm/explain
```

Shows phase, last action.

## Failed Actions

If shrink / forcemerge fails:
- Index stuck
- Manual intervention

For: investigate; rerun.

## Best Practices

- ILM from day 1
- Data streams for logs
- Tier nodes (hot/warm/cold attrs)
- Searchable snapshots for long retention
- Monitor index counts

## Common Mistakes

- No ILM (disk fills)
- Too many small indices (cluster state bloat)
- Force-merge in hot (writes blocked)
- Wrong allocate (shards not moving)

## Per-Index Settings

```bash
PUT /logs/_settings
{
  "index.lifecycle.name": "logs-policy"
}
```

Attach to existing.

## Test in Lower Env

ILM bugs:
- Stuck indices
- Wrong policies

Test before prod.

## Quick Refs

```bash
# Apply policy
PUT /_ilm/policy/X

# Attach
PUT /_index_template/Y

# Status
GET /index/_ilm/explain
GET /_ilm/policy/X

# Manual
POST /index/_ilm/move/<step>
```

## Interview Prep

**Mid**: "What's ILM."

**Senior**: "Hot/warm/cold."

**Staff**: "Retention cost optimization."

## Next Topic

→ Move to [L18/C03 — Loki](../C03/README.md)
