from typing import Annotated
import uuid
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.db import get_session
from app.models.player import Player


router = APIRouter(prefix="/players")


@router.post("", response_model=uuid.UUID, status_code=status.HTTP_201_CREATED)
async def create_player(
    *, session: Session = Depends(get_session), name: Annotated[str, Body(embed=True)]
) -> uuid.UUID:
    player_id = uuid.uuid4()
    player = Player(player_id=player_id, name=name)
    session.add(player)
    session.commit()
    return player.get_player_id
