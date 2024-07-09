
class Player:
    def __init__(self, player_id, name):
        self.player_id = player_id 
        self.name = name
        self._symbol = None

    @property
    def symbol(self):
        if self._symbol == None:
            raise LookupError("A symbol wasn't assinged to a player!")
        return self._symbol

    @symbol.setter
    def symbol(self, _symbol):
        self._symbol = _symbol


class Board:
    def __init__(self):
        self.fields = [["[ ]","[ ]","[ ]"],["[ ]","[ ]","[ ]"],["[ ]","[ ]","[ ]"]]


    def check_victory(self, x, y, symbol):
        if self.fields[x][0] == symbol and self.fields[x][1] == symbol and self.fields[x][2] == symbol:
            print("Player wins, a full row!")
            return True
        if self.fields[0][y] == symbol and self.fields[1][y] == symbol and self.fields[2][y] == symbol:
            print("Player wins, a full column!")
            return True
        if self.fields[0][0] == symbol and self.fields[1][1] == symbol and self.fields[2][2] == symbol:
            print("Player wins, a full diagonal!")
            return True
        if self.fields[0][2] == symbol and self.fields[1][1] == symbol and self.fields[2][0] == symbol:
            print("Player wins, a full diagonal!")
            return True
        return False


    def edit_field(self, symbol):
        x = int(input("Select row:"))
        y = int(input("Select column: "))

        if self.fields[x-1][y-1] == "[ ]":
            self.fields[x-1][y-1] = f"[{symbol}]"
        else:
            print("This field is already taken!")

        if self.check_victory(x - 1, y - 1, f"[{symbol}]"):
            return True
        return False
    
    
    def print_board(self):
        for i in range(0, 3):
            print(self.fields[i][0], self.fields[i][1], self.fields[i][2])


class Room:
    def __init__(self, room_id, board, first_player: Player, second_player: Player):
        self.room_id = room_id
        self.board = board
        self.first_player = first_player
        self.second_player = second_player

    def assign_symbols(self):
        self.first_player.symbol("X")
        self.second_player.symbol("O")

    def begin_game(self):
        x = 0
        while x == 0:
            board.print_board()
            if board.edit_field(self.first_player.symbol):
                x = 1
        board.print_board



player1 = Player(420, "Andrew")
player2 = Player(69, "Ashley")

board = Board()

room = Room(1, board, player1, player2)

room.assign_symbols()
room.begin_game()
