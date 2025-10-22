from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Iterable, List, Optional


class Instrument(ABC):
    """Base domain object representing a financial instrument."""

    def __init__(self, symbol: str, price: float, sector: Optional[str] = None) -> None:
        self.symbol = symbol
        self.price = price
        self.sector = sector

    def get_metrics(self) -> Dict[str, float]:
        """Return base metrics shared by every instrument."""
        return {"price": self.price}

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"{self.__class__.__name__}(symbol={self.symbol}, price={self.price})"


class Stock(Instrument):
    def __init__(self, symbol: str, price: float, sector: Optional[str], issuer: Optional[str]) -> None:
        super().__init__(symbol, price, sector)
        self.issuer = issuer


class Bond(Instrument):
    def __init__(
        self,
        symbol: str,
        price: float,
        sector: Optional[str],
        issuer: Optional[str],
        maturity: Optional[datetime],
    ) -> None:
        super().__init__(symbol, price, sector)
        self.issuer = issuer
        self.maturity = maturity


class ETF(Instrument):
    def __init__(self, symbol: str, price: float, sector: Optional[str], issuer: Optional[str]) -> None:
        super().__init__(symbol, price, sector)
        self.issuer = issuer


class InstrumentDecorator(Instrument):
    """Base decorator for extending instrument analytics without altering the core class."""

    def __init__(self, instrument: Instrument) -> None:
        super().__init__(instrument.symbol, instrument.price, instrument.sector)
        self._instrument = instrument

    def get_metrics(self) -> Dict[str, float]:
        return self._instrument.get_metrics()

    def __getattr__(self, item: str):
        return getattr(self._instrument, item)


class VolatilityDecorator(InstrumentDecorator):
    def __init__(self, instrument: Instrument, price_history: Iterable[float]) -> None:
        super().__init__(instrument)
        self._price_history = list(price_history)

    def get_metrics(self) -> Dict[str, float]:
        from analytics import calculate_volatility

        metrics = super().get_metrics()
        metrics["volatility"] = calculate_volatility(self._price_history)
        return metrics


class BetaDecorator(InstrumentDecorator):
    def __init__(
        self, instrument: Instrument, asset_prices: Iterable[float], benchmark_prices: Iterable[float]
    ) -> None:
        super().__init__(instrument)
        self._asset_prices = list(asset_prices)
        self._benchmark_prices = list(benchmark_prices)

    def get_metrics(self) -> Dict[str, float]:
        from analytics import calculate_beta

        metrics = super().get_metrics()
        metrics["beta"] = calculate_beta(self._asset_prices, self._benchmark_prices)
        return metrics


class DrawdownDecorator(InstrumentDecorator):
    def __init__(self, instrument: Instrument, price_history: Iterable[float]) -> None:
        super().__init__(instrument)
        self._price_history = list(price_history)

    def get_metrics(self) -> Dict[str, float]:
        from analytics import calculate_max_drawdown

        metrics = super().get_metrics()
        metrics["max_drawdown"] = calculate_max_drawdown(self._price_history)
        return metrics


class PortfolioComponent(ABC):
    """Composite root for positions and nested portfolios."""

    @abstractmethod
    def get_value(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def get_positions(self) -> List["Position"]:
        raise NotImplementedError


class Position(PortfolioComponent):
    def __init__(self, symbol: str, quantity: float, price: float) -> None:
        self.symbol = symbol
        self.quantity = quantity
        self.price = price

    def get_value(self) -> float:
        return self.quantity * self.price

    def get_positions(self) -> List["Position"]:
        return [self]

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Position(symbol={self.symbol}, quantity={self.quantity}, price={self.price})"


class PortfolioGroup(PortfolioComponent):
    def __init__(self, name: str) -> None:
        self.name = name
        self._components: List[PortfolioComponent] = []

    def add(self, component: PortfolioComponent) -> None:
        self._components.append(component)

    def get_value(self) -> float:
        return sum(component.get_value() for component in self._components)

    def get_positions(self) -> List[Position]:
        positions: List[Position] = []
        for component in self._components:
            positions.extend(component.get_positions())
        return positions

    @property
    def components(self) -> List[PortfolioComponent]:
        return list(self._components)


class Portfolio(PortfolioGroup):
    def __init__(self, name: str, owner: Optional[str]) -> None:
        super().__init__(name)
        self.owner = owner
