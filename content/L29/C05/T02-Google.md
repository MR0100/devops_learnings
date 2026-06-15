# L29/C05/T02 — Google (Googleyness, GCA, Domain)

## Learning Objectives

- Prep Google's algorithm-heavy loop and the committee-driven decision
- Distinguish the four scored dimensions: coding, system design, Googleyness & Leadership, and GCA
- Calibrate Google's even-vesting comp and the SRE track specifically

## Roles

- **SWE** — broad IC track; DevOps/platform work lives here.
- **SRE** — Google *invented* the discipline; the SRE track is deep, production-focused, and prestigious.
- **Cloud Engineer / Customer Engineer** — GCP-facing.

For DevOps, the cleanest fit is often **SRE**, which at Google splits into SWE-SRE (more coding) and SysEng-SRE (more systems), both rigorous.

## Levels

- L3: SWE II · L4: SWE III · **L5: Senior SWE** · **L6: Staff SWE** · L7: Senior Staff · L8: Principal · L9: Distinguished · L10: Fellow

L5 is the senior anchor; L6 (Staff) is the hard cross-team jump. (See [C01/T05](../C01/T05-Levels.md).)

## Process

1. Recruiter screen
2. Phone screen (1-2 coding problems)
3. Onsite, typically **4-5 rounds**:
   - Coding (2) — algorithm-heavy
   - System design (1; required at L5+)
   - Behavioral — **Googleyness & Leadership** (1)
   - Domain / SRE-specific (varies; for SRE expect a "non-abstract large system design" or troubleshooting round)
4. Feedback → **hiring committee** → team match → offer

## The Hiring Committee

Google's defining feature: the interviewers **don't decide**. Your written feedback becomes a **packet** reviewed by an independent **hiring committee** of senior engineers who never met you. Implications:

- **No interviewer veto** — not even the hiring manager hires or rejects you alone.
- **Written quality is decisive** — the committee sees notes, not you. **Vague answers produce vague notes.** Be specific and memorable so your interviewers can write strong, concrete feedback.
- **Team matching is separate** — at Google you can pass the committee and *then* be matched to a team, sometimes after the hire decision. (Full mechanics: [C01/T04](../C01/T04-Bar-Raiser.md).)

## Coding

- **LeetCode medium-to-hard** — Google leans harder than most. Expect to be pushed to the **optimal** solution and to handle multiple problems per round.
- Clean code, correct complexity analysis, and a tested example are non-negotiable.
- Practice hards specifically; a "good enough" medium-tier solution that you can't optimize reads as a borderline signal here.

## System Design

- Required at L5+; the standard 35-45 min framework (requirements → API → data model → scale → reliability).
- For **SRE**, expect "Non-Abstract Large System Design" (NALSD): real capacity math, back-of-envelope numbers, failure domains, and how you'd actually run it. Latency numbers and capacity estimation matter — have them cold (see [C03](../C03/README.md)).
- Drive the discussion; Google scores whether you *lead* the design, not just answer prompts.

## Behavioral — Googleyness & Leadership

Google's behavioral signal has two named components:

| Component | What they want |
|---|---|
| **Googleyness** | Comfort with ambiguity, bias to action, collaboration, intellectual humility, doing the right thing |
| **Leadership** | Leading through influence (not authority), mentoring, driving outcomes across teams |

The "Googleyness" bar rewards people who navigate undefined problems gracefully and collaborate without ego. Have stories of operating with no clear path, changing your mind on new data, and lifting a team.

## GCA — General Cognitive Ability

Google explicitly scores **how you think**, not just whether you know the answer. GCA shows up as open-ended or unfamiliar problems where the interviewer watches your reasoning, assumptions, and how you structure ambiguity. You can't memorize it; practice thinking out loud on problems you haven't seen, stating assumptions, and decomposing methodically.

## SRE-Specific

Google originated SRE, so for SRE roles expect depth on: SLIs/SLOs/error budgets, toil reduction, capacity planning, incident response, and the production mindset from the SRE book. A DevOps candidate who can speak fluently about error budgets and NALSD has a real edge here (see [L19](../../L19/README.md)).

## Sample Q&A

**Q (coding): "Can you do better than O(n²)?"** Google interviewers push to optimal. State your current complexity, name the bottleneck, propose the better structure, and only stop when you've reached the asymptotic floor or the interviewer is satisfied.

**Q (Googleyness): "Tell me about a time you worked on something with no clear direction."** Show comfort with ambiguity: how you framed the problem, made progress without full information, and adjusted as you learned. The signal is calm structured action, not heroics.

**Q (Googleyness): "Tell me about a time you changed your mind."** Intellectual humility is core Googleyness. Show you sought disconfirming evidence and updated gracefully — being "right a lot" *and* able to be wrong without ego.

## Specific to Google

- Practice **hard** algorithms, not just mediums — the bar is genuinely higher.
- Read the **SRE book / Site Reliability Workbook** for SRE roles; speak error-budget fluently.
- Be specific in every answer so interviewers can write strong notes for the committee.
- Show Googleyness: humility, collaboration, ambiguity-comfort — not just raw technical strength.

## Compensation

- Base + target bonus (~15%) + **RSUs vesting evenly** (front-loaded historically, now roughly even quarterly after a short cliff) + sign-on.
- **Annual refreshers** matter for long-term value and stack over time.
- Even vesting makes year-1 comp closer to the headline than Amazon's back-loaded grant — factor that when comparing.

Rough US bands: L5 ~$400-600K, L6 ~$600-900K, L7 ~$900K-1.5M (verify on levels.fyi).

## Best Practices

- Grind hards, not just mediums; aim for optimal solutions.
- For SRE, master SLOs/error budgets and NALSD capacity math.
- Prepare Googleyness stories: ambiguity, changing your mind, collaboration.
- Answer specifically so the committee gets a vivid packet.
- Drive system-design rounds rather than waiting for prompts.

## Common Mistakes

- Only practicing mediums and getting stuck short of optimal.
- Weak or generic system design at L5+.
- Skipping Googleyness prep and coming across as a lone technical hero.
- Vague answers that produce thin written feedback for the committee.
- For SRE, no fluency in error budgets / capacity estimation.

## Quick Refs

```
Coding:   medium-HARD; optimal expected; multiple per round
Design:   L5+ required; SRE → NALSD capacity math
Behav:    Googleyness (ambiguity, humility, collab) + Leadership
GCA:      how you think on unfamiliar problems — narrate
Decision: hiring committee on the packet — be specific & memorable
Comp:     even RSU vest; refreshers stack; L5 ~$400-600K
```

## Interview Prep

**Junior**: "How is Google's coding bar different?" — It's harder — medium-to-hard, and they push me to the *optimal* solution rather than accepting a working one. So I practice hards specifically, state and improve my complexity out loud, and make sure I can reach the asymptotic floor, not just pass the test cases.

**Mid**: "What is Googleyness and how do you show it?" — Comfort with ambiguity, intellectual humility, and collaboration without ego. I prepare stories of operating with no clear path, of changing my mind on new evidence, and of lifting a team through influence rather than authority — because Google scores those as explicitly as it scores code.

**Senior**: "Who actually decides, and what does that change?" — An independent hiring committee reviews a written packet; the interviewers don't decide and there's no manager veto. Since the committee only sees notes, I answer specifically and memorably so my interviewers can write strong, concrete feedback — vague answers become vague notes and sink the packet.

**Staff**: "How do you prep the SRE design round?" — Non-Abstract Large System Design: real capacity math, back-of-envelope QPS and storage numbers, failure domains, and how I'd actually operate it. I come fluent in SLIs/SLOs and error budgets and ground the design in latency and capacity numbers I know cold, since at Staff the differentiator is operational judgment, not algorithm speed.

## Next Topic

→ [T03 — Meta](T03-Meta.md)
