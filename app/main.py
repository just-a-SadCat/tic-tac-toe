from typing import Annotated
import uuid
from fastapi import Body, FastAPI
from pydantic import BaseModel

from app.player import Player
from app.room import Room

app = FastAPI()
room = None
player = Player(0, "Maks")
active_player = None


@app.post("/rooms", response_model=uuid.UUID)
async def create_room(player_id: Annotated[int, Body(embed=True)]) -> uuid.UUID:
    global room
    room = Room(uuid.uuid4(), player)
    return room.room_id()


@app.post("/rooms/players", response_model=Player)
async def add_player(player_id: Annotated[int, Body(embed=True)]) -> Player:
    room.add_player(player)
    print(f"Added player: {player.name}")
    return player.player_id()


@app.get("/rooms/players", response_model=bool)
async def start_game():
    return room.is_full()


@app.post("/rooms/board", response_model=None)
async def start_turn():
    global active_player
    active_player = room.active_player
    room.print_board()


@app.post("/rooms/board", response_model=None)
async def make_play(row: int, col: int):
    print(f"Current player: {active_player.name}")
    room.make_play(active_player, row, col)


@app.get("/rooms/board", response_model=bool)
async def check_board_state():
    return room.check_board_state(active_player)
