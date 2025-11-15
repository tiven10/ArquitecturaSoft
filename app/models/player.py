from pydantic import BaseModel

class Player(BaseModel):
    name: str
    level: int = 1
    hp: int = 100
    attack: int = 10
    defense: int = 5
