from app.exc import IncorrectInput, InvalidPlay, OutOfOrder
from app.player import Player
from app.room import Room


def main(room: Room) -> None:
    while True:
        active_player = room.active_player
        print(f"Current player: {active_player.name}")

        move_result = False
        while move_result is False:
            room.print_board()
            try:
                try:
                    print("Select row first, then column (Pick from 1 to 3): ")
                    row = int(input()) - 1
                    col = int(input()) - 1
                except ValueError:
                    raise IncorrectInput("The input was not a number")
                room.make_play(active_player, row, col)

            except IncorrectInput:
                print("Your input was incorrect, try again!")
            except InvalidPlay:
                print("That play is impossible, try again!")
            except OutOfOrder:
                print("Please interact when it's your turn!")
            else:
                move_result = True
        if room.check_board_state(active_player):
            break


if __name__ == "__main__":
    player1 = Player(420, "Andrew")
    player2 = Player(69, "Ashley")

    room = Room(1, player1)
    room.add_player(player2)

    if room.is_full():

        main(room)
    else:
        print("Cannot start a game without a second player!")
