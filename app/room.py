import uuid
from app.board import Board
from app.exc import OutOfOrder, RoomFull
from app.player import Player, Symbols


class Room:
    def __init__(self, room_id: uuid, first_player: Player):
        self._room_id = room_id
        self._first_player = first_player
        self._second_player = None
        self.board = Board()
        self._active_player = first_player

    @property
    def room_id(self):
        return self._room_id

    @property
    def second_player(self):
        if self._second_player is None:
            raise LookupError("A player wasn't assigned!")
        return self._second_player

    @second_player.setter
    def second_player(self, second_player: Player):
        self._second_player = second_player

    @property
    def active_player(self):
        return self._active_player

    def assign_symbols(self) -> None:
        self._first_player.symbol = Symbols.X.value
        self.second_player.symbol = Symbols.O.value

    def swap_players(self, previous_player: Player) -> None:
        if previous_player is self._first_player:
            self._active_player = self.second_player
            return
        self._active_player = self._first_player

    def make_play(self, player: Player) -> None:
        if player is self._active_player:
            self.board.edit_field(player.symbol)
            self.swap_players(player)
        else:
            raise OutOfOrder(
                "A player tried interacting while not being the active player"
            )

    def add_player(self, player: Player) -> None:
        if self._second_player is None:
            self.set_second_player(player)
        else:
            raise RoomFull("The room is already full!")

    def isFull(self):
        if self._second_player is None:
            return False
        return True
