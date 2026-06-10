# L21/C04/T02 — MongoDB (Replica Sets, Sharding)

## Learning Objectives

- Operate MongoDB
- Use sharding

## MongoDB

Document DB:
- BSON
- Flexible schema
- Replica sets + sharding

## Replica Set

3+ mongod:
- 1 primary
- N secondaries
- Auto-failover

```bash
mongod --replSet rs0 --port 27017
mongo --eval 'rs.initiate({_id:"rs0",members:[{_id:0,host:"m1:27017"},{_id:1,host:"m2:27017"},{_id:2,host:"m3:27017"}]})'
```

## Failover

Primary down → election.
New primary elected.
App reconnects.

## Read Preference

```js
db.collection.find().readPref('secondaryPreferred')
```

For: read scaling.

## Write Concern

```js
db.collection.insertOne({...}, {writeConcern: {w: "majority"}})
```

Wait for majority ack.

For: durability.

## Sharding

Horizontal scale:
- Mongos: router
- Config servers (replica set)
- Shards (each replica set)

## Shard Key

Choose carefully:
- High cardinality
- Even distribution
- Match queries

For: even load.

## Shard Types

### Ranged
By value range.
- Hot ranges risk.

### Hashed
Hash of key.
- Even distribution.
- Range queries slower.

## Setup

```bash
# Config servers
mongod --configsvr --replSet csrs

# Shard servers
mongod --shardsvr --replSet shard0
mongod --shardsvr --replSet shard1

# Router
mongos --configdb csrs/configsvr1,...
```

```js
sh.addShard("shard0/m1,m2,m3")
sh.enableSharding("mydb")
sh.shardCollection("mydb.users", {user_id: "hashed"})
```

## Backup

- mongodump (logical)
- File system snapshot
- Atlas (managed)

```bash
mongodump --uri 'mongodb://...' --out /backup
mongorestore --uri 'mongodb://...' /backup
```

## Atlas

Managed:
- Easy
- Backups
- Multi-region
- Cost

## Performance

- Indexes critical
- Aggregation pipelines
- Profiler:
  ```js
  db.setProfilingLevel(1, {slowms: 100})
  ```

## Best Practices

- Replica set 3+
- Shard for > 1 TB
- Choose shard key well
- Backups + tested
- Atlas if budget

## Common Mistakes

- Shard with bad key
- Single-node prod
- No backup
- Wrong write concern

## Quick Refs

```js
rs.status()
rs.config()
sh.status()
db.collection.getIndexes()
db.collection.explain('executionStats').find({...})
```

## Interview Prep

**Mid**: "MongoDB replica."

**Senior**: "Sharding."

**Staff**: "MongoDB at scale."

## Next Topic

→ [T03 — Cassandra (Tunable Consistency)](T03-Cassandra.md)
