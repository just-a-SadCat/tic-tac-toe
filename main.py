board = [["[ ]","[ ]","[ ]"],["[ ]","[ ]","[ ]"],["[ ]","[ ]","[ ]"]]

class Player():
    player_id: int
    name: str


class Room():
    room_id: int
    first_player_id: int
    second_player_id: int


def print_board(board: list[list[str]]):
    for i in range(0, 3):
        print(board[i][0], board[i][1], board[i][2])


def check_victory(board: list[list[str]], x: int, y: int, symbol: str):
    if board[x][0] == symbol and board[x][1] == symbol and board[x][2] == symbol:
        print("Player wins, a full row!")
        return True
    if board[0][y] == symbol and board[1][y] == symbol and board[2][y] == symbol:
        print("Player wins, a full column!")
        return True
    if board[0][0] == symbol and board[1][1] == symbol and board[2][2] == symbol:
        print("Player wins, a full diagonal!")
        return True
    if board[0][2] == symbol and board[1][1] == symbol and board[2][0] == symbol:
        print("Player wins, a full diagonal!")
        return True
    return False


def change_active_player():
    ...


def edit_field(board: list[list[str]], symbol: str):
    x = int(input("Select row:"))
    y = int(input("Select column: "))

    if board[x-1][y-1] == "[ ]":
        board[x-1][y-1] = f"[{symbol}]"
    else:
        print("This field is already taken!")

    if check_victory(board, x - 1, y - 1, f"[{symbol}]"):
        return True
    return False


x = 0
while x == 0:
    print_board(board)
    if edit_field(board, "X"):
        x = 1
print_board(board)
