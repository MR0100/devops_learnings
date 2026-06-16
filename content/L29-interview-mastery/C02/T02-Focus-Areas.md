# L29/C02/T02 — DSA Focus Areas

## Learning Objectives

- Master common DSA
- Prepare efficiently

## Top Topics

### Strings / Arrays
- Two pointers
- Sliding window
- Palindrome / substring

### Hash Maps
- Anagrams
- Two-sum
- Frequency

### Linked List
- Reverse
- Cycle
- Merge

### Trees
- Traversal (BFS, DFS, in/pre/postorder)
- LCA
- Path sum

### Graphs
- BFS / DFS
- Cycle detection
- Shortest path (Dijkstra basic)
- Topological sort

### Heaps
- Top K
- Median
- K-way merge

### Stack
- Valid parentheses
- Largest rectangle
- Daily temperatures

### Binary Search
- Sorted array
- Rotated
- Modified BS

### Dynamic Programming (lighter for DevOps)
- Climbing stairs
- Coin change
- Longest common subsequence

## Patterns

### Sliding Window
```python
left, right = 0, 0
while right < len(s):
    # extend
    while invalid:
        # shrink
        left += 1
    # update
    right += 1
```

For: substring problems.

### Two Pointers
For sorted arrays; pair sum.

### Fast / Slow
For: cycle in linked list.

### BFS
Level-order; shortest path.

### DFS
Path; cycle; backtracking.

### Top K (Heap)
Largest / smallest K.

### Backtracking
Permutations; combinations.

## Practice Set

NeetCode 150 / Blind 75.

For: high-yield.

## Per Topic Time

- Easy: 5-15 min
- Med: 20-40 min
- Hard: 45-60 min

## Strategy

1. Read problem
2. Examples
3. Approach (brute force)
4. Optimize
5. Code
6. Test
7. Complexity

## Best Practices

- Pattern first
- Multiple problems per pattern
- Mocks
- Time pressure practice

## Common Mistakes

- All hards (waste)
- No patterns (slow recognize)
- Silent coding

## Quick Refs

```
Patterns:
- Sliding window
- Two pointers
- Fast/slow
- BFS/DFS
- Top K heap
- Backtracking

Practice: NeetCode 150
```

## Interview Prep

**Junior**: "Which DSA topics should I prioritize for a DevOps loop?" — The high-yield core: strings/arrays with two-pointer and sliding window, hash maps for counting and lookups, tree traversal, and graph BFS/DFS. These cover the large majority of Mediums you'll see. DP and backtracking are lower-yield for DevOps; I cover them last.

**Mid**: "How do you recognize which pattern a problem wants?" — I map keywords to patterns: 'contiguous subarray/substring with a constraint' → sliding window; 'pair sums in a sorted array' → two pointers; 'cycle in a linked list' → fast/slow pointers; 'shortest path in unweighted graph' → BFS; 'top/smallest K' → heap. Naming the pattern out loud lets the interviewer redirect me early if I've mis-read the problem.

**Senior**: "Why are graphs over-represented in SRE interviews?" — Because the work is graph-shaped: service dependency DAGs, deploy ordering, network topology, blast-radius analysis. A topological sort *is* dependency ordering; BFS *is* a blast-radius walk. I make that connection explicit, since framing the abstract problem in operational terms is a senior signal and often the bridge into the system-design round.

**Staff**: "How do you decide depth vs breadth in prep?" — Breadth across patterns beats depth in any one: I want to recognize all the common patterns instantly rather than master DP. I drill a few problems per pattern until recognition is automatic, then stop — the marginal Hard problem buys less than a mock interview or a system-design rep at this level.

## Next Topic

→ [T03 — Concurrency Problems](T03-Concurrency-Problems.md)
