# Formal Algorithmic Complexity

Use this guide to derive growth bounds from code. A conclusion is formal only relative to the declared input measure, cost model, preconditions, and called-operation contracts.

## Contents

- Core distinctions
- Derivation procedure
- Sums and recurrences
- Amortized analysis
- Space
- Specialized models
- Limits of static analysis
- Scientific sources

## Core Distinctions

For an input `x`, size `|x| = n`, and cost `C(x)`:

- worst case: `T_w(n) = max_{|x|=n} C(x)`;
- best case: `T_b(n) = min_{|x|=n} C(x)`;
- expected case: `T_avg(n) = E[C(x)]` for an explicitly declared distribution `x ~ D_n`;
- randomized algorithm on the worst input: `T_rand(n) = max_x E_r[C(x,r)]`;
- amortized cost: worst total cost over every valid operation sequence, divided across that sequence.

Keep the selected case separate from asymptotic notation:

- `O(g(n))` is an asymptotic upper bound;
- `Ω(g(n))` is an asymptotic lower bound;
- `Θ(g(n))` is a tight asymptotic bound;
- `o(g(n))` and `ω(g(n))` are strict asymptotic bounds.

Big O does not mean worst case, Ω does not mean best case, and Θ does not mean average case. Each notation can qualify any already-defined cost function.

## Derivation Procedure

1. Identify the exact implementation, transitive calls, preconditions, and input domain.
2. Define all independent size parameters before choosing a single `n`.
3. Select a cost model: unit-cost RAM, word-RAM, bit operations, comparisons, allocations, database requests, bytes transferred, cache misses, or another explicit unit.
4. Build the cost expression from the program.
5. Resolve sums or recurrences and verify the proposed solution.
6. Prove both upper and lower bounds before claiming `Θ`.
7. Derive peak auxiliary space separately from output and total allocation.
8. Record assumptions, unknown operation costs, and the evidence level.

### Composition Rules

- Sequence: add costs; simplify only after retaining relevant independent parameters.
- Branch, worst case: take the maximum reachable branch plus condition cost.
- Branch, best case: take the minimum reachable branch under valid inputs.
- Branch, expected case: weight branches only with a justified probability model.
- Loop: write a summation when the iteration count or body cost varies.
- Nested loops: multiply only when their ranges are independent and rectangular; triangular or data-dependent loops require a sum.
- Recursion: derive a recurrence from actual subproblem sizes and nonrecursive work.
- Call: use a documented cost contract or recursively analyze it; never assume a library operation is constant merely because it is one source line.
- Lazy/streaming code: distinguish cost to construct the computation from cost to consume it.
- Hashing: state expected/amortized and collision assumptions; also report worst case when material.
- Integer arithmetic: unit-cost arithmetic is inappropriate when operand bit length grows materially.

### Tight Bounds

An upper bound alone supports `O`, not automatically `Θ`. Establish a matching lower bound by one of these methods:

- count operations performed for every valid input;
- exhibit an infinite family of inputs attaining the upper-order cost;
- use a known lower bound under the same computational model;
- use output size, input reading, or comparison-decision-tree arguments.

Do not describe a loose but true bound as the answer when a tighter useful bound is available.

## Sums and Recurrences

Prefer, in order:

1. direct summation and substitution/induction;
2. recursion-tree reasoning checked by substitution;
3. Master theorem only for a matching recurrence such as `T(n)=aT(n/b)+f(n)` and after checking its conditions;
4. Akra–Bazzi for fractional, unequal subproblem sizes under its regularity assumptions;
5. an unresolved recurrence or `unknown` when data dependence or mutual recursion prevents a defensible solution.

For Akra–Bazzi recurrences

`T(x) = Σ a_i T(b_i x + h_i(x)) + g(x)`,

find `p` satisfying `Σ a_i b_i^p = 1`; under the theorem's assumptions the solution is

`Θ(x^p (1 + integral_1^x g(u)/u^(p+1) du))`.

Do not force Master theorem onto `T(n-1)`, arbitrary unequal splits, mutually recursive systems, or recurrences with unmet regularity conditions.

## Amortized Analysis

Use amortization for a sequence guarantee, not for a probability claim. Valid proof styles are:

- aggregate: bound total cost of an arbitrary sequence;
- accounting: assign credits and prove the balance never becomes invalid;
- potential: define state potential `Φ` and amortized cost
  `ĉ_i = c_i + Φ(D_i) - Φ(D_{i-1})`.

For the potential method, show why the telescoping sum of amortized costs bounds the real total, commonly with `Φ(D_0)=0` and nonnegative potential. An amortized bound does not guarantee the latency of each operation.

## Space

Report separately when relevant:

- peak auxiliary heap/storage;
- maximum recursion or explicit-stack depth;
- required output space;
- memory retained by closures, caches, globals, or reachable objects;
- total allocated bytes as an empirical performance metric, not as asymptotic peak-space complexity.

For in-place claims, state the convention: `O(1)` auxiliary storage may still permit mutation and output references. For recursion, count frames live simultaneously, not the total calls made.

## Specialized Models

Use a specialized model only when it changes the useful conclusion.

### Multi-parameter and output-sensitive analysis

Keep expressions such as `Θ(V+E)`, `O(nm)`, or `O(n+k)` rather than hiding structure in `n`. If parameters have a proven relationship, give both the multivariate form and the simplified form under that relationship. Include output size `k` when producing the output itself imposes a lower bound.

### Parameterized complexity

First give the ordinary multivariate running time. Classify a parameterized problem only when `k` and the problem family are defined:

- FPT: `f(k) n^c`, where `c` is independent of `k`;
- XP: `n^{f(k)}`.

FPT is a structural classification, not a practical-speed guarantee.

### Parallel work and span

For a computation DAG, report:

- work `W = T_1`, total operations;
- span `D = T_infinity`, critical-path length;
- parallelism `W/D`.

Under an appropriate work-depth scheduler, `T_P = O(W/P + D)`; necessarily `T_P >= max(W/P, D)`. Treat communication, synchronization, contention, memory bandwidth, NUMA, and scheduler overhead as empirical costs outside the abstract bound unless modeled explicitly.

### I/O and cache complexity

For external memory, declare input count `N`, internal memory `M`, block size `B`, and count block transfers. For ideal-cache/cache-oblivious analysis, declare cache size `Z`, line/block length `L`, replacement assumptions, and any tall-cache condition. Report CPU work separately.

### Comparison, decision-tree, and bit complexity

Use comparison count for comparison-based algorithms when it provides a stronger machine-independent result. Use bit complexity for arbitrary-precision arithmetic, cryptography, symbolic computation, or any operation whose cost grows with operand width.

## Limits of Static Analysis

- Undecidability prevents a complete automatic complexity analyzer for arbitrary Turing-complete programs.
- Sound tools must restrict the language/model or return `unknown`.
- A human derivation is only as reliable as its operation contracts and assumptions.
- A formal abstract-cost proof does not predict wall-clock time, WCET, cache behavior, or a compiler's generated code unless those are explicitly modeled.
- Finite benchmark samples cannot prove an asymptotic class; many functions agree on a finite interval and diverge later.

## Scientific Sources

- Cormen et al., *Introduction to Algorithms*, 4th ed., [MIT Press](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/).
- MIT 6.006, [asymptotic analysis and recurrence notes](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/pages/lecture-notes/).
- NIST Dictionary of Algorithms and Data Structures: [Big O](https://xlinux.nist.gov/dads/HTML/bigOnotation.html), [Ω](https://xlinux.nist.gov/dads/HTML/omegaCapital.html), [Θ](https://xlinux.nist.gov/dads/HTML/theta.html), and [space complexity](https://xlinux.nist.gov/dads/HTML/asymptoticSpaceComplexity.html).
- Tarjan, “Amortized Computational Complexity,” [DOI 10.1137/0606031](https://doi.org/10.1137/0606031).
- Akra and Bazzi, “On the Solution of Linear Recurrence Equations,” [DOI 10.1023/A:1018373005182](https://doi.org/10.1023/A:1018373005182).
- Downey and Fellows, *Fundamentals of Parameterized Complexity*, [DOI 10.1007/978-1-4471-5559-1](https://doi.org/10.1007/978-1-4471-5559-1).
- Blumofe and Leiserson, “Scheduling Multithreaded Computations by Work Stealing,” [DOI 10.1145/324133.324234](https://doi.org/10.1145/324133.324234).
- Aggarwal and Vitter, “The Input/Output Complexity of Sorting and Related Problems,” [DOI 10.1145/48529.48535](https://doi.org/10.1145/48529.48535).
- Frigo et al., “Cache-Oblivious Algorithms,” [DOI 10.1109/SFFCS.1999.814600](https://doi.org/10.1109/SFFCS.1999.814600).
- Charguéraud and Pottier, “Verifying the Correctness and Amortized Complexity of a Union-Find Implementation in Separation Logic with Time Credits,” [paper](https://www.chargueraud.org/research/2018/bigo_credits/bigo_credits.pdf).
