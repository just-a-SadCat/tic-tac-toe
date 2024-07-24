from fastapi import FastAPI

from app.routers import players, rooms

app = FastAPI()
app.include_router(players.router)
app.include_router(rooms.router)
