# L01/C01/T02 — History and Evolution

## Learning Objectives

- Place DevOps in a timeline from 1970s software crisis to modern Platform Engineering
- Identify the technical and cultural forces that produced each shift
- Recognize why each prior movement was necessary but insufficient

## Timeline

```
1968  NATO Software Engineering Conference (birth of "software crisis")
1970s Waterfall dominates; "ops" not yet a discipline
1986  Royce's "Managing the Development of Large Software Systems"
1991  Linus Torvalds releases Linux 0.01
1995  Amazon, Yahoo, eBay launch — internet operations become a job
2001  Agile Manifesto (Snowbird, Utah)
2003  Google's Ben Treynor coins "Site Reliability Engineering"
2006  Werner Vogels: "You build it, you run it" (Amazon)
2007  Concept of "Infrastructure as Code" emerges (Puppet, Chef)
2008  Andrew Shafer & Patrick Debois — "Agile Infrastructure" talk
2009  Allspaw & Hammond — "10+ Deploys per Day" (Velocity)
2009  Patrick Debois — first DevOpsDays (Ghent, Belgium)
2010  Continuous Delivery (Humble & Farley) published
2013  Docker open-sourced
2014  Kubernetes open-sourced by Google
2016  Google's SRE Book published
2017  GitOps coined by Weaveworks
2018  Accelerate (Forsgren, Humble, Kim) — DORA research formalized
2020  Team Topologies (Skelton & Pais) — modern team patterns
2022  "Platform Engineering" enters mainstream vocabulary
2023+ Internal Developer Platforms (IDPs) become standard at scale
```

## The Forces Behind Each Shift

### Waterfall → Agile (2001)

- **Problem**: Long release cycles meant requirements changed before software shipped
- **Insight**: Embrace change instead of fighting it
- **Result**: Iterative development, but ops still operated by quarterly release windows

### Agile → DevOps (2009)

- **Problem**: Agile teams could code fast but couldn't deploy fast
- **Insight**: The dev/ops handoff was the new bottleneck
- **Result**: Shared ownership, automation, continuous integration → continuous delivery

### DevOps → SRE (2003, popularized 2016)

- **Problem**: Google had 1000s of engineers and 1000s of services; how to scale operations?
- **Insight**: Treat operations as a software engineering problem
- **Result**: SRE — operations done by software engineers with measurable reliability targets

### DevOps + SRE → Platform Engineering (2020+)

- **Problem**: Every team rebuilding the same infra wheel; cognitive load exploding
- **Insight**: Cognitive load is the real bottleneck; product teams need paved roads
- **Result**: Platform teams build internal products that abstract complexity for product devs

## Why Each Was Necessary

Each shift was **necessary but insufficient** for what came next:

- **Agile** without DevOps gives you fast dev and slow deploys
- **DevOps** without SRE gives you fast deploys without reliability discipline
- **SRE** without Platform Engineering gives you reliable services that cost too much to build

## Real-World Examples by Era

- **Pre-DevOps (2005)**: A typical bank deploys 4 times a year, each deploy is an all-hands weekend
- **Early DevOps (2010)**: Flickr deploys 10+ times a day with separate dev and ops
- **SRE Era (2015)**: Google deploys thousands of times a day with error budget gates
- **Platform Era (2024)**: Spotify, Netflix, Stripe ship hundreds of times a day with self-service platforms

## Reading Recommendations

- *The Phoenix Project* — narrative of pre-DevOps to post-DevOps transformation
- *The Unicorn Project* — same author, dev perspective
- *Site Reliability Engineering* (Google) — Chapter 1 ("Introduction")
- *Team Topologies* — Chapter 1
- Patrick Debois, "DevOps Areas" article series

## Interview Prep

**Mid**: "Why did SRE emerge separately from DevOps?"
- Answer should mention scale, engineering rigor, error budgets, and Google's specific needs

**Senior**: "Walk me through the evolution from Agile to Platform Engineering and the bottleneck each shift addressed."

**Staff**: "Pick a 2024 organizational challenge — say cognitive load — and explain how the historical sequence informs your solution."

## Next Topic

→ [T03 — DevOps vs Traditional IT Operations](T03-DevOps-vs-Traditional-IT.md)
