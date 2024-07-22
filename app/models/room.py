from enum import Enum
from typing import List
import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.board import Board
from models.base import Base


class ActiveState(str, Enum):
    FIRST = "FIRST"
    SECOND = "SECOND"


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

    board: Mapped[Board]  # TODO

    @property
    def active_player(self):
        if self.active_player_state is ActiveState.FIRST:
            return self.first_player
        else:
            return self.second_player


class Player(Base):
    __tablename__ = "players"
    player_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str]
    symbol: Mapped[str | None] = mapped_column(default=None)

    rooms: Mapped[List[Room]] = relationship(
        "Room",
        primaryjoin="Player.player_id == Room.first_player_id OR Player.player_id == Room.second_player_id",
    )
