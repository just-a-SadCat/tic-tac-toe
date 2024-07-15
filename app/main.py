from typing import Annotated
import uuid
from fastapi import Body, FastAPI, HTTPException, Path
from pydantic import BaseModel
from starlette import status

from app.exc import IncorrectInput, InvalidPlay, OutOfOrder, RoomFull, RoomNotFull
from app.player import Player
from app.room import Room

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
    col: int
    row: int


@app.post("/rooms", response_model=uuid.UUID, status_code=status.HTTP_201_CREATED)
async def create_room(player_id: Annotated[int, Body(embed=True)]) -> uuid.UUID:
    room_id = uuid.uuid4()
    room = Room(room_id, players[player_id, temp_player])
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
async def display_players(room_id: Annotated[uuid.UUID, Path()]) -> list[Player]:
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
    "/rooms/{room_id}/board", response_model=str, status_code=status.HTTP_204_NO_CONTENT
)
async def make_play(
    room_id: Annotated[uuid.UUID, Path()], input: Annotated[PlayInput, Body(embed=True)]
) -> str:
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
    response = (
        f"Player {player.name} made a play at row {input.row}, column {input.col}."
    )
    return response


@app.get("/rooms/{room_id}/board", response_model=bool, status_code=status.HTTP_200_OK)
async def check_board_state(
    room_id: Annotated[uuid.UUID, Path()],
    player_id: Annotated[uuid.UUID, Body(embed=True)],
) -> bool:
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
    return room.check_board_state()
