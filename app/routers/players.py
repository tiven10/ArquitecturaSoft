from fastapi import APIRouter, HTTPException
from typing import List
from app.models.player import Player, Role

router = APIRouter()

# Base de datos en memoria para jugadores
players_db = {}

@router.post("/players/", response_model=Player, status_code=201)
def create_player(player_data: Player):
    """
    Crea un nuevo jugador con estadísticas detalladas basadas en su rol.
    """
    if player_data.name in players_db:
        raise HTTPException(status_code=400, detail="Jugador Ya existe")

    # Crear una instancia del jugador para poder modificarla
    player = player_data.copy()

    # Lógica de asignación de estadísticas por rol
    xp_base = 100
    player.xp_to_next_level = xp_base

    if player.role == Role.GUERRERO:
        player.hp = player.max_hp = 120
        player.mp = player.max_mp = 10
        player.attack = 15
        player.defense = 10
    elif player.role == Role.MAGO:
        player.hp = player.max_hp = 90
        player.mp = player.max_mp = 30
        player.attack = 5
        player.defense = 5
        player.magic_power = 20
    elif player.role == Role.ARQUERO:
        player.hp = player.max_hp = 100
        player.mp = player.max_mp = 15
        player.attack = 12
        player.defense = 7
    elif player.role == Role.ESCUDERO:
        player.hp = player.max_hp = 150
        player.mp = player.max_mp = 5
        player.attack = 8
        player.defense = 15
    elif player.role == Role.ASESINO:
        player.hp = player.max_hp = 90
        player.mp = player.max_mp = 20
        player.attack = 18
        player.defense = 5
    elif player.role == Role.PALADIN:
        player.hp = player.max_hp = 130
        player.mp = player.max_mp = 20
        player.attack = 12
        player.defense = 12
        player.magic_power = 5

    players_db[player.name] = player
    return player

@router.get("/players/", response_model=List[Player])
def get_players():
    """
    Retorna la lista de todos los jugadores.
    """
    return list(players_db.values())

@router.get("/players/{player_name}", response_model=Player)
def get_player_by_name(player_name: str):
    """
    Busca y retorna un jugador por su nombre.
    """
    player = players_db.get(player_name)
    if not player:
        raise HTTPException(status_code=404, detail="Jugador No Encontrado")
    return player

@router.put("/players/{player_name}", response_model=Player)
def update_player(player_name: str, updated_player: Player):
    """
    Actualiza los datos de un jugador existente.
    """
    if player_name not in players_db:
        raise HTTPException(status_code=404, detail="Jugador No Encontrado")

    players_db[player_name] = updated_player
    return updated_player

@router.delete("/players/{player_name}", response_model=dict)
def delete_player(player_name: str):
    """
    Elimina un jugador de la base de datos.
    """
    if player_name not in players_db:
        raise HTTPException(status_code=404, detail="Jugador Encontrado")

    del players_db[player_name]
    return {"message": "Jugador Eliminado"}
