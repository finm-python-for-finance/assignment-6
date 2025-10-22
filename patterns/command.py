from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def undo(self) -> None:
        raise NotImplementedError


class OrderBook:
    """Minimal in-memory order book for command demonstrations."""

    def __init__(self) -> None:
        self._executed_orders: List[Dict] = []

    def execute(self, order: Dict) -> None:
        self._executed_orders.append(order)

    def reverse(self, order: Dict) -> None:
        if order in self._executed_orders:
            self._executed_orders.remove(order)

    @property
    def executed_orders(self) -> List[Dict]:
        return list(self._executed_orders)


class ExecuteOrderCommand(Command):
    def __init__(self, order_book: OrderBook, order: Dict) -> None:
        self.order_book = order_book
        self.order = order

    def execute(self) -> None:
        self.order_book.execute(self.order)

    def undo(self) -> None:
        self.order_book.reverse(self.order)


class UndoOrderCommand(Command):
    def __init__(self, order_book: OrderBook, order: Dict) -> None:
        self.order_book = order_book
        self.order = order

    def execute(self) -> None:
        self.order_book.reverse(self.order)

    def undo(self) -> None:
        self.order_book.execute(self.order)


class CommandInvoker:
    def __init__(self) -> None:
        self._history: List[Command] = []
        self._redo_stack: List[Command] = []

    def execute(self, command: Command) -> None:
        command.execute()
        self._history.append(command)
        self._redo_stack.clear()

    def undo(self) -> Optional[Command]:
        if not self._history:
            return None
        command = self._history.pop()
        command.undo()
        self._redo_stack.append(command)
        return command

    def redo(self) -> Optional[Command]:
        if not self._redo_stack:
            return None
        command = self._redo_stack.pop()
        command.execute()
        self._history.append(command)
        return command
