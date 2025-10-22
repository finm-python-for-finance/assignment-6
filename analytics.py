from __future__ import annotations

from statistics import mean, pstdev
from typing import Iterable, List


def _to_return_series(prices: Iterable[float]) -> List[float]:
    items = list(prices)
    if len(items) < 2:
        return []
    return [(items[i] / items[i - 1]) - 1 for i in range(1, len(items)) if items[i - 1] != 0]


def calculate_volatility(prices: Iterable[float]) -> float:
    returns = _to_return_series(prices)
    if len(returns) < 2:
        return 0.0
    return pstdev(returns)


def calculate_beta(asset_prices: Iterable[float], benchmark_prices: Iterable[float]) -> float:
    asset_returns = _to_return_series(asset_prices)
    benchmark_returns = _to_return_series(benchmark_prices)
    length = min(len(asset_returns), len(benchmark_returns))
    if length == 0:
        return 0.0

    asset_returns = asset_returns[-length:]
    benchmark_returns = benchmark_returns[-length:]
    benchmark_mean = mean(benchmark_returns)
    asset_mean = mean(asset_returns)

    covariance = sum(
        (a - asset_mean) * (b - benchmark_mean) for a, b in zip(asset_returns, benchmark_returns)
    ) / length
    variance = sum((b - benchmark_mean) ** 2 for b in benchmark_returns) / length
    if variance == 0:
        return 0.0
    return covariance / variance


def calculate_max_drawdown(prices: Iterable[float]) -> float:
    series = list(prices)
    if not series:
        return 0.0

    peak = series[0]
    max_drawdown = 0.0
    for price in series:
        peak = max(peak, price)
        if peak == 0:
            continue
        drawdown = (price - peak) / peak
        max_drawdown = min(max_drawdown, drawdown)
    return abs(max_drawdown)
