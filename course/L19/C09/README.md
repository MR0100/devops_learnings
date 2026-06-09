# L19/C09 — SRE Leadership at FAANGM

## Topics

- **T01 SRE Org Structures (Embedded vs Central)** — Who works where
- **T02 Influence Without Authority** — How staff SREs operate
- **T03 The Staff SRE Role** — Beyond IC work

## SRE Org Structures

### Embedded
- SREs sit within product teams
- One SRE per ~5-10 product engineers
- Pros: Close to the product; deep context
- Cons: Dispersed; SRE community weak; can drift to operations role

### Central
- One SRE team owns shared platform/services
- Product teams self-serve
- Pros: Strong SRE community; reusable platform
- Cons: Less context for each service; bottleneck

### Hybrid (Google's model)
- Central SRE team
- Embedded SREs assigned to high-priority products
- SREs can rotate
- Strong cross-team SRE practice

### Federation
- Per-domain SRE teams (Payments SRE, Search SRE)
- Connected via a Steering Group
- Best for large orgs (500+ engineers)

## Choosing Structure

| Org size | Structure |
|---|---|
| < 30 engineers | DevOps engineer (no formal SRE) |
| 30-100 | Central SRE team (small) |
| 100-300 | Central + embedded for top services |
| 300+ | Federated (per-domain) + central core |

## Influence Without Authority

A staff SRE doesn't have direct authority over product team decisions. They influence through:

### Data
- "Your service's SLO has been below target for 3 consecutive quarters"
- "Toil from this service is 60% of your on-call shift"
- "Cost of this service grew 200% YoY"

Hard to argue with numbers.

### Standards
- Production Readiness Reviews (gates)
- Platform requirements (standardized monitoring, etc.)
- Compliance requirements (SOC2, etc.)

If you set the standard, you set the bar.

### Story
- "Last incident cost $X and Y hours; here's how to prevent"
- Postmortems shared widely
- "Customer A was about to leave because of these issues"

Narratives stick.

### Reciprocity
- Help teams when they need it; they help you when you need it
- "I'll add this dashboard if you adopt the SLO"
- Quid pro quo without being transactional

### Sponsorship
- Find a VP/Director who champions SRE
- Their authority backs your guidance
- Cultivate them carefully

## The Staff SRE Role

Beyond IC contributions:
- **Setting direction**: 2-year SRE roadmap
- **Cross-team initiatives**: drive a fleet-wide migration
- **Mentoring**: bring up juniors and mid-level SREs
- **Hiring**: shape what SRE looks like at the company
- **External voice**: conference talks, write-ups, OSS contributions
- **Sponsor's sponsor**: build relationships at VP+ level

### Typical Year of a Staff SRE
- Q1: Identify top 3 reliability bets for the year
- Q1-Q2: Drive one of them to completion
- Q3: Hand off; start the next
- Q4: Review; plan next year

### Pillars
1. **Technical Excellence** — depth in core systems
2. **Project Execution** — deliver multi-quarter initiatives
3. **Cross-functional Influence** — partner with PMs, designers, leadership
4. **Direction Setting** — establish SRE strategy
5. **Cross-team Communication** — bridge between teams + leadership

## Principal SRE

Above Staff. Multi-year strategy. Multi-team architecture. Industry influence.

Examples of Principal SRE work:
- Designed Google Borg's reliability model
- Wrote SRE Book chapter on Capacity Planning
- Led migration of all internal services to Spanner
- Defined company-wide error budget policy

## Career Path

```
SRE I → SRE II → Senior SRE → Staff SRE → Senior Staff SRE → Principal SRE
                                ↓
                              Sometimes: SRE Manager (leadership track)
```

IC track is real and valued at FAANGM. You don't have to manage to advance.

## SRE Anti-Patterns at the Org Level

- **SRE as ticket queue**: support for product teams' incidents (not engineering)
- **SRE with no authority**: can't push back; becomes Ops
- **One SRE team for all** at scale: bottleneck
- **No central practice**: every team reinvents
- **Manager track only**: top ICs leave

## Interview Themes

- "Compare embedded and central SRE structures"
- "Influence without authority — example"
- "What does a Staff SRE do that an SRE doesn't?"
- "How do you build SRE practice in a company that has none?"
- "Career path SRE → Principal SRE"
