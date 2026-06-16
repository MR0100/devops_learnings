# L19/C03/T04 — Healthy On-Call Practices

## Learning Objectives

- Sustain on-call long-term
- Avoid burnout

## Sustainable

If on-call destroys engineers: not sustainable.

Goals:
- < 25% time on-call
- < 2 pages/shift
- Recovery after
- Continuous improvement

## Page Volume Targets

### Per Shift (Week)
- 0-2 pages: healthy
- 3-5: investigate
- 5+: emergency intervention

### Per Year
- 50-100: healthy
- 200+: dysfunctional

If consistently high: invest in noise reduction.

## Recovery

After a shift, give the engineer time to rest:
- Comp day off
- No urgent deadlines
- Easy work

## Compensation

Compensate on-call to respect the burden it places on people:
- Pay differential (US)
- Comp time (EU)
- Career advancement weight

## Schedule

Keep the schedule predictable so engineers can protect family and personal life:
- Know weeks in advance
- Can plan life
- Vacation considered

## Transitions

At the end of a shift, hand off enough context for continuity:
- Hand-off doc
- Open incidents
- Recent context

## Workload Caps

While on-call, cap the rest of the workload so the engineer can focus on incidents:
- No critical project deadlines
- Reduced 1:1s
- Fewer meetings

## Tools

Equip the on-call engineer so they're ready to respond:
- Mobile app (charged)
- Laptop nearby
- Stable network (or hotspot)
- VPN ready
- Credentials accessible

## Mental Health

Support mental health for engineers carrying a heavy load:
- Therapy access
- EAP programs
- Sabbatical for high-load

## Burnout Symptoms

Watch for these burnout symptoms so you can intervene early:
- Cynicism
- Detachment
- Constant fatigue
- "It's just always broken"
- Quitting

## Manager Role

The manager's job is to protect the team:
- Cap volume
- Hear complaints
- Push back if unsustainable
- Invest in fix
- Compensate

## Postmortems

After a bad shift or page, hold a postmortem to drive continuous improvement:
- Discuss
- Action items
- Improve

## Wellness Check-ins

Run a post-shift wellness check-in to catch problems before they fester:
- "How was your shift?"
- "What was tough?"
- "What can we improve?"

## Hand-Off

```
Outgoing: 
  Open: incident-1234 (mitigation ongoing)
  Recent: 3 pages this week
  Followups: postmortem due tomorrow
Incoming:
  Acknowledged
  Asked questions
```

A clear hand-off makes the transition between shifts smooth.

## On-Call Improvement

Treat on-call improvement as a project so it gets better over time:
- Top 5 noise sources
- Quarterly review
- Action items
- Track over time

## Severity Discipline

Don't page for:
- Warnings (ticket)
- Disk 85% (warn)
- Single transient

Reserve a page for real signal rather than noise:
- User-facing impact
- Multi-event
- Sustained

## Auto-Resolve

```
If alert resolves in 5 min auto:
  Don't page after window
```

This filters out transient blips that self-heal before anyone needs to act.

## Quiet Hours

Some teams apply different severity rules at night to keep on-call sustainable:
- Severity rules different at night
- Warning → wait for morning

## On-Call Salary

Reflect on-call in pay as a form of economic respect:
- Pay band considers on-call
- Bonus for difficult years
- Career growth credit

## Lateral Move

If on-call causes burnout, offer a lateral move for career sustainability:
- Move to non-on-call role
- Different service
- Step back

## Sabbatical

After several years, a sabbatical aids long-term retention:
- 1-3 month break
- Recharge
- Return refreshed

## Sign of Health

These are the indicators of a healthy on-call program:
- Engineers volunteer for on-call
- New hires excited (not afraid)
- Retention high
- Pages low

## Sign of Issues

These signs mean on-call is broken and you need to act:
- People quit citing on-call
- Trade for any other shift
- "I can't do another year"
- High frequency complaints

## Best Practices

- Cap volume
- Compensation
- Recovery
- Predictable schedule
- Tooling
- Manager support
- Wellness focus

## Common Mistakes

- 2-person rotation (death)
- No comp
- Frequent pages tolerated
- No recovery
- Manager dismissive

## Quick Refs

```
Target:
  < 25% time on-call
  < 2 pages/shift
  Comp post-shift
  Predictable schedule
  Mobile-ready

Burnout:
  Cap volume
  Talk to manager
  Improve alerts
  Take breaks
```

## Interview Prep

**Junior**: "What does healthy on-call look like?" — Under ~2 pages per shift, on-call taking under ~25% of an engineer's time, recovery time after a shift, and a predictable schedule known weeks in advance so people can plan their lives.

**Mid**: "What page volumes signal trouble?" — Per shift, 0–2 pages is healthy, 3–5 warrants investigation, and 5+ is an emergency; per year, 50–100 is healthy and 200+ is dysfunctional, and consistently high numbers mean you must invest in noise reduction rather than tolerate it.

**Senior**: "How do you prevent on-call burnout?" — Cap page volume and enforce severity discipline (page only on sustained user impact, ticket the rest), compensate the burden with comp time or pay differential, guarantee recovery and reduced workload during/after shifts, and watch for early burnout signals like cynicism and "it's just always broken."

**Staff**: "How do you build a healthy on-call culture across an org?" — Make the manager accountable for capping volume and pushing back when on-call is unsustainable, treat on-call improvement as a tracked project with quarterly reviews of the top noise sources, run post-shift wellness check-ins, and measure health by leading indicators — engineers volunteering for on-call and high retention rather than people quitting over the pager.

## Next Topic

→ Move to [L19/C04 — Incident Management](../C04/README.md)
