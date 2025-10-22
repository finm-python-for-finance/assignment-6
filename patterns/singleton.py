from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class SingletonMeta(type):
    """Metaclass ensuring only one instance exists."""

    _instances: Dict[type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    """Central configuration singleton shared across modules."""

    def __init__(self, path: str = "config.json") -> None:
        if hasattr(self, "_initialised"):
            return
        self._path = Path(path)
        self._data: Dict[str, Any] = {}
        self._load()
        self._initialised = True

    def _load(self) -> None:
        if not self._path.exists():
            raise FileNotFoundError(f"Config file not found: {self._path}")
        with self._path.open("r", encoding="utf-8") as fh:
            self._data = json.load(fh)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    @property
    def data(self) -> Dict[str, Any]:
        return dict(self._data)
