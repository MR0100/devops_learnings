# L29/C01/T05 — Levels at Each Company

## Learning Objectives

- Map your current scope to the right target level across companies
- Translate between company ladders so you can compare offers honestly
- Decide whether to aim lateral, stretch, or accept a down-level

## Why Level Is the Most Important Number

Level determines comp band, scope, title, and trajectory — and it's far harder to change *after* you join than to negotiate at offer time (an internal promotion takes 1-2 years; a job change for a level bump is faster). Aiming wrong costs you: aim too high and you fail the loop; aim too low and you leave a band of comp and scope on the table and spend years climbing back. The goal is to interview at the level your *current scope* justifies — usually lateral, sometimes one stretch level up.

## The Universal Ladder (Conceptual)

Strip away company names and the levels mean the same thing:

| Tier | Scope | Typical IC behaviors |
|---|---|---|
| Mid (L3-L4) | A sub-component | Executes well-defined work independently |
| **Senior (L5)** | Owns features/services | Independent; mentors; the industry "anchor" level |
| **Staff (L6)** | Cross-team | Drives technical strategy across teams; force-multiplier |
| Senior Staff / Principal (L7-L8) | Org-wide | Sets direction for an org; recognized expert |
| Distinguished (L9+) | Industry-level | Rare; shapes the field |

Senior (L5) is the level most candidates target and most interviews calibrate against. The jump from Senior to Staff is the hardest in the industry because it shifts from "ships great work" to "makes other teams more effective" — a *scope* change, not a skill increment.

## The Company Ladders

These map to the conceptual tiers above. Titles vary; the tier is what matters when comparing.

### Google
- L3: SWE II · L4: SWE III · **L5: Senior SWE** · **L6: Staff SWE** · L7: Senior Staff · L8: Principal · L9: Distinguished · L10: Google Fellow

### Meta
- E3-E4: SWE · **E5: Senior** · **E6: Staff** · E7: Senior Staff · E8: Principal · E9: Distinguished

### Amazon
- L4: SDE I · **L5: SDE II** · **L6: Senior SDE** · L7: Principal SDE · L8: Senior Principal · L10: Distinguished
- Note: Amazon's L6 is "Senior," and L7 ("Principal") is a bigger jump than the L6→L7 at Google. An Amazon L6 ≈ Google/Meta Senior-to-Staff boundary — calibrate carefully.

### Apple
- ICT2: Engineer · ICT3: Senior · **ICT4: Staff-equivalent (common senior target)** · ICT5: Senior Staff · ICT6: Principal
- Apple downplays titles internally; comp and scope vary widely by org at the same ICT.

### Microsoft
- 59-60: SWE · **61-62: Senior SWE** · 63-64: Principal · 65-67: Partner · 68+: Technical Fellow
- Microsoft reaches the "Principal" *title* earlier than Amazon reaches L7; a Microsoft 63 is **not** an Amazon L7. Translate by scope, not title.

### Netflix
- Flat ladder: **Senior** → Senior Staff → Principal. Netflix hires senior-only and pays top-of-market in mostly cash (see [C05/T06](../C05/T06-Netflix.md)).

## Translating Between Ladders

The trap is comparing *titles*. "Principal" means org-wide strategy at Amazon (L7) but is reached two title-steps earlier at Microsoft (63). Always translate to the **conceptual tier by scope**:

```
Senior  ≈ Google L5 ≈ Meta E5 ≈ Amazon L5 ≈ Apple ICT4 ≈ MSFT 62
Staff   ≈ Google L6 ≈ Meta E6 ≈ Amazon L6 ≈ Apple ICT5 ≈ MSFT 63-64*
```
(*Microsoft bands are wide; verify with levels.fyi for the specific role.)

When weighing two offers, compare the *scope and comp band*, not the word on the business card.

## Compensation by Tier (Approximate)

Rough US total-comp ranges; vary heavily by company, location, and year — verify against levels.fyi:

| Tier | Approx total comp |
|---|---|
| Senior (L5/E5) | $300K-550K |
| Staff (L6/E6) | $500K-900K |
| Senior Staff (L7/E7) | $700K-1.5M |
| Principal (L8/E8) | $1M+ |

The cross-tier jumps are large — another reason level negotiation ([C06/T02](../C06/T02-Level-Negotiation.md)) is worth real effort.

## Targeting Your Level

- **Lateral** (same tier as today): the safe default; you know you can do the job.
- **One stretch up:** reasonable if your current scope already brushes the next tier (you're a Senior doing cross-team work → aim Staff).
- **Two levels up:** unusual and risky; the loop will expose the gap.

If the loop suggests you're between levels, you may be **down-leveled** ("we'd offer L5, not L6"). Decide in advance: accept as a foot in the door and promote internally, negotiate with evidence of higher scope ([C06/T02](../C06/T02-Level-Negotiation.md)), or decline and try elsewhere.

## DevOps / SRE Specifics

- SRE and DevOps usually follow the **same IC ladder** as SWE (Google L5 SRE = Google L5 SWE in band).
- A few companies run a **distinct SRE ladder or job family** (historically Google SRE), but the leveling tiers and comp bands track the SWE ones closely.
- Your scope evidence is operational: incidents led, reliability moved, platforms built, teams unblocked — frame it in those terms when arguing your level.

## Best Practices

- Research the target company's level expectations and map them to your scope.
- Self-assess honestly against the *next* tier's behaviors before aiming there.
- Translate offers by scope and band, never by title.
- Prepare scope evidence (cross-team impact, platforms, incidents) to justify your level.
- Decide your down-level response before the offer call.

## Common Mistakes

- Comparing titles across companies instead of scope/band (e.g. MSFT Principal vs Amazon L7).
- Aiming two levels up and failing the loop.
- Aiming too low and under-earning for years.
- Not knowing your target level going in, so you can't argue for it.
- Treating SRE as a separate, lower track when it's usually the SWE band.

## Quick Refs

```
Senior (L5): independent, owns features — the anchor level
Staff  (L6): cross-team force-multiplier — the hard jump
L7+:        org-wide strategy / principal
Translate by SCOPE, not title (MSFT 63 ≠ Amazon L7)
Target:     lateral safe | one stretch ok | two up risky
Down-level: decide accept vs negotiate vs decline in advance
```

## Interview Prep

**Junior**: "What level should I target?" — Lateral to my current tier is the safe default, since I know I can do that job. I aim one level up only if my current scope already brushes the next tier — and I go in knowing my target level so I can argue for it rather than accepting whatever the loop assigns.

**Mid**: "How do you compare a Microsoft and an Amazon offer at the same title?" — By scope and comp band, not the title word. Microsoft reaches the 'Principal' title earlier than Amazon reaches L7, so a Microsoft 63 isn't an Amazon L7. I map both to the conceptual tier and check the actual bands on levels.fyi.

**Senior**: "Why is the Senior-to-Staff jump the hard one?" — Because it's a scope change, not a skill increment: Senior means I ship great work independently; Staff means I make *other teams* more effective. To target Staff I bring evidence of cross-team impact — a platform others adopted, an incident pattern I eliminated org-wide — not just a longer list of things I personally built.

**Staff**: "They want to down-level you — how do you respond?" — I decided my floor before the call. If my scope evidence genuinely supports the higher level I push back with specifics — cross-org influence, strategy I set — and I'm willing to walk. If it's a real gap, I weigh accepting and promoting internally against re-applying at level elsewhere, and I ask exactly what the leveling assessment flagged so I know which it is.

## Next Topic

→ Move to [L29/C02 — Coding for DevOps Roles](../C02/README.md)
