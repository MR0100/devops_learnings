# L29/C01/T03 — Onsite Loop

## Learning Objectives

- Understand what each round of the onsite tests and how the votes combine into a decision
- Pace yourself across a 4-6 hour day without fading in the back half
- Recover from one weak round instead of letting it sink the whole loop

## What the Onsite Is

The onsite (now usually a "virtual onsite" over video) is the full loop: **4-6 rounds of 45-60 minutes each**, run back to back in a single day or split across two. Each interviewer writes independent feedback and a vote; those feedbacks go to a committee or debrief that makes the call (see [T04](T04-Bar-Raiser.md)). It is a marathon, and the candidates who fail it are often not the weakest technically — they're the ones who fade in hours 4-5 or carry a bad mood from one round into the next.

## The Standard Round Mix

A senior+ DevOps/SRE loop typically contains:

| Round | What it tests | Where to go deep |
|---|---|---|
| Coding (1-2) | Clean, correct, tested code; communication | [C02](../C02/README.md) |
| System design (1-2) | Scope, trade-offs, scale, reliability | [C03](../C03/README.md) |
| Behavioral (1-2) | STAR stories mapped to company values | [C04](../C04/README.md) |
| Hiring manager | Team fit, project alignment, your questions | this file |
| Bar raiser / domain (varies) | Bar calibration or deep domain (K8s, Linux, networking) | [T04](T04-Bar-Raiser.md) |

For SRE specifically, expect at least one **deep technical / domain** round: debug a degraded system, reason about a Linux box at 100% CPU, or trace a request end to end. Design rounds weight heavily at senior+ — they're where leveling is decided.

## Round by Round

### Coding rounds
For DevOps these split into pure-algorithm Mediums and systems-flavored problems (rate limiter, log parser, top-K). Same bar as SWE: state the plan, narrate, state Big-O, test with an example. A partial solution with great communication beats a silent complete one.

### System design rounds
The senior+ centerpiece. 45 minutes to scope a system, propose an architecture, and defend trade-offs. Drive the discussion; don't wait to be prompted. This round, more than any other, sets your level — a Staff candidate is expected to surface failure modes and cross-cutting concerns unprompted.

### Behavioral rounds
"Tell me about a time…" answered in STAR, mapped to that company's values (Amazon LPs, Googleyness, Meta pillars). Specific, quantified, I-focused (your contribution, not "we"). This is where culture-fit and leveling signal live; under-preparing it is the most common senior-candidate failure.

### Hiring manager round
Less of an exam, more a mutual fit conversation: would you thrive on this team, does the work excite you, do your questions show you understand the role. At Meta and Apple the manager's vote carries outsized weight (see [T04](T04-Bar-Raiser.md)). Have sharp questions about the team's on-call, roadmap, and biggest current problem.

## Pacing the Day

Energy management is a real, scoreable variable:

- **Sleep** the night before; do not cram. Cramming trades a sharper morning for a foggier afternoon — a bad trade across a 6-round day.
- **Hydrate and snack** in the gaps. Take the bathroom break between rounds; you've earned it.
- **Reset between rounds.** Each interviewer starts you at zero and usually hasn't seen the others' feedback. A bad round is *not* visible to the next interviewer unless you bring it in with your body language.
- **Finish strong.** The last round counts exactly as much as the first; the fade is what loses loops.

## Recovering From a Bad Round

You will probably have one round that goes poorly — almost everyone does. The decision is made on the *aggregate*, and a single "no hire" can be outweighed by strong signals elsewhere, especially if the strong rounds include design and the bar raiser. Two moves:

1. **Compartmentalize.** Do not replay the bad round during the next one. The interviewer in front of you has a clean slate; give them your best.
2. **Counterbalance.** Be visibly excellent in the rounds you're strong in. A loop with four strong rounds and one weak one usually clears.

Take brief notes after each round (what was asked, how it felt) so you can adjust prep if there's a second day — but don't dwell.

## Best Practices

- Sleep well; don't cram the night before.
- Practice a full multi-round day, not just isolated problems, to build stamina.
- Reset emotionally between rounds; each interviewer is a clean slate.
- Have tailored questions ready for every interviewer, especially the hiring manager.
- Finish the last round as sharp as the first.
- Confirm logistics the day before (video link, IDE/collab tool, ID, a backup
  network) so nothing technical eats your first five minutes.
- Keep water and a snack within reach; the back-half slump is usually blood sugar,
  not ability.
- Jot the interviewer's name and one thing they care about at the start of each
  round — it makes your closing questions land as genuine, not scripted.

## Common Mistakes

- Fading in the back half from fatigue or low blood sugar.
- Carrying a bad mood or a botched round into the next one.
- Treating the hiring-manager round as low-stakes and bringing no real questions.
- Under-preparing behavioral relative to coding, then losing the level on stories.
- Cramming the night before and showing up foggy.

## Quick Refs

```
Format:  4-6 rounds × 45-60 min (often virtual)
Mix:     coding + design + behavioral + HM + (bar raiser/domain)
Level:   design + behavioral rounds decide it
Pace:    sleep, hydrate, snack, reset between rounds
Recover: decision is aggregate — one weak round rarely sinks a strong loop
Finish:  last round counts as much as the first
```

## Interview Prep

**Junior**: "What does the onsite actually consist of?" — Four to six 45-60 minute rounds: coding, system design, behavioral, and a hiring-manager conversation, each with an independent interviewer and vote. I prepare for the mix, not just coding, and I rehearse pacing so I'm as sharp in round five as round one.

**Mid**: "You bombed the second round — what now?" — I compartmentalize: the next interviewer has a clean slate and hasn't seen that feedback, so I give them my best instead of replaying the miss. The decision is made on the aggregate, so I counterbalance by being clearly strong in the rounds I'm good at.

**Senior**: "Which round decides your level?" — System design, with behavioral close behind. At senior+ the coding bar is table stakes; the design round is where I show scope, trade-off reasoning, and failure-mode thinking, and the behavioral round is where leveling signal lives. I invest prep there, not in grinding more Mediums.

**Staff**: "How do you treat the hiring-manager round?" — As a two-way fit conversation that I also drive. I come with sharp questions about the team's on-call load, roadmap, and biggest current problem, and I frame my interest around solving that problem. At Staff the manager's read on whether I'd raise the team's bar carries real weight in the debrief.

## Next Topic

→ [T04 — Bar Raiser / Hiring Committee](T04-Bar-Raiser.md)
