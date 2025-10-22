from __future__ import annotations

import json
from pathlib import Path

from data_loader import (
    BloombergXMLAdapter,
    InstrumentCSVLoader,
    MarketDataLoader,
    YahooFinanceAdapter,
)
from engine import TradingEngine
from models import BetaDecorator, DrawdownDecorator, Instrument, Portfolio, VolatilityDecorator
from patterns.builder import PortfolioBuilder
from patterns.command import CommandInvoker
from patterns.observer import SignalPublisher
from patterns.singleton import Config
from patterns.strategy import BreakoutStrategy, MeanReversionStrategy, Strategy
from reporting import SignalReporter, portfolio_snapshot


def _load_strategy_params(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_portfolio(path: str | Path) -> Portfolio:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return PortfolioBuilder.from_dict(data)


def _decorate_instrument_with_metrics(instrument: Instrument, benchmark_symbol: str, history_window: int = 50) -> Instrument:
    loader = MarketDataLoader("market_data.csv")
    price_history = [tick.price for tick in loader.iter_ticks(symbols=[instrument.symbol], limit=history_window)]
    benchmark_history = [
        tick.price for tick in MarketDataLoader("market_data.csv").iter_ticks(symbols=[benchmark_symbol], limit=history_window)
    ]
    decorated = VolatilityDecorator(instrument, price_history)
    decorated = BetaDecorator(decorated, price_history, benchmark_history)
    decorated = DrawdownDecorator(decorated, price_history)
    return decorated


def _instantiate_strategy(name: str, params: dict) -> Strategy:
    if name == "MeanReversionStrategy":
        return MeanReversionStrategy(params["lookback_window"], params["threshold"])
    if name == "BreakoutStrategy":
        return BreakoutStrategy(params["lookback_window"], params["threshold"])
    raise ValueError(f"Unsupported strategy {name}")


def main() -> None:
    config = Config()
    instruments = InstrumentCSVLoader("instruments.csv").load()
    portfolio = _load_portfolio("portfolio_structure.json")

    strategy_params = _load_strategy_params("strategy_params.json")
    default_strategy_name = config.get("default_strategy", "MeanReversionStrategy")
    strategy = _instantiate_strategy(default_strategy_name, strategy_params[default_strategy_name])

    publisher = SignalPublisher()
    reporter = SignalReporter(publisher, alert_threshold=50_000)
    engine = TradingEngine(strategy=strategy, publisher=publisher, invoker=CommandInvoker())

    market_loader = MarketDataLoader("market_data.csv")
    ticks = market_loader.iter_ticks(
        symbols=[instrument.symbol for instrument in instruments], limit=strategy.lookback_window * 5
    )
    engine.run(ticks)

    # Demonstrate strategy interchangeability.
    alternate_name = "BreakoutStrategy" if default_strategy_name != "BreakoutStrategy" else "MeanReversionStrategy"
    alternate_strategy = _instantiate_strategy(alternate_name, strategy_params[alternate_name])
    engine.switch_strategy(alternate_strategy)
    engine.run(
        MarketDataLoader("market_data.csv").iter_ticks(
            symbols=[instrument.symbol for instrument in instruments], limit=alternate_strategy.lookback_window * 3
        )
    )

    # Demonstrate adapters.
    yahoo_point = YahooFinanceAdapter("external_data_yahoo.json").get_data("AAPL")
    bloomberg_point = BloombergXMLAdapter("external_data_bloomberg.xml").get_data("MSFT")
    external_points = [yahoo_point, bloomberg_point]

    # Decorate instrument analytics.
    decorated_instruments = {
        instrument.symbol: _decorate_instrument_with_metrics(instrument, benchmark_symbol="SPY").get_metrics()
        for instrument in instruments
    }

    summary = {
        "config": config.data,
        "portfolio": portfolio_snapshot(portfolio),
        "signals": reporter.summary(),
        "order_count": len(engine.order_book.executed_orders),
        "decorated_metrics": decorated_instruments,
        "external_market_data": {point.symbol: point.price for point in external_points},
    }

    print(json.dumps(summary, default=str, indent=2))


if __name__ == "__main__":
    main()
