from fastapi import FastAPI
from app.routers import players

app = FastAPI()

app.include_router(players.router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido A LostCastle :D"}
