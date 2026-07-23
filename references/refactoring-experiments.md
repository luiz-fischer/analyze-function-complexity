# Experimental Refactoring of High-Complexity Functions

Use this guide only when the user explicitly requests optimization or refactoring. Treat refactoring as a controlled intervention: preserve required behavior, change a stated causal contributor, and evaluate the result against predeclared goals. A high metric or threshold alone is not a decision rule.

## Contents

- Goal-Question-Metric decision frame
- Diagnose the complexity that matters
- Dependency, history, and execution evidence
- Refactoring hypotheses and candidates
- Behavioral preservation
- Controlled before/after experiments
- Comprehension experiments
- Multiobjective and Pareto decisions
- Search-based refactoring
- End-to-end protocol
- Included comparison helper
- Required report
- Scientific sources

## Goal-Question-Metric Decision Frame

Define measurement top-down before editing:

1. **Goal**: state the object, purpose, quality focus, viewpoint, and environment.
2. **Questions**: state what must be true for the refactor to count as an improvement.
3. **Metrics**: select the smallest set that can answer those questions.
4. **Guardrails**: declare outcomes that no candidate may violate.
5. **Decision rule**: declare how candidates will be retained without inspecting results first.

Example:

- Goal: reduce change and comprehension cost of policy branching without changing public behavior or worsening p95 latency by more than 3%.
- Questions: are responsibilities independently volatile; are paths easier to follow; are outputs, exceptions, side effects, and latency preserved?
- Metrics: change-history coupling, task errors/time, structural contributors, differential failures, mutation score, paired p95 latency.
- Guardrails: zero semantic-oracle failures, unchanged public contract, no new data race, latency noninferiority bound.

Do not optimize every available metric. Record the construct each metric represents and the smallest effect that matters.

## Diagnose the Complexity That Matters

Classify the motivating problem before choosing a transformation:

- **algorithmic**: growth is unsuitable at expected constraints; derive before/after bounds under the same cost model;
- **measured runtime**: a representative profile shows material workload share; preserve end-to-end relevance;
- **structural**: control flow, nesting, or dependencies impede a concrete review, test, or change task;
- **design**: contracts or independently volatile responsibilities create repeated change cost;
- **incidental environment cost**: compiler, JIT, cache, I/O, contention, or configuration dominates and source restructuring may not help.

If the motivating evidence and proposed mechanism do not match, stop or reformulate the hypothesis. Lower cyclomatic complexity does not establish faster execution, and faster execution does not establish easier maintenance.

## Dependency, History, and Execution Evidence

Use static program slicing and a program-dependence graph when language-aware tooling is available. Inspect control dependencies, data dependencies, aliasing, mutable state, exception flow, synchronization, resource lifetime, callbacks, and transitive calls. Treat an approximate slice according to the tool's soundness and language coverage.

Use dynamic slicing, tracing, coverage, or process mining to learn which paths and interactions occur in recorded workloads. Never infer that an unobserved path is unreachable. Preserve trace identifiers, workload definitions, sampling, and instrumentation overhead.

Mine repository history when the hypothesis concerns responsibilities or change cost:

- co-change and temporal coupling;
- defect-fix concentration and churn;
- ownership and reviewer boundaries;
- recurring variant additions;
- callers and interfaces affected together.

Treat repository associations as observational evidence. Control obvious confounders and do not claim that complexity caused defects without a causal design.

## Refactoring Hypotheses and Candidates

Write each candidate as a falsifiable intervention:

> Changing **mechanism X** with **transformation Y**, under **preconditions P**, should improve **outcome Z** by the declared meaningful amount while satisfying **guardrails G**.

Generate the smallest plausible candidates. Depending on the diagnosed cause, consider algorithm/data-structure substitution, extracting a cohesive slice, isolating effects, replacing duplicated variant branching with an evidenced strategy/table, batching I/O, splitting or fusing traversals, or removing accidental recomputation. These are candidate mechanisms, not automatic prescriptions.

Apply one interpretable causal change at a time unless interactions are the explicit object of a factorial experiment. Record transformation preconditions and reject candidates that merely move complexity across files or hide it behind indirection.

## Behavioral Preservation

Define the semantic oracle before editing and cover all relevant observables: return values, errors, exceptions, mutation, ordering, timing contracts, resource use, logs/events, I/O, concurrency, and compatibility.

Use the smallest sufficient combination:

- **characterization tests**: capture legacy behavior when no complete specification exists; label accidental behavior and oracle gaps;
- **differential testing**: execute original and candidate on identical generated and recorded inputs and compare declared observables;
- **contracts/refinement**: check preconditions, postconditions, invariants, history constraints, and allowed nondeterminism;
- **property-based testing**: generate inputs from domain constraints and shrink counterexamples;
- **metamorphic testing**: verify justified relations when an exact oracle is unavailable;
- **mutation testing**: test whether the suite detects plausible semantic faults; inspect equivalent and stillborn mutants before interpreting the score;
- **formal equivalence or refinement tools**: use when supported, recording the modeled language fragment and proof assumptions.

For concurrent or distributed code, compare sets of allowed outcomes rather than forcing deterministic equality. Exercise schedule, retry, timeout, partial-failure, idempotency, and ordering properties as applicable. Passing finite tests supports preservation but does not prove it for an unbounded domain.

## Controlled Before/After Experiments

Treat the original and candidate as interventions on the same experimental units:

- pair by input, seed, process/fork, trace, or workload instance;
- randomize or interleave execution order and block by machine, time window, runtime state, or dataset when relevant;
- retain independent units instead of treating inner-loop iterations as independent samples;
- predeclare warmup, timed region, exclusions, stopping rule, noninferiority/effect threshold, and aggregation;
- report paired effect sizes, uncertainty, raw samples, and sensitivity to exclusions;
- replicate in a fresh process and another environment only when generalization is claimed.

Use a repeated single-system design when only one codebase exists: alternate baseline and candidate under controlled comparable workloads, inspect drift and carryover, and avoid attributing uncontrolled temporal changes to the refactor.

Remeasure end-to-end behavior after microbenchmarks. Reject a local speedup that has no material workload share or causes a guardrail regression.

## Comprehension Experiments

When the goal is human comprehension, measure humans rather than treating a source metric as the outcome. Use a randomized crossover design when feasible:

- recruit participants representative of intended maintainers and record experience;
- use equivalent held-out tasks such as predicting behavior, locating a defect, or implementing a change;
- counterbalance version/task order and account for learning and carryover;
- record correctness, completion time, navigation/actions, and predeclared subjective workload;
- keep evaluators blind to the favored candidate when possible;
- report participant-level paired effects and uncertainty.

Do not claim broad comprehension improvement from one reviewer, preference voting, or a lower Cognitive Complexity score.

## Multiobjective and Pareto Decisions

Separate hard guardrails from optimization objectives. Common objectives include latency, throughput, allocations, peak memory, I/O, structural contributors, mutation adequacy, task error/time, change surface, and implementation size. Declare whether each is minimized or maximized.

Candidate A Pareto-dominates B when A is no worse on every predeclared objective and strictly better on at least one. Retain the nondominated frontier; do not sum incompatible metrics or invent weights after seeing outcomes.

When several candidates remain nondominated:

1. eliminate candidates with unresolved semantic or operational risk;
2. apply the predeclared practical-effect thresholds;
3. prefer the smaller, more reversible change when outcomes are materially equivalent;
4. present the remaining trade-off to the user when stakeholder values are required.

A candidate need not dominate the baseline to be selected, but any accepted trade-off must name the sacrificed outcome, magnitude, rationale, and monitoring plan.

## Search-Based Refactoring

Use search-based software engineering only when the candidate space is too large for reasoned enumeration. Define legal transformation operators and their semantic preconditions. Predeclare objectives, constraints, budget, seed policy, and termination.

Separate data into generation/tuning, validation, and untouched holdout sets. Deduplicate semantically equivalent candidates, retain provenance, and rerun finalists from a clean baseline. Never optimize directly against the final test suite, a single structural metric, or a noisy one-shot benchmark.

Treat search output as exploratory. Validate finalists with the full semantic oracle, paired experiment, sensitivity analysis, and Pareto procedure. Search stability across seeds is evidence about the search process, not proof that a candidate is optimal.

## End-to-End Protocol

1. Confirm explicit authorization to modify code.
2. Define GQM goal, questions, metrics, guardrails, and decision rule.
3. Establish source, behavior, performance, structure, and environment baselines.
4. Diagnose the causal complexity using formal, static, dynamic, and history evidence.
5. State the refactoring hypothesis and transformation preconditions.
6. Build or strengthen the semantic oracle before the material edit.
7. Implement the smallest candidate and preserve independent provenance.
8. Run differential, property, metamorphic, mutation, and formal checks as applicable.
9. Run paired/interleaved performance or comprehension experiments where required.
10. Exclude guardrail failures before computing the Pareto frontier.
11. Retain, revise, or reject the candidate under the predeclared rule.
12. Rerun repository tests and end-to-end measurements; document limits and monitoring.

## Included Comparison Helper

Use `scripts/compare_refactorings.py` to summarize already collected numeric observations. It does not run benchmarks, test semantics, measure comprehension, or establish causality.

Provide one row per independent unit and variant:

```csv
unit,variant,latency_ms,alloc_bytes,cyclomatic,mutation_score,test_failures
run-1,baseline,10.2,5000,14,0.84,0
run-1,candidate-a,8.7,5100,8,0.91,0
run-2,baseline,10.5,4950,14,0.84,0
run-2,candidate-a,8.9,5050,8,0.91,0
```

```bash
python3 scripts/compare_refactorings.py results.csv \
  --baseline baseline \
  --minimize latency_ms,alloc_bytes,cyclomatic \
  --maximize mutation_score \
  --guardrail 'test_failures<=0' \
  --bootstrap 2000 --seed 7
```

The helper:

- validates one observation per unit/variant;
- aggregates each objective by median;
- computes direction-adjusted paired median effects and percentile bootstrap intervals at the unit level;
- requires every observation of a variant to satisfy each guardrail;
- reports missing pairs and weak designs;
- returns the nondominated frontier among eligible variants.

Repeat static candidate metrics across paired units only for table convenience; do not misrepresent those copies as independent observations. Predeclare objectives and guardrails. Pareto membership over observed medians is descriptive and can change with uncertainty or another workload.

## Required Report

Include:

- GQM goal, questions, metrics, guardrails, and decision rule;
- diagnosed complexity and causal evidence;
- baseline and hypothesis;
- dependency/slice/history/trace evidence;
- semantic oracle and its limits;
- candidate transformations and preconditions;
- paired effects, uncertainty, comprehension evidence, and guardrail results;
- Pareto frontier and retained trade-off;
- validation, rollback, and monitoring plan.

## Scientific Sources

- Basili, “Software Modeling and Measurement: The Goal/Question/Metric Paradigm,” [University of Maryland technical report](https://drum.lib.umd.edu/items/8119803a-362b-42ec-b6ce-2311713e7236).
- Mens and Tourwé, “A Survey of Software Refactoring,” [DOI 10.1109/TSE.2004.1265817](https://doi.org/10.1109/TSE.2004.1265817).
- Weiser, “Program Slicing,” [DOI 10.5555/800078.802557](https://doi.org/10.5555/800078.802557).
- Claessen and Hughes, “QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs,” [DOI 10.1145/351240.351266](https://doi.org/10.1145/351240.351266).
- Jia and Harman, “An Analysis and Survey of the Development of Mutation Testing,” [DOI 10.1109/TSE.2010.62](https://doi.org/10.1109/TSE.2010.62).
- Harman and Jones, “Search-Based Software Engineering,” [DOI 10.1016/S0950-5849(01)00189-6](https://doi.org/10.1016/S0950-5849(01)00189-6).
- van der Aalst, *Process Mining: Data Science in Action*, [DOI 10.1007/978-3-662-49851-4](https://doi.org/10.1007/978-3-662-49851-4).
- See the controlled-experiment, formal-proof, measurement-validity, decomposition, and behavioral-subtyping sources in the other reference files.
