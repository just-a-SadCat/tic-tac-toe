from typing import Annotated
import uuid
from fastapi import Body, FastAPI, HTTPException, Path
from pydantic import BaseModel
from starlette import status

from app.board import BoardStates
from app.exc import (
    IncorrectInput,
    InvalidPlay,
    OutOfOrder,
    RoomFull,
    RoomNotFull,
    BoardStatesNotFound,
)
from app.player import Player
from app.room import NextTurn, Room, WinnerStates

app = FastAPI()

rooms: dict[uuid.UUID, Room] = dict()

players: dict[uuid.UUID, Player] = dict()
temp_uuid = uuid.uuid4()
temp_player = Player(temp_uuid, "Maks")
players[temp_uuid] = temp_player


class PlayerSchema(BaseModel):
    player_id: uuid.UUID
    name: str
    symbol: str


class PlayInput(BaseModel):
    player_id: uuid.UUID
    row: int
    col: int


@app.post("/rooms", response_model=uuid.UUID, status_code=status.HTTP_201_CREATED)
async def create_room(player_id: Annotated[int, Body(embed=True)]) -> uuid.UUID:
    room_id = uuid.uuid4()
    room = Room(room_id, players[player_id])
    rooms[room_id] = room
    return room.room_id()


@app.put("/rooms/{room_id}/players/add", status_code=status.HTTP_204_NO_CONTENT)
async def add_player(
    room_id: Annotated[uuid.UUID, Path()],
    player_id: Annotated[uuid.UUID, Body(embed=True)],
) -> None:
    try:
        room = rooms[room_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            details="Room with given id not found",
        )

    try:
        player = players[player_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            details="Player with given id not found",
        )

    try:
        room.add_player(player)
    except RoomFull:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            details="Room cannot have more than two players",
        )


@app.get(
    "/rooms/{room_id}/players",
    response_model=list[PlayerSchema],
    status_code=status.HTTP_200_OK,
)
async def get_players(room_id: Annotated[uuid.UUID, Path()]) -> list[Player]:
    try:
        room = rooms[room_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            details="Room with given id not found",
        )

    try:
        room.is_full()
    except RoomNotFull:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            details="Room is required to have two players",
        )

    response: list[Player] = [room.first_player, room.second_player]
    return response


@app.put(
    "/rooms/{room_id}/board",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def make_play(
    room_id: Annotated[uuid.UUID, Path()], input: Annotated[PlayInput, Body()]
) -> None:
    try:
        room = rooms[room_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            details="Room with given id not found",
        )

    try:
        player = players[input.player_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            details="Player with given id not found",
        )
    try:
        room.make_play(player, input.row, input.col)
    except OutOfOrder:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            details="Player tried acting outside their turn",
        )
    except IncorrectInput:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            details="Player's input was incorrect",
        )
    except InvalidPlay:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            details="Player attempted an impossible play",
        )


@app.get(
    "/rooms/{room_id}/board",
    response_model=uuid.UUID | NextTurn,
    status_code=status.HTTP_200_OK,
)
async def decide_result(room_id: Annotated[uuid.UUID, Path()]) -> uuid.UUID | NextTurn:
    try:
        room = rooms[room_id]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            details="Room with given id not found",
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
            details="Failed to find the board states",
        )
