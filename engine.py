from __future__ import annotations

from typing import Iterable, Optional

from data_loader import MarketDataPoint
from patterns.command import CommandInvoker, ExecuteOrderCommand, OrderBook
from patterns.observer import SignalPublisher
from patterns.strategy import Strategy


class TradingEngine:
    """Coordinates market data ingestion, strategy execution, and order commands."""

    def __init__(
        self,
        strategy: Strategy,
        publisher: SignalPublisher,
        invoker: Optional[CommandInvoker] = None,
        order_book: Optional[OrderBook] = None,
    ) -> None:
        self.strategy = strategy
        self.publisher = publisher
        self.invoker = invoker or CommandInvoker()
        self.order_book = order_book or OrderBook()

    def process_tick(self, tick: MarketDataPoint) -> None:
        signals = self.strategy.generate_signals(tick)
        for signal in signals:
            self.publisher.notify(signal)
            command = ExecuteOrderCommand(self.order_book, signal)
            self.invoker.execute(command)

    def run(self, ticks: Iterable[MarketDataPoint]) -> None:
        for tick in ticks:
            self.process_tick(tick)

    def switch_strategy(self, strategy: Strategy) -> None:
        self.strategy = strategy
