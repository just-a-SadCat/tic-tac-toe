from typing import Annotated
import uuid
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status

from app.db import get_session
from app.exc import (
    BoardStatesNotFound,
    DuplicatePlayer,
    IncorrectInput,
    InvalidPlay,
    OutOfOrder,
    RoomFull,
    RoomNotFull,
)
from app.models.player import Player
from app.models.room import NextTurn, Room, WinnerStates
from app.schema import PlayInput, PlayerSchema

router = APIRouter(prefix="/rooms")


@router.post("", response_model=uuid.UUID, status_code=status.HTTP_201_CREATED)
async def create_room(
    *,
    session: Session = Depends(get_session),
    player_id: Annotated[uuid.UUID, Body(embed=True)],
) -> uuid.UUID:
    room_id = uuid.uuid4()
    result = session.execute(select(Player).where(Player.player_id == player_id))
    player = result.scalar()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player with given id not found",
        )
    room = Room(room_id=room_id, first_player_id=player.get_player_id)
    session.add(room)
    session.commit()
    return room.get_room_id


@router.put("/{room_id}/players/add", status_code=status.HTTP_204_NO_CONTENT)
async def add_player(
    *,
    session: Session = Depends(get_session),
    room_id: Annotated[uuid.UUID, Path()],
    player_id: Annotated[uuid.UUID, Body(embed=True)],
) -> None:
    result = session.execute(select(Room).where(Room.room_id == room_id))
    room = result.scalar()
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room with given id not found",
        )

    result = session.execute(select(Player).where(Player.player_id == player_id))
    player = result.scalar()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player with given id not found",
        )

    try:
        room.add_player(player)
    except RoomFull:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Room cannot have more than two players",
        )
    except DuplicatePlayer:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Room cannot have multiple instances of the same player",
        )
    session.commit()


@router.get(
    "/{room_id}/players",
    response_model=list[PlayerSchema],
    status_code=status.HTTP_200_OK,
)
async def get_players(
    *, session: Session = Depends(get_session), room_id: Annotated[uuid.UUID, Path()]
) -> list[Player]:
    result = session.execute(select(Room).where(Room.room_id == room_id))
    room = result.scalar()
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room with given id not found",
        )

    try:
        room.is_full()
    except RoomNotFull:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room is required to have two players",
        )

    response: list[Player] = [room.first_player, room.second_player]
    return response


@router.put(
    "/{room_id}/board",
    response_model=list[list[str]],
    status_code=status.HTTP_200_OK,
)
async def make_play(
    *,
    session: Session = Depends(get_session),
    room_id: Annotated[uuid.UUID, Path()],
    input: Annotated[PlayInput, Body()],
) -> list[list[str]]:
    result = session.execute(select(Room).where(Room.room_id == room_id))
    room = result.scalar()
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room with given id not found",
        )

    result = session.execute(select(Player).where(Player.player_id == input.player_id))
    player = result.scalar()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player with given id not found",
        )
    try:
        room.make_play(player, input.row, input.col)
    except OutOfOrder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Player tried acting outside their turn",
        )
    except IncorrectInput:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Player's input was incorrect",
        )
    except InvalidPlay:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player attempted an impossible play",
        )
    session.commit()
    return room.print_board()


@router.get(
    "/{room_id}/board",
    response_model=uuid.UUID | NextTurn,
    status_code=status.HTTP_200_OK,
)
async def decide_result(
    *, session: Session = Depends(get_session), room_id: Annotated[uuid.UUID, Path()]
) -> uuid.UUID | NextTurn:
    """Function returns a player id if any player is declared winner.
    In case of a stalemate or a turn not ending the game, returns a NextTurn specifying
    whether to continue the game or not"""
    result = session.execute(select(Room).where(Room.room_id == room_id))
    room = result.scalar()
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room with given id not found",
        )
    result = room.compare_board_states()
    try:
        match result:
            case WinnerStates.NONE:
                return NextTurn.YES
            case WinnerStates.FIRST:
                return room.first_player.get_player_id
            case WinnerStates.SECOND:
                return room.second_player.get_player_id
            case WinnerStates.STALEMATE:
                return NextTurn.NO
    except BoardStatesNotFound:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find the board states",
        )
