class IncorrectInput(Exception):
    pass


class InvalidPlay(Exception):
    pass


class Player:
    def __init__(self, player_id, name):
        self.player_id = player_id
        self.name = name
        self._symbol = None

    @property
    def symbol(self):
        if self._symbol is None:
            raise LookupError("A symbol wasn't assinged to a player!")
        return self._symbol

    @symbol.setter
    def symbol(self, symbol):
        self._symbol = symbol


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


class Room:
    def __init__(self, room_id, first_player: Player, second_player: Player):
        self.room_id = room_id
        self.first_player = first_player
        self.second_player = second_player
        self.board = Board()
        self._active_player = first_player

    @property
    def active_player(self):
        return self._active_player

    @active_player.setter
    def active_player(self, active_player):
        self._active_player = active_player

    def assign_symbols(self):
        self.first_player.symbol = "X"
        self.second_player.symbol = "O"

    def swap_players(self, previous_player: Player):
        if previous_player is self.first_player:
            self.active_player = self.second_player
            return
        self.active_player = self.first_player

    def make_play(self, active_player):
        self.board.edit_field(active_player.symbol)
        self.swap_players(active_player)


def main(room: Room):
    while True:
        active_player = room.active_player
        print(f"Current player: {active_player.name}")
        room.board.print_board()
        move_result = False
        while move_result is False:
            try:
                room.make_play(active_player)
            except IncorrectInput:
                print("Your input was incorrect, try again!")
            except InvalidPlay:
                print("That play is impossible, try again!")
            else:
                move_result = True

        if room.board.check_victory(active_player):
            room.board.print_board()
            break
        if room.board.check_stalemate():
            print("It's a stalemate!")
            room.board.print_board()
            break


player1 = Player(420, "Andrew")
player2 = Player(69, "Ashley")

room = Room(1, player1, player2)
room.assign_symbols()

main(room)
