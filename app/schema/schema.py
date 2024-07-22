import uuid
from pydantic import BaseModel


class PlayerSchema(BaseModel):
    player_id: uuid.UUID
    name: str
    symbol: str


class PlayInput(BaseModel):
    player_id: uuid.UUID
    row: int
    col: int
