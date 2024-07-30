from enum import Enum
import json
from app.exc import IncorrectInput, InvalidPlay
from app.player import Player


class BoardStates(str, Enum):
    NO_WIN = "NO_WIN"
    WIN = "WIN"
    STALEMATE = "STALEMATE"


class Board:
    def __init__(self, fields: str) -> None:
        self._fields = fields

    @property
    def fields(self) -> list[list[str]]:
        result: list[list[str]] = json.loads(self._fields)
        return result

    def edit_field(self, symbol: str, row: int, col: int) -> list[list[str]]:
        board = self.fields
        if row < 1 or col < 1:
            raise IncorrectInput("The input was a zero or a negative number")
        try:
            if board[row - 1][col - 1] == " ":
                board[row - 1][col - 1] = symbol
                return board
            else:
                raise InvalidPlay("A used field was chosen")
        except IndexError:
            raise IncorrectInput("The chosen indexes were invalid")

    def check_victory(self, player: Player) -> bool:
        symbol = player.symbol

        for row in self.fields:
            if all(col == symbol for col in row):
                print(f"{player.name} wins, a full row!")
                return True

        for col in range(0, 3):
            if all(self.fields[i][col] == symbol for i in range(3)):
                print(f"{player.name} wins, a full column!")
                return True

        if all(self.fields[i][i] == symbol for i in range(3)):
            print(f"{player.name} wins, a full diagonal!")
            return True

        if (
            self.fields[0][2] == symbol
            and self.fields[1][1] == symbol
            and self.fields[2][0] == symbol
        ):
            print(f"{player.name} wins, a full diagonal!")
            return True

        return False

    def check_stalemate(self) -> bool:
        for row in self.fields:
            for col in row:
                if col == " ":
                    return False
        return True
