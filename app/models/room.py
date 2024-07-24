from enum import Enum
from typing import List, TYPE_CHECKING
import uuid
from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.board import Board

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

    active_player_state: Mapped[ActiveState] = mapped_column(default=ActiveState.FIRST)

    board_JSON: Mapped[str] = mapped_column(
        JSON(none_as_null=False),
        default='[[" ", " ", " "],[" ", " ", " "], [" ", " ", " "]]',
    )

    @property
    def active_player(self) -> "Player":
        if self.active_player_state is ActiveState.FIRST:
            return self.first_player
        else:
            return self.second_player

    @property
    def board(self) -> Board:
        return Board(self.board_JSON)

    @property
    def update_board(self, update: str):
        self.board_JSON = update
