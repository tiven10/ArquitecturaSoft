from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from enum import Enum
import random

from app.routers.players import players_db, Player

router = APIRouter()

# --- Modelos de Datos para el Combate ---
class AttackType(str, Enum):
    FISICO = "Ataque Físico"
    MAGICO = "Hechizo de Fuego"

class CombatRequest(BaseModel):
    player1_name: str
    player2_name: str

class TurnRequest(BaseModel):
    combat_id: str
    attacker_name: str
    attack_type: AttackType

# --- "Base de Datos" para Sesiones de Combate ---
combat_sessions = {}

# --- Lógica de Combate ---

def level_up(player: Player):
    player.level += 1
    player.xp = 0 # Reiniciar XP o llevar el excedente
    player.xp_to_next_level = int(player.xp_to_next_level * 1.5)
    
    # Mejorar estadísticas
    player.max_hp += 10
    player.max_mp += 5
    player.attack += 2
    player.defense += 1
    player.magic_power += 2
    
    # Restaurar vida y maná
    player.hp = player.max_hp
    player.mp = player.max_mp
    return f"{player.name} ha subido al nivel {player.level}!"

@router.post("/combat/start")
def start_combat(request: CombatRequest):
    """
    Inicia una nueva sesión de combate entre dos jugadores.
    """
    if request.player1_name not in players_db or request.player2_name not in players_db:
        raise HTTPException(status_code=404, detail="Uno o ambos jugadores no fueron encontrados.")

    combat_id = f"combat_{len(combat_sessions) + 1}"
    turn_order = [request.player1_name, request.player2_name]
    random.shuffle(turn_order)

    combat_sessions[combat_id] = {
        "players": [request.player1_name, request.player2_name],
        "turn": turn_order[0],
        "log": [f"La batalla entre {request.player1_name} y {request.player2_name} ha comenzado!"]
    }

    combat_sessions[combat_id]["log"].append(f"Es el turno de {turn_order[0]}.")

    return {"combat_id": combat_id, "message": combat_sessions[combat_id]["log"][-2:]}

@router.post("/combat/turn")
def take_turn(request: TurnRequest):
    """
    Ejecuta un turno en una sesión de combate activa.
    """
    session = combat_sessions.get(request.combat_id)
    if not session:
        raise HTTPException(status_code=404, detail="Sesión de combate no encontrada.")

    if request.attacker_name != session["turn"]:
        raise HTTPException(status_code=400, detail=f"No es el turno de {request.attacker_name}.")

    attacker = players_db[request.attacker_name]
    defender_name = next(p for p in session["players"] if p != request.attacker_name)
    defender = players_db[defender_name]

    turn_log = []
    damage = 0
    
    # Lógica de Ataque
    if random.random() < 0.1: # 10% de probabilidad de fallar
        turn_log.append(f"¡{attacker.name} intenta atacar a {defender.name} pero falla!")
    else:
        if request.attack_type == AttackType.FISICO:
            damage = max(1, attacker.attack - defender.defense)
            turn_log.append(f"{attacker.name} usa {AttackType.FISICO} contra {defender.name}.")
        
        elif request.attack_type == AttackType.MAGICO:
            if attacker.mp >= 10:
                attacker.mp -= 10
                damage = max(1, attacker.magic_power)
                turn_log.append(f"{attacker.name} lanza {AttackType.MAGICO} sobre {defender.name}. Costó 10 MP.")
            else:
                damage = 0
                turn_log.append(f"{attacker.name} intenta lanzar un hechizo ¡pero no tiene suficiente maná!")

        # Golpe Crítico
        if random.random() < 0.2: # 20% de probabilidad de crítico
            damage = int(damage * 1.5)
            turn_log.append("¡GOLPE CRÍTICO!")

    defender.hp = max(0, defender.hp - damage)
    turn_log.append(f"{defender.name} recibe {damage} puntos de daño. Vida restante: {defender.hp} HP.")

    # Comprobar si el combate terminó
    if defender.hp == 0:
        turn_log.append(f"¡{defender.name} ha sido derrotado!")
        turn_log.append(f"¡{attacker.name} es el ganador!")

        # Otorgar XP
        xp_gain = defender.level * 10
        attacker.xp += xp_gain
        turn_log.append(f"{attacker.name} ha ganado {xp_gain} puntos de experiencia.")

        # Comprobar si sube de nivel
        if attacker.xp >= attacker.xp_to_next_level:
            level_up_message = level_up(attacker)
            turn_log.append(level_up_message)
        
        del combat_sessions[request.combat_id] # Finalizar sesión

    else:
        # Pasar el turno
        session["turn"] = defender_name
        turn_log.append(f"Ahora es el turno de {defender_name}.")

    session["log"].extend(turn_log)
    return {"log": turn_log}
