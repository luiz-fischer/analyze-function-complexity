#!/usr/bin/env python3
"""Compare refactoring variants with paired effects, guardrails, and Pareto dominance.

The input is a CSV with one row per independent unit and variant. Objective and
guardrail columns must be finite numbers. Positive paired effects always mean
that the candidate improved relative to the baseline. This script summarizes
collected data; it does not run experiments or establish semantic equivalence.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import operator
import random
import re
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Sequence


GUARDRAIL_PATTERN = re.compile(
    r"^([^\s<>=!]+)\s*(<=|>=|==|<|>)\s*"
    r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)$"
)

COMPARATORS: dict[str, Callable[[float, float], bool]] = {
    "<=": operator.le,
    ">=": operator.ge,
    "==": operator.eq,
    "<": operator.lt,
    ">": operator.gt,
}

MIN_RECOMMENDED_PAIRS = 5
MIN_RECOMMENDED_BOOTSTRAP = 200


@dataclass(frozen=True)
class Observation:
    unit: str
    variant: str
    values: dict[str, float]


@dataclass(frozen=True)
class Guardrail:
    column: str
    comparison: str
    threshold: float
    expression: str

    def accepts(self, value: float) -> bool:
        return COMPARATORS[self.comparison](value, self.threshold)


@dataclass(frozen=True)
class PairedEffect:
    metric: str
    direction: str
    pairs: int
    median_improvement: float | None
    improvement_ci95: tuple[float, float] | None
    median_relative_improvement: float | None
    relative_improvement_ci95: tuple[float, float] | None


@dataclass(frozen=True)
class VariantResult:
    variant: str
    observations: int
    eligible: bool
    guardrail_failures: list[str]
    objective_medians: dict[str, float]
    paired_effects: list[PairedEffect]


@dataclass(frozen=True)
class Analysis:
    claim_kind: str
    baseline: str
    unit_column: str
    variant_column: str
    objectives: dict[str, str]
    guardrails: list[str]
    bootstrap_iterations: int
    pareto_frontier: list[str]
    variants: list[VariantResult]
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "claim_kind": self.claim_kind,
            "baseline": self.baseline,
            "unit_column": self.unit_column,
            "variant_column": self.variant_column,
            "objectives": self.objectives,
            "guardrails": self.guardrails,
            "bootstrap_iterations": self.bootstrap_iterations,
            "pareto_frontier": self.pareto_frontier,
            "variants": [asdict(item) for item in self.variants],
            "warnings": self.warnings,
        }


def _finite_number(value: str, column: str, row_number: int) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"row {row_number}: {column!r} is not numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"row {row_number}: {column!r} must be finite")
    return result


def _split_columns(raw: str | None) -> list[str]:
    if raw is None:
        return []
    result = [item.strip() for item in raw.split(",") if item.strip()]
    if len(result) != len(set(result)):
        raise ValueError("objective columns must not be repeated")
    return result


def parse_guardrail(expression: str) -> Guardrail:
    match = GUARDRAIL_PATTERN.fullmatch(expression.strip())
    if match is None:
        raise ValueError(
            f"invalid guardrail {expression!r}; expected COLUMN<=NUMBER or a related comparison"
        )
    column, comparison, raw_threshold = match.groups()
    threshold = float(raw_threshold)
    if not math.isfinite(threshold):
        raise ValueError(f"guardrail threshold must be finite: {expression!r}")
    normalized = f"{column}{comparison}{raw_threshold}"
    return Guardrail(column, comparison, threshold, normalized)


def read_csv(
    path: Path,
    unit_column: str,
    variant_column: str,
    numeric_columns: Sequence[str],
) -> list[Observation]:
    observations: list[Observation] = []
    seen: set[tuple[str, str]] = set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header")
        required = [unit_column, variant_column, *numeric_columns]
        missing = [column for column in required if column not in reader.fieldnames]
        if missing:
            available = ", ".join(reader.fieldnames)
            raise ValueError(
                f"CSV is missing {', '.join(missing)}; available columns: {available}"
            )
        for row_number, row in enumerate(reader, start=2):
            if not row or all(value is None or not value.strip() for value in row.values()):
                continue
            unit = (row.get(unit_column) or "").strip()
            variant = (row.get(variant_column) or "").strip()
            if not unit:
                raise ValueError(f"row {row_number}: {unit_column!r} must not be empty")
            if not variant:
                raise ValueError(f"row {row_number}: {variant_column!r} must not be empty")
            key = (unit, variant)
            if key in seen:
                raise ValueError(
                    f"row {row_number}: duplicate observation for unit={unit!r}, variant={variant!r}"
                )
            seen.add(key)
            values = {
                column: _finite_number(row.get(column) or "", column, row_number)
                for column in numeric_columns
            }
            observations.append(Observation(unit, variant, values))
    if not observations:
        raise ValueError("CSV has no observation rows")
    return observations


def _percentile(sorted_values: Sequence[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("cannot calculate a percentile of no values")
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def _bootstrap_median_ci(
    values: Sequence[float], iterations: int, rng: random.Random
) -> tuple[float, float] | None:
    if iterations <= 0 or len(values) < 2:
        return None
    draws: list[float] = []
    for _ in range(iterations):
        sample = [rng.choice(values) for _ in values]
        draws.append(float(statistics.median(sample)))
    draws.sort()
    return _percentile(draws, 0.025), _percentile(draws, 0.975)


def _paired_effect(
    metric: str,
    direction: str,
    baseline: dict[str, Observation],
    candidate: dict[str, Observation],
    iterations: int,
    rng: random.Random,
) -> PairedEffect:
    common_units = sorted(set(baseline) & set(candidate))
    improvements: list[float] = []
    relative: list[float] = []
    for unit in common_units:
        baseline_value = baseline[unit].values[metric]
        candidate_value = candidate[unit].values[metric]
        effect = (
            baseline_value - candidate_value
            if direction == "minimize"
            else candidate_value - baseline_value
        )
        improvements.append(effect)
        if baseline_value != 0:
            relative.append(effect / abs(baseline_value))
    median_effect = float(statistics.median(improvements)) if improvements else None
    median_relative = float(statistics.median(relative)) if relative else None
    return PairedEffect(
        metric=metric,
        direction=direction,
        pairs=len(common_units),
        median_improvement=median_effect,
        improvement_ci95=_bootstrap_median_ci(improvements, iterations, rng),
        median_relative_improvement=median_relative,
        relative_improvement_ci95=_bootstrap_median_ci(relative, iterations, rng),
    )


def _dominates(
    left: dict[str, float],
    right: dict[str, float],
    objectives: dict[str, str],
) -> bool:
    no_worse = True
    strictly_better = False
    for metric, direction in objectives.items():
        left_value = left[metric]
        right_value = right[metric]
        if direction == "minimize":
            no_worse = no_worse and left_value <= right_value
            strictly_better = strictly_better or left_value < right_value
        else:
            no_worse = no_worse and left_value >= right_value
            strictly_better = strictly_better or left_value > right_value
    return no_worse and strictly_better


def analyze(
    observations: Sequence[Observation],
    baseline_name: str,
    objectives: dict[str, str],
    guardrails: Sequence[Guardrail],
    bootstrap: int,
    seed: int,
    unit_column: str = "unit",
    variant_column: str = "variant",
) -> Analysis:
    if not objectives:
        raise ValueError("declare at least one minimize or maximize objective")
    if bootstrap < 0:
        raise ValueError("bootstrap iterations must be >= 0")
    if set(objectives.values()) - {"minimize", "maximize"}:
        raise ValueError("objective direction must be minimize or maximize")

    by_variant: dict[str, dict[str, Observation]] = {}
    for observation in observations:
        if observation.variant in by_variant and observation.unit in by_variant[observation.variant]:
            raise ValueError(
                f"duplicate observation for unit={observation.unit!r}, variant={observation.variant!r}"
            )
        by_variant.setdefault(observation.variant, {})[observation.unit] = observation
        missing_values = (set(objectives) | {item.column for item in guardrails}) - set(
            observation.values
        )
        if missing_values:
            raise ValueError(
                f"observation {observation.unit!r}/{observation.variant!r} lacks "
                f"{', '.join(sorted(missing_values))}"
            )
        if any(not math.isfinite(value) for value in observation.values.values()):
            raise ValueError("all observed values must be finite")
    if baseline_name not in by_variant:
        raise ValueError(f"baseline variant {baseline_name!r} is absent")

    rng = random.Random(seed)
    warnings: list[str] = []
    if not guardrails:
        warnings.append("no guardrails declared; Pareto eligibility does not establish safety")
    if len(objectives) == 1:
        warnings.append("only one objective declared; the result is an ordering, not a trade-off frontier")
    if 0 < bootstrap < MIN_RECOMMENDED_BOOTSTRAP:
        warnings.append(
            f"fewer than {MIN_RECOMMENDED_BOOTSTRAP} bootstrap iterations; intervals may be unstable"
        )
    if bootstrap == 0:
        warnings.append("bootstrap disabled; paired effects have no uncertainty interval")

    baseline_units = by_variant[baseline_name]
    variant_results: list[VariantResult] = []
    medians_by_variant: dict[str, dict[str, float]] = {}
    eligible: set[str] = set()

    for variant in sorted(by_variant):
        unit_map = by_variant[variant]
        observations_for_variant = list(unit_map.values())
        medians = {
            metric: float(
                statistics.median(item.values[metric] for item in observations_for_variant)
            )
            for metric in objectives
        }
        medians_by_variant[variant] = medians

        failures: list[str] = []
        for guardrail in guardrails:
            failed = [
                item for item in observations_for_variant if not guardrail.accepts(item.values[guardrail.column])
            ]
            if failed:
                failures.append(
                    f"{guardrail.expression}: {len(failed)}/{len(observations_for_variant)} observation(s) failed"
                )
        is_eligible = not failures
        if is_eligible:
            eligible.add(variant)

        paired_effects: list[PairedEffect] = []
        if variant != baseline_name:
            common = set(baseline_units) & set(unit_map)
            baseline_only = set(baseline_units) - set(unit_map)
            candidate_only = set(unit_map) - set(baseline_units)
            if len(common) < MIN_RECOMMENDED_PAIRS:
                warnings.append(
                    f"{variant}: only {len(common)} paired unit(s); effect estimates are weak"
                )
            if baseline_only or candidate_only:
                warnings.append(
                    f"{variant}: incomplete pairing "
                    f"({len(baseline_only)} baseline-only, {len(candidate_only)} candidate-only unit(s))"
                )
            for metric, direction in objectives.items():
                paired_effects.append(
                    _paired_effect(
                        metric,
                        direction,
                        baseline_units,
                        unit_map,
                        bootstrap,
                        rng,
                    )
                )

        variant_results.append(
            VariantResult(
                variant=variant,
                observations=len(observations_for_variant),
                eligible=is_eligible,
                guardrail_failures=failures,
                objective_medians=medians,
                paired_effects=paired_effects,
            )
        )

    if baseline_name not in eligible:
        warnings.append("baseline violates at least one guardrail; check the guardrail definition and risk")

    frontier = sorted(
        variant
        for variant in eligible
        if not any(
            other != variant
            and _dominates(
                medians_by_variant[other], medians_by_variant[variant], objectives
            )
            for other in eligible
        )
    )
    if not frontier:
        warnings.append("no eligible variant remains after applying guardrails")

    return Analysis(
        claim_kind="descriptive-paired-refactoring-comparison",
        baseline=baseline_name,
        unit_column=unit_column,
        variant_column=variant_column,
        objectives=dict(objectives),
        guardrails=[item.expression for item in guardrails],
        bootstrap_iterations=bootstrap,
        pareto_frontier=frontier,
        variants=variant_results,
        warnings=warnings,
    )


def _format_number(value: float | None) -> str:
    if value is None:
        return "unknown"
    return f"{value:.6g}"


def _format_interval(value: tuple[float, float] | None) -> str:
    if value is None:
        return "unknown"
    return f"[{_format_number(value[0])}, {_format_number(value[1])}]"


def render_markdown(analysis: Analysis) -> str:
    lines = [
        "# Refactoring comparison",
        "",
        f"- Baseline: `{analysis.baseline}`",
        f"- Claim: `{analysis.claim_kind}`",
        f"- Bootstrap iterations: {analysis.bootstrap_iterations}",
        "- Positive paired effects mean improvement over baseline.",
        "",
        "## Objectives and guardrails",
        "",
    ]
    for metric, direction in analysis.objectives.items():
        lines.append(f"- `{metric}`: {direction}")
    if analysis.guardrails:
        for expression in analysis.guardrails:
            lines.append(f"- Guardrail: `{expression}`")
    else:
        lines.append("- Guardrails: none declared")

    lines.extend(["", "## Pareto frontier", ""])
    if analysis.pareto_frontier:
        lines.append(", ".join(f"`{item}`" for item in analysis.pareto_frontier))
    else:
        lines.append("No eligible variant.")

    objective_names = list(analysis.objectives)
    lines.extend(["", "## Variant summary", ""])
    header = ["Variant", "Eligible", "Pareto", *objective_names]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join("---" for _ in header) + "|")
    frontier = set(analysis.pareto_frontier)
    for variant in analysis.variants:
        row = [
            f"`{variant.variant}`",
            "yes" if variant.eligible else "no",
            "yes" if variant.variant in frontier else "no",
            *[_format_number(variant.objective_medians[name]) for name in objective_names],
        ]
        lines.append("| " + " | ".join(row) + " |")

    lines.extend(["", "## Paired effects versus baseline", ""])
    lines.append(
        "| Variant | Metric | Pairs | Median improvement | 95% bootstrap interval | "
        "Median relative improvement | Relative interval |"
    )
    lines.append("|---|---|---:|---:|---|---:|---|")
    has_effect = False
    for variant in analysis.variants:
        for effect in variant.paired_effects:
            has_effect = True
            relative = (
                "unknown"
                if effect.median_relative_improvement is None
                else f"{100.0 * effect.median_relative_improvement:.4g}%"
            )
            relative_interval = (
                "unknown"
                if effect.relative_improvement_ci95 is None
                else "["
                + f"{100.0 * effect.relative_improvement_ci95[0]:.4g}%, "
                + f"{100.0 * effect.relative_improvement_ci95[1]:.4g}%]"
            )
            lines.append(
                f"| `{variant.variant}` | `{effect.metric}` ({effect.direction}) | "
                f"{effect.pairs} | {_format_number(effect.median_improvement)} | "
                f"{_format_interval(effect.improvement_ci95)} | {relative} | {relative_interval} |"
            )
    if not has_effect:
        lines.append("| — | — | 0 | unknown | unknown | unknown | unknown |")

    failures = [item for item in analysis.variants if item.guardrail_failures]
    if failures:
        lines.extend(["", "## Guardrail failures", ""])
        for variant in failures:
            for failure in variant.guardrail_failures:
                lines.append(f"- `{variant.variant}`: {failure}")

    if analysis.warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in analysis.warnings)

    lines.extend(
        [
            "",
            "Pareto membership is descriptive over observed medians. Validate semantics, "
            "experimental independence, practical thresholds, and external validity separately.",
        ]
    )
    return "\n".join(lines)


def _self_test() -> None:
    rows: list[Observation] = []
    for index in range(1, 7):
        unit = f"run-{index}"
        rows.extend(
            [
                Observation(
                    unit,
                    "baseline",
                    {
                        "latency": 10.0 + index / 10,
                        "alloc": 5000.0 + index,
                        "complexity": 14.0,
                        "mutation": 0.84,
                        "failures": 0.0,
                    },
                ),
                Observation(
                    unit,
                    "balanced",
                    {
                        "latency": 8.5 + index / 10,
                        "alloc": 4700.0 + index,
                        "complexity": 8.0,
                        "mutation": 0.91,
                        "failures": 0.0,
                    },
                ),
                Observation(
                    unit,
                    "speed-tradeoff",
                    {
                        "latency": 7.5 + index / 10,
                        "alloc": 6200.0 + index,
                        "complexity": 10.0,
                        "mutation": 0.92,
                        "failures": 0.0,
                    },
                ),
                Observation(
                    unit,
                    "unsafe",
                    {
                        "latency": 6.0 + index / 10,
                        "alloc": 4500.0 + index,
                        "complexity": 6.0,
                        "mutation": 0.70,
                        "failures": 1.0,
                    },
                ),
            ]
        )
    objectives = {
        "latency": "minimize",
        "alloc": "minimize",
        "complexity": "minimize",
        "mutation": "maximize",
    }
    result = analyze(
        rows,
        baseline_name="baseline",
        objectives=objectives,
        guardrails=[parse_guardrail("failures<=0")],
        bootstrap=300,
        seed=7,
    )
    assert set(result.pareto_frontier) == {"balanced", "speed-tradeoff"}
    unsafe = next(item for item in result.variants if item.variant == "unsafe")
    assert not unsafe.eligible and unsafe.guardrail_failures
    balanced = next(item for item in result.variants if item.variant == "balanced")
    latency = next(item for item in balanced.paired_effects if item.metric == "latency")
    assert latency.pairs == 6
    assert latency.median_improvement is not None and latency.median_improvement > 0
    assert latency.improvement_ci95 is not None
    try:
        parse_guardrail("not a guardrail")
    except ValueError:
        pass
    else:
        raise AssertionError("invalid guardrail was accepted")
    json.dumps(result.to_dict())
    assert "Pareto frontier" in render_markdown(result)
    print("Self-test passed: pairing, bootstrap, guardrails, and Pareto frontier.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare refactoring variants from paired numeric observations."
    )
    parser.add_argument("csv_path", nargs="?", type=Path)
    parser.add_argument("--baseline", help="name in the variant column used as baseline")
    parser.add_argument("--unit-column", default="unit")
    parser.add_argument("--variant-column", default="variant")
    parser.add_argument("--minimize", help="comma-separated numeric objective columns")
    parser.add_argument("--maximize", help="comma-separated numeric objective columns")
    parser.add_argument(
        "--guardrail",
        action="append",
        default=[],
        help="required numeric condition, for example 'test_failures<=0'; repeat as needed",
    )
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        _self_test()
        return 0
    if args.csv_path is None:
        parser.error("csv_path is required unless --self-test is used")
    if not args.baseline:
        parser.error("--baseline is required")
    try:
        minimize = _split_columns(args.minimize)
        maximize = _split_columns(args.maximize)
        overlap = set(minimize) & set(maximize)
        if overlap:
            raise ValueError(
                f"objective(s) declared in both directions: {', '.join(sorted(overlap))}"
            )
        objectives = {column: "minimize" for column in minimize}
        objectives.update({column: "maximize" for column in maximize})
        if not objectives:
            raise ValueError("declare at least one --minimize or --maximize objective")
        guardrails = [parse_guardrail(value) for value in args.guardrail]
        numeric_columns = list(
            dict.fromkeys([*objectives, *(item.column for item in guardrails)])
        )
        observations = read_csv(
            args.csv_path,
            args.unit_column,
            args.variant_column,
            numeric_columns,
        )
        result = analyze(
            observations,
            baseline_name=args.baseline,
            objectives=objectives,
            guardrails=guardrails,
            bootstrap=args.bootstrap,
            seed=args.seed,
            unit_column=args.unit_column,
            variant_column=args.variant_column,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    else:
        print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
