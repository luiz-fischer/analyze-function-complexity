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

## Repository layout

```text
.
├── .gitignore
├── LICENSE
├── README.md
├── SKILL.md
├── references/
│   ├── algorithmic-complexity.md
│   ├── performance-measurement.md
│   ├── refactoring-experiments.md
│   ├── scientific-validation.md
│   └── structural-and-solid.md
└── scripts/
    ├── analyze_scaling.py
    └── compare_refactorings.py
```

The repository root is the installable skill directory. The Agent Skills specification permits additional files, so the GitHub README and ignore rules can live beside `SKILL.md` while the repository remains a self-contained package.

## Standard and requirements

This package follows the open [Agent Skills specification](https://agentskills.io/specification): the skill directory name matches the YAML `name`, `SKILL.md` contains the required `name` and `description`, and optional material is organized under `references/` and `scripts/`.

Requirements:

- An Agent Skills-compatible client.
- Python 3.10 or newer to run the optional analysis scripts.
- No third-party Python packages; both scripts use only the standard library.

The skill instructions can still be used without running the scripts. Client support and skill-loading behavior vary, so restart or reload the client after a manual installation when necessary.

## Installation

Replace `OWNER/REPOSITORY` and `REPOSITORY` below with the GitHub repository coordinates and local clone directory you choose when publishing.

### Portable installation with the skills CLI

Install only this skill:

```bash
npx skills@latest add OWNER/REPOSITORY --skill analyze-function-complexity
```

Install it non-interactively for Codex:

```bash
npx skills@latest add OWNER/REPOSITORY \
  --skill analyze-function-complexity \
  --agent codex \
  --yes
```

The Agent Skills standard defines the package format, not a mandatory installer. The `skills` CLI is a convenient cross-client installer used by public skill repositories.

### Manual installation for Codex

On Linux or macOS:

```bash
git clone https://github.com/OWNER/REPOSITORY.git
mkdir -p ~/.codex/skills/analyze-function-complexity
cp -R REPOSITORY/SKILL.md REPOSITORY/references REPOSITORY/scripts \
  ~/.codex/skills/analyze-function-complexity/
```

Verify the installation and the bundled scripts:

```bash
test -f ~/.codex/skills/analyze-function-complexity/SKILL.md
python3 ~/.codex/skills/analyze-function-complexity/scripts/analyze_scaling.py --self-test
python3 ~/.codex/skills/analyze-function-complexity/scripts/compare_refactorings.py --self-test
```

### Project-scoped installation

For clients that discover the shared `.agents/skills/` location:

```bash
git clone https://github.com/OWNER/REPOSITORY.git
mkdir -p YOUR_PROJECT/.agents/skills/analyze-function-complexity
cp -R REPOSITORY/SKILL.md REPOSITORY/references REPOSITORY/scripts \
  YOUR_PROJECT/.agents/skills/analyze-function-complexity/
```

Commit the copied skill if the project should provide it to every contributor.

### Upload to ChatGPT

Create an archive containing the installable skill directory:

```bash
git clone https://github.com/OWNER/REPOSITORY.git analyze-function-complexity
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

Run either script with `--help` for its full input contract and options.

## Validation

From the repository root:

```bash
skills-ref validate .
python3 ./scripts/analyze_scaling.py --self-test
python3 ./scripts/compare_refactorings.py --self-test
python3 -m py_compile ./scripts/*.py
```

`skills-ref` is the reference validator linked by the Agent Skills specification. The two self-tests exercise the deterministic checks bundled with this skill.

Before accepting a change, also review whether:

- The YAML name still matches the parent directory.
- The description still states both capability and trigger conditions.
- Every path referenced by `SKILL.md` exists and remains relative to the skill root.
- Claims labeled as proofs, measurements, inferences, or heuristics remain clearly separated.
- New executable code documents dependencies, handles invalid input, and has a reproducible test.

## Publishing on GitHub

Before the first public release:

1. Replace all `OWNER/REPOSITORY` placeholders in this README.
2. Run every command in the validation section.
3. Review bundled scripts and references for secrets, private paths, proprietary data, and unsafe commands.
4. Create the repository and push the prepared directory:

```bash
cd /path/to/analyze-function-complexity
git init
git add .
git commit -m "Publish analyze-function-complexity Agent Skill"
git branch -M main
git remote add origin https://github.com/OWNER/REPOSITORY.git
git push -u origin main
```

Use semantic version tags such as `v1.0.0` once the public API and behavior are stable. Keep release notes explicit about changes to triggers, scientific protocols, report fields, and script input formats.

## Security

Agent Skills can contain executable code. Review the source before installation, especially when installing a fork. The bundled scripts process local CSV files, write results to standard output, and require no network access or external package installation.

## License

Copyright (c) 2026 Luiz Fischer.

This project is released under the [MIT License](LICENSE). You may use, copy, modify, publish, and redistribute it under the license terms. Copies or substantial portions must retain the copyright notice and permission notice.
