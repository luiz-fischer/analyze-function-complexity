---
name: analyze-function-complexity
description: Analyze, independently validate, optimize, or refactor a function or method across formal algorithmic time/space complexity, structural complexity, measured runtime performance, and SOLID applicability; also evaluate this skill's own workflow complexity when explicitly requested. Use for single-agent or multi-agent analysis involving Big O/Theta/Omega, best/worst/expected/amortized cost, scaling or bottlenecks, benchmarking/profiling, cyclomatic/NPath/cognitive complexity, maintainability, counterexamples, reproducibility, uncertainty, parallel validation, complexity reduction, behavior-preserving refactoring, or function-level SOLID review. Separates proofs, contracts, measurements, inferences, and heuristics; requires explicit assumptions, falsifiers, guardrails, and limits.
---

# Analyze Function Complexity

## Purpose

Produce an evidence-aware analysis of a function, method, closure, or small call path. Treat these as separate questions:

1. **Algorithmic complexity**: growth under an explicit mathematical cost model.
2. **Runtime performance**: observed cost for a specified workload and environment.
3. **Structural complexity**: control-flow or source-code properties used as review signals.
4. **SOLID**: contextual design principles, evaluated only where the surrounding contracts make them applicable.
5. **Experimental refactoring**: an explicitly requested, behavior-preserving intervention evaluated against predeclared goals and guardrails.
6. **Skill quality**: trigger, routing, context-cost, and workflow complexity evaluated only when this skill itself is the requested subject.
7. **Multi-agent validation**: independent evidence lanes coordinated without treating model agreement as proof or allowing concurrent measurements to contaminate one another.

Never present one dimension as proof of another. A low cyclomatic score does not imply speed; a fast benchmark does not establish asymptotic complexity; SOLID is not a numeric quality scale.

Answer in the user's language. Analyze only unless the user also asks to optimize or refactor.

## Load the Relevant Guidance

- Read [references/algorithmic-complexity.md](references/algorithmic-complexity.md) for every formal complexity analysis.
- Read [references/performance-measurement.md](references/performance-measurement.md) when performance, scaling, benchmarking, profiling, allocation, latency, throughput, cache, I/O, or concurrency matters.
- Read [references/structural-and-solid.md](references/structural-and-solid.md) when reviewing code metrics, maintainability, test-path complexity, or SOLID.
- Read [references/scientific-validation.md](references/scientific-validation.md) when a conclusion is high-impact, disputed, surprising, dependent on uncertain assumptions, or when evaluating the skill itself. Apply the compact claim-validation protocol below to every material conclusion.
- Read [references/refactoring-experiments.md](references/refactoring-experiments.md) completely when the user asks to optimize, simplify, decompose, or refactor code. Do not load it for analysis-only requests.
- Read [references/multi-agent-validation.md](references/multi-agent-validation.md) completely when the user requests multiple agents or parallel validation, or when the activation criteria below require independent validators.

## Evidence Vocabulary

Label important findings with exactly one primary evidence type:

| Label | Meaning |
|---|---|
| `formal` | Derived and checked from a declared model, assumptions, and proof obligations. |
| `contract` | Supported by a language, library, data-structure, or API contract. |
| `measured` | Observed in a recorded environment and workload. |
| `heuristic` | A review signal or proxy whose interpretation is contextual. |
| `inferred` | Plausible from incomplete context, but not yet demonstrated. |
| `unknown` | Evidence is insufficient; state what would resolve it. |

Use confidence (`high`, `medium`, `low`) separately from evidence type. For every material conclusion, record how it was verified and what observation, counterexample, contract change, or missing context could overturn it. Do not upgrade an inference to a fact by assigning high confidence.

- `high`: the claim survived a suitable independent check or replicated measurement, with no unresolved assumption likely to change it;
- `medium`: one defensible evidence path supports it, but verification, representativeness, or a material assumption remains limited;
- `low`: the claim is tentative, proxy-based, or depends on substantial missing context.

These labels are ordinal review judgments unless calibrated against a held-out corpus. Do not translate them into probabilities without empirical calibration.

## Multi-Agent Execution

Keep the main agent responsible for scope, preregistration, scheduling, conflict resolution, authorization boundaries, and the final report. Use a flat fan-out/fan-in topology: validators do not delegate or communicate with one another. Use one execution mode:

- **Sequential**: use for low-risk, narrow questions that have one defensible evidence route and do not request independent validation.
- **Multi-agent**: use when the user requests it, a refactoring spans at least two evidence dimensions, a material claim is high-impact/disputed/surprising, or independent formal and empirical checks are both feasible.

Before delegation, freeze an immutable task packet containing the target source or path and revision, relevant contracts, size variables, cost model, workloads, material claim IDs, assumptions to challenge, allowed commands, and authorization limits. Do not include the coordinator's expected answer or another validator's conclusions.

Ensure every claim that triggered multi-agent validation receives two sealed evidence routes; one validator may cover several claim IDs. Add a third lane only when it addresses a distinct evidence dimension or after disagreement as an explicitly labeled adjudicator. Choose from the bundled model-neutral profiles:

- [afc-formal-complexity-validator](agents/afc-formal-complexity-validator.md): proof obligations, bounds, cost models, recurrences, witnesses, and counterexamples;
- [afc-empirical-performance-validator](agents/afc-empirical-performance-validator.md): profiling, benchmark design, scaling evidence, uncertainty, and measurement threats;
- [afc-structural-refactoring-validator](agents/afc-structural-refactoring-validator.md): CFG and maintainability signals, SOLID applicability, behavioral oracles, and refactoring guardrails.

Use named profiles when the host discovers them. Otherwise spawn generic isolated workers with the corresponding profile body and frozen task packet. If the host cannot delegate, execute the same lanes sequentially with separate evidence notes and disclose the fallback.

Run source inspection, formal derivation, counterexample search, and oracle design in parallel when they are read-only and independent. Never run timing benchmarks, profilers, load tests, or other resource-sensitive measurements concurrently in the same physical contention domain. Use one controlled measurement queue per host unless CPUs, memory, storage, networks, caches, thermal/power behavior, and background load are demonstrably isolated; containers or core pinning alone do not establish this. Use separate worktrees or sequential execution for commands that can mutate source, generated files, build caches, databases, or fixtures. Validators must not edit the target; the coordinator is the sole writer unless the user explicitly authorizes isolated candidate branches.

Do not hard-code a role to Claude, Kimi, DeepSeek, or any other model family. When heterogeneous models are available, rotate or randomize role assignment across replicated evaluations so model and role are not confounded. Record the host and model identifiers when known. Agreement among models is corroboration only, not statistical independence, formal proof, or experimental replication.

Require every validator to return a self-contained handoff containing scope, claim IDs, findings, primary evidence labels, verification performed, assumptions, falsifiers or limits, confidence, commands/tools, shared dependencies, whether peer outputs were seen, an independence classification (`independent-check`, `robustness-check`, `repeatability-only`, or `adjudication`), and unresolved disagreements. Use [references/validator-handoff.schema.json](references/validator-handoff.schema.json) when the host supports structured output; otherwise return its Markdown equivalent. The coordinator must retain every first-round handoff, compare evidence paths, preserve dissent, rerun invalid lanes when possible, and resolve claims by evidence quality rather than majority vote.

## Workflow

### 1. Establish Scope Before Calculating

Inspect the function and enough surrounding code to understand:

- language/runtime and relevant compiler or interpreter behavior;
- callers, callees, overloads, callbacks, and error paths;
- input domains, data structures, mutability, and side effects;
- library operations whose cost dominates the body;
- contracts and types needed for SOLID applicability;
- whether code is generated, declarative, or performance-critical.

Define every independent size variable, such as `n` elements, `m` keys, string length `L`, graph vertices `V` and edges `E`, or precision `b`. Do not silently collapse variables unless a relationship is known.

State the material claims before testing them. For each one, identify the assumptions most likely to change the answer and a plausible falsifier or counterexample family.

If critical context is absent, make the narrowest reasonable assumptions and mark them. Ask only when different answers would materially change the result and the context cannot be inspected.

### 2. Derive Formal Time and Space Complexity

Declare the cost model and the case being analyzed. Distinguish:

- `O` upper bound, `Omega` lower bound, and `Theta` tight bound;
- best, worst, and expected cases;
- per-operation, amortized sequence cost, and total batch cost;
- auxiliary space from total space and output storage;
- exact count, asymptotic class, and practical constant factors.

Show a compact derivation rather than stating a class without support. Use sums for dependent loops, recurrences for recursion, and documented operation costs for containers or library calls. Report output-sensitive, multi-parameter, work/span, cache/I/O, bit, or parameterized complexity when the ordinary RAM model would hide a relevant cost.

Use `formal` only after checking the required upper/lower-bound argument, recurrence solution, or space bound under the declared contracts. When practical, use a second route such as substitution, induction, a symbolic/resource-analysis tool with documented assumptions, or an explicit witness family. A benchmark, profiler, or repeated model answer is not a formal verification.

Do not infer an expected bound without an input distribution. Do not call amortized analysis “average case.”

### 3. Evaluate Structural Complexity

Use structural metrics only when they answer a review question. Prefer language-aware AST/CFG tooling already present in the repository, and record tool/version/conventions.

At minimum, describe control-flow contributors and nesting. Calculate cyclomatic complexity when a defensible CFG or documented tool convention is available. Use NPath/ACPATH, Cognitive Complexity, Halstead, or Maintainability Index only under the limits in the reference.

Never invent precise counts from syntax a tool treats ambiguously. Never combine heterogeneous metrics into a homemade score or use a universal threshold as scientific fact.

For subjective classifications, preserve dissent instead of manufacturing consensus. When the decision matters, use independent reviewers or repository-history evidence and report agreement separately from correctness.

### 4. Measure Performance When Evidence Requires It

Static inspection may identify likely costs but cannot produce runtime measurements. If runnable code and representative inputs exist, choose the smallest valid method:

- profile an end-to-end workload to locate real hotspots;
- microbenchmark an isolated operation to compare implementations or study scaling;
- use tracing or load tests for latency tails, contention, or distributed/I/O behavior;
- inspect allocation, cache, branch, I/O, or synchronization counters only when they test a stated hypothesis.

Use the ecosystem's established harness, optimized/release code, validated outputs, warmup where needed, multiple independent repetitions, representative and adversarial inputs, and a recorded environment. Prevent dead-code elimination and constant folding. Do not run load tests against production or external systems without explicit authorization.

For empirical scaling, geometric input sizes and repeated samples are preferred. The helper can summarize a CSV:

```bash
python3 scripts/analyze_scaling.py measurements.csv --size-column n --time-column time
python3 scripts/analyze_scaling.py --self-test
```

Treat fitted models as diagnostics, never proof of Big O. Profile before optimizing and remeasure after each material change.

### 5. Assess SOLID Only Where Applicable

Evaluate each principle with one of these statuses:

- `conforms`
- `risk`
- `violation-with-evidence`
- `not-applicable`
- `insufficient-evidence`

For every applicable principle, name the scope, code evidence, relevant contract or change axis, impact, confidence, and trade-off. Do not issue a percentage, stars, aggregate score, or automatic pass/fail.

Function-level applicability is intentionally limited:

- **SRP**: inspect cohesion and independent reasons/actors for change; length alone is not a violation.
- **OCP**: requires an observed or explicitly expected variation axis; avoid speculative abstraction.
- **LSP**: requires subtype, override, implementation, or callback substitutability and its behavioral contract.
- **ISP**: requires an interface boundary and actual consumers; parameter count alone is irrelevant.
- **DIP**: requires policy/dependency context; dependency injection is a technique, not proof of compliance.

Expand inspection to callers, types, interfaces, and dependency edges when needed. Otherwise mark the principle not applicable or evidence insufficient.

### 6. Validate and Try to Falsify Material Claims

For each material conclusion:

1. state the claim, scope, assumptions, and evidence type;
2. select a verification route that is independent enough to expose the likely error mode;
3. search for boundary, adversarial, and counterexample inputs;
4. use metamorphic checks when transformations have known effects on semantics or complexity;
5. vary uncertain contracts or input distributions and report whether the conclusion is robust;
6. investigate disagreements among proof, contract, measurement, and tooling instead of averaging them.

A failed falsification attempt increases confidence only within the attempted domain; it does not prove the claim. Repeated answers from the same model are not independent replication. If verification is unavailable, say so and retain `inferred` or `unknown` where appropriate.

When multi-agent execution is active, apply the synthesis and failure rules in `references/multi-agent-validation.md`. Do not expose one validator's conclusion to another before their initial handoffs are frozen.

### 7. Decide Whether Refactoring Is Justified

Do not treat a high metric, long function, or generic threshold as authorization or sufficient evidence to refactor. When the user requests a change:

1. use Goal-Question-Metric to state the goal, questions, success metrics, and hard guardrails;
2. classify the target problem as algorithmic, measured-runtime, structural, design, or a combination;
3. establish behavioral, performance, structural, and interface baselines relevant to that goal;
4. identify the smallest causal contributor and the evidence that changing it should help;
5. decline or narrow the refactor when the expected benefit is unsupported or the validation oracle is inadequate.

### 8. Run Refactoring as a Controlled Intervention

Follow the experimental protocol in `references/refactoring-experiments.md`:

1. map data/control dependencies, side effects, callers, and observed execution paths;
2. state a falsifiable refactoring hypothesis and transformation preconditions;
3. preserve behavior with contracts, differential tests, properties, metamorphic relations, and mutation adequacy as applicable;
4. change one interpretable causal unit at a time, keeping candidates independently reproducible;
5. compare original and candidates with paired/interleaved measurements and comprehension evidence when relevant;
6. enforce semantic and operational guardrails before ranking candidates;
7. use Pareto dominance across predeclared objectives instead of a homemade aggregate score;
8. retain the original when no candidate has a justified trade-off.

The helper can summarize paired numeric outcomes and Pareto eligibility:

```bash
python3 scripts/compare_refactorings.py results.csv \
  --baseline baseline --minimize latency_ms,alloc_bytes,cyclomatic \
  --maximize mutation_score --guardrail 'test_failures<=0'
python3 scripts/compare_refactorings.py --self-test
```

Search-based refactoring may generate candidates, but never let the search see held-out validation cases or bypass transformation preconditions. Treat its output as exploratory until independently validated.

Keep validation agents read-only. The coordinator may implement the selected intervention only after behavioral guardrails and ownership boundaries are explicit; use isolated candidate worktrees when more than one implementation is intentionally explored.

### 9. Prioritize Findings Without Conflation

Rank recommendations by observed or demonstrated impact:

1. correctness and semantic risks;
2. proven scaling bottlenecks at expected constraints;
3. measured hotspots or regressions;
4. structural and design risks supported by change/test context;
5. speculative improvements, clearly labeled.

For each recommendation, state expected benefit, trade-offs, and how to validate it. Do not recommend refactoring solely to lower a metric, and do not sacrifice clarity for a lower asymptotic class that does not matter at the actual scale.

## Required Report Shape

Adapt depth to the request, but keep these sections or their concise equivalents:

```markdown
## Conclusion
One direct outcome, including the dominant risk or “no material issue found.”

## Scope and assumptions
- Function/call path, inputs and size variables
- Cost model and analyzed cases
- Runtime/workload/tool context, or what is unavailable

## Evidence matrix
| Dimension | Finding | Evidence | Verification | Confidence | Falsifier / limits |
|---|---|---|---|---|---|

## Derivation and measurements
Formal derivation, structural contributors, and measured results kept distinct.

## Validation performed
Counterexamples, metamorphic checks, sensitivity analysis, independent checks, disagreements, and unavailable validation.

## Multi-agent validation (when used)
Execution mode, frozen task packet, validator lanes, host/model identifiers when known, isolation, handoff status, disagreements, invalidated lanes, serialized measurements, and sequential fallback.

## Refactoring experiment (when requested)
Goal-Question-Metric plan, baseline, hypothesis, dependency/slice evidence, semantic oracle, candidates, guardrails, paired effects, Pareto frontier, and retained trade-off.

## SOLID applicability
| Principle | Status | Scope and evidence | Impact/trade-off |
|---|---|---|---|

## Recommendations
Prioritized actions and a concrete validation method.
```

When the available evidence does not justify a number or conclusion, say `unknown` and identify the missing contract, input distribution, benchmark, profile, or caller context.
