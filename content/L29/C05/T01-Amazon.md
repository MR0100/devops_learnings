# L29/C05/T01 — Amazon (LP-Heavy, Frugality, Ownership)

## Learning Objectives

- Prep Amazon's LP-saturated loop and the bar raiser specifically
- Build two LP stories per principle, weighted toward the DevOps-relevant ones
- Calibrate Amazon's back-loaded comp so you compare offers honestly

## Roles

- **SDE (Software Development Engineer)** — the broad IC track; DevOps work usually lives here on a platform/infra team.
- **SRE (Site Reliability Engineer)** — reliability for AWS and consumer services; ops-heavy.
- **TPM (Technical Program Manager)** — coordination-heavy, less coding.

DevOps at Amazon is typically an SDE with an infra/platform focus, or a dedicated SRE. Both run the standard loop with heavy Leadership Principle pressure.

## Levels

| Level | Title | Tier |
|---|---|---|
| L4 | SDE I | New grad → mid |
| L5 | SDE II | Mid-senior (the common entry target) |
| L6 | Senior SDE | Senior / Staff-boundary |
| L7 | Principal SDE | Org-level |
| L8 | Senior Principal | Multi-org |

Calibrate: Amazon's L6 ("Senior") sits near the Google/Meta Senior-to-Staff boundary, and L7 ("Principal") is a large jump — don't equate it with a Microsoft "Principal." (See [C01/T05](../C01/T05-Levels.md).)

## Process

1. Recruiter screen
2. Online assessment or phone screen (coding; sometimes a work-style survey)
3. Onsite loop, **5 rounds**:
   - Coding (1-2)
   - System design (1-2; senior+)
   - Behavioral (LP-heavy, woven through every round)
   - **Bar raiser (1)** — mixed coding/behavioral, run by an external calibrator

The defining feature: **Leadership Principles are tested in every round**, not just the behavioral one. A coding interviewer will still ask "tell me about a time you had to dive deep to fix a bug." Prepare LP stories as carefully as algorithms.

## The Bar Raiser

A trained interviewer from **outside the hiring team** with **veto power**, present specifically to protect the company-wide bar. They're behavioral-heavy and strict, drilling for depth ("walk me through exactly what *you* did, not the team"). Their bar: is this candidate above the median Amazonian at the target level? Bring extra LP stories and expect relentless follow-ups. (Full mechanics in [C01/T04](../C01/T04-Bar-Raiser.md).)

## The Leadership Principles

There are 16 LPs; you don't get questions on all of them, but you must have stories ready. The DevOps-weighted ones:

- **Ownership** — you act beyond your job scope and think long-term, not "that's not my team's problem."
- **Bias for Action** — speed matters; calculated risks over analysis paralysis. (Ops-relevant: acting decisively in an incident.)
- **Dive Deep** — you stay connected to the details, audit the metrics, find the root cause. The bar raiser loves this one.
- **Insist on the Highest Standards** — you hold a high bar and don't ship known-broken.
- **Earn Trust** — you're candid, self-critical, and treat others with respect.
- **Are Right, A Lot** — strong judgment; you seek diverse perspectives and disconfirming data.
- **Frugality** — accomplish more with less (see below).
- **Customer Obsession** — start from the customer and work backward, even for internal platforms.

Prepare **two stories per LP** so you're not reusing the same one when an interviewer asks a follow-up. (Deep LP technique in [C04/T02](../C04/T02-Amazon-LPs.md).)

## Frugality

Amazon genuinely values doing more with less, and a **frugality story is the one candidates most often lack**. Have a concrete, quantified example:

- "Cut our AWS bill ~$500K/year by right-sizing and moving batch workloads to Spot."
- "Avoided a six-figure vendor tool by building a 200-line internal exporter that covered our actual need."

The signal is resourcefulness, not cheapness — constraints breeding invention.

## Customer Obsession (Even Internal)

For a platform/infra role, your "customer" is the **internal developer** who uses your tooling. Frame stories around their experience: "deploy time was 45 minutes and engineers were context-switching away; I treated them as customers, cut it to 9 minutes, and adoption went from 3 teams to 30." External-customer stories work too where you have them.

## Coding

- **LeetCode medium**, occasionally harder. Edge cases matter; clean, tested code.
- The coding interviewer still scores LPs — narrate your judgment, not just your algorithm.

## System Design

- **L5:** a single-region service or two, covering scale and reliability solidly.
- **L6+:** multi-region, multiple subsystems, real trade-offs (consistency vs availability, cost vs latency).
- Amazon design rounds reward operational thinking: how do you deploy it, monitor it, roll it back? That's home turf for a DevOps candidate — lean in.

## Sample Q&A

**Q: "Tell me about a time you took ownership of something outside your responsibility."** Pick a story where you saw a problem nobody owned and drove it to resolution. Emphasize *you* — Amazon penalizes "we" answers where your specific contribution is invisible.

**Q: "Tell me about a time you had to dig deep into a hard problem."** This is Dive Deep. Walk through the investigation: the symptom, the metrics you pulled, the hypotheses you ruled out, the root cause, the fix, and the prevention. Depth and specificity are the whole signal.

**Q: "Tell me about a time you disagreed with your manager."** This is Have Backbone; Disagree and Commit. Show you pushed back with data, then — whichever way it went — committed fully once the decision was made. The failure mode is either being a pushover or sulking after losing.

## Specific to Amazon

- Map your stories to LPs explicitly during prep; tag each story with the 2-3 LPs it demonstrates.
- Always have a **frugality** and a **dive-deep** story ready; they're the most common gaps.
- Quantify everything — Amazon's culture is metric-driven and the bar raiser will ask for numbers.
- Use "I," not "we"; the loop is scoring *your* contribution.

## Compensation

- **Base is capped** (historically ~$350-400K total cash cap including base+sign-on per year, with base itself often well under $200K).
- **RSUs vest back-loaded: 5% / 15% / 40% / 40%** over four years.
- **Sign-on bonuses in years 1 and 2** bridge the thin early RSU vesting — without them, your year-1 and year-2 comp would be far below the headline number.
- **One-year cliff** on the first RSU tranche.

Model this carefully: the headline TC assumes the stock holds and the back-loaded years arrive. Compare against an evenly-vesting Google/Meta offer on a multi-year basis, not just year one. (See [C06/T01](../C06/T01-Comp-Components.md).)

## Best Practices

- Two stories per LP, tagged by principle; weight the DevOps-relevant ones.
- Always carry a quantified frugality story and a deep root-cause story.
- Frame internal-platform work as customer obsession toward developers.
- Prepare specifically for the bar raiser's depth follow-ups.
- Model the back-loaded comp across all four years before comparing offers.

## Common Mistakes

- Generic stories not mapped to any LP.
- No frugality story — a glaring gap at Amazon.
- "We" answers that hide your individual contribution.
- Under-preparing the bar raiser and getting caught shallow on follow-ups.
- Comparing Amazon's year-1 TC to an evenly-vesting offer's, missing the back-load.

## Quick Refs

```
LPs:       16; tested in EVERY round; 2 stories each
Top LPs:   Ownership, Bias for Action, Dive Deep, Earn Trust, Frugality
Bar raiser: external, veto, behavioral-heavy — bring depth
Frugality: have a quantified story (the common gap)
Voice:     "I" not "we"; quantify everything
Comp:      base-capped; RSU 5/15/40/40; sign-on Y1+Y2 bridges
```

## Interview Prep

**Junior**: "Why does Amazon ask behavioral questions in the coding round?" — Because Leadership Principles are tested in *every* round, not just the behavioral one. A coding interviewer will still ask 'tell me about a time you dove deep,' so I prepare two LP stories per principle as seriously as I prepare algorithms.

**Mid**: "Amazon wants a frugality example — what do you give?" — A concrete, quantified one: cutting the AWS bill ~$500K by right-sizing and moving batch to Spot, or replacing a costly vendor tool with a small internal exporter. The signal is resourcefulness under constraint, and it's the story candidates most often lack.

**Senior**: "How do you handle the bar raiser?" — As the strictest, most behavioral round, run by someone external with veto power who drills for depth. I bring extra stories so I'm not reusing one on a follow-up, and I answer in 'I' with specifics — the exact metrics I pulled, the hypotheses I ruled out — because vague 'we' answers fail the raise-the-bar test.

**Staff**: "How do you read Amazon's comp against a Google offer?" — Amazon back-loads RSUs 5/15/40/40 and caps cash, bridging the thin early years with year-1 and year-2 sign-ons. So I model all four years, not just the headline year-1 number, assume some stock risk, and compare it against Google's even quarterly vest on a total multi-year basis before deciding.

## Next Topic

→ [T02 — Google](T02-Google.md)
