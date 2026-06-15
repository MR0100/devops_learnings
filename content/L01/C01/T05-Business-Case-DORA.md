# L01/C01/T05 — The Business Case for DevOps (DORA Metrics Intro)

## Learning Objectives

- Articulate the business case for DevOps using empirical research
- Name the four DORA metrics, their definitions, and their benchmarks
- Explain why elite performers ship more often *and* fail less often

## Why a Business Case Matters

Engineers love DevOps for craft reasons. Executives fund it for business reasons. A staff engineer translates between the two.

## The DORA Research

The State of DevOps Report (now part of Google Cloud) is the largest body of academic research on software delivery performance. Started in 2014 by Nicole Forsgren, Jez Humble, and Gene Kim. Findings published yearly; capstone book: *Accelerate* (2018).

Methodology: cluster analysis on 30,000+ surveyed engineers across thousands of organizations.

## The Four Key Metrics

### 1. Deployment Frequency (DF)

How often do you successfully push to production?

| Performer | Frequency |
|---|---|
| Elite | Multiple times per day |
| High | Daily to weekly |
| Medium | Weekly to monthly |
| Low | Monthly to bi-annually |

### 2. Lead Time for Changes (LT)

Time from "code committed" to "code in production".

| Performer | Lead Time |
|---|---|
| Elite | Less than 1 hour |
| High | 1 day to 1 week |
| Medium | 1 week to 1 month |
| Low | 1 month to 6 months |

### 3. Mean Time to Recovery (MTTR)

Time to restore service after an incident.

| Performer | MTTR |
|---|---|
| Elite | Less than 1 hour |
| High | Less than 1 day |
| Medium | 1 day to 1 week |
| Low | 1 week to 1 month |

### 4. Change Failure Rate (CFR)

Percentage of deployments that cause a production failure requiring intervention.

| Performer | CFR |
|---|---|
| Elite | 0–15% |
| High | 16–30% |
| Medium | 16–30% |
| Low | 16–30% |

## The Counter-Intuitive Finding

> Elite performers ship **973× more frequently** with **6,570× faster lead times** AND have **3× lower change failure rates**.

The pre-DevOps assumption was that speed and stability were tradeoffs. DORA falsified this empirically. Both improve together when capabilities (CI, IaC, observability, test automation, team culture) improve.

## How to Compute Each Metric

### Deployment Frequency
```
count(successful_prod_deploys) / time_window
```
Source: CI/CD pipeline records.

### Lead Time
```
median(deploy_time - commit_time) over successful deploys
```
Source: Git commit timestamps + deploy timestamps.

### MTTR
```
mean(restoration_time - incident_start_time) over P0/P1 incidents
```
Source: incident management system (PagerDuty, Opsgenie).

### Change Failure Rate
```
count(deploys_causing_incident) / count(all_deploys)
```
Source: link deploys to incidents (annotate incidents with related deploys).

## The 5th Metric (2021 onward): Reliability

In 2021, DORA added **Reliability** to operational performance, recognizing that velocity metrics alone can lead to corner-cutting. Reliability is typically measured via SLO compliance.

## Common Gaming and How to Avoid It

| Gaming Pattern | Why It's Bad | Defense |
|---|---|---|
| Counting deploys to staging | Inflates DF | Define "deploy" = "production prod release" |
| Excluding hotfixes from CFR | Hides instability | Include all production-impacting changes |
| Defining "incident" narrowly | Hides MTTR issues | Use externally-observable criteria (customer impact) |
| Per-engineer DORA scoring | Creates perverse incentives | Use only at team/system level |

## Business Outcomes That Correlate

Beyond the four metrics, DORA research correlates elite performance with:

- 2× more likely to exceed organizational performance goals
- Higher employee satisfaction / lower burnout
- Better security posture (yes — speed and security correlate)
- Better recovery from operational incidents

## Sample Executive Pitch (2 minutes)

> "Our deploy frequency is monthly; elite performers deploy daily. Our lead time is 6 weeks; elite is under a day. The cost is opportunity — we're losing 30 weeks of feature delivery per year per team. The cause isn't engineers; it's our pipeline, our testing strategy, and our team structure. I'm proposing a 6-month investment plan with these gates: (1) CI build under 10 minutes by Q2, (2) trunk-based development by Q3, (3) first daily deployer team by Q4. Investment: $X. Expected ROI: a 3× feature throughput improvement, measured by DORA, validated quarterly."

This is how a staff engineer talks to executives.

## Common Mistakes

- **Leading with tools, not money** — executives fund outcomes (throughput, risk, retention), not "we want to adopt Kubernetes."
- **Presenting the four metrics as four goals** — they form a *system*; chasing one (e.g., deploy frequency) while ignoring CFR produces a worse, not better, story.
- **Quoting elite benchmarks without your baseline** — a target with no measured starting point is a wish, not a business case.
- **Promising a transformation "done date"** — invites the "are we done yet?" question; pitch capability-building with quarterly gates instead.
- **Ignoring the human cost** — a DORA-only pitch that drives burnout collapses; pair it with SPACE so leadership sees sustainability.

## Best Practices

- **Quantify the opportunity cost** — translate slow lead time into "X weeks of feature delivery lost per team per year" so finance can reason about it.
- **Tie each metric to a business outcome** — frequency → time-to-market, CFR → customer trust/revenue at risk, MTTR → SLA and reputation.
- **Propose dated, falsifiable gates** — e.g., "CI under 10 minutes by Q2," so the program is auditable, not aspirational.
- **Measure before you pitch** — compute your real DORA baseline first; the gap between it and elite *is* the case.
- **Re-measure quarterly and report honestly** — including regressions; credibility compounds and protects the next budget ask.

## Quick Refs

**The four DORA metrics → what to say to an exec**

| Metric | Plain-English business value |
|---|---|
| Deployment Frequency | How fast we can put value (and fixes) in front of customers |
| Lead Time for Changes | Idea-to-customer latency; our responsiveness to the market |
| Change Failure Rate | How often shipping breaks things; customer trust at risk |
| Time to Restore (MTTR) | How fast we recover; SLA exposure and reputation |

**Pitch skeleton**: Baseline → Elite benchmark → Cost of the gap (in weeks/$) → Root cause (pipeline/testing/structure, *not* people) → Dated investment gates → Expected ROI, validated quarterly.

**Anti-gaming rule**: report every metric with a quality counterweight (frequency *with* CFR, MTTR *with* incident count) so no single number can be juiced in isolation.

## Interview Prep

**Mid**: "Name and define the four DORA metrics."

**Senior**: "Your team's CFR is 35% and MTTR is 4 hours. Pick one to improve first and explain why."
- Either is defensible. A great answer: "CFR — because high CFR multiplies the cost of MTTR. If we deploy 10x a day with 35% CFR, we cause 3.5 incidents/day. Reducing CFR halves the firefighting load, freeing capacity to attack MTTR."

**Staff**: "Your CTO says DORA metrics are great but our engineers report burnout and your team velocity is plateauing. What do you do?"
- Recognize DORA measures *flow*, not *human cost*. Add SPACE metrics (Satisfaction, Performance, Activity, Communication, Efficiency). Question whether DORA gains came from sustainable improvements or pressure.

## Lab

Compute your current team's DORA metrics over the last 90 days. If your tooling doesn't track them, this exercise reveals the first investment: instrumentation.

## Next Chapter

→ [C02 — DevOps Culture & Principles](../C02/README.md)
