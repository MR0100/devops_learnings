# L29/C01/T02 — Tech Phone Screen

## Learning Objectives

- Pass the tech phone screen as the gate to the onsite loop
- Know what each question type signals and how it's scored
- Communicate under time pressure on a shared editor with no IDE help

## Where It Sits in the Funnel

The recruiter screen confirms interest, level, and comp range. The tech phone screen is the first round where an **engineer**, not a recruiter, votes on your output. It is a filter, not the loop: companies use it to avoid spending 5-6 onsite slots on someone who can't write a clean function. One interviewer, one signal — but a "No Hire" here usually ends the process.

Most are conducted over CoderPad, HackerRank, Google Docs, or a company tool with **no autocomplete, no compiler, and no test runner**. Practice in a plain editor before the real thing, not in your IDE.

## Format

45-60 minutes, tightly run:

| Segment | Time | What's happening |
|---|---|---|
| Intro / rapport | 5 min | Brief background; do not over-talk |
| Technical problem(s) | 35-45 min | 1-2 problems; the entire signal lives here |
| Your questions | 5-10 min | Scored loosely; ask something real |

The interviewer is often writing notes while you talk. Long silences read as "stuck." Keep a narration going.

## Question Types (DevOps / SRE)

DevOps and SRE screens skew away from pure algorithm puzzles toward **systems-flavored** problems. Expect one of these:

### Coding (DSA)
LeetCode easy-to-medium: hash maps, two pointers, BFS/DFS, intervals, string parsing. Rarely hard. They want clean, correct, tested code — not the optimal trick.

> *Parse a log file and return the top-K endpoints by request count.* (Hash map + heap; classic SRE-flavored version of "top K frequent.")

### Linux / Systems
Debug-a-script or reason-about-a-box problems:

> *A box shows 100% CPU but `top` shows no process above 5%. Where do you look?* (kernel/iowait/steal time, `top` showing %wa, interrupts, `vmstat`, `iostat`.)

> *Here's a Bash script that's supposed to rotate logs; it deletes the wrong files. Find the bug.* (Quoting, glob expansion, `find -mtime` off-by-one.)

### Mini System Design
A 20-30 min scoped design, not the full 60-min onsite version:

> *Design a service that health-checks 10,000 hosts every 30 seconds.* (Fan-out, batching, timeouts, where state lives, what happens when a checker dies.)

### Conceptual Deep Dive
"Walk me through what happens when…" — they probe how deep your mental model goes:

> *Walk through what happens when you run `kubectl apply -f deploy.yaml`.* (kubectl → API server auth/admission → etcd write → controller reconcile → scheduler → kubelet → CRI → CNI → readiness probe.)

> *What happens, end to end, when you type a URL and hit enter?* (DNS, TCP/TLS handshake, HTTP, load balancer, TLS termination, app, response.)

## Sample Q&A

**Q: "Why did the screen-share editor not auto-close my bracket?"** Don't ask this. Treat the editor as dumb and write balanced syntax yourself; fumbling with tooling burns time and signal.

**Q (interviewer): "Can you make it faster?"** This means your current solution has a worse complexity than they want. State your current Big-O out loud, name the bottleneck, then propose the better structure ("the nested loop is O(n²); a hash set makes the lookup O(1), so O(n) total").

**Q (interviewer): "What's the edge case here?"** Always have an answer ready: empty input, single element, duplicates, integer overflow, very large input, concurrent access. Naming these unprompted is a strong-hire signal.

## Scoring: What the Interviewer Writes Down

- Did they reach a working solution? (Correctness is table stakes.)
- Is the code clean — good names, no dead branches, handles edge cases?
- Did they communicate the plan *before* coding?
- Did they test it themselves by tracing an example?
- Did they take hints gracefully, or argue?

A partial solution with great communication often beats a silent full solution.

## Prep

- Grind LeetCode **medium** until easy problems are reflex; you want spare cognitive budget for talking.
- Drill the systems canon: `kubectl apply` flow, URL-to-render, TCP handshake, DNS resolution, how a load balancer picks a backend.
- Memorize latency numbers (L1/RAM/SSD/disk/network) so design answers are concrete.
- Do 3-5 **mock interviews out loud** with a timer; solo practice does not train the narration muscle.
- Pre-write 2-3 thoughtful closing questions about the team's on-call, tooling, or roadmap.

## Communication

- Restate the problem and confirm assumptions before writing anything.
- Ask clarifying questions: input size, format, constraints, expected output.
- Narrate your approach, then code; do not code in silence.
- Walk through a concrete example to test your own code at the end.
- Call out edge cases explicitly.

## Common Mistakes

- Silent thinking — the interviewer can't score what they can't hear.
- Jumping straight to code without stating the plan.
- Never running an example through the finished code.
- Missing obvious edge cases (empty, null, duplicates, overflow).
- Arguing with a hint instead of incorporating it.
- Burning 10 minutes over-explaining your background in the intro.

## Best Practices

- Do mock interviews on a plain editor, not your IDE.
- Think out loud continuously; pause-narrate even while stuck.
- State Big-O before and after optimizing.
- Test with at least one worked example before saying "done."
- Treat the screen as collaborative — the interviewer is a future colleague, not an examiner.

## Quick Refs

```
Time:    45-60 min (5 intro / 35-45 tech / 5-10 questions)
Types:   coding (easy-med) | linux/systems | mini design | conceptual
Editor:  plain (no autocomplete/compiler) — practice that way
Signal:  correct + clean + communicated + tested
Comm:    restate → clarify → plan → code → test
Outcome: recruiter follows up 1-7 days; pass → onsite
```

## Interview Prep

**Junior**: "I restate the problem, confirm input size and constraints, then code the straightforward solution and trace an example to verify it before saying I'm done."

**Mid**: "I narrate a plan first, state the Big-O, then code — and when asked to optimize I name the bottleneck explicitly before swapping in the better data structure."

**Senior**: "For a systems screen I treat 'walk me through `kubectl apply`' as a depth probe and go layer by layer — kubectl auth, API server admission, etcd, controller reconcile, kubelet, CNI — pausing to let them steer."

**Staff**: "I drive the screen like a design review: scope the problem, surface the failure modes and trade-offs unprompted, and frame the solution around what I'd actually run in production, not just what passes the test."

## Next Topic

→ [T03 — Onsite Loop (Coding, System Design, Behavioral)](T03-Onsite-Loop.md)
