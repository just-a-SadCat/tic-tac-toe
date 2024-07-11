from typing import Annotated
import uuid
from fastapi import Body, FastAPI
from pydantic import BaseModel

from app.player import Player
from app.room import Room

app = FastAPI()
room = None
player = Player(0, "Maks")


@app.post("/rooms", response_model=uuid.UUID)
async def create_room(player_id: Annotated[int, Body(embed=True)]) -> uuid.UUID:
    global room
    room = Room(uuid.uuid4(), player)
    return room.room_id()


@app.get("/rooms/players", response_model=Player)
async def add_player(player_id: Annotated[int, Body(embed=True)]) -> Player:
    room.add_player(player)
    print(f"Dodano gracza {player.name}")
