# L11/C04/T03 — Catalog Compilation

## Learning Objectives

- Understand Puppet catalog
- Debug compilation

## Catalog

JSON document: desired state of node.

Compiled per-node by server:
```
Facts (from agent)
   ↓
Puppet code (manifests + Hiera)
   ↓
Catalog (specific to node)
   ↓
Sent to agent
   ↓
Agent applies
```

## Compilation Steps

1. Agent sends facts to server
2. Server loads code (environment)
3. Server evaluates node classifier → assigns classes/roles
4. Server evaluates classes/manifests
5. Hiera lookups
6. Resource graph built
7. Catalog serialized to JSON
8. Agent receives, applies

## View Catalog

```bash
puppet catalog find web01.example.com > catalog.json
```

Inspect:
```bash
jq '.resources[] | select(.type == "Service")' catalog.json
```

## Debugging

```bash
# On server
puppet agent --test --debug --trace

# Show what would change
puppet agent --test --noop
```

## ENC (External Node Classifier)

Script that returns classes per node:
```bash
#!/bin/bash
# enc.sh
cat <<EOF
---
classes:
  - profiles::base
  - roles::webserver
environment: production
EOF
```

```ini
# /etc/puppetlabs/puppet/puppet.conf
[main]
node_terminus = exec
external_nodes = /etc/puppetlabs/code/enc.sh
```

For: external decision logic (LDAP, DB).

## site.pp (Default ENC)

```puppet
# site.pp
node default {
  include profiles::base
}

node /^web\d+\.example\.com$/ {
  include roles::webserver
}

node 'db01.example.com' {
  include roles::database
}
```

Simple; embedded in code.

## Hiera Classification

```yaml
# data/nodes/web01.yaml
classes:
  - roles::webserver
```

```puppet
# site.pp
node default {
  include lookup('classes', Array, 'unique')
}
```

For: data-driven classification.

## Performance

Catalog compilation: expensive.
- Hiera lookups: each = file read
- Resource counts: 1000s common
- Compile time: seconds

For huge fleets: multiple compile servers.

## Cache

PuppetDB caches catalogs.
Agent compares facts; server skips compile if facts unchanged.

For: speed.

## Resource Graph

```
Package[nginx] → File[/etc/nginx/nginx.conf] ~> Service[nginx]
```

Cycles: compile fails.

Use puppetlabs/graph module to visualize.

## Containment

```puppet
class app {
  contain app::install
  contain app::config
  contain app::service
}

class app::install { ... }
class app::config { ... }
class app::service { ... }
```

`contain`: subclass becomes part of parent for ordering.

## Anchor Pattern (Legacy)

Old way:
```puppet
class app {
  anchor { 'app::begin': } ->
  Class['app::install'] ->
  Class['app::config'] ~>
  Class['app::service'] ~>
  anchor { 'app::end': }
}
```

`contain` is modern.

## Stages

```puppet
stage { 'pre':  before => Stage['main'] }
stage { 'post': require => Stage['main'] }

class { 'profiles::base':
  stage => 'pre',
}
```

For: ordering across classes.

## Run Order

1. Pre stage
2. Main stage (default)
3. Post stage

Within stage: dependencies dictate.

## Catalog Diff

```bash
# Compare environments
puppet catalog diff catalog1.json catalog2.json
```

For: see what changes when env updated.

## Reports

PuppetDB stores:
- Resource changes
- Failures
- Duration

Query:
```bash
puppet query 'reports[certname, time] { status = "failed" }'
```

For: drift, audit.

## Trusted Facts

Set by server (not agent):
- `$trusted['certname']`
- `$trusted['authenticated']`

Tamper-proof; use for security decisions.

## Custom Facts

```ruby
# /opt/puppetlabs/puppet/cache/lib/facter/myfact.rb
Facter.add(:myfact) do
  setcode do
    'value'
  end
end
```

Pluginsync sends to all agents.

## Common Issues

### Dup Resources
```puppet
file { '/etc/foo': content => 'a' }
file { '/etc/foo': content => 'b' }  # ERROR: duplicate
```

Each resource name: unique per catalog.

### Cycle
```puppet
File['a'] -> File['b']
File['b'] -> File['a']
```

Catalog fails.

### Hiera Miss
```
Error: Could not find data item nginx::workers
```

Missing in hiera; no default. Add default.

## Performance Tuning

### JRuby Instances
```ini
# /etc/puppetlabs/puppetserver/conf.d/puppetserver.conf
jruby-puppet: {
  max-active-instances: 4
}
```

More JRuby = more concurrent compiles.

### Heap
```bash
-Xmx4g
```

Bigger heap for many JRuby.

### Hiera Cache
Built-in 5-min default. Tune.

## Compile Server Pool

For huge fleets:
- Multiple servers behind LB
- All connect to PuppetDB
- Agents random-pick

For: scale compilation.

## Best Practices

- Containment for ordering
- Hiera for data (not in code)
- Test catalogs (rspec-puppet)
- PuppetDB for reports
- Compile server cluster for scale

## Common Mistakes

- exec resources (avoid)
- Cycle in dependencies
- Hiera miss errors
- Single compile server (bottleneck)
- No reports (blind to drift)

## Quick Refs

```bash
# Compile catalog manually
puppet master --compile NODE.example.com

# Get from server
puppet catalog find NODE.example.com

# Debug
puppet agent --test --debug

# Noop
puppet agent --test --noop

# Force run
puppet agent --test --no-splay
```

## Interview Prep

**Mid**: "What's a catalog."

**Senior**: "Catalog compilation flow."

**Staff**: "Performance tuning Puppet."

## Next Topic

→ Move to [L11/C05 — Chef](../C05/README.md)
