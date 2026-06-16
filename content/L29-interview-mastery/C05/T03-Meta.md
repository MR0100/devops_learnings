# L29/C05/T03 — Meta (Move Fast, Impact)

## Learning Objectives

- Prep Meta's loop and the Production Engineer (PE) track for DevOps/SRE
- Quantify impact relentlessly — Meta's defining behavioral signal
- Understand the manager-driven decision and the separate leveling discussion

## Roles

- **SWE (E3-E8)** — broad IC track.
- **Production Engineer (PE)** — Meta's hybrid SWE/SRE role; **this is the DevOps/SRE track.** PEs embed with product teams and own reliability, scaling, and operational tooling with real software depth.

If you're a DevOps/SRE candidate, target **Production Engineer**: the loop shifts toward systems, Linux, and networking and away from pure algorithms.

## Levels

- E3-E4: SWE (junior-mid) · **E5: Senior** · **E6: Staff** · E7: Senior Staff · E8: Principal

E5 (Senior) is the common target; E6 (Staff) is the cross-team jump. (See [C01/T05](../C01/T05-Levels.md).)

## Process

1. Recruiter screen
2. Phone screen (1-2 coding problems; for PE, often a systems/Linux problem instead of or alongside DSA)
3. Onsite, typically **4-5 rounds**:
   - Coding (2)
   - System design (1; senior+)
   - Behavioral — "**Jedi**" / leadership round (1-2)
   - For **PE:** a systems/troubleshooting round replaces or supplements one coding round
4. Debrief → **hiring manager + committee for leveling** → team match → offer

Meta's decision leans on the **hiring manager** more than Amazon/Google's external bodies, with a committee involved chiefly to calibrate *level*. Manager rapport matters.

## Production Engineer Specifics

The PE loop is the reason a DevOps candidate should prefer Meta's PE track:

- **Systems over algorithms** — expect Linux internals, networking, "debug this degraded service," and coding that's more scripting/systems than LeetCode-hard.
- **Operational depth** — how you'd monitor, scale, and roll back; on-call judgment.
- Still includes real coding — PEs write software — but the flavor is practical.

## Coding

- **LeetCode medium**; less brutal than Google. Clean, correct, communicated.
- For PE, some rounds are **systems coding** (parse logs, manipulate processes, write a small tool) rather than abstract DSA.

## System Design

- Senior+ centerpiece; standard framework with strong emphasis on **scale** — Meta operates at billions of users, so they want to see you reason about that magnitude (sharding, caching, fan-out, hot keys).
- Trade-offs and back-of-envelope numbers expected.

## Behavioral — Move Fast & Impact

Meta's culture is built around **shipping and measurable impact**. The behavioral signal:

| Theme | What they want to hear |
|---|---|
| **Impact** | Quantified outcomes — users affected, revenue, latency, cost |
| **Move Fast** | Decisive shipping; iterating over perfecting |
| **Be Open / Be Bold** | Calculated risk-taking; transparency about failures |

**Quantification is non-negotiable at Meta.** Every story should carry a number: "shipped to 1M users," "cut p99 from 800ms to 200ms," "saved $500K/year." A story without a metric reads as low-impact regardless of how hard the work was.

## Failure Is Acceptable — If You Learned

Meta's "Move Fast" explicitly tolerates breakage in service of speed (the old "move fast and break things," now tempered to "move fast with stable infra"). A good failure story: "I shipped X quickly, it broke Y, I learned Z, and now I do W." What they *don't* want is paralysis or a flawless-but-slow record with no bold bets.

## Sample Q&A

**Q: "Tell me about your most impactful project."** Lead with the metric. Structure: the problem, what you shipped, and the *quantified* outcome — then the scale (users, QPS, dollars). If you can't attach a number, pick a different story.

**Q: "Tell me about a time you moved fast and something broke."** This is on-brand for Meta. Show decisive shipping, honest ownership of what broke, the fix, and the systemic prevention. The willingness to take the risk is the signal; the recovery proves judgment.

**Q: "Why Meta / why this team?"** Reference their actual scale and a product or infra problem you want to work on. PE candidates: name the reliability/scaling challenge that excites you.

## Specific to Meta

- **Quantify every behavioral story** — this is the single biggest differentiator at Meta.
- Target the **PE track** for DevOps; it plays to systems strength over algorithm speed.
- Show bias to ship and comfort with calculated risk, not perfectionism.
- For design, reason explicitly at billion-user scale.

## Compensation

- Base (~$200K+) + target bonus (~10-25%, performance-multiplied) + **RSUs (heavy)** + sign-on.
- **One-year cliff**, then vesting (historically front-loaded / even quarterly — better early-year comp than Amazon's back-load).
- Refreshers tied to performance ratings; strong performers get larger refreshes.

Rough US bands: E5 ~$400-580K, E6 ~$700K-1M (verify on levels.fyi). (See [C06/T01](../C06/T01-Comp-Components.md).)

## Best Practices

- Attach a metric to every story; rehearse the numbers.
- Choose the PE track and prep systems/Linux/networking depth.
- Have a "moved fast, broke something, recovered" story ready.
- Reason at Meta-scale in design rounds.
- Build manager rapport — the decision leans on them.

## Common Mistakes

- Behavioral stories with no quantified impact (the cardinal Meta sin).
- Applying to generic SWE when PE fits a DevOps profile better.
- An all-clean record with no bold bets or learned failures.
- Under-scaling a design when Meta wants billion-user reasoning.
- Treating the loop as committee-driven and neglecting the manager.

## Quick Refs

```
Track:    Production Engineer (PE) = DevOps/SRE — systems-flavored loop
Coding:   medium; PE rounds lean systems/Linux
Design:   senior+; reason at billion-user scale
Behav:    Move Fast + IMPACT (quantify everything) + Be Bold
Failure:  acceptable if you learned and prevented recurrence
Decision: hiring-manager-led; committee calibrates level
```

## Interview Prep

**Junior**: "What's the single most important thing for Meta behavioral?" — Quantify every story. 'Shipped to 1M users,' 'cut p99 from 800ms to 200ms,' '$500K saved' — a story without a number reads as low-impact at Meta no matter how hard the work was, so I rehearse the metrics, not just the narrative.

**Mid**: "Which track should a DevOps engineer target at Meta?" — Production Engineer. It's Meta's SWE/SRE hybrid and the loop shifts toward Linux, networking, and systems troubleshooting rather than algorithm-hard LeetCode, so it plays to operational strength while still expecting real coding.

**Senior**: "Tell me about moving fast and breaking something." — I lead with a decisive ship, own honestly what broke, then show the fix and the systemic prevention. Meta's 'Move Fast' explicitly tolerates calculated breakage, so the willingness to take the bet is the signal and the recovery proves my judgment — paralysis or a flawless-but-slow record scores worse.

**Staff**: "How does Meta's decision and comp compare to Amazon's?" — The decision leans on the hiring manager with a committee mainly calibrating level, so manager rapport matters more than at Amazon or Google. On comp, Meta's RSUs vest more evenly than Amazon's 5/15/40/40 back-load, so year-one is closer to the headline — I model both across four years and weigh the performance-driven refresher upside.

## Next Topic

→ [T04 — Microsoft](T04-Microsoft.md)
