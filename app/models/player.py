from enum import Enum
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
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
    _symbol: Mapped[str | None] = mapped_column("symbol", default=None)

    _player_id = synonym("player_id")

    rooms: Mapped[List["Room"]] = relationship(
        "Room",
        primaryjoin="or_(Player.player_id == Room.first_player_id, Player.player_id == Room.second_player_id)",
    )

    @property
    def get_player_id(self) -> uuid.UUID:
        return self._player_id

    @property
    def symbol(self) -> str:
        if self._symbol is None:
            raise LookupError("A symbol wasn't assinged to a player!")
        return self._symbol

    @symbol.setter
    def set_symbol(self, symbol: str) -> None:
        self._symbol = symbol
