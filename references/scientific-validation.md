# Scientific Validation and Falsification

Use this guide to test the reliability of material complexity, performance, structural, and design conclusions. Validation can expose errors and calibrate uncertainty; it cannot turn finite observations or reviewer agreement into mathematical proof.

## Contents

- Claim protocol
- Verification by evidence type
- Counterexamples and metamorphic testing
- Sensitivity and triangulation
- Confidence calibration
- Reproducibility
- Evaluating the skill itself
- Refactoring the skill when its own complexity grows
- Scientific sources

## Claim Protocol

Record these fields before presenting a material conclusion:

1. **Claim**: a precise, falsifiable statement with scope.
2. **Target**: implementation/version, input domain, size variables, case, workload, or design boundary.
3. **Assumptions**: operation contracts, distributions, environment, and excluded behavior.
4. **Evidence type**: exactly one primary label from `SKILL.md`.
5. **Verification**: the check performed independently enough to expose the likely error.
6. **Falsifier**: an observation, counterexample, contract change, or missing artifact that would overturn or weaken the claim.
7. **Confidence and limits**: support strength and external-validity boundary.

Prefer checks that fail differently from the original method. Restating a derivation, rerunning identical data, or asking the same model repeatedly is not independent validation.

## Verification by Evidence Type

### Formal claims

- Check upper- and lower-bound obligations separately before claiming `Theta`.
- Verify sums and recurrence solutions by substitution or induction when practical.
- Exhibit a witness family for worst-case or lower-bound claims.
- Check termination, reachable branches, recursion depth, output size, and called-operation contracts.
- Use abstract interpretation, symbolic execution, ranking functions, SMT, resource analyzers, or proof assistants when available and proportionate.
- Record each tool's language fragment, soundness claim, version, and unmodeled behavior. Tool output is `formal` only within a documented sound model; otherwise classify it as `contract`, `inferred`, or supporting evidence.

### Contract claims

- Cite the exact language/library/API version or inspect the implementation when no complexity contract exists.
- Test alternate valid implementations allowed by the contract. If the conclusion changes, state it conditionally.
- Distinguish specification guarantees from common implementation behavior.

### Measured claims

- Predeclare the estimand, minimum meaningful effect, independent experimental unit, exclusion rules, and stopping rule.
- Prefer randomized, blocked, paired/interleaved comparisons when evaluating alternatives.
- Report effect size and uncertainty, preserve raw samples, and run sensitivity analyses for exclusions and aggregation choices.
- Diagnose warmup, drift, heteroscedasticity, temporal dependence, cache/GC/JIT transitions, and saturation when they could alter the conclusion.
- Replicate on a fresh process and, when claiming portability, another relevant environment.

### Heuristic and design claims

- Declare the metric/rubric and its construct; do not substitute reproducibility for construct validity.
- Compare against a compatible local baseline and control obvious confounders such as LOC, language, generated code, and domain.
- For consequential subjective labels, use independent reviewers. Report raw agreement and an appropriate chance-corrected statistic; do not treat agreement as proof of correctness.
- Use repository history, co-change, defects, ownership, callers, and contracts to support SRP/OCP/DIP claims. Treat observational associations as noncausal unless a valid causal design exists.

## Counterexamples and Metamorphic Testing

Search boundary and adversarial families: empty/singleton/maximal inputs, skew, duplicates, hash collisions, aliasing, mutation, overflow, exceptions, lazy consumption, recursion depth, concurrency schedules, and I/O failures as applicable.

Use only metamorphic relations justified for the target. Examples:

- alpha-renaming or formatting should preserve semantic and asymptotic conclusions;
- adding bounded constant work should preserve the asymptotic class while allowing measured constants to change;
- duplicating an independent loop body changes a constant factor, not its growth class;
- adding an input-dependent nested traversal changes the bound only if its range and reachability justify the factor;
- replacing a container or API contract may legitimately change the conclusion and should appear in sensitivity analysis;
- semantically equivalent implementations should pass the same correctness oracle, while performance may differ.

Property-based generation, fuzzing, differential analyzers, and metamorphic tests can falsify conclusions. Passing them is supporting evidence, not proof for unbounded domains.

## Sensitivity and Triangulation

Create an assumption matrix when plausible alternatives change the answer. Report the conclusion under each contract, distribution, or environment rather than collapsing them into one value.

Triangulate only evidence that answers compatible questions. Formal bounds, API contracts, benchmarks, profiles, hardware counters, and repository history may reinforce one another, but they are not interchangeable. When they disagree, investigate hidden operation costs, model mismatch, finite-range effects, instrumentation, compiler behavior, or invalid inputs.

## Confidence Calibration

Treat `high`, `medium`, and `low` as ordinal until evaluated on held-out cases. On a labeled corpus, report accuracy or error rate by confidence label with uncertainty and an explicit error taxonomy. If numeric probabilities are emitted, evaluate calibration with reliability diagrams and a proper score such as Brier score; do not invent probability mappings after seeing outcomes.

Track especially:

- incorrect tight bounds and confused case/notation;
- omitted size variables, output costs, recursion space, or library contracts;
- measurements presented as proofs;
- heuristic metrics presented as causal or universal;
- unsupported certainty and missed `unknown` outcomes.

## Reproducibility

Preserve code revision, prompts/instructions, raw outputs, tool versions, commands, input generators and seeds, benchmark data, environment, exclusions, and analysis decisions. Separate exploratory work from predeclared confirmatory checks. A replication should rebuild the result from source artifacts without access to the expected answer.

## Evaluating the Skill Itself

Use a versioned, stratified corpus covering loops, data-dependent control flow, recursion, amortization, hashing, laziness, multiple parameters, output sensitivity, bit cost, parallelism, I/O, structural metrics, and design-context cases.

- Use proved answers for formal cases and documented tool conventions for exact structural counts.
- Treat SOLID judgments as rubric-based expert assessments, not objective ground truth.
- Obtain independent annotations, preserve disagreements, and adjudicate only after the initial labels are frozen.
- Compare skill versions with a randomized paired and blinded evaluation on the same held-out cases.
- Predeclare scoring for correctness, assumption coverage, unsupported certainty, reproducibility, and recommendation usefulness.
- Report paired effect sizes and uncertainty; use a test appropriate to the outcome rather than defaulting to a p-value.
- Run ablations to identify whether the evidence vocabulary, derivation rules, falsification step, or report schema causes the improvement.
- Keep a final untouched holdout set and prevent prompts, expected answers, and prior outputs from leaking into evaluation.
- Calibrate confidence on historical cases and verify it again on the holdout set.

Do not call reviewer consensus, self-consistency, or benchmark-curve fit a gold standard. Publish the corpus composition, exclusions, scoring rubric, raw anonymized ratings, and skill version needed for replication.

## Refactoring the Skill When Its Own Complexity Grows

Do not use line count alone. Refactor the skill when evidence shows instruction conflict, excessive unconditional context, degraded trigger precision/recall, repeated navigation errors, poor adherence, or a workflow branch that changes independently.

### Goal-Question-Metric

Define the skill-quality goal before reorganizing it. Derive questions and predeclared measures such as task correctness, unsupported-certainty rate, trigger precision/recall, tool/reference selection accuracy, instruction adherence, context tokens loaded, latency, and evaluator effort. Treat correctness and safety as guardrails rather than metrics that can be traded away silently.

### Hierarchical task analysis

Map the skill as `goal -> plans -> operations`:

1. triggering and scope selection;
2. reference routing;
3. evidence collection;
4. derivation or measurement;
5. validation/falsification;
6. optional refactoring;
7. report generation.

Split a branch into a direct reference when it has distinct triggers, artifacts, or validation rules. Keep shared invariants in `SKILL.md`. Avoid nested reference chains and duplication. Make the degree of freedom lower only for fragile, repeatable operations.

### Trigger corpus and confusion analysis

Maintain versioned positive, negative, and boundary prompts. Freeze expected trigger/routing labels before evaluation. Report precision, recall, false-positive/false-negative categories, and confidence intervals; do not optimize only for recall. Include near-neighbor tasks that should activate other skills or no skill.

### Factorial experiments

When several instruction components may interact, test presence/absence or ordering with a randomized full or fractional factorial design. Predeclare factors, interactions of interest, blocking variables such as task family/model/runtime, outcomes, and exclusions. Use ablation for isolated contribution and factorial analysis for interactions. Do not infer component value from one prompt or one ordering.

### Item Response Theory

Use IRT only when the response matrix contains enough genuinely different evaluated systems or agents, cases span useful difficulty, and model-fit/independence assumptions are checked. Estimate item difficulty and discrimination to diagnose the corpus and select balanced holdouts; retain ordinary per-category accuracy and error analysis. Do not interpret an unstable latent score as intrinsic skill quality or use IRT to hide failures on critical cases.

### Process mining and context cost

From privacy-safe event logs, model paths such as `request -> skill trigger -> reference loads -> tools -> validation -> outcome`. Use conformance checking to find skipped validations, unnecessary loads, loops, and overloaded branches. Logs show observed behavior, not causal necessity; preserve consent, redaction, sampling, and version metadata.

Measure context cost experimentally: unconditional and conditional tokens loaded, task accuracy, missed instructions, latency, and tool calls. Compare monolithic and modular variants on the same randomized held-out tasks. Prefer a modular variant only when it preserves guardrails and is Pareto-superior or has an explicit justified trade-off.

### Regression and stopping rule

After restructuring, rerun syntax validation, script self-tests, trigger/routing cases, held-out task evaluation, calibration, and blinded forward-tests. Stop decomposing when further splits add navigation failures or no practically meaningful benefit. Preserve the previous version and record rollback criteria.

## Scientific Sources

- Wohlin et al., *Experimentation in Software Engineering*, [DOI 10.1007/978-3-642-29044-2](https://doi.org/10.1007/978-3-642-29044-2).
- Chen et al., “Metamorphic Testing: A Review of Challenges and Opportunities,” [DOI 10.1145/3143561](https://doi.org/10.1145/3143561).
- Cohen, “A Coefficient of Agreement for Nominal Scales,” [DOI 10.1177/001316446002000104](https://doi.org/10.1177/001316446002000104).
- Brier, “Verification of Forecasts Expressed in Terms of Probability,” [DOI 10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2](https://doi.org/10.1175/1520-0493(1950)078%3C0001:VOFEIT%3E2.0.CO;2).
- Basili, “Software Modeling and Measurement: The Goal/Question/Metric Paradigm,” [University of Maryland technical report](https://drum.lib.umd.edu/items/8119803a-362b-42ec-b6ce-2311713e7236).
- Annett and Duncan, “Task Analysis and Training Design,” [ERIC ED019566](https://eric.ed.gov/?id=ED019566).
- Lalor, Wu, and Yu, “Building an Evaluation Scale Using Item Response Theory,” [PMC5167538](https://pmc.ncbi.nlm.nih.gov/articles/PMC5167538/).
- van der Aalst, *Process Mining: Data Science in Action*, [DOI 10.1007/978-3-662-49851-4](https://doi.org/10.1007/978-3-662-49851-4).
- See the formal-proof, benchmarking, measurement-validity, and behavioral-subtyping sources in the other reference files.
