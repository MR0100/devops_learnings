# L30/C06/T01 — Public Repos & READMEs

## Learning Objectives

- Publish portfolio
- Strong READMEs

## Why the Repo (and Its README) Is the Real Deliverable

The capstones (C01–C05) only count as portfolio if someone can *find* and
*understand* them — and most reviewers spend 60 seconds on a repo before
deciding it's impressive or skippable. The README is doing that persuasion. A
hiring manager skims it to answer three questions fast: *what did you build, why
those choices, and what did you learn?* A repo with great code and a one-line
README reads as "didn't finish"; a repo with a strong README reads as "operates
at a senior level." The README is not documentation overhead — it *is* the
portfolio artifact.

### What a Strong README Signals (and the Trade-off)

- **Architecture diagram + outcome statement** — signals you think in systems and
  in results, not just code.
- **"Key Decisions / Trade-offs" section** — the single highest-signal part. Anyone
  can wire tools together; explaining *why this tool over that one, and what you
  gave up* is the senior tell. (This maps directly to the rationale sections you
  wrote into each capstone.)
- **"What I Learned" + "What I'd Do Next"** — shows reflection and growth, which
  is what distinguishes a portfolio from a tutorial follow-along.

The trade-off to manage is **scope vs. polish**: six pinned repos that are clean,
documented, and real beat twenty half-finished ones. Depth of a few signals more
than breadth of many.

## README Structure

```markdown
# Project Name

One-line description.

## What it does

2-3 paragraphs.

## Architecture

[Diagram]

## Tech Stack

- AWS EKS
- Terraform
- ArgoCD
- Prometheus
- ...

## Setup

```bash
# Clone
git clone ...

# Prerequisites
# - AWS account
# - kubectl
# - Terraform

# Run
terraform init
terraform apply
```

## Key Decisions

- Why GitOps
- Why this stack
- Trade-offs

## What I Learned

- Lessons
- Challenges
- Future work

## Demo

[Video / screenshots]
```

## Visuals

- Architecture diagram (Excalidraw / Mermaid)
- Screenshots (dashboards)
- Demo video

## Code Quality

- Clean
- Linted
- Tested
- Documented

## Commit Hygiene

- Clear messages
- Conventional Commits
- No "WIP" final commit

## License

```
LICENSE: MIT or Apache 2.0
```

## CI

Even portfolio:
- Tests
- Lint
- Demonstrate practice

## Best Practices

- Clear README
- Architecture diagram
- Tech stack listed
- Setup instructions
- Trade-offs discussed
- Demo
- Lessons learned

## Common Mistakes

- No README
- No diagram
- Stale
- Broken setup
- No tests

## Quick Refs

```
README must answer in 60s: what / why these choices / what you learned
Sections: Description → Architecture → Stack → Setup → Decisions → Lessons → Next
Highest-signal section: Key Decisions / Trade-offs
Visuals: diagram + screenshots   Demo: 5-min video
Pin your best 6; depth > breadth
```

## Interview Prep

**Junior**: "Why publish your projects on GitHub?" — So people can actually see
your work. A resume claims skills; a public repo with working code and a clear
README proves them, and recruiters and hiring managers screen candidates by
looking at their GitHub.

**Mid**: "What makes a portfolio README good?" — It answers, fast, what the
project does, how it's architected, how to run it, and what you learned — ideally
with an architecture diagram and a short demo. The most important part is a
'key decisions' section explaining *why* you chose each tool and what the
trade-offs were, because that's what shows depth beyond just wiring tools
together.

**Senior**: "Your repos have great code but get little attention. What would you
change?" — Almost always the framing, not the code. I'd lead each README with an
outcome statement and an architecture diagram so the value is obvious in the
first screen, add the decisions/trade-offs section that shows senior thinking,
and include a short Loom so a reviewer can see it working without standing it up.
Then I'd pin the best six and prune the rest — a focused set of polished,
real-scope projects reads far stronger than a long list of half-finished ones.
The work being good isn't enough if the first 60 seconds don't communicate that.

**Staff**: "How should a portfolio reflect staff-level scope rather than just
'I can build things'?" — At staff level the signal isn't 'I deployed a stack,'
it's 'I made good judgment calls under real constraints and can communicate
them.' So the repos should foreground decisions and trade-offs (why Spot here but
on-demand there, why this failover RTO and not a faster/costlier one), include
cost and operational reality (this runs at $X/month, here's how I'd scale it),
and connect to impact (what this would do for a team or an org). I'd also make the
portfolio *cohere* — projects that ladder toward 1–2 areas I want to be known
for, plus the writing and talks that reference them — so it reads as a point of
view, not a pile of demos. The README's 'what I'd do next' section is where you
show you see the system beyond what you built, which is the staff lens.

## Next Topic

→ [T02 — Blog Posts as Proof of Depth](T02-Blog-Posts.md)
