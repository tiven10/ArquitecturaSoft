from pydantic import BaseModel, Field
from enum import Enum
from typing import List

class Role(str, Enum):
    GUERRERO = "Guerrero"
    MAGO = "Mago"
    ARQUERO = "Arquero"
    ESCUDERO = "Escudero"
    ASESINO = "Asesino"
    PALADIN = "Paladin"

class Item(BaseModel):
    name: str
    description: str
    quantity: int = 1

class PlayerStatus(str, Enum):
    NORMAL = "Normal"
    ENVENENADO = "Envenenado"
    PARALIZADO = "Paralizado"
    QUEMADO = "Quemado"

class Player(BaseModel):
    name: str
    role: Role
    level: int = 1
    xp: int = 0
    xp_to_next_level: int = 100
    hp: int = 100
    max_hp: int = 100
    mp: int = 10
    max_mp: int = 10
    attack: int = 10
    defense: int = 5
    magic_power: int = 0
    gold: int = 0
    status: PlayerStatus = PlayerStatus.NORMAL
    inventory: List[Item] = []
