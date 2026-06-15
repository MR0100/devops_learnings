# L01/C03/T01 — Plan, Code, Build, Test

## Learning Objectives

- Identify the activities, artifacts, tools, and SLOs in the first half of the lifecycle
- Recognize where each phase commonly fails and what the failure looks like downstream
- Connect each phase to a DORA metric and reason about which phase to invest in
- Apply the test pyramid and shift-left principle to a real pipeline

## The Left Half of the Loop

Plan → Code → Build → Test is the "inner loop plus first half of the outer loop." The boundary that matters: **Plan and Code are the inner loop** (where an engineer iterates locally, hundreds of times a day), while **Build and Test are the first machine-gated checks** (CI, run on every push). The economics differ — inner-loop friction is paid per keystroke; CI friction is paid per push. Optimize them differently.

A useful framing: each phase has an *artifact it produces* and a *gate it must pass*. If you can't name the artifact, the phase isn't real; if you can't name the gate, the phase isn't trustworthy.

## Plan

**Activities**: requirements, design, architecture decisions, sprint planning, backlog grooming, threat modeling
**Artifacts**: PRDs, ADRs (Architecture Decision Records), tickets, design docs, RFCs
**Tools**: Jira, Linear, Asana, Notion, Confluence; RFC-in-a-repo workflows
**SLOs**: lead time of a ticket from creation to "in progress"; % of work that is planned vs. interrupt-driven
**Failure modes**: ambiguous requirements → rework; design done by 1 architect → missed edge cases; no written decisions → the same debate re-litigated every quarter

Plan is the cheapest place to catch a defect and the most expensive place to skip. A bug caught in Plan costs a sentence in a doc; the same bug caught in production costs an incident. This is the steepest part of the cost-of-change curve.

## Code

**Activities**: implementation, code review, pairing, local testing
**Artifacts**: source code, unit tests, commits, PRs, branches
**Tools**: VS Code, JetBrains, vim, Cursor; GitHub/GitLab/Bitbucket; pre-commit hooks
**SLOs**: PR review SLA (e.g., < 4 hours business time); PR size (target: < 400 lines changed); test coverage gate
**Failure modes**: PR backlog → context loss and merge conflicts; no review standards → inconsistency; giant PRs → rubber-stamp reviews that catch nothing

The single highest-leverage lever in Code is **PR size**. Review quality collapses past ~400 lines — reviewers skim, defects slip, and the LGTM is a formality. Small PRs review fast, merge fast, and keep the trunk green.

```
   Inner loop (Code phase, repeated ~hundreds/day):

   edit → save → typecheck → unit test → repeat
    │       │        │           │
    │       │        │           └─ < 10 sec
    │       │        └─ < 1 sec (LSP)
    │       └─ instant
    └─ this loop's latency is the engineer's productivity ceiling
```

## Build

**Activities**: compilation, dependency resolution, artifact creation, image building, SBOM generation
**Artifacts**: binaries, container images, packages, lockfiles, SBOMs
**Tools**: Maven, Gradle, npm/pnpm, Cargo, Bazel, Buck2; Docker, BuildKit, ko, Jib
**SLOs**: build time (target: < 10 minutes), build reliability (target: > 99%), cache hit rate
**Failure modes**: flaky builds → engineers stop trusting CI; build time > 30 min → context switching dominates; non-reproducible builds → "works in CI, not in prod"

Build time is a throughput governor. If a build takes 30 minutes, an engineer rebases-and-waits, switches context, and loses the thread — so effective cycles per day collapse. The fixes, in rough order of leverage: **dependency caching → build parallelism → incremental/remote build graphs (Bazel, Turborepo, Nx) → layer caching for images.**

Aim for **reproducible builds**: same source + same inputs → byte-identical artifact. Pin dependency versions (lockfiles), pin base images by digest (not `:latest`), and avoid build-time network calls. Reproducibility is what makes "the image we tested is the image we ship" a true statement.

## Test

**Activities**: unit, integration, contract, e2e, performance, security (SAST/SCA) tests
**Artifacts**: test reports, coverage reports, SBOMs, vulnerability findings
**Tools**: pytest, JUnit, Go test, Vitest; Cypress, Playwright; Pact (contract); k6, Gatling; Trivy, Snyk, Semgrep
**SLOs**: test runtime (target: < 10 min on PR), flake rate (< 1%), coverage gate, mean time to green
**Failure modes**: flaky tests → ignored and then deleted; long runtime → tests skipped or run nightly only; only unit tests → integration surprises in prod

The cardinal sin of Test is **the flaky test**. One flaky test that fails 5% of the time, run on every PR, fails *somebody's* build constantly — and the team learns to click "re-run" without reading. Once "re-run on red" is reflex, the test suite is decoration. Quarantine flaky tests immediately; a quarantined test is honest, a flaky one in the gate is a lie.

**Shift-left** means moving each check as early (left) in the lifecycle as it can run: typecheck in the editor, lint pre-commit, unit tests on push, SAST in CI, contract tests before integration. Every check that moves left gives faster, cheaper feedback.

## Common Pattern: The Test Pyramid

```
              ╱╲
             ╱E2╲          (few — slow, brittle, expensive; full-stack confidence)
            ╱────╲
           ╱ Integ╲        (some — real dependencies, focused)
          ╱────────╲
         ╱ Contract ╲      (cheap cross-service guarantees, no full env)
        ╱────────────╲
       ╱     Unit     ╲    (many — fast, cheap, isolated)
      ╱────────────────╲
```

The pyramid's logic: push test volume toward the cheap, fast bottom. The **inverted pyramid (ice-cream cone)** — mostly slow e2e tests, few unit tests — is the classic anti-pattern: a 90-minute suite that's flaky and tells you *that* something broke but never *where*. Modern adjustment: add **contract tests** (Pact) between unit and integration to catch cross-service breaks without standing up a full environment.

## How These Phases Connect to DORA

| Phase | DORA Influence | Why |
|---|---|---|
| Plan | Lead Time | Time from idea to "in progress" is the front of lead time |
| Code | Lead Time | PR review delays and rework dominate elapsed time |
| Build | Deploy Frequency | Slow/flaky builds cap how often you *can* ship |
| Test | Change Failure Rate | Test gaps are exactly the defects that escape to prod |

The diagnostic value: if **CFR is high**, look at Test (and the canary in T02). If **Deploy Frequency is low** despite small batches, look at Build time. If **Lead Time is high** but builds are fast, look at PR review SLA in Code.

## Common Mistakes

- **Treating Plan as overhead** — skipping ADRs/RFCs to "move fast," then re-litigating the same architecture decision every quarter with no record of why
- **Reviewing 1,000-line PRs** — reviewers can't hold it in their head, so they approve on trust and the gate catches nothing
- **Tolerating flaky tests** — leaving them in the gate trains the whole team to ignore red, which eventually hides real failures
- **Building non-reproducibly** — `:latest` base images and unpinned deps mean the artifact you tested isn't the artifact you ship
- **Coverage as a vanity metric** — gating on 80% line coverage rewards tests that execute code without asserting anything
- **An ice-cream-cone test suite** — investing in slow e2e tests while neglecting fast unit tests, ending with a suite too slow to run on every PR

## Best Practices

- **Write the decision down** — an ADR per significant choice; cheap to write, priceless when someone asks "why is it like this?" in two years
- **Keep PRs under ~400 lines** — the single biggest lever on review quality and merge speed
- **Cache aggressively, pin everything** — dependency cache, layer cache, remote build cache; lockfiles and digest-pinned base images for reproducibility
- **Quarantine flaky tests on detection** — a quarantined test is honest; a flaky one in the gate erodes trust in the whole suite
- **Shift checks left** — typecheck in the editor, lint pre-commit, SAST/SCA in CI; each step earlier is cheaper and faster
- **Gate on the metrics that matter** — green tests, no new high-severity vulns, no coverage *regression* — not an arbitrary coverage floor

## Quick Refs

```bash
# Find slow tests (pytest) to attack the long pole of test runtime
pytest --durations=20

# Detect flaky tests by running the suite N times
for i in $(seq 1 20); do pytest -q tests/ || echo "FAILED on run $i"; done

# Reproducible container build: pin base by digest, scan, generate SBOM
docker build -t app:$(git rev-parse --short HEAD) .
trivy image --severity HIGH,CRITICAL app:$(git rev-parse --short HEAD)
syft app:$(git rev-parse --short HEAD) -o spdx-json > sbom.json

# Bazel: only rebuild/test what changed (incremental build graph)
bazel test //... --build_tests_only
```

Mnemonic: **Plan catches bugs in a sentence; Test catches them in a build; production catches them in an incident.** Every phase that catches earlier is an order of magnitude cheaper.

## Interview Prep

**Junior**: "What are the phases in the first half of the DevOps lifecycle?"
- Plan, Code, Build, Test — turning an idea into requirements, then code, then a tested, shippable artifact, with each phase producing an artifact and passing a gate.

**Mid**: "Walk me through the first half of the DevOps lifecycle and the artifact each phase produces."
- Plan produces tickets/ADRs, Code produces source and PRs, Build produces a versioned artifact (image/binary + SBOM), and Test produces reports that gate the artifact — and I'd connect each to its DORA metric (Plan/Code → Lead Time, Build → Deploy Frequency, Test → Change Failure Rate).

**Senior**: "Build times are 45 minutes; we want them under 10. Where do you look first?"
- Profile the build to find the long pole, then attack in order: dependency and layer caching, build parallelism, a remote/incremental build graph (Bazel/Turborepo) so only changed targets rebuild, test sharding, and pulling slow integration tests out of the PR build onto a post-merge stage.

**Staff**: "Design the planning and code phases for an org of 200 engineers shipping to a regulated industry."
- Standardize decision records (ADR/RFC) and require threat modeling in Plan for auditability; enforce small PRs with mandatory review, signed commits, and SAST/SCA gates in Code; wire compliance evidence (who approved, what scanned) into the pipeline so the audit trail is a byproduct of the normal flow rather than a separate manual burden.

## Next Topic

→ [T02 — Release, Deploy, Operate, Monitor](T02-Release-Deploy-Operate-Monitor.md)
