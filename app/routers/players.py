from fastapi import APIRouter, HTTPException
from typing import List
from app.models.player import Player

router = APIRouter()


players_db = []

@router.post("/jugadores/", response_model=Player, status_code=201)
def create_player(player: Player):
   
    players_db.append(player)
    return player

@router.get("/jugadores/", response_model=List[Player])
def get_players():
  
    return players_db

@router.get("/jugadores/{player_name}", response_model=Player)
def get_player_by_name(player_name: str):
  
    for player in players_db:
        if player.name == player_name:
            return player
    raise HTTPException(status_code=404, detail="Jugador no encontrado")
