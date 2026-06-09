# L01/C04/T02 — SRE vs DevOps Engineer

## Learning Objectives

- Distinguish SRE and DevOps Engineer roles on technical and cultural axes
- Recognize which companies use which model
- Choose between roles based on your interests

## Origin & Identity

- **SRE**: born at Google in 2003 (Ben Treynor). The discipline of operating production using software engineering practices.
- **DevOps Engineer**: emerged from industry (2010+) as a hybrid role with broader scope.

## The Bar to Hire

- **SRE** at Google requires the same coding bar as SWE. Concretely: data structures, algorithms, system design at the same depth.
- **DevOps Engineer** often weights infrastructure/tooling skills over algorithmic depth.

## What They Optimize For

| Dimension | SRE | DevOps Engineer |
|---|---|---|
| Reliability of services | Primary objective | One of many |
| Coding contributions | High (production code, controllers) | Moderate (tools, IaC) |
| On-call | Mandatory rotation with strict policies | Common but varied |
| SLI/SLO ownership | Explicit | Sometimes |
| Error budgets | Used to gate deploys | Rare |
| Tooling building | Yes, with software rigor | Yes, broader |
| Capacity planning | First-class | Common |

## A Concrete Comparison

| Task | SRE | DevOps Engineer |
|---|---|---|
| Write a Kubernetes operator | Yes, in Go, with tests | Maybe, often configures existing operators |
| Define an SLO and burn-rate alert | Yes | Sometimes |
| Tune a Postgres query plan | Often, especially if owning data infra | Sometimes |
| Build a Terraform module library | Yes | Yes |
| Run a postmortem | Lead | Often participates |
| Refactor production code for reliability | Yes | Less commonly |

## When Companies Pick One Over the Other

- **Google, Meta, Microsoft**: have SRE and Production Engineer titles
- **Amazon**: Sysops / TPM / SDE (no formal SRE org, embedded)
- **Netflix**: Senior SWEs do reliability; few formal SREs
- **Stripe, Shopify**: Reliability Engineers
- **Most startups**: DevOps Engineers, often the only ops staff

## Which Should You Choose

| You Are... | Probably Pick |
|---|---|
| Strong coder, love systems, want to write production code | SRE |
| Broad infrastructure interest, less coding-focused | DevOps Engineer |
| Want depth in a specific domain (networking, databases) | SRE or specialist |
| Want to influence many teams' practices | Platform Engineer or DevOps |
| Want clear OKRs tied to reliability | SRE |

## Interview Prep

**Mid**: "What's the difference between SRE and DevOps Engineer?"

**Senior**: "Why does Google have SRE and Amazon doesn't?"

**Staff**: "Argue for or against creating a separate SRE org in a company that currently has only DevOps engineers."

## Next Topic

→ [T03 — Platform Engineer & Internal Developer Platforms](T03-Platform-Engineer.md)
