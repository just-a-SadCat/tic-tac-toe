from enum import Enum
import json
from typing import List, TYPE_CHECKING
import uuid
from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
from app.board import Board, BoardStates
from app.exc import (
    BoardStatesNotFound,
    DuplicatePlayer,
    OutOfOrder,
    RoomFull,
    RoomNotFull,
)
from app.models.player import Symbols

if TYPE_CHECKING:
    from app.models.player import Player
from app.models.base import Base


class ActiveState(str, Enum):
    FIRST = "FIRST"
    SECOND = "SECOND"


class WinnerStates(str, Enum):
    NONE = "NONE"
    FIRST = "FIRST"
    SECOND = "SECOND"
    STALEMATE = "STALEMATE"


class NextTurn(str, Enum):
    NO = "NO"
    YES = "YES"


class Room(Base):
    __tablename__ = "rooms"

    room_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

    first_player_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.player_id"))
    second_player_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("players.player_id"), default=None
    )

    first_player: Mapped["Player"] = relationship(
        "Player", foreign_keys=[first_player_id]
    )
    second_player: Mapped["Player | None"] = relationship(
        "Player", foreign_keys=[second_player_id]
    )

    _room_id = synonym("room_id")
    _first_player = synonym("first_player")
    _second_player = synonym("second_player")

    active_player_state: Mapped[ActiveState] = mapped_column(default=ActiveState.FIRST)

    board_json: Mapped[str] = mapped_column(
        JSON(none_as_null=False),
        default='[[" ", " ", " "],[" ", " ", " "], [" ", " ", " "]]',
    )

    @property
    def active_player(self) -> "Player":
        if self.active_player_state is ActiveState.FIRST:
            return self.first_player
        else:
            return self.second_player

    def copy_board(self) -> Board:
        return Board(self.board_json)

    def update_board(self, fields: list[list[str]]) -> None:
        self.board_json = json.dumps(fields)

    @property
    def get_room_id(self) -> int:
        return self._room_id

    @property
    def get_first_player(self) -> "Player":
        return self._first_player

    @property
    def get_second_player(self) -> "Player":
        if self._second_player is None:
            raise LookupError("A player wasn't assigned!")
        return self._second_player

    def print_board(self) -> list[list[str]]:
        board = self.copy_board()
        return board.fields

    def _assign_symbols(self) -> None:
        self._first_player.set_symbol = Symbols.X.value
        self._second_player.set_symbol = Symbols.O.value

    def add_player(self, player: "Player") -> None:
        if self._second_player is None:
            if not player is self._first_player:
                self._second_player = player
                self._assign_symbols()
            else:
                raise DuplicatePlayer("Cannot add a player already inside!")
        else:
            raise RoomFull("The room is already full!")

    def is_full(self) -> None:
        if self._second_player is None:
            raise RoomNotFull("The room is not full yet!")

    def _switch_players(self) -> None:
        if self.active_player is self._first_player:
            self.active_player_state = ActiveState.SECOND
            return
        self.active_player_state = ActiveState.FIRST

    def make_play(self, player: "Player", row: int, col: int) -> None:
        board = self.copy_board()
        if player is self.active_player:
            fields = board.edit_field(player.symbol, row, col)
            if fields is not None:
                self.update_board(fields)
            self._switch_players()
        else:
            raise OutOfOrder(
                "A player tried interacting while not being the active player"
            )

    def _check_board_state(self, active_player: "Player") -> BoardStates:
        board = self.copy_board()
        if board.check_victory(active_player):
            return BoardStates.WIN
        if board.check_stalemate():
            return BoardStates.STALEMATE
        return BoardStates.NO_WIN

    def compare_board_states(self) -> WinnerStates:
        stateFirst: BoardStates = self._check_board_state(self._first_player)
        stateSecond: BoardStates = self._check_board_state(self._second_player)

        match stateFirst:
            case BoardStates.STALEMATE:
                return WinnerStates.STALEMATE
            case BoardStates.WIN:
                return WinnerStates.FIRST
            case BoardStates.NO_WIN:
                if stateSecond is BoardStates.WIN:
                    return WinnerStates.SECOND
                return WinnerStates.NONE
            case _:
                raise BoardStatesNotFound("Couldn't find a boardstate, somehow")
