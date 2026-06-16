# L29/C02/T05 — Worked Example: Top-K from Logs

## Learning Objectives

- Solve the single most common SRE-flavored coding question end to end
- Choose between a full sort, a heap, and Quickselect — and justify the choice by complexity
- Extend the in-memory answer to log volumes that don't fit in memory

## Why This Problem

"Parse a log file and return the top-K endpoints (or IPs, or error codes) by frequency" is the canonical DevOps coding question. It shows up in phone screens and onsites because it mirrors real work — finding the noisiest client during an incident, the hottest endpoint before a capacity review, the top error after a deploy. It also has a clean optimization story (sort → heap → Quickselect) that lets a strong candidate demonstrate complexity reasoning. Treat it as the "two-sum" of SRE interviews: you should be able to write it cold and discuss three variants.

## The Problem

> Given a stream of access-log lines, return the K most frequent request paths.

Input is a list (or stream) of lines like:

```
10.0.0.4 - - [15/Jun/2026:10:00:01] "GET /api/orders HTTP/1.1" 200 412
10.0.0.7 - - [15/Jun/2026:10:00:01] "POST /api/login HTTP/1.1" 401 88
```

Output: the K paths with the highest request counts, e.g. `[("/api/orders", 50231), ("/api/login", 18004), ...]`.

## Step 1 — Clarify

Before writing anything, pin down the constraints out loud:

- **What's the key?** Path, path+method, full URL, IP? Confirm — it changes the parse.
- **How big is the input?** Fits in memory, or a 50 GB file / unbounded stream? This decides the whole approach.
- **Ties?** If two paths tie at the K-th spot, is any tie-break acceptable? Usually yes.
- **Is K small relative to N?** If K ≪ unique-keys, a heap wins; if K ≈ unique-keys, just sort.

These questions *are* the signal — an interviewer scoring an SRE wants to see you reach for the input-size question first.

## Step 2 — Count Frequencies (One Pass)

Whatever the final selection method, the first step is always a single streaming pass to build a frequency map. Stream line by line so memory is bounded by the number of *unique* keys, not the file size.

```python
import re
from collections import Counter

# capture the request path out of the "METHOD PATH HTTP/x" quoted field
PATH_RE = re.compile(r'"[A-Z]+ (\S+) HTTP/[\d.]+"')

def count_paths(lines):
    counts = Counter()
    for line in lines:               # 'lines' is an iterator — never read the whole file
        m = PATH_RE.search(line)
        if m:
            counts[m.group(1)] += 1
    return counts
```

`Counter` is a hash map: each `+= 1` is O(1), so counting is **O(n)** time over n lines and **O(u)** space for u unique keys.

## Step 3 — Select the Top-K

Now pick the K largest counts. Three approaches, with the trade-off you should state:

### Option A — Sort everything (simplest)

```python
def top_k_sort(counts, k):
    return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:k]
```

**O(u log u)**. Fine when K is close to u, or when u is small. The default if the interviewer just wants a correct answer fast — but say "this sorts more than we need" so they know you see the waste.

### Option B — Heap of size K (the expected answer)

Keep a min-heap of the K largest seen so far. `heapq.nlargest` does exactly this internally:

```python
import heapq

def top_k_heap(counts, k):
    return heapq.nlargest(k, counts.items(), key=lambda kv: kv[1])
```

**O(u log K)** time, **O(K)** extra space. When K ≪ u (e.g. top-10 of a million paths), this is a real win over the full sort — and it's the answer the interviewer is usually fishing for. Be ready to explain *why* it's `log K` not `log u`: the heap never grows past K, so each of the u pushes costs `log K`.

### Option C — Quickselect (optimal, rarely required)

Partition the u items so the K largest end up on one side — **O(u) average** time. Mention it as the asymptotically optimal option, but don't reach for it unless asked: it's fiddly, unstable on ties, and a partial sort by hand is bug-prone under time pressure. Knowing *when not* to use the clever tool is itself senior judgment.

## Step 4 — When It Doesn't Fit in Memory

The senior extension: u unique keys don't fit on one box (think every URL with query strings, or per-IP counts across a fleet). This is map-reduce:

1. **Shard** by hashing the key: `shard = hash(key) % N`. All occurrences of a given key land in the same shard, so per-shard counts are complete.
2. **Count** each shard independently (in parallel, on separate workers).
3. **Merge** each shard's local top-K into a global top-K with one more heap pass.

Because every key is fully contained in one shard, the local top-K candidates are sufficient — you never miss a key that was "split" across shards. This is exactly how a `kubectl logs | sort | uniq -c | sort -rn | head` pipeline scales out to a distributed log query.

## Worked Trace

For `counts = {"/a": 5, "/b": 9, "/c": 2, "/d": 9}` and `k = 2`:

- Heap keeps the 2 largest by count → `/b` (9) and `/d` (9) tie at the top; `/a` (5) and `/c` (2) fall out.
- Result: `[("/b", 9), ("/d", 9)]` (tie order arbitrary, which you confirmed was acceptable in Step 1).

## Best Practices

- Always start with the one-pass `Counter` — the selection method is a *second* decision.
- State the complexity of each option and pick by the K-vs-u relationship.
- Stream the input; never `f.read()` a log file of unknown size.
- Name the tie-break behavior before you're asked.
- Offer the sharded map-reduce version as the "what if it doesn't fit" extension.

## Common Mistakes

- Sorting when a size-K heap is clearly better (K ≪ u) — and not noticing.
- Reading the whole file into a list, blowing up memory on a large log.
- Claiming Quickselect without being able to write a correct partition under pressure.
- Forgetting that `heapq` is a *min*-heap, so the top of the heap is the smallest of the current K.
- Mis-parsing the path (grabbing the method or the full line) — test the regex on one real line.

## Quick Refs

```
Count:   one pass, Counter / hash map → O(n) time, O(u) space
Select:  sort      O(u log u)   — K ≈ u, or simplest
         heap      O(u log K)   — K ≪ u  ← expected answer
         quickselect O(u) avg   — optimal, rarely needed
Scale:   shard by hash(key) % N → count → merge top-K  (map-reduce)
Gotcha:  heapq is a MIN-heap; stream the file, don't read() it
```

## Interview Prep

**Junior**: "Return the top-K paths from a log." — One pass with a `Counter` to build counts, then `heapq.nlargest(k, ...)`. I'd state it's O(n) to count and O(u log K) to select, and trace one parsed line to confirm my regex grabs the path, not the method.

**Mid**: "Why a heap instead of just sorting?" — When K is far smaller than the number of unique keys, the heap never grows past K, so selection is O(u log K) versus O(u log u) for a full sort. If K were close to u I'd just sort — the heap's bookkeeping wouldn't pay off.

**Senior**: "The log is 50 GB and won't fit in memory." — Map-reduce: shard keys by hash so each key is fully contained in one shard, count shards in parallel, then merge per-shard top-K into a global top-K. The key insight is that hashing keeps every occurrence of a key together, so local top-K candidates are sufficient and nothing is missed.

**Staff**: "Now it's a live stream and you want top-K continuously." — Exact top-K over an unbounded stream needs unbounded memory, so I'd use an approximate sketch — Count-Min Sketch for frequency estimates plus a heap of heavy hitters (the Space-Saving / Misra-Gries algorithm) — trading bounded error for bounded memory. I'd make the accuracy-vs-memory trade-off explicit and tie it to a real system like a top-talkers dashboard that can tolerate small estimation error.

## Next Topic

→ [T06 — Worked Example: Topological Sort for Dependency Ordering](T06-Topological-Sort.md)
