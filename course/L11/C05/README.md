# L11/C05 — Chef

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Cookbooks.md) | Cookbooks, Recipes, Resources | 1 hr |
| [T02](T02-Chef-Infra-Workstation.md) | Chef Infra & Workstation | 0.5 hr |

## Architecture

```
[Workstation] —writes & tests cookbooks— uploads to → [Chef Server]
                                                          │
                                                          ▼
                                              Nodes pull cookbooks
                                              (chef-client every ~30 min)
```

- **Chef Workstation**: developer machine with `chef`, `knife`, `Test Kitchen`
- **Chef Server**: cookbook repository
- **Chef Client (Infra Client)**: agent on nodes (or `chef-zero` for serverless mode)

## Cookbooks

A cookbook is a unit of distribution.

```
cookbooks/nginx/
├── metadata.rb           # name, version, dependencies
├── recipes/
│   ├── default.rb        # the "default" recipe
│   └── package.rb        # additional recipes
├── attributes/
│   └── default.rb        # default attributes
├── templates/
│   └── default/
│       └── nginx.conf.erb
├── files/
│   └── default/
├── libraries/            # helper Ruby code
├── resources/            # custom resources
├── providers/
└── test/integration/     # InSpec tests
```

## Recipes

Ruby DSL declaring resources.

```ruby
# cookbooks/nginx/recipes/default.rb

package 'nginx' do
  action :install
end

template '/etc/nginx/nginx.conf' do
  source 'nginx.conf.erb'
  owner 'root'
  group 'root'
  mode '0644'
  variables(workers: node['nginx']['workers'])
  notifies :restart, 'service[nginx]', :delayed
end

service 'nginx' do
  action [:enable, :start]
end
```

### Common Resources
- `package` (install/remove)
- `service` (start/stop/enable)
- `template` (ERB-rendered file)
- `cookbook_file` (static file)
- `file` (manage file content)
- `directory`
- `user` / `group`
- `cron`
- `execute` / `bash` (script execution; use sparingly)
- `mount`
- `gem_package`, `pip_package`, `npm_package`

## Attributes

Default values that can be overridden:

```ruby
# cookbooks/nginx/attributes/default.rb
default['nginx']['workers'] = 4
default['nginx']['user'] = 'www-data'
```

Override hierarchy: defaults → role/environment → node-specific → force.

## Roles & Environments

### Roles
```ruby
# roles/web.rb
name 'web'
description 'Web servers'
run_list 'recipe[nginx]', 'recipe[nodejs]'
default_attributes 'nginx' => {'workers' => 8}
```

### Environments
```ruby
name 'production'
default_attributes 'env' => 'production'
override_attributes 'app' => {'replicas' => 16}
```

## Data Bags

Encrypted JSON for secrets and shared data:
```bash
knife data bag create users
knife data bag from file users alice.json
```

```ruby
users = data_bag('users')
users.each do |user_id|
  user_data = data_bag_item('users', user_id)
  user user_data['name'] do
    uid user_data['uid']
  end
end
```

## Chef Workstation

```bash
chef generate cookbook nginx
chef exec rspec                    # unit tests
chef exec kitchen test             # Test Kitchen integration tests
knife cookbook upload nginx
knife node run_list add web1 'recipe[nginx]'
knife bootstrap host -N web1 -x ubuntu --sudo
```

## InSpec

Compliance + test framework. Used with Test Kitchen.

```ruby
# test/integration/default/nginx_test.rb
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

```bash
chef exec inspec exec test/integration/default/nginx_test.rb
```

## Chef vs Puppet

| | Chef | Puppet |
|---|---|---|
| DSL | Ruby (Ruby-backed) | Puppet (custom) |
| Model | Imperative-ish (recipes order matter) | Declarative (DAG resolution) |
| Approach | "Cookbook" mental model | "Catalog" mental model |
| Learning | Ruby experience helps | Puppet-specific |
| Pull model | Yes (chef-client) | Yes (puppet agent) |

## State Today

Both Chef and Puppet have declined as cloud-native (containers, K8s, IaC) ate their market. Still used in:
- Long-running fleets
- Regulated industries
- Legacy investments

Most teams choose Ansible for new CM work.

## Interview Themes

- "Chef vs Puppet"
- "Walk me through a cookbook"
- "InSpec — what does it test?"
- "When Chef over Ansible?"
- "Data bag — what is it?"
