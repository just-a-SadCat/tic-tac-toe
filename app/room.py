import uuid
from app.board import Board, BoardStates
from app.exc import OutOfOrder, RoomFull, RoomNotFull
from app.player import Player, Symbols


class Room:
    def __init__(self, room_id: uuid.UUID, first_player: Player):
        self._room_id = room_id
        self._first_player = first_player
        self._second_player: Player | None = None
        self._board = Board()
        self._active_player = first_player

    @property
    def room_id(self) -> int:
        return self._room_id

    @property
    def first_player(self) -> Player:
        return self._first_player

    @property
    def second_player(self) -> Player:
        if self._second_player is None:
            raise LookupError("A player wasn't assigned!")
        return self._second_player

    @property
    def active_player(self) -> Player:
        return self._active_player

    def print_board(self) -> None:
        self._board.print_board()

    def _assign_symbols(self) -> None:
        self._first_player.symbol = Symbols.X.value
        self._second_player.symbol = Symbols.O.value

    def add_player(self, player: Player) -> None:
        if self._second_player is None:
            self._second_player = player
            self._assign_symbols()
        else:
            raise RoomFull("The room is already full!")

    def is_full(self) -> None:
        if self._second_player is None:
            raise RoomNotFull("The room is not full yet!")

    def _switch_players(self) -> None:
        if self._active_player is self._first_player:
            self._active_player = self._second_player
            return
        self._active_player = self._first_player

    def make_play(self, player: Player, row: int, col: int) -> None:
        if player is self._active_player:
            self._board.edit_field(player.symbol, row, col)
            self._switch_players()
        else:
            raise OutOfOrder(
                "A player tried interacting while not being the active player"
            )

    def check_board_state(self, active_player: Player) -> BoardStates:
        if self._board.check_victory(active_player):
            self.print_board()
            return BoardStates.WIN
        if self._board.check_stalemate():
            print("It's a stalemate!")
            self.print_board()
            return BoardStates.STALEMATE
        return BoardStates.NO_WIN

    def compare_board_states(self):
        stateFirst: BoardStates = self.check_board_state(self._first_player)
        stateSecond: BoardStates = self.check_board_state(self._second_player)

        # match stateFirst:

        if stateFirst is BoardStates.STALEMATE or stateSecond is BoardStates.STALEMATE:
            ...
        elif stateFirst is stateSecond:
            ...
        elif stateFirst is BoardStates.WIN:
            ...
        else:
            ...
