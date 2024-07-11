from enum import Enum
import uuid


class Player:
    def __init__(self, player_id: uuid, name: str):
        self._player_id = player_id
        self.name = name
        self._symbol: str = None

    @property
    def player_id(self):
        return self._player_id

    @property
    def symbol(self):
        if self._symbol is None:
            raise LookupError("A symbol wasn't assinged to a player!")
        return self._symbol

    @symbol.setter
    def symbol(self, symbol: str):
        self._symbol = symbol


class Symbols(Enum):
    X = "X"
    O = "O"
