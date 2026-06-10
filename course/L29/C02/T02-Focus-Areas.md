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

## Next Topic

→ [T03 — Concurrency Problems](T03-Concurrency-Problems.md)
