# L29/C02 — Coding for DevOps Roles

## Topics

- **T01 Yes, You Still Need DSA** — Reality check
- **T02 Focus Areas** — Where to invest
- **T03 Concurrency Problems** — Common at FAANGM
- **T04 Systems Coding** — Beyond LeetCode
- **T05 Worked Example: Top-K from Logs** — The canonical SRE coding question, solved end to end
- **T06 Worked Example: Topological Sort** — Dependency ordering (deploy order, Terraform DAG, CI stages)
- **T07 Worked Example: Sliding-Window Rate Counting** — Rate limiting and burn-rate windows, solved three ways

## The Reality

You will be asked DSA questions in DevOps interviews at FAANGM. Even though you'll mostly write Terraform, you must solve algorithmic problems.

### Why
- Tests problem-solving structure
- Filters for engineering rigor
- Calibrates against other engineers
- Predicts ability to write tooling, operators, internal services

Don't fight it. Prepare.

## What Level

For senior+ DevOps:
- Medium LeetCode comfortably (~75th percentile speed)
- Hard occasionally
- 2 problems per 60-min interview is typical

Less than SWE rotation? Slightly. But not "no algorithms" — that myth gets candidates rejected.

## Focus Areas

### High-Yield
- **Strings & arrays**: parsing, sliding window
- **Hash maps**: counting, lookups
- **Trees / BSTs**: traversal, depth, path-finding
- **Graphs**: BFS, DFS, topological sort
- **Sliding window**: subarray sums, substrings
- **Heaps / priority queues**: top-K, scheduling
- **Binary search**: on arrays, on answer space
- **Two pointers**: sorted-array problems

### Medium-Yield
- **Dynamic programming**: 1D, 2D
- **Greedy**: scheduling, intervals
- **Backtracking**: combinations, permutations
- **Tries**: prefix problems

### Lower-Yield (Still Possible)
- **Bit manipulation**
- **Math (number theory)**
- **Geometry**

## Concurrency Problems

Common for DevOps (systems-flavored):
- Implement a thread-safe queue
- Rate limiter (token bucket, sliding window)
- Connection pool
- Producer-consumer
- Read-write lock
- Counting semaphore
- Bounded blocking queue

```python
class RateLimiter:
    def __init__(self, rate, burst):
        self.rate = rate
        self.burst = burst          # bucket capacity (max tokens)
        self.tokens = burst         # start full so an initial burst is allowed
        self.last = time.time()
        self.lock = threading.Lock()
    
    def allow(self):
        with self.lock:
            now = time.time()
            self.tokens = min(self.burst, self.tokens + (now - self.last) * self.rate)
            self.last = now
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False
```

## Systems Coding

Beyond LeetCode, you may get:
- Build a thread-safe cache (LRU + TTL)
- Implement a simple Bloom filter
- Parse log file and find top errors
- Implement consistent hashing
- Build a key-value store
- Implement a thread pool

These are more "engineering" than "algorithms" — test design choices.

## Languages

Most interviewers accept Python, Java, Go, C++.

### Python
- Fastest to write
- Great for parsing, dict-heavy
- Concurrency awkward (GIL)
- Recommended for most candidates

### Go
- Great for systems coding (concurrency, channels)
- Some interviewers prefer it for DevOps roles
- Standard library decent

### Java
- More verbose; slower to write
- Strong for concurrency (java.util.concurrent)
- OK if you're fluent

### C++
- Fastest runtime; mostly irrelevant in interview
- Use only if you're strong

## Approach During Interview

### Step 1: Clarify
- Restate problem
- Edge cases (empty, single, all same)
- Input range, output format
- Time/space constraints

### Step 2: Brute Force First
- Talk through naive solution
- State its time/space
- Then optimize

### Step 3: Optimize
- Discuss approach
- Get interviewer buy-in before coding
- Code the chosen approach

### Step 4: Code
- Clean, readable
- Use meaningful names
- Comment intent (not what)

### Step 5: Test
- Walk through example
- Edge cases
- Don't trust "should work"

### Step 6: Analyze
- Time: Big-O
- Space: Big-O
- Compare to brute force

## Common Mistakes

- Jumping to code without thinking
- Not asking clarifying questions
- Defending bad approach when challenged
- Forgetting edge cases
- Bug-free but no testing walk-through
- Silent coding (talk through your thinking)

## Practice Schedule

### 8 weeks (intensive)
- 5 mediums/week
- Cover: arrays/strings → hash → trees → graphs → DP → backtracking
- Weekly mock interview

### 4 weeks (refresh)
- 3 mediums/day
- Plus 1 hard/week
- Focus weak areas

### Maintenance
- 1 problem/day or 5/week
- Mix mediums and hards
- Mock interview once a month

## Resources

- **LeetCode** — primary
- **Cracking the Coding Interview** — McDowell
- **Elements of Programming Interviews** — Aziz et al.
- **NeetCode 150** — focused list of essential problems
- **HackerRank** for systems / SQL specific

## DevOps-Specific Problem Lists

Some interviewers tailor for DevOps:
- Implement a deployment system in code
- Schedule jobs with dependencies (topological sort)
- Log parser (largest source, top N errors)
- Capacity allocation (knapsack)

These reward systems thinking + algorithms.

## SQL

You may be asked SQL. Especially:
- Window functions
- JOINs (inner, left, self)
- Aggregations
- Subqueries / CTEs

For analytics-flavored teams.

## Live Coding Etiquette

- Share your screen or use shared editor (CoderPad, etc.)
- Type slowly + carefully (typos cost time)
- Talk through your thinking
- Ask if you're not sure about constraints
- It's OK to look up syntax (most allow)

## Interview Themes

- "Solve [LeetCode medium]"
- "Implement a rate limiter"
- "Find top 10 IPs in a log file"
- "Thread-safe LRU cache"
- "SQL window function for X"
