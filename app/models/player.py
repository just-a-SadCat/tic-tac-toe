from enum import Enum
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.room import Room


class Symbols(str, Enum):
    X = "X"
    O = "O"


class Player(Base):
    __tablename__ = "players"
    player_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str]
    symbol: Mapped[str | None] = mapped_column(default=None)

    rooms: Mapped[List["Room"]] = relationship(
        "Room",
        primaryjoin="_or(Player.player_id == Room.first_player_id, Player.player_id == Room.second_player_id)",
    )
