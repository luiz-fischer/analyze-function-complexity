# Targeted Cognitive Complexity Refactoring

Use this protocol when the user explicitly asks to reduce a method's Cognitive
Complexity to a target threshold, especially by extracting focused helpers. Apply
it together with `refactoring-experiments.md`.

Treat the threshold as an acceptance policy under a named metric convention, not
as a universal scientific boundary. Reduce accidental control-flow difficulty
without merely moving it outside the measured method.

## Contents

- Freeze the target and acceptance contract
- Establish a reproducible baseline
- Build a complexity map
- Strengthen the behavioral oracle
- Select cohesive transformations
- Refactor incrementally
- Apply the final acceptance gate
- Required evidence

## 1. Freeze the Target and Acceptance Contract

Before editing, record:

- the fully qualified target method and source revision;
- the requested threshold;
- the analyzer, rule, version, configuration, and language plugin;
- the authorized source and test scope;
- public signatures, compatibility requirements, and project conventions;
- build, targeted-test, broader-test, and metric commands;
- required observables: return values, validation order, exception types and
  messages, mutation, ordering, logs/events, I/O, resource lifetime, timing
  contracts, and allowed concurrent outcomes as applicable.

Use the repository's established commands and language-aware analyzer. If the
metric tool or its convention is unavailable, report the final metric as
`unknown`; do not invent a count or claim that the threshold was met.

## 2. Establish a Reproducible Baseline

Before the material edit:

1. Compile or build the relevant target.
2. Run the existing tests related to the method and surrounding behavior.
3. Record command, exit code, runner identity, and the actual pass/fail summary.
4. Measure the target method and list every increment and nesting contribution.
5. Record maximum nesting and inspect the nearby call path for displaced
   complexity.

Confirm zero failing tests from runner evidence. When the runner emits an
explicit failure count, quote or record the exact summary and verify that the
count is zero. When it does not, use its documented success contract, exit code,
and completion summary; never fabricate the literal text `failed=0`.

Preserve complete logs when output may be truncated. Search the artifact for the
summary and inspect every reported failure. Reading an arbitrarily large log
line-by-line is unnecessary when the runner provides a reliable structured or
terminal summary.

If the baseline does not compile or already has failing tests, distinguish those
pre-existing failures from candidate regressions. Do not claim full behavioral
preservation until the acceptance contract can resolve them.

## 3. Build a Complexity Map

Map the constructs that contribute under the selected analyzer:

- nested `if`, `else`, pattern, ternary, and exception branches;
- long decision chains or variant dispatch;
- loops containing conditional control flow;
- short-circuit or otherwise difficult boolean expressions;
- local functions, recursion, jumps, and early exits;
- repeated blocks and independently changing responsibilities;
- validation mixed with transformation, persistence, transport, or presentation;
- data, control, aliasing, exception, state, and resource-lifetime dependencies.

Rank contributors by causal relevance to the requested metric and to the
maintenance task. Separate essential domain branching from accidental
implementation complexity.

## 4. Strengthen the Behavioral Oracle

Strengthen the smallest sufficient oracle before editing. Cover boundary and
adversarial cases such as null or missing values, empty collections, duplicates,
invalid variants, overflow, partial failure, ordering, and concurrency where
applicable.

Use characterization, differential, property-based, metamorphic, mutation, or
contract tests according to risk. Preserve exact exception types and messages
when they are observable contracts. Passing finite tests supports preservation;
it does not prove equivalence over an unbounded domain.

## 5. Select Cohesive Transformations

Choose the smallest transformation that addresses a mapped contributor:

- use a guard clause when it reduces nesting without changing validation or
  side-effect order;
- name a complex boolean predicate when the name exposes domain intent;
- extract validation only when it forms a coherent contract;
- extract a cohesive data/control slice with explicit inputs and outputs;
- consolidate genuinely repeated behavior without merging merely similar cases;
- use a table, `switch`, pattern dispatch, strategy, or handler only when it
  matches an evidenced variation axis;
- isolate type-specific processing when its contract and dependencies are
  distinct.

Treat `private`, `static`, local, synchronous, asynchronous, tuple, record, or
named-result choices as language- and contract-dependent. Make a helper static
only when it requires no instance state or substitutable behavior. Do not
introduce asynchronous behavior solely to restructure control flow.

Give every helper one describable responsibility and a name that states intent.
Keep it near its use when project conventions allow. Avoid excessive parameters,
boolean mode flags, hidden mutable dependencies, unnecessary locals, speculative
abstractions, or result tuples whose fields need explanation.

Reject an extraction that only hides complexity behind indirection. Inspect:

- complexity and nesting of every new or materially changed helper;
- aggregate contributors across the small call path;
- call depth and navigation cost;
- duplication, coupling, parameter flow, and mutable state;
- exception, resource, and concurrency boundaries.

## 6. Refactor Incrementally

Apply one interpretable transformation at a time:

1. State the contributor and expected metric delta.
2. Verify the extraction preconditions and dependency slice.
3. Make the smallest edit.
4. Compile.
5. Run the relevant tests.
6. Inspect the actual result and failure summary.
7. Measure again when the delta informs the next change.

Do not stack additional edits on a failing candidate. If compilation or tests
fail, record the failure count when available, analyze each failure, identify the
changed condition, state transition, null/empty handling, ordering, or exception
behavior responsible, correct it, and rerun the same checks until they show zero
failures.

## 7. Apply the Final Acceptance Gate

Accept the refactoring only when all applicable checks succeed:

- the relevant code compiles with exit code zero;
- targeted tests and the broader suite proportional to the change risk report
  zero failures;
- all observed regressions have been analyzed and corrected;
- the same analyzer and configuration report target complexity less than or
  equal to the requested threshold;
- helpers and the nearby call path do not reveal unjustified complexity
  displacement;
- required behavior, interfaces, errors, effects, and project conventions remain
  satisfied.

Running a command is not evidence that it passed. Inspect its exit status and
result. If any required check cannot run or its output is ambiguous, mark that
acceptance item `unknown` or `failed` and do not report the refactor as complete.

## Required Evidence

Report:

| Item | Required evidence |
|---|---|
| Target | Method, source revision, requested threshold |
| Metric baseline | Value, contributors, analyzer/version/configuration |
| Intervention | Extracted or simplified responsibility and preconditions |
| Behavior | Oracle used, boundary cases, and known limits |
| Compilation | Exact command and exit status |
| Tests | Exact commands, runner summaries, and verified failure count |
| Metric result | Final value under the same convention and target comparison |
| Displacement check | Helper/call-path complexity, coupling, and duplication |
| Verdict | `accepted`, `rejected`, or `unknown`, with unmet gates |

Never replace missing test, compilation, or metric evidence with confidence
language.
