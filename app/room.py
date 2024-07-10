from app.board import Board
from app.player import Player


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
