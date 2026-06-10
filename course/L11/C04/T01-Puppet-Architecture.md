# L11/C04/T01 — Puppet Architecture (Master/Agent)

## Learning Objectives

- Understand Puppet model
- Run master+agent

## Puppet Components

- **Puppet Server**: central, holds code
- **Puppet Agent**: on each node
- **Facter**: collects facts
- **PuppetDB**: stores reports
- **Hiera**: data lookup

## Flow

```
Agent (every 30 min)
  → Sends facts
  → Server compiles catalog
  → Agent applies catalog
  → Reports back
```

Pull model.

## Install Server

```bash
# RHEL
sudo dnf install -y puppetserver
sudo systemctl enable puppetserver --now
```

Default port: 8140.

## Install Agent

```bash
sudo dnf install -y puppet-agent
sudo systemctl enable puppet --now
```

Default: polls every 30 min.

## Configure Agent

```ini
# /etc/puppetlabs/puppet/puppet.conf
[main]
server = puppet.example.com
certname = web01.example.com
environment = production
runinterval = 30m
```

## Cert Signing

```bash
# On agent (first run)
sudo /opt/puppetlabs/bin/puppet agent --test
# CSR sent to server

# On server
sudo puppetserver ca list
sudo puppetserver ca sign --certname web01.example.com

# Agent retries; cert installed
```

For: secure mutual TLS.

## Manifest

```puppet
# /etc/puppetlabs/code/environments/production/manifests/site.pp
node 'web01.example.com' {
  package { 'nginx':
    ensure => installed,
  }

  service { 'nginx':
    ensure => running,
    enable => true,
    require => Package['nginx'],
  }

  file { '/etc/nginx/nginx.conf':
    ensure  => file,
    content => template('nginx/nginx.conf.erb'),
    notify  => Service['nginx'],
  }
}
```

## Resources

Declarative units:
- `package`
- `service`
- `file`
- `user`
- `group`
- `cron`
- `exec` (escape hatch)

Each: type + name + attributes.

## Relationships

```puppet
require => Package['nginx']  # this depends on nginx package
notify => Service['nginx']    # change → restart nginx
subscribe => File['cfg']      # restart when cfg changes
before => Package['app']      # this before app package
```

Implicit dependency graph.

## Resource Ordering

```puppet
Package['nginx'] -> File['/etc/nginx/nginx.conf'] ~> Service['nginx']
```

- `->`: ordering
- `~>`: ordering + notify

## Classes

```puppet
class nginx (
  String $version = 'present',
  Integer $workers = 4,
) {
  package { 'nginx':
    ensure => $version,
  }

  file { '/etc/nginx/nginx.conf':
    content => template('nginx/nginx.conf.erb'),
    notify  => Service['nginx'],
  }

  service { 'nginx':
    ensure => running,
    enable => true,
  }
}
```

```puppet
# Apply
node 'web01' {
  class { 'nginx':
    workers => 8,
  }
}
```

## Modules

```
modules/
  nginx/
    manifests/
      init.pp        # nginx class
      install.pp     # install sub
      config.pp      # config sub
    templates/
      nginx.conf.erb
    files/
    facts.d/
    metadata.json
```

Like Ansible roles.

## Hiera

Data lookup:
```yaml
# data/common.yaml
nginx::workers: 4
nginx::port: 80
```

```yaml
# data/nodes/web01.yaml
nginx::workers: 8   # override
```

```puppet
class nginx (
  Integer $workers = lookup('nginx::workers'),
) {
}
```

For: separate code and data.

## Facter

Auto-collected facts:
```bash
facter os.family
facter networking.ip
facter memory.system.total_bytes
```

Use in manifests:
```puppet
if $facts['os']['family'] == 'RedHat' {
  package { 'httpd': }
} else {
  package { 'apache2': }
}
```

## Custom Facts

```ruby
# modules/myapp/facts.d/version.sh
#!/bin/bash
echo "myapp_version=$(cat /opt/myapp/VERSION)"
```

Sync'd via plugin sync; available as `$facts['myapp_version']`.

## Environments

```
production
staging
dev
```

```bash
puppet agent --test --environment=staging
```

Code lives in `/etc/puppetlabs/code/environments/<env>/`.

For: isolate config per env.

## r10k

GitOps for Puppet code:
```yaml
# Puppetfile
mod 'puppetlabs/nginx'
mod 'puppetlabs/stdlib', '8.5.0'
mod 'my_module', git: 'https://github.com/me/my_module.git', tag: 'v1.0'
```

```bash
r10k deploy environment -p
```

Deploys environments from Git.

## Code Manager

PE (Puppet Enterprise) GUI for r10k. Push code via PE UI.

## PuppetDB

Stores:
- Catalogs
- Facts
- Reports
- Resources

Queries:
```bash
puppet query 'nodes[certname] { catalog_environment = "production" }'
```

For: inventory, drift detection.

## Exported Resources

Cross-node configuration:
```puppet
# On each host
@@host { $facts['fqdn']:
  ip => $facts['networking']['ip'],
}

# On load balancer
Host <<| |>>   # collect all exported hosts
```

For: dynamic config from peers.

## Bolt

Ad-hoc commands:
```bash
bolt task run mytask --targets web01,web02
bolt command run 'uptime' --targets all
bolt apply manifest.pp --targets web01
```

Like Ansible push; no agent needed.

## Comparison Modes

### Apply
Local; no server:
```bash
puppet apply site.pp
```

For: standalone.

### Agent
Polls server.

### Bolt
Ad-hoc; SSH/WinRM.

## Reports

PuppetDB + UI shows:
- Last run
- Changes
- Failures
- Drift

## Idempotency

Declarative; built-in.

Resource model: ensure desired state.

## Vs Ansible

| | Puppet | Ansible |
|---|---|---|
| Model | Pull (default) | Push (default) |
| Agent | Yes | No |
| Language | Puppet DSL | YAML |
| Strength | Compliance, large fleets | Ad-hoc, simple |
| Compile catalog | Server | N/A |
| Reports | PuppetDB | Limited |

## Best Practices

- Modules versioned (r10k)
- Hiera for data
- Custom facts
- Roles + profiles (modules)
- Test (rspec-puppet)
- Run reports
- Code review manifests

## Common Mistakes

- exec everywhere (escape hatch)
- No version pinning
- Mixed code + data
- Skipping --noop / dry runs
- Wide-open environments

## Quick Refs

```bash
# Agent
puppet agent --test
puppet agent --test --noop  # dry run

# Apply standalone
puppet apply manifest.pp

# Cert
puppetserver ca list / sign / clean

# Query
puppet query 'nodes[certname] {}'

# Bolt
bolt command run / task run / apply
```

## Interview Prep

**Junior**: "What's Puppet."

**Mid**: "Manifests vs Hiera."

**Senior**: "r10k workflow."

**Staff**: "Puppet at scale."

## Next Topic

→ [T02 — Manifests, Modules, Hiera](T02-Manifests-Modules-Hiera.md)
