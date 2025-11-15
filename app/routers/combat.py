from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.routers.players import players_db # Importamos la "base de datos"

router = APIRouter()

class AttackRequest(BaseModel):
    attacker_name: str
    defender_name: str

@router.post("/combat/attack")
def attack(request: AttackRequest):
    """
    Simula un ataque de un jugador a otro.
    """
    attacker = players_db.get(request.attacker_name)
    defender = players_db.get(request.defender_name)

    if not attacker or not defender:
        raise HTTPException(status_code=404, detail="Attacker or defender not found")

    # Lógica de combate simple
    damage = max(0, attacker.attack - defender.defense)
    defender.hp = max(0, defender.hp - damage)

    # Comprobar si el defensor fue derrotado
    if defender.hp == 0:
        message = f"{attacker.name} attacked {defender.name} for {damage} damage. {defender.name} has been defeated!"
    else:
        message = f"{attacker.name} attacked {defender.name} for {damage} damage. {defender.name} has {defender.hp} HP remaining."
    
    return {"message": message, "defender_hp": defender.hp}
