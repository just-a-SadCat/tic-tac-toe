from dataclasses import dataclass
from enum import StrEnum
import uuid


@dataclass
class Player:
    def __init__(self, player_id: uuid.UUID, name: str) -> None:
        self._player_id = player_id
        self.name = name
        self._symbol: str | None = None

    @property
    def player_id(self) -> int:
        return self._player_id

    @property
    def symbol(self) -> str:
        if self._symbol is None:
            raise LookupError("A symbol wasn't assinged to a player!")
        return self._symbol

    @symbol.setter
    def symbol(self, symbol: str) -> None:
        self._symbol = symbol


class Symbols(StrEnum):
    X = "X"
    O = "O"
