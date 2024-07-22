from typing import Annotated
import uuid
from fastapi import Body, Depends, FastAPI, HTTPException, Path
from pydantic import BaseModel
from starlette import status
from sqlalchemy.orm import Session

from app.board import BoardStates
from app.db import get_session
from app.exc import (
    DuplicatePlayer,
    IncorrectInput,
    InvalidPlay,
    OutOfOrder,
    RoomFull,
    RoomNotFull,
    BoardStatesNotFound,
)
from app.player import Player
from app.room import NextTurn, Room, WinnerStates
from app.schema.schema import PlayInput, PlayerSchema

app = FastAPI()

rooms = dict[uuid.UUID, Room]()

players = dict[uuid.UUID, Player]()
temp_uuid = uuid.uuid4()
temp_player = Player(temp_uuid, "Maks")
players[temp_uuid] = temp_player


@app.post("/players", response_model=uuid.UUID, status_code=status.HTTP_201_CREATED)
async def create_player(
    *, session: Session = Depends(get_session), name: Annotated[str, Body(embed=True)]
) -> uuid.UUID:
    player_id = uuid.uuid4()
    player = Player(player_id, name)
    players[player_id] = player
    session.add(player)
    return player.player_id


@app.post("/rooms", response_model=uuid.UUID, status_code=status.HTTP_201_CREATED)
async def create_room(
    *,
    session: Session = Depends(get_session),
    player_id: Annotated[uuid.UUID, Body(embed=True)],
) -> uuid.UUID:
    room_id = uuid.uuid4()
    try:
        player = players[player_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player with given id not found",
        )
    room = Room(room_id, player)
    rooms[room_id] = room
    session.add(room)
    return room.room_id


@app.put("/rooms/{room_id}/players/add", status_code=status.HTTP_204_NO_CONTENT)
async def add_player(
    *,
    session: Session = Depends(get_session),
    room_id: Annotated[uuid.UUID, Path()],
    player_id: Annotated[uuid.UUID, Body(embed=True)],
) -> None:
    try:
        room = rooms[room_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room with given id not found",
        )

    try:
        player = players[player_id]
    except KeyError:
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


@app.get(
    "/rooms/{room_id}/players",
    response_model=list[PlayerSchema],
    status_code=status.HTTP_200_OK,
)
async def get_players(
    *, session: Session = Depends(get_session), room_id: Annotated[uuid.UUID, Path()]
) -> list[Player]:
    try:
        room = rooms[room_id]
    except KeyError:
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


@app.put(
    "/rooms/{room_id}/board",
    response_model=list[list[str]],
    status_code=status.HTTP_200_OK,
)
async def make_play(
    *,
    session: Session = Depends(get_session),
    room_id: Annotated[uuid.UUID, Path()],
    input: Annotated[PlayInput, Body()],
) -> list[list[str]]:
    try:
        room = rooms[room_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room with given id not found",
        )

    try:
        player = players[input.player_id]
    except KeyError:
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
    return room.print_board()


@app.get(
    "/rooms/{room_id}/board",
    response_model=uuid.UUID | NextTurn,
    status_code=status.HTTP_200_OK,
)
async def decide_result(
    *, session: Session = Depends(get_session), room_id: Annotated[uuid.UUID, Path()]
) -> uuid.UUID | NextTurn:
    """Function returns a player id if any player is declared winner.
    In case of a stalemate or a turn not ending the game, returns a NextTurn specifying
    whether to continue the game or not"""
    try:
        room = rooms[room_id]
    except KeyError:
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
                return room.first_player.player_id
            case WinnerStates.SECOND:
                return room.second_player.player_id
            case WinnerStates.STALEMATE:
                return NextTurn.NO
    except BoardStatesNotFound:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find the board states",
        )
