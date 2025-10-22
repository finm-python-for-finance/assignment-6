from __future__ import annotations

from datetime import datetime
from typing import Dict

from models import Bond, ETF, Instrument, Stock


class InstrumentFactory:
    """Factory responsible for instantiating instruments from raw dictionaries."""

    _type_map = {
        "stock": Stock,
        "bond": Bond,
        "etf": ETF,
    }

    @classmethod
    def create_instrument(cls, data: Dict[str, str]) -> Instrument:
        instrument_type = (data.get("type") or "").lower()
        symbol = data.get("symbol")
        price = float(data.get("price", 0.0))
        sector = data.get("sector")
        issuer = data.get("issuer")
        if instrument_type not in cls._type_map:
            raise ValueError(f"Unsupported instrument type: {instrument_type}")

        if instrument_type == "bond":
            maturity_raw = data.get("maturity")
            maturity = datetime.fromisoformat(maturity_raw) if maturity_raw else None
            return Bond(symbol=symbol, price=price, sector=sector, issuer=issuer, maturity=maturity)
        return cls._type_map[instrument_type](symbol=symbol, price=price, sector=sector, issuer=issuer)
