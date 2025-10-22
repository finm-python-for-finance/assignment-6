from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator, List, Optional, Sequence
from xml.etree import ElementTree as ET

from models import Instrument
from patterns.factory import InstrumentFactory


@dataclass(frozen=True)
class MarketDataPoint:
    timestamp: datetime
    symbol: str
    price: float


class InstrumentCSVLoader:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> List[Instrument]:
        instruments: List[Instrument] = []
        with self.path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                instruments.append(InstrumentFactory.create_instrument(row))
        return instruments


class MarketDataLoader:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def iter_ticks(
        self, symbols: Optional[Sequence[str]] = None, limit: Optional[int] = None
    ) -> Iterator[MarketDataPoint]:
        symbols_filter = set(symbols) if symbols else None
        count = 0
        with self.path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                symbol = row["symbol"]
                if symbols_filter and symbol not in symbols_filter:
                    continue
                timestamp = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
                price = float(row["price"])
                yield MarketDataPoint(timestamp=timestamp, symbol=symbol, price=price)
                count += 1
                if limit is not None and count >= limit:
                    break


class YahooFinanceAdapter:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def get_data(self, symbol: str) -> MarketDataPoint:
        with self.path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if payload.get("ticker") != symbol:
            raise ValueError(f"Symbol {symbol} not found in Yahoo payload")
        timestamp = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
        return MarketDataPoint(timestamp=timestamp, symbol=symbol, price=float(payload["last_price"]))


class BloombergXMLAdapter:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def get_data(self, symbol: str) -> MarketDataPoint:
        tree = ET.parse(self.path)
        root = tree.getroot()
        xml_symbol = root.findtext("symbol")
        if xml_symbol != symbol:
            raise ValueError(f"Symbol {symbol} not found in Bloomberg payload")
        price = float(root.findtext("price"))
        timestamp = datetime.fromisoformat(root.findtext("timestamp").replace("Z", "+00:00"))
        return MarketDataPoint(timestamp=timestamp, symbol=symbol, price=price)
