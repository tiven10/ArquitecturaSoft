from fastapi import APIRouter
from app.models.player import Player

router = APIRouter()

@router.post("/players/", response_model=Player)
def create_player(player: Player):
    return player
