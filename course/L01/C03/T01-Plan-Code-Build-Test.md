# L01/C03/T01 — Plan, Code, Build, Test

## Learning Objectives

- Identify the activities, artifacts, and tools in the first half of the lifecycle
- Recognize where each phase commonly fails
- Connect each phase to a DORA metric

## Plan

**Activities**: requirements, design, architecture decisions, sprint planning, backlog grooming
**Artifacts**: PRDs, ADRs (Architecture Decision Records), tickets, design docs
**Tools**: Jira, Linear, Asana, Notion, Confluence
**SLOs**: lead time of a ticket from creation to "in progress"
**Failure modes**: ambiguous requirements → rework; design done by 1 architect → miss edge cases

## Code

**Activities**: implementation, code review, pairing
**Artifacts**: source code, unit tests, commits, PRs
**Tools**: VS Code, JetBrains, vim, Cursor; GitHub/GitLab/Bitbucket
**SLOs**: PR review SLA (e.g., < 4 hours business time); test coverage gate
**Failure modes**: PR backlog → context loss; lack of code review standards → inconsistency

## Build

**Activities**: compilation, dependency resolution, artifact creation
**Artifacts**: binaries, container images, packages
**Tools**: Maven, Gradle, npm, Cargo, Bazel, Buck2; Docker, Buildkit
**SLOs**: build time (target: < 10 minutes), build reliability (target: > 99%)
**Failure modes**: flaky builds → engineers stop trusting CI; build time > 30 min → context switching cost dominates

## Test

**Activities**: unit, integration, contract, e2e, performance, security tests
**Artifacts**: test reports, coverage reports, SBOMs
**Tools**: pytest, JUnit, Go test, Cypress, Playwright, k6, Trivy
**SLOs**: test runtime, flake rate (< 1%), coverage gate
**Failure modes**: flaky tests → ignored; long test runtime → tests skipped; only unit tests → prod surprises

## Common Pattern: The Test Pyramid

```
              ╱╲
             ╱E2╲          (few — slow, expensive)
            ╱────╲
           ╱ Integ╲        (some — focused)
          ╱────────╲
         ╱   Unit   ╲      (many — fast, cheap)
        ╱────────────╲
```

Modern adjustment: add **contract tests** between unit and integration.

## How These Phases Connect to DORA

| Phase | DORA Influence |
|---|---|
| Plan | Lead Time (from ticket to commit) |
| Code | Lead Time (PR review delays) |
| Build | Deploy Frequency (slow builds cap throughput) |
| Test | Change Failure Rate (gaps let defects escape) |

## Interview Prep

**Mid**: "Walk me through the first half of the DevOps lifecycle."

**Senior**: "Build times are 45 minutes; we want them under 10. Where do you look first?"
- Dependency caching, parallelism, monorepo build graphs (Bazel), test sharding, removing slow integration tests from PR build.

**Staff**: "Design the planning and code phases for an org of 200 engineers shipping to a regulated industry."

## Next Topic

→ [T02 — Release, Deploy, Operate, Monitor](T02-Release-Deploy-Operate-Monitor.md)
