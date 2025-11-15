from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from enum import Enum
import random

from app.routers.players import players_db, Player
from app.models.player import Role

router = APIRouter()

# --- Base de Datos de Ataques ---
ATTACKS_BY_ROLE = {
    Role.GUERRERO: [
        {"name": "Corte Transversal", "type": "FISICO", "power": 1.1, "cost": 0},
        {"name": "Embestida", "type": "FISICO", "power": 0.9, "cost": 0},
        {"name": "Golpe Potente", "type": "FISICO", "power": 1.4, "cost": 5},
        {"name": "Fisura", "type": "FISICO", "power": 1.2, "cost": 3},
    ],
    Role.MAGO: [
        {"name": "Bola de Fuego", "type": "MAGICO", "power": 1.2, "cost": 8},
        {"name": "Descarga de Escarcha", "type": "MAGICO", "power": 1.0, "cost": 5},
        {"name": "Explosión Arcana", "type": "MAGICO", "power": 1.8, "cost": 15},
        {"name": "Misil Mágico", "type": "MAGICO", "power": 0.9, "cost": 3},
    ],
    Role.ARQUERO: [
        {"name": "Disparo Preciso", "type": "FISICO", "power": 1.2, "cost": 3},
        {"name": "Flecha de Hielo", "type": "MAGICO", "power": 0.8, "cost": 5},
        {"name": "Lluvia de Flechas", "type": "FISICO", "power": 0.7, "cost": 5},
        {"name": "Disparo Mortal", "type": "FISICO", "power": 2.0, "cost": 15},
    ],
    Role.PALADIN: [
        {"name": "Golpe Justiciero", "type": "FISICO", "power": 1.1, "cost": 0},
        {"name": "Sentencia", "type": "MAGICO", "power": 1.3, "cost": 8},
        {"name": "Luz Sagrada", "type": "MAGICO", "power": 1.6, "cost": 12},
        {"name": "Martillo del Honrado", "type": "FISICO", "power": 1.4, "cost": 10},
    ],
    Role.ASESINO: [
        {"name": "Puñalada Rápida", "type": "FISICO", "power": 1.1, "cost": 2},
        {"name": "Ataque Sombrío", "type": "FISICO", "power": 1.3, "cost": 5},
        {"name": "Veneno Debilitante", "type": "MAGICO", "power": 0.7, "cost": 8},
        {"name": "Eviscerar", "type": "FISICO", "power": 1.9, "cost": 15},
    ],
    Role.ESCUDERO: [
        {"name": "Golpe de Escudo", "type": "FISICO", "power": 1.0, "cost": 0},
        {"name": "Muro de Hierro", "type": "DEFENSIVO", "power": 1.5, "cost": 8},
        {"name": "Provocar", "type": "EFECTO", "power": 0, "cost": 5},
        {"name": "Embate", "type": "FISICO", "power": 1.3, "cost": 6},
    ]
}

# --- Modelos de Datos para el Combate ---
class CombatRequest(BaseModel):
    player1_name: str
    player2_name: str

class TurnRequest(BaseModel):
    combat_id: str
    attacker_name: str
    attack_name: str

# --- "Base de Datos" para Sesiones de Combate ---
combat_sessions = {}

# --- Lógica de Combate ---

def level_up(player: Player):
    player.level += 1
    player.xp = 0
    player.xp_to_next_level = int(player.xp_to_next_level * 1.5)
    player.max_hp += 10
    player.max_mp += 5
    player.attack += 2
    player.defense += 1
    player.magic_power += 2
    player.hp = player.max_hp
    player.mp = player.max_mp
    return f"{player.name} ha subido al nivel {player.level}!"

@router.get("/combat/attacks/{player_name}")
def get_player_attacks(player_name: str):
    """Retorna los ataques disponibles para un jugador basado en su rol."""
    if player_name not in players_db:
        raise HTTPException(status_code=404, detail="Jugador no encontrado.")
    player = players_db[player_name]
    return ATTACKS_BY_ROLE.get(player.role, [])

@router.post("/combat/start")
def start_combat(request: CombatRequest):
    """Inicia una nueva sesión de combate entre dos jugadores."""
    if request.player1_name not in players_db or request.player2_name not in players_db:
        raise HTTPException(status_code=404, detail="Uno o ambos jugadores no fueron encontrados.")

    combat_id = f"combat_{random.randint(1000, 9999)}"
    turn_order = [request.player1_name, request.player2_name]
    random.shuffle(turn_order)

    combat_sessions[combat_id] = {
        "players": [request.player1_name, request.player2_name],
        "turn": turn_order[0],
        "log": [f"La batalla entre {request.player1_name} y {request.player2_name} ha comenzado!"]
    }
    combat_sessions[combat_id]["log"].append(f"Es el turno de {turn_order[0]}.")
    return {"combat_id": combat_id, "message": combat_sessions[combat_id]["log"][-2:], "attacker_name": turn_order[0]}

@router.post("/combat/turn")
def take_turn(request: TurnRequest):
    """Ejecuta un turno en una sesión de combate activa."""
    session = combat_sessions.get(request.combat_id)
    if not session: raise HTTPException(status_code=404, detail="Sesión de combate no encontrada.")
    if request.attacker_name != session["turn"]: raise HTTPException(status_code=400, detail=f"No es el turno de {request.attacker_name}.")

    attacker = players_db[request.attacker_name]
    defender_name = next(p for p in session["players"] if p != request.attacker_name)
    defender = players_db[defender_name]
    turn_log = []

    # Encontrar el ataque
    available_attacks = ATTACKS_BY_ROLE.get(attacker.role, [])
    attack_info = next((atk for atk in available_attacks if atk["name"] == request.attack_name), None)

    if not attack_info: raise HTTPException(status_code=400, detail="Ataque no válido para esta clase.")
    if attacker.mp < attack_info["cost"]: raise HTTPException(status_code=400, detail="¡No tienes suficiente maná para este ataque!")

    attacker.mp -= attack_info["cost"]
    turn_log.append(f"{attacker.name} usa {attack_info['name']}! (Costó {attack_info['cost']} MP)")
    
    damage = 0
    if random.random() < 0.05: # 5% de probabilidad de fallar
        turn_log.append(f"¡Pero el ataque falla!")
    else:
        base_stat = 0
        if attack_info["type"] == "FISICO":
            base_stat = attacker.attack
        elif attack_info["type"] == "MAGICO":
            base_stat = attacker.magic_power

        base_damage = base_stat * attack_info["power"]
        # Variabilidad y defensa
        variability = random.uniform(0.85, 1.15)
        damage = max(1, round((base_damage * variability) - defender.defense))
        
        if random.random() < 0.1: # 10% de probabilidad de crítico
            damage = round(damage * 1.5)
            turn_log.append("¡GOLPE CRÍTICO!")

    defender.hp = max(0, defender.hp - damage)
    turn_log.append(f"{defender.name} recibe {damage} puntos de daño. Vida restante: {defender.hp} HP.")

    if defender.hp == 0:
        turn_log.append(f"¡{defender.name} ha sido derrotado! ¡{attacker.name} es el ganador!")
        xp_gain = defender.level * 15
        attacker.xp += xp_gain
        turn_log.append(f"{attacker.name} ha ganado {xp_gain} puntos de experiencia.")
        if attacker.xp >= attacker.xp_to_next_level:
            turn_log.append(level_up(attacker))
        del combat_sessions[request.combat_id]
    else:
        session["turn"] = defender_name
        turn_log.append(f"Ahora es el turno de {defender_name}.")

    session["log"].extend(turn_log)
    return {"log": turn_log, "session_ended": defender.hp == 0, "next_turn": session.get("turn")}
