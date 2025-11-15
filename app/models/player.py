from pydantic import BaseModel
from enum import Enum

class Role(str, Enum):
    GUERRERO = "Guerrero"
    MAGO = "Mago"
    ARQUERO = "Arquero"
    ESCUDERO = "Escudero"

class Player(BaseModel):
    name: str
    role: Role
    level: int = 1
    hp: int = 100
    attack: int = 10
    defense: int = 5
    magic_power: int = 0
