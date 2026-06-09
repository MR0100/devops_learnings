# L11/C04 — Puppet

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Architecture.md) | Architecture (Master/Agent) | 0.5 hr |
| [T02](T02-Manifests-Modules-Hiera.md) | Manifests, Modules, Hiera | 1 hr |
| [T03](T03-Catalog.md) | Catalog Compilation | 0.5 hr |

## Architecture

```
[Puppet Master/Server]
     │
     │  every ~30 min
     │
┌────┼────┬────────┬────────┐
▼    ▼    ▼        ▼        ▼
Agent Agent Agent Agent ... Agent
```

- **Master/Server**: holds manifests, modules, Hiera data; compiles catalogs
- **Agent**: pulls catalog periodically, applies, reports back
- **PuppetDB**: stores facts, catalogs, reports
- **Foreman**: optional UI for inventory + reporting

### Communication
- Agents authenticate via certificates (Puppet has its own PKI)
- HTTPS to master
- Catalog (per-node "compiled plan") is encrypted in transit

## Manifests

Puppet DSL — declarative, similar to a programming language.

```puppet
# /etc/puppetlabs/code/environments/production/manifests/site.pp
node 'web1.example.com' {
  include nginx
  include nodejs
  
  package { 'htop':
    ensure => present,
  }
  
  file { '/etc/motd':
    ensure  => file,
    content => "Welcome to ${fqdn}\n",
    mode    => '0644',
    owner   => 'root',
  }
  
  service { 'nginx':
    ensure  => running,
    enable  => true,
    require => Package['nginx'],
  }
}
```

### Resources
Resources are the building blocks. Types: `package`, `file`, `service`, `user`, `group`, `cron`, `mount`, `exec`, etc.

### Relationships
```puppet
Package['nginx'] -> File['/etc/nginx/nginx.conf'] ~> Service['nginx']
                     # before                       # notify (restart on change)
```

Or in resource:
```puppet
service { 'nginx':
  require   => Package['nginx'],
  subscribe => File['/etc/nginx/nginx.conf'],
}
```

## Modules

```
modules/nginx/
├── manifests/
│   ├── init.pp           # class nginx { ... }
│   ├── config.pp         # class nginx::config { ... }
│   └── service.pp
├── files/                # static files
├── templates/            # ERB or EPP templates
├── data/                 # Hiera data (module-level)
├── lib/                  # custom facts, functions, types
├── examples/
└── metadata.json
```

Use:
```puppet
include nginx
class { 'nginx': workers => 8 }
```

## Hiera

Hierarchical key-value store for parameters. Keep data out of code.

```yaml
# hiera.yaml
version: 5
defaults:
  datadir: data
  data_hash: yaml_data
hierarchy:
  - name: "Per-node"
    path: "nodes/%{trusted.certname}.yaml"
  - name: "Per-environment"
    path: "environments/%{server_facts.environment}.yaml"
  - name: "Per-OS"
    path: "os/%{os.family}.yaml"
  - name: "Common"
    path: "common.yaml"
```

```yaml
# data/common.yaml
nginx::workers: 4
ntp::servers:
  - pool.ntp.org

# data/environments/production.yaml
nginx::workers: 16
```

## Catalog Compilation

```
Agent reports facts → Master
   ↓
Master loads manifests + modules
   ↓
Looks up data via Hiera
   ↓
Resolves classes, resources
   ↓
Compiles catalog (DAG of resources)
   ↓
Sends catalog to agent
   ↓
Agent applies (in DAG order)
   ↓
Agent reports back to PuppetDB
```

### Why Catalogs Matter
- Pure data (idempotent intent)
- Master can compile any node's catalog without that node present
- Reports give cluster-wide visibility (PuppetDB)
- Catalogs can be cached / diff'd

## When Puppet Today

- Long-running fleets needing self-healing convergence
- Regulated industries with mandatory drift correction
- Heritage Puppet shops

Most cloud-native orgs have moved away from Puppet.

## Pros & Cons

### Pros
- Mature, predictable
- Self-healing (drift auto-corrects each run)
- Reporting via PuppetDB
- Strong type system

### Cons
- Steep learning curve
- Master is critical infra
- Per-node agent maintenance
- Less momentum than Ansible

## Interview Themes

- "Puppet vs Ansible — when each?"
- "Catalog compilation — what is it?"
- "How does Hiera help separate data from code?"
- "Self-healing convergence — explain"
