# L29/C05/T05 — Apple (Secretive, Hardware-Software)

## Learning Objectives

- Prep Apple-specific process, the org-by-org variance, and team-fit weighting
- Show deep technical fundamentals and domain craftsmanship
- Navigate Apple's secrecy and compartmentalization without losing signal

## Roles

- **Software Engineer (SWE)** — broad IC track; titling and scope vary heavily by org.
- **Infrastructure / Platform Engineer** — internal tooling, build, CI/CD, fleet.
- **Site Reliability Engineer** — newer at Apple; reliability for services (iCloud, App Store, Apple Music, Maps).

DevOps work spans infra/platform and SRE, often inside a product org rather than a central platform team.

## Levels

Apple uses the **ICT** (Individual Contributor, Technical) ladder:

| Level | Rough mapping |
|---|---|
| ICT2 | Engineer (new grad → 2 yr) |
| ICT3 | Engineer (mid; 3-5 yr) |
| ICT4 | Senior Engineer (5-10 yr) |
| ICT5 | Staff / Principal-equivalent |
| ICT6 | Principal |

Apple deliberately **downplays titles internally** — levels are not public-facing, and you often won't see "Senior" on a business card. ICT4 is the common senior target; ICT5+ carries org-level scope. Comp and scope vary widely by org even at the same ICT.

## Process

1. Recruiter screen
2. **Multiple phone screens** (often 1-2 technical screens before onsite)
3. Onsite loop (4-6 rounds, team-defined):
   - Coding (1-2)
   - System design (1)
   - **Team-fit / domain rounds (heavy)** — often 2+ rounds with the hiring team
4. Team debrief → offer

The loop is **assembled by the hiring team**, so there is no single uniform Apple process — two candidates in different orgs can have very different loops. Expect more conversational, team-driven rounds than the structured LP/committee machinery at Amazon or Google.

## Culture

- **Secretive.** Information is compartmentalized; you may not learn what the team actually builds until late (or after) the process. NDAs are standard.
- **Hardware + software integration.** Apple's edge is the seam between silicon, OS, and product — teams value people who think across that boundary.
- **Quality and craftsmanship.** Polish, attention to detail, and design taste are first-class signals, not nice-to-haves.
- **More siloed** than peers — collaboration is intense *within* a team, deliberately limited *across* teams.

## Coding

- LeetCode **medium**, occasionally medium-hard.
- **Team-specific flavor:** an iOS team values Swift/Objective-C familiarity; a low-level team probes C/C++ and memory; an infra team leans Python/Go and systems. Match the language to the org.
- Clean code, edge cases, and reasoning out loud — standard expectations.

## System Design

- Solid distributed-systems fundamentals expected at senior+ (ICT4+).
- **Depth depends on the team:** a services org runs a normal scale/reliability design; a device/embedded team may probe resource constraints, power, or on-device vs cloud trade-offs.
- Expect questions grounded in *their* domain rather than generic "design Twitter."

## Behavioral

- **Less leadership-principle / pillar driven** than Amazon or Meta — no scripted value framework to recite.
- **More team-fit and conversational.** Interviewers assess whether you'd thrive in their specific culture and collaborate well.
- Common themes: quality and craftsmanship, customer experience, collaboration, ownership of a hard technical problem.

## Sample Q&A

**Q: "What can you tell me about the team / what will I work on?"** Apple often won't say much pre-offer. Ask once, accept the boundary gracefully, and **do not keep probing** — pushing on secrecy reads as a poor culture fit. Redirect to "what qualities make someone successful here?"

**Q: "Tell me about a project you're proud of."** Lead with **technical depth and craftsmanship** — the hard problem, the trade-offs, the polish you insisted on. Apple rewards depth-of-one over breadth-of-many. Hype without substance is a fast "no."

**Q: "Why Apple?"** Anchor in the **product and the hardware-software integration** — genuine enthusiasm for what they ship and how it's built. Show you care about the craft, not just the brand.

## Specific to Apple

- Show genuine interest in their **product** and domain; surface-level brand enthusiasm doesn't land.
- Demonstrate **technical depth in your area** rather than broad-but-shallow coverage.
- **Respect the secrecy** — don't push for details they can't share; treating the boundary professionally is itself a signal.
- Tailor language/stack knowledge to the org you're interviewing for.

## Compensation

- Base + annual bonus + RSUs (4-year vest).
- Often **lower total comp than peak FAANG** at the same level, and **highly variable by org** — some teams pay well above band, others sit lower.
- Limited public leveling data makes negotiation harder; gather org-specific signal where you can.

## Best Practices

- Go **deep** in your domain; depth-of-one beats breadth-of-many at Apple.
- Show passion for the product and the hardware-software craft.
- Nail technical fundamentals — clean coding, solid systems reasoning.
- Match coding language and design depth to the specific team.
- Respect secrecy; ask about the team once, then let it go.

## Common Mistakes

- Probing too hard on secret projects or pushing past a "can't share that."
- Hype-only enthusiasm with no technical depth underneath.
- Generic, reused behavioral stories with no craftsmanship angle.
- Assuming a uniform "Apple process" — under-preparing for a team-specific loop.
- Bringing the wrong language/stack for the org (e.g., no Swift sense for an iOS team).

## Quick Refs

```
Culture:  Secretive | hardware+software | craftsmanship
Process:  Team-assembled (no uniform loop); team-fit heavy
Levels:   ICT2-6; ICT4 = senior; titles downplayed
Coding:   LeetCode medium; language matches the team
Design:   Fundamentals + team-domain depth
Behav:    Conversational team-fit, not LP/pillars
Comp:     Variable by org; often below peak FAANG
Rule:     Respect secrecy — don't over-probe
```

## Interview Prep

**Junior**: "I show clean fundamentals and match my coding language to the team's stack — Swift sense for an iOS org, Python/Go for infra — and trace my code on an example."

**Mid**: "I lead behavioral answers with technical depth and craftsmanship on one hard problem rather than a broad résumé tour, since Apple rewards depth-of-one."

**Senior**: "I treat the loop as team-assembled and conversational, build genuine fit with the hiring team, and ground my design answers in their actual domain and constraints."

**Staff**: "I demonstrate cross-boundary thinking at the hardware-software seam and org-level technical judgment, while respecting compartmentalization — asking about scope once and reading the secrecy boundary as a fit signal."

## Next Topic

→ [T06 — Netflix](T06-Netflix.md)
