# L29/C05/T04 — Microsoft (Growth Mindset)

## Learning Objectives

- Prep Microsoft-specific process, levels, and the manager-driven decision
- Frame stories around growth mindset, customer obsession, and "One Microsoft"
- Calibrate Azure depth expectations for cloud-adjacent roles

## Roles

- **Software Engineer (SWE)** — the broad IC track across all orgs.
- **Service Engineer / Site Reliability Engineer** — Azure and M365 reliability; Microsoft's SRE-flavored track.
- **Data Center / Infra Engineer** — physical and platform infra for Azure.

DevOps work usually lives under SWE on a platform team or under the Service Engineer track. Azure orgs (the largest engineering population) skew the role toward cloud platform depth.

## Levels

Microsoft uses a numeric ladder; titles map to bands:

| Level | Title | Rough experience |
|---|---|---|
| 59-60 | SWE | New grad → 2 yr |
| 61-62 | SWE II / Senior SWE | 3-7 yr |
| 63-64 | Principal SWE | 8-15 yr |
| 65-67 | Partner | 15+ yr, org-level scope |
| 68+ | Technical Fellow / Distinguished | Company-level |

Note the jump: Senior at Microsoft (62-63) is a wider band than at Amazon/Google, and "Principal" (63-64) is reached earlier in title than at Amazon (L7). Calibrate carefully when comparing offers — a Microsoft 63 is not an Amazon L7.

## Process

1. Recruiter screen (30 min)
2. Phone screen (60 min: coding, sometimes a design lite)
3. Onsite / virtual loop (4-5 rounds):
   - Coding (2 rounds)
   - System design (1; senior+)
   - Behavioral (1-2)
   - **As-appropriate** round (1) — hiring manager, Azure-specific, or team-specific
4. Hiring manager + team debrief → offer

Microsoft historically ran an "as-appropriate" or "AA" interviewer who joins late and can change direction based on earlier rounds. Loops are increasingly virtual.

## Manager-Driven Hiring

This is the structural difference from Amazon/Google. **There is no independent bar raiser or off-team hiring committee with veto power.** The hiring manager carries the most weight, and the decision is a team consensus, not an external calibration body.

Implications:
- **Team fit matters more.** You're interviewing for a specific team, and the manager is choosing a teammate, not filling a generic req.
- **The hiring manager round is the most important one.** Build genuine rapport; show you'd be easy to work with.
- Slightly lower variance than committee-driven processes, but reference and manager rapport count for more.

## Coding

- LeetCode **medium**, occasionally easy-medium; less brutal than Google.
- Emphasis on **clean, correct code and edge cases** over exotic algorithms.
- Be ready to discuss multiple solutions and their trade-offs, then test your code.

## System Design

- Standard framework applies: requirements → API → data model → scale → reliability.
- **Azure services are welcome but not required** — using Cosmos DB or Azure Service Bus by name is fine, but a vendor-neutral design (queues, sharded stores, LB) scores equally. Don't pretend Azure fluency you lack.
- For Azure-org roles, expect to go deeper on cloud primitives (regions, availability zones, Azure Resource Manager, managed identities).

## Behavioral — Growth Mindset

Microsoft's culture under Satya Nadella centers on **growth mindset** ("learn-it-all, not know-it-all"). The behavioral signal is built around it:

| Theme | What they want to hear |
|---|---|
| Growth mindset | A real failure → what you learned → how you changed |
| Customer obsession | Decisions driven by the customer (internal devs count) |
| One Microsoft | Collaboration across teams, not heroics in a silo |
| Diversity & inclusion | Inclusive behavior, making space for others |
| Coaching | Lifting peers and juniors, not just shipping yourself |

The growth-mindset story arc matters more than the win itself: **mistake → reflection → behavior change → better outcome.** A clean success with no learning is a weaker answer than a recovered failure.

## Sample Q&A

**Q: "Tell me about a time you failed."** Pick a real, scoped failure you owned. Structure: what you tried, why it broke, what you learned, and the concrete thing you do differently now. The reflection is the point — a polished failure with no change of behavior misses the signal.

**Q: "Tell me about a time you disagreed with a teammate."** Show you sought their reasoning, weighed it against data, and either changed your mind or disagreed-and-committed gracefully. "One Microsoft" rewards collaboration over being right.

**Q: "Why Microsoft?"** Reference their actual stack and direction — Azure, the open-source pivot (they own GitHub and ship VS Code), or the team's product. Generic "great company" answers fall flat against candidates who did the reading.

## Specific to Microsoft

- The company spans Azure, M365/Office, Windows, Gaming (Xbox), GitHub, and HoloLens — **research the specific org** you're interviewing for and tailor interest accordingly.
- Microsoft is now a major **open-source** player (VS Code, TypeScript, GitHub); showing comfort there reads as cultural fit.
- Show genuine interest in their stack, not feigned Azure expertise — interviewers can tell.

## Compensation

- Base + annual bonus + RSUs (4-year vest, **even 25/25/25/25**, no Amazon-style back-loading).
- Often lower total comp than FAANG at the same level, offset by **strong work-life-balance reputation** and predictable bonuses.
- Stock-heavy upside for senior bands; refreshers matter for long-term value.

For: candidates weighing the comp / quality-of-life trade-off.

## Best Practices

- Build a growth-mindset story bank: failures with genuine learning arcs.
- Research the specific org and reference its real products and stack.
- Use inclusive, collaborative ("One Microsoft") language; avoid lone-hero framing.
- Frame decisions around the customer, even internal ones.
- For Azure-org roles, brush up on Azure primitives (ARM, identities, networking).

## Common Mistakes

- Generic stories reused verbatim from an Amazon LP prep doc.
- No growth/learning narrative — only polished wins.
- Faking Azure depth in a design round when a neutral design would score the same.
- Treating the loop as committee-driven and under-investing in manager rapport.
- "Why Microsoft" answers with no specific org or product knowledge.

## Quick Refs

```
Culture:   Growth mindset (learn-it-all)
Values:    Customer obsession | One Microsoft | D&I
Hiring:    Manager-driven (no external bar raiser)
Levels:    62-63 Senior, 63-64 Principal — calibrate vs Amazon
Coding:    LeetCode medium; clean + edge cases
Design:    Azure welcome, not required
Comp:      Even RSU vest; lower than FAANG; better WLB
```

## Interview Prep

**Junior**: "I lead a growth-mindset answer with a real failure, what I learned, and the habit I changed — the reflection, not the win, is what they're scoring."

**Mid**: "I tailor 'why Microsoft' to the specific org, naming its stack and the open-source work, and frame decisions around the customer including internal developers."

**Senior**: "I treat the hiring-manager round as decisive since there's no external bar raiser, building real rapport and showing I'd be an easy, collaborative teammate across teams."

**Staff**: "I anchor stories in 'One Microsoft' — cross-org influence, coaching, and inclusive leadership at scale — and in design I reach for Azure primitives only where they genuinely improve the answer."

## Next Topic

→ [T05 — Apple](T05-Apple.md)
