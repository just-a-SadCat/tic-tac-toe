from app.exc import IncorrectInput, InvalidPlay
from app.player import Player


class Board:
    def __init__(self) -> None:
        self._fields = [
            ["[ ]", "[ ]", "[ ]"],
            ["[ ]", "[ ]", "[ ]"],
            ["[ ]", "[ ]", "[ ]"],
        ]

    def print_board(self) -> None:
        for row in self._fields:
            print(row[0], row[1], row[2])

    def edit_field(self, symbol: str, row: int, col: int) -> None:
        if row < 0 or col < 0:
            raise IncorrectInput("Thr input was a zero or a negative number")
        try:
            if self._fields[row][col] == "[ ]":
                self._fields[row][col] = f"[{symbol}]"
            else:
                raise InvalidPlay("A used field was chosen")
        except IndexError:
            raise IncorrectInput("The chosen indexes were invalid")

    def check_victory(self, player: Player) -> bool:
        symbol = f"[{player.symbol}]"

        for row in self._fields:
            if all(col == symbol for col in row):
                print(f"{player.name} wins, a full row!")
                return True

        for col in range(0, 3):
            if all(self._fields[i][col] == symbol for i in range(3)):
                print(f"{player.name} wins, a full column!")
                return True

        if all(self._fields[i][i] == symbol for i in range(3)):
            print(f"{player.name} wins, a full diagonal!")
            return True

        if (
            self._fields[0][2] == symbol
            and self._fields[1][1] == symbol
            and self._fields[2][0] == symbol
        ):
            print(f"{player.name} wins, a full diagonal!")
            return True

        return False

    def check_stalemate(self) -> bool:
        for row in self._fields:
            for col in row:
                if col == "[ ]":
                    return False
        return True
