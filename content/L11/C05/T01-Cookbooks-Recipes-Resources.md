# L11/C05/T01 — Cookbooks, Recipes, Resources

## Learning Objectives

- Structure Chef code
- Use resources

## Chef

Ruby-based config management:
- Cookbooks (modules)
- Recipes (manifests)
- Resources (idempotent units)
- Pull model (Chef Client polls Chef Server)

## Cookbook Structure

```
cookbooks/nginx/
  metadata.rb
  recipes/
    default.rb
    install.rb
    config.rb
  attributes/
    default.rb
  templates/
    default/
      nginx.conf.erb
  files/
    default/
  resources/         # custom resources
  libraries/         # helper Ruby
  spec/              # tests
  test/              # InSpec tests
  Berksfile
```

## Recipe

```ruby
# recipes/default.rb
package 'nginx' do
  action :install
end

service 'nginx' do
  action [:enable, :start]
end

template '/etc/nginx/nginx.conf' do
  source 'nginx.conf.erb'
  owner 'root'
  group 'root'
  mode '0644'
  notifies :restart, 'service[nginx]'
end
```

## Resources

Declarative units:
- `package`
- `service`
- `file` / `template`
- `directory`
- `user` / `group`
- `cron`
- `execute` (escape hatch)
- `bash` / `ruby_block`

## Resource Pattern

```ruby
resource_type 'name' do
  attribute1 'value1'
  attribute2 'value2'
  action :action_name
  notifies :other_action, 'other_resource[name]', :delayed
end
```

## Actions

```ruby
package 'nginx' do
  action :install    # default
end

package 'nginx' do
  action :upgrade
end

package 'nginx' do
  action :remove
end
```

Each resource: multiple actions.

## Notifications

```ruby
template '/etc/nginx/nginx.conf' do
  notifies :restart, 'service[nginx]', :delayed
end
```

Timing:
- `:delayed` (default; end of run)
- `:immediately` (now)

Like Ansible handlers but inline.

## Attributes

```ruby
# attributes/default.rb
default['nginx']['port'] = 80
default['nginx']['workers'] = 4
```

Used:
```ruby
template '/etc/nginx/nginx.conf' do
  source 'nginx.conf.erb'
  variables(
    port: node['nginx']['port'],
    workers: node['nginx']['workers']
  )
end
```

## Attribute Precedence

```
default → force_default → normal → override → force_override → automatic
```

Auto (Ohai-discovered): highest.

Override in:
- attributes file
- recipe
- environment
- role
- node-specific

## Templates (ERB)

```erb
<%# templates/default/nginx.conf.erb %>
worker_processes <%= @workers %>;

events {
  worker_connections 1024;
}

http {
  server {
    listen <%= @port %>;
  }
}
```

Variables passed via `variables` param.

## metadata.rb

```ruby
name 'nginx'
maintainer 'Me'
maintainer_email 'me@example.com'
license 'MIT'
description 'Installs/configures nginx'
version '1.0.0'

supports 'ubuntu'
supports 'centos'

depends 'firewall'
depends 'apt'
```

## Berksfile

```ruby
source 'https://supermarket.chef.io'

metadata
cookbook 'apt'
cookbook 'firewall'
```

```bash
berks install
berks upload
```

For: dependency management (like bundler).

## Run List

```ruby
# Node JSON
{
  "run_list": [
    "recipe[base]",
    "recipe[nginx]",
    "recipe[myapp]"
  ]
}
```

Order matters.

## Roles

```ruby
# roles/webserver.rb
name 'webserver'
description 'Web server'
run_list 'recipe[base]', 'recipe[nginx]'

default_attributes(
  'nginx' => {
    'workers' => 8
  }
)
```

Assign:
```ruby
run_list 'role[webserver]'
```

## Environments

```ruby
# environments/production.rb
name 'production'
default_attributes(
  'app' => {
    'version' => '1.2.3'
  }
)
```

Node:
```ruby
chef_environment 'production'
```

## Custom Resources

```ruby
# resources/vhost.rb
resource_name :vhost
provides :vhost

property :servername, String, name_property: true
property :port, Integer, default: 80

action :create do
  template "/etc/nginx/sites/#{new_resource.servername}" do
    source 'vhost.erb'
    variables(
      servername: new_resource.servername,
      port: new_resource.port
    )
    notifies :restart, 'service[nginx]'
  end
end

action :delete do
  file "/etc/nginx/sites/#{new_resource.servername}" do
    action :delete
  end
end
```

Use:
```ruby
vhost 'site1.com' do
  port 8080
end
```

## Data Bags

JSON store:
```bash
knife data bag create users
knife data bag from file users alice.json
```

```ruby
alice = data_bag_item('users', 'alice')
user alice['username'] do
  uid alice['uid']
end
```

For: shared data; encrypted bags for secrets.

## Encrypted Data Bag

```bash
knife data bag create secrets db --secret-file ~/.chef/encrypted_data_bag_secret
```

For: secrets.

## Chef Vault

Better than encrypted data bag:
- Per-node decryption
- Easier rotation

For: prod secrets.

## ohai

Facter equivalent. Auto-discovers:
- OS
- Network
- CPU
- Memory
- Cloud metadata

```ruby
node['platform_family']
node['cpu']['total']
```

## Run

```bash
# Apply local (chef-zero)
chef-client --local-mode --runlist 'recipe[nginx]'

# Apply from server
chef-client

# Dry run
chef-client --why-run
```

## Why-Run

Like `--check` in Ansible:
```bash
chef-client --why-run
```

Shows what would change.

## Chef Solo (Legacy)

No server; standalone:
```bash
chef-solo -c solo.rb -j node.json
```

For: simple setups.

## Cookbook Testing

### ChefSpec
```ruby
# spec/recipes/default_spec.rb
require 'chefspec'

describe 'nginx::default' do
  let(:chef_run) { ChefSpec::ServerRunner.new.converge(described_recipe) }

  it 'installs nginx' do
    expect(chef_run).to install_package('nginx')
  end

  it 'starts nginx service' do
    expect(chef_run).to enable_service('nginx')
    expect(chef_run).to start_service('nginx')
  end
end
```

### InSpec
```ruby
# test/integration/default/default_test.rb
describe package('nginx') do
  it { should be_installed }
end

describe service('nginx') do
  it { should be_enabled }
  it { should be_running }
end

describe port(80) do
  it { should be_listening }
end
```

For: post-converge verification.

### Test Kitchen
```yaml
# .kitchen.yml
driver:
  name: docker

provisioner:
  name: chef_zero

platforms:
  - name: ubuntu-22.04

suites:
  - name: default
    run_list:
      - recipe[nginx::default]
    verifier:
      inspec_tests:
        - test/integration/default
```

```bash
kitchen test
```

Spins up Docker; converges; verifies.

## Best Practices

- Cookbooks: single concern
- Custom resources (reusable)
- Test Kitchen + InSpec
- Berksfile for deps
- Encrypted secrets (Chef Vault)
- Pin versions in metadata
- Use roles + environments

## Common Mistakes

- execute for everything (escape hatch)
- No tests
- Secrets in code
- Unpinned dependencies
- Default attributes that don't work

## Quick Refs

```bash
# Generate
chef generate cookbook my-cookbook

# Berks
berks install / upload

# Knife
knife cookbook upload nginx
knife node show NODE
knife search node 'role:webserver'

# Run
chef-client / chef-client --why-run / chef-client --local-mode

# Test
kitchen test
chef exec rspec
```

## Interview Prep

**Junior**: "What's Chef."

**Mid**: "Cookbook structure."

**Senior**: "Custom resources."

**Staff**: "Chef at scale."

## Next Topic

→ [T02 — Chef Infra & Workstation](T02-Chef-Infra-Workstation.md)
