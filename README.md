# Analyze Function Complexity

An evidence-aware [Agent Skill](https://agentskills.io/) for analyzing and reducing the complexity of functions, methods, closures, and small call paths.

The skill keeps distinct claims distinct: formal asymptotic complexity, measured runtime behavior, structural code metrics, design heuristics, and experimental evidence. When refactoring is requested, it uses a behavior-preserving, hypothesis-driven workflow with explicit objectives, guardrails, uncertainty, and falsifiers.

Created and maintained by **Luiz Fischer**.

## Capabilities

- Derives time and auxiliary-space complexity under an explicit cost model.
- Distinguishes worst-case, best-case, expected, amortized, and output-sensitive bounds.
- Uses loop sums, recurrence relations, aggregate analysis, accounting, potentials, and counterexamples where applicable.
- Treats cyclomatic, NPath, cognitive, and maintainability metrics as review signals rather than universal laws.
- Separates profiling and benchmarking evidence from mathematical complexity claims.
- Evaluates function-level SOLID concerns only when the surrounding contracts make them meaningful.
- Designs controlled refactoring experiments with behavioral oracles, paired workloads, randomized execution order, bootstrap intervals, effect sizes, guardrails, and sensitivity checks.
- Compares multiple refactoring candidates without hiding regressions or inconclusive evidence.
- Coordinates independent formal, empirical, and structural/refactoring validators while preserving disagreements and serializing resource-sensitive measurements.
- Escalates consequential unresolved decisions to a bundled blind critical council with independent opinions, fresh peer review, advisory ranking, and evidence-first chair synthesis.
- Uses model-neutral agent profiles that can run with Claude, Kimi, DeepSeek-backed hosts, or any compatible orchestrator.

## Repository layout

```text
.
├── .claude-plugin/
│   └── plugin.json
├── .gitignore
├── LICENSE
├── NOTICE
├── README.md
├── SKILL.md
├── agents/
│   ├── afc-critical-council-member.md
│   ├── afc-critical-council-reviewer.md
│   ├── afc-empirical-performance-validator.md
│   ├── afc-formal-complexity-validator.md
│   └── afc-structural-refactoring-validator.md
├── kimi.plugin.json
├── references/
│   ├── algorithmic-complexity.md
│   ├── critical-council.md
│   ├── multi-agent-validation.md
│   ├── performance-measurement.md
│   ├── refactoring-experiments.md
│   ├── scientific-validation.md
│   ├── structural-and-solid.md
│   └── validator-handoff.schema.json
└── scripts/
    ├── analyze_scaling.py
    ├── compare_refactorings.py
    └── critical_council.py
```

The repository root is the installable skill directory. It is also packaged for Claude Code and Kimi Code. The Markdown files under `agents/` are actual model-neutral validator and council profiles; they are separate from client-specific UI metadata.

## Standard and requirements

This package follows the open [Agent Skills specification](https://agentskills.io/specification): the skill directory name matches the YAML `name`, `SKILL.md` contains the required `name` and `description`, and supporting material is organized under `references/`, `scripts/`, and `agents/`.

Requirements:

- An Agent Skills-compatible client, or another host that can inject `SKILL.md` as instructions.
- Python 3.10 or newer to run the optional analysis scripts.
- No third-party Python packages; all three scripts use only the standard library.

The helper scripts and subagents are optional. The critical-council protocol, profiles, and utility are included in this repository; no separate `council` skill is required. Without subagent support, the skill executes technical validation lanes sequentially and reports that no independent council formed. Client discovery behavior varies, so reload or restart the client after creating a new skill or agent directory.

## Multi-agent validation

The main agent remains the coordinator and sole final-report author. It selects at most three validation lanes:

| Profile | Primary responsibility | Default execution |
|---|---|---|
| `afc-formal-complexity-validator` | Cost models, bounds, recurrences, witnesses, and counterexamples | Parallel and read-only |
| `afc-empirical-performance-validator` | Profiling, scaling, benchmark design, uncertainty, and validity threats | Planned in parallel; measurements serialized or isolated |
| `afc-structural-refactoring-validator` | CFG metrics, maintainability, SOLID applicability, behavioral oracles, and refactoring guardrails | Parallel and read-only |

The coordinator freezes a common task packet before delegation, withholds sibling conclusions, and synthesizes by claim ID and evidence quality rather than majority vote. Agent agreement is corroboration, not proof or statistical replication.

Validators use [`references/validator-handoff.schema.json`](references/validator-handoff.schema.json) when the host supports structured output, giving Claude-, Kimi-, and DeepSeek-backed workers the same evidence contract.

Profiles do not declare a model. A host may route them to Claude, Kimi, DeepSeek, or another model. For repeated heterogeneous evaluations, rotate model-role assignments so model family is not confounded with validator role. The complete protocol is in [`references/multi-agent-validation.md`](references/multi-agent-validation.md).

## Critical council escalation

The critical council is a second-stage decision review, not another source of technical evidence. It activates when explicitly requested or when a consequential complexity or refactoring decision remains unresolved after normal validation because valid evidence conflicts, multiple candidates remain Pareto-eligible, or assumptions and trade-offs can change the preferred action.

Standard mode uses three independent read-only members, two fresh blind reviewers, and the main coordinator as chair. Lightweight mode uses two members and one reviewer only when disclosed. Reviewers rank comparable, complete council opinions answering the same decision; they never rank the complementary formal, empirical, and structural validator handoffs against one another.

The bundled [member](agents/afc-critical-council-member.md), [reviewer](agents/afc-critical-council-reviewer.md), [protocol](references/critical-council.md), and [local artifact utility](scripts/critical_council.py) make this feature self-contained. The utility pseudonymizes and shuffles opinions, records reproducibility digests and a run ID, validates ballot quorum, preserves true ties, and does not contact a model provider. Its ranking is advisory; proofs, contracts, behavioral guardrails, valid measurements, and credible unresolved risks remain decisive.

If the host cannot create at least two isolated member opinions, ordinary evidence-first synthesis continues and the report states that no council formed. Missing technical evidence produces more validation or `unknown`, never a vote.

## Installation

### Portable installation with the skills CLI

Install only this skill:

```bash
npx skills@latest add luiz-fischer/analyze-function-complexity \
  --skill analyze-function-complexity
```

Install it non-interactively for Codex:

```bash
npx skills@latest add luiz-fischer/analyze-function-complexity \
  --skill analyze-function-complexity \
  --agent codex \
  --yes
```

The Agent Skills standard defines the package format, not a mandatory installer. The `skills` CLI is a convenient cross-client installer used by public skill repositories.

### Claude Code with native subagents

Clone the repository and load it as a plugin for the current session:

```bash
git clone https://github.com/luiz-fischer/analyze-function-complexity.git
claude --plugin-dir ./analyze-function-complexity
```

Claude Code discovers the root skill and the profiles under `agents/`. For a manual user-level installation:

```bash
cd analyze-function-complexity
mkdir -p ~/.claude/skills/analyze-function-complexity ~/.claude/agents
cp -R LICENSE NOTICE SKILL.md references scripts agents \
  ~/.claude/skills/analyze-function-complexity/
cp agents/*.md ~/.claude/agents/
```

The profiles use the portable subset of the Claude Code and Kimi Code agent-file formats. See the official [Claude Code subagent documentation](https://code.claude.com/docs/en/sub-agents).

### Kimi Code with native subagents

Install the skill as a Kimi plugin from the public repository:

```text
/plugins install https://github.com/luiz-fischer/analyze-function-complexity
```

The skill can dynamically delegate to Kimi's built-in workers. To make the five named profiles available globally, clone the repository and copy them into Kimi's shared agent directory:

```bash
git clone https://github.com/luiz-fischer/analyze-function-complexity.git
mkdir -p ~/.agents/agents
cp analyze-function-complexity/agents/*.md ~/.agents/agents/
```

Alternatively, install both the skill and profiles manually in the shared cross-tool locations:

```bash
mkdir -p ~/.agents/skills/analyze-function-complexity ~/.agents/agents
cp -R analyze-function-complexity/SKILL.md \
  analyze-function-complexity/LICENSE \
  analyze-function-complexity/NOTICE \
  analyze-function-complexity/references \
  analyze-function-complexity/scripts \
  analyze-function-complexity/agents \
  ~/.agents/skills/analyze-function-complexity/
cp analyze-function-complexity/agents/*.md ~/.agents/agents/
```

Reload Kimi after installation. See the official [Kimi Code agents and subagents documentation](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/agents.html).

### DeepSeek-backed multi-agent execution

DeepSeek provides models and compatible APIs; the agent host supplies skill discovery, worker isolation, and parallel orchestration. Configure DeepSeek in a supported coding-agent host, then install this skill and its profiles using that host's instructions. DeepSeek's official guide documents integration with Claude Code and other agent tools: [Integrate with AI Tools](https://api-docs.deepseek.com/guides/coding_agents/).

When using the raw API, the external orchestrator must create the coordinator, validator, member, and reviewer calls, freeze the required task packets, and serialize shared-hardware measurements. The skill does not transmit source code or call any provider on its own.

### Manual installation for Codex

On Linux or macOS:

```bash
git clone https://github.com/luiz-fischer/analyze-function-complexity.git
mkdir -p ~/.codex/skills/analyze-function-complexity
cp -R analyze-function-complexity/SKILL.md \
  analyze-function-complexity/LICENSE \
  analyze-function-complexity/NOTICE \
  analyze-function-complexity/references \
  analyze-function-complexity/scripts \
  analyze-function-complexity/agents \
  ~/.codex/skills/analyze-function-complexity/
```

Verify the installation and the bundled scripts:

```bash
test -f ~/.codex/skills/analyze-function-complexity/SKILL.md
python3 ~/.codex/skills/analyze-function-complexity/scripts/analyze_scaling.py --self-test
python3 ~/.codex/skills/analyze-function-complexity/scripts/compare_refactorings.py --self-test
python3 ~/.codex/skills/analyze-function-complexity/scripts/critical_council.py self-test
```

### Project-scoped installation

For clients that discover the shared `.agents/skills/` location:

```bash
git clone https://github.com/luiz-fischer/analyze-function-complexity.git
mkdir -p YOUR_PROJECT/.agents/skills/analyze-function-complexity
cp -R analyze-function-complexity/SKILL.md \
  analyze-function-complexity/LICENSE \
  analyze-function-complexity/NOTICE \
  analyze-function-complexity/references \
  analyze-function-complexity/scripts \
  analyze-function-complexity/agents \
  YOUR_PROJECT/.agents/skills/analyze-function-complexity/
mkdir -p YOUR_PROJECT/.agents/agents
cp analyze-function-complexity/agents/*.md YOUR_PROJECT/.agents/agents/
```

Commit the copied skill if the project should provide it to every contributor.

### Upload to ChatGPT

Create an archive containing the installable skill directory:

```bash
git clone https://github.com/luiz-fischer/analyze-function-complexity.git
zip -r analyze-function-complexity.zip analyze-function-complexity \
  -x 'analyze-function-complexity/.git/*'
```

In ChatGPT, open **Plugins**, select the **Skills** tab, choose **Create**, and upload the archive from your computer. Availability may depend on the account plan and workspace permissions.

## Usage

After installation, ask the agent naturally. Example prompts:

```text
Analyze the worst-case time and auxiliary-space complexity of this function.
```

```text
Profile this method, explain which conclusions are empirical, and identify the dominant bottleneck.
```

```text
Refactor this high-complexity function without changing behavior. Predeclare the hypothesis, objective metrics, guardrails, and validation protocol before editing it.
```

```text
Compare these refactoring candidates using paired observations and report uncertainty, regressions, and inconclusive results.
```

```text
Use independent formal, empirical, and structural validators. Run safe read-only work in parallel, serialize benchmarks, preserve disagreements, and then synthesize one evidence matrix.
```

```text
Use the bundled critical council to decide between these validated refactoring candidates. Keep members independent, blind the peer review, preserve dissent, and resolve the result by evidence rather than votes.
```

The main workflow and output contract are documented in [`SKILL.md`](SKILL.md). Detailed scientific and engineering protocols are loaded from the files in [`references/`](references/) only when needed.

## Optional helper scripts

### Explore empirical scaling

Given a CSV containing input size and repeated measurements:

```bash
python3 scripts/analyze_scaling.py measurements.csv \
  --size-column n \
  --time-column elapsed_ms \
  --bootstrap 2000 \
  --json
```

This script compares pre-specified growth shapes and reports uncertainty and predictive diagnostics. Its output is empirical model evidence, not a proof of Big O.

### Compare refactoring variants

Given paired observations identified by workload unit and variant:

```bash
python3 scripts/compare_refactorings.py results.csv \
  --baseline baseline \
  --minimize elapsed_ms,allocated_bytes \
  --guardrail 'test_failures<=0' \
  --bootstrap 2000 \
  --json
```

### Prepare a critical council review

After at least two independent member opinions answer the same frozen decision, prepare a pseudonymized review packet and private label map:

```bash
python3 scripts/critical_council.py prepare \
  --input stage1.json \
  --packet review-packet.md \
  --map label-map.json \
  --seed reproducible-run-id
```

After fresh reviewers return complete rankings, copy the generated run ID into `ballots.json` and aggregate the valid ballots:

```bash
python3 scripts/critical_council.py aggregate \
  --ballots ballots.json \
  --map label-map.json \
  --output aggregate.json
```

The utility writes only caller-selected local paths, refuses replacement unless `--force` is supplied, rejects output links, directories, and input-path reuse, and does not perform provider calls or chair synthesis. Run any script with `--help` for its full input contract and options.

## Validation

From the repository root:

```bash
skills-ref validate .
python3 -I -B ./scripts/analyze_scaling.py --self-test
python3 -I -B ./scripts/compare_refactorings.py --self-test
python3 -I -B ./scripts/critical_council.py self-test
python3 -m py_compile ./scripts/*.py
python3 -m json.tool ./.claude-plugin/plugin.json >/dev/null
python3 -m json.tool ./kimi.plugin.json >/dev/null
python3 -m json.tool ./references/validator-handoff.schema.json >/dev/null
```

`skills-ref` is the reference validator linked by the Agent Skills specification. The three self-tests exercise the deterministic checks bundled with this skill.

The repository also runs the validation suite automatically on every push and pull
request through the CI workflow at .github/workflows/ci.yml. It validates required
files and manifests, scans for machine-specific paths, and runs the complete Python
test matrix on supported Python versions.

Before accepting a change, also review whether:

- The YAML name still matches the parent directory.
- The description still states both capability and trigger conditions.
- Every path referenced by `SKILL.md` exists and remains relative to the skill root.
- Agent profiles remain model-neutral, read-only by default, and compatible with their documented discovery paths.
- Resource-sensitive measurements remain serialized or physically isolated.
- Critical-council rankings compare complete opinions answering the same decision, never complementary technical handoffs.
- Council artifacts carry matching run IDs, and the private label map is not exposed before reviews are frozen.
- Claims labeled as proofs, measurements, inferences, or heuristics remain clearly separated.
- New executable code documents dependencies, handles invalid input, and has a reproducible test.

## Releasing

Before publishing a release:

1. Run every command in the validation section.
2. Test one sequential analysis, one technical multi-agent analysis, one complete critical-council run, and one no-agent fallback on held-out functions.
3. Review scripts, profiles, references, and manifests for secrets, private paths, proprietary data, and unsafe commands.
4. Confirm that Claude and Kimi discover the skill and named profiles after a clean installation.
5. Push the reviewed commit and create a semantic version tag such as `v1.1.0`.

Keep release notes explicit about changes to triggers, agent roles, scientific protocols, report fields, and script input formats.

## Security

Agent Skills can contain executable code. Review the source before installation, especially when installing a fork. The scaling and refactoring helpers read local CSV files and write results to standard output or caller-selected paths. The critical-council utility reads local JSON, creates caller-selected Markdown and JSON artifacts, makes parent directories when needed, stores the private map with restrictive permissions on supporting systems, rejects links, directories, and input/output path reuse, and overwrites regular files only with explicit `--force`. None of the scripts requires network access or third-party packages.

## License

Copyright (c) 2026 Luiz Fischer.

This project is released under the [MIT License](LICENSE). You may use, copy, modify, publish, and redistribute it under the license terms. Copies or substantial portions must retain the copyright notice and permission notice.
