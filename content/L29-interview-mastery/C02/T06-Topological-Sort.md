# L29/C02/T06 — Worked Example: Topological Sort for Dependency Ordering

## Learning Objectives

- Implement topological sort both ways (Kahn's BFS and DFS) and know when to use each
- Detect cycles — the failure mode that matters most in real dependency graphs
- Map the abstract problem onto real DevOps systems: deploy order, Terraform graphs, CI stages, init ordering

## Why This Problem

Half of DevOps *is* dependency ordering. Terraform builds a DAG and applies resources in dependency order. `kubectl` waits on CRDs before custom resources. systemd orders units by `After=`/`Requires=`. A CI pipeline runs stages whose inputs are other stages' outputs. A package manager installs dependencies before dependents. Every one of these is a topological sort, and the interview version — "given task dependencies, return a valid execution order, or report that none exists" — is a graph Medium you should own. The cycle-detection half is what separates a textbook answer from one that understands production: a real dependency graph with a cycle is a *bug you must report*, not a sort you can complete.

## The Problem

> You have N build tasks. Some tasks depend on others (task B can't start until task A finishes). Return a valid order to run all tasks, or detect that the dependencies are circular.

Input: a list of edges `A → B` meaning "A must run before B."

```python
tasks = ["build", "test", "package", "deploy"]
deps = [("build", "test"), ("build", "package"),
        ("test", "deploy"), ("package", "deploy")]
```

A valid output: `["build", "test", "package", "deploy"]` (or `build, package, test, deploy` — both respect every edge).

## Step 1 — Clarify

- **Edge direction:** does `(A, B)` mean "A before B" or "A depends on B"? These are reverses of each other — confirm, because getting it backwards silently produces a wrong-but-valid-looking order.
- **Cycle handling:** return empty? raise? return the cycle for debugging? In ops, *naming the cycle* is the most useful answer.
- **Multiple valid orders:** is any topological order acceptable, or is there a tie-break (e.g. alphabetical, or maximize parallelism)?
- **Disconnected nodes:** tasks with no dependencies must still appear in the output.

## Step 2 — Kahn's Algorithm (BFS, the default)

Kahn's is the cleaner answer for most interviews because cycle detection falls out for free: if you can't process every node, the leftover nodes form a cycle.

```python
from collections import deque, defaultdict

def topo_sort(tasks, deps):
    graph = defaultdict(list)         # A -> [nodes that depend on A]
    indegree = {t: 0 for t in tasks}  # how many prerequisites each task has

    for a, b in deps:                 # edge a -> b : a must run before b
        graph[a].append(b)
        indegree[b] += 1

    # start with every task that has no prerequisites
    queue = deque([t for t in tasks if indegree[t] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in graph[node]:       # "finishing" node removes a prereq from its dependents
            indegree[nxt] -= 1
            if indegree[nxt] == 0:    # all prereqs satisfied → ready to run
                queue.append(nxt)

    if len(order) != len(tasks):
        # some nodes never reached indegree 0 → they're in a cycle
        cyclic = [t for t in tasks if indegree[t] > 0]
        raise ValueError(f"cycle detected involving: {cyclic}")

    return order
```

**Complexity: O(V + E)** — every node and edge is visited once. That's optimal; you can't order a graph without looking at every dependency.

The mental model: indegree is "how many things must finish before this can start." You start tasks whose indegree is 0, and finishing a task decrements its dependents' indegrees. When `len(order) < len(tasks)`, the nodes that never hit indegree 0 are exactly the cycle — and reporting *which* tasks are stuck is the answer a tired on-call engineer actually wants.

## Step 3 — DFS Variant (and why direction matters)

The DFS approach: depth-first from each node, and **prepend** a node to the result *after* its descendants are fully visited (post-order), so dependencies land before dependents.

```python
def topo_sort_dfs(tasks, deps):
    graph = defaultdict(list)
    for a, b in deps:
        graph[a].append(b)

    WHITE, GRAY, BLACK = 0, 1, 2      # unvisited / on-stack / done
    color = {t: WHITE for t in tasks}
    order = []

    def visit(node):
        color[node] = GRAY            # mark on the current recursion stack
        for nxt in graph[node]:
            if color[nxt] == GRAY:    # back-edge to a node on the stack = cycle
                raise ValueError(f"cycle through {node} -> {nxt}")
            if color[nxt] == WHITE:
                visit(nxt)
        color[node] = BLACK
        order.append(node)            # post-order: appended after all descendants

    for t in tasks:
        if color[t] == WHITE:
            visit(t)

    return order[::-1]                # reverse post-order = topological order
```

The three-color scheme is the cycle detector: hitting a **GRAY** node means a back-edge to something still on the recursion stack — a cycle. A two-color (visited/unvisited) scheme can't tell a cycle from a diamond (a node reachable by two forward paths), which is the classic bug in this problem. Use Kahn's when you want iterative code and easy cycle *reporting*; use DFS when recursion is natural or you also need to find which edge closes the cycle.

## Step 4 — Real-World Framing

Say this out loud — it's what turns a graph Medium into an SRE-aware answer:

- **Terraform** builds exactly this DAG from resource references and applies in topological order; a cycle is the `Error: Cycle:` you've seen.
- **Deploy ordering** across microservices: schema migration before the service that reads the new column, config before the consumer.
- **CI stages**: `build → test → package → deploy`, where independent branches (test and package both depend only on build) reveal where you can **parallelize** — any two nodes with no path between them can run concurrently.
- **systemd / init**: unit ordering is a topo sort over `After=`/`Before=`.

The parallelism point is a strong extension: Kahn's naturally exposes it — every node in the queue *at the same time* has all prerequisites met and can run in parallel. Process the queue in "waves" and each wave is a parallel batch.

## Worked Trace

For the `build/test/package/deploy` example:

- Indegrees: `build=0, test=1, package=1, deploy=2`.
- Queue starts `[build]`. Pop `build` → order `[build]`; decrement `test`→0 and `package`→0, queue `[test, package]`.
- Pop `test` → order `[build, test]`; decrement `deploy`→1.
- Pop `package` → order `[build, test, package]`; decrement `deploy`→0, queue `[deploy]`.
- Pop `deploy` → order `[build, test, package, deploy]`. All 4 processed → no cycle.

## Best Practices

- Confirm edge direction before coding — reversed edges produce a plausible but wrong order.
- Prefer Kahn's when you need to *report* the cycle; use the GRAY/BLACK DFS when you need the specific cycling edge.
- Compare `len(order)` to `len(tasks)` — that single check is your cycle detector in Kahn's.
- Include zero-dependency and disconnected nodes; they belong in the output.
- Mention the parallelism extension (queue waves) — it shows you see the operational use.

## Common Mistakes

- Two-color DFS that flags diamonds (a node reached twice via valid paths) as false cycles.
- Reversing the edge meaning and silently emitting a wrong order.
- Forgetting tasks with no edges, so they're dropped from the result.
- Not detecting cycles at all — returning a partial order as if it were complete.
- Recursing in DFS deep enough to hit Python's recursion limit on a large graph (prefer Kahn's, or an explicit stack).

## Quick Refs

```
Edge (A,B): A must run before B   ← always confirm direction
Kahn (BFS):  indegree map; start at 0; decrement dependents; O(V+E)
   cycle  := len(order) != len(tasks) → leftover nodes are the cycle
DFS:        post-order + reverse; GRAY node on stack = cycle
Parallel:   nodes in the queue together = a parallel wave
Real:       Terraform DAG, deploy order, CI stages, systemd units
```

## Interview Prep

**Junior**: "Return a valid order for tasks with dependencies." — Kahn's algorithm: build an indegree count, start with every task at indegree 0, and as each finishes, decrement its dependents — adding them when they reach 0. It's O(V+E). I'd confirm first whether edge `(A,B)` means 'A before B,' since reversing it gives a wrong order.

**Mid**: "How do you detect a cycle?" — In Kahn's, if the output has fewer nodes than the input, the leftover nodes never reached indegree 0 and are exactly the cycle — I return *which* tasks are stuck. In DFS I use three colors and treat an edge to a GRAY (on-stack) node as the cycle; a two-color scheme would false-positive on diamonds.

**Senior**: "Where does this show up in your actual work?" — It's everywhere dependencies exist: Terraform's resource DAG, deploy ordering (migration before the service that reads the new column), CI stage graphs, systemd unit ordering. Framing the abstract problem as 'this is the Terraform apply graph' is usually how I bridge from the coding round into the design discussion.

**Staff**: "You have 500 tasks and want to run them as fast as possible." — Kahn's exposes parallelism for free: every node in the ready-queue at the same moment has all prerequisites met, so process the queue in waves and each wave is a parallel batch. The makespan is the longest dependency chain (critical path), not the task count — so I'd identify the critical path to know the floor on completion time and where to invest in speeding up individual steps.

## Next Topic

→ [T07 — Worked Example: Sliding-Window Rate Counting](T07-Sliding-Window-Rate.md)
