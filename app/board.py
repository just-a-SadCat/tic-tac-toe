from app.exc import IncorrectInput, InvalidPlay
from app.player import Player


class Board:
    def __init__(self):
        self._fields = [
            ["[ ]", "[ ]", "[ ]"],
            ["[ ]", "[ ]", "[ ]"],
            ["[ ]", "[ ]", "[ ]"],
        ]

    def check_victory(self, player: Player):
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

    def check_stalemate(self):
        for row in self._fields:
            for col in row:
                if col == "[ ]":
                    return False
        return True

    def edit_field(self, symbol: str) -> None:
        try:
            print("Select (Pick from 1 to 3): 1.row 2.column:")
            x = int(input()) - 1
            y = int(input()) - 1
        except ValueError:
            raise IncorrectInput("The input was not a number")

        if x < 0 or y < 0:
            raise IncorrectInput("Thr input was a zero or a negative number")
        try:
            if self._fields[x][y] == "[ ]":
                self._fields[x][y] = f"[{symbol}]"
            else:
                raise InvalidPlay("A used field was chosen")
        except IndexError:
            raise IncorrectInput("The chosen indexes were invalid")

    def print_board(self) -> None:
        for row in self._fields:
            print(row[0], row[1], row[2])
