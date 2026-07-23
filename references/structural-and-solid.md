# Structural Complexity and SOLID

Structural metrics and SOLID answer design/review questions, not runtime-complexity questions. Keep three validity questions separate:

1. **Calculation validity**: was the metric computed according to a declared definition?
2. **Construct validity**: does it actually represent the claimed attribute, such as comprehensibility?
3. **Predictive validity**: does it predict effort, defects, or change cost in this context?

A reproducible number may still be a weak proxy. There is no scientifically valid universal “function complexity score.”

## Contents

- Structural metrics
- Interpreting metrics responsibly
- SOLID rubric
- SOLID and performance trade-offs
- Scientific and foundational sources

## Structural Metrics

### Cyclomatic complexity

For a control-flow graph, McCabe's cyclomatic number is

`V(G) = E - N + 2P`,

where `E` is the number of edges, `N` nodes, and `P` connected components. For a conventional single-entry connected function, a tool may implement a decisions-plus-one shortcut.

Use it as a control-flow and basis-path signal. Report:

- the value;
- each contributing construct;
- the tool/version or CFG convention;
- treatment of boolean operators, `switch`/patterns, `catch`, conditional expressions, early returns, and language-specific constructs.

Limits:

- It is not runtime time/space complexity.
- It does not count all feasible paths or dictate the exact number of tests.
- Equal values can hide very different nesting and comprehensibility.
- A fixed threshold such as 10 is a policy heuristic, not a natural or universal scientific boundary.
- Generated code and homogeneous declarative branches need contextual interpretation.

### NPath and ACPATH

NPath aims to estimate acyclic execution paths and can reveal multiplicative path growth that cyclomatic complexity treats additively. Use only with a documented language-aware implementation.

State handling of short-circuit operators, exceptions, loop entry/exit, `goto`, early returns, and infeasible paths. Do not equate NPath with required test cases.

The original NPath definition has known correctness problems even for some simple C programs, and general acyclic-path counting is computationally difficult. Prefer ACPATH for supported C-like programs when its stated restrictions hold. Treat limits such as 200 as tool policies, not scientific constants.

### Cognitive Complexity

Cognitive Complexity is a SonarSource rule-based heuristic intended to represent difficulty following control flow. If used:

- cite the specification/tool version;
- list increments and nesting contributions;
- report maximum nesting alongside it;
- compare only under compatible language/tool conventions.

Empirical work finds some association with comprehension measures but mixed results, and it is not consistently superior to traditional metrics. Treat it as a review signal, not a cognition measurement or performance predictor.

### Halstead metrics

Only calculate Halstead metrics when operator/operand classification is explicit and reproducible:

- `n1`, `n2`: distinct operators and operands;
- `N1`, `N2`: total operator and operand occurrences;
- vocabulary `n = n1+n2`;
- length `N = N1+N2`;
- volume `V = N log2(n)`;
- difficulty `D = (n1/2)(N2/n2)`;
- effort `E = D*V`.

Always expose the four base counts. Derived “effort,” time, or predicted-defect formulas are models, not direct human-effort measurements; their theoretical and empirical basis is contested. Do not infer runtime performance from Halstead metrics.

### Maintainability Index

Maintainability Index is a calibrated composite model with incompatible variants. If it is relevant at all:

- record the exact formula, scale, tool, version, and components;
- show LOC, cyclomatic, and Halstead inputs separately;
- use it for within-project trends under a stable toolchain, not cross-language comparison.

Do not use it as the primary assessment of one function, a universal red/yellow/green gate, or a substitute for explaining the underlying contributors.

### Supporting counts

SLOC, nesting depth, parameter/dependency counts, and fan-in/fan-out can be exact under a declared convention. They are context signals, not independent proof of difficulty, defects, or poor design. Avoid summing metrics with different scales into a homemade index.

## Interpreting Metrics Responsibly

- List contributors so results are auditable.
- Prefer deltas against a compatible project baseline over universal thresholds.
- Investigate whether complexity is essential to the domain or accidental in the implementation.
- Do not refactor solely to lower a number; this can spread complexity across files and hide it from function-level tools.
- Treat correlations as associations, not causal evidence.
- Separate generated, repetitive declarative, parser/state-machine, and business-policy code when comparing metrics.
- If an AST/CFG tool is unavailable or conventions are ambiguous, describe contributors qualitatively rather than inventing a precise value.

## SOLID Rubric

SOLID is a practitioner design framework, not a validated additive measurement scale. Liskov substitution has a strong formal basis in behavioral subtyping; the other principles remain contextual design guidance.

For each principle use one status:

- `conforms`: applicable, and inspected evidence supports the principle;
- `risk`: a concrete concern exists but evidence is insufficient for a violation;
- `violation-with-evidence`: a relevant contract/change axis and code relationship demonstrate the problem;
- `not-applicable`: the necessary design relationship is absent;
- `insufficient-evidence`: the relationship may exist but required callers/contracts/history are unavailable.

Each row must state scope, evidence and counterevidence, relevant requirement/contract, impact, confidence, and trade-off. Never calculate a SOLID percentage, average, star rating, or combined pass/fail.

### SRP — Single Responsibility Principle

Primary scope is a module, class, or component. For an isolated function, assess only cohesion and signs of independent reasons for change.

Ask:

- Which actor or requirement family causes this unit to change?
- Does it combine independently volatile policy, persistence, transport, security, or presentation concerns?
- Do history and callers show unrelated change reasons?
- Would extraction isolate real volatility, or merely fragment a cohesive algorithm?

Length, multiple steps, several verbs, or high cyclomatic complexity are not automatic SRP violations.

### OCP — Open/Closed Principle

Evaluate only after identifying an existing or explicitly expected variation axis.

Ask:

- Does adding a known variant repeatedly modify stable central logic?
- Is type/variant branching duplicated across locations?
- Would a strategy, callback, data table, or polymorphism localize changes?
- Is the abstraction justified by actual variants, change history, or a requirement?

Mark `not-applicable` when no credible extension axis exists. OCP does not mean code can never be edited, and speculative indirection can reduce clarity and performance.

### LSP — Liskov Substitution Principle

Applies only to subtype, override, interface implementation, or callback substitutability with a behavioral contract.

Check that the substitute:

- does not strengthen preconditions;
- does not weaken postconditions;
- preserves invariants and history/state constraints;
- preserves compatible exception, nullability, side-effect, concurrency, and resource guarantees;
- satisfies properties expected by clients of the abstraction.

Run the same contract tests against implementations when possible. A standalone function with no substitution relation is `not-applicable`.

### ISP — Interface Segregation Principle

Requires an interface boundary and actual consumers.

Inspect which operations each client uses, whether clients depend on irrelevant capabilities, and whether changes for one client group force unrelated clients to change. Smaller interfaces are useful only when they express cohesive stable capabilities. Parameter count or method count alone does not demonstrate an ISP violation.

### DIP — Dependency Inversion Principle

Requires the surrounding policy/dependency graph.

Identify high-level policy and volatile mechanisms. Ask whether policy directly owns/imports details that obstruct testing, substitution, or evolution, and whether an abstraction would express the policy's need at the appropriate boundary.

Do not flag every concrete instantiation, stable value type, library call, lack of dependency-injection framework, or pure data function. Dependency injection can support DIP but is neither necessary nor sufficient.

## SOLID and Performance Trade-offs

- SOLID compliance does not prove performance, correctness, or maintainability.
- Indirection may add dispatch/allocation overhead, but compilers may eliminate it; measure if the path is hot.
- Combining operations may improve locality or reduce I/O round trips while increasing structural coupling.
- Splitting functions can improve naming/test seams without changing complexity, or can obscure a hot call path.
- Recommend a design change only when the maintainability benefit and its validation plan are explicit.

## Scientific and Foundational Sources

- McCabe, “A Complexity Measure,” [DOI 10.1109/TSE.1976.233837](https://doi.org/10.1109/TSE.1976.233837).
- Shepperd, “A Critique of Cyclomatic Complexity as a Software Metric,” [DOI 10.1049/sej.1988.0003](https://doi.org/10.1049/sej.1988.0003).
- Nejmeh, “NPATH: a Measure of Execution Path Complexity,” [DOI 10.1145/42372.42379](https://doi.org/10.1145/42372.42379).
- Bagnara et al., “The ACPATH Metric,” [arXiv:1610.07914](https://arxiv.org/abs/1610.07914).
- SonarSource, [Cognitive Complexity specification, version 1.7](https://assets-eu-01.kc-usercontent.com/5a869490-919a-0159-3da4-b8c3c397c0bc/39475230-c3ff-4e73-8ab3-fe0c9f21e9dd/Cognitive_Complexity_Sonar_Guide_2023.pdf).
- Muñoz Barón, Wyrich, and Wagner, empirical meta-analysis of code comprehension, [DOI 10.1145/3382494.3410636](https://doi.org/10.1145/3382494.3410636).
- Lavazza et al., evaluation of Cognitive Complexity, [DOI 10.1016/j.jss.2022.111561](https://doi.org/10.1016/j.jss.2022.111561).
- Weyuker, “Evaluating Software Complexity Measures,” [DOI 10.1109/32.6178](https://doi.org/10.1109/32.6178).
- Fenton, “Software Measurement: A Necessary Scientific Basis,” [DOI 10.1109/32.268921](https://doi.org/10.1109/32.268921).
- Oman and Hagemeister, original Maintainability Index work, [DOI 10.1109/ICSM.1992.242525](https://doi.org/10.1109/ICSM.1992.242525).
- Parnas, “On the Criteria To Be Used in Decomposing Systems into Modules,” [DOI 10.1145/361598.361623](https://doi.org/10.1145/361598.361623).
- Liskov and Wing, “A Behavioral Notion of Subtyping,” [DOI 10.1145/197320.197383](https://doi.org/10.1145/197320.197383), [author PDF](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf).
- Martin, [Design Principles and Design Patterns](https://web.archive.org/web/20150906155800/http://www.objectmentor.com/resources/articles/Principles_and_Patterns.pdf).
