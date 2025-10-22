from __future__ import annotations

from datetime import datetime, timedelta

from data_loader import InstrumentCSVLoader, MarketDataPoint
from models import BetaDecorator, DrawdownDecorator, Stock, VolatilityDecorator
from patterns.command import CommandInvoker, ExecuteOrderCommand, OrderBook, UndoOrderCommand
from patterns.observer import AlertObserver, LoggerObserver, SignalPublisher
from patterns.singleton import Config
from patterns.strategy import BreakoutStrategy, MeanReversionStrategy


def test_factory_creates_instrument_types():
    instruments = InstrumentCSVLoader("instruments.csv").load()
    assert any(inst.__class__.__name__ == "Stock" for inst in instruments)
    assert any(inst.__class__.__name__ == "Bond" for inst in instruments)
    assert any(inst.__class__.__name__ == "ETF" for inst in instruments)


def test_config_singleton():
    config_a = Config()
    config_b = Config()
    assert config_a is config_b
    assert "log_level" in config_a.data


def test_decorators_add_metrics():
    base_instrument = Stock("TEST", 100.0, "Tech", "Test Inc")
    price_history = [100, 102, 101, 103, 105]
    benchmark_history = [200, 199, 201, 202, 204]
    decorated = VolatilityDecorator(base_instrument, price_history)
    decorated = BetaDecorator(decorated, price_history, benchmark_history)
    decorated = DrawdownDecorator(decorated, price_history)
    metrics = decorated.get_metrics()
    assert "volatility" in metrics and metrics["volatility"] >= 0
    assert "beta" in metrics
    assert "max_drawdown" in metrics


def test_observer_notifications_and_command_lifecycle():
    publisher = SignalPublisher()
    logger = LoggerObserver()
    alert = AlertObserver(threshold_notional=1_000)
    publisher.attach(logger)
    publisher.attach(alert)

    signal = {
        "symbol": "AAPL",
        "price": 200.0,
        "action": "BUY",
        "size": 10,
        "strategy": "TestStrategy",
        "timestamp": datetime.utcnow(),
    }
    publisher.notify(signal)
    assert logger.records[-1] == signal
    assert alert.alerts and alert.alerts[-1]["notional"] == 2000.0

    order_book = OrderBook()
    invoker = CommandInvoker()
    execute_command = ExecuteOrderCommand(order_book, signal)
    invoker.execute(execute_command)
    assert order_book.executed_orders[-1] == signal

    undo_command = UndoOrderCommand(order_book, signal)
    invoker.execute(undo_command)
    assert signal not in order_book.executed_orders

    invoker.undo()
    assert signal in order_book.executed_orders

    invoker.undo()
    assert signal not in order_book.executed_orders

    invoker.redo()
    assert signal in order_book.executed_orders


def test_strategy_outputs_expected_signals():
    timestamps = [datetime.utcnow() + timedelta(seconds=i) for i in range(5)]
    mean_reversion = MeanReversionStrategy(lookback_window=3, threshold=0.05)
    prices = [100, 100, 100, 120]
    signals = []
    for ts, price in zip(timestamps, prices):
        tick = MarketDataPoint(timestamp=ts, symbol="TEST", price=price)
        signals.extend(mean_reversion.generate_signals(tick))
    assert signals and signals[-1]["action"] == "SELL"

    breakout = BreakoutStrategy(lookback_window=3, threshold=0.05)
    signals = []
    breakout_prices = [100, 101, 102, 110]
    for ts, price in zip(timestamps, breakout_prices):
        tick = MarketDataPoint(timestamp=ts, symbol="TEST", price=price)
        signals.extend(breakout.generate_signals(tick))
    assert signals and signals[-1]["action"] == "BUY"
