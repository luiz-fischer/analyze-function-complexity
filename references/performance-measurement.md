# Performance Measurement and Empirical Scaling

Performance evidence is conditional: it describes a specific implementation, workload, runtime, build, and machine. Keep it separate from formal complexity.

Use this wording for curve fits: “empirically compatible with `n log n` over `n=...` to `n=...` under the recorded conditions.” Never say that timing data proves Big O.

## Contents

- Choose the experiment that answers the question
- Protocol
- Scaling experiments and helper
- Resource metrics
- Specialized models
- Ecosystem harnesses
- Safety and validity guardrails
- Scientific sources

## Choose the Experiment That Answers the Question

| Question | Primary method | Typical outputs |
|---|---|---|
| Where does a real workload spend resources? | End-to-end profiling | inclusive/exclusive CPU, allocations, I/O, blocking |
| Is implementation A materially faster than B? | Controlled comparative benchmark | ratio/difference, confidence interval, distribution |
| How does cost grow with input size? | Scaling benchmark plus formal inspection | raw series, doubling ratios, empirical fits |
| Are latency tails or contention acceptable? | Load test/tracing | throughput, p50/p95/p99, saturation, queueing |
| Why is a numeric kernel slow? | Profile plus hardware counters/Roofline when applicable | FLOPs, bandwidth, arithmetic intensity, cache events |
| What limits parallel speedup? | Work/span reasoning plus scaling/profile data | speedup, efficiency, serial fraction, contention |

Profile to locate hotspots before optimizing. Instrumentation changes execution, so confirm final performance without the profiler.

## Protocol

### 1. Predeclare the question

Define before measuring:

- cold-start or warmed/steady-state behavior;
- latency per operation, throughput, CPU time, allocation rate, peak memory, I/O, energy, or a named percentile;
- typical, boundary, worst-case, and adversarial input families as applicable;
- the smallest effect that matters operationally;
- what is included in the timed region.

Setup, input generation, teardown, and correctness validation belong outside the timed region unless the question explicitly includes them.

### 2. Validate the benchmark

- Confirm implementations are semantically equivalent and validate outputs.
- Use the optimized/release build and production-relevant runtime settings.
- Consume results and vary inputs enough to prevent dead-code elimination and constant folding.
- Batch operations only to overcome clock/harness overhead; report the normalized per-operation value.
- Check that timer overhead is small relative to the measurement.
- Use an established ecosystem harness rather than a hand-rolled wall-clock loop.
- Complement isolated microbenchmarks with a representative larger workload when external validity matters.

### 3. Control and record the environment

Record, as relevant:

- CPU model/count, RAM, OS/kernel, power/governor/turbo settings, virtualization, affinity and NUMA;
- compiler/runtime/JIT versions and flags;
- benchmark commit, build mode, dependencies, input generator/seed;
- background load, temperature/thermal throttling, storage and network context.

Use a quiet machine. Randomize or interleave A/B order to reduce temporal and code-layout bias. Do not compare absolute values from unlike runners as if they were interchangeable.

### 4. Warmup and independence

- Measure cold start separately.
- For JITs and adaptive runtimes, retain and inspect warmup series; do not assume every benchmark reaches a stable peak.
- Use multiple fresh processes/forks. Inner-loop iterations are useful for precision but are not independent experimental units.
- Treat fork/process as the main unit when possible.
- Run a pilot, then choose a repetition budget based on target uncertainty and available time. Fixed sample counts are operational defaults, not scientific constants.

### 5. Statistics

- Preserve raw samples and metadata.
- Select mean, median, or percentile based on the estimand, not whichever looks favorable.
- Report sample count, center, dispersion, effect size, and uncertainty.
- For A/B tests, prefer paired/interleaved designs and preserve pairing in resampling.
- Bootstrap at the independent-unit level; use block methods or disclose limitations when temporal autocorrelation exists.
- Never delete outliers silently. Investigate, predeclare any exclusion rule, and show sensitivity when exclusions matter.
- Statistical significance is not practical significance.
- Avoid causal claims from uncontrolled observational profiles.

## Scaling Experiments

Use geometric input sizes, normally at least 6 useful sizes over 16x or more when feasible, with repeated independent samples at each size. These are diagnostics, not universal validity thresholds.

Cover input distributions that exercise materially different paths. Random average inputs do not establish worst-case behavior.

For adjacent points, inspect:

- doubling/size ratio `T(n_i) / T(n_{i-1})`;
- empirical local exponent
  `p_i = log(T(n_i)/T(n_{i-1})) / log(n_i/n_{i-1})`;
- normalized ratios such as `T(n)/n`, `T(n)/(n log n)`, or `T(n)/n^2`;
- transitions caused by fixed overhead, cache levels, GC, JIT, vectorization, paging, or saturation.

Fit only theoretically plausible shapes. Validate by leaving out sizes and by predicting the largest sizes from smaller ones. Treat near-tied or unstable models as inconclusive. A log-log slope is an empirical exponent over the measured interval, not a proof.

### Included helper

`scripts/analyze_scaling.py` accepts a CSV with repeated `n,time` rows. It reports aggregates, adjacent local exponents, candidate-shape fits, leave-one-size-out error, holdout-tail error, selection stability from within-size bootstrap, and warnings. It uses only the Python standard library.

Example:

```csv
n,time,run_id
128,0.000421,1
128,0.000408,2
256,0.000901,1
```

```bash
python3 scripts/analyze_scaling.py results.csv
python3 scripts/analyze_scaling.py results.csv --json --bootstrap 1000 --seed 7 \
  --models linear,n_log_n --relative-tolerance 0.15
```

The helper summarizes already collected data; it is not a benchmark harness. Pre-specify theoretically plausible shapes with `--models`; searching every built-in shape is labeled exploratory. The additive model parameters are fitted by OLS on median values, while held-out relative prediction is judged by log error.

Set `--relative-tolerance` before inspecting results. Its value `epsilon` becomes the validation gate `log(1+epsilon)` for both leave-one-size-out and largest-size holdout error. The default 25% is an operational fallback, not a scientific constant.

The stronger label `compatible-over-observed-range` requires at least 6 sizes spanning 16x, at least 3 repeated samples per size, resampling variation, and at least 200 bootstrap iterations. Five or more independent repetitions remain preferable. Otherwise the result is `insufficient-design`; candidates can still be inspected as point fits. Other outcomes are `none-adequate` and `ambiguous`.

Selection stability includes a Wilson interval for Monte Carlo uncertainty. It is not the probability that a model is true. The bootstrap treats rows within each size as exchangeable independent observations; paired runs, temporal blocks, and run-ID designs require an external block-aware analysis.

## Resource Metrics

Choose only metrics relevant to a stated hypothesis:

- CPU: wall/user/system time, cycles, instructions, IPC, branches/misses, cache/TLB events, context switches, page faults;
- memory: allocated bytes/op, allocation rate, live/retained heap, peak heap, peak RSS, GC count/pause;
- I/O: logical/physical bytes, syscalls, IOPS, bandwidth, latency distribution, queue depth, flush/fsync semantics;
- concurrency: useful work, span/critical path, speedup, efficiency, contention, lock time, scheduling, false sharing;
- service: throughput, p50/p95/p99, errors, queue depth, saturation, coordinated-omission handling;
- energy: joules/work unit with the meter, sampling method, and idle baseline recorded.

Hardware performance-monitoring events are microarchitecture-specific. Separate warm and cold cache experiments, and do not use disruptive global cache-dropping procedures as a casual benchmark step.

## Specialized Models

### Amdahl's law

For a fixed workload where measured fraction `f` is improved by factor `s`:

`speedup = 1 / ((1-f) + f/s)`.

The maximum as `s` grows is `1/(1-f)`. Treat `f` as an estimate with uncertainty and re-profile after optimization because the fractions change.

### Work/span

Combine the formal work/span bounds in the algorithmic reference with measured speedup, efficiency, scheduler overhead, contention, and memory effects. Abstract parallelism is not guaranteed physical speedup.

### Roofline

For numeric or streaming kernels with meaningful FLOP and data-movement counts:

`attainable performance <= min(peak compute, bandwidth * arithmetic intensity)`.

Use Roofline to test compute-bound versus memory-bound hypotheses. Do not apply it generically to CRUD, network-bound orchestration, or irregular control-flow code.

## Ecosystem Harnesses

Prefer a repository's existing harness. If none exists, choose the established option for the ecosystem and do not install dependencies without the user's authorization.

| Ecosystem | Preferred starting point |
|---|---|
| JVM | [OpenJDK JMH](https://openjdk.org/projects/code-tools/jmh/) |
| .NET | [BenchmarkDotNet](https://benchmarkdotnet.org/articles/guides/how-it-works.html) |
| C++ | [Google Benchmark](https://google.github.io/benchmark/user_guide.html) |
| Python | [pyperf](https://pyperf.readthedocs.io/en/stable/runner.html) |
| Go | [`testing.B`](https://pkg.go.dev/testing#B) plus [benchstat](https://pkg.go.dev/golang.org/x/perf/cmd/benchstat) |
| Rust | [Criterion.rs](https://bheisler.github.io/criterion.rs/book/analysis.html) or the repository's standard bench setup |

For system investigation, platform profilers such as Linux `perf`, Java Flight Recorder, or .NET diagnostics may be appropriate. Record versions and collection settings.

## Safety and Validity Guardrails

- Do not run load/stress tests against production, paid APIs, shared databases, or external services without explicit authorization.
- Do not expose secrets or sensitive production payloads in benchmark fixtures or reports.
- Do not install dependencies or mutate application code for an analysis-only request.
- Do not claim a hotspot matters without relating it to end-to-end workload share.
- Do not extrapolate beyond the measured range without a formal model and an explicit uncertainty warning.
- Do not report profiler percentages as absolute time savings without applying Amdahl's-law reasoning and remeasurement.

## Scientific Sources

- Kalibera and Jones, “Rigorous Benchmarking in Reasonable Time,” [DOI 10.1145/2464157.2464160](https://doi.org/10.1145/2464157.2464160), [author record](https://kar.kent.ac.uk/33611/).
- Georges, Buytaert, and Eeckhout, “Statistically Rigorous Java Performance Evaluation,” [DOI 10.1145/1297027.1297033](https://doi.org/10.1145/1297027.1297033).
- Mytkowicz et al., “Producing Wrong Data Without Doing Anything Obviously Wrong,” [DOI 10.1145/1508244.1508275](https://doi.org/10.1145/1508244.1508275).
- Barrett et al., “Virtual Machine Warmup Blows Hot and Cold,” [DOI 10.1145/3133876](https://doi.org/10.1145/3133876).
- McGeoch, “Experimental Analysis of Algorithms,” [chapter DOI 10.1007/978-1-4612-1166-7_8](https://doi.org/10.1007/978-1-4612-1166-7_8).
- Amdahl, “Validity of the Single Processor Approach to Achieving Large Scale Computing Capabilities,” [DOI 10.1145/1465482.1465560](https://doi.org/10.1145/1465482.1465560).
- Williams, Waterman, and Patterson, “Roofline: An Insightful Visual Performance Model,” [DOI 10.1145/1498765.1498785](https://doi.org/10.1145/1498765.1498785).
- NIST, [Software Performance Measurement](https://www.nist.gov/itl/ai/software-performance-measurement).
