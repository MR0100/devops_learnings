# L01/C01/T02 — History and Evolution

## Learning Objectives

- Place DevOps in a timeline from the 1970s software crisis to modern Platform Engineering
- Identify the technical and cultural forces that produced each shift, not just the dates
- Recognize why each prior movement was necessary but insufficient for what came next
- Use the history to reason about where the industry is heading (and to answer "why did X emerge?" interview questions)

## Prerequisites

A working definition of DevOps as a culture (L01/C01/T01). This topic gives that definition its historical spine.

## Timeline

```
1968  NATO Software Engineering Conference (birth of "software crisis")
1970  Royce describes the waterfall-like model (later misread as prescriptive)
1979  Bell Labs / ITIL roots — operations formalized as a discipline
1991  Linus Torvalds releases Linux 0.01 — cheap, hackable server OS
1995  Amazon, Yahoo, eBay launch — internet operations become a full-time job
1999  Extreme Programming (Kent Beck) — CI, small releases, test-first
2001  Agile Manifesto (Snowbird, Utah)
2003  Google's Ben Treynor founds Site Reliability Engineering
2006  Werner Vogels: "You build it, you run it" (Amazon)
2007  Infrastructure as Code emerges (Puppet 2005, Chef 2009)
2008  Andrew Shafer & Patrick Debois — "Agile Infrastructure" talk (Agile Toronto)
2009  Allspaw & Hammond — "10+ Deploys per Day" (Velocity)
2009  Patrick Debois — first DevOpsDays (Ghent, Belgium); the word "DevOps" is coined
2010  Continuous Delivery (Humble & Farley) published
2013  Docker open-sourced — reproducible, portable runtime
2014  Kubernetes open-sourced by Google (descended from Borg)
2014  The Phoenix Project (Kim, Behr, Spafford) popularizes DevOps narratively
2016  Google's SRE Book published — SRE goes public
2017  GitOps coined by Weaveworks
2018  Accelerate (Forsgren, Humble, Kim) — DORA research formalized
2019  Team Topologies (Skelton & Pais) — modern team-interaction patterns
2022  "Platform Engineering" enters mainstream vocabulary
2023+ Internal Developer Platforms (IDPs) become standard at scale
```

## The Forces Behind Each Shift

History here is not a list of tools — it's a chain of **bottlenecks**. Each movement dissolved the bottleneck the previous one exposed.

### Waterfall → Agile (2001)

- **Problem**: 18-month release cycles meant requirements changed before software shipped; integration was a "big bang" at the end
- **Insight**: Embrace change instead of fighting it; ship small, get feedback, iterate
- **Result**: Iterative development and short feedback loops — but ops still operated on quarterly release windows, so the new bottleneck moved downstream to deployment

### Agile → DevOps (2008–2009)

- **Problem**: Agile teams could *code* fast but couldn't *deploy* fast; the dev→ops handoff was a literal wall (different teams, different incentives, different tickets)
- **Trigger**: Debois, frustrated that "agile sysadmins" had no community, plus Allspaw/Hammond proving 10+ deploys/day was possible at Flickr with dev and ops cooperating
- **Insight**: The handoff *was* the bottleneck; shared ownership and automation dissolve it
- **Result**: CI → CD, Infrastructure as Code, shared on-call, "you build it, you run it"

### DevOps → SRE (born 2003, popularized 2016)

- **Problem**: Google had thousands of engineers and thousands of services. "Everyone owns ops" doesn't scale to that without rigor; you need a *measurable*, engineering-grade approach
- **Insight**: Treat operations as a software engineering problem — automate toil away, set numeric reliability targets, and budget for failure
- **Result**: SRE — error budgets, SLOs, toil caps (≤50%), and operations staffed by people who code at a software-engineer bar

### DevOps + SRE → Platform Engineering (2019–2022+)

- **Problem**: At 50+ teams, every team rebuilds the same observability, secrets, and deployment plumbing — slightly differently each time. Cognitive load on product engineers explodes
- **Insight**: Cognitive load is the real bottleneck; product teams need *paved roads*, not 200 raw primitives
- **Result**: Platform teams build an Internal Developer Platform (a *product*) that abstracts complexity, so the operational knowledge is paid for once and amortized across teams

## Why Each Was Necessary but Insufficient

Each shift was **necessary but insufficient** for what came next — this framing is the key to the "evolution" interview question:

- **Agile** without DevOps → fast dev, slow deploys (code piles up in a release queue)
- **DevOps** without SRE → fast deploys without reliability discipline (you ship breakage faster)
- **SRE** without Platform Engineering → reliable services that cost too much to *build* and re-build per team
- **Platform Engineering** without the prior three → a platform with no CD, no SLOs, and no culture to adopt it

```
Agile ──► DevOps ──► SRE ──► Platform Engineering
 fast      fast       reliable   reusable, low-
 dev       deploys    at scale   cognitive-load
 loop                            paved roads
   each layer ADDS to the last; none replaces it
```

A common misread is to see these as a "succession" where the newest kills the oldest. They compose. A 2024 elite org is Agile *and* DevOps *and* SRE *and* Platform — at different layers of the same problem.

## Real-World Examples by Era

- **Pre-DevOps (2005)**: A typical bank deploys 4 times a year; each deploy is an all-hands weekend with a rollback plan printed on paper
- **Early DevOps (2010)**: Flickr/Etsy deploy 10–50 times a day; dev and ops share dashboards and a deploy button, but are still distinct teams
- **SRE Era (2015)**: Google deploys thousands of times a day, gated by error budgets — when a service burns its budget, feature work stops until reliability is restored
- **Platform Era (2024)**: Spotify, Netflix, Stripe ship hundreds of times a day; a new service goes from `git init` to production in hours via a self-service golden path

## Common Misreadings of the History

- **"Waterfall was always bad"** — Royce's 1970 paper actually *argued against* naive single-pass waterfall and recommended feedback loops; the rigid version was a misinterpretation
- **"DevOps replaced Agile"** — DevOps extends Agile past "code committed" to "code observed in production"
- **"SRE is just rebranded ops"** — SRE inverts the relationship: ops work is a software problem with budgets and SLOs, not a queue of tickets
- **"Platform Engineering is the death of DevOps"** — it's DevOps principles delivered *as a product* by a dedicated team; the principles didn't change, the delivery model did

## Common Mistakes

- **Memorizing dates without forces** — the interview value is in *why* each shift happened, not the year
- **Treating the timeline as linear succession** — these layers coexist; an elite org runs all four simultaneously
- **Skipping the bottleneck framing** — every movement removed one constraint and exposed the next; lose that thread and the history is just trivia
- **Crediting tools, not culture** — Docker and Kubernetes accelerated DevOps but didn't cause it; the cultural shift (shared ownership) predates them
- **Assuming bigger = more advanced** — a 10-person startup may be "post-DevOps" in practice while a 10,000-person enterprise is still pre-DevOps

## Best Practices

- **Anchor every movement to its bottleneck** — "Agile fixed slow dev; DevOps fixed slow deploys; SRE fixed ops-at-scale; Platform fixed cognitive load"
- **Read the source narratives** — *The Phoenix Project* for the cultural story, *Accelerate* for the empirical backing
- **Use history to justify adoption** — when proposing Platform Engineering, point to the duplication pain that historically triggered it (50+ teams)
- **Map your own org onto the timeline** — knowing which era you're actually in tells you which problem to solve next
- **Separate practice from packaging** — SRE and Platform Engineering are *packagings* of DevOps principles; adopt the principle even if you skip the packaging

## Quick Refs

```
Mnemonic — the four bottlenecks, in order:
  Agile     → slow, inflexible DEVELOPMENT
  DevOps    → the DEV↔OPS WALL (handoff)
  SRE       → operating reliably AT SCALE
  Platform  → COGNITIVE LOAD on product teams

Three names to know:
  Patrick Debois  — coined "DevOps", founded DevOpsDays (2009)
  Ben Treynor     — founded SRE at Google (2003)
  Skelton & Pais  — Team Topologies / Platform Engineering (2019)
```

## Reading Recommendations

- *The Phoenix Project* — narrative of pre-DevOps to post-DevOps transformation
- *The Unicorn Project* — same world, developer's perspective
- *Site Reliability Engineering* (Google) — Chapter 1 ("Introduction")
- *Accelerate* (Forsgren, Humble, Kim) — the DORA research, the empirical case
- *Team Topologies* (Skelton & Pais) — Chapter 1, and the platform-team chapters
- Patrick Debois, "DevOps Areas" article series

## Interview Prep

**Junior**: "What does the word 'DevOps' come from?"
- It was coined by Patrick Debois in 2009 around the first DevOpsDays in Ghent, growing out of "agile infrastructure" — the idea that the dev and ops split was an artificial wall.

**Mid**: "Why did SRE emerge separately from DevOps?"
- Google needed to operate thousands of services with thousands of engineers, which demanded a measurable, engineering-grade approach — error budgets, SLOs, and toil caps — that goes beyond DevOps's cultural principles.

**Senior**: "Walk me through the evolution from Agile to Platform Engineering and the bottleneck each shift addressed."
- Agile removed slow, inflexible development; DevOps removed the dev/ops handoff wall; SRE removed the inability to operate reliably at scale; Platform Engineering removed the cognitive load of every team rebuilding the same infra — each necessary but insufficient for the next.

**Staff**: "Pick a 2024 organizational challenge — say cognitive load — and explain how the historical sequence informs your solution."
- Cognitive load is the modern bottleneck the same way the dev/ops wall was in 2009; the historical pattern says you solve it by productizing the operational knowledge (an IDP with golden paths) rather than mandating yet another team, exactly as Platform Engineering emerged to amortize the duplicated work SRE made visible at scale.

## Next Topic

→ [T03 — DevOps vs Traditional IT Operations](T03-DevOps-vs-Traditional-IT.md)
