# L11/C04/T02 — Manifests, Modules, Hiera

## Learning Objectives

- Structure Puppet code
- Use Hiera

## Manifest

`.pp` file:
```puppet
# init.pp
class nginx {
  package { 'nginx': ensure => installed }
  service { 'nginx': ensure => running, enable => true }
}
```

## Module Structure

```
modules/nginx/
  manifests/
    init.pp       # nginx class
    install.pp    # nginx::install
    config.pp     # nginx::config
    service.pp    # nginx::service
  templates/
    nginx.conf.epp
  files/
    fastcgi_params
  facts.d/
  metadata.json
  README.md
  examples/
  spec/
```

## Sub-Classes

```puppet
# init.pp
class nginx {
  contain nginx::install
  contain nginx::config
  contain nginx::service

  Class['nginx::install'] -> Class['nginx::config'] ~> Class['nginx::service']
}

# install.pp
class nginx::install {
  package { 'nginx': ensure => installed }
}

# config.pp
class nginx::config {
  file { '/etc/nginx/nginx.conf':
    content => epp('nginx/nginx.conf.epp'),
  }
}

# service.pp
class nginx::service {
  service { 'nginx': ensure => running, enable => true }
}
```

Separation of concerns.

## Templates

EPP (newer) or ERB:
```epp
<%# nginx/templates/nginx.conf.epp %>
<%- | Integer $workers, Integer $port | -%>
worker_processes <%= $workers %>;

http {
  server {
    listen <%= $port %>;
  }
}
```

Use:
```puppet
content => epp('nginx/nginx.conf.epp', { 'workers' => 4, 'port' => 80 })
```

ERB (Ruby):
```erb
worker_processes <%= @workers %>;
listen <%= @port %>;
```

## Parameters

```puppet
class nginx (
  Integer $workers = 4,
  Integer $port = 80,
  Optional[String] $ssl_cert = undef,
) {
  # Use $workers, $port, $ssl_cert
}
```

Type checking + defaults.

## Apply with Params

```puppet
class { 'nginx':
  workers => 8,
  port    => 8080,
}
```

Or via Hiera (auto):
```yaml
nginx::workers: 8
nginx::port: 8080
```

## Hiera

YAML data layer:
```yaml
# hiera.yaml
version: 5
hierarchy:
  - name: "Nodes"
    path: "nodes/%{trusted.certname}.yaml"
  - name: "OS family"
    path: "os/%{facts.os.family}.yaml"
  - name: "Common"
    path: "common.yaml"
```

Lookup order: specific → general.

## Data Files

```yaml
# data/common.yaml
nginx::workers: 4

# data/os/RedHat.yaml
nginx::package_name: 'nginx'

# data/nodes/web01.example.com.yaml
nginx::workers: 8  # specific override
```

## Lookup

In class:
```puppet
class nginx (
  Integer $workers,   # required; comes from Hiera
) {
}
```

Hiera supplies via `lookup`. Auto-bound by class param name.

## Manual Lookup

```puppet
$workers = lookup('nginx::workers', { default_value => 4 })
```

For: non-class-param data.

## Hiera Backends

- YAML (default)
- JSON
- Vault (encrypted)
- eyaml (encrypted YAML)
- Custom

## Encrypted Hiera (eyaml)

```yaml
# data/secrets.eyaml
db_password: >
  ENC[PKCS7,...]
```

Decrypted at lookup. Like Ansible Vault.

## Roles + Profiles Pattern

Roles:
```puppet
# roles/manifests/webserver.pp
class roles::webserver {
  include profiles::base
  include profiles::nginx
  include profiles::monitoring
}
```

Profiles:
```puppet
# profiles/manifests/nginx.pp
class profiles::nginx {
  class { 'nginx':
    workers => 4,
  }
  # firewall, monitoring, etc.
}
```

Modules: stay generic; profile = app + opinions.

Each node: one role.

For: scale, modularity.

## Defined Types

```puppet
define mymodule::vhost(
  String $servername,
  Integer $port = 80,
) {
  file { "/etc/nginx/sites/${name}":
    content => epp('mymodule/vhost.epp', { ... }),
  }
}

# Use multiple times
mymodule::vhost { 'site1':
  servername => 'site1.com',
}
mymodule::vhost { 'site2':
  servername => 'site2.com',
  port       => 8080,
}
```

For: per-instance config.

## Iteration

```puppet
$users = ['alice', 'bob', 'carol']
$users.each |$user| {
  user { $user:
    ensure => present,
  }
}
```

Or with Hiera:
```yaml
my_users:
  - alice
  - bob
```

```puppet
$users = lookup('my_users')
$users.each |$u| {
  user { $u: ensure => present }
}
```

## Conditional

```puppet
if $facts['os']['family'] == 'RedHat' {
  package { 'httpd': ensure => installed }
}

case $facts['os']['family'] {
  'RedHat': { include profiles::rhel }
  'Debian': { include profiles::debian }
  default:  { fail("Unsupported OS") }
}
```

## Tests

### rspec-puppet
```ruby
# spec/classes/nginx_spec.rb
require 'spec_helper'

describe 'nginx' do
  it { is_expected.to contain_package('nginx') }
  it { is_expected.to contain_service('nginx').with_ensure('running') }

  context 'with custom workers' do
    let(:params) { { 'workers' => 8 } }
    it { is_expected.to contain_file('/etc/nginx/nginx.conf').with_content(/worker_processes 8/) }
  end
end
```

For: TDD modules.

## puppet-lint

```bash
puppet-lint manifests/
```

Style checker.

## puppet parser validate

```bash
puppet parser validate site.pp
```

Syntax check.

## Forge

```bash
puppet module install puppetlabs/nginx
```

Public module repo.

## Best Practices

- Modules: single concern
- Sub-classes (install/config/service)
- Roles + profiles pattern
- Hiera for data
- eyaml for secrets
- rspec-puppet tests
- puppet-lint clean
- metadata.json updated

## Common Mistakes

- Data in manifests (use Hiera)
- Manifests in roles (use modules)
- exec abuse (find module / resource)
- No tests
- Forge modules without version pin

## Quick Refs

```bash
# Validate
puppet parser validate site.pp

# Lint
puppet-lint site.pp

# Test (rspec)
bundle exec rspec spec/

# Install module
puppet module install MODULE

# Hiera lookup test
puppet lookup nginx::workers --node web01
```

## Interview Prep

**Mid**: "Modules vs profiles."

**Senior**: "Hiera hierarchy."

**Staff**: "Puppet code architecture at scale."

## Next Topic

→ [T03 — Catalog Compilation](T03-Catalog-Compilation.md)
