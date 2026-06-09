# L26/C01 — FinOps Principles

## Topics

- **T01 The FinOps Foundation Framework** — Inform/Optimize/Operate
- **T02 Inform, Optimize, Operate Phases** — Implementation stages

## What FinOps Is

> Financial Operations: a discipline combining engineering + finance + business to manage cloud spend.

Goal: maximize business value per cloud dollar.

Not just "cost cutting." Tradeoffs:
- Speed vs cost
- Reliability vs cost
- Innovation vs cost

## The FinOps Foundation Framework

### Three Phases

#### Inform
- **Visibility**: see what you spend
- **Allocation**: attribute spend to teams/products
- **Benchmarking**: compare to peers and budget
- **Forecasting**: predict next month/quarter

#### Optimize
- **Right-sizing**: match resources to actual usage
- **Pricing**: commit when stable (RIs, Savings Plans)
- **Architecture**: change designs for cheaper alternatives
- **Waste reduction**: kill unused resources

#### Operate
- **Continuous improvement**: monthly reviews
- **Governance**: policies + alerting
- **Education**: engineers understand cost impact
- **Automation**: anomaly detection, auto-stop

## Six Principles (FinOps Foundation)

1. **Teams need to collaborate** (eng + finance + product + leadership)
2. **Decisions are driven by business value** (not just cost)
3. **Everyone takes ownership** (engineers responsible for their costs)
4. **FinOps data is accessible + timely** (delays hurt)
5. **A centralized team drives FinOps** (cross-functional core)
6. **Take advantage of the variable cost model** (cloud economics)

## FinOps Maturity Model

### Crawl
- Some cost visibility
- Ad-hoc optimization
- No clear ownership
- Surprise bills

### Walk
- Per-team cost allocation
- Regular reviews
- Commitment-based pricing
- Cost-aware architecture decisions

### Run
- Real-time cost visibility
- Per-feature/product cost
- Engineering KPIs include cost
- Continuous optimization automation
- Showback/chargeback

## Who Does FinOps

- **FinOps Engineer / Analyst** — tooling + reports
- **Engineers** — own their service's cost
- **Finance** — budget alignment, accruals
- **Leadership** — sets policy, rewards

A small dedicated team (1-5 FTEs) plus distributed engineer responsibility scales.

## Common FinOps Anti-Patterns

- **Cost as engineering team's only KPI** — they cut corners on reliability
- **Surprise budget cuts** — without data
- **Finance dictating tech choices** — without understanding tradeoffs
- **Engineering ignoring cost** — until forced
- **No cost data in dev workflow** — engineers can't decide
- **All-on-demand pricing** at scale — pure waste

## When to Start

- Cloud bill >$1M/year — definitely
- Growth >20% MoM — proactive
- Surprise bills hitting CFO — reactive
- Pre-IPO — investors will ask

## ROI of FinOps Practice

Typical:
- 15-40% savings in year 1
- 5-15% ongoing in subsequent years
- Investment: ~1-2 FTEs + tooling

Pays for itself many times over for any org spending >$1M/year on cloud.

## Tools

### Cloud-Native (Free)
- AWS Cost Explorer, Budgets
- GCP Cost Reports
- Azure Cost Management

### Commercial
- Vantage
- Cloudability (Apptio)
- CloudCheckr (NetApp)
- Densify (right-sizing)
- Spot.io (commitments)
- Apptio Cloudability

### OSS / DIY
- Steampipe + Athena queries on CUR (Cost and Usage Report)
- CUDOS dashboards (AWS reference)
- Kubecost / OpenCost for K8s

## Reporting Cadence

- **Daily**: anomaly detection alerts
- **Weekly**: team-level review
- **Monthly**: cross-team review + plan
- **Quarterly**: budget vs actual + forecasting

## Interview Themes

- "What's FinOps?"
- "Three phases — explain"
- "FinOps maturity — where is your team?"
- "Build a FinOps program"
- "ROI calculation"
