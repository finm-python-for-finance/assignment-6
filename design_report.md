# Design Report

## Overview

The project models a modular trading and analytics stack that exercises creational, structural, and behavioral design patterns. Each pattern addresses a realistic concern—instrument instantiation, portfolio composition, analytics extensibility, and signal-driven execution.

## Creational Patterns

- **Factory**: `InstrumentFactory` instantiates `Stock`, `Bond`, and `ETF` objects from CSV rows, encapsulating parsing concerns (including ISO date handling for bond maturities).
- **Singleton**: `Config` loads and exposes `config.json` once via a `SingletonMeta`. All modules receive consistent configuration references.
- **Builder**: `PortfolioBuilder` constructs nested `Portfolio` trees from dictionaries (e.g., `portfolio_structure.json`) while supporting fluent `add_position`, `add_subportfolio`, and `set_owner` chaining.

## Structural Patterns

- **Decorator**: `VolatilityDecorator`, `BetaDecorator`, and `DrawdownDecorator` layer analytics on any `Instrument` without altering core classes. Decorators stack in `main.py` to produce composite metrics.
- **Adapter**: `YahooFinanceAdapter` (JSON) and `BloombergXMLAdapter` (XML) normalise external feeds into `MarketDataPoint` objects for the engine.
- **Composite**: `PortfolioComponent` defines the tree contract. `Position` acts as a leaf; `PortfolioGroup` and `Portfolio` aggregate values, enable recursive traversals, and feed reporting utilities.

## Behavioral Patterns

- **Strategy**: `Strategy` abstracts signal generation; `MeanReversionStrategy` and `BreakoutStrategy` maintain rolling state and emit order intents. `TradingEngine` can hot-swap strategies at runtime.
- **Observer**: `SignalPublisher` manages `LoggerObserver` and `AlertObserver`, keeping logging/reporting decoupled from signal creation.
- **Command**: `ExecuteOrderCommand`, `UndoOrderCommand`, and `CommandInvoker` encapsulate order lifecycle with undo/redo support backed by a lightweight `OrderBook`.

## Testing

`pytest` suites validate:
- Factory output types and Singleton behavior.
- Decorator metric augmentation.
- Observer notifications and command undo/redo semantics.
- Strategy signal correctness for deterministic price series.

## Tradeoffs

- Decorators compute analytics eagerly for clarity; for large datasets, memoisation or streaming windows would reduce cost.
- Command pattern uses an in-memory `OrderBook`; a production system would persist execution state.
- Strategies operate per-symbol without shared context; cross-asset logic would layer on a coordinator or mediator.

## Extensibility

Adding instruments, analytics, or strategies requires only new subclasses or decorator instances. The adapters accept alternative sources by implementing `get_data`, and the command history enables experimentation with execution policies without modifying engine code.
