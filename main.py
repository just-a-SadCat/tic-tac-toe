from app.exc import IncorrectInput, InvalidPlay, OutOfOrder
from app.player import Player
from app.room import Room


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
            except OutOfOrder:
                print("Please interact when it's your turn!")
            else:
                move_result = True

        if room.board.check_victory(active_player):
            room.board.print_board()
            break
        if room.board.check_stalemate():
            print("It's a stalemate!")
            room.board.print_board()
            break


if __name__ == "__main__":
    player1 = Player(420, "Andrew")
    player2 = Player(69, "Ashley")

    room = Room(1, player1)
    room.second_player = player2

    if room.isFull():
        room.assign_symbols()
        main(room)
    else:
        print("Cannot start a game without a second player!")
