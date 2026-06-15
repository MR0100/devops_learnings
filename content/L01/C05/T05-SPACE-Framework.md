# L01/C05/T05 — SPACE Framework for Developer Productivity

## Learning Objectives

- Define the SPACE framework and its 5 dimensions
- Use SPACE as a counterweight to DORA metric obsession
- Apply SPACE to diagnose developer experience issues

## Origin

Authored by Nicole Forsgren (DORA), Margaret-Anne Storey, Brian Houck, Chandra Maddila, et al. (2021). Direct response to teams measuring only DORA and missing human-cost / quality dimensions.

## The 5 Dimensions

**S** — Satisfaction & Well-being
**P** — Performance
**A** — Activity
**C** — Communication & Collaboration
**E** — Efficiency & Flow

## Each Dimension Explained

### Satisfaction & Well-being

- Developer satisfaction (NPS)
- Burnout
- Retention
- Feeling of psychological safety
- Tooling satisfaction

### Performance

- Outcome-oriented (quality, customer impact)
- Code quality, defect rate
- Service reliability (SLO compliance)

### Activity

- Number of PRs, commits, code reviews
- Story points completed
- Build counts

> **Warning**: Activity metrics are the easiest to game. Use only with the other dimensions.

### Communication & Collaboration

- Cross-team work
- PR review depth
- Onboarding speed for new engineers
- Knowledge sharing

### Efficiency & Flow

- Interruptions per day
- Flow state hours
- Lead time (overlap with DORA)
- Time spent in meetings

## Why SPACE Complements DORA

| DORA Measures | SPACE Adds |
|---|---|
| System flow | Human cost |
| Delivery performance | Engineer experience |
| What you ship | How it feels to ship |

A team can score "elite" on DORA while burning out. SPACE catches that.

## Common SPACE Measurement Methods

| Dimension | Method |
|---|---|
| Satisfaction | Quarterly survey |
| Performance | DORA + SLO + defect data |
| Activity | PR/commit metrics (with caution) |
| Communication | Survey + cross-team PR counts |
| Efficiency | Survey + calendar analysis |

## Common Mistakes

- **Activity-only programs** — leadership often defaults here; produces gaming
- **Survey fatigue** — quarterly cap, not monthly
- **Per-engineer scoring** — destroys psychological safety; aggregate at team level
- **Goodhart's Law** — any single metric becomes a target

## Putting It Together: DORA + SPACE

A balanced team scorecard:

| Metric | Source | Why |
|---|---|---|
| Deploy Frequency | DORA | Flow |
| Lead Time (p50, p90) | DORA | Flow + outliers |
| Change Failure Rate | DORA | Quality |
| MTTR | DORA | Recovery |
| Engineer NPS | SPACE | Human cost |
| Onboarding time | SPACE | Efficiency / Communication |
| Time in flow / hours uninterrupted | SPACE | Efficiency |
| Burnout signals (sick days, PTO usage) | SPACE | Satisfaction |

## Best Practices

- **Pick metrics across multiple dimensions** — at least one from a *perception* dimension (Satisfaction) plus an objective one; never report Activity alone.
- **Aggregate at the team level** — SPACE is for understanding systems, not ranking individuals; per-engineer scores destroy the trust the data depends on.
- **Pair every objective metric with a perceptual one** — e.g., PR throughput (Activity) next to "I can ship without friction" (Satisfaction) to catch gaming.
- **Survey on a sustainable cadence** — quarterly, with a stable instrument, so trends are comparable and fatigue stays low.
- **Use SPACE to interpret DORA, not replace it** — when DORA improves but Satisfaction drops, you've bought flow with burnout; act on it.

## Quick Refs

**SPACE dimensions (the acronym)**

| Letter | Dimension | Example signal |
|---|---|---|
| **S** | Satisfaction & well-being | Engineer NPS, burnout indicators |
| **P** | Performance | Outcomes/quality (e.g., reliability) |
| **A** | Activity | PRs, commits, deploys |
| **C** | Communication & collaboration | Review latency, onboarding time |
| **E** | Efficiency & flow | Uninterrupted focus time, handoff count |

**Rules of thumb**: choose ≥3 dimensions · always include a perception metric · aggregate per *team* · cap surveys at quarterly · DORA measures flow, SPACE measures the humans producing it — report both.

## Interview Prep

**Senior**: "What is the SPACE framework and why was it created?"

**Staff**: "Critique a team that reports only DORA metrics."

**Principal**: "Design a metrics program for an org of 1000 engineers that captures both delivery and engineer experience."

## Next Chapter

→ [C06 — Common Misconceptions & Anti-Patterns](../C06/README.md)
