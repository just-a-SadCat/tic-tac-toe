from app.exc import IncorrectInput, InvalidPlay


class Board:
    def __init__(self):
        self.fields = [
            ["[ ]", "[ ]", "[ ]"],
            ["[ ]", "[ ]", "[ ]"],
            ["[ ]", "[ ]", "[ ]"],
        ]

    def check_victory(self, player):
        symbol = f"[{player.symbol}]"

        for x in range(0, 3):
            if (
                self.fields[x][0] == symbol
                and self.fields[x][1] == symbol
                and self.fields[x][2] == symbol
            ):
                print(f"{player.name} wins, a full row!")
                return True

        for y in range(0, 3):
            if (
                self.fields[0][y] == symbol
                and self.fields[1][y] == symbol
                and self.fields[2][y] == symbol
            ):
                print(f"{player.name} wins, a full column!")
                return True

        if (
            self.fields[0][0] == symbol
            and self.fields[1][1] == symbol
            and self.fields[2][2] == symbol
        ):
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

    def check_stalemate(self):
        for x in range(0, 3):
            for y in range(0, 3):
                if self.fields[x][y] == "[ ]":
                    return False
        return True

    def edit_field(self, symbol) -> None:
        try:
            print("Select (Pick from 1 to 3): 1.row 2.column:")
            x = int(input())
            y = int(input())
        except ValueError:
            raise IncorrectInput("The input was not a number")

        if x > 3 or x < 1 or y > 3 or y < 0:
            raise IncorrectInput(
                "The input was a number not corresponding to any row/column"
            )

        if self.fields[x - 1][y - 1] == "[ ]":
            self.fields[x - 1][y - 1] = f"[{symbol}]"
        else:
            raise InvalidPlay("A used field was chosen")

    def print_board(self):
        for i in range(0, 3):
            print(self.fields[i][0], self.fields[i][1], self.fields[i][2])
