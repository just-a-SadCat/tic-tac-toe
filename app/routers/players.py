from typing import Annotated
import uuid
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.db import get_session
from app.models.player import Player


router = APIRouter()


@router.post("/players", response_model=uuid.UUID, status_code=status.HTTP_201_CREATED)
async def create_player(
    *, session: Session = Depends(get_session), name: Annotated[str, Body(embed=True)]
) -> uuid.UUID:
    player_id = uuid.uuid4()
    player = Player(player_id, name)
    session.add(player)
    return player.player_id
