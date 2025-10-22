from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from typing import Deque, Dict, List

from data_loader import MarketDataPoint


class Strategy(ABC):
    """Abstract trading strategy."""

    def __init__(self, lookback_window: int, threshold: float) -> None:
        self.lookback_window = lookback_window
        self.threshold = threshold

    @abstractmethod
    def generate_signals(self, tick: "MarketDataPoint") -> List[dict]:
        raise NotImplementedError


class MeanReversionStrategy(Strategy):
    def __init__(self, lookback_window: int, threshold: float) -> None:
        super().__init__(lookback_window, threshold)
        self._history: Dict[str, Deque[float]] = {}

    def generate_signals(self, tick: "MarketDataPoint") -> List[dict]:
        history = self._history.setdefault(tick.symbol, deque(maxlen=self.lookback_window))
        history.append(tick.price)
        if len(history) < self.lookback_window:
            return []
        average_price = sum(history) / len(history)
        deviation = (tick.price - average_price) / average_price if average_price else 0.0
        if deviation >= self.threshold:
            return [self._build_signal(tick, "SELL", deviation)]
        if deviation <= -self.threshold:
            return [self._build_signal(tick, "BUY", deviation)]
        return []

    def _build_signal(self, tick: "MarketDataPoint", action: str, deviation: float) -> dict:
        return {
            "symbol": tick.symbol,
            "price": tick.price,
            "action": action,
            "strategy": self.__class__.__name__,
            "deviation": deviation,
            "timestamp": tick.timestamp,
            "size": 100,
        }


class BreakoutStrategy(Strategy):
    def __init__(self, lookback_window: int, threshold: float) -> None:
        super().__init__(lookback_window, threshold)
        self._history: Dict[str, Deque[float]] = {}

    def generate_signals(self, tick: "MarketDataPoint") -> List[dict]:
        history = self._history.setdefault(tick.symbol, deque(maxlen=self.lookback_window))
        history.append(tick.price)
        if len(history) < self.lookback_window:
            return []

        past_prices = list(history)[:-1]
        current_price = tick.price
        if not past_prices:
            return []

        max_price = max(past_prices)
        min_price = min(past_prices)
        breakout_up = (current_price - max_price) / max_price if max_price else 0.0
        breakout_down = (current_price - min_price) / min_price if min_price else 0.0

        if breakout_up >= self.threshold:
            return [self._build_signal(tick, "BUY", breakout_up)]
        if breakout_down <= -self.threshold:
            return [self._build_signal(tick, "SELL", breakout_down)]
        return []

    def _build_signal(self, tick: "MarketDataPoint", action: str, breakout: float) -> dict:
        return {
            "symbol": tick.symbol,
            "price": tick.price,
            "action": action,
            "strategy": self.__class__.__name__,
            "breakout": breakout,
            "timestamp": tick.timestamp,
            "size": 100,
        }
