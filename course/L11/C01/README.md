# L11/C01 — When Do You Need Config Management

## Topics

| Topic | Title | Duration |
|---|---|---|
| [T01](T01-Mutable-vs-Immutable.md) | Mutable vs Immutable Patterns | 0.5 hr |
| [T02](T02-Pull-vs-Push.md) | Pull vs Push Models | 0.5 hr |

## Where Config Management Still Lives

Config management was the dominant DevOps tool in 2010-2018. In 2025+ it's narrower but still matters:

- **Bootstrap servers** (cloud-init, Ansible)
- **Long-lived non-K8s servers** (DB hosts, build hosts, NFS, legacy apps)
- **Network gear** (Ansible has rich network modules)
- **Hybrid environments** (on-prem + cloud)
- **Air-gapped / regulated** (where containers aren't approved)
- **Bare-metal provisioning** (PXE + Ansible)

## Mutable Patterns (Traditional CM)

- Long-lived hosts
- Repeated agent runs converge state
- Drift inevitable; agent re-converges
- Examples: Puppet master/agent, Chef Infra

### Pros
- Mature, well-understood
- Fine-grained control
- Plays well with on-prem

### Cons
- State drift between converges
- Slow at scale (per-host runs)
- Hard to test
- Replaced by immutable infra in cloud

## Immutable Patterns (Modern)

- Bake config into images (AMI, container)
- Replace, don't patch
- Lifecycle: cattle, not pets

### When You Still Use Config Mgmt with Immutable
- During image build (Ansible inside Packer)
- For day-2 ops that don't justify a rebuild (cert rotation)

## Pull vs Push

### Pull Model (Puppet, Chef agents)
- Agent on each node
- Pulls catalog from master at interval (typically 30 min)
- Self-healing (if change drifts, next run reverts)

Pros:
- Scales (master serves many nodes)
- Self-healing
- Works behind NAT/firewall (outbound only)

Cons:
- Latency (changes wait until next pull)
- Agent maintenance
- Master is critical infra

### Push Model (Ansible, Salt push)
- Control node initiates connection
- SSH or message bus
- Immediate execution

Pros:
- No agent
- Immediate
- Simpler

Cons:
- Control node must reach all nodes
- Doesn't self-heal (drift accumulates)
- Slower at very large scale

## Today's Recommendation

| Use Case | Pick |
|---|---|
| Greenfield cloud-native | Containers + K8s, skip CM |
| Bootstrap cloud VMs | cloud-init or Ansible playbook |
| Bake images | Packer + Ansible |
| Network gear | Ansible |
| Hybrid + many legacy | Salt or Ansible |
| Massive fleet (10K+) | Salt or Chef Habitat |
| Regulated, mutable required | Puppet + Foreman |

## Interview Themes

- "When does config management still apply?"
- "Pull vs push — tradeoffs"
- "Immutable infra — what does it kill in CM?"
- "How do you handle drift?"
