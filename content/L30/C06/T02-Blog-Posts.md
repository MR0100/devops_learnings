# L30/C06/T02 — Blog Posts as Proof of Depth

## Learning Objectives

- Write technical blogs
- Show depth

## Why

- Demonstrate writing
- Teach (proves understanding)
- SEO (recruiters find)
- Build personal brand

### The Deeper Reason: Writing Is the Senior+ Skill

For senior and staff roles, the job is increasingly *influence at distance* —
design docs, RFCs, postmortems, proposals that move teams you're not in the room
with. A technical blog post is the public, durable proof you can do that:
explain a hard system clearly to people who weren't there. It also forces real
understanding — you cannot write a credible "how we cut Prometheus cardinality
by 70%" post without actually understanding cardinality. The act of writing *is*
the depth check.

And it compounds. Unlike an interview answer that evaporates, a post keeps
working: it gets found by recruiters via search, seeds a conference talk
(C06/T03), gives an interviewer something concrete to ask about, and links back
to the capstone repo. One good post is reused many times.

### Trade-offs to Manage

- **Depth vs. cadence** — one substantial, specific post a quarter beats weekly
  shallow ones. Quality is the brand; volume of "intro to X" posts is noise.
- **Specific vs. safe** — concrete numbers and real failures ("we had a 3-hour
  outage, here's the root cause") land far harder than generic best-practice
  posts, but require you to have actually done the thing. Write from real
  experience, sanitized as needed.

## Topics

- How you built project X
- Lessons from incident
- Deep dive on tech
- Tutorial
- Opinion piece

## Format

```markdown
# Title

## Problem
What you faced.

## Approach
What you tried.

## Solution
What worked.

## Code
Examples.

## Lessons
Reflection.

## Resources
Further reading.
```

## Platforms

- Personal blog (GitHub Pages, Medium)
- Dev.to
- Hashnode
- Substack
- Company tech blog (if allowed)

## Quality

- Clear writing
- Edit
- Diagrams
- Code samples
- Citations

## Depth

For senior+ readers:
- Not "Hello World"
- Trade-offs discussed
- Real numbers
- Production lessons

## Examples

### "How we cut Kafka costs by 60%"
Real numbers, approach, lessons.

### "Debugging a memory leak across services"
Deep dive technical.

### "Migrating from x to y: pros and cons"
Trade-offs.

### "SLO-based alerting for our payment service"
Specific, production-relevant.

## Frequency

- 1 post/month = strong
- More: better
- Quality > quantity

## Promotion

- LinkedIn share
- Twitter/X
- Hacker News (high-quality)
- Reddit / r/devops

## Best Practices

- Real content
- Depth
- Visuals
- Regular cadence
- Engage in comments

## Common Mistakes

- Shallow ("intro to K8s")
- No real-world
- Stale (no recent posts)
- Errors not edited

## Quick Refs

```
Why: writing = the senior+ influence skill; compounds (post → talk → CFP → repo)
Format: Problem → Approach → Solution → Lessons
Frequency: 1 substantial post/quarter > weekly shallow
Land: specific + real numbers + real failures > generic best-practice
Platforms: own blog (control) + Medium/Hashnode (reach) + LinkedIn/Twitter share
```

## Interview Prep

**Junior**: "Why write technical blog posts?" — They prove you understand
something well enough to explain it, demonstrate communication skill, and help
people (recruiters, peers) find you. Teaching a topic is one of the best ways to
show you actually know it.

**Mid**: "What makes a technical post worth reading?" — Specificity. A post grounded
in real experience — concrete numbers, a real problem you hit, what you tried,
what broke, what you'd do differently — beats generic advice every time. Code
samples, a diagram, and tight editing matter, but the core is that it's a real
story, not a rephrased tutorial.

**Senior**: "How does writing fit into building a senior-level reputation?" — At
senior+ the job is influence beyond your immediate team — design docs, RFCs,
postmortems — and a public blog is the visible proof you can do that: take a hard
system and make it clear to people who weren't there. It also compounds: a post
becomes a conference talk, gives interviewers something concrete to dig into, and
links back to the capstone that inspired it. I'd write from real production
experience, pick depth over cadence (one strong quarterly post over weekly
filler), and concentrate on the 1–2 topics I want to be known for so the body of
work reads as expertise, not a scattered feed.

**Staff**: "How do you use writing strategically, not just as a personal-brand
checkbox?" — Strategically, writing is a leverage tool: the same clear-explanation
muscle that makes a good blog post makes the design docs and proposals that move
an org. So I'd treat external writing and internal influence as the same skill,
practiced in public. I'd be deliberate about owning a narrative in 1–2 areas — say,
'observability cost at scale' — and build a through-line: the capstone repo, a
deep-dive post with real numbers, a conference talk, and the internal RFC that
applied it, all reinforcing each other. The point isn't volume or vanity metrics;
it's that when people in my domain think about that problem, my work is part of
the conversation — which is exactly what staff-level 'known in your domain'
means. And I'd keep it honest: claim 'we' for team work, be specific enough that
it's clearly earned, because at this level credibility is the whole asset.

## Next Topic

→ [T03 — Conference Talks / Lightning Talks](T03-Conference-Talks.md)
