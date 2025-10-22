from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Dict, List


class Observer(ABC):
    @abstractmethod
    def update(self, signal: Dict) -> None:
        raise NotImplementedError


class SignalPublisher:
    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, signal: Dict) -> None:
        for observer in list(self._observers):
            observer.update(signal)


class LoggerObserver(Observer):
    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger("signal_logger")
        self.records: List[Dict] = []

    def update(self, signal: Dict) -> None:
        self.records.append(signal)
        self.logger.info("Signal generated: %s", signal)


class AlertObserver(Observer):
    def __init__(self, threshold_notional: float) -> None:
        self.threshold_notional = threshold_notional
        self.alerts: List[Dict] = []

    def update(self, signal: Dict) -> None:
        size = abs(signal.get("size", 1))
        price = signal.get("price", 0.0)
        notional = size * price
        if notional >= self.threshold_notional:
            alert = dict(signal)
            alert["notional"] = notional
            self.alerts.append(alert)
