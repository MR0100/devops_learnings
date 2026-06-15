# L29/C02/T01 — Yes, You Still Need DSA

## Learning Objectives

- Prepare DSA
- Right scope

## Why DSA — Even for DevOps

The most common candidate mistake is assuming DevOps and SRE roles skip the coding loop. They don't. At FAANGM, infra and reliability roles run the *same* coding bar as the SWE rotation — sometimes one fewer DSA round, but never zero. The myth that "I'll only write Terraform" gets strong operators rejected before the onsite.

What the round actually tests is not whether you've memorized LeetCode, but three things: (1) **problem-solving structure** — can you decompose an unfamiliar problem, reach for the right data structure, and reason about complexity; (2) **engineering rigor** — clean, correct, tested code under time pressure; and (3) **calibration** — they're scoring you against every other engineer who solved the same problem, so the bar is relative and consistent. The deeper bet is that someone who can't write a clean BFS also can't write a reliable controller, log pipeline, or internal tool — and at FAANGM, DevOps engineers ship real software.

## Scope — How Much, How Hard

For DevOps and SRE:
- **LeetCode Easy and Medium** are the core; you must solve Mediums comfortably and out loud.
- **Hard** problems are rare and mostly appear at Staff+ or in Google loops; you don't need competitive-programmer speed.
- Most rounds land squarely on **Medium**. The goal is to make Easies reflexive so you have spare cognitive budget to *narrate* while solving a Medium.

## Topics

- Strings
- Arrays / Hash
- Trees / Graphs
- BFS / DFS
- Heaps
- Two pointers
- Sliding window
- Binary search
- Recursion / DP (rare)

## Time

Prep:
- 100-200 problems Medium
- 2-3 months
- 1-2 hours/day

## Strategy

### Pattern-Based
Recognize:
- "Find duplicates" → hash
- "Path in tree" → DFS
- "Shortest" → BFS
- "Top K" → heap

For: faster recognition.

## Practice

LeetCode:
- Easy first (warm)
- Medium core
- Hard occasional

NeetCode roadmap.

Mock interviews:
- Pramp
- interviewing.io

## Pace

For 45-min round:
- 5 min understand
- 5 min approach
- 25 min code
- 5 min test
- 5 min discuss

## Communication

- Talk approach
- Justify choice
- Discuss complexity
- Mention trade-offs

## Optimization

Often:
- Naive first
- Optimized after
- Discuss complexity

## Edge Cases

- Empty input
- Single element
- Duplicates
- Negative
- Large

## Testing

Walk through:
- Trace by hand
- Example
- Find bugs

## Best Practices

- Pattern recognition
- Practice often
- Mock interviews
- Talk through

## Common Mistakes

- Skip prep (think DevOps doesn't need)
- Hard only (med most common)
- No mocks
- Silent coding

## Quick Refs

```
Topics: arrays, strings, trees, graphs, heaps
Time: 2-3 months prep
Patterns: recognize quickly
Mock: practice talking
```

## Interview Prep

**Junior**: "How much DSA do I really need for a DevOps role?" — Enough to solve LeetCode Mediums comfortably and out loud. The rounds are real and scored on the same bar as SWE; "DevOps doesn't need algorithms" is a myth that gets people rejected. I'd target ~100-150 Mediums over 2-3 months and make Easies reflexive.

**Mid**: "How do you approach a problem you've never seen?" — Pattern-match first: 'find duplicates / count' signals a hash map, 'shortest path' signals BFS, 'top-K' signals a heap, 'substring/window' signals sliding window. I state the brute force and its Big-O, name the bottleneck, then propose the pattern that removes it — getting interviewer buy-in before I code.

**Senior**: "What separates a strong coding round from a passing one?" — Communication and edge-case discipline. A partial solution with clear narration, stated complexity, and named edge cases (empty, single, duplicates, overflow, huge input) often beats a silent correct one. I trace a concrete example through my own code before claiming it works, and I take hints gracefully instead of defending a dead approach.

**Staff**: "How do you keep DSA sharp without grinding full-time?" — Maintenance mode: 5 problems a week mixing Mediums with the occasional Hard, plus one mock a month done out loud on a plain editor. At Staff the DSA bar is table stakes, not the differentiator — so I invest the marginal hour in system design and behavioral, where the leveling decision actually gets made, and keep DSA at 'reflex, not rusty.'

## Next Topic

→ [T02 — Focus Areas (Strings, Trees, Graphs, BFS/DFS, Heaps)](T02-Focus-Areas.md)
