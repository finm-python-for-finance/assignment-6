from __future__ import annotations

import logging
from typing import Dict

from models import PortfolioComponent
from patterns.observer import AlertObserver, LoggerObserver, SignalPublisher


class SignalReporter:
    """Utility for wiring observers to a publisher and summarising activity."""

    def __init__(self, publisher: SignalPublisher, alert_threshold: float, logger: logging.Logger | None = None) -> None:
        self.logger_observer = LoggerObserver(logger)
        self.alert_observer = AlertObserver(alert_threshold)
        publisher.attach(self.logger_observer)
        publisher.attach(self.alert_observer)

    def summary(self) -> Dict[str, int]:
        return {
            "signals_logged": len(self.logger_observer.records),
            "alerts_triggered": len(self.alert_observer.alerts),
        }


def portfolio_snapshot(component: PortfolioComponent) -> Dict[str, float]:
    """Aggregate simple analytics for a portfolio component tree."""
    total_value = component.get_value()
    positions = component.get_positions()
    return {
        "positions": len(positions),
        "total_value": total_value,
        "symbols": len({pos.symbol for pos in positions}),
    }
