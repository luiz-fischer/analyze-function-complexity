# Multi-Agent Validation Protocol

## Contents

1. [Purpose](#purpose)
2. [Activation and lane selection](#activation-and-lane-selection)
3. [Preregister the task packet](#preregister-the-task-packet)
4. [Validator roles](#validator-roles)
5. [Scheduling and isolation](#scheduling-and-isolation)
6. [Independence and contamination controls](#independence-and-contamination-controls)
7. [Heterogeneous model use](#heterogeneous-model-use)
8. [Handoff contract](#handoff-contract)
9. [Synthesis and disagreement](#synthesis-and-disagreement)
10. [Critical council escalation](#critical-council-escalation)
11. [Refactoring ownership](#refactoring-ownership)
12. [Failure and fallback](#failure-and-fallback)
13. [Host adapters](#host-adapters)

## Purpose

Use multiple agents to obtain independent evidence paths, isolate verbose work, and expose different failure modes. Do not use agent count, model diversity, or answer agreement as evidence by itself.

The coordinator owns the question, preregistration, frozen inputs, permissions, scheduling, final synthesis, and any source modification. Validators own narrow read-only evidence lanes and return auditable handoffs.

Keep the topology flat: coordinator fan-out, sealed validator handoffs, then coordinator fan-in. Validators must not delegate, communicate directly with one another, or synthesize sibling results.

## Activation and lane selection

Use multi-agent validation when at least one condition holds:

- the user explicitly requests multiple agents or parallel validation;
- a refactoring changes behavior-sensitive code and targets two or more dimensions;
- a material claim is disputed, surprising, high-impact, or assumption-sensitive;
- formal and empirical checks can independently address the same decision;
- the analysis spans a call path large enough that independent context reduces omission risk.

Prefer sequential execution when the target is small, one evidence route is sufficient, runnable artifacts are absent, or coordination cost exceeds the expected risk reduction.

Choose only the relevant lanes. Ensure each claim that triggered multi-agent validation receives two sealed evidence routes; one validator may cover multiple claim IDs. A third validator may cover a genuinely different evidence dimension or adjudicate a frozen disagreement, but an adjudicator is not a retroactive independent replicate. Two strong independent lanes are better than three duplicated opinions. Use no more than three validators by default.

Before selecting the mode, detect only the capabilities needed by the protocol: isolated spawning, parallel spawning, command execution, structured output, worktree isolation, and controlled write access. Do not assume that a model name implies any host capability.

## Preregister the task packet

Create the packet before any validator begins. Freeze it by content hash, revision identifier, or an equivalent immutable snapshot. Include:

- target source, paths, revision, and surrounding contracts;
- question and material claim IDs without expected conclusions;
- input domains, size variables, cases, and cost model;
- workload definitions and environment constraints when measurement is allowed;
- hypotheses, candidate falsifiers, and known uncertainty sources;
- estimands, practical thresholds, experimental units, exclusions, sample budgets, stopping rules, and measurement-order seeds when applicable;
- permitted tools, commands, paths, networks, and external systems;
- write restrictions and authorization boundaries;
- required handoff fields and completion deadline.

Pass the same raw facts to validators that address the same claim. Add role-specific questions, but do not add the coordinator's preferred answer, another validator's output, or the intended refactoring.

## Validator roles

### Formal complexity validator

Use for bounds, dependent loops, recursion, amortized analysis, output sensitivity, and space claims. Require a declared cost model, proof obligations for the stated bound, an independent check route when practical, and explicit witness or counterexample families.

### Empirical performance validator

Use for profiling, scaling, allocations, latency, throughput, cache, I/O, and concurrency claims. Require a measurement plan, environment record, output validation, repetitions, uncertainty, diagnostics, and threats to validity. Fitted scaling is empirical evidence, never proof of Big O.

### Structural and refactoring validator

Use for CFG-based metrics, nesting, test-path complexity, SOLID applicability, behavioral equivalence, mutation adequacy, and refactoring guardrails. Require documented metric conventions and distinguish design heuristics from demonstrated defects.

## Scheduling and isolation

Parallelize only independent, read-only work such as:

- source and contract inspection;
- formal derivations using different proof routes;
- counterexample and boundary-input search;
- test-oracle and metamorphic-relation design;
- static metric calculation on an immutable snapshot.

Serialize or physically isolate:

- timing benchmarks and profilers;
- load, stress, contention, and concurrency experiments;
- allocation, cache, branch, disk, and network measurements;
- commands sharing build caches, databases, ports, fixtures, or generated files;
- source edits and candidate transformations.

Concurrent measurements on one host can change CPU frequency, scheduler behavior, cache state, memory pressure, I/O queues, thermal state, and background load. Treat such results as contaminated unless isolation was demonstrated. Containers and core pinning do not by themselves isolate shared caches, memory bandwidth, turbo or power limits, thermal state, storage, or network paths.

When isolation is necessary, use separate worktrees and task-specific temporary directories. For performance experiments, prefer one controlled measurement queue per physical contention domain, managed by the coordinator. When separate machines are used, treat machine as a block, estimate effects within machine, and report between-machine heterogeneity.

## Independence and contamination controls

- Start validators in fresh contexts when the host supports it.
- Give validators raw artifacts rather than summaries that encode a conclusion.
- Do not reveal sibling identities, answers, confidence, or votes before initial handoffs are frozen.
- Keep held-out validation cases hidden from candidate generation and refactoring search.
- Record shared references, tools, datasets, and model families because they create correlated error.
- Do not ask validators to reproduce hidden reasoning; request evidence, derivations, commands, and falsifiers.
- Reopen a lane only with new evidence or a specific contradiction, and retain its original handoff.
- Freeze and retain all first-round handoffs before adjudication so unfavorable outputs cannot be silently discarded.

Independence is procedural and limited. Agents using related models, the same documentation, or the same benchmark harness are not statistically independent samples.

Classify each lane honestly:

- `independent-check`: a sealed output using a meaningfully different verification route;
- `robustness-check`: separate analysis sharing a major model, dataset, tool, or protocol dependency;
- `repeatability-only`: a rerun using essentially the same model, prompt, data, and method.

## Heterogeneous model use

Agent profiles are model-neutral. A host may route lanes to Claude, Kimi, DeepSeek, or another capable model.

When more than one model family is available:

1. assign roles without showing prior answers;
2. avoid permanently binding one model family to one role;
3. rotate or randomize model-role assignment across repeated evaluations;
4. record provider, model identifier, host, and relevant settings when available;
5. compare evidence quality, not model reputation or vote count.

Model heterogeneity may expose correlated reasoning failures, but agreement is only corroboration. It cannot establish a theorem, calibrated probability, or experimental replication.

## Handoff contract

When the host supports structured output, return JSON conforming to [validator-handoff.schema.json](validator-handoff.schema.json). Otherwise return one self-contained Markdown handoff with this equivalent shape:

```markdown
## Validator verdict
One scoped conclusion or `insufficient evidence`.

## Scope
- Role and assigned claim IDs
- Artifact revision or hash
- Inputs, cases, cost model, and environment used
- Independence classification, shared dependencies, and whether peer outputs were seen

## Evidence
| Claim ID | Finding | Evidence type | Verification | Confidence | Falsifier / limit |
|---|---|---|---|---|---|

## Checks performed
- Derivations, counterexamples, tests, tools, and commands
- For measurements: raw-data reference, experimental unit, host block, order seed, concurrent load, and exclusions

## Assumptions and threats
- Material assumptions, contamination risks, and missing context

## Disagreements and unknowns
- Conflicts within the evidence and what would resolve them
```

Use the skill's evidence vocabulary exactly. Never include hidden chain-of-thought. A compact derivation, observable evidence, and reproducible commands are sufficient.

## Synthesis and disagreement

The coordinator must:

1. verify that each lane used the frozen artifact and stayed within scope;
2. reject or rerun contaminated, unauthorized, or incomplete lanes;
3. align findings by claim ID rather than merging prose;
4. distinguish genuinely independent evidence from duplicated reasoning;
5. resolve conflicts using contracts, proof validity, measurement quality, and representativeness;
6. preserve unresolved dissent in the final evidence matrix;
7. label any post-disagreement third pass as adjudication rather than replication;
8. lower confidence when a material disagreement cannot be resolved.

Never average complexity classes, confidence labels, metric values produced under different conventions, or incompatible benchmark environments. Never decide truth by majority vote. An unresolved material disagreement prevents `high` confidence.

## Critical council escalation

Technical validators and a critical council serve different purposes. Validators create and challenge claim-level evidence through formal, contractual, measured, structural, or falsification routes. The council is a second-stage, decision-level deliberation that consumes frozen validator handoffs; it must not rerun the same lanes as opinion polling or create a `consensus` evidence label. Rank only complete council opinions that answer the same frozen decision, never the complementary formal, empirical, and structural handoffs themselves.

Read [critical-council.md](critical-council.md) completely when the user explicitly requests a council, panel, jury, or blind review. Without an explicit request, escalate only when a consequential decision remains unresolved after valid ordinary checks because evidence lanes materially disagree, multiple options remain Pareto-eligible, or assumptions and trade-offs can change the preferred action, and the frozen evidence can be reviewed without new technical experiments. Missing proofs, contracts, behavioral oracles, or representative measurements require more evidence or an `unknown` result, not a vote.

Standard mode adds three read-only independent members, two fresh blind reviewers, and the coordinator as chair after first-round technical handoffs are frozen. Use the bundled member and reviewer profiles and `../scripts/critical_council.py`; no external council skill is a dependency. If the host cannot produce at least two isolated opinions, continue with ordinary coordinator synthesis and explicitly state that no council formed. The blind aggregate is advisory, and decisive technical evidence or a credible unresolved safety objection overrides ranking.

## Refactoring ownership

Keep validators read-only by default. The coordinator is the sole writer and applies at most one interpretable causal change before revalidation.

If multiple implementation candidates are explicitly authorized, give each candidate a separate worktree and a disjoint owner. Freeze each resulting revision, then validate candidates against the same held-out oracle and controlled measurement queue. Do not let a candidate author grade its own result without an independent lane.

## Failure and fallback

If a validator times out, fails, lacks a required tool, or violates isolation:

- mark the lane invalid or incomplete rather than inferring its result;
- continue with remaining valid evidence when the decision is still supportable;
- retry once with a narrower task or execute the lane sequentially;
- report the fallback and its effect on confidence;
- return `unknown` when the missing lane is necessary for the claim.

The absence of subagent support never blocks the skill. Execute the same role checklists sequentially and maintain separate handoff records.

For a requested critical council, lack of isolated member capacity triggers the no-council fallback in [critical-council.md](critical-council.md). Sequential technical role checks remain useful, but do not relabel one coordinator's repeated perspectives as independent council opinions.

## Host adapters

- **Claude Code**: use native custom subagents or agent teams. The bundled validator and council Markdown profiles can be installed in `.claude/agents/` or loaded as plugin agents.
- **Kimi Code CLI**: use native `Agent` or `AgentSwarm`. Install the same validator and council profiles in `.agents/agents/`, `.kimi-code/agents/`, or the user-level equivalents.
- **DeepSeek models**: run through an agent host that provides task isolation and delegation, or implement the coordinator/worker calls in an external orchestrator. The raw model API does not install this repository or create workers by itself.
- **Other hosts**: map the three technical roles to isolated workers and, when the critical gate opens, map the bundled member and reviewer profiles as a separate stage. If concurrency, named profiles, or model routing is unavailable, use the documented fallback without changing the evidence contract.

Keep host-specific configuration outside scientific conclusions. The analysis protocol, task packet, handoff schema, and measurement controls remain identical across hosts.
