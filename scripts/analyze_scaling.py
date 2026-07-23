#!/usr/bin/env python3
"""Diagnose finite-range scaling measurements without claiming Big O proof.

Input rows contain a positive size and positive measured value. Repeated rows
for one size are samples. Output is Markdown by default or JSON with --json.
Only the Python standard library is required.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence


Transform = Callable[[float], float]

MODELS: dict[str, Transform] = {
    "constant": lambda n: 1.0,
    "log_n": math.log2,
    "sqrt_n": math.sqrt,
    "linear": lambda n: n,
    "n_log_n": lambda n: n * math.log2(n),
    "quadratic": lambda n: n * n,
    "cubic": lambda n: n * n * n,
}

MIN_STRONG_SIZES = 6
MIN_STRONG_REPEATS = 3
MIN_BOOTSTRAP_ITERATIONS = 200
DEFAULT_RELATIVE_TOLERANCE = 0.25


@dataclass(frozen=True)
class Aggregate:
    n: float
    count: int
    median: float
    mean: float
    mad: float
    minimum: float
    maximum: float
    median_ci95: tuple[float, float] | None = None


@dataclass(frozen=True)
class Fit:
    model: str
    alpha: float | None
    beta: float | None
    rmse: float | None
    nrmse: float | None
    r_squared: float | None
    loocv_log_rmse: float | None
    tail_log_rmse: float | None
    score: float | None
    valid: bool


@dataclass(frozen=True)
class LocalGrowth:
    from_n: float
    to_n: float
    size_ratio: float | None
    value_ratio: float | None
    empirical_exponent: float | None


@dataclass
class Analysis:
    claim_kind: str
    observed_range: dict[str, float]
    distinct_sizes: int
    total_samples: int
    best_shape: str | None
    runner_up: str | None
    conclusion: str
    selection_stability: float | None
    selection_stability_ci95: tuple[float, float] | None
    bootstrap_iterations: int
    bootstrap_mcse_max: float | None
    relative_tolerance: float
    models_considered: list[str]
    search_mode: str
    empirical_power_exponent: dict[str, float | list[float]] | None
    aggregates: list[Aggregate]
    local_growth: list[LocalGrowth]
    fits: list[Fit]
    model_stability: dict[str, float]
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "claim_kind": self.claim_kind,
            "observed_range": self.observed_range,
            "distinct_sizes": self.distinct_sizes,
            "total_samples": self.total_samples,
            "best_shape": self.best_shape,
            "runner_up": self.runner_up,
            "conclusion": self.conclusion,
            "selection_stability": self.selection_stability,
            "selection_stability_ci95": self.selection_stability_ci95,
            "bootstrap_iterations": self.bootstrap_iterations,
            "bootstrap_mcse_max": self.bootstrap_mcse_max,
            "relative_tolerance": self.relative_tolerance,
            "models_considered": self.models_considered,
            "search_mode": self.search_mode,
            "empirical_power_exponent": self.empirical_power_exponent,
            "aggregates": [asdict(item) for item in self.aggregates],
            "local_growth": [asdict(item) for item in self.local_growth],
            "fits": [asdict(item) for item in self.fits],
            "model_stability": self.model_stability,
            "warnings": self.warnings,
        }


def _positive_number(value: str, field: str, row_number: int) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"row {row_number}: {field!r} is not numeric") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise ValueError(f"row {row_number}: {field!r} must be finite and > 0")
    return parsed


def read_csv(path: Path, size_column: str, time_column: str) -> dict[float, list[float]]:
    groups: dict[float, list[float]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header")
        missing = [name for name in (size_column, time_column) if name not in reader.fieldnames]
        if missing:
            available = ", ".join(reader.fieldnames)
            raise ValueError(f"CSV is missing {', '.join(missing)}; available columns: {available}")
        for row_number, row in enumerate(reader, start=2):
            if not row or all(value is None or not value.strip() for value in row.values()):
                continue
            n = _positive_number(row[size_column], size_column, row_number)
            measured = _positive_number(row[time_column], time_column, row_number)
            groups.setdefault(n, []).append(measured)
    if not groups:
        raise ValueError("CSV has no measurement rows")
    return groups


def _mad(values: Sequence[float], center: float) -> float:
    return _stable_median([abs(value - center) for value in values])


def _stable_median(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("cannot calculate a median of no values")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    lower = ordered[middle - 1]
    upper = ordered[middle]
    return lower + (upper - lower) / 2.0


def _stable_mean(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("cannot calculate a mean of no values")
    scale = max(abs(value) for value in values)
    if scale == 0:
        return 0.0
    return scale * statistics.fmean(value / scale for value in values)


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


def aggregate_groups(
    groups: dict[float, list[float]],
    bootstrap_medians: dict[float, list[float]] | None = None,
) -> list[Aggregate]:
    result: list[Aggregate] = []
    for n in sorted(groups):
        values = groups[n]
        median = _stable_median(values)
        interval: tuple[float, float] | None = None
        if bootstrap_medians and bootstrap_medians.get(n):
            draws = sorted(bootstrap_medians[n])
            interval = (_percentile(draws, 0.025), _percentile(draws, 0.975))
        result.append(
            Aggregate(
                n=n,
                count=len(values),
                median=median,
                mean=_stable_mean(values),
                mad=_mad(values, median),
                minimum=min(values),
                maximum=max(values),
                median_ci95=interval,
            )
        )
    return result


def _fit_parameters(
    model: str, points: Sequence[tuple[float, float]]
) -> tuple[float, float] | None:
    if not points:
        return None
    if model == "constant":
        return _stable_mean([value for _, value in points]), 0.0

    try:
        raw_x = [MODELS[model](n) for n, _ in points]
    except (OverflowError, ValueError):
        return None
    x_scale = max(abs(value) for value in raw_x)
    raw_y = [value for _, value in points]
    y_scale = max(abs(value) for value in raw_y)
    if not math.isfinite(x_scale) or x_scale <= 0 or y_scale <= 0:
        return None
    xs = [value / x_scale for value in raw_x]
    ys = [value / y_scale for value in raw_y]
    x_mean = _stable_mean(xs)
    y_mean = _stable_mean(ys)
    sxx = sum((value - x_mean) ** 2 for value in xs)
    if sxx <= sys.float_info.epsilon:
        return None
    beta_scaled = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / sxx
    alpha_scaled = y_mean - beta_scaled * x_mean
    try:
        beta = beta_scaled * y_scale / x_scale
        alpha = alpha_scaled * y_scale
    except OverflowError:
        return None
    if not math.isfinite(alpha) or not math.isfinite(beta) or beta < 0:
        return None
    return alpha, beta


def _predict(model: str, parameters: tuple[float, float], n: float) -> float:
    alpha, beta = parameters
    if model == "constant":
        return alpha
    try:
        prediction = alpha + beta * MODELS[model](n)
    except (OverflowError, ValueError):
        return math.inf
    return prediction if math.isfinite(prediction) else math.inf


def _rmse(actual: Sequence[float], predicted: Sequence[float]) -> float | None:
    if not actual or any(not math.isfinite(value) for value in predicted):
        return None
    scale = max(max(abs(value) for value in actual), max(abs(value) for value in predicted))
    if scale == 0:
        return 0.0
    normalized = math.sqrt(
        statistics.fmean(((a / scale) - (p / scale)) ** 2 for a, p in zip(actual, predicted))
    )
    result = scale * normalized
    return result if math.isfinite(result) else None


def _log_rmse(actual: Sequence[float], predicted: Sequence[float]) -> float | None:
    if not actual or any(value <= 0 or not math.isfinite(value) for value in predicted):
        return None
    return math.sqrt(
        statistics.fmean((math.log(p) - math.log(a)) ** 2 for a, p in zip(actual, predicted))
    )


def _loocv(model: str, points: Sequence[tuple[float, float]]) -> float | None:
    if len(points) < 4:
        return None
    actual: list[float] = []
    predicted: list[float] = []
    for index, point in enumerate(points):
        training = points[:index] + points[index + 1 :]
        parameters = _fit_parameters(model, training)
        if parameters is None:
            return None
        estimate = _predict(model, parameters, point[0])
        if estimate <= 0 or not math.isfinite(estimate):
            return None
        actual.append(point[1])
        predicted.append(estimate)
    return _log_rmse(actual, predicted)


def _tail_holdout(model: str, points: Sequence[tuple[float, float]]) -> float | None:
    if len(points) < 5:
        return None
    parameters = _fit_parameters(model, points[:-2])
    if parameters is None:
        return None
    actual = [value for _, value in points[-2:]]
    predicted = [_predict(model, parameters, n) for n, _ in points[-2:]]
    return _log_rmse(actual, predicted)


def fit_candidates(
    points: Sequence[tuple[float, float]], models: Sequence[str] | None = None
) -> list[Fit]:
    selected = list(models) if models is not None else list(MODELS)
    unknown = set(selected) - set(MODELS)
    if unknown:
        raise ValueError(f"unknown model(s): {', '.join(sorted(unknown))}")
    if not selected:
        raise ValueError("at least one candidate model is required")
    actual = [value for _, value in points]
    y_scale = max(abs(value) for value in actual)
    if not math.isfinite(y_scale) or y_scale <= 0:
        raise ValueError("candidate fitting requires positive finite measured values")
    normalized_actual = [value / y_scale for value in actual]
    normalized_mean = _stable_mean(normalized_actual)
    sst = sum((value - normalized_mean) ** 2 for value in normalized_actual)
    fits: list[Fit] = []
    for model in selected:
        parameters = _fit_parameters(model, points)
        if parameters is None:
            fits.append(
                Fit(model, None, None, None, None, None, None, None, None, False)
            )
            continue
        predicted = [_predict(model, parameters, n) for n, _ in points]
        alpha, beta = parameters
        if any(value <= 0 or not math.isfinite(value) for value in predicted):
            fits.append(Fit(model, alpha, beta, None, None, None, None, None, None, False))
            continue
        rmse = _rmse(actual, predicted)
        try:
            residuals = [(a / y_scale) - (p / y_scale) for a, p in zip(actual, predicted)]
        except OverflowError:
            residuals = []
        if residuals and all(math.isfinite(value) for value in residuals):
            relative_rmse = math.sqrt(statistics.fmean(value * value for value in residuals))
            nrmse = relative_rmse / normalized_mean if normalized_mean else None
            sse = sum(value * value for value in residuals)
            r_squared = None if sst <= sys.float_info.epsilon else 1.0 - sse / sst
            if r_squared is not None and not math.isfinite(r_squared):
                r_squared = None
        else:
            nrmse = None
            r_squared = None
        loocv = _loocv(model, points)
        tail = _tail_holdout(model, points)
        score = loocv
        fits.append(
            Fit(model, alpha, beta, rmse, nrmse, r_squared, loocv, tail, score, True)
        )
    return sorted(
        fits,
        key=lambda fit: (
            fit.score is None,
            fit.score if fit.score is not None else math.inf,
            fit.nrmse if fit.nrmse is not None else math.inf,
        ),
    )


def _log_ratio_delta(numerator: float, denominator: float) -> float | None:
    try:
        relative_change = (numerator - denominator) / denominator
    except OverflowError:
        relative_change = math.inf
    if math.isfinite(relative_change) and relative_change > -1.0:
        delta = math.log1p(relative_change)
        if delta != 0.0 or numerator == denominator:
            return delta
    delta = math.log(numerator) - math.log(denominator)
    return delta if math.isfinite(delta) and (delta != 0.0 or numerator == denominator) else None


def _safe_ratio(numerator: float, denominator: float) -> float | None:
    log_ratio = _log_ratio_delta(numerator, denominator)
    if log_ratio is None:
        return None
    if log_ratio > math.log(sys.float_info.max) or log_ratio < math.log(sys.float_info.min):
        return None
    ratio = math.exp(log_ratio)
    return ratio if math.isfinite(ratio) and ratio > 0 else None


def calculate_local_growth(points: Sequence[tuple[float, float]]) -> list[LocalGrowth]:
    result: list[LocalGrowth] = []
    for (previous_n, previous_value), (n, value) in zip(points, points[1:]):
        size_ratio = _safe_ratio(n, previous_n)
        value_ratio = _safe_ratio(value, previous_value)
        delta_n = _log_ratio_delta(n, previous_n)
        delta_value = _log_ratio_delta(value, previous_value)
        exponent = (
            delta_value / delta_n
            if delta_n is not None and delta_value is not None and delta_n > 0
            else None
        )
        result.append(LocalGrowth(previous_n, n, size_ratio, value_ratio, exponent))
    return result


def empirical_power_exponent(points: Sequence[tuple[float, float]]) -> float | None:
    if len(points) < 2:
        return None
    xs = [math.log(n) for n, _ in points]
    ys = [math.log(value) for _, value in points]
    x_mean = _stable_mean(xs)
    y_mean = _stable_mean(ys)
    sxx = sum((x - x_mean) ** 2 for x in xs)
    if sxx <= sys.float_info.epsilon:
        return None
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / sxx


def bootstrap_diagnostics(
    groups: dict[float, list[float]],
    iterations: int,
    seed: int,
    models: Sequence[str],
) -> tuple[dict[str, int], list[float], dict[float, list[float]]]:
    counts = {model: 0 for model in models}
    exponents: list[float] = []
    medians: dict[float, list[float]] = {n: [] for n in groups}
    rng = random.Random(seed)
    for _ in range(iterations):
        points: list[tuple[float, float]] = []
        for n in sorted(groups):
            values = groups[n]
            sample = [rng.choice(values) for _ in values]
            center = _stable_median(sample)
            medians[n].append(center)
            points.append((n, center))
        ranked = [
            fit
            for fit in fit_candidates(points, models)
            if fit.valid and fit.score is not None
        ]
        if ranked:
            counts[ranked[0].model] += 1
        exponent = empirical_power_exponent(points)
        if exponent is not None and math.isfinite(exponent):
            exponents.append(exponent)
    return counts, exponents, medians


def _wilson_interval(successes: int, trials: int, z: float = 1.96) -> tuple[float, float]:
    if trials <= 0:
        raise ValueError("Wilson interval requires positive trials")
    proportion = successes / trials
    denominator = 1.0 + z * z / trials
    center = (proportion + z * z / (2.0 * trials)) / denominator
    margin = (
        z
        * math.sqrt(proportion * (1.0 - proportion) / trials + z * z / (4.0 * trials * trials))
        / denominator
    )
    return max(0.0, center - margin), min(1.0, center + margin)


def analyze(
    groups: dict[float, list[float]],
    bootstrap: int = 500,
    seed: int = 1,
    relative_tolerance: float = DEFAULT_RELATIVE_TOLERANCE,
    models: Sequence[str] | None = None,
) -> Analysis:
    if len(groups) < 3:
        raise ValueError("at least 3 distinct input sizes are required")
    if bootstrap < 0:
        raise ValueError("bootstrap iterations must be >= 0")
    if not math.isfinite(relative_tolerance) or relative_tolerance <= 0:
        raise ValueError("relative tolerance must be finite and > 0")
    for n, values in groups.items():
        if not math.isfinite(n) or n <= 0:
            raise ValueError("every input size must be finite and > 0")
        if not values:
            raise ValueError(f"input size {n} has no samples")
        if any(not math.isfinite(value) or value <= 0 for value in values):
            raise ValueError(f"input size {n} has a sample that is not finite and > 0")

    selected_models = list(models) if models is not None else list(MODELS)
    fit_candidates([(n, _stable_median(values)) for n, values in sorted(groups.items())], selected_models)
    search_mode = "pre-specified" if models is not None else "exploratory"

    fewer_than_minimum = [n for n, values in groups.items() if len(values) < MIN_STRONG_REPEATS]
    has_resampling_variation = any(len(set(values)) > 1 for values in groups.values())
    range_is_narrow = math.log(max(groups)) - math.log(min(groups)) < math.log(16.0)
    design_reasons: list[str] = []
    if len(groups) < MIN_STRONG_SIZES:
        design_reasons.append(f"fewer than {MIN_STRONG_SIZES} distinct input sizes")
    if range_is_narrow:
        design_reasons.append("input-size range below 16x")
    if fewer_than_minimum:
        design_reasons.append(
            f"{len(fewer_than_minimum)} size(s) with fewer than {MIN_STRONG_REPEATS} repetitions"
        )
    if bootstrap < MIN_BOOTSTRAP_ITERATIONS:
        design_reasons.append(
            f"fewer than {MIN_BOOTSTRAP_ITERATIONS} bootstrap iterations"
        )
    if not has_resampling_variation:
        design_reasons.append("no within-size variation available for resampling")

    can_resample = (
        bootstrap >= MIN_BOOTSTRAP_ITERATIONS
        and not fewer_than_minimum
        and has_resampling_variation
    )
    counts = {model: 0 for model in selected_models}
    exponent_draws: list[float] = []
    median_draws: dict[float, list[float]] = {}
    actual_bootstrap = 0
    if can_resample:
        counts, exponent_draws, median_draws = bootstrap_diagnostics(
            groups, bootstrap, seed, selected_models
        )
        actual_bootstrap = bootstrap

    aggregates = aggregate_groups(groups, median_draws)
    points = [(item.n, item.median) for item in aggregates]
    fits = fit_candidates(points, selected_models)
    ranked = [fit for fit in fits if fit.valid and fit.score is not None]
    best = ranked[0] if ranked else None
    runner_up = ranked[1] if len(ranked) > 1 else None
    stability = {
        model: count / actual_bootstrap
        for model, count in counts.items()
        if actual_bootstrap and count
    }
    best_stability = stability.get(best.model) if best else None
    best_stability_ci: tuple[float, float] | None = None
    if best and actual_bootstrap:
        best_stability_ci = _wilson_interval(counts[best.model], actual_bootstrap)

    warnings = [
        "Finite empirical measurements do not prove asymptotic Big O.",
        "Fits use additive OLS on median values; validation error is multiplicative on held-out sizes.",
        "Bootstrap assumes within-size rows are exchangeable independent samples; paired runs need block analysis.",
    ]
    if search_mode == "exploratory":
        warnings.append(
            "All built-in shapes were searched exploratorily; pre-specify --models when theory narrows candidates."
        )
    if len(groups) < 6:
        warnings.append("Fewer than 6 distinct sizes weakens scaling discrimination.")
    if range_is_narrow:
        warnings.append("The input-size range is below 16x, so fixed costs may dominate.")
    low_repeats = [n for n, values in groups.items() if len(values) < 5]
    if low_repeats:
        warnings.append(f"{len(low_repeats)} size(s) have fewer than 5 samples.")
    noisy = [
        item.n for item in aggregates if item.median > 0 and item.mad / item.median > 0.10
    ]
    if noisy:
        warnings.append(f"{len(noisy)} size(s) have MAD above 10% of the median.")

    tolerance_log = math.log1p(relative_tolerance)
    if design_reasons:
        conclusion = "insufficient-design"
        warnings.append("Strong compatibility label blocked: " + "; ".join(design_reasons) + ".")
    elif (
        best is None
        or best.loocv_log_rmse is None
        or best.tail_log_rmse is None
        or best.loocv_log_rmse > tolerance_log
        or best.tail_log_rmse > tolerance_log
    ):
        conclusion = "none-adequate"
        warnings.append(
            "No candidate meets the predeclared relative predictive tolerance "
            f"of {relative_tolerance:.1%} on both validation checks."
        )
    elif best_stability_ci is None or best_stability_ci[0] <= 0.50:
        conclusion = "ambiguous"
        warnings.append(
            "Bootstrap selection does not put the leading shape above 50% with 95% Monte Carlo confidence."
        )
    else:
        conclusion = "compatible-over-observed-range"

    exponent = empirical_power_exponent(points)
    exponent_result: dict[str, float | list[float]] | None = None
    if exponent is not None:
        exponent_result = {"estimate": exponent}
        if exponent_draws:
            ordered = sorted(exponent_draws)
            exponent_result["ci95"] = [
                _percentile(ordered, 0.025),
                _percentile(ordered, 0.975),
            ]

    return Analysis(
        claim_kind="empirical_growth",
        observed_range={"min_n": min(groups), "max_n": max(groups)},
        distinct_sizes=len(groups),
        total_samples=sum(len(values) for values in groups.values()),
        best_shape=best.model if best else None,
        runner_up=runner_up.model if runner_up else None,
        conclusion=conclusion,
        selection_stability=best_stability,
        selection_stability_ci95=best_stability_ci,
        bootstrap_iterations=actual_bootstrap,
        bootstrap_mcse_max=(0.5 / math.sqrt(actual_bootstrap)) if actual_bootstrap else None,
        relative_tolerance=relative_tolerance,
        models_considered=selected_models,
        search_mode=search_mode,
        empirical_power_exponent=exponent_result,
        aggregates=aggregates,
        local_growth=calculate_local_growth(points),
        fits=fits,
        model_stability=dict(sorted(stability.items(), key=lambda item: item[1], reverse=True)),
        warnings=warnings,
    )


def _number(value: float | None, digits: int = 4) -> str:
    if value is None:
        return "—"
    if not math.isfinite(value):
        return "invalid"
    return f"{value:.{digits}g}"


def render_markdown(result: Analysis) -> str:
    lines = [
        "# Empirical scaling diagnostic",
        "",
        f"Conclusion: {result.conclusion}; leading shape: {result.best_shape or 'none'}.",
        "",
        (
            f"Range: {_number(result.observed_range['min_n'])} to "
            f"{_number(result.observed_range['max_n'])}; "
            f"{result.distinct_sizes} sizes; {result.total_samples} samples."
        ),
        (
            f"Search: {result.search_mode}; models: {', '.join(result.models_considered)}; "
            f"relative predictive tolerance: {result.relative_tolerance:.1%}; "
            f"bootstrap iterations used: {result.bootstrap_iterations}."
        ),
        "",
        "## Warnings",
        "",
    ]
    lines.extend(f"- {warning}" for warning in result.warnings)
    lines.extend(
        [
            "",
            "## Aggregates",
            "",
            "| n | samples | median | mean | MAD | min | max | median 95% bootstrap interval |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in result.aggregates:
        interval = "—"
        if item.median_ci95:
            interval = f"[{_number(item.median_ci95[0])}, {_number(item.median_ci95[1])}]"
        lines.append(
            f"| {_number(item.n)} | {item.count} | {_number(item.median)} | "
            f"{_number(item.mean)} | {_number(item.mad)} | {_number(item.minimum)} | "
            f"{_number(item.maximum)} | {interval} |"
        )
    lines.extend(
        [
            "",
            "## Adjacent growth",
            "",
            "| from n | to n | size ratio | value ratio | local empirical exponent |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    for item in result.local_growth:
        lines.append(
            f"| {_number(item.from_n)} | {_number(item.to_n)} | "
            f"{_number(item.size_ratio)} | {_number(item.value_ratio)} | "
            f"{_number(item.empirical_exponent)} |"
        )
    lines.extend(
        [
            "",
            "## Candidate shapes",
            "",
            "| shape | LOOCV rank score | LOOCV log-RMSE | tail log-RMSE | NRMSE | R2 | stability |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for fit in result.fits:
        stability = result.model_stability.get(fit.model)
        stability_text = f"{stability:.1%}" if stability is not None else "—"
        lines.append(
            f"| {fit.model} | {_number(fit.score)} | {_number(fit.loocv_log_rmse)} | "
            f"{_number(fit.tail_log_rmse)} | {_number(fit.nrmse)} | "
            f"{_number(fit.r_squared)} | {stability_text} |"
        )
    lines.extend(["", "## Empirical power-law slope", ""])
    if result.empirical_power_exponent is None:
        lines.append("Unavailable.")
    else:
        estimate = float(result.empirical_power_exponent["estimate"])
        interval = result.empirical_power_exponent.get("ci95")
        text = f"p = {_number(estimate)} from log(value) = c + p log(n)"
        if isinstance(interval, list):
            text += f", bootstrap 95% interval [{_number(interval[0])}, {_number(interval[1])}]"
        lines.append(text + ". This is a finite-range diagnostic, not an asymptotic proof.")
    if result.selection_stability_ci95:
        lines.extend(
            [
                "",
                "## Selection stability",
                "",
                (
                    f"Leading-shape frequency: {result.selection_stability:.1%}; "
                    f"95% Monte Carlo Wilson interval "
                    f"[{result.selection_stability_ci95[0]:.1%}, "
                    f"{result.selection_stability_ci95[1]:.1%}]. "
                    "This is not a probability that the model is true."
                ),
            ]
        )
    return "\n".join(lines) + "\n"


def _synthetic_groups(shape: str) -> dict[float, list[float]]:
    groups: dict[float, list[float]] = {}
    for index, n in enumerate((8, 16, 32, 64, 128, 256, 512, 1024)):
        base = 2.0 + 0.01 * MODELS[shape](float(n))
        groups[float(n)] = [
            base * (1.0 + 0.008 * math.sin(index * 3.0 + repetition))
            for repetition in range(7)
        ]
    return groups


def self_test() -> None:
    linear = analyze(_synthetic_groups("linear"), bootstrap=250, seed=11)
    if linear.best_shape != "linear":
        raise AssertionError(f"expected linear data to select linear, got {linear.best_shape}")
    if linear.conclusion != "compatible-over-observed-range":
        raise AssertionError(f"expected compatible linear data, got {linear.conclusion}")
    n_log_n = analyze(_synthetic_groups("n_log_n"), bootstrap=250, seed=17)
    if n_log_n.best_shape != "n_log_n":
        raise AssertionError(f"expected n_log_n data to select n_log_n, got {n_log_n.best_shape}")
    try:
        analyze({1.0: [1.0], 2.0: [2.0]}, bootstrap=0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected fewer than 3 sizes to fail")
    print("Self-test passed: linear, n_log_n, and invalid-input checks.")


def _parse_models(value: str | None) -> list[str] | None:
    if value is None:
        return None
    models = [item.strip() for item in value.split(",") if item.strip()]
    if not models:
        raise ValueError("--models must name at least one model")
    unknown = set(models) - set(MODELS)
    if unknown:
        raise ValueError(f"unknown model(s): {', '.join(sorted(unknown))}")
    if len(models) != len(set(models)):
        raise ValueError("--models must not contain duplicates")
    return models


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Explore empirical growth shapes. Results do not prove Big O."
    )
    parser.add_argument("csv_path", nargs="?", type=Path, help="CSV with size/value rows")
    parser.add_argument("--size-column", default="n", help="size column name")
    parser.add_argument("--time-column", default="time", help="measured-value column name")
    parser.add_argument("--bootstrap", type=int, default=500, help="bootstrap resamples")
    parser.add_argument("--seed", type=int, default=1, help="bootstrap random seed")
    parser.add_argument(
        "--relative-tolerance",
        type=float,
        default=DEFAULT_RELATIVE_TOLERANCE,
        help="maximum relative predictive error for compatibility (default: 0.25)",
    )
    parser.add_argument(
        "--models",
        help="comma-separated pre-specified shapes; default searches all built-ins",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--self-test", action="store_true", help="run built-in tests")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.self_test:
        self_test()
        return 0
    if args.csv_path is None:
        parser.error("csv_path is required unless --self-test is used")
    try:
        groups = read_csv(args.csv_path, args.size_column, args.time_column)
        models = _parse_models(args.models)
        result = analyze(
            groups,
            bootstrap=args.bootstrap,
            seed=args.seed,
            relative_tolerance=args.relative_tolerance,
            models=models,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, sort_keys=True, allow_nan=False))
    else:
        print(render_markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
