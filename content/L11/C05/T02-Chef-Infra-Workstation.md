# L11/C05/T02 — Chef Infra & Workstation

## Learning Objectives

- Setup Chef workstation
- Use Chef Infra Server

## Chef Architecture

```
Workstation (developer)
   ↓ knife uploads cookbooks
Chef Infra Server
   ↓ Chef Client polls
Nodes (managed servers)
```

## Workstation

Developer machine. Has:
- Chef Workstation (ChefDK successor)
- Tools: knife, chef, kitchen, chef-cli

```bash
# Install
curl -L https://omnitruck.chef.io/install.sh | sudo bash -s -- -P chef-workstation
```

## ~/.chef Directory

```
~/.chef/
  config.rb         # connection to Chef Server
  USER.pem          # user key
  ORG-validator.pem # validator key (legacy)
```

## config.rb

```ruby
current_dir = File.dirname(__FILE__)
log_level                :info
log_location             STDOUT
node_name                'alice'
client_key               "#{current_dir}/alice.pem"
chef_server_url          'https://chef.example.com/organizations/myorg'
cookbook_path            ["#{current_dir}/../cookbooks"]
```

## knife

CLI for Chef Server:
```bash
# Upload cookbook
knife cookbook upload nginx

# List nodes
knife node list

# Show node
knife node show web01

# Search
knife search node 'platform_family:debian'

# Bootstrap (install agent on node)
knife bootstrap 10.0.0.1 -N web01 -x ubuntu --sudo --run-list 'role[webserver]'

# SSH to results
knife ssh 'role:webserver' 'uptime' --ssh-user ubuntu
```

## Bootstrap

Install Chef Client on new node:
```bash
knife bootstrap NODE_IP -N hostname -x SSH_USER --sudo --run-list 'recipe[base]'
```

Chef Client installed; first run executed.

For: onboarding.

## Chef Infra Server

Central repo:
- Cookbooks
- Roles
- Environments
- Data bags
- Node objects
- ACLs

Self-hosted or Chef-managed.

Install:
```bash
# Reference
chef-server-ctl install
chef-server-ctl reconfigure
chef-server-ctl user-create / org-create
```

## Hosted Chef (Deprecated)

Chef SaaS shut down. Self-host or Chef Automate.

## Node Object

```bash
knife node show web01
```

JSON: facts, run_list, attributes.

## Search

```bash
knife search node 'platform:ubuntu AND role:webserver'
knife search node 'fqdn:web*' -a ipaddress
```

For: discover infrastructure.

## Chef Automate

UI + analytics layer:
- Compliance (InSpec)
- Visibility (run reports)
- Workflow

For: enterprise.

## Chef Client

Daemon on each node:
- `chef-client` interval (default 30 min)
- Pulls run list
- Compiles + converges
- Reports to Chef Server / Automate

## Service vs Cron

```bash
# systemd
systemctl enable chef-client.service

# Or cron
*/30 * * * * /usr/bin/chef-client
```

## Splay

Random delay before run:
```ruby
splay 1800  # up to 30 min jitter
```

For: avoid thundering herd.

## Reporting

Each run sends report:
- Resources updated
- Failures
- Duration

To Chef Automate (or just stdout in standalone).

## Audit Mode

```ruby
chef-client --audit-only
```

Runs InSpec; doesn't change.

For: compliance.

## Chef Vault Setup

```bash
# Create vault item with secret
knife vault create secrets db --json db-secrets.json -A 'admin1,admin2' -S 'role:webserver'

# Update access
knife vault refresh secrets db

# View
knife vault show secrets db
```

For: per-node decryption.

## Knife Plugins

- knife-ec2 (AWS bootstrap)
- knife-gcp
- knife-azure
- knife-vsphere

For: cloud-aware ops.

## Test Kitchen Drivers

- docker (fast, common)
- vagrant
- ec2
- gce

```yaml
driver:
  name: docker
```

## Cookbook Upload

```bash
# Without deps
knife cookbook upload nginx

# With Berks
berks install
berks upload
```

## Cookbook Versions

```ruby
# metadata.rb
version '1.2.3'
```

Multiple versions live on server; node pinned to specific.

For: rolling updates.

## Constraints

```ruby
# Environment
cookbook 'nginx', '~> 1.2.0'
```

For: control which version per env.

## Chef Habitat

Application packaging (separate tool):
- Build artifacts
- Configurable runtime
- Lifecycle management

Less common.

## Comparison to Puppet

| | Chef | Puppet |
|---|---|---|
| Language | Ruby DSL | Puppet DSL |
| Model | Pull | Pull |
| Server | Chef Infra | Puppet Server |
| Reporting | Chef Automate | PuppetDB / PE |
| Bootstrap | knife bootstrap | puppet agent setup |
| Testing | Test Kitchen + InSpec | rspec-puppet |

## Decline

Both Puppet and Chef declining. Reasons:
- Containers
- Immutable infrastructure
- Ansible simpler
- Pulumi / Terraform for IaC

But: still widely deployed; long tail.

## Best Practices

- Workstation cleanly configured
- Knife in CI (not just laptops)
- Bootstrap via cloud-init or AMI
- Cookbook versions pinned
- Test Kitchen + InSpec
- Chef Automate for reporting

## Common Mistakes

- knife from random laptops
- Cookbooks unpinned
- Direct edits to server (not via Berks)
- No tests
- Cleartext secrets

## Migration Out

Many orgs migrating Chef → Ansible / immutable / K8s.

Process:
1. Audit current cookbooks
2. New systems: don't add Chef
3. Containerize where possible
4. Replace per app

## Quick Refs

```bash
# Workstation
knife configure

# Bootstrap
knife bootstrap IP -N NAME -x USER --sudo --run-list 'role[X]'

# Search
knife search node 'QUERY'

# Cookbook
knife cookbook upload COOKBOOK
berks upload

# Node
knife node show NAME
knife node run_list add NAME 'recipe[X]'

# Run on node
chef-client
chef-client --why-run
```

## Interview Prep

**Mid**: "Chef architecture."

**Senior**: "Migrate Chef → alternative."

**Staff**: "Config management strategy."

## Next Topic

→ Move to [L11/C06 — SaltStack](../C06/README.md)
