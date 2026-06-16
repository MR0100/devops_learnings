# L29/C06/T01 — Compensation Components

## Learning Objectives

- Decompose a FAANGM offer into its real parts and compute true annualized total comp
- Know which levers are flexible (and which aren't) before you negotiate
- Compare offers across companies on a multi-year, apples-to-apples basis

## Why This Matters

The single biggest negotiation mistake is fixating on **base salary**, which at FAANGM is band-capped and the *least* flexible component. The real money — and the real negotiating room — is in equity and sign-on. To negotiate well you first have to read the offer correctly, because a higher headline number can be worth less than a lower one once vesting schedules and refreshers are accounted for.

## The Five Components

| Component | What it is | Flexibility |
|---|---|---|
| **Base** | Annual cash salary | Low — band-capped |
| **Bonus** | % of base, often performance-multiplied | Low — formula-driven |
| **RSUs** | Equity granted over a vesting period (usually 4 yr) | **Medium-high** — the biggest lever |
| **Sign-on** | One-time cash, often split Y1/Y2 | **High** — most flexible |
| **Refresher** | Annual new RSU grants after you join | Set later by performance |

## Computing Total Comp

The headline "TC" number is an *annualized average* and hides the year-by-year reality. A grant of $400K RSUs over 4 years adds $100K/year *only if it vests evenly*. Model it per year:

```
Year 1 = Base + Bonus + (RSU vested Y1) + Sign-on Y1
Year 2 = Base + Bonus + (RSU vested Y2) + Sign-on Y2
Year 3 = Base + Bonus + (RSU vested Y3)
Year 4 = Base + Bonus + (RSU vested Y4)
Year 5 = Base + Bonus + Refreshers (original grant now exhausted)
```

The year-5 "cliff" matters: once your initial 4-year grant fully vests, your comp depends entirely on **refreshers** accumulated along the way. A company with strong refresher culture sustains comp; one with weak refreshers leaves you facing a drop.

## Vesting Schedules — Read These Carefully

The same dollar grant pays out very differently depending on the schedule:

- **Standard (Google, Meta historically):** 4-year vest, ~even quarterly after a 1-year cliff. Year 1 ≈ headline.
- **Amazon (back-loaded): 5% / 15% / 40% / 40%.** Years 1-2 are far below headline; **sign-on bonuses in Y1 and Y2 bridge the gap.** Without modeling the bridge, an Amazon offer looks deceptively strong or weak depending on which year you anchor on.
- **Netflix:** no multi-year vest at all — high all-cash salary, you choose stock allocation (see [C05/T06](../C05/T06-Netflix.md)).

Always ask for the exact vesting schedule in writing and compute all four years before comparing.

## The Negotiation Levers, Ranked

1. **Sign-on bonus** — the most flexible; recruiters can often add or raise it with little approval. The first thing to push on.
2. **RSU grant** — flexible especially with a competing offer; the highest-dollar lever over time.
3. **Base** — band-capped; small movement, and only within the level's range.
4. **Level** — the largest lever of all but the hardest to move (see [T02](T02-Level-Negotiation.md)); changes every other number.

Negotiate components **separately** — "can we improve the sign-on and the RSU grant?" — rather than asking for "more money" in the abstract.

## Real Numbers (2024-2025 US, Approximate)

Senior (L5 / E5):
- Base: $180-220K · Bonus: 10-20% · RSU: $200-400K / 4 yr · Sign-on: $50-100K
- **Total Y1: ~$300-500K**

Staff (L6 / E6): **Total Y1: ~$500-900K**
Senior Staff (L7 / E7): **Total Y1: ~$700K-1.5M**

These vary widely by company, location, and stock performance — always verify against levels.fyi for the specific role and year (see [T04](T04-Data-Realism.md)).

## Best Practices

- Compute true year-by-year total comp; never compare on headline alone.
- Get the full breakdown and vesting schedule in writing.
- Push sign-on first (most flexible), then RSU (highest dollar), then base.
- Model the year-5 refresher cliff when weighing a long-term move.
- Negotiate each component separately and explicitly.

## Common Mistakes

- Fixating on base, the least flexible component.
- Comparing Amazon's back-loaded offer to an even-vesting one on year-1 numbers.
- Ignoring refreshers and the year-5 cliff.
- Negotiating "more money" vaguely instead of naming components.
- No data to anchor the ask.

## Quick Refs

```
Components: Base + Bonus + RSU + Sign-on + Refresher
TC:         annualized average — model it PER YEAR
Vesting:    even (Google/Meta) | back-loaded 5/15/40/40 (Amazon) | cash (Netflix)
Levers:     sign-on (most flex) > RSU (most $) > base (capped) > level (hardest)
Always:     get it in writing; verify vs levels.fyi; model 4 years
```

## Interview Prep

**Junior**: "What makes up a FAANGM offer?" — Five parts: base, bonus, RSUs vesting over ~four years, a one-time sign-on, and annual refreshers. The mistake is fixating on base, which is band-capped; the real money and the negotiating room are in equity and sign-on.

**Mid**: "How do you compute true total comp?" — Per year, not on the headline. A $400K grant only adds $100K/year if it vests evenly — Amazon back-loads 5/15/40/40, so I model each year and account for the Y1/Y2 sign-on that bridges the thin early years. I also factor the year-5 cliff, when the original grant is exhausted and refreshers carry the comp.

**Senior**: "Which levers do you actually pull?" — Sign-on first — it's the most flexible and recruiters can move it with little approval. Then the RSU grant, which is the biggest dollar lever over time and flexible with a competing offer. Base barely moves since it's band-capped, and I negotiate each component by name rather than asking vaguely for 'more.'

**Staff**: "How do you compare two offers with different vesting?" — I model all four years and risk-adjust. Even-vesting Google/Meta is close to headline in year one; Amazon's back-load makes year one look weak unless I count the sign-on bridge; Netflix is all-cash and fully liquid with no upside. I compare the multi-year, risk-adjusted totals — and weigh refresher culture, since that determines comp past year four — rather than the four headline numbers.

## Next Topic

→ [T02 — Level Negotiation](T02-Level-Negotiation.md)
