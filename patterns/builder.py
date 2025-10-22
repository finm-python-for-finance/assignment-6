from __future__ import annotations

from typing import Dict, List, Tuple

from models import Portfolio, PortfolioComponent, PortfolioGroup, Position


class PortfolioBuilder:
    """Builder for complex portfolio trees with fluent API."""

    def __init__(self, name: str) -> None:
        self._name = name
        self._owner: str | None = None
        self._positions: List[Tuple[str, float, float]] = []
        self._sub_builders: List[Tuple[str, "PortfolioBuilder"]] = []

    def set_owner(self, name: str) -> "PortfolioBuilder":
        self._owner = name
        return self

    def add_position(self, symbol: str, quantity: float, price: float) -> "PortfolioBuilder":
        self._positions.append((symbol, quantity, price))
        return self

    def add_subportfolio(self, name: str, builder: "PortfolioBuilder") -> "PortfolioBuilder":
        self._sub_builders.append((name, builder))
        return self

    def build(self) -> Portfolio:
        portfolio = Portfolio(self._name, self._owner)
        for symbol, quantity, price in self._positions:
            portfolio.add(Position(symbol, quantity, price))
        for name, builder in self._sub_builders:
            sub_portfolio = builder.build()
            sub_group = PortfolioGroup(name)
            for component in sub_portfolio.components:
                sub_group.add(component)
            portfolio.add(sub_group)
        return portfolio

    @classmethod
    def from_dict(cls, data: Dict) -> Portfolio:
        builder = cls(data.get("name", "Portfolio"))
        if owner := data.get("owner"):
            builder.set_owner(owner)
        for position in data.get("positions", []):
            builder.add_position(
                position["symbol"],
                float(position.get("quantity", 0)),
                float(position.get("price", 0)),
            )
        for sub in data.get("sub_portfolios", []):
            sub_builder = cls(sub.get("name", "SubPortfolio"))
            for position in sub.get("positions", []):
                sub_builder.add_position(
                    position["symbol"],
                    float(position.get("quantity", 0)),
                    float(position.get("price", 0)),
                )
            builder.add_subportfolio(sub_builder._name, sub_builder)
        return builder.build()
