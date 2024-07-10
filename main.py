
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
        self.fields = [["[ ]","[ ]","[ ]"],["[ ]","[ ]","[ ]"],["[ ]","[ ]","[ ]"]]


    def check_victory(self, symbol, player_name):
        symbol = f"[{symbol}]"

        for x in range (0, 3):
            if self.fields[x][0] == symbol and self.fields[x][1] == symbol and self.fields[x][2] == symbol:
                print(f"{player_name} wins, a full row!")
                return True
            
        for y in range(0, 3):
            if self.fields[0][y] == symbol and self.fields[1][y] == symbol and self.fields[2][y] == symbol:
                print(f"{player_name} wins, a full column!")
                return True
            
        if self.fields[0][0] == symbol and self.fields[1][1] == symbol and self.fields[2][2] == symbol:
            print(f"{player_name} wins, a full diagonal!")
            return True
        
        if self.fields[0][2] == symbol and self.fields[1][1] == symbol and self.fields[2][0] == symbol:
            print(f"{player_name} wins, a full diagonal!")
            return True
        
        return False

    def check_stalemate(self):
        for x in range(0, 3):
            for y in range (0, 3):
                if self.fields[x][y] == "[ ]":
                    return False
        return True


    def edit_field(self, symbol):
        try:
            x = int(input("Select row: "))
            y = int(input("Select column: "))
        except ValueError:
            print("Incorrect input, was not a number!")

        try:
            if x > 3 or x < 1 or y > 3 or y < 0:
                print("Please pick a number from 1 to 3!!")
                return False

            if self.fields[x-1][y-1] == "[ ]":
                self.fields[x-1][y-1] = f"[{symbol}]"
            else:
                print("This field is already taken!")
                return False
            return True
        
        except UnboundLocalError:
            print("Input incorrect, try again!")
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
        self.first_player.symbol = "X"
        self.second_player.symbol = "O"

    def swap_players(self, previous_player: Player):
        if previous_player is self.first_player:
            return self.second_player
        return self.first_player

    def begin_game(self):
        active_player: Player = self.first_player
        while True:
            print(f"Current player: {active_player.name}")
            board.print_board()
            move_result = board.edit_field(active_player.symbol)
            if move_result:
                if board.check_victory(active_player.symbol, active_player.name):
                    board.print_board()
                    break
                active_player = self.swap_players(active_player)
            if(board.check_stalemate()):
                print("It's a stalemate!")
                board.print_board()
                break
            
                
player1 = Player(420, "Andrew")
player2 = Player(69, "Ashley")

board = Board()

room = Room(1, board, player1, player2)

room.assign_symbols()
room.begin_game()
