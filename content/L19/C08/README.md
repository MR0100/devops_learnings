# L19/C08 — Production Readiness

## Topics

- **T01 PRR Checklist** — Production Readiness Review
- **T02 Launch Reviews** — Pre-launch sign-off
- **T03 Quarterly Service Reviews** — Ongoing health checks

## Production Readiness Review (PRR)

Before a new service goes to production (or is handed to SRE), a PRR ensures it meets minimum bar.

### Why
- Prevent unreliable services from causing pages
- Force teams to invest in observability up front
- Document expectations

### The Checklist

#### Architecture
- [ ] Diagram of services + dependencies
- [ ] Failure modes documented
- [ ] Multi-AZ deployment (or justified single-AZ)
- [ ] Multi-region story (or justified single-region)
- [ ] Stateless tier separated from stateful
- [ ] Idempotency for writes

#### Observability
- [ ] Metrics exposed (RED method minimum)
- [ ] Logs structured + shipped to central log store
- [ ] Traces emitted with proper trace context
- [ ] Custom dashboards in Grafana / DD
- [ ] Alerts with runbooks; SLO-based not threshold
- [ ] On-call rotation defined
- [ ] PagerDuty schedule + escalation
- [ ] Status page integration

#### Reliability
- [ ] SLO defined and agreed
- [ ] Error budget policy documented
- [ ] Auto-scaling configured (HPA, CA / Karpenter)
- [ ] PDBs for critical workloads
- [ ] Topology spread across AZs
- [ ] Resource requests/limits sane
- [ ] Health probes (liveness, readiness, startup)
- [ ] Graceful shutdown (terminationGracePeriodSeconds, preStop hooks)
- [ ] Load tested at 2× projected peak
- [ ] Chaos tested for key failure modes

#### Security
- [ ] Pod Security Standards: restricted
- [ ] Non-root user
- [ ] Read-only root filesystem where possible
- [ ] NetworkPolicy default-deny + explicit allow
- [ ] Secrets via External Secrets / Vault (not in env)
- [ ] Image signed (Cosign) + scanned
- [ ] mTLS where applicable
- [ ] IAM least privilege

#### Operations
- [ ] CI/CD via GitOps (no manual kubectl apply)
- [ ] Rollback tested
- [ ] Runbooks for top 5 incident types
- [ ] DR plan + restore tested
- [ ] Cost projection
- [ ] Capacity plan for next 90 days

#### Documentation
- [ ] Service catalog entry (Backstage)
- [ ] On-call documentation
- [ ] Architecture decision records
- [ ] Migration / launch plan

## Launch Reviews

Specific to a launch event (vs ongoing PRR):
- Marketing + Eng aligned on date
- Capacity provisioned for expected traffic
- Rollback plan exists
- Status page templates ready
- Support team trained
- War room scheduled for first 2-4 hours

## Quarterly Service Reviews

Every quarter, per service, ask:
- SLO compliance over last quarter?
- Top 5 alerts that fired?
- Time spent on toil vs engineering?
- Outstanding action items?
- Capacity headroom?
- Cost trend?
- Tech debt items?

Output: 1-page summary; gaps become action items.

## SRE's "Can Refuse to Operate"

If a service fails PRR:
- SRE can refuse to operate it
- Or operate with reservations (page dev team, not SRE)
- Or accept with a remediation plan

This is the lever that drives dev teams to invest in operability.

Without this authority, "SRE adoption" doesn't happen — devs throw services over the wall.

## Anti-Patterns

- PRR as a one-time gate (it should be ongoing)
- PRR with no consequences (rubber stamp)
- PRR conducted in a vacuum (without dev team)
- PRR that's too long (people gaming, skipping)
- No re-review when service grows or changes architecture

## Sample PRR Process

1. Service team requests PRR (4 weeks before launch)
2. SRE reviews architecture, asks questions
3. Joint workshop on observability + reliability
4. Gap identification → action items
5. Team addresses gaps
6. SRE re-verifies (1 week before launch)
7. Sign-off (or deferral)
8. Post-launch retro at 30 days

## Interview Themes

- "PRR — what's on the checklist?"
- "SRE refuse to operate — why important?"
- "Launch review vs PRR"
- "Quarterly review — what does it surface?"
- "Anti-patterns in PRR"
